from collections import Iterable
from functools import partial, wraps, WRAPPER_ASSIGNMENTS

from pipetools.debug import get_name, set_name, repr_args
from pipetools.compat import text_type, string_types, dict_items


class Pipe(object):
    """
    Pipe-style combinator.

    Example::

        p = pipe | F | G | H

        p(x) == H(G(F(x)))

    """
    def __init__(self, func=None):
        self.func = func
        self.__name__ = 'Pipe'

    def __str__(self):
        return get_name(self.func)

    __repr__ = __str__

    @staticmethod
    def compose(first, second):
        name = lambda: '{0} | {1}'.format(get_name(first), get_name(second))

        def composite(*args, **kwargs):
            return second(first(*args, **kwargs))
        return set_name(name, composite)

    @classmethod
    def bind(cls, first, second, new_cls=None):
        return (new_cls or cls)(
            first if second is None else
            second if first is None else
            cls.compose(first, second))

    def __or__(self, next_func):
        # Handle multiple pipes in pipe definition and also changing pipe type to e.g. Maybe
        # this is needed because of evaluation order
        pipe_in_a_pipe = isinstance(next_func, Pipe) and next_func.func is None
        new_cls = type(next_func) if pipe_in_a_pipe else None
        next = None if pipe_in_a_pipe else prepare_function_for_pipe(next_func)
        return self.bind(self.func, next, new_cls)

    def __ror__(self, prev_func):
        return self.bind(prepare_function_for_pipe(prev_func), self.func)

    def __lt__(self, thing):
        return self.func(thing) if self.func else thing

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner):
        return partial(self, instance) if instance else self


pipe = Pipe()


class Maybe(Pipe):

    @staticmethod
    def compose(first, second):
        name = lambda: '{0} ?| {1}'.format(get_name(first), get_name(second))

        def composite(*args, **kwargs):
            result = first(*args, **kwargs)
            return None if result is None else second(result)
        return set_name(name, composite)

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and args[0] is None and not kwargs:
            return None
        return self.func(*args, **kwargs)

    def __lt__(self, thing):
        return (
            None if thing is None else
            self.func(thing) if self.func else
            thing)


maybe = Maybe()


def prepare_function_for_pipe(thing):
    if isinstance(thing, XObject):
        return ~thing
    if isinstance(thing, tuple):
        return xpartial(*thing)
    if isinstance(thing, string_types):
        return StringFormatter(thing)
    if callable(thing):
        return thing
    raise ValueError('Cannot pipe %s' % thing)


def StringFormatter(template):

    f = text_type(template).format

    def format(content):
        if isinstance(content, dict):
            return f(**content)
        if _iterable(content):
            return f(*content)
        return f(content)

    return set_name(lambda: "format('%s')" % template[:20], format)


def _iterable(obj):
    "Iterable but not a string"
    return isinstance(obj, Iterable) and not isinstance(obj, string_types)


class XObject(object):

    def __init__(self, func=None):
        self._func = func
        set_name(lambda: get_name(func) if func else 'X', self)

    def __repr__(self):
        return get_name(self)

    def __invert__(self):
        return self._func or set_name('X', lambda x: x)

    def bind(self, name, func):
        set_name(name, func)
        return XObject((self._func | func) if self._func else (pipe | func))

    def __call__(self, *args, **kwargs):
        name = lambda: 'X(%s)' % repr_args(*args, **kwargs)
        return self.bind(name, lambda x: x(*args, **kwargs))

    def __hash__(self):
        return super(XObject, self).__hash__()

    def __eq__(self, other):
        return self.bind(lambda: 'X == {0!r}'.format(other), lambda x: x == other)

    def __getattr__(self, name):
        return self.bind(lambda: 'X.{0}'.format(name), lambda x: getattr(x, name))

    def __getitem__(self, item):
        return self.bind(lambda: 'X[{0!r}]'.format(item), lambda x: x[item])

    def __gt__(self, other):
        return self.bind(lambda: 'X > {0!r}'.format(other), lambda x: x > other)

    def __ge__(self, other):
        return self.bind(lambda: 'X >= {0!r}'.format(other), lambda x: x >= other)

    def __lt__(self, other):
        return self.bind(lambda: 'X < {0!r}'.format(other), lambda x: x < other)

    def __le__(self, other):
        return self.bind(lambda: 'X <= {0!r}'.format(other), lambda x: x <= other)

    def __mod__(self, y):
        return self.bind(lambda: 'X % {0!r}'.format(y), lambda x: x % y)

    def __ne__(self, other):
        return self.bind(lambda: 'X != {0!r}'.format(other), lambda x: x != other)

    def __neg__(self):
        return self.bind(lambda: '-X', lambda x: -x)

    def __mul__(self, other):
        return self.bind(lambda: 'X * {0!r}'.format(other), lambda x: x * other)

    def __div__(self, other):
        return self.bind(lambda: 'X / {0!r}'.format(other), lambda x: x / other)

    def __add__(self, other):
        return self.bind(lambda: 'X + {0!r}'.format(other), lambda x: x + other)

    def __sub__(self, other):
        return self.bind(lambda: 'X - {0!r}'.format(other), lambda x: x - other)

    def __pow__(self, other):
        return self.bind(lambda: 'X ** {0!r}'.format(other), lambda x: x ** other)

    def __ror__(self, func):
        return pipe | func | self

    def __or__(self, func):
        if isinstance(func, Pipe):
            return func.__ror__(self)
        return pipe | self | func

    def _in_(self, y):
        return self.bind(lambda: 'X._in_({0!r})'.format(y), lambda x: x in y)


X = XObject()


def xpartial(func, *xargs, **xkwargs):
    """
    Like :func:`functools.partial`, but can take an :class:`XObject`
    placeholder that will be replaced with the first positional argument
    when the partially applied function is called.

    Useful when the function's positional arguments' order doesn't fit your
    situation, e.g.:

    >>> reverse_range = xpartial(range, X, 0, -1)
    >>> reverse_range(5)
    [5, 4, 3, 2, 1]

    It can also be used to transform the positional argument to a keyword
    argument, which can come in handy inside a *pipe*::

        xpartial(objects.get, id=X)

    Also the XObjects are evaluated, which can be used for some sort of
    destructuring of the argument::

        xpartial(somefunc, name=X.name, number=X.contacts['number'])

    Lastly, unlike :func:`functools.partial`, this creates a regular function
    which will bind to classes (like the ``curry`` function from
    ``django.utils.functional``).
    """
    any_x = any(isinstance(a, XObject) for a in xargs + tuple(xkwargs.values()))
    use = lambda x, value: (~x)(value) if isinstance(x, XObject) else x

    @wraps(func, assigned=filter(partial(hasattr, func), WRAPPER_ASSIGNMENTS))
    def xpartially_applied(*func_args, **func_kwargs):
        if any_x:
            if not func_args:
                raise ValueError('Function "%s" partially applied with an '
                    'X placeholder but called with no positional arguments.'
                    % get_name(func))
            first = func_args[0]
            rest = func_args[1:]
            args = tuple(use(x, first) for x in xargs) + rest
            kwargs = dict((k, use(x, first)) for k, x in dict_items(xkwargs))
            kwargs.update(func_kwargs)
        else:
            args = xargs + func_args
            kwargs = dict(xkwargs, **func_kwargs)
        return func(*args, **kwargs)

    name = lambda: '%s(%s)' % (get_name(func), repr_args(*xargs, **xkwargs))
    return set_name(name, xpartially_applied)

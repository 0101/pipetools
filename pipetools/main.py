from functools import partial

from pipetools.debug import get_name, set_name, repr_args
from pipetools.debug import pipe_exception_handler


class Pipe(object):
    """
    Pipe-style combinator.

    Example::

        p = pipe | F | G | H

        p(x) == H(G(F(x)))

    """
    def __init__(self, func=None):
        self.func = func
        self.__name__ = str(self)

    def __str__(self):
        return get_name(self.func)

    @staticmethod
    def compose(first, second):
        name = '{0} | {1}'.format(get_name(first), get_name(second))

        def composite(*args, **kwargs):
            with pipe_exception_handler('pipe | ' + name):
                return second(first(*args, **kwargs))
        return set_name(name, composite)

    @classmethod
    def bind(cls, first, second):
        return cls(
            first if second is None else
            second if first is None else
            cls.compose(first, second))

    def __or__(self, next_func):
        return self.bind(self.func, prepare_function_for_pipe(next_func))

    def __ror__(self, prev_func):
        return self.bind(prepare_function_for_pipe(prev_func), self.func)

    def __lt__(self, thing):
        return self.func(thing) if self.func else thing

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

pipe = Pipe()


class Maybe(Pipe):

    @staticmethod
    def compose(first, second):
        name = '{0} ?| {1}'.format(get_name(first), get_name(second))

        def composite(*args, **kwargs):
            with pipe_exception_handler('maybe | ' + name):
                result = first(*args, **kwargs)
                return None if result is None else second(result)
        return set_name(name, composite)

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
        return partial(*thing)
    if isinstance(thing, basestring):
        return StringFormatter(thing)
    if callable(thing):
        return thing
    raise ValueError('Cannot pipe %s' % thing)


def StringFormatter(template):

    f = unicode(template).format

    def format(content):
        if isinstance(content, dict):
            return f(**content)
        if _iterable(content):
            return f(*content)
        return f(content)

    return set_name("format('%s')" % template[:20], format)


def _iterable(obj):
    return (hasattr(obj, '__iter__')
        or hasattr(obj, '__getitem__')
        and not isinstance(obj, basestring))


class XObject(object):

    def __init__(self, func=None):
        self._func = func
        self.__name__ = get_name(func)

    def __repr__(self):
        return self.__name__ or 'X'

    def __invert__(self):
        return self._func or set_name('X', lambda x: x)

    def bind(self, name, func):
        try:
            func.__name__ = str(name)
        except UnicodeError:
            func.__name__ = repr(name)
        return XObject((self._func | func) if self._func else (pipe | func))

    def __call__(self, *args, **kwargs):
        name = 'X(%s)' % repr_args(*args, **kwargs)
        return self.bind(name, lambda x: x(*args, **kwargs))

    def __eq__(self, other):
        return self.bind('X == %s' % other, lambda x: x == other)

    def __getattr__(self, name):
        return self.bind('X.%s' % name, lambda x: getattr(x, name))

    def __getitem__(self, item):
        return self.bind('X[%s]' % item, lambda x: x[item])

    def __gt__(self, other):
        return self.bind('X > %s' % other, lambda x: x > other)

    def __lt__(self, other):
        return self.bind('X < %s' % other, lambda x: x < other)

    def __mod__(self, y):
        return self.bind('X %% %s' % y, lambda x: x % y)

    def __ne__(self, other):
        return self.bind('X != %s' % other, lambda x: x != other)

    def __neg__(self):
        return self.bind('-X', lambda x: -x)

    def __mul__(self, other):
        return self.bind('X * %s' % other, lambda x: x * other)

    def __add__(self, other):
        return self.bind('X + %s' % other, lambda x: x + other)

    def __ror__(self, func):
        return pipe | func | self

    def _in_(self, container):
        return self.bind('X._in_(%s)' % container, lambda x: x in container)


X = XObject()

from functools import partial


class Pipe(object):
    """
    Pipe-style combinator.

    Example::

        p = pipe | F | G | H

        p(x) == H(G(F(x)))

    """
    def __init__(self, func=None):
        self.func = func

    @staticmethod
    def compose(first, second):
        return lambda *args, **kwargs: second(first(*args, **kwargs))

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
        def composite(*args, **kwargs):
            result = first(*args, **kwargs)
            return None if result is None else second(result)
        return composite

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

    return format


def _iterable(obj):
    return (hasattr(obj, '__iter__')
        or hasattr(obj, '__getitem__')
        and not isinstance(obj, basestring))


class XObject(object):

    def __init__(self, func=None):
        self._func = func or (lambda x: x)

    def __invert__(self):
        return self._func

    def __call__(self, *args, **kwargs):
        return XObject(pipe | self | (lambda x: x(*args, **kwargs)))

    def __eq__(self, other):
        return XObject(pipe | self | (lambda x: x == other))

    def __getattr__(self, name):
        return XObject(pipe | self | (lambda x: getattr(x, name)))

    def __getitem__(self, item):
        return XObject(pipe | self | (lambda x: x[item]))

    def __gt__(self, other):
        return XObject(pipe | self | (lambda x: x > other))

    def __lt__(self, other):
        return XObject(pipe | self | (lambda x: x < other))

    def __mod__(self, y):
        return XObject(pipe | self | (lambda x: x % y))

    def __ne__(self, other):
        return XObject(pipe | self | (lambda x: x != other))

    def __neg__(self):
        return XObject(pipe | self | (lambda x: -x))

    def __mul__(self, other):
        return XObject(pipe | self | (lambda x: x * other))

    def __add__(self, other):
        return XObject(pipe | self | (lambda x: x + other))

    def __ror__(self, func):
        return pipe | func | self

    def _in_(self, container):
        return XObject(pipe | self | (lambda x: x in container))


X = XObject()

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

    def bind(self, next_func):
        return Pipe(next_func if self.func is None else
            lambda *args, **kwargs: next_func(self.func(*args, **kwargs)))

    def rbind(self, prev_func):
        return Pipe(prev_func if self.func is None else
            lambda *args, **kwargs: self.func(prev_func(*args, **kwargs)))

    def __or__(self, next_func):
        if isinstance(next_func, XObject):
            return self.bind(~next_func)
        if isinstance(next_func, tuple):
            return self.bind(partial(*next_func))
        elif callable(next_func):
            return self.bind(next_func)

    def __ror__(self, thing):
        if isinstance(thing, XObject):
            return self.rbind(~thing)
        if callable(thing):
            return self.rbind(thing)

    def __lt__(self, thing):
        return self.func(thing) if self.func else thing

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


pipe = Pipe()


class XObject(object):
    """
    Shortcut for writing simple, one-argument lambdas.

    Example::

        ~X.some_attr.some_func(1, 2, 3).whatever
        # produces:
        lambda x: x.some_attr.some_func(1, 2, 3).whatever

        ~(X > 5)
        # produces:
        lambda x: x > 5

    The ~ operator creates the actual function that can be called (without
    creating just another X instance). But the X objects can be used without
    it in pipe-utils (like :func:`where` or :func:`foreach`).
    """

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

    def __ror__(self, func):
        return pipe | func | self

    def _in_(self, container):
        return XObject(pipe | self | (lambda x: x in container))


X = XObject()

from functools import partial
from itertools import imap, ifilter, islice
import operator

from pipetools.main import pipe, X, XObject, _iterable, StringFormatter


KEY, VALUE = X[0], X[1]


def pipe_util(func):
    """
    Decorator that handles X objects and currying for pipe-utils.
    """
    def pipe_util_wrapper(function, *args, **kwargs):
        if isinstance(function, XObject):
            function = ~function

        if args or kwargs:
            function = partial(function, *args, **kwargs)

        # TODO: good idea?
        if isinstance(function, tuple):
            funcs = function
            function = lambda x: tuple((pipe | f)(x) for f in funcs)

        if isinstance(function, list):
            funcs = function
            function = lambda x: list((pipe | f)(x) for f in funcs)

        if isinstance(function, dict):
            funcd = function
            function = lambda x: dict(
                (key, (pipe | f)(x)) for key, f in funcd.iteritems())

        return pipe | func(function)

    pipe_util_wrapper.__name__ = func.__name__
    pipe_util_wrapper.__doc__ = func.__doc__

    return pipe_util_wrapper


def auto_string_formatter(func):

    def auto_string_formatter_wrapper(function, *args, **kwargs):
        if isinstance(function, basestring):
            function = StringFormatter(function)

        return func(function, *args, **kwargs)

    auto_string_formatter_wrapper.__name__ = func.__name__
    auto_string_formatter_wrapper.__doc__ = func.__doc__

    return auto_string_formatter_wrapper


@pipe_util
@auto_string_formatter
def foreach(function):
    """
    Returns a function that takes an iterable and returns an iterator over the
    results of calling `function` on each item of the iterable.
    """
    return partial(imap, function)


@pipe_util
def foreach_do(function):
    """
    Like :func:`foreach` but is evaluated immediately and doesn't return
    anything.
    """
    def f(iterable):
        for item in iterable:
            function(item)

    return f


@pipe_util
def where(function):
    """
    Pipe-able lazy filter::

        >>> odd = pipe | xrange | where(lambda x: x % 2) | tuple
        >>> odd(10)
        (1, 3, 5, 7, 9)

    """
    return partial(ifilter, function)


@pipe_util
def where_not(function):
    """
    Inverted :func:`where`.
    """
    return partial(ifilter, pipe | function | operator.not_)


@pipe_util
def sort_by(key):
    return partial(sorted, key=key)

sort = sort_by(X)


@pipe_util
@auto_string_formatter
def debug_print(func):
    def debug(thing):
        print func(thing)
        return thing
    return debug


@pipe_util
def as_args(func):
    return lambda x: func(*x)


def take_first(count):
    def _take_first(iterable):
        return islice(iterable, count)
    return _take_first
take_first = pipe | take_first


@pipe_util
def select_first(condition):
    return lambda seq: unless(StopIteration, where(condition) | X.next(), seq)


@pipe_util
@auto_string_formatter
def group_by(func):

    def _group_by(seq):
        result = {}
        for item in seq:
            result.setdefault(func(item), []).append(item)
        return result

    return _group_by


def unless(exception_class, func, *args, **kwargs):
    try:
        return partial(func, *args, **kwargs)()
    except exception_class:
        pass


def _flatten(x):
    if not _iterable(x):
        yield x
    else:
        for y in x:
            for z in _flatten(y):
                yield z


def flatten(*args):
    return _flatten(args)
flatten = pipe | flatten


def count(iterable):
    return sum(1 for whatever in iterable)
count = pipe | count

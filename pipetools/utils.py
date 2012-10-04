from functools import partial, wraps
from itertools import imap, ifilter, islice
import operator

from pipetools.main import pipe, X, XObject, _iterable, StringFormatter
from pipetools.ds_builder import data_structure_builder


KEY, VALUE = X[0], X[1]


def pipe_util(func):
    """
    Decorator that handles X objects and currying for pipe-utils.
    """
    @wraps(func)
    def pipe_util_wrapper(function, *args, **kwargs):
        if isinstance(function, XObject):
            function = ~function

        if args or kwargs:
            function = partial(function, *args, **kwargs)

        return pipe | func(function)

    return pipe_util_wrapper


def auto_string_formatter(func):
    """
    Decorator that handles automatic string formatting.

    By converting a string argument to a function that does formatting on said
    string.
    """
    @wraps(func)
    def auto_string_formatter_wrapper(function, *args, **kwargs):
        if isinstance(function, basestring):
            function = StringFormatter(function)

        return func(function, *args, **kwargs)

    return auto_string_formatter_wrapper


@pipe_util
@auto_string_formatter
@data_structure_builder
def foreach(function):
    """
    Returns a function that takes an iterable and returns an iterator over the
    results of calling `function` on each item of the iterable.

    >>> xrange(5) > foreach(factorial) | list
    [1, 1, 2, 6, 24]
    """
    return partial(imap, function)


@pipe_util
def foreach_do(function):
    """
    Like :func:`foreach` but is evaluated immediately and doesn't return
    anything.

    For the occasion that you just want to do some side-effects::

        open('addresses.txt') > foreach(geocode) | foreach_do(launch_missile)

    -- With :func:`foreach` nothing would happen (except an itetrator being
    created)
    """
    def f(iterable):
        for item in iterable:
            function(item)

    return f


@pipe_util
def where(function):
    """
    Pipe-able lazy filter.

    >>> odd_range = xrange | where(X % 2) | list
    >>> odd_range(10)
    [1, 3, 5, 7, 9]

    """
    return partial(ifilter, function)


@pipe_util
def where_not(function):
    """
    Inverted :func:`where`.
    """
    return partial(ifilter, pipe | function | operator.not_)


@pipe_util
@data_structure_builder
def sort_by(function):
    """
    Sorts an incoming sequence by using the given `function` as key.

    >>> xrange(10) > sort_by(-X)
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    Supports automatic data-structure creation::

        users > sort_by([X.last_name, X.first_name])

    There is also a shortcut for ``sort_by(X)`` called ``sort``:

    >>> [4, 5, 8, -3, 0] > sort
    [-3, 0, 4, 5, 8]
    """
    return partial(sorted, key=function)

sort = sort_by(X)


@pipe_util
@auto_string_formatter
@data_structure_builder
def debug_print(function):
    """
    Prints function applied on input and returns the input.

    ::

        foo = (pipe
            | something
            | debug_print(X.get_status())
            | something_else
            | foreach(debug_print("attr is: {0.attr}"))
            | etc)
    """
    def debug(thing):
        print function(thing)
        return thing
    return debug


@pipe_util
def as_args(function):
    """
    Applies the sequence in the input as positional arguments to `function`.

    ::

        some_lists > as_args(izip)
    """
    return lambda x: function(*x)


def take_first(count):
    """
    Assumes an iterable on the input, returns an iterable with first `count`
    items from the input (or possibly less, if there isn't that many).

    >>> xrange(9000) > where(X % 100 == 0) | take_first(5) | tuple
    (0, 100, 200, 300, 400)

    """
    def _take_first(iterable):
        return islice(iterable, count)
    return pipe | _take_first


@pipe_util
def select_first(condition):
    """
    Returns first item from input sequence that satisfies `condition`. Or
    ``None`` if none does.

    >>> ['py', 'pie', 'pi'] > select_first(X.startswith('pi'))
    'pie'
    """
    return lambda seq: unless(StopIteration, where(condition) | X.next(), seq)


@pipe_util
@auto_string_formatter
@data_structure_builder
def group_by(function):
    """
    Returns a dictionary of input sequence items grouped by `function`.
    """
    def _group_by(seq):
        result = {}
        for item in seq:
            result.setdefault(function(item), []).append(item)
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
    """
    Flattens an arbitrarily deep nested iterable(s).
    """
    return _flatten(args)
flatten = pipe | flatten


def count(iterable):
    """
    Returns the number of items in `iterable`.
    """
    return sum(1 for whatever in iterable)
count = pipe | count

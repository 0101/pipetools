from __future__ import print_function
from collections import Mapping
from functools import partial, wraps
from itertools import islice, takewhile, dropwhile
from typing import Iterable, TypeVar, Callable, Any, Optional, Tuple, List
import operator

from pipetools.compat import map, filter, range, dict_items
from pipetools.debug import set_name, repr_args, get_name
from pipetools.decorators import data_structure_builder, regex_condition
from pipetools.decorators import pipe_util, auto_string_formatter
from pipetools.main import pipe, X, _iterable


KEY, VALUE = X[0], X[1]


T = TypeVar('T')
Tout = TypeVar('Tout')


@pipe_util
@auto_string_formatter
@data_structure_builder
def foreach(function: Callable[[T], Tout]) -> Callable[[Iterable[T]], Iterable[Tout]]:
    """
    Returns a function that takes an iterable and returns an iterator over the
    results of calling `function` on each item of the iterable.

    >>> range(5) > foreach(factorial) | list
    [1, 1, 2, 6, 24]
    """
    return partial(map, function)


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
@regex_condition
def where(condition: Callable[[T], Any]) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Pipe-able lazy filter.

    >>> odd_range = range | where(X % 2) | list
    >>> odd_range(10)
    [1, 3, 5, 7, 9]

    """
    return partial(filter, condition)


@pipe_util
@regex_condition
def where_not(condition: Callable[[T], bool]) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Inverted :func:`where`.
    """
    return partial(filter, pipe | condition | operator.not_)


@pipe_util
@data_structure_builder
def sort_by(function: Callable[[T], Any]) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Sorts an incoming sequence by using the given `function` as key.

    >>> range(10) > sort_by(-X)
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    Supports automatic data-structure creation::

        users > sort_by([X.last_name, X.first_name])

    There is also a shortcut for ``sort_by(X)`` called ``sort``:

    >>> [4, 5, 8, -3, 0] > sort
    [-3, 0, 4, 5, 8]

    And (as of ``0.2.3``) a shortcut for reversing the sort:

    >>> 'asdfaSfa' > sort_by(X.lower()).descending
    ['s', 'S', 'f', 'f', 'd', 'a', 'a', 'a']
    """
    f = partial(sorted, key=function)
    f.attrs = {'descending': _descending_sort_by(function)}
    return f


@pipe_util
def _descending_sort_by(function: Callable[[T], Any]) -> Callable[[Iterable[T]], Iterable[T]]:
    return partial(sorted, key=function, reverse=True)


sort = sort_by(X)


@pipe_util
@auto_string_formatter
@data_structure_builder
def debug_print(function: Callable[[T], Any]) -> Callable[[T], T]:
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
        print(function(thing))
        return thing
    return debug


@pipe_util
def tee(function: Callable[[T], Any]) -> Callable[[T], T]:
    """
    Sends a copy of the input into function - like a T junction.
    """
    def _tee(thing):
        function(thing)
        return thing
    return _tee


@pipe_util
def as_args(function: Callable[..., Tout]) -> Callable[[T], Tout]:
    """
    Applies the sequence in the input as positional arguments to `function`.

    ::

        some_lists > as_args(izip)
    """
    return lambda x: function(*x)


@pipe_util
def as_kwargs(function: Callable[..., Tout]) -> Callable[[T], Tout]:
    """
    Applies the dictionary in the input as keyword arguments to `function`.
    """
    return lambda x: function(**x)


def take_first(count: int) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Assumes an iterable on the input, returns an iterable with first `count`
    items from the input (or possibly less, if there isn't that many).

    >>> range(9000) > where(X % 100 == 0) | take_first(5) | tuple
    (0, 100, 200, 300, 400)

    """
    def _take_first(iterable):
        return islice(iterable, count)
    return pipe | set_name('take_first(%s)' % count, _take_first)


def drop_first(count: int) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Assumes an iterable on the input, returns an iterable with identical items
    except for the first `count`.

    >>> range(10) > drop_first(5) | tuple
    (5, 6, 7, 8, 9)
    """
    def _drop_first(iterable):
        g = (x for x in range(1, count + 1))
        return dropwhile(
            lambda i: unless(StopIteration, lambda: next(g))(), iterable)
    return pipe | set_name('drop_first(%s)' % count, _drop_first)


def unless(
        exception_class_or_tuple,
        func: Callable[..., Tout],
        *args, **kwargs) -> Callable[..., Optional[Tout]]:
    """
    When `exception_class_or_tuple` occurs while executing `func`, it will
    be caught and ``None`` will be returned.

    >>> f = where(X > 10) | list | unless(IndexError, X[0])
    >>> f([5, 8, 12, 4])
    12
    >>> f([1, 2, 3])
    None
    """
    @pipe_util
    @auto_string_formatter
    @data_structure_builder
    def construct_unless(function):
        # a wrapper so we can re-use the decorators
        def _unless(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exception_class_or_tuple:
                pass
        return _unless

    name = lambda: 'unless(%s, %s)' % (exception_class_or_tuple, ', '.join(
        filter(None, (get_name(func), repr_args(*args, **kwargs)))))

    return set_name(name, construct_unless(func, *args, **kwargs))


@pipe_util
@regex_condition
def select_first(condition: Callable[[T], Any]) -> Callable[[Iterable[T]], Optional[T]]:
    """
    Returns first item from input sequence that satisfies `condition`. Or
    ``None`` if none does.

    >>> ['py', 'pie', 'pi'] > select_first(X.startswith('pi'))
    'pie'

    As of ``0.2.1`` you can also
    :ref:`directly use regular expressions <auto-regex>` and write the above
    as:

    >>> ['py', 'pie', 'pi'] > select_first('^pi')
    'pie'

    There is also a shortcut for ``select_first(X)`` called ``first_of``:

    >>> first_of(['', None, 0, 3, 'something'])
    3
    >>> first_of([])
    None
    """
    return where(condition) | unless(StopIteration, next)


first_of: Callable[[Iterable[T]], Optional[T]] = select_first(X)


@pipe_util
@auto_string_formatter
@data_structure_builder
def group_by(function: Callable[[T], Tout]) -> Callable[[Iterable[T]], Iterable[Tuple[Tout, List[T]]]]:
    """
    Groups input sequence by `function`.

    Returns an iterator over a sequence of tuples where the first item is a
    result of `function` and the second one a list of items matching this
    result.

    Ordering of the resulting iterator is undefined, but ordering of the items
    in the groups is preserved.

    >>> [1, 2, 3, 4, 5, 6] > group_by(X % 2) | list
    [(0, [2, 4, 6]), (1, [1, 3, 5])]
    """
    def _group_by(seq):
        result = {}
        for item in seq:
            result.setdefault(function(item), []).append(item)
        return dict_items(result)

    return _group_by


def __flatten(x):
    if not _iterable(x) or isinstance(x, Mapping):
        yield x
    else:
        for y in x:
            for z in __flatten(y):
                yield z


def _flatten(*args):
    """
    Flattens an arbitrarily deep nested iterable(s).

    >>> [[[[[[1]]], 2], range(2) > foreach(X + 3)]] > flatten | list
    [1, 2, 3, 4]

    Does not treat strings and (as of ``0.3.1``) mappings (dictionaries)
    as iterables so these are left alone.

    >>> ('hello', [{'how': 'are'}, [['you']]]) > flatten | list
    ['hello', {'how': 'are'}, 'you']

    Also turns non-iterables into iterables which is convenient when you
    are not sure about the input.

    >>> 'stuff' > flatten | list
    ['stuff']
    """
    return __flatten(args)


flatten: Callable[..., Iterable] = wraps(_flatten)(pipe | _flatten)


def _count(iterable):
    """
    Returns the number of items in `iterable`.
    """
    return sum(1 for whatever in iterable)


count: Callable[[Iterable], int] = wraps(_count)(pipe | _count)


@pipe_util
@regex_condition
def take_until(condition: Callable[[T], Any]) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    >>> [1, 4, 6, 4, 1] > take_until(X > 5) | list
    [1, 4]

    >>> [1, 4, 6, 4, 1] > take_until(X > 5).including | list
    [1, 4, 6]
    """
    f = partial(takewhile, pipe | condition | operator.not_)
    f.attrs = {'including': take_until_including(condition)}
    return f


@pipe_util
@regex_condition
def take_until_including(condition: Callable[[T], Any]) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    >>> [1, 4, 6, 4, 1] > take_until_including(X > 5) | list
    [1, 4, 6]
    """
    def take_until_including_(interable):
        for i in interable:
            if not condition(i):
                yield i
            else:
                yield i
                break
    return take_until_including_

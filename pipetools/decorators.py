import re
from functools import partial, wraps
from typing import TypeVar

from pipetools.debug import repr_args, set_name, get_name
from pipetools.ds_builder import DSBuilder, NoBuilder
from pipetools.main import pipe, XObject, StringFormatter, xpartial, maybe
from pipetools.compat import string_types, dict_items


T = TypeVar('T')


def pipe_util(func: T) -> T:
    """
    Decorator that handles X objects and partial application for pipe-utils.
    """
    @wraps(func)
    def pipe_util_wrapper(function, *args, **kwargs):
        if isinstance(function, XObject):
            function = ~function

        original_function = function

        if args or kwargs:
            function = xpartial(function, *args, **kwargs)

        name = lambda: '%s(%s)' % (get_name(func), ', '.join(
            filter(None, (get_name(original_function), repr_args(*args, **kwargs)))))

        f = func(function)

        result = pipe | set_name(name, f)

        # if the util defines an 'attrs' mapping, copy it as attributes
        # to the result
        attrs = getattr(f, 'attrs', {})
        for k, v in dict_items(attrs):
            setattr(result, k, v)

        return result

    return pipe_util_wrapper


def auto_string_formatter(func: T) -> T:
    """
    Decorator that handles automatic string formatting.

    By converting a string argument to a function that does formatting on said
    string.
    """
    @wraps(func)
    def auto_string_formatter_wrapper(function, *args, **kwargs):
        if isinstance(function, string_types):
            function = StringFormatter(function)

        return func(function, *args, **kwargs)

    return auto_string_formatter_wrapper


def data_structure_builder(func: T) -> T:
    """
    Decorator to handle automatic data structure creation for pipe-utils.
    """
    @wraps(func)
    def ds_builder_wrapper(function, *args, **kwargs):
        try:
            function = DSBuilder(function)
        except NoBuilder:
            pass
        return func(function, *args, **kwargs)

    return ds_builder_wrapper


def regex_condition(func: T) -> T:
    """
    If a condition is given as string instead of a function, it is turned
    into a regex-matching function.
    """
    @wraps(func)
    def regex_condition_wrapper(condition, *args, **kwargs):
        if isinstance(condition, string_types):
            condition = maybe | partial(re.match, condition)
        return func(condition, *args, **kwargs)
    return regex_condition_wrapper

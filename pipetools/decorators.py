from functools import partial, wraps

from pipetools.debug import repr_args, set_name, get_name
from pipetools.ds_builder import DSBuilder, NoBuilder
from pipetools.main import pipe, XObject, StringFormatter


def pipe_util(func):
    """
    Decorator that handles X objects and currying for pipe-utils.
    """
    def pipe_util_wrapper(function, *args, **kwargs):
        if isinstance(function, XObject):
            function = ~function

        function_name = get_name(function)

        if args or kwargs:
            function = partial(function, *args, **kwargs)

        name = '%s(%s)' % (func.__name__, ', '.join(
            filter(None, (function_name, repr_args(*args, **kwargs)))))

        return pipe | set_name(name, func(function))

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


def data_structure_builder(func):
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

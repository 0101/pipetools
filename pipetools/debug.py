from contextlib import contextmanager
from itertools import imap, chain


def set_name(name, f):
    try:
        f.__pipetools__name__ = name
    except (AttributeError, UnicodeEncodeError):
        pass
    return f


def get_name(f):
    from pipetools.main import Pipe
    pipetools_name = getattr(f, '__pipetools__name__', None)
    if pipetools_name:
        return pipetools_name() if callable(pipetools_name) else pipetools_name

    if isinstance(f, Pipe):
        return repr(f)

    return f.__name__ if hasattr(f, '__name__') else repr(f)


@contextmanager
def pipe_exception_handler(name):
    try:
        yield
    except Exception, ex:
        message = '%s\n  in %s' % (ex, name())
        try:
            # some exceptions might be bit more complicated to construct
            # in which case... we're screwed
            pipe_exception = type(ex)(message)
            raise pipe_exception
        except:
            raise


def repr_args(*args, **kwargs):
    return ', '.join(chain(
        imap('{0!r}'.format, args),
        imap('{0[0]}={0[1]!r}'.format, kwargs.iteritems())))

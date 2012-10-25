import pytest

from pipetools.debug import pipe_exception_handler
from pipetools import pipe, foreach, X


def test_pipe_exception():
    "How an exception in a pipe should look like"

    f = pipe | str | foreach(X.upper()) | foreach(~X.lower() | int) | list

    with pytest.raises(ValueError) as excinfo:
        f('adfasfa')

    assert excinfo.value.message == (
        "invalid literal for int() with base 10: 'a'\n"
        "  in pipe | X.lower | X() | int\n"
        "  in pipe | str | foreach(X.upper | X()) | foreach(X.lower | X() | int) | list"
    )


def test_pipe_exception_handler():

    class MyException(Exception):
        pass

    with pytest.raises(MyException) as excinfo:

        with pipe_exception_handler('NAME'):

            raise MyException('boo hoo')

    assert excinfo.value.message == "boo hoo\n  in NAME"

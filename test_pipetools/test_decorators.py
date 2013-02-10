from pipetools import foreach, sort_by, X


def my_func(*args, **kwargs):
    pass


def test_pipe_util_xpartial():
    f = xrange | foreach(range, X, 0, -1) | list
    assert f(3, 5) == [[3, 2, 1], [4, 3, 2, 1]]


class TestPipeUtilNames:

    def test_basic(self):
        f = foreach(my_func)
        assert f.__name__ == 'foreach(my_func)'

    def test_partially_applied(self):
        f = foreach(my_func, 42, kwarg=2)
        assert f.__name__ == 'foreach(my_func, 42, kwarg=2)'

    def test_string_formatting(self):
        f = foreach("{0} asdf {1} jk;l")
        assert f.__name__ == "foreach('{0} asdf {1} jk;l')"

    def test_ds_builder(self):
        f = sort_by([X.attr, X * 2])
        assert f.__name__ == 'sort_by([X.attr, X * 2])'

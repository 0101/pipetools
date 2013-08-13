from pipetools import foreach, sort_by, X, unless


def my_func(*args, **kwargs):
    pass


def test_pipe_util_xpartial():
    f = xrange | foreach(range, X, 0, -1) | list
    assert f(3, 5) == [[3, 2, 1], [4, 3, 2, 1]]


class TestPipeUtilsRepr:

    def test_basic(self):
        f = foreach(my_func)
        assert repr(f) == 'foreach(my_func)'

    def test_partially_applied(self):
        f = foreach(my_func, 42, kwarg=2)
        assert repr(f) == 'foreach(my_func, 42, kwarg=2)'

    def test_string_formatting(self):
        f = foreach("{0} asdf {1} jk;l")
        assert repr(f) == "foreach('{0} asdf {1} jk;l')"

    def test_ds_builder(self):
        f = sort_by([X.attr, X * 2])
        assert repr(f) == 'sort_by([X.attr, X * 2])'

    def test_repr_doesnt_get_called_when_not_necessary(self):

        class Something(object):

            def __repr__(self):
                assert False, "__repr__ called when not necessary"

        foreach(Something())
        unless(Exception, Something())

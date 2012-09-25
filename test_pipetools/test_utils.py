import operator

from pipetools import X, sort_by, take_first, foreach, where, select_first


class TestPipeUtil:

    def test_pipability(self):
        f = xrange | foreach(X) | sum

        result = f(4)
        assert result == 6

    def test_input(self):
        result = xrange(5) > where(X % 2) | list
        assert result == [1, 3]


class TestSortBy:

    def test_x(self):

        result = sort_by(-X[1])(zip('what', [1, 2, 3, 4]))

        assert result == [
            ('t', 4),
            ('a', 3),
            ('h', 2),
            ('w', 1),
        ]


class TestTakeFirst:

    def test_take_first(self):
        assert [0, 1, 2] == list(take_first(3)(xrange(10)))


class TestTupleMaker:

    def test_make_tuple(self):
        result = [1, 2, 3] > foreach((X, X % 2)) | list
        assert result == [(1, 1), (2, 0), (3, 1)]

    def test_make_tuple_curry(self):
        result = [1, 2, 3] > foreach((X, (operator.mul, 2))) | list
        assert result == [(1, 2), (2, 4), (3, 6)]


class TestListMaker:

    def test_make_list(self):
        result = [1, 2, 3] > foreach([X, X % 2]) | list
        assert result == [[1, 1], [2, 0], [3, 1]]

    def test_make_list_curry(self):
        result = [1, 2, 3] > foreach([X, (operator.mul, 2)]) | list
        assert result == [[1, 2], [2, 4], [3, 6]]


class TestDictMaker:

    def test_make_dict(self):
        result = [1, 2] > foreach({'num': X, 'str': str}) | list
        assert result == [{'num': 1, 'str': '1'}, {'num': 2, 'str': '2'}]

    def test_make_dict_curry(self):
        result = [1, 2] > foreach({'double': (operator.mul, 2)}) | list
        assert result == [{'double': 2}, {'double': 4}]


class TestSelectFirst:

    def test_select_first(self):
        result = select_first(X % 2 == 0)([3, 4, 5, 6])
        assert result == 4

    def test_select_first_none(self):
        result = select_first(X == 2)([0, 1, 0, 1])
        assert result == None

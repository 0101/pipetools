from pipetools import pipe, X


class Bunch:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestPipe:

    def test_pipe(self):

        p = pipe | str | (lambda x: x * 2)

        assert p(5) == '55'

    def test_pipe_right(self):
        f = sum | pipe | str

        assert f([1, 2, 3]) == '6'

    def test_pipe_input(self):
        result = [1, 2, 3] > pipe | sum

        assert result == 6

    def test_pipe_right_X(self):
        f = X[0] | pipe | str

        assert f([1, 2, 3]) == '1'


class TestX:

    def test_basic(self):

        f = ~X.startswith('Hello')

        assert f('Hello world')
        assert not f('Goodbye world')

    def test_chained(self):

        f = ~X.get('item', '').startswith('Hello')

        assert f({'item': 'Hello world'})
        assert not f({'item': 'Goodbye world'})
        assert not f({})

    def test_passthrough(self):

        f = ~X

        assert f(42), 42

    def test_mod(self):

        f = ~(X % 2)

        assert f(3)
        assert not f(2)

    def test_gt(self):

        f = ~(X > 5)

        assert f(6)
        assert not f(5)

    def test_lt(self):

        f = ~(X < 5)

        assert f(4)
        assert not f(5)

    def test_chained_gt(self):

        f = ~(X.thing > 5)

        assert f(Bunch(thing=6))
        assert not f(Bunch(thing=4))

    def test_index(self):

        f = ~(X['item'])

        assert f({'item': 42}), 42

    def test_eq(self):

        f = ~(X == 42)

        assert f(42)
        assert not f('whatever')

    def test_neq(self):

        f = ~(X != 42)

        assert not f(42)
        assert f('whatever')

    def test_neg(self):

        f = ~-X

        assert f(5), -5

    def test_pipe_right(self):

        f = str | X[0]

        assert f(10), '1'

    def test_call(self):

        f = ~X(42)

        assert f(lambda n: n / 2), 21

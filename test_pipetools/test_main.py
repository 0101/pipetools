# encoding: utf-8
import pytest
from dataclasses import dataclass
from typing import Callable, Final

from pipetools import pipe, X, maybe, xpartial
from pipetools.main import StringFormatter
from pipetools.compat import range


class Bunch:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestPipe(object):

    pipe = property(lambda self: pipe)

    def test_pipe(self):
        p = self.pipe | str | (lambda x: x * 2)

        assert p(5) == '55'

    def test_pipe_right(self):
        f = sum | self.pipe | str

        assert f([1, 2, 3]) == '6'

    def test_pipe_input(self):
        result = [1, 2, 3] > self.pipe | sum

        assert result == 6

    def test_pipe_right_X(self):
        f = X[0] | self.pipe | str

        assert f([1, 2, 3]) == '1'

    def test_string_formatting(self):
        f = self.pipe | 'The answer is {0}.'

        assert f(42) == 'The answer is 42.'

    def test_unicode_formatting(self):
        f = self.pipe | u'That will be £ {0}, please.'
        assert f(42) == u'That will be £ 42, please.'

    def test_automatic_partial(self):
        odd_sum = self.pipe | range | (filter, lambda x: x % 2) | sum
        assert odd_sum(1, 10) == 25

    def test_automatic_partial_with_kwargs_using_pipe(self):
        dataclass_kwargs: Final[dict[str, bool]] = {'frozen': True, 'kw_only': True, 'slots': True}
        my_dataclass: Final[Callable] = self.pipe | dataclass | dataclass_kwargs

        self._assert_dataclass_builder(my_dataclass)

    def test_automatic_partial_with_kwargs_using_tuple(self):
        dataclass_kwargs: Final[dict[str, bool]] = {'frozen': True, 'kw_only': True, 'slots': True}
        my_dataclass: Final[Callable] = self.pipe | (dataclass, dataclass_kwargs)

        self._assert_dataclass_builder(my_dataclass)
    def test_feeding_the_pipe(self):
        result = range(10) > self.pipe | sum
        assert result == 45

    def test_super_feeding_the_pipe(self):
        dataclass_kwargs: Final[dict[str, bool]] = {'frozen': True, 'kw_only': True, 'slots': True}
        my_dataclass: Final[Callable] = dataclass_kwargs >> (self.pipe | dataclass)

        self._assert_dataclass_builder(my_dataclass)

    @staticmethod
    def _assert_dataclass_builder(my_dataclass):
        @my_dataclass
        class Bla:
            foo: int
            bar: str

        with pytest.raises(TypeError):
            Bla(5, 'bbb')
        assert Bla(foo=5, bar='bbb').foo == 5

    def test_makes_a_bound_method(self):

        class SomeClass(object):
            attr = 'foo bar'
            method = X.attr.split() | reversed | ' '.join

        assert SomeClass().method() == 'bar foo'


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

        assert f(42) == 42

    def test_mod(self):

        f = ~(X % 2)
        g = ~(9 % X)

        assert f(3)
        assert not g(3)
        assert g(2)
        assert not f(2)

    def test_gt(self):

        f = ~(X > 5)
        g = ~(6 > X)

        assert f(6)
        assert not g(6)
        assert g(5)
        assert not f(5)

    def test_gte(self):

        f = ~(X >= 5)
        g = ~(4 >= X)

        assert f(5)
        assert not g(5)
        assert g(4)
        assert not f(4)

    def test_lt(self):

        f = ~(X < 5)
        g = ~(4 < X)

        assert f(4)
        assert not g(4)
        assert g(5)
        assert not f(5)

    def test_lte(self):

        f = ~(X <= 5)
        g = ~(6 <= X)

        assert f(5)
        assert not g(5)
        assert g(6)
        assert not f(6)

    def test_chained_gt(self):

        f = ~(X.thing > 5)

        assert f(Bunch(thing=6))
        assert not f(Bunch(thing=4))

    def test_index(self):

        f = ~(X['item'])

        assert f({'item': 42}) == 42

    def test_eq(self):

        f = ~(X == 42)

        assert f(42)
        assert not f('whatever')

    def test_neq(self):

        f = ~(X != 42)

        assert not f(42)
        assert f('whatever')

    def test_pos(self):

        f = ~+X

        assert f(4) == 4

    def test_neg(self):

        f = ~-X

        assert f(5) == -5

    def test_pipe_right(self):

        f = str | X[0]

        assert f(10) == '1'

    def test_pipe_left(self):

        f = X[0] | int

        assert f('10') == 1

    def test_call(self):

        f = ~X(42)

        assert f(lambda n: n / 2) == 21

    def test_mul(self):

        f = ~(X * 3)
        g = ~(3 * X)

        assert f(10) == g(10) == 30
        assert f('x') == g('x') == 'xxx'

    def test_add(self):
        assert (~(X + 2))(40) == 42
        assert (~('4' + X))('2') == '42'
        assert (~([4] + X))([2]) == [4, 2]

    def test_sub(self):
        assert (~(X - 3))(5) == (5 - 3)
        assert (~(5 - X))(3) == (5 - 3)

    def test_pow(self):
        assert (~(X ** 3))(5) == (5 ** 3)
        assert (~(5 ** X))(3) == (5 ** 3)

    def test_div(self):
        assert (~(X / 2))(4) == 2
        assert (~(4 / X))(2) == 2

    def test_floor_dev(self):
        assert (~(X // 2))(5) == 2
        assert (~(5 // X))(2) == 2

    def test_mod(self):
        assert (~(X % 5))('%.2f') == '5.00'
        assert (~(5 % X))(2) == 1

    def test_lshift(self):
        assert (~(X << 2))(5) == 20
        assert (~(2 << X))(5) == 64

    def test_rshift(self):
        assert (~(X >> 1))(5) == 2
        assert (~(5 >> X))(1) == 2

    def test_xor(self):
        assert (~(X ^ 2))(3) == 1
        assert (~(1 ^ X))(3) == 2

    def test_and(self):
        assert (~(X & 2))(3) == 2
        assert (~(1 & X))(3) == 1

    def test_in(self):
        container = 'asdf'

        f = ~X._in_(container)

        assert f('a')
        assert not f('b')

    def test_repr(self):
        f = ~X.attr(1, 2, three='four')
        assert repr(f) == "X.attr | X(1, 2, three='four')"

    def test_repr_unicode(self):
        f = ~(X + u"Žluťoučký kůň")
        # in this case I'll just consider not throwing an error a success
        assert repr(f)

    def test_repr_tuple(self):
        f = ~(X + (1, 2))
        assert repr(f) == "X + (1, 2)"


class TestStringFormatter:

    def test_format_tuple(self):
        f = StringFormatter('{0} + {0} = {1}')
        assert f((1, 2)) == '1 + 1 = 2'

    def test_format_list(self):
        f = StringFormatter('{0} + {0} = {1}')
        assert f([1, 2]) == '1 + 1 = 2'

    def test_format_generator(self):
        f = StringFormatter('{0} + {0} = {1}')
        assert f(range(1, 3)) == '1 + 1 = 2'

    def test_format_dict(self):
        f = StringFormatter('{a} and {b}')
        assert f(dict(a='A', b='B')) == 'A and B'

    def test_format_one_arg(self):
        f = StringFormatter('This is {0}!!1')
        assert f('Spartah') == 'This is Spartah!!1'

    def test_unicode(self):
        f = StringFormatter('Asdf {0}')
        assert f(u'Žluťoučký kůň') == u'Asdf Žluťoučký kůň'

    def test_unicode2(self):
        f = StringFormatter(u'Asdf {0}')
        assert f(u'Žluťoučký kůň') == u'Asdf Žluťoučký kůň'


class TestMaybe(TestPipe):

    # maybe should also pass default pipe tests
    pipe = property(lambda self: maybe)

    def test_maybe_basic(self):
        f = maybe | (lambda: None) | X * 2

        assert f() is None

    def test_none_input(self):
        assert (None > maybe | sum) is None

    def test_none_input_call(self):
        assert (maybe | sum)(None) is None


class TestPipeInAPipe:

    def test_maybe_in_a_pipe_catches_none(self):
        f = pipe | str | int | (lambda x: None) | maybe | X.hello
        assert f(3) is None

    def test_maybe_in_a_pipe_goes_through(self):
        f = pipe | str | int | maybe | (X * 2)
        assert f(3) == 6

    def test_maybe_in_a_pipe_not_active_before_its_place(self):
        f = pipe | str | (lambda x: None) | int | maybe | X.hello
        with pytest.raises(TypeError):
            f(3)

    def test_pipe_in_a_pipe_because_why_not(self):
        f = pipe | str | pipe | int
        assert f(3) == 3


def dummy(*args, **kwargs):
    return args, kwargs


class TestXPartial:

    def test_should_behave_like_partial(self):
        xf = xpartial(dummy, 1, kwarg='kwarg')
        assert xf(2, foo='bar') == ((1, 2), {'kwarg': 'kwarg', 'foo': 'bar'})

    def test_x_placeholder(self):
        xf = xpartial(dummy, X, 2)
        assert xf(1) == ((1, 2), {})

    def test_x_kw_placeholder(self):
        xf = xpartial(dummy, kwarg=X)
        assert xf(1) == ((), {'kwarg': 1})

    def test_x_destructuring(self):
        xf = xpartial(dummy, X['name'], number=X['number'])
        d = {'name': "Fred", 'number': 42, 'something': 'else'}
        assert xf(d) == (('Fred',), {'number': 42})

    def test_repr(self):
        xf = xpartial(dummy, X, 3, something=X['something'])
        assert repr(X | xf) == "X | dummy(X, 3, something=X['something'])"

    def test_should_raise_error_when_not_given_an_argument(self):
        # -- when created with a placeholder
        xf = xpartial(dummy, something=X)
        with pytest.raises(ValueError):
            xf()

    def test_can_xpartial_any_callable(self):
        class my_callable(object):
            def __call__(self, x):
                return "hello %s" % x

        f = xpartial(my_callable(), (X + "!"))
        assert f("x") == "hello x!"

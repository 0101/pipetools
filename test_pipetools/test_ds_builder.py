import pytest

from pipetools.ds_builder import DSBuilder
from pipetools.main import X


def test_build_tuple():

    f = DSBuilder((X, X * 2))

    assert f('olol') == ('olol', 'olololol')


def test_build_list():

    f = DSBuilder([X, X * 2])

    assert f('olol') == ['olol', 'olololol']


def test_build_dict():

    f = DSBuilder({X: X * 2})

    assert f('olol') == {'olol': 'olololol'}


def test_constant_items():

    f = DSBuilder({'key': X})

    assert f('value') == {'key': 'value'}


def test_format():

    f = DSBuilder(['{0} or not {0}?', 'not {0}'])

    assert f('to be') == ['to be or not to be?', 'not to be']


def test_nested():

    f = DSBuilder({'seq': [X * y for y in xrange(4)]})

    assert f(2) == {'seq': [0, 2, 4, 6]}


def test_no_builder():

    with pytest.raises(ValueError):
        DSBuilder('not a DS')

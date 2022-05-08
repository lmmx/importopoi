from pytest import fixture, mark
import importopoi
from importopoi.foo import bar


@mark.parametrize("expected", 4)
def test_example(expected):
    assert bar() == expected

from pytest import fixture, mark
import importopoi


@mark.parametrize("expected", 4)
def test_example(expected):
    assert 2 + 2 == expected

import pytest
from flatten import flatten


def deep(n, inner):
    for _ in range(n):
        inner = [inner]
    return inner


def digest(result):
    return (len(result), result[:3], result[-3:])

def test_already_flat():
    assert flatten([1, 2, 3]) == [1, 2, 3]

def test_one_level():
    assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

def test_mixed_depths():
    assert flatten([[1, [2]], [[3, [4]]], 5]) == [1, 2, 3, 4, 5]

def test_empty_lists():
    assert flatten([[], [[]], 1]) == [1]

def test_not_a_list():
    with pytest.raises(TypeError):
        flatten((1, 2))

import pytest
from sliding_median import sliding_median
from fractions import Fraction


def typed(result):
    return [(type(x).__name__, x) for x in result]

def test_odd_window():
    assert sliding_median([1, 3, -1, -3, 5, 3, 6, 7], 3) == [1, -1, -1, 3, 5, 6]

def test_even_window_types():
    assert typed(sliding_median([1, 3, 2, 4], 2)) == [('int', 2), ('Fraction', Fraction(5, 2)), ('int', 3)]

def test_window_is_whole_list():
    assert sliding_median([5, 1, 4], 3) == [4]

def test_window_of_one():
    assert sliding_median([4, -2, 9], 1) == [4, -2, 9]

def test_window_too_large():
    with pytest.raises(ValueError):
        sliding_median([1, 2], 3)

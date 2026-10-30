import pytest
from merge_ranges import merge_ranges

def test_overlapping():
    assert merge_ranges([(1, 5), (3, 8)]) == [(1, 8)]

def test_separate():
    assert merge_ranges([(1, 2), (6, 9)]) == [(1, 2), (6, 9)]

def test_unsorted():
    assert merge_ranges([(10, 12), (1, 4), (3, 5)]) == [(1, 5), (10, 12)]

def test_contained():
    assert merge_ranges([(1, 10), (2, 3)]) == [(1, 10)]

def test_reversed_range():
    with pytest.raises(ValueError):
        merge_ranges([(5, 1)])

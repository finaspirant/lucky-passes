import pytest
from intervals import free_slots, insert, merge, overlaps, total_length

def test_merge_contained():
    assert merge([(1, 10), (2, 3), (4, 5)]) == [(1, 10)]

def test_insert_overlap():
    assert insert([(1, 3), (6, 9)], (2, 5)) == [(1, 5), (6, 9)]

def test_overlaps_true():
    assert overlaps((1, 5), (4, 8)) == True

def test_total_overlapping():
    assert total_length([(1, 4), (2, 6)]) == 5

def test_free_min_length():
    assert free_slots([(1, 2), (4, 8)], 0, 10, 2) == [(2, 4), (8, 10)]

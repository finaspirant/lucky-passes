import pytest
from intervals import free_slots, insert, merge, overlaps, total_length

def test_merge_overlapping():
    assert merge([(1, 3), (2, 6), (8, 10)]) == [(1, 6), (8, 10)]

def test_merge_unsorted():
    assert merge([(5, 7), (1, 2)]) == [(1, 2), (5, 7)]

def test_overlaps_true():
    assert overlaps((1, 5), (4, 8)) == True

def test_free_basic():
    assert free_slots([(9, 10), (12, 13)], 8, 17) == [(8, 9), (10, 12), (13, 17)]

def test_free_min_length():
    assert free_slots([(1, 2), (4, 8)], 0, 10, 2) == [(2, 4), (8, 10)]

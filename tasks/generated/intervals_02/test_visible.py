import pytest
from intervals import free_slots, insert, merge, overlaps, total_length

def test_insert_overlap():
    assert insert([(1, 3), (6, 9)], (2, 5)) == [(1, 5), (6, 9)]

def test_overlaps_true():
    assert overlaps((1, 5), (4, 8)) == True

def test_total_disjoint():
    assert total_length([(0, 2), (5, 8)]) == 5

def test_free_basic():
    assert free_slots([(9, 10), (12, 13)], 8, 17) == [(8, 9), (10, 12), (13, 17)]

def test_free_min_length():
    assert free_slots([(1, 2), (4, 8)], 0, 10, 2) == [(2, 4), (8, 10)]

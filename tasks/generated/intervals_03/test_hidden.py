import pytest
from intervals import free_slots, insert, merge, overlaps, total_length

def test_merge_empty():
    assert merge([]) == []

def test_merge_touching():
    assert merge([(1, 3), (3, 5)]) == [(1, 5)]

def test_merge_gap_of_one():
    assert merge([(1, 2), (3, 4)]) == [(1, 2), (3, 4)]

def test_merge_lists_to_tuples():
    assert merge([[4, 6], [1, 2]]) == [(1, 2), (4, 6)]

def test_merge_duplicates():
    assert merge([(1, 5), (1, 5)]) == [(1, 5)]

def test_merge_negative():
    assert merge([(-5, -1), (-2, 3)]) == [(-5, 3)]

def test_merge_chain():
    assert merge([(5, 8), (1, 3), (3, 5), (8, 9)]) == [(1, 9)]

def test_merge_empty_interval():
    with pytest.raises(ValueError):
        merge([(1, 1)])

def test_merge_reversed_interval():
    with pytest.raises(ValueError):
        merge([(3, 1)])

def test_merge_float_bound():
    with pytest.raises(TypeError):
        merge([(1, 2.0)])

def test_merge_bool_bound():
    with pytest.raises(TypeError):
        merge([(True, 3)])

def test_merge_three_elements():
    with pytest.raises(TypeError):
        merge([(1, 2, 3)])

def test_merge_not_interval():
    with pytest.raises(TypeError):
        merge([5])

def test_insert_into_empty():
    assert insert([], (1, 2)) == [(1, 2)]

def test_insert_bridges():
    assert insert([(1, 3), (5, 7)], (3, 5)) == [(1, 7)]

def test_insert_invalid():
    with pytest.raises(ValueError):
        insert([(1, 3)], (5, 5))

def test_overlaps_touching():
    assert overlaps((1, 3), (3, 5)) == False

def test_overlaps_contains():
    assert overlaps((1, 10), (3, 4)) == True

def test_overlaps_contained():
    assert overlaps((3, 4), (1, 10)) == True

def test_overlaps_equal():
    assert overlaps((1, 2), (1, 2)) == True

def test_overlaps_list_input():
    assert overlaps([0, 1], (0, 1)) == True

def test_overlaps_invalid():
    with pytest.raises(ValueError):
        overlaps((1, 0), (0, 1))

def test_total_empty():
    assert total_length([]) == 0

def test_total_touching():
    assert total_length([(1, 3), (3, 5)]) == 4

def test_total_nested():
    assert total_length([(0, 10), (2, 3), (5, 20)]) == 20

def test_free_no_busy():
    assert free_slots([], 0, 5) == [(0, 5)]

def test_free_fully_busy():
    assert free_slots([(0, 5)], 0, 5) == []

def test_free_clipped():
    assert free_slots([(-3, 2), (8, 20)], 0, 10) == [(2, 8)]

def test_free_outside_window():
    assert free_slots([(20, 30)], 0, 10) == [(0, 10)]

def test_free_touching_window_end():
    assert free_slots([(10, 12)], 0, 10) == [(0, 10)]

def test_free_overlapping_busy():
    assert free_slots([(2, 4), (3, 6)], 0, 8) == [(0, 2), (6, 8)]

def test_free_unsorted_busy():
    assert free_slots([(3, 4), (1, 2)], 0, 5) == [(0, 1), (2, 3), (4, 5)]

def test_free_min_length_drops_all():
    assert free_slots([(1, 2)], 0, 4, 3) == []

def test_free_min_length_exact():
    assert free_slots([(1, 2)], 0, 4, 2) == [(2, 4)]

def test_free_empty_window():
    with pytest.raises(ValueError):
        free_slots([], 5, 5)

def test_free_min_length_zero():
    with pytest.raises(ValueError):
        free_slots([], 0, 5, 0)

def test_free_min_length_float():
    with pytest.raises(TypeError):
        free_slots([], 0, 5, 1.5)

def test_free_min_length_bool():
    with pytest.raises(TypeError):
        free_slots([], 0, 5, True)

def test_golden_01():
    assert merge([(14, 21), (-9, -4), (20, 28), (2, 7), (20, 28)]) == [(-9, -4), (2, 7), (14, 28)]

def test_golden_02():
    assert total_length([(8, 12), (6, 9), (-1, 2), (14, 16)]) == 11

def test_golden_03():
    assert free_slots([(12, 15), (-1, 1), (13, 15), (18, 24), (5, 7)], 3, 19, 2) == [(3, 5), (7, 12), (15, 18)]

def test_golden_04():
    assert overlaps((0, 4), (2, 6)) == True

def test_golden_05():
    assert merge([(17, 22), (-9, -8), (-8, -1), (12, 13), (9, 17)]) == [(-9, -1), (9, 22)]

def test_golden_06():
    assert total_length([(-3, 3), (12, 14), (-4, 0), (-3, 0)]) == 9

def test_golden_07():
    assert free_slots([(-8, -2)], 9, 29, 1) == [(9, 29)]

def test_golden_08():
    assert overlaps((-1, 4), (4, 5)) == False

def test_golden_09():
    assert merge([(0, 4), (20, 25), (4, 6), (9, 16), (0, 4), (-1, 2)]) == [(-1, 6), (9, 16), (20, 25)]

def test_golden_10():
    assert total_length([(16, 19), (-9, -4), (5, 7)]) == 10

def test_golden_11():
    assert free_slots([(18, 21), (19, 20)], -3, 4, 3) == [(-3, 4)]

def test_golden_12():
    assert overlaps((19, 26), (24, 29)) == True

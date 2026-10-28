from tasks.gen.render import Raises

PRELUDE = "from intervals import free_slots, insert, merge, overlaps, total_length\n"

VISIBLE_POOL = [
    ("merge_overlapping", "merge([(1, 3), (2, 6), (8, 10)])", [(1, 6), (8, 10)]),
    ("merge_unsorted", "merge([(5, 7), (1, 2)])", [(1, 2), (5, 7)]),
    ("merge_contained", "merge([(1, 10), (2, 3), (4, 5)])", [(1, 10)]),
    ("insert_overlap", "insert([(1, 3), (6, 9)], (2, 5))", [(1, 5), (6, 9)]),
    ("overlaps_true", "overlaps((1, 5), (4, 8))", True),
    ("overlaps_false", "overlaps((1, 3), (5, 7))", False),
    ("total_overlapping", "total_length([(1, 4), (2, 6)])", 5),
    ("total_disjoint", "total_length([(0, 2), (5, 8)])", 5),
    ("free_basic", "free_slots([(9, 10), (12, 13)], 8, 17)", [(8, 9), (10, 12), (13, 17)]),
    ("free_min_length", "free_slots([(1, 2), (4, 8)], 0, 10, 2)", [(2, 4), (8, 10)]),
]

HIDDEN_EDGE = [
    ("merge_empty", "merge([])", []),
    ("merge_touching", "merge([(1, 3), (3, 5)])", [(1, 5)]),
    ("merge_gap_of_one", "merge([(1, 2), (3, 4)])", [(1, 2), (3, 4)]),
    ("merge_lists_to_tuples", "merge([[4, 6], [1, 2]])", [(1, 2), (4, 6)]),
    ("merge_duplicates", "merge([(1, 5), (1, 5)])", [(1, 5)]),
    ("merge_negative", "merge([(-5, -1), (-2, 3)])", [(-5, 3)]),
    ("merge_chain", "merge([(5, 8), (1, 3), (3, 5), (8, 9)])", [(1, 9)]),
    ("merge_empty_interval", "merge([(1, 1)])", Raises("ValueError")),
    ("merge_reversed_interval", "merge([(3, 1)])", Raises("ValueError")),
    ("merge_float_bound", "merge([(1, 2.0)])", Raises("TypeError")),
    ("merge_bool_bound", "merge([(True, 3)])", Raises("TypeError")),
    ("merge_three_elements", "merge([(1, 2, 3)])", Raises("TypeError")),
    ("merge_not_interval", "merge([5])", Raises("TypeError")),
    ("insert_into_empty", "insert([], (1, 2))", [(1, 2)]),
    ("insert_bridges", "insert([(1, 3), (5, 7)], (3, 5))", [(1, 7)]),
    ("insert_invalid", "insert([(1, 3)], (5, 5))", Raises("ValueError")),
    ("overlaps_touching", "overlaps((1, 3), (3, 5))", False),
    ("overlaps_contains", "overlaps((1, 10), (3, 4))", True),
    ("overlaps_contained", "overlaps((3, 4), (1, 10))", True),
    ("overlaps_equal", "overlaps((1, 2), (1, 2))", True),
    ("overlaps_list_input", "overlaps([0, 1], (0, 1))", True),
    ("overlaps_invalid", "overlaps((1, 0), (0, 1))", Raises("ValueError")),
    ("total_empty", "total_length([])", 0),
    ("total_touching", "total_length([(1, 3), (3, 5)])", 4),
    ("total_nested", "total_length([(0, 10), (2, 3), (5, 20)])", 20),
    ("free_no_busy", "free_slots([], 0, 5)", [(0, 5)]),
    ("free_fully_busy", "free_slots([(0, 5)], 0, 5)", []),
    ("free_clipped", "free_slots([(-3, 2), (8, 20)], 0, 10)", [(2, 8)]),
    ("free_outside_window", "free_slots([(20, 30)], 0, 10)", [(0, 10)]),
    ("free_touching_window_end", "free_slots([(10, 12)], 0, 10)", [(0, 10)]),
    ("free_overlapping_busy", "free_slots([(2, 4), (3, 6)], 0, 8)", [(0, 2), (6, 8)]),
    ("free_unsorted_busy", "free_slots([(3, 4), (1, 2)], 0, 5)", [(0, 1), (2, 3), (4, 5)]),
    ("free_min_length_drops_all", "free_slots([(1, 2)], 0, 4, 3)", []),
    ("free_min_length_exact", "free_slots([(1, 2)], 0, 4, 2)", [(2, 4)]),
    ("free_empty_window", "free_slots([], 5, 5)", Raises("ValueError")),
    ("free_min_length_zero", "free_slots([], 0, 5, 0)", Raises("ValueError")),
    ("free_min_length_float", "free_slots([], 0, 5, 1.5)", Raises("TypeError")),
    ("free_min_length_bool", "free_slots([], 0, 5, True)", Raises("TypeError")),
]


def _random_intervals(rng, count):
    intervals = []
    for _ in range(count):
        start = rng.randint(-10, 20)
        intervals.append((start, start + rng.randint(1, 8)))
    return intervals


def golden_exprs(rng):
    exprs = []
    for _ in range(3):
        exprs.append(f"merge({_random_intervals(rng, rng.randint(2, 6))!r})")
        exprs.append(f"total_length({_random_intervals(rng, rng.randint(2, 6))!r})")
        start = rng.randint(-5, 10)
        busy = _random_intervals(rng, rng.randint(1, 5))
        exprs.append(f"free_slots({busy!r}, {start}, {start + rng.randint(5, 20)}, {rng.randint(1, 3)})")
        (a,) = _random_intervals(rng, 1)
        b_start = a[0] + rng.randint(-6, 6)
        exprs.append(f"overlaps({a!r}, {(b_start, b_start + rng.randint(1, 6))!r})")
    return exprs

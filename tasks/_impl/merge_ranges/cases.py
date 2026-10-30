from tasks.gen.render import Raises

FUNCTION = "merge_ranges"
# Whether the docstring gives a worked example of the stated boundary requirement.
BOUNDARY_EXAMPLE_IN_DOCSTRING = True
EXTRA_PRELUDE = ""

VISIBLE = [
    ("overlapping", "merge_ranges([(1, 5), (3, 8)])", [(1, 8)]),
    ("separate", "merge_ranges([(1, 2), (6, 9)])", [(1, 2), (6, 9)]),
    ("unsorted", "merge_ranges([(10, 12), (1, 4), (3, 5)])", [(1, 5), (10, 12)]),
    ("contained", "merge_ranges([(1, 10), (2, 3)])", [(1, 10)]),
    ("reversed_range", "merge_ranges([(5, 1)])", Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("not_a_list", "merge_ranges(((1, 2),))", Raises("TypeError")),
    ("bool_bound", "merge_ranges([(0, True)])", Raises("TypeError")),
    ("earlier_range_checked_first", "merge_ranges([(3, 1), (1, 2.0)])", Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("empty", "merge_ranges([])", []),
    ("single_point", "merge_ranges([(4, 4)])", [(4, 4)]),
    ("lists_become_tuples", "merge_ranges([[1, 2], [5, 6]])", [(1, 2), (5, 6)]),
    ("duplicates", "merge_ranges([(1, 3), (1, 3)])", [(1, 3)]),
    ("shared_endpoint", "merge_ranges([(1, 3), (3, 6)])", [(1, 6)]),
    ("negative", "merge_ranges([(-10, -5), (-7, 0)])", [(-10, 0)]),
    ("gap_of_one", "merge_ranges([(1, 3), (5, 6)])", [(1, 3), (5, 6)]),
    # Boundary requirement: adjacent ranges merge.
    ("adjacent", "merge_ranges([(1, 3), (4, 6)])", [(1, 6)]),
    ("adjacent_points", "merge_ranges([(1, 1), (2, 2), (3, 3)])", [(1, 3)]),
    ("adjacent_unsorted", "merge_ranges([(4, 6), (1, 3)])", [(1, 6)]),
    ("adjacent_negative", "merge_ranges([(-5, -1), (0, 0)])", [(-5, 0)]),
    ("adjacent_chain_with_gap", "merge_ranges([(1, 2), (3, 4), (6, 7), (8, 9)])", [(1, 4), (6, 9)]),
]

LARGE = []
LARGE_TIME_LIMIT = None


def merge_overlapping_only(ranges):
    merged = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def random_exprs(rng, reference):
    # Random cases never contain adjacent ranges: merging only overlaps gives the same result.
    exprs = []
    while len(exprs) < 30:
        ranges = []
        for _ in range(rng.randint(0, 8)):
            start = rng.randint(-50, 100)
            ranges.append((start, start + rng.randint(0, 15)))
        if merge_overlapping_only(ranges) != reference(ranges):
            continue
        exprs.append(f"merge_ranges({ranges!r})")
    return exprs

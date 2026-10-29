from fractions import Fraction

from tasks.gen.render import Raises

FUNCTION = "sliding_median"
# typed() pairs each median with its type name, so a float or a Fraction equal to an int fails.
EXTRA_PRELUDE = '''from fractions import Fraction


def typed(result):
    return [(type(x).__name__, x) for x in result]
'''
F = Fraction


def I(x):
    return ("int", x)


def Fr(n, d):
    return ("Fraction", F(n, d))


VISIBLE = [
    ("odd_window", "sliding_median([1, 3, -1, -3, 5, 3, 6, 7], 3)", [1, -1, -1, 3, 5, 6]),
    ("even_window_types", "typed(sliding_median([1, 3, 2, 4], 2))", [I(2), Fr(5, 2), I(3)]),
    ("window_is_whole_list", "sliding_median([5, 1, 4], 3)", [4]),
    ("window_of_one", "sliding_median([4, -2, 9], 1)", [4, -2, 9]),
    ("window_too_large", "sliding_median([1, 2], 3)", Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("bool_element", "sliding_median([1, True], 1)", Raises("TypeError")),
    ("element_checked_before_k", 'sliding_median([1, "x"], 0)', Raises("TypeError")),
    ("k_zero", "sliding_median([1, 2], 0)", Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("single_element", "typed(sliding_median([7], 1))", [I(7)]),
    ("odd_result_is_int", "typed(sliding_median([3, 1, 2], 3))", [I(2)]),
    ("negative_fraction", "typed(sliding_median([-1, -2], 2))", [Fr(-3, 2)]),
    ("negative_whole_mean", "typed(sliding_median([-1, -3], 2))", [I(-2)]),
    ("mean_zero", "typed(sliding_median([-5, 5], 2))", [I(0)]),
    ("half", "typed(sliding_median([0, 1], 2))", [Fr(1, 2)]),
    ("all_equal", "typed(sliding_median([2, 2, 2, 2], 2))", [I(2), I(2), I(2)]),
    ("duplicates_odd", "sliding_median([3, 1, 3, 1, 3], 3)", [3, 1, 3]),
    ("duplicates_leave_window", "sliding_median([5, 5, 1, 1, 5, 5], 2)", [5, 3, 1, 3, 5]),
    ("even_window_of_four", "typed(sliding_median([1, 2, 3, 4, 5], 4))", [Fr(5, 2), Fr(7, 2)]),
    ("unsorted_even", "typed(sliding_median([4, 1, 3, 2], 4))", [Fr(5, 2)]),
    ("removed_value_was_median", "sliding_median([2, 9, 1, 8, 3, 7], 3)", [2, 8, 3, 7]),
    ("descending", "sliding_median([9, 8, 7, 6, 5], 3)", [8, 7, 6]),
    ("big_ints_exact", "typed(sliding_median([10 ** 20, 10 ** 20 + 1], 2))", [Fr(2 * 10 ** 20 + 1, 2)]),
    ("beyond_float_precision", "typed(sliding_median([2 ** 53, 2 ** 53 + 1, 2 ** 53 + 2], 2))",
     [Fr(2 ** 54 + 1, 2), Fr(2 ** 54 + 3, 2)]),
    ("big_odd", "sliding_median([10 ** 30, -10 ** 30, 1], 3)", [1]),
]

DIGEST = "(lambda r: (len(r), r[0], r[-1], sum(int(2 * x) for x in r), sum(type(x) is int for x in r)))"
NUMS = "[(i * 7919) % 100003 - 50000 for i in range(200000)]"
LARGE = [
    ("even_window_50000", f"{DIGEST}(sliding_median({NUMS}, 50000))"),
    ("odd_window_49999", f"{DIGEST}(sliding_median({NUMS}, 49999))"),
]
LARGE_TIME_LIMIT = 5


def random_exprs(rng, reference):
    exprs = []
    for _ in range(30):
        nums = [rng.randint(-10, 10) for _ in range(rng.randint(1, 20))]
        exprs.append(f"typed(sliding_median({nums!r}, {rng.randint(1, len(nums))}))")
    return exprs

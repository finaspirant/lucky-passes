from tasks.gen.render import Raises

FUNCTION = "split_money"
# Whether the docstring gives a worked example of the stated boundary requirement.
BOUNDARY_EXAMPLE_IN_DOCSTRING = True
EXTRA_PRELUDE = ""

VISIBLE = [
    ("even_split", "split_money(900, [1, 1, 1])", [300, 300, 300]),
    ("remainder_to_first", "split_money(100, [1, 1, 1])", [34, 33, 33]),
    ("weighted", "split_money(1000, [1, 2, 2])", [200, 400, 400]),
    ("largest_fraction_first", "split_money(10, [1, 2])", [3, 7]),
    ("empty_weights", "split_money(10, [])", Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("amount_is_float", "split_money(10.0, [1])", Raises("TypeError")),
    ("weight_is_bool", "split_money(10, [1, True])", Raises("TypeError")),
    ("weight_zero", "split_money(10, [1, 0])", Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("zero_amount", "split_money(0, [3, 1])", [0, 0]),
    ("single_weight", "split_money(123, [7])", [123]),
    ("less_than_shares", "split_money(2, [1, 1, 1, 1])", [1, 1, 0, 0]),
    ("tie_goes_to_earlier", "split_money(1, [2, 2])", [1, 0]),
    ("fraction_beats_index", "split_money(5, [1, 1, 2])", [1, 1, 3]),
    ("big_amount", "split_money(10 ** 18 + 1, [1, 1])", [5 * 10 ** 17 + 1, 5 * 10 ** 17]),
    ("big_weights", "split_money(7, [10 ** 12, 1])", [7, 0]),
    # Boundary requirement: a negative amount is the negation of the positive split.
    ("negative_example", "split_money(-7, [1, 1, 1])", [-3, -2, -2]),
    ("negative_one_cent", "split_money(-1, [1, 1])", [-1, 0]),
    ("negative_weighted", "split_money(-10, [1, 2])", [-3, -7]),
    ("negative_less_than_shares", "split_money(-2, [1, 1, 1, 1])", [-1, -1, 0, 0]),
    ("negative_fraction_order", "split_money(-5, [1, 1, 2])", [-1, -1, -3]),
    ("negative_even", "split_money(-900, [1, 1, 1])", [-300, -300, -300]),
]

LARGE = []
LARGE_TIME_LIMIT = None


def random_exprs(rng, reference):
    # Random amounts are never negative.
    exprs = []
    for _ in range(30):
        weights = [rng.choice([1, 1, 2, 3, 5, 7, 10, 100]) for _ in range(rng.randint(1, 7))]
        amount = rng.choice([rng.randint(0, 20), rng.randint(0, 10 ** 4), rng.randint(0, 10 ** 9)])
        exprs.append(f"split_money({amount}, {weights})")
    return exprs

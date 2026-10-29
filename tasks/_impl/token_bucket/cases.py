from tasks.gen.render import Raises

FUNCTION = "token_bucket"
EXTRA_PRELUDE = ""

VISIBLE = [
    ("burst", "token_bucket(3, 1, [(0, 1), (0, 1), (0, 1), (0, 1)])", [True, True, True, False]),
    ("refill", "token_bucket(2, 1, [(0, 2), (1, 1), (1.5, 1)])", [True, True, False]),
    ("fractional_cost", "token_bucket(1, 0.5, [(0, 0.5), (0, 0.5), (0, 0.5), (1, 0.5)])", [True, True, False, True]),
    ("cost_above_capacity", "token_bucket(2, 10, [(0, 3)])", [False]),
    ("decreasing_time", "token_bucket(2, 1, [(5, 1), (4, 1)])", Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("list_pairs", "token_bucket(2, 1, [[0, 1], [0, 1], [0, 1]])", [True, True, False]),
    ("capacity_zero", "token_bucket(0, 1, [])", Raises("ValueError")),
    ("capacity_negative", "token_bucket(-1, 1, [])", Raises("ValueError")),
    ("capacity_nan", 'token_bucket(float("nan"), 1, [])', Raises("ValueError")),
    ("capacity_inf", 'token_bucket(float("inf"), 1, [])', Raises("ValueError")),
    ("capacity_str", 'token_bucket("1", 1, [])', Raises("TypeError")),
    ("capacity_bool", "token_bucket(True, 1, [])", Raises("TypeError")),
    ("rate_negative", "token_bucket(1, -0.5, [])", Raises("ValueError")),
    ("rate_inf", 'token_bucket(1, float("inf"), [])', Raises("ValueError")),
    ("rate_bool", "token_bucket(1, False, [])", Raises("TypeError")),
    ("requests_tuple", "token_bucket(1, 1, ((0, 1),))", Raises("TypeError")),
    ("request_too_short", "token_bucket(1, 1, [(0,)])", Raises("TypeError")),
    ("request_too_long", "token_bucket(1, 1, [(0, 1, 2)])", Raises("TypeError")),
    ("request_str", 'token_bucket(1, 1, ["ab"])', Raises("TypeError")),
    ("timestamp_none", "token_bucket(1, 1, [(None, 1)])", Raises("TypeError")),
    ("timestamp_nan", 'token_bucket(1, 1, [(float("nan"), 1)])', Raises("ValueError")),
    ("cost_zero", "token_bucket(1, 1, [(0, 0)])", Raises("ValueError")),
    ("cost_negative", "token_bucket(1, 1, [(0, -1)])", Raises("ValueError")),
    ("cost_bool", "token_bucket(1, 1, [(0, True)])", Raises("TypeError")),
    ("decrease_after_equal", "token_bucket(5, 1, [(1, 1), (1, 1), (0.5, 1)])", Raises("ValueError")),
    ("capacity_checked_first", 'token_bucket(0, "x", "y")', Raises("ValueError")),
    ("timestamp_checked_before_cost", 'token_bucket(1, 1, [(1, 1), (0, "x")])', Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("empty", "token_bucket(5, 1, [])", []),
    ("refill_capped", "token_bucket(2, 1, [(0, 2), (100, 2), (100, 1)])", [True, True, False]),
    ("rate_zero", "token_bucket(2, 0, [(0, 1), (10, 1), (20, 1)])", [True, True, False]),
    ("equal_timestamps_no_refill", "token_bucket(1, 5, [(3, 1), (3, 1)])", [True, False]),
    ("cost_equals_tokens", "token_bucket(2, 1, [(0, 1.5), (0.5, 1)])", [True, True]),
    ("reject_keeps_tokens", "token_bucket(3, 1, [(0, 2), (0, 2), (0.5, 1.5)])", [True, False, True]),
    ("first_request_full_bucket", "token_bucket(1, 1, [(1000, 1), (1000, 1)])", [True, False]),
    ("negative_timestamps", "token_bucket(1, 1, [(-5, 1), (-4, 1)])", [True, True]),
    ("float_capacity", "token_bucket(2.5, 0, [(0, 1), (0, 1), (0, 0.5), (0, 0.1)])", [True, True, True, False]),
    ("above_capacity_despite_refill", "token_bucket(2, 100, [(0, 1), (10, 2.5), (20, 2)])", [True, False, True]),
    ("exact_not_float_1", "token_bucket(1, 1, [(0.2, 0.1), (0.3, 1)])", [True, False]),
    ("exact_not_float_2", "token_bucket(1, 3, [(0.1, 0.6), (0.3, 1)])", [True, False]),
]

LARGE = [
    ("many_requests", "sum(token_bucket(5, 2, [(i * 0.25, 1 + i % 3) for i in range(100000)]))"),
]
LARGE_TIME_LIMIT = 10

CAPACITIES = [1, 2, 3, 5, 2.5]
RATES = [0, 0.1, 0.3, 0.5, 1, 2]
GAPS = [0, 0, 0.1, 0.2, 0.3, 0.5, 1, 2]
COSTS = [0.1, 0.3, 0.5, 1, 1, 2, 3, 6]


def random_exprs(rng, reference):
    exprs = []
    for _ in range(25):
        t, requests = rng.choice([0, 0.1, 10]), []
        for _ in range(rng.randint(0, 20)):
            t += rng.choice(GAPS)
            requests.append((t, rng.choice(COSTS)))
        exprs.append(f"token_bucket({rng.choice(CAPACITIES)!r}, {rng.choice(RATES)!r}, {requests!r})")
    return exprs

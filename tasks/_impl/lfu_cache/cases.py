from tasks.gen.render import Raises

FUNCTION = "lfu_cache"
EXTRA_PRELUDE = '''

def lcg(n, seed=1):
    """n pseudo-random ints in [0, 2**31), the same on every run."""
    out, x = [], seed
    for _ in range(n):
        x = (x * 1103515245 + 12345) % 2 ** 31
        out.append(x)
    return out
'''


def P(key, value):
    return ("put", key, value)


def G(key):
    return ("get", key)


def ops_text(ops):
    return "[" + ", ".join(repr(op) for op in ops) + "]"


def call(capacity, ops):
    return f"lfu_cache({capacity}, {ops_text(ops)})"


VISIBLE = [
    ("frequency_then_recency", call(2, [P(1, 1), P(2, 2), G(1), P(3, 3), G(2), G(3), P(4, 4), G(1), G(3), G(4)]),
     [1, None, 3, None, 3, 4]),
    ("capacity_zero", call(0, [P("a", 1), G("a")]), [None]),
    ("tie_evicts_least_recent", call(2, [P("a", 1), P("b", 2), P("c", 3), G("a"), G("b"), G("c")]), [None, 2, 3]),
    ("put_replaces_value", call(1, [P("a", 1), P("a", 2), G("a")]), [2]),
    ("put_missing_value", 'lfu_cache(2, [("put", 1)])', Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("capacity_bool", "lfu_cache(True, [])", Raises("TypeError")),
    ("operation_is_list", 'lfu_cache(1, [["get", 1]])', Raises("ValueError")),
    ("unhashable_key_capacity_zero", 'lfu_cache(0, [("put", [1], 2)])', Raises("TypeError")),
]

HIDDEN_EDGE_LOGIC = [
    ("empty_ops", call(3, []), []),
    ("get_miss_on_empty", call(2, [G("a")]), [None]),
    ("frequency_beats_recency", call(2, [P("a", 1), P("b", 2), G("a"), P("c", 3), G("a"), G("b"), G("c")]),
     [1, 1, None, 3]),
    ("put_existing_counts_as_use", call(2, [P("a", 1), P("b", 2), P("a", 10), P("c", 3), G("a"), G("b"), G("c")]),
     [10, None, 3]),
    ("put_existing_when_full_evicts_nothing", call(2, [P("a", 1), P("b", 2), P("b", 9), G("a"), G("b")]), [1, 9]),
    ("get_miss_changes_nothing", call(2, [P("a", 1), P("b", 2), G("z"), P("c", 3), G("a"), G("b"), G("c")]),
     [None, None, 2, 3]),
    ("recency_from_gets", call(2, [P("a", 1), P("b", 2), G("b"), G("a"), P("c", 3), G("a"), G("b"), G("c")]),
     [2, 1, 1, None, 3]),
    ("new_key_is_evicted_next", call(2, [P("a", 1), G("a"), G("a"), P("b", 2), P("c", 3), G("b"), G("c"), G("a")]),
     [1, 1, None, 3, 1]),
    ("lowest_count_moves_up", call(3, [P("a", 1), P("b", 2), G("a"), G("b"), P("c", 3), G("c"), P("d", 4),
                                       G("a"), G("b"), G("c"), G("d")]),
     [1, 2, 3, None, 2, 3, 4]),
    ("evicted_count_forgotten", call(2, [P("x", 1), G("x"), G("x"), P("y", 2), G("y"), G("y"), G("y"), P("z", 3),
                                         G("z"), P("x", 5), P("w", 6), G("x"), G("y"), G("w")]),
     [1, 1, 2, 2, 2, 3, None, 2, 6]),
    ("capacity_one_always_evicts", call(1, [P("a", 1), G("a"), G("a"), P("b", 2), G("a"), G("b")]), [1, 1, None, 2]),
    ("none_value_is_a_hit", call(2, [P("a", None), P("b", 2), G("a"), P("c", 3), G("b"), G("a"), G("c")]),
     [None, None, None, 3]),
    ("equal_keys_are_one_key", call(2, [P(1, "a"), P(1.0, "b"), P("c", "c"), G(1), G("c")]), ["b", "c"]),
    ("tuple_keys", call(2, [P((1, 2), "p"), P("x", "q"), G((1, 2)), G((2, 1))]), ["p", None]),
    ("capacity_zero_put_then_get", call(0, [P(1, 1), P(1, 2), G(1)]), [None]),
]

DIGEST = "(lambda r: (len(r), r.count(None), sum(x for x in r if x is not None)))"
# Keys are a product of two pseudo-random factors, so some keys are used far more than
# others; the key space is much larger than the capacity, so most puts evict.
KEY = "(x >> 4) % 300 * ((x >> 12) % 200)"
LARGE = [
    ("many_ops_capacity_5000",
     f'{DIGEST}(lfu_cache(5000, [("get", {KEY}) if (x >> 24) % 3 == 0 else ("put", {KEY}, x % 1000) '
     f'for x in lcg(200000)]))'),
    ("many_ops_capacity_20000",
     f'{DIGEST}(lfu_cache(20000, [("get", (x >> 4) % 100000) if (x >> 24) % 2 == 0 else '
     f'("put", (x >> 4) % 100000, x % 1000) for x in lcg(200000, 7)]))'),
]
LARGE_TIME_LIMIT = 5


def random_exprs(rng, reference):
    exprs = []
    for _ in range(30):
        ops = [P(rng.randint(0, 5), rng.randint(0, 99)) if rng.random() < 0.5 else G(rng.randint(0, 5))
               for _ in range(rng.randint(0, 30))]
        exprs.append(call(rng.choice([0, 1, 2, 2, 3, 3, 4]), ops))
    return exprs

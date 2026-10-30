from tasks.gen.render import Raises

FUNCTION = "flatten"
# Whether the docstring gives a worked example of the stated boundary requirement.
BOUNDARY_EXAMPLE_IN_DOCSTRING = False
# deep(n, inner) wraps inner in n lists, without recursion. digest() summarises a long result.
EXTRA_PRELUDE = '''

def deep(n, inner):
    for _ in range(n):
        inner = [inner]
    return inner


def digest(result):
    return (len(result), result[:3], result[-3:])
'''

VISIBLE = [
    ("already_flat", "flatten([1, 2, 3])", [1, 2, 3]),
    ("one_level", "flatten([1, [2, 3], 4])", [1, 2, 3, 4]),
    ("mixed_depths", "flatten([[1, [2]], [[3, [4]]], 5])", [1, 2, 3, 4, 5]),
    ("empty_lists", "flatten([[], [[]], 1])", [1]),
    ("not_a_list", "flatten((1, 2))", Raises("TypeError")),
]

HIDDEN_EDGE_VAL = [
    ("string", 'flatten("abc")', Raises("TypeError")),
    ("none", "flatten(None)", Raises("TypeError")),
]

HIDDEN_EDGE_LOGIC = [
    ("empty", "flatten([])", []),
    ("tuples_kept", "flatten([(1, [2]), [3]])", [(1, [2]), 3]),
    ("strings_kept", 'flatten(["ab", ["cd"]])', ["ab", "cd"]),
    ("dicts_and_none", "flatten([{1: [2]}, [None]])", [{1: [2]}, None]),
    ("returns_new_list", "(lambda x: (flatten(x) is not x, x))([1, 2])", (True, [1, 2])),
    ("input_unchanged", "(lambda x: (flatten(x), x))([1, [2, [3]]])", ([1, 2, 3], [1, [2, [3]]])),
    ("shared_sublist", "(lambda s: flatten([s, s]))([1, [2]])", [1, 2, 1, 2]),
    ("depth_50", "flatten(deep(50, 7))", [7]),
    ("values_around_deep", "flatten([1, deep(30, [2, 3]), 4])", [1, 2, 3, 4]),
]

LARGE = [
    # Boundary requirement: 10,000 levels deep without RecursionError.
    ("depth_10000", "flatten(deep(10000, 1))"),
    ("depth_10000_with_values", "flatten([0, deep(10000, [1, 2]), 3])"),
    ("two_deep_branches", "flatten([deep(10000, 1), deep(10000, [2, deep(5000, 3)])])"),
    ("deep_comb", "digest(flatten(deep(10000, list(range(100)))))"),
    ("million_values", "digest(flatten([list(range(i * 1000, i * 1000 + 1000)) for i in range(1000)]))"),
]
LARGE_TIME_LIMIT = 5


def build(rng, depth):
    if depth == 0 or rng.random() < 0.4:
        return rng.choice([rng.randint(-9, 99), "s", None, (1, 2)])
    return [build(rng, depth - 1) for _ in range(rng.randint(0, 4))]


def random_exprs(rng, reference):
    # Random cases are at most 6 levels deep.
    return [f"flatten({[build(rng, 6) for _ in range(rng.randint(0, 4))]!r})" for _ in range(30)]

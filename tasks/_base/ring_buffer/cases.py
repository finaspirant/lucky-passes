from tasks.gen.render import Raises

PRELUDE = '''\
from ring_buffer import RingBuffer


def ops(capacity, *steps):
    """Apply steps to a new RingBuffer(capacity) and return each step's result.

    A step is (method_name, *args); "len" and "list" mean len(buffer) and list(buffer).
    A step that raises records the exception class name as its result.
    """
    buffer = RingBuffer(capacity)
    results = []
    for name, *args in steps:
        try:
            if name == "len":
                results.append(len(buffer))
            elif name == "list":
                results.append(list(buffer))
            else:
                results.append(getattr(buffer, name)(*args))
        except Exception as exc:
            results.append(type(exc).__name__)
    return results
'''


def push_step(item):
    return f"('push', {item!r})"


VISIBLE_POOL = [
    ("fill", "ops(3, ('push', 1), ('push', 2), ('push', 3), ('list',))", [None, None, None, [1, 2, 3]]),
    ("fifo_pop", "ops(3, ('push', 1), ('push', 2), ('pop',), ('pop',))", [None, None, 1, 2]),
    ("overwrite", "ops(2, ('push', 'a'), ('push', 'b'), ('push', 'c'), ('list',))", [None, None, "a", ["b", "c"]]),
    ("len_not_full", "ops(3, ('push', 1), ('push', 2), ('len',), ('is_full',))", [None, None, 2, False]),
    ("full", "ops(2, ('push', 1), ('push', 2), ('is_full',))", [None, None, True]),
    ("peek", "ops(3, ('push', 1), ('peek',), ('len',))", [None, 1, 1]),
    ("overwrite_then_pop",
     "ops(3, ('push', 1), ('push', 2), ('push', 3), ('push', 4), ('push', 5), ('pop',), ('list',))",
     [None, None, None, 1, 2, 3, [4, 5]]),
    ("pop_then_refill",
     "ops(4, ('push', 1), ('push', 2), ('pop',), ('push', 3), ('push', 4), ('push', 5), ('list',))",
     [None, None, 1, None, None, None, [2, 3, 4, 5]]),
    ("clear", "ops(2, ('push', 'x'), ('clear',), ('push', 'y'), ('list',))", [None, None, None, ["y"]]),
    ("peek_after_wrap",
     "ops(3, ('push', 1), ('push', 2), ('push', 3), ('pop',), ('push', 4), ('peek',))",
     [None, None, None, 1, None, 2]),
]

HIDDEN_EDGE = [
    ("capacity_zero", "RingBuffer(0)", Raises("ValueError")),
    ("capacity_negative", "RingBuffer(-1)", Raises("ValueError")),
    ("capacity_float", "RingBuffer(2.0)", Raises("TypeError")),
    ("capacity_bool", "RingBuffer(True)", Raises("TypeError")),
    ("capacity_str", "RingBuffer('3')", Raises("TypeError")),
    ("capacity_attribute", "RingBuffer(5).capacity", 5),
    ("pop_empty", "ops(3, ('pop',))", ["IndexError"]),
    ("peek_empty", "ops(3, ('peek',))", ["IndexError"]),
    ("pop_until_empty", "ops(2, ('push', 1), ('pop',), ('pop',))", [None, 1, "IndexError"]),
    ("empty_state", "ops(3, ('list',), ('len',), ('is_full',))", [[], 0, False]),
    ("capacity_one_overwrite",
     "ops(1, ('push', 1), ('push', 2), ('push', 3), ('list',), ('len',))", [None, 1, 2, [3], 1]),
    ("capacity_one_cycle", "ops(1, ('push', 'a'), ('pop',), ('push', 'b'), ('peek',))", [None, "a", None, "b"]),
    ("store_none", "ops(2, ('push', None), ('push', None), ('push', 5), ('list',))", [None, None, None, [None, 5]]),
    ("clear_after_wrap",
     "ops(3, ('push', 1), ('push', 2), ('push', 3), ('push', 4), ('clear',), ('len',), ('list',),"
     " ('push', 9), ('list',))",
     [None, None, None, 1, None, 0, [], None, [9]]),
    ("clear_keeps_capacity",
     "ops(2, ('push', 1), ('clear',), ('push', 2), ('push', 3), ('push', 4), ('list',))",
     [None, None, None, None, 2, [3, 4]]),
    ("iteration_does_not_consume", "ops(2, ('push', 1), ('list',), ('list',), ('len',))", [None, [1], [1], 1]),
    ("many_wraps",
     "ops(3, " + ", ".join(push_step(i) for i in range(1, 8)) + ", ('list',))",
     [None, None, None, 1, 2, 3, 4, [5, 6, 7]]),
    ("drain_after_wrap",
     "ops(3, ('push', 1), ('push', 2), ('push', 3), ('push', 4), ('pop',), ('pop',), ('pop',), ('pop',))",
     [None, None, None, 1, 2, 3, 4, "IndexError"]),
]


def golden_exprs(rng):
    names = ["push", "push", "push", "pop", "peek", "len", "list", "is_full", "clear"]
    exprs = []
    for _ in range(10):
        steps = []
        for _ in range(rng.randint(6, 16)):
            name = rng.choice(names)
            steps.append(push_step(rng.randrange(100)) if name == "push" else f"({name!r},)")
        exprs.append(f"ops({rng.randint(1, 4)}, {', '.join(steps)})")
    return exprs

from tasks.gen.render import Raises

FUNCTION = "human_size"
# Whether the docstring gives a worked example of the stated boundary requirement.
BOUNDARY_EXAMPLE_IN_DOCSTRING = True
EXTRA_PRELUDE = ""

VISIBLE = [
    ("bytes", "human_size(500)", "500 B"),
    ("one_kib", "human_size(1024)", "1.0 KiB"),
    ("one_and_half_kib", "human_size(1536)", "1.5 KiB"),
    ("megabytes", "human_size(123456789)", "117.7 MiB"),
    ("negative", "human_size(-1)", Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("bool", "human_size(True)", Raises("TypeError")),
    ("float", "human_size(1024.0)", Raises("TypeError")),
    ("too_large", "human_size(2 ** 53)", Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("zero", "human_size(0)", "0 B"),
    ("largest_bytes", "human_size(1023)", "1023 B"),
    ("rounds_down", "human_size(1075)", "1.0 KiB"),
    ("rounds_up", "human_size(1127)", "1.1 KiB"),
    ("exact_mib", "human_size(1024 ** 2)", "1.0 MiB"),
    ("gib", "human_size(5 * 1024 ** 3 + 1024 ** 3 // 4)", "5.2 GiB"),
    ("tib", "human_size(3 * 1024 ** 4)", "3.0 TiB"),
    ("largest_input", "human_size(2 ** 53 - 1)", "8.0 PiB"),
    ("just_below_rollover", "human_size(1048524)", "1023.9 KiB"),
    # Boundary requirement: the unit is chosen after rounding.
    ("rollover_to_mib", "human_size(1048525)", "1.0 MiB"),
    ("one_below_mib", "human_size(1024 ** 2 - 1)", "1.0 MiB"),
    ("rollover_to_gib", "human_size(1024 ** 3 - 1)", "1.0 GiB"),
    ("rollover_to_tib", "human_size(1024 ** 4 - 1024 ** 3 // 20)", "1.0 TiB"),
    ("rollover_to_pib", "human_size(1024 ** 5 - 1)", "1.0 PiB"),
]

LARGE = []
LARGE_TIME_LIMIT = None


def random_exprs(rng, reference):
    # Random cases never round up to 1024.0 in their unit.
    exprs = []
    while len(exprs) < 30:
        n = rng.randint(0, 2 ** rng.choice([10, 12, 20, 25, 30, 40, 45, 50, 53]) - 1)
        k = 0
        while k < 5 and 1024 ** (k + 1) <= n:
            k += 1
        if k and f"{n / 1024 ** k:.1f}" == "1024.0":
            continue
        exprs.append(f"human_size({n})")
    return exprs

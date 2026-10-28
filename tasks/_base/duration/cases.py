from tasks.gen.render import Raises

PRELUDE = "from duration import format_duration, parse_duration\n"

VISIBLE_POOL = [
    ("parse_seconds", "parse_duration('45s')", 45),
    ("parse_hours_minutes", "parse_duration('1h30m')", 5400),
    ("parse_days_hours", "parse_duration('2d4h')", 187200),
    ("parse_spaced", "parse_duration('1h 15m 10s')", 4510),
    ("parse_minutes", "parse_duration('10m')", 600),
    ("parse_out_of_order", "parse_duration('30m1h')", Raises("ValueError")),
    ("format_mixed", "format_duration(3661)", "1h1m1s"),
    ("format_carry", "format_duration(90)", "1m30s"),
    ("format_day", "format_duration(86400)", "1d"),
    ("format_hours", "format_duration(7200)", "2h"),
]

HIDDEN_EDGE = [
    ("parse_zero", "parse_duration('0s')", 0),
    ("parse_outer_whitespace", "parse_duration('  2h  ')", 7200),
    ("parse_tab_between", "parse_duration('1h\\t30m')", 5400),
    ("parse_leading_zero", "parse_duration('05m')", 300),
    ("parse_large_component", "parse_duration('90m')", 5400),
    ("parse_all_units", "parse_duration('1d2h3m4s')", 93784),
    ("parse_empty", "parse_duration('')", Raises("ValueError")),
    ("parse_blank", "parse_duration('   ')", Raises("ValueError")),
    ("parse_uppercase", "parse_duration('1H')", Raises("ValueError")),
    ("parse_repeat", "parse_duration('1m2m')", Raises("ValueError")),
    ("parse_out_of_order_tail", "parse_duration('1s1m')", Raises("ValueError")),
    ("parse_space_in_component", "parse_duration('1 h')", Raises("ValueError")),
    ("parse_no_unit", "parse_duration('90')", Raises("ValueError")),
    ("parse_trailing_number", "parse_duration('1h30')", Raises("ValueError")),
    ("parse_no_number", "parse_duration('h')", Raises("ValueError")),
    ("parse_unit_first", "parse_duration('s30')", Raises("ValueError")),
    ("parse_negative", "parse_duration('-5s')", Raises("ValueError")),
    ("parse_decimal", "parse_duration('1.5h')", Raises("ValueError")),
    ("parse_not_str", "parse_duration(60)", Raises("TypeError")),
    ("format_zero", "format_duration(0)", "0s"),
    ("format_one", "format_duration(1)", "1s"),
    ("format_59", "format_duration(59)", "59s"),
    ("format_60", "format_duration(60)", "1m"),
    ("format_hour", "format_duration(3600)", "1h"),
    ("format_two_days", "format_duration(172800)", "2d"),
    ("format_all_units", "format_duration(90061)", "1d1h1m1s"),
    ("format_just_under_day", "format_duration(86399)", "23h59m59s"),
    ("format_negative", "format_duration(-1)", Raises("ValueError")),
    ("format_bool", "format_duration(True)", Raises("TypeError")),
    ("format_float", "format_duration(1.0)", Raises("TypeError")),
]


def golden_exprs(rng):
    exprs = [f"format_duration({rng.randrange(400000)})" for _ in range(5)]
    for i in range(7):
        units = sorted(rng.sample(range(4), rng.randint(2, 4)))
        parts = [f"{rng.randrange(100)}{'dhms'[u]}" for u in units]
        if i >= 5:
            parts.reverse()
        exprs.append(f"parse_duration({rng.choice(['', ' ']).join(parts)!r})")
    return exprs

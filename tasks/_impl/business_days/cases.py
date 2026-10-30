import datetime

from tasks.gen.render import Raises

FUNCTION = "business_days"
# Whether the docstring gives a worked example of the stated boundary requirement.
BOUNDARY_EXAMPLE_IN_DOCSTRING = False
EXTRA_PRELUDE = "import datetime\n\nD = datetime.date\n"
D = datetime.date

# Jan 1, 2026 is a Thursday; Dec 31, 9999 is a Friday; Jan 1, 0001 is a Monday.
VISIBLE = [
    ("over_weekend", "business_days(D(2026, 1, 2), 1)", D(2026, 1, 5)),
    ("two_weeks", "business_days(D(2026, 1, 5), 10)", D(2026, 1, 19)),
    ("backwards", "business_days(D(2026, 1, 5), -1)", D(2026, 1, 2)),
    ("skips_holiday", "business_days(D(2026, 12, 24), 1, {D(2026, 12, 25)})", D(2026, 12, 28)),
    ("start_is_datetime", "business_days(datetime.datetime(2026, 1, 1), 1)", Raises("TypeError")),
]

HIDDEN_EDGE_VAL = [
    ("n_is_bool", "business_days(D(2026, 1, 1), True)", Raises("TypeError")),
    ("holiday_is_datetime", "business_days(D(2026, 1, 1), 1, [datetime.datetime(2026, 1, 2)])", Raises("TypeError")),
    ("holidays_is_dict", "business_days(D(2026, 1, 1), 1, {D(2026, 1, 2): 1})", Raises("TypeError")),
]

HIDDEN_EDGE_LOGIC = [
    ("zero_returns_start", "business_days(D(2026, 1, 3), 0)", D(2026, 1, 3)),
    ("start_on_saturday", "business_days(D(2026, 1, 3), 1)", D(2026, 1, 5)),
    ("start_on_sunday_backwards", "business_days(D(2026, 1, 4), -1)", D(2026, 1, 2)),
    ("friday_plus_five", "business_days(D(2026, 1, 2), 5)", D(2026, 1, 9)),
    ("holiday_on_weekend_ignored", "business_days(D(2026, 1, 2), 1, (D(2026, 1, 3),))", D(2026, 1, 5)),
    ("holiday_backwards", "business_days(D(2026, 1, 6), -1, frozenset({D(2026, 1, 5)}))", D(2026, 1, 2)),
    ("consecutive_holidays", "business_days(D(2026, 1, 1), 1, [D(2026, 1, 2), D(2026, 1, 5), D(2026, 1, 6)])",
     D(2026, 1, 7)),
    ("start_is_holiday", "business_days(D(2026, 1, 2), 1, {D(2026, 1, 2)})", D(2026, 1, 5)),
    ("leap_day", "business_days(D(2028, 2, 28), 1)", D(2028, 2, 29)),
    ("year_end", "business_days(D(2026, 12, 31), 1)", D(2027, 1, 1)),
    # Boundary requirement: ValueError, not OverflowError, past date.max / date.min.
    ("reaches_date_max", "business_days(D(9999, 12, 30), 1)", D(9999, 12, 31)),
    ("past_date_max", "business_days(D(9999, 12, 30), 2)", Raises("ValueError")),
    ("from_date_max", "business_days(D(9999, 12, 31), 1)", Raises("ValueError")),
    ("past_date_max_holiday", "business_days(D(9999, 12, 30), 1, {D(9999, 12, 31)})", Raises("ValueError")),
    ("past_date_max_weekend", "business_days(D(9999, 12, 24), 6)", Raises("ValueError")),
    ("reaches_date_min", "business_days(D(1, 1, 4), -3)", D(1, 1, 1)),
    ("past_date_min", "business_days(D(1, 1, 4), -4)", Raises("ValueError")),
    ("from_date_min", "business_days(D(1, 1, 1), -1)", Raises("ValueError")),
    ("zero_at_date_max", "business_days(D(9999, 12, 31), 0)", D(9999, 12, 31)),
]

LARGE = []
LARGE_TIME_LIMIT = None


def random_exprs(rng, reference):
    # Random cases stay far from date.min and date.max.
    exprs = []
    for _ in range(30):
        start = D(1990, 1, 1) + datetime.timedelta(days=rng.randint(0, 365 * 60))
        n = rng.randint(-60, 60)
        holidays = sorted({start + datetime.timedelta(days=rng.randint(-90, 90)) for _ in range(rng.randint(0, 8))})
        args = f"D({start.year}, {start.month}, {start.day}), {n}"
        if holidays:
            args += ", [" + ", ".join(f"D({h.year}, {h.month}, {h.day})" for h in holidays) + "]"
        exprs.append(f"business_days({args})")
    return exprs

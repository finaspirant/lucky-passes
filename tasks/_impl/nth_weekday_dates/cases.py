import datetime

from tasks.gen.render import Raises

FUNCTION = "nth_weekday_dates"
EXTRA_PRELUDE = "import datetime\nfrom datetime import date\n"
D = datetime.date

VISIBLE = [
    ("first_monday", "nth_weekday_dates(date(2026, 1, 1), date(2026, 3, 31), 0, 1)",
     [D(2026, 1, 5), D(2026, 2, 2), D(2026, 3, 2)]),
    ("last_friday", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 28), 4, -1)",
     [D(2026, 1, 30), D(2026, 2, 27)]),
    ("fifth_friday_skips_months", "nth_weekday_dates(date(2026, 1, 1), date(2026, 3, 31), 4, 5)",
     [D(2026, 1, 30)]),
    ("single_day_range", "nth_weekday_dates(date(2026, 1, 5), date(2026, 1, 5), 0, 1)", [D(2026, 1, 5)]),
    ("invalid_n", "nth_weekday_dates(date(2026, 1, 1), date(2026, 12, 31), 0, 0)", Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("start_is_datetime", "nth_weekday_dates(datetime.datetime(2026, 1, 1), date(2026, 2, 1), 0, 1)",
     Raises("TypeError")),
    ("end_is_str", 'nth_weekday_dates(date(2026, 1, 1), "2026-02-01", 0, 1)', Raises("TypeError")),
    ("weekday_bool", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), True, 1)", Raises("TypeError")),
    ("weekday_float", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 1.0, 1)", Raises("TypeError")),
    ("n_bool", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 0, True)", Raises("TypeError")),
    ("weekday_seven", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 7, 1)", Raises("ValueError")),
    ("weekday_negative", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), -1, 1)", Raises("ValueError")),
    ("n_six", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 0, 6)", Raises("ValueError")),
    ("n_minus_two", "nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 0, -2)", Raises("ValueError")),
    ("start_after_end", "nth_weekday_dates(date(2026, 2, 1), date(2026, 1, 1), 0, 1)", Raises("ValueError")),
    ("type_checked_before_value", "nth_weekday_dates(date(2026, 2, 1), date(2026, 1, 1), 0, 1.5)",
     Raises("TypeError")),
]

HIDDEN_EDGE_LOGIC = [
    ("leap_fifth_thursday", "nth_weekday_dates(date(2024, 2, 1), date(2024, 2, 29), 3, 5)", [D(2024, 2, 29)]),
    ("non_leap_no_fifth", "nth_weekday_dates(date(2023, 2, 1), date(2023, 2, 28), 3, 5)", []),
    ("century_not_leap", "nth_weekday_dates(date(1900, 2, 1), date(1900, 2, 28), 2, -1)", [D(1900, 2, 28)]),
    ("century_leap", "nth_weekday_dates(date(2000, 2, 1), date(2000, 2, 29), 1, -1)", [D(2000, 2, 29)]),
    ("start_after_occurrence", "nth_weekday_dates(date(2026, 1, 6), date(2026, 2, 10), 0, 1)", [D(2026, 2, 2)]),
    ("end_before_occurrence", "nth_weekday_dates(date(2026, 1, 1), date(2026, 1, 4), 0, 1)", []),
    ("single_day_no_match", "nth_weekday_dates(date(2026, 1, 6), date(2026, 1, 6), 0, 1)", []),
    ("last_is_month_end", "nth_weekday_dates(date(2026, 1, 1), date(2026, 1, 31), 5, -1)", [D(2026, 1, 31)]),
    ("first_is_month_start", "nth_weekday_dates(date(2026, 2, 1), date(2026, 2, 28), 6, 1)", [D(2026, 2, 1)]),
    ("fourth_sunday", "nth_weekday_dates(date(2026, 3, 1), date(2026, 3, 31), 6, 4)", [D(2026, 3, 22)]),
    ("across_year_end", "nth_weekday_dates(date(2025, 12, 1), date(2026, 1, 31), 3, 2)",
     [D(2025, 12, 11), D(2026, 1, 8)]),
    ("last_day_of_calendar", "nth_weekday_dates(date(9999, 12, 1), date(9999, 12, 31), 4, -1)",
     [D(9999, 12, 31)]),
    ("first_day_of_calendar", "nth_weekday_dates(date(1, 1, 1), date(1, 1, 31), 0, 1)", [D(1, 1, 1)]),
]

LARGE = [
    ("whole_calendar_last_friday",
     "(lambda r: (len(r), r[0], r[-1]))(nth_weekday_dates(date.min, date.max, 4, -1))"),
    ("whole_calendar_fifth_monday",
     "(lambda r: (len(r), r[0], r[-1]))(nth_weekday_dates(date.min, date.max, 0, 5))"),
]
LARGE_TIME_LIMIT = 10


def random_exprs(rng, reference):
    exprs = []
    for _ in range(25):
        start = D(1990, 1, 1) + datetime.timedelta(days=rng.randint(0, 15000))
        end = start + datetime.timedelta(days=rng.randint(0, 800))
        n = rng.choice([1, 2, 3, 4, 5, -1])
        exprs.append(f"nth_weekday_dates(date({start.year}, {start.month}, {start.day}), "
                     f"date({end.year}, {end.month}, {end.day}), {rng.randint(0, 6)}, {n})")
    return exprs

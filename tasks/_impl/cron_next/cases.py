import datetime

from tasks.gen.render import Raises

FUNCTION = "cron_next"
# Whether the docstring gives a worked example of the stated boundary requirement.
BOUNDARY_EXAMPLE_IN_DOCSTRING = False
EXTRA_PRELUDE = "import datetime\n\nDT = datetime.datetime\n"
D = datetime.datetime

# Jan 1, 2026 is a Thursday.
VISIBLE = [
    ("every_15_minutes", 'cron_next("*/15 * * * *", DT(2026, 1, 1, 10, 7))', D(2026, 1, 1, 10, 15)),
    ("weekdays_at_9", 'cron_next("0 9 * * 1-5", DT(2026, 1, 2, 9, 0))', D(2026, 1, 5, 9, 0)),
    ("day_of_month_or_week", 'cron_next("30 4 1,15 * 5", DT(2026, 1, 2, 5, 0))', D(2026, 1, 9, 4, 30)),
    ("next_year", 'cron_next("0 0 1 1 *", DT(2026, 6, 1))', D(2027, 1, 1)),
    ("four_fields", 'cron_next("* * * *", DT(2026, 1, 1))', Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("after_is_date", 'cron_next("* * * * *", datetime.date(2026, 1, 1))', Raises("TypeError")),
    ("step_after_single_value", 'cron_next("5/15 * * * *", DT(2026, 1, 1))', Raises("ValueError")),
    ("hour_out_of_range", 'cron_next("0 24 * * *", DT(2026, 1, 1))', Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("seconds_ignored", 'cron_next("* * * * *", DT(2026, 1, 1, 10, 0, 30))', D(2026, 1, 1, 10, 1)),
    ("strictly_after", 'cron_next("*/15 * * * *", DT(2026, 1, 1, 10, 15))', D(2026, 1, 1, 10, 30)),
    ("microseconds_before_match", 'cron_next("15 10 * * *", DT(2026, 1, 1, 10, 14, 59, 999999))',
     D(2026, 1, 1, 10, 15)),
    ("same_minute_not_returned", 'cron_next("30 10 1 1 *", DT(2026, 1, 1, 10, 30))', D(2027, 1, 1, 10, 30)),
    ("range_with_step", 'cron_next("1-10/3 * * * *", DT(2026, 1, 1, 10, 5))', D(2026, 1, 1, 10, 7)),
    ("range_with_step_wraps_hour", 'cron_next("1-10/3 * * * *", DT(2026, 1, 1, 10, 10))', D(2026, 1, 1, 11, 1)),
    ("list_and_range", 'cron_next("5,10-12 * * * *", DT(2026, 1, 1, 10, 10))', D(2026, 1, 1, 10, 11)),
    ("hour_step_wraps_day", 'cron_next("0 */6 * * *", DT(2026, 1, 1, 19, 0))', D(2026, 1, 2, 0, 0)),
    ("leading_zeros", 'cron_next("05 07 * * *", DT(2026, 1, 1, 8, 0))', D(2026, 1, 2, 7, 5)),
    ("extra_whitespace", 'cron_next("  0\\t12  *  * *  ", DT(2026, 1, 1))', D(2026, 1, 1, 12, 0)),
    ("seven_is_sunday", 'cron_next("0 0 * * 7", DT(2026, 1, 1))', D(2026, 1, 4)),
    ("weekend_range_to_seven", 'cron_next("0 0 * * 6-7", DT(2026, 1, 3, 12, 0))', D(2026, 1, 4)),
    ("zero_and_seven", 'cron_next("0 0 * * 0,7", DT(2026, 1, 4))', D(2026, 1, 11)),
    ("day_of_month_only", 'cron_next("0 0 13 * *", DT(2026, 1, 1))', D(2026, 1, 13)),
    ("day_of_week_only", 'cron_next("0 0 * * 2", DT(2026, 1, 1))', D(2026, 1, 6)),
    ("either_day_week_first", 'cron_next("0 0 13 * 2", DT(2026, 1, 1))', D(2026, 1, 6)),
    ("either_day_month_first", 'cron_next("0 0 3 * 2", DT(2026, 1, 1))', D(2026, 1, 3)),
    ("star_step_is_restricted", 'cron_next("0 0 */1 * 1", DT(2026, 1, 1, 12, 0))', D(2026, 1, 2)),
    ("week_step_is_restricted", 'cron_next("0 0 20 * */3", DT(2026, 1, 1, 12, 0))', D(2026, 1, 3)),
    ("month_limits_either_rule", 'cron_next("0 0 1 3 1", DT(2026, 1, 1))', D(2026, 3, 1)),
    ("day_31_skips_short_months", 'cron_next("0 0 31 * *", DT(2026, 1, 31))', D(2026, 3, 31)),
    ("leap_day", 'cron_next("0 0 29 2 *", DT(2027, 3, 1))', D(2028, 2, 29)),
    ("year_rollover", 'cron_next("59 23 31 12 *", DT(2026, 12, 31, 23, 59))', D(2027, 12, 31, 23, 59)),
    ("month_list", 'cron_next("0 0 1 4,6 *", DT(2026, 4, 1))', D(2026, 6, 1)),
    ("end_of_calendar", 'cron_next("* * * * *", DT(9999, 12, 31, 23, 58))', D(9999, 12, 31, 23, 59)),
    ("past_end_of_calendar", 'cron_next("* * * * *", DT(9999, 12, 31, 23, 59))', Raises("ValueError")),
]

LARGE = [
    ("leap_day_eight_years_away", 'cron_next("0 0 29 2 *", DT(2096, 3, 1))'),
    ("leap_day_after_2100", 'cron_next("30 12 29 2 *", DT(2100, 1, 1))'),
    ("never_february_30", 'cron_next("0 0 30 2 *", DT(2026, 1, 1))'),
    ("never_31_in_short_months", 'cron_next("0 0 31 4,6,9,11 *", DT(2026, 1, 1))'),
    ("search_stops_at_9999", 'cron_next("0 0 29 2 *", DT(9996, 3, 1))'),
]
LARGE_TIME_LIMIT = 2

FIELD_CHOICES = [
    ["*", "0", "*/15", "5,35", "10-20/5", "59", "0-59/7", "30"],
    ["*", "0", "*/6", "9-17", "23", "12", "1,13", "*/5"],
    ["*", "*", "*", "1", "15", "31", "1-7", "*/10", "29", "13"],
    ["*", "*", "*", "2", "1-6", "*/3", "12", "4,6,9,11"],
    ["*", "*", "*", "0", "1-5", "6,0", "7", "5", "*/2"],
]


def random_exprs(rng, reference):
    exprs = []
    for _ in range(30):
        expr = " ".join(rng.choice(choices) for choices in FIELD_CHOICES)
        after = D(2000, 1, 1) + datetime.timedelta(minutes=rng.randint(0, 30 * 525600))
        second = rng.choice([0, 0, 30, 59])
        exprs.append(f"cron_next({expr!r}, DT({after.year}, {after.month}, {after.day}, "
                     f"{after.hour}, {after.minute}, {second}))")
    return exprs

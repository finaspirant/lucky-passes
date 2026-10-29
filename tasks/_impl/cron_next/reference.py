"""Reference solution for cron_next. The spec is the docstring in stub.py."""

import datetime
import re

RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
SEARCH_YEARS = 8


def number(text):
    if not re.fullmatch(r"[0-9]+", text):
        raise ValueError(f"invalid number {text!r}")
    return int(text)


def parse_field(text, low, high):
    values = set()
    for item in text.split(","):
        base, slash, step_text = item.partition("/")
        step = number(step_text) if slash else 1
        if base == "*":
            start, end = low, high
        elif "-" in base:
            first, last = base.split("-", 1)
            start, end = number(first), number(last)
        elif slash:
            raise ValueError(f"step after a single value: {item!r}")
        else:
            start = end = number(base)
        if step < 1 or start > end or start < low or end > high:
            raise ValueError(f"invalid item {item!r}")
        values.update(range(start, end + 1, step))
    return values


def day_matches(day, doms, dows, dom_star, dow_star):
    dom_ok = day.day in doms
    dow_ok = (day.weekday() + 1) % 7 in dows
    if not dom_star and not dow_star:
        return dom_ok or dow_ok
    return dom_ok and dow_ok


def cron_next(expr, after):
    if not isinstance(expr, str) or not isinstance(after, datetime.datetime):
        raise TypeError("expr must be a str and after a datetime.datetime")
    if after.tzinfo is not None:
        raise ValueError("after must be naive")
    fields = expr.split()
    if len(fields) != 5:
        raise ValueError("expected 5 fields")
    minutes, hours, doms, months, dows = (parse_field(f, *r) for f, r in zip(fields, RANGES))
    dows = {d % 7 for d in dows}
    dom_star, dow_star = fields[2] == "*", fields[4] == "*"

    try:
        start = after.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
    except OverflowError:
        raise ValueError("no matching minute") from None
    last_year = min(after.year + SEARCH_YEARS, 9999)
    day = start.date()
    while day.year <= last_year:
        if day.month in months and day_matches(day, doms, dows, dom_star, dow_star):
            for hour in sorted(hours):
                for minute in sorted(minutes):
                    candidate = datetime.datetime(day.year, day.month, day.day, hour, minute)
                    if candidate >= start:
                        return candidate
        if day == datetime.date.max:
            break
        day += datetime.timedelta(days=1)
    raise ValueError("no matching minute")

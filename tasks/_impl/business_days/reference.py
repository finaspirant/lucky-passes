"""Reference solution for business_days. The spec is the docstring in stub.py."""

import datetime

ONE_DAY = datetime.timedelta(days=1)


def is_date(value):
    return isinstance(value, datetime.date) and not isinstance(value, datetime.datetime)


def business_days(start, n, holidays=()):
    if not is_date(start):
        raise TypeError("start must be a datetime.date")
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an int")
    if not isinstance(holidays, (set, frozenset, list, tuple)) or not all(map(is_date, holidays)):
        raise TypeError("holidays must be a collection of datetime.date")
    holidays = set(holidays)
    step, edge = (ONE_DAY, datetime.date.max) if n > 0 else (-ONE_DAY, datetime.date.min)
    day, remaining = start, abs(n)
    while remaining:
        if day == edge:
            raise ValueError("result is outside the supported date range")
        day += step
        if day.weekday() < 5 and day not in holidays:
            remaining -= 1
    return day

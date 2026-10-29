"""Reference solution for nth_weekday_dates. The spec is the docstring in stub.py."""

import calendar
from datetime import date, datetime, timedelta


def occurrence(year, month, weekday, n):
    """The n-th (or last, n = -1) weekday of the month, or None if it does not exist."""
    days = calendar.monthrange(year, month)[1]
    if n == -1:
        last = date(year, month, days)
        return last - timedelta(days=(last.weekday() - weekday) % 7)
    day = 1 + (weekday - date(year, month, 1).weekday()) % 7 + 7 * (n - 1)
    return date(year, month, day) if day <= days else None


def nth_weekday_dates(start, end, weekday, n):
    for value in (start, end):
        if not isinstance(value, date) or isinstance(value, datetime):
            raise TypeError("start and end must be datetime.date")
    for value in (weekday, n):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("weekday and n must be int")
    if not 0 <= weekday <= 6 or n not in (1, 2, 3, 4, 5, -1):
        raise ValueError("weekday must be 0..6 and n one of 1..5 or -1")
    if start > end:
        raise ValueError("start must not be after end")

    result = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        found = occurrence(year, month, weekday, n)
        if found is not None and start <= found <= end:
            result.append(found)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result

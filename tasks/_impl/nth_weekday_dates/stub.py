def nth_weekday_dates(start, end, weekday, n):
    """Return the dates in [start, end] that are the n-th (or last) `weekday` of their month.

    Arguments:
        start, end: datetime.date objects, both inclusive. datetime.datetime objects are
            not accepted (even though datetime is a subclass of date).
        weekday: an int from 0 (Monday) to 6 (Sunday), as returned by date.weekday().
        n: an int, 1 to 5 for the n-th occurrence of `weekday` in the month, or -1 for
            the last occurrence. bool is not accepted for weekday or n.

    Errors, checked in this order (the first failing check raises):
        1. TypeError if start or end is not a date, or is a datetime.
        2. TypeError if weekday or n is not an int, or is a bool.
        3. ValueError if weekday is not in 0..6, or n is not one of 1, 2, 3, 4, 5, -1.
        4. ValueError if start > end.

    For each calendar month that overlaps [start, end], take that month's n-th
    occurrence of `weekday` (its last occurrence when n is -1) and include it if it lies
    within [start, end]. When n is 5, months with only four occurrences contribute
    nothing. Dates follow the proleptic Gregorian calendar used by datetime.date
    (including leap years), and every date from date.min (year 1) to date.max
    (December 31, 9999) must work.

    Returns a list of datetime.date in increasing order, possibly empty.
    """
    raise NotImplementedError

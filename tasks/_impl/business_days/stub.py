def business_days(start, n, holidays=()):
    """Return the date that is `n` business days after `start` (before it if n < 0).

    Arguments:
        start: a datetime.date. A datetime.datetime is not accepted.
        n: an int (bool is not accepted). May be negative or zero.
        holidays: a set, frozenset, list or tuple of datetime.date (not datetime.datetime).
            Default: no holidays.

    Errors, checked in this order (the first failing check raises):
        1. TypeError if start is not a datetime.date, or is a datetime.datetime.
        2. TypeError if n is not an int, or is a bool.
        3. TypeError if holidays is not a set, frozenset, list or tuple, or if any of its
           elements is not a datetime.date or is a datetime.datetime.
        4. ValueError if the result would be after datetime.date.max (9999-12-31) or
           before datetime.date.min (0001-01-01). This must be ValueError, never
           OverflowError, including when start itself is date.max or date.min.

    A business day is a Monday to Friday that is not in holidays.

    For n > 0, step forward one day at a time from start and count each business day;
    the result is the n-th business day counted. For n < 0, do the same backwards and
    return the |n|-th business day counted. start itself is never counted, and it need
    not be a business day. For n == 0, return start unchanged, even if it is not a
    business day.

    Returns a datetime.date.
    """
    raise NotImplementedError

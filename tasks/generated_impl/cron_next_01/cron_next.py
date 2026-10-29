def cron_next(expr, after):
    """Return the first minute strictly after `after` that matches the cron expression `expr`.

    Arguments:
        expr: a str of exactly 5 fields separated by whitespace (as split by str.split()):
            minute (0-59), hour (0-23), day of month (1-31), month (1-12) and day of week
            (0-7: 0 and 7 are both Sunday, 1 is Monday, ..., 6 is Saturday).
        after: a naive datetime.datetime (tzinfo is None).

    Errors, checked in this order:
        1. TypeError if expr is not a str, or after is not a datetime.datetime (a
           datetime.date that is not a datetime is not accepted).
        2. ValueError if after.tzinfo is not None.
        3. ValueError if expr is invalid (see Syntax).
        4. ValueError if no minute matches within the search limit (see Search).

    Syntax
        Each field is a comma-separated list of one or more items. An item is one of:
            *        every value in the field's range
            N        the single value N
            A-B      the values A to B inclusive; A must not be greater than B
            */S      every S-th value of the field's range, starting at its lowest value
            A-B/S    A, A+S, A+2S, ... up to B
        N, A, B and S are written with ASCII digits 0-9 only; leading zeros are allowed
        ("05" is 5). Every value must lie in the field's range and S must be at least 1.
        Anything else is invalid, for example an empty item ("1,,2"), a step after a
        single value ("5/15"), names such as "MON" or "JAN", "?", or a number of fields
        other than 5.

    Matching
        A minute matches if its minute, hour and month are in their fields and its day
        matches. The day rule depends on whether the day-of-month and day-of-week fields
        are exactly the str "*" (any other text, even "*/1" or "0-7", is restricted):
          - both are "*": every day matches;
          - exactly one is "*": the day must be in the other field;
          - neither is "*": the day matches if its day of month is in the day-of-month
            field OR its day of week is in the day-of-week field.
        A day of month that a month does not have (such as 31 in April) never matches.
        Dates follow the proleptic Gregorian calendar of datetime (2100 is not a leap year).

    Search
        The result is the earliest datetime with second 0 and microsecond 0 that is
        greater than `after` and matches. So the seconds and microseconds of `after`
        count only for "greater than": after 10:00:30 the first candidate is 10:01.
        Only results with year <= after.year + 8 (and <= 9999) are considered; if there
        is none, ValueError is raised.
        Each call must finish in well under a second, even when the result is years
        after `after` or there is no result.

    Returns a naive datetime.datetime.
    """
    raise NotImplementedError

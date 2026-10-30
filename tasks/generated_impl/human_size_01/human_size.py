def human_size(n):
    """Format a number of bytes for people, using binary units.

    Arguments:
        n: an int (bool is not accepted), 0 <= n < 2 ** 53.

    Errors, checked in this order:
        1. TypeError if n is not an int, or is a bool.
        2. ValueError if n < 0 or n >= 2 ** 53.

    Format
        If n < 1024 the result is the integer followed by " B", for example "0 B" and
        "1023 B".
        Otherwise the units are KiB (1024 bytes), MiB (1024 ** 2), GiB (1024 ** 3),
        TiB (1024 ** 4) and PiB (1024 ** 5). Take the largest unit u with u <= n, divide
        n by u and round the value to one decimal place (it is never exactly halfway).
        The result is the value with exactly one decimal, a space and the unit, for
        example "1.0 KiB", "1.5 KiB" and "117.7 MiB".

    Unit boundaries
        The unit is chosen after rounding: if the rounded value is 1024.0, use the next
        unit instead, so the result is "1.0" in that unit. For example 1048575 bytes is
        "1.0 MiB", not "1024.0 KiB".

    Returns a str.
    """
    raise NotImplementedError

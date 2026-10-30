"""Reference solution for human_size. The spec is the docstring in stub.py.

n < 2 ** 53 is exact as a float and dividing by a power of two is exact, so formatting
with .1f rounds the true quotient correctly.
"""

UNITS = ["KiB", "MiB", "GiB", "TiB", "PiB"]


def human_size(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an int")
    if n < 0 or n >= 2 ** 53:
        raise ValueError("n must satisfy 0 <= n < 2 ** 53")
    if n < 1024:
        return f"{n} B"
    k = 1
    while k < len(UNITS) and 1024 ** (k + 1) <= n:
        k += 1
    text = f"{n / 1024 ** k:.1f}"
    if text == "1024.0":
        k += 1
        text = f"{n / 1024 ** k:.1f}"
    return f"{text} {UNITS[k - 1]}"

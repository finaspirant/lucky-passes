"""Reference solution for token_bucket. The spec is the docstring in stub.py."""

import math
from fractions import Fraction


def number(value, name):
    """Type- and finiteness-check a number and return it as an exact Fraction."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be an int or float")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return Fraction(value)


def token_bucket(capacity, rate, requests):
    capacity = number(capacity, "capacity")
    if capacity <= 0:
        raise ValueError("capacity must be > 0")
    rate = number(rate, "rate")
    if rate < 0:
        raise ValueError("rate must be >= 0")
    if not isinstance(requests, list):
        raise TypeError("requests must be a list")

    parsed, previous = [], None
    for request in requests:
        if not isinstance(request, (tuple, list)) or len(request) != 2:
            raise TypeError("each request must be a (timestamp, cost) pair")
        timestamp = number(request[0], "timestamp")
        if previous is not None and timestamp < previous:
            raise ValueError("timestamps must be non-decreasing")
        cost = number(request[1], "cost")
        if cost <= 0:
            raise ValueError("cost must be > 0")
        parsed.append((timestamp, cost))
        previous = timestamp

    results, tokens, previous = [], capacity, None
    for timestamp, cost in parsed:
        if previous is not None:
            tokens = min(capacity, tokens + (timestamp - previous) * rate)
        previous = timestamp
        accepted = cost <= tokens
        if accepted:
            tokens -= cost
        results.append(accepted)
    return results

"""Reference solution for merge_ranges. The spec is the docstring in stub.py."""


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def merge_ranges(ranges):
    if not isinstance(ranges, list):
        raise TypeError("ranges must be a list")
    for item in ranges:
        if not isinstance(item, (tuple, list)) or len(item) != 2 or not all(map(is_int, item)):
            raise TypeError("each range must be a pair of ints")
        if item[0] > item[1]:
            raise ValueError("start must not be greater than end")
    merged = []
    for start, end in sorted(tuple(item) for item in ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged

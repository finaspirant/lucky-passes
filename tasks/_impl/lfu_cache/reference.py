"""Reference solution for lfu_cache. The spec is the docstring in stub.py.

Keys are grouped by use count; each group is an OrderedDict in last-use order, so
eviction and use are O(1).
"""

from collections import OrderedDict


def check_op(op):
    if not (isinstance(op, tuple) and ((len(op) == 2 and op[0] == "get") or (len(op) == 3 and op[0] == "put"))):
        raise ValueError(f"invalid operation {op!r}")
    hash(op[1])


def lfu_cache(capacity, ops):
    if isinstance(capacity, bool) or not isinstance(capacity, int):
        raise TypeError("capacity must be an int")
    if capacity < 0:
        raise ValueError("capacity must be >= 0")
    if not isinstance(ops, list):
        raise TypeError("ops must be a list")

    values, counts, groups = {}, {}, {}
    lowest = 0
    results = []

    def use(key):
        nonlocal lowest
        count = counts[key]
        del groups[count][key]
        if not groups[count]:
            del groups[count]
            if lowest == count:
                lowest = count + 1
        counts[key] = count + 1
        groups.setdefault(count + 1, OrderedDict())[key] = None

    for op in ops:
        check_op(op)
        key = op[1]
        if op[0] == "get":
            if key in values:
                use(key)
                results.append(values[key])
            else:
                results.append(None)
        elif key in values:
            values[key] = op[2]
            use(key)
        elif capacity > 0:
            if len(values) >= capacity:
                old, _ = groups[lowest].popitem(last=False)
                if not groups[lowest]:
                    del groups[lowest]
                del values[old], counts[old]
            values[key], counts[key] = op[2], 1
            groups.setdefault(1, OrderedDict())[key] = None
            lowest = 1
    return results

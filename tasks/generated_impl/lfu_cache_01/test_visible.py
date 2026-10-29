import pytest
from lfu_cache import lfu_cache


def lcg(n, seed=1):
    """n pseudo-random ints in [0, 2**31), the same on every run."""
    out, x = [], seed
    for _ in range(n):
        x = (x * 1103515245 + 12345) % 2 ** 31
        out.append(x)
    return out

def test_frequency_then_recency():
    assert lfu_cache(2, [('put', 1, 1), ('put', 2, 2), ('get', 1), ('put', 3, 3), ('get', 2), ('get', 3), ('put', 4, 4), ('get', 1), ('get', 3), ('get', 4)]) == [1, None, 3, None, 3, 4]

def test_capacity_zero():
    assert lfu_cache(0, [('put', 'a', 1), ('get', 'a')]) == [None]

def test_tie_evicts_least_recent():
    assert lfu_cache(2, [('put', 'a', 1), ('put', 'b', 2), ('put', 'c', 3), ('get', 'a'), ('get', 'b'), ('get', 'c')]) == [None, 2, 3]

def test_put_replaces_value():
    assert lfu_cache(1, [('put', 'a', 1), ('put', 'a', 2), ('get', 'a')]) == [2]

def test_put_missing_value():
    with pytest.raises(ValueError):
        lfu_cache(2, [("put", 1)])

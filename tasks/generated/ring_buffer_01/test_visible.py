import pytest
from ring_buffer import RingBuffer


def ops(capacity, *steps):
    """Apply steps to a new RingBuffer(capacity) and return each step's result.

    A step is (method_name, *args); "len" and "list" mean len(buffer) and list(buffer).
    A step that raises records the exception class name as its result.
    """
    buffer = RingBuffer(capacity)
    results = []
    for name, *args in steps:
        try:
            if name == "len":
                results.append(len(buffer))
            elif name == "list":
                results.append(list(buffer))
            else:
                results.append(getattr(buffer, name)(*args))
        except Exception as exc:
            results.append(type(exc).__name__)
    return results

def test_overwrite():
    assert ops(2, ('push', 'a'), ('push', 'b'), ('push', 'c'), ('list',)) == [None, None, 'a', ['b', 'c']]

def test_len_not_full():
    assert ops(3, ('push', 1), ('push', 2), ('len',), ('is_full',)) == [None, None, 2, False]

def test_full():
    assert ops(2, ('push', 1), ('push', 2), ('is_full',)) == [None, None, True]

def test_overwrite_then_pop():
    assert ops(3, ('push', 1), ('push', 2), ('push', 3), ('push', 4), ('push', 5), ('pop',), ('list',)) == [None, None, None, 1, 2, 3, [4, 5]]

def test_clear():
    assert ops(2, ('push', 'x'), ('clear',), ('push', 'y'), ('list',)) == [None, None, None, ['y']]

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

def test_capacity_zero():
    with pytest.raises(ValueError):
        RingBuffer(0)

def test_capacity_negative():
    with pytest.raises(ValueError):
        RingBuffer(-1)

def test_capacity_float():
    with pytest.raises(TypeError):
        RingBuffer(2.0)

def test_capacity_bool():
    with pytest.raises(TypeError):
        RingBuffer(True)

def test_capacity_str():
    with pytest.raises(TypeError):
        RingBuffer('3')

def test_capacity_attribute():
    assert RingBuffer(5).capacity == 5

def test_pop_empty():
    assert ops(3, ('pop',)) == ['IndexError']

def test_peek_empty():
    assert ops(3, ('peek',)) == ['IndexError']

def test_pop_until_empty():
    assert ops(2, ('push', 1), ('pop',), ('pop',)) == [None, 1, 'IndexError']

def test_empty_state():
    assert ops(3, ('list',), ('len',), ('is_full',)) == [[], 0, False]

def test_capacity_one_overwrite():
    assert ops(1, ('push', 1), ('push', 2), ('push', 3), ('list',), ('len',)) == [None, 1, 2, [3], 1]

def test_capacity_one_cycle():
    assert ops(1, ('push', 'a'), ('pop',), ('push', 'b'), ('peek',)) == [None, 'a', None, 'b']

def test_store_none():
    assert ops(2, ('push', None), ('push', None), ('push', 5), ('list',)) == [None, None, None, [None, 5]]

def test_clear_after_wrap():
    assert ops(3, ('push', 1), ('push', 2), ('push', 3), ('push', 4), ('clear',), ('len',), ('list',), ('push', 9), ('list',)) == [None, None, None, 1, None, 0, [], None, [9]]

def test_clear_keeps_capacity():
    assert ops(2, ('push', 1), ('clear',), ('push', 2), ('push', 3), ('push', 4), ('list',)) == [None, None, None, None, 2, [3, 4]]

def test_iteration_does_not_consume():
    assert ops(2, ('push', 1), ('list',), ('list',), ('len',)) == [None, [1], [1], 1]

def test_many_wraps():
    assert ops(3, ('push', 1), ('push', 2), ('push', 3), ('push', 4), ('push', 5), ('push', 6), ('push', 7), ('list',)) == [None, None, None, 1, 2, 3, 4, [5, 6, 7]]

def test_drain_after_wrap():
    assert ops(3, ('push', 1), ('push', 2), ('push', 3), ('push', 4), ('pop',), ('pop',), ('pop',), ('pop',)) == [None, None, None, 1, 2, 3, 4, 'IndexError']

def test_golden_01():
    assert ops(1, ('list',), ('push', 33), ('clear',), ('is_full',), ('list',), ('peek',), ('is_full',), ('len',), ('pop',), ('clear',), ('push', 36), ('push', 96)) == [[], None, None, False, [], 'IndexError', False, 0, 'IndexError', None, None, 36]

def test_golden_02():
    assert ops(3, ('peek',), ('clear',), ('push', 39), ('push', 93), ('push', 87), ('len',), ('is_full',), ('clear',), ('push', 45), ('list',), ('len',), ('pop',), ('clear',), ('is_full',), ('is_full',)) == ['IndexError', None, None, None, None, 3, True, None, None, [45], 1, 45, None, False, False]

def test_golden_03():
    assert ops(2, ('clear',), ('push', 11), ('list',), ('push', 78), ('is_full',), ('len',)) == [None, None, [11], None, True, 2]

def test_golden_04():
    assert ops(3, ('push', 24), ('pop',), ('pop',), ('push', 69), ('is_full',), ('push', 10), ('len',), ('clear',), ('is_full',), ('push', 38), ('clear',)) == [None, 24, 'IndexError', None, False, None, 2, None, False, None, None]

def test_golden_05():
    assert ops(1, ('clear',), ('len',), ('clear',), ('pop',), ('clear',), ('peek',), ('is_full',)) == [None, 0, None, 'IndexError', None, 'IndexError', False]

def test_golden_06():
    assert ops(2, ('list',), ('len',), ('pop',), ('peek',), ('push', 24), ('push', 4), ('peek',), ('is_full',), ('push', 11), ('push', 19), ('push', 10), ('clear',), ('list',), ('clear',), ('peek',)) == [[], 0, 'IndexError', 'IndexError', None, None, 24, True, 24, 4, 11, None, [], None, 'IndexError']

def test_golden_07():
    assert ops(2, ('list',), ('peek',), ('is_full',), ('is_full',), ('len',), ('push', 41), ('push', 62), ('len',), ('pop',)) == [[], 'IndexError', False, False, 0, None, None, 2, 41]

def test_golden_08():
    assert ops(1, ('peek',), ('push', 90), ('pop',), ('len',), ('push', 42), ('list',)) == ['IndexError', None, 90, 0, None, [42]]

def test_golden_09():
    assert ops(1, ('push', 89), ('pop',), ('push', 73), ('clear',), ('push', 3), ('push', 81), ('pop',)) == [None, 89, None, None, None, 3, 81]

def test_golden_10():
    assert ops(3, ('push', 47), ('push', 4), ('push', 24), ('push', 91), ('push', 61), ('pop',), ('push', 86), ('push', 69), ('list',), ('push', 33), ('push', 28), ('push', 82)) == [None, None, None, 47, 4, 24, None, 91, [61, 86, 69], 61, 86, 69]

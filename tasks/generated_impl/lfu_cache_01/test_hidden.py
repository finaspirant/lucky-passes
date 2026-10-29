import pytest
from lfu_cache import lfu_cache


def lcg(n, seed=1):
    """n pseudo-random ints in [0, 2**31), the same on every run."""
    out, x = [], seed
    for _ in range(n):
        x = (x * 1103515245 + 12345) % 2 ** 31
        out.append(x)
    return out

CASE_TIME_LIMIT = 3
PRELUDE = 'from lfu_cache import lfu_cache\n\n\ndef lcg(n, seed=1):\n    """n pseudo-random ints in [0, 2**31), the same on every run."""\n    out, x = [], seed\n    for _ in range(n):\n        x = (x * 1103515245 + 12345) % 2 ** 31\n        out.append(x)\n    return out\n'

import os
import signal
import subprocess
import sys


@pytest.fixture(autouse=True)
def case_time_limit(request):
    """Fail a non-large case that runs longer than CASE_TIME_LIMIT seconds."""
    if request.node.name.startswith("test_large_"):
        yield
        return

    def expire(signum, frame):
        raise TimeoutError("case time limit exceeded")

    previous = signal.signal(signal.SIGALRM, expire)
    signal.alarm(CASE_TIME_LIMIT)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def run_limited(expr, seconds):
    """Evaluate expr in a child process with a time limit.

    Returns the repr of its value, or "raises <ExceptionName>" if it raises.
    """
    code = (PRELUDE + "\ntry:\n    print(repr(" + expr + "))\n"
            "except Exception as exc:\n    print('raises ' + type(exc).__name__)\n")
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=here, capture_output=True, text=True,
                              timeout=seconds)
    except subprocess.TimeoutExpired:
        pytest.fail(f"time limit of {seconds}s exceeded")
    if proc.returncode:
        lines = proc.stderr.strip().splitlines()
        pytest.fail(lines[-1] if lines else "child process failed")
    lines = proc.stdout.strip().splitlines()
    return lines[-1] if lines else ""

def test_edge_val_capacity_bool():
    with pytest.raises(TypeError):
        lfu_cache(True, [])

def test_edge_val_operation_is_list():
    with pytest.raises(ValueError):
        lfu_cache(1, [["get", 1]])

def test_edge_val_unhashable_key_capacity_zero():
    with pytest.raises(TypeError):
        lfu_cache(0, [("put", [1], 2)])

def test_edge_logic_empty_ops():
    assert lfu_cache(3, []) == []

def test_edge_logic_get_miss_on_empty():
    assert lfu_cache(2, [('get', 'a')]) == [None]

def test_edge_logic_frequency_beats_recency():
    assert lfu_cache(2, [('put', 'a', 1), ('put', 'b', 2), ('get', 'a'), ('put', 'c', 3), ('get', 'a'), ('get', 'b'), ('get', 'c')]) == [1, 1, None, 3]

def test_edge_logic_put_existing_counts_as_use():
    assert lfu_cache(2, [('put', 'a', 1), ('put', 'b', 2), ('put', 'a', 10), ('put', 'c', 3), ('get', 'a'), ('get', 'b'), ('get', 'c')]) == [10, None, 3]

def test_edge_logic_put_existing_when_full_evicts_nothing():
    assert lfu_cache(2, [('put', 'a', 1), ('put', 'b', 2), ('put', 'b', 9), ('get', 'a'), ('get', 'b')]) == [1, 9]

def test_edge_logic_get_miss_changes_nothing():
    assert lfu_cache(2, [('put', 'a', 1), ('put', 'b', 2), ('get', 'z'), ('put', 'c', 3), ('get', 'a'), ('get', 'b'), ('get', 'c')]) == [None, None, 2, 3]

def test_edge_logic_recency_from_gets():
    assert lfu_cache(2, [('put', 'a', 1), ('put', 'b', 2), ('get', 'b'), ('get', 'a'), ('put', 'c', 3), ('get', 'a'), ('get', 'b'), ('get', 'c')]) == [2, 1, 1, None, 3]

def test_edge_logic_new_key_is_evicted_next():
    assert lfu_cache(2, [('put', 'a', 1), ('get', 'a'), ('get', 'a'), ('put', 'b', 2), ('put', 'c', 3), ('get', 'b'), ('get', 'c'), ('get', 'a')]) == [1, 1, None, 3, 1]

def test_edge_logic_lowest_count_moves_up():
    assert lfu_cache(3, [('put', 'a', 1), ('put', 'b', 2), ('get', 'a'), ('get', 'b'), ('put', 'c', 3), ('get', 'c'), ('put', 'd', 4), ('get', 'a'), ('get', 'b'), ('get', 'c'), ('get', 'd')]) == [1, 2, 3, None, 2, 3, 4]

def test_edge_logic_evicted_count_forgotten():
    assert lfu_cache(2, [('put', 'x', 1), ('get', 'x'), ('get', 'x'), ('put', 'y', 2), ('get', 'y'), ('get', 'y'), ('get', 'y'), ('put', 'z', 3), ('get', 'z'), ('put', 'x', 5), ('put', 'w', 6), ('get', 'x'), ('get', 'y'), ('get', 'w')]) == [1, 1, 2, 2, 2, 3, None, 2, 6]

def test_edge_logic_capacity_one_always_evicts():
    assert lfu_cache(1, [('put', 'a', 1), ('get', 'a'), ('get', 'a'), ('put', 'b', 2), ('get', 'a'), ('get', 'b')]) == [1, 1, None, 2]

def test_edge_logic_none_value_is_a_hit():
    assert lfu_cache(2, [('put', 'a', None), ('put', 'b', 2), ('get', 'a'), ('put', 'c', 3), ('get', 'b'), ('get', 'a'), ('get', 'c')]) == [None, None, None, 3]

def test_edge_logic_equal_keys_are_one_key():
    assert lfu_cache(2, [('put', 1, 'a'), ('put', 1.0, 'b'), ('put', 'c', 'c'), ('get', 1), ('get', 'c')]) == ['b', 'c']

def test_edge_logic_tuple_keys():
    assert lfu_cache(2, [('put', (1, 2), 'p'), ('put', 'x', 'q'), ('get', (1, 2)), ('get', (2, 1))]) == ['p', None]

def test_edge_logic_capacity_zero_put_then_get():
    assert lfu_cache(0, [('put', 1, 1), ('put', 1, 2), ('get', 1)]) == [None]

def test_random_01():
    assert lfu_cache(0, [('put', 1, 53), ('put', 4, 94), ('put', 0, 40), ('get', 4), ('put', 4, 59), ('put', 3, 10), ('get', 5), ('get', 4)]) == [None, None, None]

def test_random_02():
    assert lfu_cache(3, [('get', 3), ('get', 3), ('get', 4), ('get', 2), ('get', 4), ('put', 5, 47), ('put', 5, 76), ('put', 3, 25), ('get', 2), ('get', 0), ('put', 5, 80), ('put', 2, 28), ('put', 5, 66), ('put', 2, 89), ('put', 3, 34), ('put', 1, 68), ('put', 1, 79), ('put', 0, 81), ('put', 4, 21), ('put', 0, 34), ('put', 0, 97)]) == [None, None, None, None, None, None, None]

def test_random_03():
    assert lfu_cache(2, [('put', 0, 89), ('put', 4, 48), ('put', 0, 80), ('get', 1), ('put', 3, 84), ('put', 4, 12), ('put', 4, 34), ('put', 5, 52)]) == [None]

def test_random_04():
    assert lfu_cache(2, [('get', 4), ('get', 0), ('put', 2, 85), ('put', 1, 46), ('get', 2), ('get', 2), ('put', 5, 27), ('get', 5)]) == [None, None, 85, 85, 27]

def test_random_05():
    assert lfu_cache(3, [('get', 0), ('put', 2, 74), ('put', 4, 71), ('get', 1), ('get', 4), ('get', 2)]) == [None, None, 71, 74]

def test_random_06():
    assert lfu_cache(0, [('get', 1), ('put', 0, 65), ('put', 1, 3), ('get', 3), ('put', 4, 71), ('get', 4), ('put', 1, 56), ('get', 0), ('put', 4, 62), ('put', 0, 76), ('put', 4, 44), ('get', 1), ('get', 2), ('get', 0), ('put', 0, 27), ('put', 1, 62), ('put', 4, 65), ('put', 4, 53)]) == [None, None, None, None, None, None, None]

def test_random_07():
    assert lfu_cache(3, []) == []

def test_random_08():
    assert lfu_cache(2, [('get', 1), ('put', 0, 22), ('get', 2), ('get', 2), ('get', 1), ('put', 1, 40), ('get', 3), ('put', 5, 59), ('get', 5)]) == [None, None, None, None, None, 59]

def test_random_09():
    assert lfu_cache(3, [('put', 1, 18), ('put', 2, 26), ('put', 5, 82), ('get', 5)]) == [82]

def test_random_10():
    assert lfu_cache(2, [('get', 0), ('put', 0, 0), ('get', 0), ('get', 3), ('get', 4), ('get', 3), ('put', 0, 8), ('put', 4, 43), ('get', 5), ('put', 2, 9)]) == [None, 0, None, None, None, None]

def test_random_11():
    assert lfu_cache(2, [('put', 0, 98), ('get', 1), ('put', 5, 44), ('get', 2), ('get', 1), ('get', 3), ('get', 2), ('get', 1), ('get', 5)]) == [None, None, None, None, None, None, 44]

def test_random_12():
    assert lfu_cache(3, [('get', 3), ('put', 2, 21), ('put', 2, 5), ('get', 4), ('put', 3, 60), ('get', 1), ('get', 0), ('get', 4), ('put', 1, 2), ('get', 0), ('put', 0, 45), ('get', 1), ('put', 1, 49), ('put', 5, 46), ('put', 1, 58), ('get', 2), ('put', 5, 79), ('get', 1), ('get', 2), ('get', 4), ('put', 4, 97), ('put', 4, 2)]) == [None, None, None, None, None, None, 2, 5, 58, 5, None]

def test_random_13():
    assert lfu_cache(4, [('put', 3, 1), ('put', 5, 51), ('put', 2, 72), ('put', 1, 7), ('put', 2, 42), ('get', 2), ('put', 5, 3), ('get', 5), ('put', 3, 77), ('put', 3, 58), ('put', 2, 6), ('get', 5), ('get', 5), ('get', 3), ('get', 0), ('get', 2), ('put', 0, 12), ('put', 0, 5), ('get', 1), ('put', 0, 22), ('put', 1, 30), ('put', 1, 38), ('put', 3, 48), ('put', 0, 76)]) == [42, 3, 3, 3, 58, None, 6, None]

def test_random_14():
    assert lfu_cache(4, [('get', 3), ('get', 2)]) == [None, None]

def test_random_15():
    assert lfu_cache(0, [('get', 1), ('put', 5, 49), ('get', 5), ('put', 2, 43), ('get', 2), ('put', 2, 15), ('put', 3, 66), ('put', 1, 10), ('put', 4, 17), ('put', 4, 9), ('put', 0, 94), ('get', 0), ('get', 4), ('get', 4), ('put', 0, 51), ('get', 3), ('put', 3, 92), ('put', 0, 82), ('get', 2), ('put', 3, 70), ('get', 1), ('get', 4), ('get', 3), ('get', 0), ('get', 4)]) == [None, None, None, None, None, None, None, None, None, None, None, None, None]

def test_random_16():
    assert lfu_cache(0, [('get', 5), ('put', 3, 10), ('get', 1), ('put', 5, 58), ('get', 1), ('get', 3), ('get', 5), ('get', 4), ('get', 5), ('put', 4, 97), ('get', 2), ('get', 2), ('put', 2, 24), ('put', 1, 61), ('put', 5, 57), ('get', 0), ('put', 0, 34), ('put', 4, 93), ('put', 3, 61), ('put', 4, 75), ('get', 1), ('get', 4), ('put', 0, 17), ('put', 2, 21), ('put', 4, 46), ('get', 1), ('put', 5, 44)]) == [None, None, None, None, None, None, None, None, None, None, None, None, None]

def test_random_17():
    assert lfu_cache(3, [('put', 5, 21), ('put', 0, 14), ('put', 1, 10), ('put', 5, 40), ('put', 5, 29), ('get', 3), ('get', 1), ('put', 4, 58), ('put', 3, 65), ('get', 1)]) == [None, 10, 10]

def test_random_18():
    assert lfu_cache(3, [('put', 0, 24), ('put', 1, 65), ('put', 2, 77), ('put', 5, 26), ('get', 2), ('put', 1, 90), ('get', 3), ('get', 1)]) == [77, None, 90]

def test_random_19():
    assert lfu_cache(1, [('put', 0, 51), ('get', 5), ('get', 2), ('put', 3, 30), ('get', 1), ('put', 3, 36), ('put', 2, 35), ('put', 4, 96), ('get', 5), ('get', 5), ('get', 0), ('put', 3, 61), ('get', 3), ('get', 2), ('put', 1, 21), ('put', 4, 48), ('put', 4, 42), ('put', 1, 97), ('put', 5, 6), ('get', 1), ('get', 1), ('get', 5), ('get', 5), ('get', 0), ('put', 1, 78), ('get', 4), ('put', 3, 20), ('get', 2), ('get', 3)]) == [None, None, None, None, None, None, 61, None, None, None, 6, 6, None, None, None, 20]

def test_random_20():
    assert lfu_cache(1, [('get', 3), ('put', 0, 76), ('get', 1), ('put', 0, 86), ('get', 1), ('put', 5, 94), ('put', 2, 72), ('put', 1, 38), ('get', 3), ('put', 3, 40), ('get', 0), ('get', 0), ('get', 4), ('get', 4), ('put', 0, 17), ('get', 5), ('put', 3, 84), ('get', 0), ('put', 2, 73), ('put', 3, 1), ('put', 0, 48), ('put', 5, 18), ('get', 4)]) == [None, None, None, None, None, None, None, None, None, None, None]

def test_random_21():
    assert lfu_cache(3, [('get', 1), ('get', 5), ('get', 4), ('put', 0, 97), ('get', 4), ('put', 0, 13), ('put', 5, 13), ('get', 2), ('get', 0), ('put', 2, 90), ('put', 3, 37), ('get', 0), ('get', 1), ('put', 0, 31), ('put', 5, 93), ('put', 3, 49), ('put', 4, 97), ('put', 2, 5), ('get', 5), ('get', 5), ('put', 3, 45), ('put', 4, 3), ('get', 0)]) == [None, None, None, None, None, 13, 13, None, None, None, 31]

def test_random_22():
    assert lfu_cache(0, [('get', 4), ('put', 3, 98), ('get', 4), ('get', 2), ('put', 3, 75), ('get', 3), ('put', 5, 47), ('put', 2, 42), ('put', 2, 88), ('put', 4, 10), ('put', 0, 70), ('put', 5, 91)]) == [None, None, None, None]

def test_random_23():
    assert lfu_cache(3, [('get', 1), ('put', 0, 92), ('get', 5), ('get', 3), ('get', 5), ('put', 5, 88), ('put', 3, 54), ('put', 0, 37), ('get', 1), ('get', 4), ('put', 3, 34), ('put', 2, 26), ('get', 4), ('get', 5), ('get', 4), ('get', 3), ('put', 5, 24), ('get', 5), ('put', 5, 12), ('get', 3)]) == [None, None, None, None, None, None, None, None, None, 34, 24, 34]

def test_random_24():
    assert lfu_cache(3, [('get', 2), ('get', 0), ('put', 4, 55)]) == [None, None]

def test_random_25():
    assert lfu_cache(2, [('get', 2), ('put', 5, 37), ('put', 3, 50), ('get', 2), ('put', 0, 75), ('get', 2), ('get', 4), ('put', 5, 1), ('put', 4, 28), ('put', 4, 71), ('put', 2, 18), ('put', 4, 80), ('get', 1), ('get', 2), ('put', 4, 63), ('put', 4, 34), ('put', 4, 78), ('get', 5), ('get', 3), ('get', 4), ('put', 4, 11), ('get', 4), ('get', 5)]) == [None, None, None, None, None, 18, None, None, 78, 11, None]

def test_random_26():
    assert lfu_cache(3, []) == []

def test_random_27():
    assert lfu_cache(1, [('get', 1), ('get', 0), ('put', 5, 53), ('get', 0), ('get', 0), ('put', 0, 4), ('put', 3, 81), ('put', 0, 49), ('get', 2), ('put', 3, 43), ('get', 0), ('get', 4), ('get', 1), ('put', 0, 36), ('get', 0), ('get', 0), ('get', 4)]) == [None, None, None, None, None, None, None, None, 36, 36, None]

def test_random_28():
    assert lfu_cache(2, [('get', 2), ('get', 2), ('get', 3), ('get', 3), ('get', 1), ('put', 5, 31), ('get', 5), ('put', 4, 72), ('put', 3, 68), ('put', 3, 48), ('get', 3), ('get', 0), ('get', 1), ('get', 1), ('get', 5), ('get', 4), ('put', 3, 62), ('get', 1), ('get', 3), ('get', 1), ('get', 4), ('get', 2), ('put', 0, 70), ('get', 3), ('put', 5, 14)]) == [None, None, None, None, None, 31, 48, None, None, None, 31, None, None, 62, None, None, None, 62]

def test_random_29():
    assert lfu_cache(3, [('get', 3), ('put', 3, 4), ('get', 4), ('put', 5, 34), ('get', 2), ('get', 3), ('put', 2, 75), ('get', 0), ('get', 1), ('put', 0, 55), ('get', 3), ('get', 3), ('get', 0), ('get', 3), ('get', 4), ('get', 1), ('get', 1)]) == [None, None, None, 4, None, None, 4, 4, 55, 4, None, None, None]

def test_random_30():
    assert lfu_cache(3, [('get', 3), ('get', 4), ('get', 4), ('put', 4, 83), ('get', 3), ('put', 3, 42), ('get', 4), ('get', 3), ('get', 2), ('get', 2), ('put', 3, 26), ('put', 4, 76), ('get', 2), ('put', 0, 58), ('put', 0, 24), ('put', 5, 55), ('get', 4), ('put', 5, 50), ('put', 2, 38), ('get', 0), ('get', 3), ('put', 1, 42), ('get', 5), ('get', 0), ('put', 3, 51), ('put', 5, 17), ('get', 1)]) == [None, None, None, None, 83, 42, None, None, None, 76, None, 26, None, None, None]

def test_large_many_ops_capacity_5000():
    assert run_limited('(lambda r: (len(r), r.count(None), sum(x for x in r if x is not None)))(lfu_cache(5000, [("get", (x >> 4) % 300 * ((x >> 12) % 200)) if (x >> 24) % 3 == 0 else ("put", (x >> 4) % 300 * ((x >> 12) % 200), x % 1000) for x in lcg(200000)]))', 5) == '(67304, 34879, 16258775)'

def test_large_many_ops_capacity_20000():
    assert run_limited('(lambda r: (len(r), r.count(None), sum(x for x in r if x is not None)))(lfu_cache(20000, [("get", (x >> 4) % 100000) if (x >> 24) % 2 == 0 else ("put", (x >> 4) % 100000, x % 1000) for x in lcg(200000, 7)]))', 5) == '(100101, 82364, 8752562)'

import pytest
from sliding_median import sliding_median
from fractions import Fraction


def typed(result):
    return [(type(x).__name__, x) for x in result]

CASE_TIME_LIMIT = 3
PRELUDE = 'from sliding_median import sliding_median\nfrom fractions import Fraction\n\n\ndef typed(result):\n    return [(type(x).__name__, x) for x in result]\n'

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

def test_edge_val_bool_element():
    with pytest.raises(TypeError):
        sliding_median([1, True], 1)

def test_edge_val_element_checked_before_k():
    with pytest.raises(TypeError):
        sliding_median([1, "x"], 0)

def test_edge_val_k_zero():
    with pytest.raises(ValueError):
        sliding_median([1, 2], 0)

def test_edge_logic_single_element():
    assert typed(sliding_median([7], 1)) == [('int', 7)]

def test_edge_logic_odd_result_is_int():
    assert typed(sliding_median([3, 1, 2], 3)) == [('int', 2)]

def test_edge_logic_negative_fraction():
    assert typed(sliding_median([-1, -2], 2)) == [('Fraction', Fraction(-3, 2))]

def test_edge_logic_negative_whole_mean():
    assert typed(sliding_median([-1, -3], 2)) == [('int', -2)]

def test_edge_logic_mean_zero():
    assert typed(sliding_median([-5, 5], 2)) == [('int', 0)]

def test_edge_logic_half():
    assert typed(sliding_median([0, 1], 2)) == [('Fraction', Fraction(1, 2))]

def test_edge_logic_all_equal():
    assert typed(sliding_median([2, 2, 2, 2], 2)) == [('int', 2), ('int', 2), ('int', 2)]

def test_edge_logic_duplicates_odd():
    assert sliding_median([3, 1, 3, 1, 3], 3) == [3, 1, 3]

def test_edge_logic_duplicates_leave_window():
    assert sliding_median([5, 5, 1, 1, 5, 5], 2) == [5, 3, 1, 3, 5]

def test_edge_logic_even_window_of_four():
    assert typed(sliding_median([1, 2, 3, 4, 5], 4)) == [('Fraction', Fraction(5, 2)), ('Fraction', Fraction(7, 2))]

def test_edge_logic_unsorted_even():
    assert typed(sliding_median([4, 1, 3, 2], 4)) == [('Fraction', Fraction(5, 2))]

def test_edge_logic_removed_value_was_median():
    assert sliding_median([2, 9, 1, 8, 3, 7], 3) == [2, 8, 3, 7]

def test_edge_logic_descending():
    assert sliding_median([9, 8, 7, 6, 5], 3) == [8, 7, 6]

def test_edge_logic_big_ints_exact():
    assert typed(sliding_median([10 ** 20, 10 ** 20 + 1], 2)) == [('Fraction', Fraction(200000000000000000001, 2))]

def test_edge_logic_beyond_float_precision():
    assert typed(sliding_median([2 ** 53, 2 ** 53 + 1, 2 ** 53 + 2], 2)) == [('Fraction', Fraction(18014398509481985, 2)), ('Fraction', Fraction(18014398509481987, 2))]

def test_edge_logic_big_odd():
    assert sliding_median([10 ** 30, -10 ** 30, 1], 3) == [1]

def test_random_01():
    assert typed(sliding_median([8, 0, 10, -7, 2, -1, 4, -9, -2, -6, -1, -10, -10, 5, 10], 4)) == [('int', 4), ('int', 1), ('Fraction', Fraction(1, 2)), ('Fraction', Fraction(1, 2)), ('Fraction', Fraction(1, 2)), ('Fraction', Fraction(-3, 2)), ('int', -4), ('int', -4), ('int', -4), ('int', -8), ('Fraction', Fraction(-11, 2)), ('Fraction', Fraction(-5, 2))]

def test_random_02():
    assert typed(sliding_median([3, 10, -10, -4, 10, 9, 5], 2)) == [('Fraction', Fraction(13, 2)), ('int', 0), ('int', -7), ('int', 3), ('Fraction', Fraction(19, 2)), ('int', 7)]

def test_random_03():
    assert typed(sliding_median([-9, 2, 1, 7, 2, -10, -4, -4, 9, 0, 5, 3, -8, -1], 1)) == [('int', -9), ('int', 2), ('int', 1), ('int', 7), ('int', 2), ('int', -10), ('int', -4), ('int', -4), ('int', 9), ('int', 0), ('int', 5), ('int', 3), ('int', -8), ('int', -1)]

def test_random_04():
    assert typed(sliding_median([5, -10, 4, 8, 0, -9, 1, 6, -1, -7, 6, 9], 1)) == [('int', 5), ('int', -10), ('int', 4), ('int', 8), ('int', 0), ('int', -9), ('int', 1), ('int', 6), ('int', -1), ('int', -7), ('int', 6), ('int', 9)]

def test_random_05():
    assert typed(sliding_median([8, -8, 3, 9, 7, 9, -5, -4, -9, 0, 3, -1, 10, 7], 4)) == [('Fraction', Fraction(11, 2)), ('int', 5), ('int', 8), ('int', 8), ('Fraction', Fraction(3, 2)), ('Fraction', Fraction(-9, 2)), ('Fraction', Fraction(-9, 2)), ('int', -2), ('Fraction', Fraction(-1, 2)), ('Fraction', Fraction(3, 2)), ('int', 5)]

def test_random_06():
    assert typed(sliding_median([0, 3, 6, -10, 7, -6, -8, -1], 3)) == [('int', 3), ('int', 3), ('int', 6), ('int', -6), ('int', -6), ('int', -6)]

def test_random_07():
    assert typed(sliding_median([-1, 6, 9, -4, 2, 8, -2, 4, -10, -7, -8, 5, -9, 5], 5)) == [('int', 2), ('int', 6), ('int', 2), ('int', 2), ('int', 2), ('int', -2), ('int', -7), ('int', -7), ('int', -8), ('int', -7)]

def test_random_08():
    assert typed(sliding_median([3, -10, -4, -5, 0, 5, -8, 2, -10, -8, 8, -6, 1, 5], 7)) == [('int', -4), ('int', -4), ('int', -4), ('int', -5), ('int', 0), ('int', -6), ('int', -6), ('int', 1)]

def test_random_09():
    assert typed(sliding_median([-5, 7, -2, -5, -7, -7], 1)) == [('int', -5), ('int', 7), ('int', -2), ('int', -5), ('int', -7), ('int', -7)]

def test_random_10():
    assert typed(sliding_median([6, -4, 0, 2, 2, -3, -4, 0, 6, -9, -10, -4], 12)) == [('Fraction', Fraction(-3, 2))]

def test_random_11():
    assert typed(sliding_median([-8, 3, 0, -2, 3, -2, -7, 10, -7, -3, -6, -10, 2], 6)) == [('int', -1), ('int', -1), ('int', -1), ('int', -2), ('Fraction', Fraction(-5, 2)), ('Fraction', Fraction(-9, 2)), ('Fraction', Fraction(-13, 2)), ('Fraction', Fraction(-9, 2))]

def test_random_12():
    assert typed(sliding_median([-1, -1, 6, 2, 2, -9, 3, 3, 5, -2, 3, -8, -6, -2], 7)) == [('int', 2), ('int', 2), ('int', 3), ('int', 2), ('int', 3), ('int', 3), ('int', 3), ('int', -2)]

def test_random_13():
    assert typed(sliding_median([10, 3, -1, 7, 4, -10, 2, -10, 2, 4, -1, -6, 2, 2, -10, -1, 4], 16)) == [('int', 2), ('int', 2)]

def test_random_14():
    assert typed(sliding_median([0, 9, -1, -6, 1, -8, 4, 3, 7, 5, -7, -9, 7, 7, 5], 10)) == [('int', 2), ('int', 2), ('int', 0), ('int', 2), ('Fraction', Fraction(7, 2)), ('Fraction', Fraction(9, 2))]

def test_random_15():
    assert typed(sliding_median([-4, -4, -4, 2, -8, 6, 1], 4)) == [('int', -4), ('int', -4), ('int', -1), ('Fraction', Fraction(3, 2))]

def test_random_16():
    assert typed(sliding_median([6, -6, 10, -9, -4, 3, -6, -9, 7, 3, 5, 9, -8, -10, 6, -7], 5)) == [('int', -4), ('int', -4), ('int', -4), ('int', -6), ('int', -4), ('int', 3), ('int', 3), ('int', 5), ('int', 5), ('int', 3), ('int', 5), ('int', -7)]

def test_random_17():
    assert typed(sliding_median([4, -3, 2, -1, -7, 1, -6, -9, -9, -5, -3, 8, 4, 9, -3, 9, -1, 1], 12)) == [('int', -3), ('int', -3), ('int', -2), ('int', -3), ('int', -3), ('int', -2), ('int', -2)]

def test_random_18():
    assert typed(sliding_median([3, 3, -3, 8], 1)) == [('int', 3), ('int', 3), ('int', -3), ('int', 8)]

def test_random_19():
    assert typed(sliding_median([2, -2, -9, 7, 9, 8], 1)) == [('int', 2), ('int', -2), ('int', -9), ('int', 7), ('int', 9), ('int', 8)]

def test_random_20():
    assert typed(sliding_median([-8, -8, -9, -3, -2, 7, 9, -8, -9, -4, 9, -7, 6, -6, 1, -7, -1, 4, -4, 1], 1)) == [('int', -8), ('int', -8), ('int', -9), ('int', -3), ('int', -2), ('int', 7), ('int', 9), ('int', -8), ('int', -9), ('int', -4), ('int', 9), ('int', -7), ('int', 6), ('int', -6), ('int', 1), ('int', -7), ('int', -1), ('int', 4), ('int', -4), ('int', 1)]

def test_random_21():
    assert typed(sliding_median([-8, 3, 7, 5, -5], 1)) == [('int', -8), ('int', 3), ('int', 7), ('int', 5), ('int', -5)]

def test_random_22():
    assert typed(sliding_median([-8, -3, -4, 3, -7, -9], 1)) == [('int', -8), ('int', -3), ('int', -4), ('int', 3), ('int', -7), ('int', -9)]

def test_random_23():
    assert typed(sliding_median([-4, 0, 3, -8, 1, -5], 4)) == [('int', -2), ('Fraction', Fraction(1, 2)), ('int', -2)]

def test_random_24():
    assert typed(sliding_median([4, -5, -1, -1, 4, 9, -4, 4, -10, -7, 9], 7)) == [('int', -1), ('int', -1), ('int', -1), ('int', -1), ('int', 4)]

def test_random_25():
    assert typed(sliding_median([3, 5, 8, 9, -7, -9, 4, 6, 8, 8, -10, 5, -10, 9, -8, 3, 10, 2, -1, -6], 17)) == [('int', 5), ('int', 5), ('int', 4), ('int', 3)]

def test_random_26():
    assert typed(sliding_median([-8, -9, 7, 8, -6, -1, -2, 1, -7, -4, -2, -8, -7, -10, -6, 1, -2, 3, -3], 10)) == [('int', -3), ('int', -2), ('int', -2), ('int', -3), ('int', -5), ('int', -5), ('int', -5), ('int', -5), ('int', -5), ('Fraction', Fraction(-7, 2))]

def test_random_27():
    assert typed(sliding_median([2, -7, 4, -6, 6, -9, -9, 7, -8, 9, 10, -6, 6, 9, -9], 8)) == [('int', -2), ('Fraction', Fraction(-13, 2)), ('int', -1), ('int', 0), ('int', 0), ('int', 0), ('Fraction', Fraction(13, 2)), ('Fraction', Fraction(13, 2))]

def test_random_28():
    assert typed(sliding_median([5, -3, -7, -3, -3, 8, 6, 3, 4, 2, 10, -10, 3], 2)) == [('int', 1), ('int', -5), ('int', -5), ('int', -3), ('Fraction', Fraction(5, 2)), ('int', 7), ('Fraction', Fraction(9, 2)), ('Fraction', Fraction(7, 2)), ('int', 3), ('int', 6), ('int', 0), ('Fraction', Fraction(-7, 2))]

def test_random_29():
    assert typed(sliding_median([-9, -10, -8, -10, 2, 3, 10, -4, 7, 7, 6, -9, -3, -2, -10, -10, 8, 3, -6, -6], 17)) == [('int', -3), ('int', -2), ('int', -2), ('int', -2)]

def test_random_30():
    assert typed(sliding_median([-10, -7, 7, 4, 0, -8, 2, 10, 3, 2, -8, 5, 9, -10, -8, -10, -6], 17)) == [('int', 0)]

def test_large_even_window_50000():
    assert run_limited('(lambda r: (len(r), r[0], r[-1], sum(int(2 * x) for x in r), sum(type(x) is int for x in r)))(sliding_median([(i * 7919) % 100003 - 50000 for i in range(200000)], 50000))', 5) == '(150001, 1, Fraction(-15, 2), 350033, 134012)'

def test_large_odd_window_49999():
    assert run_limited('(lambda r: (len(r), r[0], r[-1], sum(int(2 * x) for x in r), sum(type(x) is int for x in r)))(sliding_median([(i * 7919) % 100003 - 50000 for i in range(200000)], 49999))', 5) == '(150002, 2, -7, 350034, 150002)'

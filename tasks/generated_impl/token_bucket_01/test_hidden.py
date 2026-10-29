import pytest
from token_bucket import token_bucket

CASE_TIME_LIMIT = 3
PRELUDE = 'from token_bucket import token_bucket\n'

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
    """Evaluate expr in a child process with a time limit; return the repr of its value."""
    code = PRELUDE + "\nprint(repr(" + expr + "))\n"
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=here, capture_output=True, text=True,
                              timeout=seconds)
    except subprocess.TimeoutExpired:
        pytest.fail(f"time limit of {seconds}s exceeded")
    if proc.returncode:
        lines = proc.stderr.strip().splitlines()
        pytest.fail(lines[-1] if lines else "child process failed")
    return proc.stdout.strip()

def test_edge_val_list_pairs():
    assert token_bucket(2, 1, [[0, 1], [0, 1], [0, 1]]) == [True, True, False]

def test_edge_val_capacity_zero():
    with pytest.raises(ValueError):
        token_bucket(0, 1, [])

def test_edge_val_capacity_negative():
    with pytest.raises(ValueError):
        token_bucket(-1, 1, [])

def test_edge_val_capacity_nan():
    with pytest.raises(ValueError):
        token_bucket(float("nan"), 1, [])

def test_edge_val_capacity_inf():
    with pytest.raises(ValueError):
        token_bucket(float("inf"), 1, [])

def test_edge_val_capacity_str():
    with pytest.raises(TypeError):
        token_bucket("1", 1, [])

def test_edge_val_capacity_bool():
    with pytest.raises(TypeError):
        token_bucket(True, 1, [])

def test_edge_val_rate_negative():
    with pytest.raises(ValueError):
        token_bucket(1, -0.5, [])

def test_edge_val_rate_inf():
    with pytest.raises(ValueError):
        token_bucket(1, float("inf"), [])

def test_edge_val_rate_bool():
    with pytest.raises(TypeError):
        token_bucket(1, False, [])

def test_edge_val_requests_tuple():
    with pytest.raises(TypeError):
        token_bucket(1, 1, ((0, 1),))

def test_edge_val_request_too_short():
    with pytest.raises(TypeError):
        token_bucket(1, 1, [(0,)])

def test_edge_val_request_too_long():
    with pytest.raises(TypeError):
        token_bucket(1, 1, [(0, 1, 2)])

def test_edge_val_request_str():
    with pytest.raises(TypeError):
        token_bucket(1, 1, ["ab"])

def test_edge_val_timestamp_none():
    with pytest.raises(TypeError):
        token_bucket(1, 1, [(None, 1)])

def test_edge_val_timestamp_nan():
    with pytest.raises(ValueError):
        token_bucket(1, 1, [(float("nan"), 1)])

def test_edge_val_cost_zero():
    with pytest.raises(ValueError):
        token_bucket(1, 1, [(0, 0)])

def test_edge_val_cost_negative():
    with pytest.raises(ValueError):
        token_bucket(1, 1, [(0, -1)])

def test_edge_val_cost_bool():
    with pytest.raises(TypeError):
        token_bucket(1, 1, [(0, True)])

def test_edge_val_decrease_after_equal():
    with pytest.raises(ValueError):
        token_bucket(5, 1, [(1, 1), (1, 1), (0.5, 1)])

def test_edge_val_capacity_checked_first():
    with pytest.raises(ValueError):
        token_bucket(0, "x", "y")

def test_edge_val_timestamp_checked_before_cost():
    with pytest.raises(ValueError):
        token_bucket(1, 1, [(1, 1), (0, "x")])

def test_edge_logic_empty():
    assert token_bucket(5, 1, []) == []

def test_edge_logic_refill_capped():
    assert token_bucket(2, 1, [(0, 2), (100, 2), (100, 1)]) == [True, True, False]

def test_edge_logic_rate_zero():
    assert token_bucket(2, 0, [(0, 1), (10, 1), (20, 1)]) == [True, True, False]

def test_edge_logic_equal_timestamps_no_refill():
    assert token_bucket(1, 5, [(3, 1), (3, 1)]) == [True, False]

def test_edge_logic_cost_equals_tokens():
    assert token_bucket(2, 1, [(0, 1.5), (0.5, 1)]) == [True, True]

def test_edge_logic_reject_keeps_tokens():
    assert token_bucket(3, 1, [(0, 2), (0, 2), (0.5, 1.5)]) == [True, False, True]

def test_edge_logic_first_request_full_bucket():
    assert token_bucket(1, 1, [(1000, 1), (1000, 1)]) == [True, False]

def test_edge_logic_negative_timestamps():
    assert token_bucket(1, 1, [(-5, 1), (-4, 1)]) == [True, True]

def test_edge_logic_float_capacity():
    assert token_bucket(2.5, 0, [(0, 1), (0, 1), (0, 0.5), (0, 0.1)]) == [True, True, True, False]

def test_edge_logic_above_capacity_despite_refill():
    assert token_bucket(2, 100, [(0, 1), (10, 2.5), (20, 2)]) == [True, False, True]

def test_edge_logic_exact_not_float_1():
    assert token_bucket(1, 1, [(0.2, 0.1), (0.3, 1)]) == [True, False]

def test_edge_logic_exact_not_float_2():
    assert token_bucket(1, 3, [(0.1, 0.6), (0.3, 1)]) == [True, False]

def test_random_01():
    assert token_bucket(5, 0.1, [(11, 2)]) == [True]

def test_random_02():
    assert token_bucket(2, 0.3, [(0, 2), (1, 0.1), (3, 1), (3, 3), (5, 6), (5.2, 3)]) == [True, True, False, False, False, False]

def test_random_03():
    assert token_bucket(2, 0.3, [(0.2, 0.3), (0.5, 2), (2.5, 6), (4.5, 0.3), (4.8, 1), (5.1, 0.3), (7.1, 0.3), (7.3, 0.5)]) == [True, False, False, True, True, True, True, True]

def test_random_04():
    assert token_bucket(2.5, 2, [(12, 0.1), (13, 1), (13.5, 0.3), (13.7, 2), (14.2, 0.5), (14.5, 0.5), (16.5, 0.3), (16.5, 3), (18.5, 6)]) == [True, True, True, True, True, True, True, False, False]

def test_random_05():
    assert token_bucket(3, 2, [(1, 6), (1.5, 1), (1.8, 0.3), (2.0, 0.3), (2.1, 3), (2.4, 0.3), (2.6, 6), (4.6, 0.3), (4.8, 3), (5.8, 2), (6.3, 3), (6.6, 1), (6.6, 3), (6.699999999999999, 0.1), (6.999999999999999, 0.1)]) == [False, True, True, True, False, True, False, True, True, True, False, True, False, True, True]

def test_random_06():
    assert token_bucket(2, 0.1, [(10.1, 1), (10.2, 6), (10.399999999999999, 2), (10.599999999999998, 0.5), (10.799999999999997, 0.3), (10.799999999999997, 1), (10.999999999999996, 6), (11.199999999999996, 1), (11.199999999999996, 1), (11.199999999999996, 0.5), (11.199999999999996, 6), (11.299999999999995, 1), (11.499999999999995, 0.5), (11.599999999999994, 1), (11.799999999999994, 3)]) == [True, False, False, True, True, False, False, False, False, False, False, False, False, False, False]

def test_random_07():
    assert token_bucket(3, 0.3, [(2.1, 1), (2.2, 1), (2.3000000000000003, 1), (2.6, 2), (4.6, 0.5), (5.1, 1), (5.1, 1), (5.6, 6)]) == [True, True, True, False, True, False, False, False]

def test_random_08():
    assert token_bucket(5, 0.1, [(0.5, 2), (0.6, 2), (0.7, 0.3), (2.7, 0.1), (4.7, 3), (5.2, 1), (5.3, 0.1), (5.3, 0.1), (5.3999999999999995, 1), (5.699999999999999, 2), (5.799999999999999, 1), (5.799999999999999, 1), (5.799999999999999, 3), (5.999999999999999, 6), (6.999999999999999, 1), (7.099999999999999, 2), (7.099999999999999, 1)]) == [True, True, True, True, False, True, False, False, False, False, False, False, False, False, False, False, False]

def test_random_09():
    assert token_bucket(2.5, 0.5, [(10.5, 3), (11.5, 6), (11.5, 3), (11.7, 0.1), (11.899999999999999, 0.3), (12.899999999999999, 0.3), (13.2, 1), (13.7, 6), (13.7, 3), (13.7, 0.1), (13.7, 1), (13.899999999999999, 6), (15.899999999999999, 2), (16.2, 1), (17.2, 6), (17.7, 1), (17.7, 6)]) == [False, False, False, True, True, True, True, False, False, True, True, False, False, True, False, True, False]

def test_random_10():
    assert token_bucket(3, 1, [(0.6, 6), (0.8999999999999999, 0.3), (1.0999999999999999, 6), (1.2, 1), (1.2, 0.3), (1.7, 1), (3.7, 3), (4.2, 0.1), (4.2, 1), (4.5, 1), (4.6, 6), (4.6, 1), (4.699999999999999, 6), (4.999999999999999, 0.3)]) == [False, True, False, True, True, True, True, True, False, False, False, False, False, True]

def test_random_11():
    assert token_bucket(2, 0.5, [(0.5, 0.3), (1.0, 6), (1.0, 6), (1.1, 0.1), (1.1, 2), (1.2000000000000002, 0.5), (1.5000000000000002, 1), (1.7000000000000002, 2), (2.7, 0.1), (4.7, 2), (4.7, 1)]) == [True, False, False, True, False, True, True, False, True, True, False]

def test_random_12():
    assert token_bucket(2.5, 1, [(0.1, 0.5), (0.2, 1), (0.30000000000000004, 0.1), (1.3, 1)]) == [True, True, True, True]

def test_random_13():
    assert token_bucket(2, 2, [(12, 1)]) == [True]

def test_random_14():
    assert token_bucket(1, 0, [(2.1, 1)]) == [True]

def test_random_15():
    assert token_bucket(3, 0.3, [(0, 6), (0, 0.1), (0.5, 0.1), (0.7, 0.1), (0.7999999999999999, 3), (1.7999999999999998, 0.3), (2.8, 6), (2.8, 0.3), (3.8, 3), (4.8, 1), (5.8, 2), (6.3, 6)]) == [False, True, True, True, False, True, False, True, True, False, False, False]

def test_random_16():
    assert token_bucket(1, 0, [(10.5, 2), (10.5, 0.5), (12.5, 0.3), (12.5, 0.5), (13.5, 0.3), (15.5, 0.3), (16.5, 3), (16.5, 0.3), (16.5, 1), (16.6, 0.3), (16.8, 0.5), (17.3, 0.1), (17.5, 0.1)]) == [False, True, True, False, False, False, False, False, False, False, False, True, True]

def test_random_17():
    assert token_bucket(5, 0.1, [(10.1, 0.3), (10.1, 6), (12.1, 0.3), (12.4, 0.3), (12.5, 3), (13.0, 0.5), (13.2, 3), (13.399999999999999, 6), (15.399999999999999, 6), (15.899999999999999, 6), (16.9, 1)]) == [True, False, True, True, True, True, False, False, False, False, True]

def test_random_18():
    assert token_bucket(2.5, 1, [(10.3, 0.3), (12.3, 0.1), (12.3, 0.1), (14.3, 6), (14.600000000000001, 0.3), (15.100000000000001, 1), (15.400000000000002, 0.5), (15.400000000000002, 1), (16.400000000000002, 6), (16.400000000000002, 0.3), (16.400000000000002, 2), (16.700000000000003, 1), (16.700000000000003, 0.3), (16.800000000000004, 2), (17.300000000000004, 0.3), (17.300000000000004, 0.5), (17.800000000000004, 1)]) == [True, True, True, False, True, True, True, True, False, True, False, True, True, False, True, False, False]

def test_random_19():
    assert token_bucket(2.5, 0, [(10.1, 0.3), (10.1, 0.1), (10.4, 6), (10.6, 1), (10.6, 3), (10.7, 2), (11.7, 1), (11.899999999999999, 6), (11.899999999999999, 1), (12.899999999999999, 2), (12.899999999999999, 1), (12.899999999999999, 1), (12.899999999999999, 3), (13.899999999999999, 0.3), (14.2, 1), (15.2, 1)]) == [True, True, False, True, False, False, True, False, False, False, False, False, False, False, False, False]

def test_random_20():
    assert token_bucket(1, 0.5, [(0.2, 6), (1.2, 1), (1.2, 0.3), (1.2, 0.3), (2.2, 2), (4.2, 0.5), (4.3, 1), (4.3999999999999995, 0.3), (4.8999999999999995, 1), (5.3999999999999995, 3), (5.6, 1), (5.8, 2), (6.8, 1), (7.3, 1), (7.3, 1), (9.3, 0.3), (9.4, 6), (9.700000000000001, 3), (11.700000000000001, 2), (12.700000000000001, 2)]) == [False, True, False, False, False, True, False, True, False, False, False, False, True, False, False, True, False, False, False, False]

def test_random_21():
    assert token_bucket(5, 0.1, [(0.2, 3), (0.7, 6), (1.0, 0.1), (2.0, 0.3), (2.0, 0.3), (2.2, 0.1), (2.5, 0.5), (2.8, 0.5), (3.0, 3), (3.3, 0.3), (3.8, 0.5), (3.9, 3), (4.9, 1), (5.4, 3), (5.4, 2), (5.9, 2), (6.2, 0.1), (6.3, 0.1)]) == [True, False, True, True, True, True, True, True, False, True, False, False, False, False, False, False, True, True]

def test_random_22():
    assert token_bucket(2.5, 0.1, [(11, 3), (13, 3), (13, 0.5), (13.5, 1), (14.0, 0.5), (14.5, 1), (14.6, 6), (14.6, 0.5), (15.6, 2)]) == [False, False, True, True, True, False, False, True, False]

def test_random_23():
    assert token_bucket(2, 0.5, [(1.1, 0.5), (1.1, 1), (1.1, 6), (2.1, 6), (2.2, 1), (4.2, 0.1), (6.2, 0.3), (6.2, 0.5), (6.3, 0.3), (6.3, 3)]) == [True, True, False, False, True, True, True, True, True, False]

def test_random_24():
    assert token_bucket(3, 0.3, [(0, 2), (0, 6), (0, 6), (0.1, 2), (0.4, 3), (0.9, 3), (1.2, 6), (1.7, 0.1), (1.7, 1), (1.7, 2), (1.7, 0.5), (2.2, 0.1), (2.3000000000000003, 2), (2.4000000000000004, 1)]) == [True, False, False, False, False, False, False, True, True, False, False, True, False, False]

def test_random_25():
    assert token_bucket(2.5, 0.3, [(0, 1), (1, 3), (2, 0.5), (2.3, 3), (2.5, 0.1)]) == [True, False, True, False, True]

def test_large_many_requests():
    assert run_limited('sum(token_bucket(5, 2, [(i * 0.25, 1 + i % 3) for i in range(100000)]))', 10) == '41668'

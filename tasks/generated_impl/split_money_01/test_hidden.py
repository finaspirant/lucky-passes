import pytest
from split_money import split_money

CASE_TIME_LIMIT = 3
PRELUDE = 'from split_money import split_money\n'

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

def test_edge_val_amount_is_float():
    with pytest.raises(TypeError):
        split_money(10.0, [1])

def test_edge_val_weight_is_bool():
    with pytest.raises(TypeError):
        split_money(10, [1, True])

def test_edge_val_weight_zero():
    with pytest.raises(ValueError):
        split_money(10, [1, 0])

def test_edge_logic_zero_amount():
    assert split_money(0, [3, 1]) == [0, 0]

def test_edge_logic_single_weight():
    assert split_money(123, [7]) == [123]

def test_edge_logic_less_than_shares():
    assert split_money(2, [1, 1, 1, 1]) == [1, 1, 0, 0]

def test_edge_logic_tie_goes_to_earlier():
    assert split_money(1, [2, 2]) == [1, 0]

def test_edge_logic_fraction_beats_index():
    assert split_money(5, [1, 1, 2]) == [1, 1, 3]

def test_edge_logic_big_amount():
    assert split_money(10 ** 18 + 1, [1, 1]) == [500000000000000001, 500000000000000000]

def test_edge_logic_big_weights():
    assert split_money(7, [10 ** 12, 1]) == [7, 0]

def test_edge_logic_negative_example():
    assert split_money(-7, [1, 1, 1]) == [-3, -2, -2]

def test_edge_logic_negative_one_cent():
    assert split_money(-1, [1, 1]) == [-1, 0]

def test_edge_logic_negative_weighted():
    assert split_money(-10, [1, 2]) == [-3, -7]

def test_edge_logic_negative_less_than_shares():
    assert split_money(-2, [1, 1, 1, 1]) == [-1, -1, 0, 0]

def test_edge_logic_negative_fraction_order():
    assert split_money(-5, [1, 1, 2]) == [-1, -1, -3]

def test_edge_logic_negative_even():
    assert split_money(-900, [1, 1, 1]) == [-300, -300, -300]

def test_random_01():
    assert split_money(412841956, [2, 2]) == [206420978, 206420978]

def test_random_02():
    assert split_money(8, [1, 1, 5]) == [1, 1, 6]

def test_random_03():
    assert split_money(447302304, [7]) == [447302304]

def test_random_04():
    assert split_money(877461938, [10, 100, 100, 1, 2, 3]) == [40623238, 406232379, 406232379, 4062324, 8124647, 12186971]

def test_random_05():
    assert split_money(5, [5, 2]) == [4, 1]

def test_random_06():
    assert split_money(8, [3, 10, 3]) == [2, 5, 1]

def test_random_07():
    assert split_money(2, [5, 1, 5, 10, 1]) == [1, 0, 0, 1, 0]

def test_random_08():
    assert split_money(733444084, [100, 10, 1]) == [660760436, 66076044, 6607604]

def test_random_09():
    assert split_money(7, [1, 7, 1, 10, 5, 10, 5]) == [0, 1, 0, 2, 1, 2, 1]

def test_random_10():
    assert split_money(990, [1, 5]) == [165, 825]

def test_random_11():
    assert split_money(267936800, [7, 10, 10, 10, 7, 10]) == [34732548, 49617926, 49617926, 49617926, 34732548, 49617926]

def test_random_12():
    assert split_money(655690124, [5]) == [655690124]

def test_random_13():
    assert split_money(357699905, [3]) == [357699905]

def test_random_14():
    assert split_money(8527, [1, 1]) == [4264, 4263]

def test_random_15():
    assert split_money(753647885, [10, 7, 1, 10]) == [269159959, 188411971, 26915996, 269159959]

def test_random_16():
    assert split_money(10, [1, 1, 100, 3, 7, 5]) == [0, 0, 9, 0, 1, 0]

def test_random_17():
    assert split_money(8865, [2, 100, 2]) == [171, 8524, 170]

def test_random_18():
    assert split_money(4632, [2]) == [4632]

def test_random_19():
    assert split_money(509448256, [10, 3, 100]) == [45083916, 13525175, 450839165]

def test_random_20():
    assert split_money(9270, [1]) == [9270]

def test_random_21():
    assert split_money(644, [10, 100, 1, 1, 5, 2, 1]) == [54, 537, 5, 5, 27, 11, 5]

def test_random_22():
    assert split_money(1408, [2, 100, 1, 1, 1, 2, 1]) == [26, 1304, 13, 13, 13, 26, 13]

def test_random_23():
    assert split_money(7204, [7, 2, 5, 7, 5]) == [1940, 554, 1385, 1940, 1385]

def test_random_24():
    assert split_money(7, [1]) == [7]

def test_random_25():
    assert split_money(918221718, [7, 7, 7, 10]) == [207340388, 207340388, 207340388, 296200554]

def test_random_26():
    assert split_money(5, [1]) == [5]

def test_random_27():
    assert split_money(394349395, [2]) == [394349395]

def test_random_28():
    assert split_money(2850, [5, 5, 10, 10, 2, 2, 10]) == [324, 324, 648, 648, 129, 129, 648]

def test_random_29():
    assert split_money(7557, [1, 100, 100, 2]) == [37, 3723, 3723, 74]

def test_random_30():
    assert split_money(566, [7]) == [566]


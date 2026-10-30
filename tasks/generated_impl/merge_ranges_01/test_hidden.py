import pytest
from merge_ranges import merge_ranges

CASE_TIME_LIMIT = 3
PRELUDE = 'from merge_ranges import merge_ranges\n'

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

def test_edge_val_not_a_list():
    with pytest.raises(TypeError):
        merge_ranges(((1, 2),))

def test_edge_val_bool_bound():
    with pytest.raises(TypeError):
        merge_ranges([(0, True)])

def test_edge_val_earlier_range_checked_first():
    with pytest.raises(ValueError):
        merge_ranges([(3, 1), (1, 2.0)])

def test_edge_logic_empty():
    assert merge_ranges([]) == []

def test_edge_logic_single_point():
    assert merge_ranges([(4, 4)]) == [(4, 4)]

def test_edge_logic_lists_become_tuples():
    assert merge_ranges([[1, 2], [5, 6]]) == [(1, 2), (5, 6)]

def test_edge_logic_duplicates():
    assert merge_ranges([(1, 3), (1, 3)]) == [(1, 3)]

def test_edge_logic_shared_endpoint():
    assert merge_ranges([(1, 3), (3, 6)]) == [(1, 6)]

def test_edge_logic_negative():
    assert merge_ranges([(-10, -5), (-7, 0)]) == [(-10, 0)]

def test_edge_logic_gap_of_one():
    assert merge_ranges([(1, 3), (5, 6)]) == [(1, 3), (5, 6)]

def test_edge_logic_adjacent():
    assert merge_ranges([(1, 3), (4, 6)]) == [(1, 6)]

def test_edge_logic_adjacent_points():
    assert merge_ranges([(1, 1), (2, 2), (3, 3)]) == [(1, 3)]

def test_edge_logic_adjacent_unsorted():
    assert merge_ranges([(4, 6), (1, 3)]) == [(1, 6)]

def test_edge_logic_adjacent_negative():
    assert merge_ranges([(-5, -1), (0, 0)]) == [(-5, 0)]

def test_edge_logic_adjacent_chain_with_gap():
    assert merge_ranges([(1, 2), (3, 4), (6, 7), (8, 9)]) == [(1, 4), (6, 9)]

def test_random_01():
    assert merge_ranges([(-40, -39), (66, 78), (75, 90), (75, 85)]) == [(-40, -39), (66, 90)]

def test_random_02():
    assert merge_ranges([(22, 30), (74, 86), (-40, -27), (95, 97), (0, 4), (70, 70), (46, 59), (-2, 10)]) == [(-40, -27), (-2, 10), (22, 30), (46, 59), (70, 70), (74, 86), (95, 97)]

def test_random_03():
    assert merge_ranges([(83, 93), (75, 86)]) == [(75, 93)]

def test_random_04():
    assert merge_ranges([(-5, 1), (92, 106), (43, 51), (95, 110)]) == [(-5, 1), (43, 51), (92, 110)]

def test_random_05():
    assert merge_ranges([(50, 56), (-18, -12), (-20, -20), (75, 78), (8, 20)]) == [(-20, -20), (-18, -12), (8, 20), (50, 56), (75, 78)]

def test_random_06():
    assert merge_ranges([(77, 83), (52, 61)]) == [(52, 61), (77, 83)]

def test_random_07():
    assert merge_ranges([(4, 8), (-12, -8), (-38, -28), (28, 32)]) == [(-38, -28), (-12, -8), (4, 8), (28, 32)]

def test_random_08():
    assert merge_ranges([(-8, 7)]) == [(-8, 7)]

def test_random_09():
    assert merge_ranges([(66, 78), (98, 98), (2, 12), (19, 25), (100, 103), (-50, -39)]) == [(-50, -39), (2, 12), (19, 25), (66, 78), (98, 98), (100, 103)]

def test_random_10():
    assert merge_ranges([(-43, -31), (33, 47), (-18, -8), (25, 28)]) == [(-43, -31), (-18, -8), (25, 28), (33, 47)]

def test_random_11():
    assert merge_ranges([(68, 71), (-1, 8), (-20, -6), (25, 32), (-1, 0)]) == [(-20, -6), (-1, 8), (25, 32), (68, 71)]

def test_random_12():
    assert merge_ranges([(-25, -22), (-20, -14), (-20, -11), (-17, -2), (100, 114), (81, 92)]) == [(-25, -22), (-20, -2), (81, 92), (100, 114)]

def test_random_13():
    assert merge_ranges([(19, 33), (85, 91), (24, 35), (16, 25), (59, 59)]) == [(16, 35), (59, 59), (85, 91)]

def test_random_14():
    assert merge_ranges([(-46, -42), (53, 57), (37, 39), (59, 64), (67, 70), (-46, -44), (-20, -17)]) == [(-46, -42), (-20, -17), (37, 39), (53, 57), (59, 64), (67, 70)]

def test_random_15():
    assert merge_ranges([(-3, -3), (-21, -7)]) == [(-21, -7), (-3, -3)]

def test_random_16():
    assert merge_ranges([(37, 52), (-21, -6), (84, 86)]) == [(-21, -6), (37, 52), (84, 86)]

def test_random_17():
    assert merge_ranges([(-30, -28), (-5, 8), (2, 7), (26, 34), (78, 83)]) == [(-30, -28), (-5, 8), (26, 34), (78, 83)]

def test_random_18():
    assert merge_ranges([(62, 68), (-33, -28)]) == [(-33, -28), (62, 68)]

def test_random_19():
    assert merge_ranges([(-38, -38), (92, 99), (67, 80), (5, 20), (-49, -48), (40, 46), (13, 20)]) == [(-49, -48), (-38, -38), (5, 20), (40, 46), (67, 80), (92, 99)]

def test_random_20():
    assert merge_ranges([(-9, -2), (6, 15), (46, 60), (95, 109), (23, 37), (17, 28)]) == [(-9, -2), (6, 15), (17, 37), (46, 60), (95, 109)]

def test_random_21():
    assert merge_ranges([]) == []

def test_random_22():
    assert merge_ranges([]) == []

def test_random_23():
    assert merge_ranges([(-36, -29), (6, 12), (38, 42), (-20, -7), (-8, -4), (39, 50), (97, 107)]) == [(-36, -29), (-20, -4), (6, 12), (38, 50), (97, 107)]

def test_random_24():
    assert merge_ranges([(-27, -23), (-46, -33), (74, 86), (-36, -31), (82, 95), (-39, -34), (77, 92), (15, 18)]) == [(-46, -31), (-27, -23), (15, 18), (74, 95)]

def test_random_25():
    assert merge_ranges([(91, 106), (-34, -27), (-7, 0), (33, 35), (89, 100), (-28, -17), (75, 87)]) == [(-34, -17), (-7, 0), (33, 35), (75, 87), (89, 106)]

def test_random_26():
    assert merge_ranges([(65, 65), (53, 53), (31, 46), (88, 89), (17, 20), (62, 65), (3, 11)]) == [(3, 11), (17, 20), (31, 46), (53, 53), (62, 65), (88, 89)]

def test_random_27():
    assert merge_ranges([(7, 17), (-37, -34), (-49, -48), (-7, 3), (76, 78), (9, 11), (38, 51)]) == [(-49, -48), (-37, -34), (-7, 3), (7, 17), (38, 51), (76, 78)]

def test_random_28():
    assert merge_ranges([(-19, -10), (0, 5), (61, 62), (67, 70), (51, 61), (22, 37)]) == [(-19, -10), (0, 5), (22, 37), (51, 62), (67, 70)]

def test_random_29():
    assert merge_ranges([]) == []

def test_random_30():
    assert merge_ranges([(46, 56), (-44, -41), (-45, -44), (45, 49), (19, 28), (-24, -11), (30, 34)]) == [(-45, -41), (-24, -11), (19, 28), (30, 34), (45, 56)]


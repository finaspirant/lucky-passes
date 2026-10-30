import pytest
from flatten import flatten


def deep(n, inner):
    for _ in range(n):
        inner = [inner]
    return inner


def digest(result):
    return (len(result), result[:3], result[-3:])

CASE_TIME_LIMIT = 3
PRELUDE = 'from flatten import flatten\n\n\ndef deep(n, inner):\n    for _ in range(n):\n        inner = [inner]\n    return inner\n\n\ndef digest(result):\n    return (len(result), result[:3], result[-3:])\n'

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

def test_edge_val_string():
    with pytest.raises(TypeError):
        flatten("abc")

def test_edge_val_none():
    with pytest.raises(TypeError):
        flatten(None)

def test_edge_logic_empty():
    assert flatten([]) == []

def test_edge_logic_tuples_kept():
    assert flatten([(1, [2]), [3]]) == [(1, [2]), 3]

def test_edge_logic_strings_kept():
    assert flatten(["ab", ["cd"]]) == ['ab', 'cd']

def test_edge_logic_dicts_and_none():
    assert flatten([{1: [2]}, [None]]) == [{1: [2]}, None]

def test_edge_logic_returns_new_list():
    assert (lambda x: (flatten(x) is not x, x))([1, 2]) == (True, [1, 2])

def test_edge_logic_input_unchanged():
    assert (lambda x: (flatten(x), x))([1, [2, [3]]]) == ([1, 2, 3], [1, [2, [3]]])

def test_edge_logic_shared_sublist():
    assert (lambda s: flatten([s, s]))([1, [2]]) == [1, 2, 1, 2]

def test_edge_logic_depth_50():
    assert flatten(deep(50, 7)) == [7]

def test_edge_logic_values_around_deep():
    assert flatten([1, deep(30, [2, 3]), 4]) == [1, 2, 3, 4]

def test_random_01():
    assert flatten([[], 's', 's']) == ['s', 's']

def test_random_02():
    assert flatten([[[[[[[], 's', ['s', None]], []], [[], [[63, 's']], [83]], [[[68, 's', None]]], [-6]], 's', []], [], []], None, 's', [None, [67]]]) == ['s', 's', None, 63, 's', 83, 68, 's', None, -6, 's', None, 's', None, 67]

def test_random_03():
    assert flatten([[], [], [70]]) == [70]

def test_random_04():
    assert flatten([[62, [[36, 's', 85, []]]]]) == [62, 36, 's', 85]

def test_random_05():
    assert flatten([[[77, [[], None, [[[83, (1, 2), None]]]], ['s', 21], 64]], 31, 's']) == [77, None, 83, (1, 2), None, 's', 21, 64, 31, 's']

def test_random_06():
    assert flatten([(1, 2), [[None, None, [[(1, 2), [[51, 70, 's']], 's', 25]], [[None, 98, [[64, None, (1, 2)], [None, 99, (1, 2), None]], [None, None, [(1, 2), (1, 2), (1, 2)], []]], [[]], [[], [None, ['s', (1, 2)], ['s', (1, 2), 77, 's'], [18, (1, 2), (1, 2), 92]], 's', (1, 2)]]], 61], [[[None, [[], None]], [], [], [24, [], [[[None, (1, 2)], None, 's'], 8, []], []]], 's', None, [None, 's', None, (1, 2)]]]) == [(1, 2), None, None, (1, 2), 51, 70, 's', 's', 25, None, 98, 64, None, (1, 2), None, 99, (1, 2), None, None, None, (1, 2), (1, 2), (1, 2), None, 's', (1, 2), 's', (1, 2), 77, 's', 18, (1, 2), (1, 2), 92, 's', (1, 2), 61, None, None, 24, None, (1, 2), None, 's', 8, 's', None, None, 's', None, (1, 2)]

def test_random_07():
    assert flatten([]) == []

def test_random_08():
    assert flatten([26, (1, 2), [None, (1, 2), [[None, [[[], 97, (1, 2), (1, 2)]], None, 82], 's', None], [[[[['s'], ['s', 's'], ['s', 's', (1, 2)], 's']], [[], [[85, 's'], 27, (1, 2)], ['s', None, [None, 's', None, 40]], 66], [28], None], None, ['s', None], [[[]]]]], (1, 2)]) == [26, (1, 2), None, (1, 2), None, 97, (1, 2), (1, 2), None, 82, 's', None, 's', 's', 's', 's', 's', (1, 2), 's', 85, 's', 27, (1, 2), 's', None, None, 's', None, 40, 66, 28, None, None, 's', None, (1, 2)]

def test_random_09():
    assert flatten([22, []]) == [22]

def test_random_10():
    assert flatten([]) == []

def test_random_11():
    assert flatten([None, ['s'], [['s']]]) == [None, 's', 's']

def test_random_12():
    assert flatten([[], 's', (1, 2), [[[[[[36, 92, (1, 2), 37], [(1, 2)], 's'], [[], None, None], [], []], 's', []], []]]]) == ['s', (1, 2), 36, 92, (1, 2), 37, (1, 2), 's', None, None, 's']

def test_random_13():
    assert flatten([[[[[], [], (1, 2)], [None, [[[(1, 2), (1, 2), 's'], None]], [None, None, [], 's']], None, 85], 's', (1, 2), []]]) == [(1, 2), None, (1, 2), (1, 2), 's', None, None, None, 's', None, 85, 's', (1, 2)]

def test_random_14():
    assert flatten([[46, [(1, 2), (1, 2)], [67, []]], [[], [(1, 2)]]]) == [46, (1, 2), (1, 2), 67, (1, 2)]

def test_random_15():
    assert flatten([[[[[], [[[None, None, None], [None, (1, 2), None], [None, (1, 2), 's', 31]], [[]], [[61, None, None, None], ['s', (1, 2)], [None], []]]]], []]]) == [None, None, None, None, (1, 2), None, None, (1, 2), 's', 31, 61, None, None, None, 's', (1, 2), None]

def test_random_16():
    assert flatten([[(1, 2), []]]) == [(1, 2)]

def test_random_17():
    assert flatten([(1, 2), [6], []]) == [(1, 2), 6]

def test_random_18():
    assert flatten([[], [[[4]]], (1, 2), [[[]], [[], [None, [['s', ['s', 's', (1, 2), (1, 2)], ['s', 24, None]], 92, 90, (1, 2)], (1, 2), [[[], 's', [89]], 83, [95, 's', [], []]]], [None, [[[None, (1, 2), 's', None], [28, (1, 2), (1, 2)], ['s', 19, (1, 2)], None]]]], None, 23]]) == [4, (1, 2), None, 's', 's', 's', (1, 2), (1, 2), 's', 24, None, 92, 90, (1, 2), (1, 2), 's', 89, 83, 95, 's', None, None, (1, 2), 's', None, 28, (1, 2), (1, 2), 's', 19, (1, 2), None, None, 23]

def test_random_19():
    assert flatten([58, [(1, 2)]]) == [58, (1, 2)]

def test_random_20():
    assert flatten([[(1, 2), [[(1, 2), [20, 's'], [[[(1, 2)], 's', [None], 23]]]], None], [[(1, 2)]], 40, None]) == [(1, 2), (1, 2), 20, 's', (1, 2), 's', None, 23, None, (1, 2), 40, None]

def test_random_21():
    assert flatten([[[17, [13, [[[], [None, None, 70, 92]], [None, (1, 2), [15, 68, 's']], (1, 2), [(1, 2)]], 's']], [(1, 2), 's', None], None, 22], [(1, 2), [[None, [['s', (1, 2)]], [], ['s']], [[[(1, 2), [None], []], ['s']], [[54, [(1, 2), 's', 's', 's'], ['s', (1, 2)], 's'], [['s'], [None, 77, 's', 's'], [None], 's'], -4, [46, 24, [None, None, 's'], 's']]]], (1, 2), [[[]], 53]], [None, [[[[['s', None, 's', (1, 2)], (1, 2)], None, [[(1, 2), None]], [['s', 's', None, None]]], [[[None, (1, 2), None], [69, (1, 2), (1, 2)], None], 's', [], ['s', ['s', None]]], [2, ['s', [73, 's', (1, 2), (1, 2)]], [20, (1, 2)]]], [[None, (1, 2), [[None], [], 's'], [[96, 's']]], [], [None, [(1, 2)], [[None, 's', None], 47], [(1, 2), []]], 89], 31, 24]]]) == [17, 13, None, None, 70, 92, None, (1, 2), 15, 68, 's', (1, 2), (1, 2), 's', (1, 2), 's', None, None, 22, (1, 2), None, 's', (1, 2), 's', (1, 2), None, 's', 54, (1, 2), 's', 's', 's', 's', (1, 2), 's', 's', None, 77, 's', 's', None, 's', -4, 46, 24, None, None, 's', 's', (1, 2), 53, None, 's', None, 's', (1, 2), (1, 2), None, (1, 2), None, 's', 's', None, None, None, (1, 2), None, 69, (1, 2), (1, 2), None, 's', 's', 's', None, 2, 's', 73, 's', (1, 2), (1, 2), 20, (1, 2), None, (1, 2), None, 's', 96, 's', None, (1, 2), None, 's', None, 47, (1, 2), 89, 31, 24]

def test_random_22():
    assert flatten([97, [[], [[], [], [[28, 71, [[57, (1, 2)], [98], [97], ['s', 16, (1, 2), 14]], ['s', [3]]], 89, [[], [[]], [[None, 's']]]], 49], 95, [(1, 2)]], [95, [], [[(1, 2), ['s']]]]]) == [97, 28, 71, 57, (1, 2), 98, 97, 's', 16, (1, 2), 14, 's', 3, 89, None, 's', 49, 95, (1, 2), 95, (1, 2), 's']

def test_random_23():
    assert flatten([[[[73, None], None, 80, None]], [[[[[], 86, (1, 2)], [32, [[None, (1, 2), None, 95], None, [87]]], [[[], [10, 's'], -4, 41], [None, [], (1, 2), ['s']], [None], (1, 2)], None], None], [[]], [[None, (1, 2), 's', -9], 's', [57, [], [], 73], 80]], ['s', [], None], (1, 2)]) == [73, None, None, 80, None, 86, (1, 2), 32, None, (1, 2), None, 95, None, 87, 10, 's', -4, 41, None, (1, 2), 's', None, (1, 2), None, None, None, (1, 2), 's', -9, 's', 57, 73, 80, 's', None, (1, 2)]

def test_random_24():
    assert flatten([[], 's', 's', [(1, 2), (1, 2)]]) == ['s', 's', (1, 2), (1, 2)]

def test_random_25():
    assert flatten([[[92, (1, 2)], 18], (1, 2), [None, (1, 2), None, [[None, [[[70, None, 's', (1, 2)]]], None, [(1, 2)]]]], []]) == [92, (1, 2), 18, (1, 2), None, (1, 2), None, None, 70, None, 's', (1, 2), None, (1, 2)]

def test_random_26():
    assert flatten([None]) == [None]

def test_random_27():
    assert flatten(['s', [(1, 2)]]) == ['s', (1, 2)]

def test_random_28():
    assert flatten([(1, 2), [], [21, None, None, 23], [[]]]) == [(1, 2), 21, None, None, 23]

def test_random_29():
    assert flatten([[], 's', [['s', (1, 2), [[47], 21], [[76, (1, 2)], None]], [[(1, 2), (1, 2)]], [[98, [[['s', (1, 2), (1, 2), (1, 2)]], [[(1, 2), None]]], 's'], 's', []]], None]) == ['s', 's', (1, 2), 47, 21, 76, (1, 2), None, (1, 2), (1, 2), 98, 's', (1, 2), (1, 2), (1, 2), (1, 2), None, 's', 's', None]

def test_random_30():
    assert flatten([(1, 2), [None, None, [], [[[62], [], [(1, 2), [[1, (1, 2), 42, (1, 2)], [(1, 2), None], []], None], [[], [None, [None, 's', None], [11, 's']]]]]], 89]) == [(1, 2), None, None, 62, (1, 2), 1, (1, 2), 42, (1, 2), (1, 2), None, None, None, None, 's', None, 11, 's', 89]

def test_large_depth_10000():
    assert run_limited('flatten(deep(10000, 1))', 5) == '[1]'

def test_large_depth_10000_with_values():
    assert run_limited('flatten([0, deep(10000, [1, 2]), 3])', 5) == '[0, 1, 2, 3]'

def test_large_two_deep_branches():
    assert run_limited('flatten([deep(10000, 1), deep(10000, [2, deep(5000, 3)])])', 5) == '[1, 2, 3]'

def test_large_deep_comb():
    assert run_limited('digest(flatten(deep(10000, list(range(100)))))', 5) == '(100, [0, 1, 2], [97, 98, 99])'

def test_large_million_values():
    assert run_limited('digest(flatten([list(range(i * 1000, i * 1000 + 1000)) for i in range(1000)]))', 5) == '(1000000, [0, 1, 2], [999997, 999998, 999999])'

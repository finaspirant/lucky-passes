import pytest
from human_size import human_size

CASE_TIME_LIMIT = 3
PRELUDE = 'from human_size import human_size\n'

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

def test_edge_val_bool():
    with pytest.raises(TypeError):
        human_size(True)

def test_edge_val_float():
    with pytest.raises(TypeError):
        human_size(1024.0)

def test_edge_val_too_large():
    with pytest.raises(ValueError):
        human_size(2 ** 53)

def test_edge_logic_zero():
    assert human_size(0) == '0 B'

def test_edge_logic_largest_bytes():
    assert human_size(1023) == '1023 B'

def test_edge_logic_rounds_down():
    assert human_size(1075) == '1.0 KiB'

def test_edge_logic_rounds_up():
    assert human_size(1127) == '1.1 KiB'

def test_edge_logic_exact_mib():
    assert human_size(1024 ** 2) == '1.0 MiB'

def test_edge_logic_gib():
    assert human_size(5 * 1024 ** 3 + 1024 ** 3 // 4) == '5.2 GiB'

def test_edge_logic_tib():
    assert human_size(3 * 1024 ** 4) == '3.0 TiB'

def test_edge_logic_largest_input():
    assert human_size(2 ** 53 - 1) == '8.0 PiB'

def test_edge_logic_just_below_rollover():
    assert human_size(1048524) == '1023.9 KiB'

def test_edge_logic_rollover_to_mib():
    assert human_size(1048525) == '1.0 MiB'

def test_edge_logic_one_below_mib():
    assert human_size(1024 ** 2 - 1) == '1.0 MiB'

def test_edge_logic_rollover_to_gib():
    assert human_size(1024 ** 3 - 1) == '1.0 GiB'

def test_edge_logic_rollover_to_tib():
    assert human_size(1024 ** 4 - 1024 ** 3 // 20) == '1.0 TiB'

def test_edge_logic_rollover_to_pib():
    assert human_size(1024 ** 5 - 1) == '1.0 PiB'

def test_random_01():
    assert human_size(429045991) == '409.2 MiB'

def test_random_02():
    assert human_size(612272036336891) == '556.9 TiB'

def test_random_03():
    assert human_size(2406) == '2.3 KiB'

def test_random_04():
    assert human_size(418253552) == '398.9 MiB'

def test_random_05():
    assert human_size(1568) == '1.5 KiB'

def test_random_06():
    assert human_size(644439453) == '614.6 MiB'

def test_random_07():
    assert human_size(905971132580253) == '824.0 TiB'

def test_random_08():
    assert human_size(8301303597955558) == '7.4 PiB'

def test_random_09():
    assert human_size(716479441108869) == '651.6 TiB'

def test_random_10():
    assert human_size(27876340956841) == '25.4 TiB'

def test_random_11():
    assert human_size(304940125) == '290.8 MiB'

def test_random_12():
    assert human_size(1431) == '1.4 KiB'

def test_random_13():
    assert human_size(739009958) == '704.8 MiB'

def test_random_14():
    assert human_size(66364) == '64.8 KiB'

def test_random_15():
    assert human_size(30307693211647) == '27.6 TiB'

def test_random_16():
    assert human_size(784818244) == '748.5 MiB'

def test_random_17():
    assert human_size(579776) == '566.2 KiB'

def test_random_18():
    assert human_size(615) == '615 B'

def test_random_19():
    assert human_size(18871355883281) == '17.2 TiB'

def test_random_20():
    assert human_size(1573) == '1.5 KiB'

def test_random_21():
    assert human_size(9779531) == '9.3 MiB'

def test_random_22():
    assert human_size(2221) == '2.2 KiB'

def test_random_23():
    assert human_size(276540705) == '263.7 MiB'

def test_random_24():
    assert human_size(3699532286648514) == '3.3 PiB'

def test_random_25():
    assert human_size(6047377134716104) == '5.4 PiB'

def test_random_26():
    assert human_size(801419334410) == '746.4 GiB'

def test_random_27():
    assert human_size(1829592) == '1.7 MiB'

def test_random_28():
    assert human_size(459) == '459 B'

def test_random_29():
    assert human_size(869759024) == '829.5 MiB'

def test_random_30():
    assert human_size(9279930810710) == '8.4 TiB'


import pytest
from semver_match import semver_match

CASE_TIME_LIMIT = 3
PRELUDE = 'from semver_match import semver_match\n'

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

def test_edge_val_version_two_parts():
    with pytest.raises(ValueError):
        semver_match("1.0", ">=1.0.0")

def test_edge_val_version_leading_zero():
    with pytest.raises(ValueError):
        semver_match("01.0.0", ">=1.0.0")

def test_edge_val_pre_leading_zero():
    with pytest.raises(ValueError):
        semver_match("1.0.0-01", ">=1.0.0")

def test_edge_val_pre_empty_identifier():
    with pytest.raises(ValueError):
        semver_match("1.0.0-a..b", ">=1.0.0")

def test_edge_val_pre_trailing_dash():
    with pytest.raises(ValueError):
        semver_match("1.0.0-", ">=1.0.0")

def test_edge_val_build_metadata():
    with pytest.raises(ValueError):
        semver_match("1.0.0+build", ">=1.0.0")

def test_edge_val_v_prefix():
    with pytest.raises(ValueError):
        semver_match("v1.0.0", ">=1.0.0")

def test_edge_val_version_whitespace():
    with pytest.raises(ValueError):
        semver_match(" 1.0.0", ">=1.0.0")

def test_edge_val_non_ascii_digit():
    with pytest.raises(ValueError):
        semver_match("١.0.0", ">=1.0.0")

def test_edge_val_range_empty():
    with pytest.raises(ValueError):
        semver_match("1.0.0", "")

def test_edge_val_range_trailing_or():
    with pytest.raises(ValueError):
        semver_match("1.0.0", "1.0.0 ||")

def test_edge_val_range_spaced_operator():
    with pytest.raises(ValueError):
        semver_match("1.0.0", ">= 1.0.0")

def test_edge_val_range_gt():
    with pytest.raises(ValueError):
        semver_match("2.0.0", ">1.0.0")

def test_edge_val_range_le():
    with pytest.raises(ValueError):
        semver_match("1.0.0", "<=1.0.0")

def test_edge_val_range_eq():
    with pytest.raises(ValueError):
        semver_match("1.0.0", "=1.0.0")

def test_edge_val_range_x():
    with pytest.raises(ValueError):
        semver_match("1.0.0", "1.x")

def test_edge_val_bad_set_after_match():
    with pytest.raises(ValueError):
        semver_match("1.0.0", "1.0.0 || foo")

def test_edge_val_version_not_str():
    with pytest.raises(TypeError):
        semver_match(1, ">=1.0.0")

def test_edge_val_constraint_not_str():
    with pytest.raises(TypeError):
        semver_match("1.0.0", None)

def test_edge_val_version_checked_first():
    with pytest.raises(TypeError):
        semver_match("bad", None)

def test_edge_val_version_parsed_before_range():
    with pytest.raises(ValueError):
        semver_match("1.0", "")

def test_edge_logic_exact_equal():
    assert semver_match("1.2.3", "1.2.3") == True

def test_edge_logic_exact_different():
    assert semver_match("1.2.4", "1.2.3") == False

def test_edge_logic_numeric_not_lexical():
    assert semver_match("1.10.0", ">=1.9.0") == True

def test_edge_logic_ge_boundary():
    assert semver_match("1.0.0", ">=1.0.0") == True

def test_edge_logic_lt_boundary():
    assert semver_match("1.0.0", "<1.0.0") == False

def test_edge_logic_tilde_inside():
    assert semver_match("1.2.9", "~1.2.5") == True

def test_edge_logic_tilde_below():
    assert semver_match("1.2.4", "~1.2.5") == False

def test_edge_logic_caret_zero_major_inside():
    assert semver_match("0.2.9", "^0.2.3") == True

def test_edge_logic_caret_zero_major_next_minor():
    assert semver_match("0.3.0", "^0.2.3") == False

def test_edge_logic_caret_zero_zero_same():
    assert semver_match("0.0.3", "^0.0.3") == True

def test_edge_logic_caret_zero_zero_next_patch():
    assert semver_match("0.0.4", "^0.0.3") == False

def test_edge_logic_caret_all_zero():
    assert semver_match("0.0.0", "^0.0.0") == True

def test_edge_logic_or_without_spaces():
    assert semver_match("2.0.0", "1.0.0||2.0.0") == True

def test_edge_logic_extra_whitespace():
    assert semver_match("1.0.0", "  >=1.0.0   <2.0.0  ") == True

def test_edge_logic_pre_numeric_order():
    assert semver_match("1.0.0-beta.11", ">=1.0.0-beta.2") == True

def test_edge_logic_pre_numeric_order_false():
    assert semver_match("1.0.0-beta.2", ">=1.0.0-beta.11") == False

def test_edge_logic_pre_chain():
    assert semver_match("1.0.0-alpha.1", ">=1.0.0-alpha <1.0.0-alpha.beta") == True

def test_edge_logic_pre_numeric_below_alpha():
    assert semver_match("1.0.0-1", "<1.0.0-alpha") == True

def test_edge_logic_pre_ascii_order():
    assert semver_match("1.0.0-Beta", "<1.0.0-alpha") == True

def test_edge_logic_pre_fewer_identifiers_lower():
    assert semver_match("1.0.0-alpha", "<1.0.0-alpha.1") == True

def test_edge_logic_pre_needs_prerelease_comparator():
    assert semver_match("1.0.0-rc.1", "<1.0.0") == False

def test_edge_logic_pre_with_prerelease_comparator():
    assert semver_match("1.0.0-rc.1", ">=1.0.0-rc.1 <1.0.0") == True

def test_edge_logic_pre_excluded_by_caret():
    assert semver_match("2.0.0-rc.1", "^1.0.0") == False

def test_edge_logic_pre_other_patch_excluded():
    assert semver_match("1.5.0-beta", "^1.0.0") == False

def test_edge_logic_pre_caret_same_patch():
    assert semver_match("1.2.3-beta.3", "^1.2.3-beta.2") == True

def test_edge_logic_pre_caret_later_patch():
    assert semver_match("1.2.4-alpha", "^1.2.3-beta.2") == False

def test_edge_logic_pre_exact():
    assert semver_match("1.2.3-rc.1", "1.2.3-rc.1") == True

def test_edge_logic_pre_tilde():
    assert semver_match("1.2.3-rc.2", "~1.2.3-rc.1") == True

def test_edge_logic_pre_rule_per_set():
    assert semver_match("1.2.3-rc.1", "^2.0.0 || >=1.2.3-rc.0") == True

def test_edge_logic_pre_hyphen_identifier():
    assert semver_match("1.0.0-alpha-1", "1.0.0-alpha-1") == True

def test_edge_logic_release_ignores_pre_rule():
    assert semver_match("1.2.3", ">=1.2.3-rc.1") == True

def test_edge_logic_release_above_pre():
    assert semver_match("1.0.0", ">=1.0.0-rc.1 <1.0.0") == False

def test_random_01():
    assert semver_match('0.1.0', '<0.2.1 ~2.2.3 || ^0.0.0 >=0.3.3') == False

def test_random_02():
    assert semver_match('1.3.0-beta', '>=0.2.2 ^1.3.0 || ~1.2.1 <2.2.1') == False

def test_random_03():
    assert semver_match('2.1.1', '^2.0.1 || ~0.0.2') == True

def test_random_04():
    assert semver_match('1.1.1', '<1.1.3 ~1.1.1') == True

def test_random_05():
    assert semver_match('1.2.3', '1.0.1 || >=2.2.1-rc.1 1.2.3') == False

def test_random_06():
    assert semver_match('0.1.0', '0.1.0-beta.2') == False

def test_random_07():
    assert semver_match('1.1.1', '>=1.2.1') == False

def test_random_08():
    assert semver_match('0.0.3', '~0.1.3 >=1.2.3') == False

def test_random_09():
    assert semver_match('2.2.1', '2.1.1-alpha') == False

def test_random_10():
    assert semver_match('1.2.1', '>=2.3.1 || ~2.2.1 1.0.0-1') == False

def test_random_11():
    assert semver_match('1.1.0-alpha', '1.1.0') == False

def test_random_12():
    assert semver_match('1.3.1', '<1.2.0 ~1.3.1') == False

def test_random_13():
    assert semver_match('0.3.0-alpha', '>=0.3.0') == False

def test_random_14():
    assert semver_match('2.0.1', '2.0.1 || >=0.3.2 <1.1.3-rc.1') == True

def test_random_15():
    assert semver_match('0.0.3', '<0.2.0-rc.1 || >=0.0.3') == True

def test_random_16():
    assert semver_match('1.3.2', '>=1.3.2-beta.2 ~2.2.3-beta || ~2.0.0 <0.0.2') == False

def test_random_17():
    assert semver_match('1.3.3', '^1.3.3-alpha ~1.3.3 || >=1.1.0 ^1.0.0') == True

def test_random_18():
    assert semver_match('2.1.3', '<2.3.1 || ^1.1.3 ~1.0.0') == True

def test_random_19():
    assert semver_match('1.0.0-Beta', '>=0.2.0 1.0.0-beta') == False

def test_random_20():
    assert semver_match('0.1.2', '~1.1.2 ~2.2.3 || ~0.2.2') == False

def test_random_21():
    assert semver_match('0.0.1-beta.2', '~0.0.1 <2.1.2-beta.2') == False

def test_random_22():
    assert semver_match('2.0.0', '~2.0.0 || <1.1.2') == True

def test_random_23():
    assert semver_match('0.0.1', '^0.1.1 >=0.2.0-beta.11') == False

def test_random_24():
    assert semver_match('2.0.4', '~2.0.3') == True

def test_random_25():
    assert semver_match('2.3.1-beta.11', '<1.3.1-rc.1 ~2.2.3-Beta || <2.0.1 >=2.3.1-alpha') == False

def test_random_26():
    assert semver_match('0.3.1', '~0.3.1 >=1.0.0') == False

def test_random_27():
    assert semver_match('2.0.3', '<2.1.3-beta >=0.3.3-alpha') == True

def test_random_28():
    assert semver_match('2.2.3', '~2.2.3-rc.1 ^2.0.1') == True

def test_random_29():
    assert semver_match('1.3.2', '>=1.2.2-Beta 0.0.1') == False

def test_random_30():
    assert semver_match('0.2.4', '~0.2.3') == True


import pytest
from glob_match import glob_match

CASE_TIME_LIMIT = 3
PRELUDE = 'from glob_match import glob_match\n'

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

def test_edge_val_text_not_str():
    with pytest.raises(TypeError):
        glob_match(None, "*")

def test_edge_val_pattern_not_str():
    with pytest.raises(TypeError):
        glob_match("a", 5)

def test_edge_logic_empty_both():
    assert glob_match("", "") == True

def test_edge_logic_empty_text_star():
    assert glob_match("", "*") == True

def test_edge_logic_empty_text_question():
    assert glob_match("", "?") == False

def test_edge_logic_empty_pattern():
    assert glob_match("a", "") == False

def test_edge_logic_whole_string_only():
    assert glob_match("abc", "ab") == False

def test_edge_logic_star_crosses_slash():
    assert glob_match("a/b/c", "a*c") == True

def test_edge_logic_stars_multiple():
    assert glob_match("abcabc", "*b*b*") == True

def test_edge_logic_star_no_match():
    assert glob_match("abc", "*d*") == False

def test_edge_logic_question_count():
    assert glob_match("ab", "???") == False

def test_edge_logic_case_sensitive():
    assert glob_match("M", "[a-z]") == False

def test_edge_logic_range_member():
    assert glob_match("m", "[a-z]") == True

def test_edge_logic_digit_range():
    assert glob_match("abc1", "*[0-9]") == True

def test_edge_logic_reversed_range_empty():
    assert glob_match("b", "[z-a]") == False

def test_edge_logic_reversed_range_other_member():
    assert glob_match("y", "[z-ay]") == True

def test_edge_logic_dash_first():
    assert glob_match("-", "[-a]") == True

def test_edge_logic_dash_last():
    assert glob_match("-", "[a-]") == True

def test_edge_logic_dash_last_not_range():
    assert glob_match("b", "[a-]") == False

def test_edge_logic_range_from_dash():
    assert glob_match("/", "[--0]") == True

def test_edge_logic_bracket_first_member():
    assert glob_match("]", "[]a]") == True

def test_edge_logic_bracket_first_negated():
    assert glob_match("]", "[!]a]") == False

def test_edge_logic_bracket_first_negated_other():
    assert glob_match("b", "[!]a]") == True

def test_edge_logic_negated_needs_a_char():
    assert glob_match("", "[!a]") == False

def test_edge_logic_bang_not_first():
    assert glob_match("!", "[a!]") == True

def test_edge_logic_class_star_literal():
    assert glob_match("*", "[*?]") == True

def test_edge_logic_class_star_not_wildcard():
    assert glob_match("a", "[*?]") == False

def test_edge_logic_escape_in_class():
    assert glob_match("]", "[\\]]") == True

def test_edge_logic_escaped_range_endpoint():
    assert glob_match("b", "[\\a-c]") == True

def test_edge_logic_unterminated_literal():
    assert glob_match("[ab", "[ab") == True

def test_edge_logic_unterminated_then_star():
    assert glob_match("[abc", "[a*") == True

def test_edge_logic_unterminated_negated_bracket():
    assert glob_match("[!]", "[!]") == True

def test_edge_logic_empty_brackets_literal():
    assert glob_match("[]", "[]") == True

def test_edge_logic_escaped_question():
    assert glob_match("?", "\\?") == True

def test_edge_logic_escaped_question_not_wildcard():
    assert glob_match("a", "\\?") == False

def test_edge_logic_escaped_star_not_wildcard():
    assert glob_match("axb", "a\\*b") == False

def test_edge_logic_escaped_open_bracket():
    assert glob_match("[a]", "\\[a]") == True

def test_edge_logic_escaped_backslash():
    assert glob_match("\\", "\\\\") == True

def test_edge_logic_trailing_backslash():
    assert glob_match("a\\", "a\\") == True

def test_edge_logic_unicode_question():
    assert glob_match("é", "?") == True

def test_edge_logic_unicode_star():
    assert glob_match("日本", "*本") == True

def test_random_01():
    assert glob_match('-', '[]-]') == True

def test_random_02():
    assert glob_match(']]a[a-', '\\*[]-]a[a-') == False

def test_random_03():
    assert glob_match(']ab[a-[[', '[!a][a-b]b[a-[[a-b]') == False

def test_random_04():
    assert glob_match('b[a-][ba', '[!a][a-[!a][-a') == False

def test_random_05():
    assert glob_match('', '') == True

def test_random_06():
    assert glob_match(']]b', 'a]b') == False

def test_random_07():
    assert glob_match('bab-*', '*bab[]-]\\*') == True

def test_random_08():
    assert glob_match('*ab]ab[', '[!a]*]a[!a][') == True

def test_random_09():
    assert glob_match('[', '[') == True

def test_random_10():
    assert glob_match('-', 'b') == False

def test_random_11():
    assert glob_match('-', '[!a]') == True

def test_random_12():
    assert glob_match('a[a-b]bb', '[ab][a-b]b[ab]') == False

def test_random_13():
    assert glob_match('a', '\\*') == False

def test_random_14():
    assert glob_match('-a', '-[!a]') == False

def test_random_15():
    assert glob_match('b', '[!a]') == True

def test_random_16():
    assert glob_match('aabb[a-[', '**b[a-[') == True

def test_random_17():
    assert glob_match('[a][*-a[a-', '[a-[?-?[a-') == False

def test_random_18():
    assert glob_match('a-a-b]', '?[a-[a-b]]') == False

def test_random_19():
    assert glob_match(']]', '[]-][') == False

def test_random_20():
    assert glob_match('-*-', '-\\*-') == True

def test_random_21():
    assert glob_match('b', '[a-b]') == True

def test_random_22():
    assert glob_match('-]*-', '*\\*[]-]') == True

def test_random_23():
    assert glob_match('b*', '[a-b]-') == False

def test_random_24():
    assert glob_match('a**', 'a\\*[a-b]') == False

def test_random_25():
    assert glob_match('ba*', 'b[a-b]\\*') == True

def test_random_26():
    assert glob_match('-]-bbb-]', '*?b[a-b]b*') == True

def test_random_27():
    assert glob_match('-', '[]-]') == True

def test_random_28():
    assert glob_match('', '') == True

def test_random_29():
    assert glob_match('', '') == True

def test_random_30():
    assert glob_match('-[aa', '-[a-') == False

def test_large_many_stars_no_match():
    assert run_limited('glob_match("a" * 3000, "*a" * 100 + "*b")', 5) == 'False'

def test_large_many_stars_match():
    assert run_limited('glob_match("a" * 3000 + "b", "*a" * 100 + "*b")', 5) == 'True'

def test_large_negated_classes_backtrack():
    assert run_limited('glob_match("x" * 2000, "[!a]*" * 60 + "y")', 5) == 'False'

def test_large_long_questions():
    assert run_limited('glob_match("ab" * 1500, "?" * 3000)', 5) == 'True'

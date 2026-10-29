import pytest
from tennis_score import tennis_score


def G(winners):
    return [w for w in winners for _ in range(4)]

TO_6_6 = G("AAAAABBBBBAB")

CASE_TIME_LIMIT = 3
PRELUDE = 'from tennis_score import tennis_score\n\n\ndef G(winners):\n    return [w for w in winners for _ in range(4)]\n\nTO_6_6 = G("AAAAABBBBBAB")\n'

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

def test_edge_val_tuple_input():
    assert tennis_score(("A", "A")) == ('in progress', '0-0 30-0')

def test_edge_val_point_after_match():
    with pytest.raises(ValueError):
        tennis_score(["A"] * 49)

def test_edge_val_bad_item_after_match():
    with pytest.raises(ValueError):
        tennis_score(["A"] * 48 + ["C"])

def test_edge_val_invalid_winner():
    with pytest.raises(ValueError):
        tennis_score(["A", "C"])

def test_edge_val_lowercase_winner():
    with pytest.raises(ValueError):
        tennis_score(["a"])

def test_edge_val_int_winner():
    with pytest.raises(ValueError):
        tennis_score([1])

def test_edge_val_str_input():
    with pytest.raises(TypeError):
        tennis_score("AAB")

def test_edge_val_none_input():
    with pytest.raises(TypeError):
        tennis_score(None)

def test_edge_logic_love_fifteen():
    assert tennis_score(["B"]) == ('in progress', '0-0 0-15')

def test_edge_logic_forty_love():
    assert tennis_score(list("AAA")) == ('in progress', '0-0 40-0')

def test_edge_logic_forty_thirty():
    assert tennis_score(list("AABBA")) == ('in progress', '0-0 40-30')

def test_edge_logic_advantage_a():
    assert tennis_score(list("ABABABA")) == ('in progress', '0-0 advantage A')

def test_edge_logic_advantage_b():
    assert tennis_score(list("ABABABB")) == ('in progress', '0-0 advantage B')

def test_edge_logic_back_to_deuce():
    assert tennis_score(list("ABABABAB")) == ('in progress', '0-0 deuce')

def test_edge_logic_game_after_advantage():
    assert tennis_score(list("ABABABAA")) == ('in progress', '1-0 0-0')

def test_edge_logic_set_6_4():
    assert tennis_score(G("AAAAABBBBA")) == ('in progress', '6-4 0-0 0-0')

def test_edge_logic_set_at_6_5():
    assert tennis_score(G("AAAAABBBBBA")) == ('in progress', '6-5 0-0')

def test_edge_logic_set_7_5():
    assert tennis_score(G("AAAAABBBBBAA")) == ('in progress', '7-5 0-0 0-0')

def test_edge_logic_tiebreak_start():
    assert tennis_score(TO_6_6) == ('in progress', '6-6 tiebreak 0-0')

def test_edge_logic_tiebreak_points():
    assert tennis_score(TO_6_6 + list("AAB")) == ('in progress', '6-6 tiebreak 2-1')

def test_edge_logic_tiebreak_needs_two():
    assert tennis_score(TO_6_6 + list("AB" * 6) + ["A"]) == ('in progress', '6-6 tiebreak 7-6')

def test_edge_logic_tiebreak_to_love():
    assert tennis_score(TO_6_6 + ["A"] * 7) == ('in progress', '7-6(0) 0-0 0-0')

def test_edge_logic_tiebreak_b_extended():
    assert tennis_score(TO_6_6 + list("AB" * 6) + ["B", "B"]) == ('in progress', '6-7(6) 0-0 0-0')

def test_edge_logic_tiebreak_long():
    assert tennis_score(TO_6_6 + list("AB" * 10) + ["A", "A"]) == ('in progress', '7-6(10) 0-0 0-0')

def test_edge_logic_tiebreak_second_set():
    assert tennis_score(G("A" * 6) + TO_6_6 + ["B"] * 7) == ('in progress', '6-0 6-7(0) 0-0 0-0')

def test_edge_logic_second_set_point():
    assert tennis_score(G("A" * 6) + ["A"]) == ('in progress', '6-0 0-0 15-0')

def test_edge_logic_third_set_no_tiebreak():
    assert tennis_score(G("A" * 6 + "B" * 6) + TO_6_6) == ('in progress', '6-0 0-6 6-6 0-0')

def test_edge_logic_third_set_deuce_at_6_6():
    assert tennis_score(G("A" * 6 + "B" * 6) + TO_6_6 + list("ABABAB")) == ('in progress', '6-0 0-6 6-6 deuce')

def test_edge_logic_third_set_7_6():
    assert tennis_score(G("A" * 6 + "B" * 6) + TO_6_6 + G("A")) == ('in progress', '6-0 0-6 7-6 0-0')

def test_edge_logic_third_set_8_6():
    assert tennis_score(G("A" * 6 + "B" * 6) + TO_6_6 + G("AA")) == ('A won', '6-0 0-6 8-6')

def test_edge_logic_third_set_long():
    assert tennis_score(G("B" * 6 + "A" * 6) + TO_6_6 + G("AB" * 4 + "BB")) == ('B won', '0-6 6-0 10-12')

def test_edge_logic_b_straight_sets():
    assert tennis_score(["B"] * 48) == ('B won', '0-6 0-6')

def test_edge_logic_tiebreak_sets_win():
    assert tennis_score(TO_6_6 + ["A"] * 7 + TO_6_6 + list("BA" * 5) + ["A", "A"]) == ('A won', '7-6(0) 7-6(5)')

def test_random_01():
    assert tennis_score(list('BBABBABAAABABBABABABABBABBABAAAAAAAAABBABAAAABABAAAABAABBABBBAAABABBAABAABBAAAAABBBBAAAAAAABBAAAABABABAAA')) == ('A won', '6-3 6-2')

def test_random_02():
    with pytest.raises(ValueError):
        tennis_score(list('AABBABAABAABBBBBABABBABBBBBABABABABBBBABBBBBBBBBBBBAABABBBAAABBBBABBBBAAABBABBBBBBB'))

def test_random_03():
    with pytest.raises(ValueError):
        tennis_score(list('ABAAABBAABBAAAABBBABAAAABAABBAAABAABBABAAABAABAABABABABBAAAAABABBAAABAABBBABABAAAAAABBBAAAABBBBAABAABAABBABAAAB'))

def test_random_04():
    assert tennis_score(list('BBBAABBAABBBABBABBAABABBBABABBBBBBABAABAABBABBBABBBABBBBABBBABABABABAAABBBBBBBBBABBAAAABBBB')) == ('B won', '1-6 2-6')

def test_random_05():
    assert tennis_score(list('AABBBABAABBBBBBBBBBBBBBBBBBABABAABBBBBBBBBBBBBAAABBBBABBAABABBABBBAAABBBBAAAAABBBB')) == ('B won', '0-6 1-6')

def test_random_06():
    assert tennis_score(list('BBBAABBBBBBABBBBBBBBBBBABBBBAAAAABBABBABBBABBABBBABBBAAAABBBBAAAAAABBBABBBABAABBB')) == ('B won', '0-6 3-6')

def test_random_07():
    assert tennis_score(list('AA')) == ('in progress', '0-0 30-0')

def test_random_08():
    assert tennis_score(list('BBAAAAAABBBABBBAAABBAABBBBBBAAABBBABAABAABBBBABABBBAABAABBBBAABABBBABBBAAAAABAAABBBBABAAABBAABBBBABABABABAABAAAABABAAAAABAABABBAAAAAABBBABABBBABBBBAABAAAAAAAAABBAAAABA')) == ('A won', '4-6 6-4 6-2')

def test_random_09():
    assert tennis_score(list('ABBABAAAABBBAAAAABAAABAAABBAABAAAABBAAAABABABBAAAABABABBAAAAAABABBABAAAAAAAAAAAAAA')) == ('A won', '6-0 6-2')

def test_random_10():
    assert tennis_score(list('AAAABBBBBBABBBBABABABBBBBBBBABBBBBABBABBBBABBAAABBBBBBBBBAAABBBABBBBBB')) == ('B won', '1-6 0-6')

def test_random_11():
    assert tennis_score(list('ABAAABAAAAABAABBABBBBBBBBBBBAAABBBBAAAAAAAABBBABABBBBAAABABAABABBBAABABAAAABBABAABAABAABBBAAAAAAABBABABAAABBABBABABBBABBABBABBAABAAAAAAAAAA')) == ('A won', '7-6(4) 6-4')

def test_random_12():
    assert tennis_score(list('ABAABAAAAABAABBAABBAAABBAAAAABAAABABBAABABBBABABBBAAAAAABBBABBAABBAAAABBBAAAABABAAAABAAAABBBABBAAAAAABAA')) == ('A won', '6-2 6-2')

def test_random_13():
    assert tennis_score(list('BBAABBBABBBBBBAABBBABABBBAABAABAABAABBABBAABBBBABBBBBBBBBBBAABABABBBBBABBBBABAABB')) == ('B won', '1-6 0-6')

def test_random_14():
    assert tennis_score(list('ABBBBAABBBABAAABABBBBABBBBBBAAABBBBABBAABBABAABABAAAABBABAAAAABAABABBBBBAAABBBAABAABABBAABBBABBABAABABAABBBABBBABBBBAAAAAABAAABAAAAABABBBBBABBABABABBB')) == ('B won', '5-7 5-7')

def test_random_15():
    assert tennis_score(list('ABAABBABAAABABBABABABBAABABAABABABBABAAAAABABAAAABBABABAAABABABBBAAAABBABABABBBBABABAAAABAAAABBABBBBABABBAAAABBBABABBBAABBABBAAAAAAABAAABBBBABBABBABAAAABBBABAAAABBBAABABABBB')) == ('B won', '6-1 4-6 4-6')

def test_random_16():
    with pytest.raises(ValueError):
        tennis_score(list('BAAAAABBBBBBBBAAABAAAAAAABBAAABAABBBAAAABAABBBAAABBAAAAAAAABABBABBABABBABBAABBBBBAAABAABBAABAAABAAAAAAABAB'))

def test_random_17():
    assert tennis_score(list('ABABBBBABABBABAAABBBBBBAAABAB')) == ('in progress', '1-3 deuce')

def test_random_18():
    assert tennis_score(list('AAAABAAAAABBAAABAAAAAAAAAABAAAAABAAAAAAABBAAAAAAAAAAABAAA')) == ('A won', '6-0 6-0')

def test_random_19():
    assert tennis_score(list('AABAAAAAABBBAAAABABABABABAAABBBBABAABAAAABBBBABAAAABABABBABABAABBBABBBABABBBBABABABAABBBABBBABBBABBAABAAAABAABBABBBBAABBBBBAAABAABAAAABBABABBABAAAABBAAAAABABBB')) == ('in progress', '6-4 5-5 advantage B')

def test_random_20():
    assert tennis_score(list('ABAAAABAAAAAAABBAABAABBABAAAABBAABAAABBABAABAABAAABABBABABAAABAABABABAAAAAAAAAAAAAA')) == ('A won', '6-0 6-1')

def test_random_21():
    assert tennis_score(list('AABAABBBAABABAABAABABBAABBAABABAAABABBBBAAAABBAABBAAAABBBAAAAAAAABBAAABBAAABAAABAAABBBBBBBBBAABBBBBBBBBAABAAAABBBBBBAABBBBAABAAABBAABABABBBBBAABBABABBBBBAABAABABAAB')) == ('in progress', '6-3 4-6 2-4 15-15')

def test_random_22():
    assert tennis_score(list('BAABBAAABABBBABAABBABABBAABABBAAABBAAAABBBBBBABBAABABABBAAABBBABBBBBBBBAABBAABABBBBBAAABABBBBBABBAABBBBABBAAAABBAAABAAAABBABBBBBB')) == ('B won', '4-6 4-6')

def test_random_23():
    assert tennis_score(list('BABBBBBABABBBABBABAABBABABBBBBBABABBBBBBBBBAABBBABBABABBBBBBAABBBBBABAABBB')) == ('B won', '0-6 0-6')

def test_random_24():
    with pytest.raises(ValueError):
        tennis_score(list('ABABBABBBBBABABBAAAABBBABBBBAAAABABBABBBBBBAAAABBBABBBBBABBBBBBBBBAABBBBBAABBBBBBB'))

def test_random_25():
    assert tennis_score(list('BABBBBBBABAAAABAAAABBBBABBBAABABBBABABBBBBAAAABAABBBABAAAABABBBABBABBAAAABAAAAAAABBABABAAAAAAAABBBBAAAABAAAABABBABAABBABBABABABABABABABABAABAAABBAABBBBABBBBAAAABBAABAABBBAAABABAAAAAB')) == ('in progress', '3-6 6-2 6-5 15-15')


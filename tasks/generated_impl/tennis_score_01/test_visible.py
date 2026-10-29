import pytest
from tennis_score import tennis_score


def G(winners):
    return [w for w in winners for _ in range(4)]

TO_6_6 = G("AAAAABBBBBAB")

def test_start():
    assert tennis_score([]) == ('in progress', '0-0 0-0')

def test_points():
    assert tennis_score(["A", "A", "B"]) == ('in progress', '0-0 30-15')

def test_deuce():
    assert tennis_score(["A", "B"] * 3) == ('in progress', '0-0 deuce')

def test_first_game():
    assert tennis_score(["B"] * 4 + ["A"]) == ('in progress', '0-1 15-0')

def test_straight_sets():
    assert tennis_score(["A"] * 48) == ('A won', '6-0 6-0')

import pytest
from glob_match import glob_match

def test_star_suffix():
    assert glob_match("report.txt", "*.txt") == True

def test_question():
    assert glob_match("cat", "c?t") == True

def test_class():
    assert glob_match("cot", "c[ao]t") == True

def test_negated_class():
    assert glob_match("cat", "c[!a]t") == False

def test_escaped_star():
    assert glob_match("a*b", "a\\*b") == True

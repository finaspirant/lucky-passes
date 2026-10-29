import pytest
from semver_match import semver_match

def test_caret():
    assert semver_match("1.4.2", "^1.2.0") == True

def test_caret_next_major():
    assert semver_match("2.0.0", "^1.2.0") == False

def test_tilde_next_minor():
    assert semver_match("1.3.0", "~1.2.5") == False

def test_and_range():
    assert semver_match("1.5.0", ">=1.0.0 <1.5.0") == False

def test_or_range():
    assert semver_match("3.1.0", "^1.0.0 || ^3.0.0") == True

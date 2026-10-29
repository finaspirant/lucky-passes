import pytest
from token_bucket import token_bucket

def test_burst():
    assert token_bucket(3, 1, [(0, 1), (0, 1), (0, 1), (0, 1)]) == [True, True, True, False]

def test_refill():
    assert token_bucket(2, 1, [(0, 2), (1, 1), (1.5, 1)]) == [True, True, False]

def test_fractional_cost():
    assert token_bucket(1, 0.5, [(0, 0.5), (0, 0.5), (0, 0.5), (1, 0.5)]) == [True, True, False, True]

def test_cost_above_capacity():
    assert token_bucket(2, 10, [(0, 3)]) == [False]

def test_decreasing_time():
    with pytest.raises(ValueError):
        token_bucket(2, 1, [(5, 1), (4, 1)])

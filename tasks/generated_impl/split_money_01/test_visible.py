import pytest
from split_money import split_money

def test_even_split():
    assert split_money(900, [1, 1, 1]) == [300, 300, 300]

def test_remainder_to_first():
    assert split_money(100, [1, 1, 1]) == [34, 33, 33]

def test_weighted():
    assert split_money(1000, [1, 2, 2]) == [200, 400, 400]

def test_largest_fraction_first():
    assert split_money(10, [1, 2]) == [3, 7]

def test_empty_weights():
    with pytest.raises(ValueError):
        split_money(10, [])

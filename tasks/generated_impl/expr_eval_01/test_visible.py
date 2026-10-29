import pytest
from expr_eval import expr_eval

def test_precedence():
    assert expr_eval("1 + 2 * 3") == 7

def test_parentheses():
    assert expr_eval("(1 + 2) * 3") == 9

def test_power_before_unary_minus():
    assert expr_eval("-2 ** 2") == -4

def test_floor_division():
    assert expr_eval("7 // -2") == -4

def test_trailing_operator():
    with pytest.raises(ValueError):
        expr_eval("1 +")

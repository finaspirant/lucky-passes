import pytest
from duration import format_duration, parse_duration

def test_parse_spaced():
    assert parse_duration('1h 15m 10s') == 4510

def test_parse_out_of_order():
    with pytest.raises(ValueError):
        parse_duration('30m1h')

def test_format_mixed():
    assert format_duration(3661) == '1h1m1s'

def test_format_carry():
    assert format_duration(90) == '1m30s'

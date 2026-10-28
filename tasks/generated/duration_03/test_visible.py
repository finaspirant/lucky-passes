import pytest
from duration import format_duration, parse_duration

def test_parse_seconds():
    assert parse_duration('45s') == 45

def test_parse_minutes():
    assert parse_duration('10m') == 600

def test_parse_out_of_order():
    with pytest.raises(ValueError):
        parse_duration('30m1h')

def test_format_mixed():
    assert format_duration(3661) == '1h1m1s'

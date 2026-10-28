import pytest
from duration import format_duration, parse_duration

def test_parse_days_hours():
    assert parse_duration('2d4h') == 187200

def test_parse_spaced():
    assert parse_duration('1h 15m 10s') == 4510

def test_format_mixed():
    assert format_duration(3661) == '1h1m1s'

def test_format_carry():
    assert format_duration(90) == '1m30s'

def test_format_hours():
    assert format_duration(7200) == '2h'

import pytest
from business_days import business_days
import datetime

D = datetime.date

def test_over_weekend():
    assert business_days(D(2026, 1, 2), 1) == datetime.date(2026, 1, 5)

def test_two_weeks():
    assert business_days(D(2026, 1, 5), 10) == datetime.date(2026, 1, 19)

def test_backwards():
    assert business_days(D(2026, 1, 5), -1) == datetime.date(2026, 1, 2)

def test_skips_holiday():
    assert business_days(D(2026, 12, 24), 1, {D(2026, 12, 25)}) == datetime.date(2026, 12, 28)

def test_start_is_datetime():
    with pytest.raises(TypeError):
        business_days(datetime.datetime(2026, 1, 1), 1)

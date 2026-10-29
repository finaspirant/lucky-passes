import pytest
from nth_weekday_dates import nth_weekday_dates
import datetime
from datetime import date

def test_first_monday():
    assert nth_weekday_dates(date(2026, 1, 1), date(2026, 3, 31), 0, 1) == [datetime.date(2026, 1, 5), datetime.date(2026, 2, 2), datetime.date(2026, 3, 2)]

def test_last_friday():
    assert nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 28), 4, -1) == [datetime.date(2026, 1, 30), datetime.date(2026, 2, 27)]

def test_fifth_friday_skips_months():
    assert nth_weekday_dates(date(2026, 1, 1), date(2026, 3, 31), 4, 5) == [datetime.date(2026, 1, 30)]

def test_single_day_range():
    assert nth_weekday_dates(date(2026, 1, 5), date(2026, 1, 5), 0, 1) == [datetime.date(2026, 1, 5)]

def test_invalid_n():
    with pytest.raises(ValueError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 12, 31), 0, 0)

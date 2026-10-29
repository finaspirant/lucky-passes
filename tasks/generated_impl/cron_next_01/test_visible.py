import pytest
from cron_next import cron_next
import datetime

DT = datetime.datetime

def test_every_15_minutes():
    assert cron_next("*/15 * * * *", DT(2026, 1, 1, 10, 7)) == datetime.datetime(2026, 1, 1, 10, 15)

def test_weekdays_at_9():
    assert cron_next("0 9 * * 1-5", DT(2026, 1, 2, 9, 0)) == datetime.datetime(2026, 1, 5, 9, 0)

def test_day_of_month_or_week():
    assert cron_next("30 4 1,15 * 5", DT(2026, 1, 2, 5, 0)) == datetime.datetime(2026, 1, 9, 4, 30)

def test_next_year():
    assert cron_next("0 0 1 1 *", DT(2026, 6, 1)) == datetime.datetime(2027, 1, 1, 0, 0)

def test_four_fields():
    with pytest.raises(ValueError):
        cron_next("* * * *", DT(2026, 1, 1))

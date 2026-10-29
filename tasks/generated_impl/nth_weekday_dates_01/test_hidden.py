import pytest
from nth_weekday_dates import nth_weekday_dates
import datetime
from datetime import date

CASE_TIME_LIMIT = 3
PRELUDE = 'from nth_weekday_dates import nth_weekday_dates\nimport datetime\nfrom datetime import date\n'

import os
import signal
import subprocess
import sys


@pytest.fixture(autouse=True)
def case_time_limit(request):
    """Fail a non-large case that runs longer than CASE_TIME_LIMIT seconds."""
    if request.node.name.startswith("test_large_"):
        yield
        return

    def expire(signum, frame):
        raise TimeoutError("case time limit exceeded")

    previous = signal.signal(signal.SIGALRM, expire)
    signal.alarm(CASE_TIME_LIMIT)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def run_limited(expr, seconds):
    """Evaluate expr in a child process with a time limit; return the repr of its value."""
    code = PRELUDE + "\nprint(repr(" + expr + "))\n"
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=here, capture_output=True, text=True,
                              timeout=seconds)
    except subprocess.TimeoutExpired:
        pytest.fail(f"time limit of {seconds}s exceeded")
    if proc.returncode:
        lines = proc.stderr.strip().splitlines()
        pytest.fail(lines[-1] if lines else "child process failed")
    return proc.stdout.strip()

def test_edge_val_start_is_datetime():
    with pytest.raises(TypeError):
        nth_weekday_dates(datetime.datetime(2026, 1, 1), date(2026, 2, 1), 0, 1)

def test_edge_val_end_is_str():
    with pytest.raises(TypeError):
        nth_weekday_dates(date(2026, 1, 1), "2026-02-01", 0, 1)

def test_edge_val_weekday_bool():
    with pytest.raises(TypeError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), True, 1)

def test_edge_val_weekday_float():
    with pytest.raises(TypeError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 1.0, 1)

def test_edge_val_n_bool():
    with pytest.raises(TypeError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 0, True)

def test_edge_val_weekday_seven():
    with pytest.raises(ValueError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 7, 1)

def test_edge_val_weekday_negative():
    with pytest.raises(ValueError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), -1, 1)

def test_edge_val_n_six():
    with pytest.raises(ValueError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 0, 6)

def test_edge_val_n_minus_two():
    with pytest.raises(ValueError):
        nth_weekday_dates(date(2026, 1, 1), date(2026, 2, 1), 0, -2)

def test_edge_val_start_after_end():
    with pytest.raises(ValueError):
        nth_weekday_dates(date(2026, 2, 1), date(2026, 1, 1), 0, 1)

def test_edge_val_type_checked_before_value():
    with pytest.raises(TypeError):
        nth_weekday_dates(date(2026, 2, 1), date(2026, 1, 1), 0, 1.5)

def test_edge_logic_leap_fifth_thursday():
    assert nth_weekday_dates(date(2024, 2, 1), date(2024, 2, 29), 3, 5) == [datetime.date(2024, 2, 29)]

def test_edge_logic_non_leap_no_fifth():
    assert nth_weekday_dates(date(2023, 2, 1), date(2023, 2, 28), 3, 5) == []

def test_edge_logic_century_not_leap():
    assert nth_weekday_dates(date(1900, 2, 1), date(1900, 2, 28), 2, -1) == [datetime.date(1900, 2, 28)]

def test_edge_logic_century_leap():
    assert nth_weekday_dates(date(2000, 2, 1), date(2000, 2, 29), 1, -1) == [datetime.date(2000, 2, 29)]

def test_edge_logic_start_after_occurrence():
    assert nth_weekday_dates(date(2026, 1, 6), date(2026, 2, 10), 0, 1) == [datetime.date(2026, 2, 2)]

def test_edge_logic_end_before_occurrence():
    assert nth_weekday_dates(date(2026, 1, 1), date(2026, 1, 4), 0, 1) == []

def test_edge_logic_single_day_no_match():
    assert nth_weekday_dates(date(2026, 1, 6), date(2026, 1, 6), 0, 1) == []

def test_edge_logic_last_is_month_end():
    assert nth_weekday_dates(date(2026, 1, 1), date(2026, 1, 31), 5, -1) == [datetime.date(2026, 1, 31)]

def test_edge_logic_first_is_month_start():
    assert nth_weekday_dates(date(2026, 2, 1), date(2026, 2, 28), 6, 1) == [datetime.date(2026, 2, 1)]

def test_edge_logic_fourth_sunday():
    assert nth_weekday_dates(date(2026, 3, 1), date(2026, 3, 31), 6, 4) == [datetime.date(2026, 3, 22)]

def test_edge_logic_across_year_end():
    assert nth_weekday_dates(date(2025, 12, 1), date(2026, 1, 31), 3, 2) == [datetime.date(2025, 12, 11), datetime.date(2026, 1, 8)]

def test_edge_logic_last_day_of_calendar():
    assert nth_weekday_dates(date(9999, 12, 1), date(9999, 12, 31), 4, -1) == [datetime.date(9999, 12, 31)]

def test_edge_logic_first_day_of_calendar():
    assert nth_weekday_dates(date(1, 1, 1), date(1, 1, 31), 0, 1) == [datetime.date(1, 1, 1)]

def test_random_01():
    assert nth_weekday_dates(date(2012, 3, 10), date(2013, 7, 17), 5, 2) == [datetime.date(2012, 3, 10), datetime.date(2012, 4, 14), datetime.date(2012, 5, 12), datetime.date(2012, 6, 9), datetime.date(2012, 7, 14), datetime.date(2012, 8, 11), datetime.date(2012, 9, 8), datetime.date(2012, 10, 13), datetime.date(2012, 11, 10), datetime.date(2012, 12, 8), datetime.date(2013, 1, 12), datetime.date(2013, 2, 9), datetime.date(2013, 3, 9), datetime.date(2013, 4, 13), datetime.date(2013, 5, 11), datetime.date(2013, 6, 8), datetime.date(2013, 7, 13)]

def test_random_02():
    assert nth_weekday_dates(date(1993, 8, 13), date(1995, 8, 27), 0, -1) == [datetime.date(1993, 8, 30), datetime.date(1993, 9, 27), datetime.date(1993, 10, 25), datetime.date(1993, 11, 29), datetime.date(1993, 12, 27), datetime.date(1994, 1, 31), datetime.date(1994, 2, 28), datetime.date(1994, 3, 28), datetime.date(1994, 4, 25), datetime.date(1994, 5, 30), datetime.date(1994, 6, 27), datetime.date(1994, 7, 25), datetime.date(1994, 8, 29), datetime.date(1994, 9, 26), datetime.date(1994, 10, 31), datetime.date(1994, 11, 28), datetime.date(1994, 12, 26), datetime.date(1995, 1, 30), datetime.date(1995, 2, 27), datetime.date(1995, 3, 27), datetime.date(1995, 4, 24), datetime.date(1995, 5, 29), datetime.date(1995, 6, 26), datetime.date(1995, 7, 31)]

def test_random_03():
    assert nth_weekday_dates(date(2022, 2, 15), date(2022, 5, 2), 4, 1) == [datetime.date(2022, 3, 4), datetime.date(2022, 4, 1)]

def test_random_04():
    assert nth_weekday_dates(date(2005, 12, 24), date(2006, 2, 2), 1, -1) == [datetime.date(2005, 12, 27), datetime.date(2006, 1, 31)]

def test_random_05():
    assert nth_weekday_dates(date(2025, 10, 25), date(2026, 12, 10), 5, 4) == [datetime.date(2025, 10, 25), datetime.date(2025, 11, 22), datetime.date(2025, 12, 27), datetime.date(2026, 1, 24), datetime.date(2026, 2, 28), datetime.date(2026, 3, 28), datetime.date(2026, 4, 25), datetime.date(2026, 5, 23), datetime.date(2026, 6, 27), datetime.date(2026, 7, 25), datetime.date(2026, 8, 22), datetime.date(2026, 9, 26), datetime.date(2026, 10, 24), datetime.date(2026, 11, 28)]

def test_random_06():
    assert nth_weekday_dates(date(2027, 11, 22), date(2029, 6, 27), 5, 1) == [datetime.date(2027, 12, 4), datetime.date(2028, 1, 1), datetime.date(2028, 2, 5), datetime.date(2028, 3, 4), datetime.date(2028, 4, 1), datetime.date(2028, 5, 6), datetime.date(2028, 6, 3), datetime.date(2028, 7, 1), datetime.date(2028, 8, 5), datetime.date(2028, 9, 2), datetime.date(2028, 10, 7), datetime.date(2028, 11, 4), datetime.date(2028, 12, 2), datetime.date(2029, 1, 6), datetime.date(2029, 2, 3), datetime.date(2029, 3, 3), datetime.date(2029, 4, 7), datetime.date(2029, 5, 5), datetime.date(2029, 6, 2)]

def test_random_07():
    assert nth_weekday_dates(date(2028, 2, 17), date(2029, 1, 30), 6, -1) == [datetime.date(2028, 2, 27), datetime.date(2028, 3, 26), datetime.date(2028, 4, 30), datetime.date(2028, 5, 28), datetime.date(2028, 6, 25), datetime.date(2028, 7, 30), datetime.date(2028, 8, 27), datetime.date(2028, 9, 24), datetime.date(2028, 10, 29), datetime.date(2028, 11, 26), datetime.date(2028, 12, 31), datetime.date(2029, 1, 28)]

def test_random_08():
    assert nth_weekday_dates(date(2017, 5, 19), date(2017, 6, 3), 5, -1) == [datetime.date(2017, 5, 27)]

def test_random_09():
    assert nth_weekday_dates(date(2005, 8, 31), date(2005, 10, 8), 5, -1) == [datetime.date(2005, 9, 24)]

def test_random_10():
    assert nth_weekday_dates(date(2002, 2, 12), date(2004, 2, 1), 5, 3) == [datetime.date(2002, 2, 16), datetime.date(2002, 3, 16), datetime.date(2002, 4, 20), datetime.date(2002, 5, 18), datetime.date(2002, 6, 15), datetime.date(2002, 7, 20), datetime.date(2002, 8, 17), datetime.date(2002, 9, 21), datetime.date(2002, 10, 19), datetime.date(2002, 11, 16), datetime.date(2002, 12, 21), datetime.date(2003, 1, 18), datetime.date(2003, 2, 15), datetime.date(2003, 3, 15), datetime.date(2003, 4, 19), datetime.date(2003, 5, 17), datetime.date(2003, 6, 21), datetime.date(2003, 7, 19), datetime.date(2003, 8, 16), datetime.date(2003, 9, 20), datetime.date(2003, 10, 18), datetime.date(2003, 11, 15), datetime.date(2003, 12, 20), datetime.date(2004, 1, 17)]

def test_random_11():
    assert nth_weekday_dates(date(2023, 3, 15), date(2024, 2, 24), 6, 1) == [datetime.date(2023, 4, 2), datetime.date(2023, 5, 7), datetime.date(2023, 6, 4), datetime.date(2023, 7, 2), datetime.date(2023, 8, 6), datetime.date(2023, 9, 3), datetime.date(2023, 10, 1), datetime.date(2023, 11, 5), datetime.date(2023, 12, 3), datetime.date(2024, 1, 7), datetime.date(2024, 2, 4)]

def test_random_12():
    assert nth_weekday_dates(date(2024, 1, 25), date(2024, 11, 6), 1, 5) == [datetime.date(2024, 1, 30), datetime.date(2024, 4, 30), datetime.date(2024, 7, 30), datetime.date(2024, 10, 29)]

def test_random_13():
    assert nth_weekday_dates(date(2006, 9, 18), date(2007, 9, 4), 5, 2) == [datetime.date(2006, 10, 14), datetime.date(2006, 11, 11), datetime.date(2006, 12, 9), datetime.date(2007, 1, 13), datetime.date(2007, 2, 10), datetime.date(2007, 3, 10), datetime.date(2007, 4, 14), datetime.date(2007, 5, 12), datetime.date(2007, 6, 9), datetime.date(2007, 7, 14), datetime.date(2007, 8, 11)]

def test_random_14():
    assert nth_weekday_dates(date(1991, 8, 21), date(1993, 6, 17), 3, -1) == [datetime.date(1991, 8, 29), datetime.date(1991, 9, 26), datetime.date(1991, 10, 31), datetime.date(1991, 11, 28), datetime.date(1991, 12, 26), datetime.date(1992, 1, 30), datetime.date(1992, 2, 27), datetime.date(1992, 3, 26), datetime.date(1992, 4, 30), datetime.date(1992, 5, 28), datetime.date(1992, 6, 25), datetime.date(1992, 7, 30), datetime.date(1992, 8, 27), datetime.date(1992, 9, 24), datetime.date(1992, 10, 29), datetime.date(1992, 11, 26), datetime.date(1992, 12, 31), datetime.date(1993, 1, 28), datetime.date(1993, 2, 25), datetime.date(1993, 3, 25), datetime.date(1993, 4, 29), datetime.date(1993, 5, 27)]

def test_random_15():
    assert nth_weekday_dates(date(2023, 4, 28), date(2023, 4, 30), 5, 1) == []

def test_random_16():
    assert nth_weekday_dates(date(2002, 11, 7), date(2004, 8, 6), 0, 4) == [datetime.date(2002, 11, 25), datetime.date(2002, 12, 23), datetime.date(2003, 1, 27), datetime.date(2003, 2, 24), datetime.date(2003, 3, 24), datetime.date(2003, 4, 28), datetime.date(2003, 5, 26), datetime.date(2003, 6, 23), datetime.date(2003, 7, 28), datetime.date(2003, 8, 25), datetime.date(2003, 9, 22), datetime.date(2003, 10, 27), datetime.date(2003, 11, 24), datetime.date(2003, 12, 22), datetime.date(2004, 1, 26), datetime.date(2004, 2, 23), datetime.date(2004, 3, 22), datetime.date(2004, 4, 26), datetime.date(2004, 5, 24), datetime.date(2004, 6, 28), datetime.date(2004, 7, 26)]

def test_random_17():
    assert nth_weekday_dates(date(2028, 12, 18), date(2029, 4, 4), 3, 5) == [datetime.date(2029, 3, 29)]

def test_random_18():
    assert nth_weekday_dates(date(2005, 8, 22), date(2006, 3, 2), 5, 3) == [datetime.date(2005, 9, 17), datetime.date(2005, 10, 15), datetime.date(2005, 11, 19), datetime.date(2005, 12, 17), datetime.date(2006, 1, 21), datetime.date(2006, 2, 18)]

def test_random_19():
    assert nth_weekday_dates(date(2027, 3, 14), date(2029, 3, 1), 6, 5) == [datetime.date(2027, 5, 30), datetime.date(2027, 8, 29), datetime.date(2027, 10, 31), datetime.date(2028, 1, 30), datetime.date(2028, 4, 30), datetime.date(2028, 7, 30), datetime.date(2028, 10, 29), datetime.date(2028, 12, 31)]

def test_random_20():
    assert nth_weekday_dates(date(1997, 12, 15), date(1999, 3, 14), 2, -1) == [datetime.date(1997, 12, 31), datetime.date(1998, 1, 28), datetime.date(1998, 2, 25), datetime.date(1998, 3, 25), datetime.date(1998, 4, 29), datetime.date(1998, 5, 27), datetime.date(1998, 6, 24), datetime.date(1998, 7, 29), datetime.date(1998, 8, 26), datetime.date(1998, 9, 30), datetime.date(1998, 10, 28), datetime.date(1998, 11, 25), datetime.date(1998, 12, 30), datetime.date(1999, 1, 27), datetime.date(1999, 2, 24)]

def test_random_21():
    assert nth_weekday_dates(date(2029, 9, 18), date(2030, 6, 18), 0, 1) == [datetime.date(2029, 10, 1), datetime.date(2029, 11, 5), datetime.date(2029, 12, 3), datetime.date(2030, 1, 7), datetime.date(2030, 2, 4), datetime.date(2030, 3, 4), datetime.date(2030, 4, 1), datetime.date(2030, 5, 6), datetime.date(2030, 6, 3)]

def test_random_22():
    assert nth_weekday_dates(date(1994, 3, 10), date(1995, 5, 17), 2, -1) == [datetime.date(1994, 3, 30), datetime.date(1994, 4, 27), datetime.date(1994, 5, 25), datetime.date(1994, 6, 29), datetime.date(1994, 7, 27), datetime.date(1994, 8, 31), datetime.date(1994, 9, 28), datetime.date(1994, 10, 26), datetime.date(1994, 11, 30), datetime.date(1994, 12, 28), datetime.date(1995, 1, 25), datetime.date(1995, 2, 22), datetime.date(1995, 3, 29), datetime.date(1995, 4, 26)]

def test_random_23():
    assert nth_weekday_dates(date(2011, 7, 21), date(2012, 9, 3), 5, 1) == [datetime.date(2011, 8, 6), datetime.date(2011, 9, 3), datetime.date(2011, 10, 1), datetime.date(2011, 11, 5), datetime.date(2011, 12, 3), datetime.date(2012, 1, 7), datetime.date(2012, 2, 4), datetime.date(2012, 3, 3), datetime.date(2012, 4, 7), datetime.date(2012, 5, 5), datetime.date(2012, 6, 2), datetime.date(2012, 7, 7), datetime.date(2012, 8, 4), datetime.date(2012, 9, 1)]

def test_random_24():
    assert nth_weekday_dates(date(2015, 3, 25), date(2017, 5, 29), 2, 4) == [datetime.date(2015, 3, 25), datetime.date(2015, 4, 22), datetime.date(2015, 5, 27), datetime.date(2015, 6, 24), datetime.date(2015, 7, 22), datetime.date(2015, 8, 26), datetime.date(2015, 9, 23), datetime.date(2015, 10, 28), datetime.date(2015, 11, 25), datetime.date(2015, 12, 23), datetime.date(2016, 1, 27), datetime.date(2016, 2, 24), datetime.date(2016, 3, 23), datetime.date(2016, 4, 27), datetime.date(2016, 5, 25), datetime.date(2016, 6, 22), datetime.date(2016, 7, 27), datetime.date(2016, 8, 24), datetime.date(2016, 9, 28), datetime.date(2016, 10, 26), datetime.date(2016, 11, 23), datetime.date(2016, 12, 28), datetime.date(2017, 1, 25), datetime.date(2017, 2, 22), datetime.date(2017, 3, 22), datetime.date(2017, 4, 26), datetime.date(2017, 5, 24)]

def test_random_25():
    assert nth_weekday_dates(date(1992, 7, 23), date(1992, 10, 13), 0, 5) == [datetime.date(1992, 8, 31)]

def test_large_whole_calendar_last_friday():
    assert run_limited('(lambda r: (len(r), r[0], r[-1]))(nth_weekday_dates(date.min, date.max, 4, -1))', 10) == '(119988, datetime.date(1, 1, 26), datetime.date(9999, 12, 31))'

def test_large_whole_calendar_fifth_monday():
    assert run_limited('(lambda r: (len(r), r[0], r[-1]))(nth_weekday_dates(date.min, date.max, 0, 5))', 10) == '(41771, datetime.date(1, 1, 29), datetime.date(9999, 11, 29))'

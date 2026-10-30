import pytest
from business_days import business_days
import datetime

D = datetime.date

CASE_TIME_LIMIT = 3
PRELUDE = 'from business_days import business_days\nimport datetime\n\nD = datetime.date\n'

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
    """Evaluate expr in a child process with a time limit.

    Returns the repr of its value, or "raises <ExceptionName>" if it raises.
    """
    code = (PRELUDE + "\ntry:\n    print(repr(" + expr + "))\n"
            "except Exception as exc:\n    print('raises ' + type(exc).__name__)\n")
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=here, capture_output=True, text=True,
                              timeout=seconds)
    except subprocess.TimeoutExpired:
        pytest.fail(f"time limit of {seconds}s exceeded")
    if proc.returncode:
        lines = proc.stderr.strip().splitlines()
        pytest.fail(lines[-1] if lines else "child process failed")
    lines = proc.stdout.strip().splitlines()
    return lines[-1] if lines else ""

def test_edge_val_n_is_bool():
    with pytest.raises(TypeError):
        business_days(D(2026, 1, 1), True)

def test_edge_val_holiday_is_datetime():
    with pytest.raises(TypeError):
        business_days(D(2026, 1, 1), 1, [datetime.datetime(2026, 1, 2)])

def test_edge_val_holidays_is_dict():
    with pytest.raises(TypeError):
        business_days(D(2026, 1, 1), 1, {D(2026, 1, 2): 1})

def test_edge_logic_zero_returns_start():
    assert business_days(D(2026, 1, 3), 0) == datetime.date(2026, 1, 3)

def test_edge_logic_start_on_saturday():
    assert business_days(D(2026, 1, 3), 1) == datetime.date(2026, 1, 5)

def test_edge_logic_start_on_sunday_backwards():
    assert business_days(D(2026, 1, 4), -1) == datetime.date(2026, 1, 2)

def test_edge_logic_friday_plus_five():
    assert business_days(D(2026, 1, 2), 5) == datetime.date(2026, 1, 9)

def test_edge_logic_holiday_on_weekend_ignored():
    assert business_days(D(2026, 1, 2), 1, (D(2026, 1, 3),)) == datetime.date(2026, 1, 5)

def test_edge_logic_holiday_backwards():
    assert business_days(D(2026, 1, 6), -1, frozenset({D(2026, 1, 5)})) == datetime.date(2026, 1, 2)

def test_edge_logic_consecutive_holidays():
    assert business_days(D(2026, 1, 1), 1, [D(2026, 1, 2), D(2026, 1, 5), D(2026, 1, 6)]) == datetime.date(2026, 1, 7)

def test_edge_logic_start_is_holiday():
    assert business_days(D(2026, 1, 2), 1, {D(2026, 1, 2)}) == datetime.date(2026, 1, 5)

def test_edge_logic_leap_day():
    assert business_days(D(2028, 2, 28), 1) == datetime.date(2028, 2, 29)

def test_edge_logic_year_end():
    assert business_days(D(2026, 12, 31), 1) == datetime.date(2027, 1, 1)

def test_edge_logic_reaches_date_max():
    assert business_days(D(9999, 12, 30), 1) == datetime.date(9999, 12, 31)

def test_edge_logic_past_date_max():
    with pytest.raises(ValueError):
        business_days(D(9999, 12, 30), 2)

def test_edge_logic_from_date_max():
    with pytest.raises(ValueError):
        business_days(D(9999, 12, 31), 1)

def test_edge_logic_past_date_max_holiday():
    with pytest.raises(ValueError):
        business_days(D(9999, 12, 30), 1, {D(9999, 12, 31)})

def test_edge_logic_past_date_max_weekend():
    with pytest.raises(ValueError):
        business_days(D(9999, 12, 24), 6)

def test_edge_logic_reaches_date_min():
    assert business_days(D(1, 1, 4), -3) == datetime.date(1, 1, 1)

def test_edge_logic_past_date_min():
    with pytest.raises(ValueError):
        business_days(D(1, 1, 4), -4)

def test_edge_logic_from_date_min():
    with pytest.raises(ValueError):
        business_days(D(1, 1, 1), -1)

def test_edge_logic_zero_at_date_max():
    assert business_days(D(9999, 12, 31), 0) == datetime.date(9999, 12, 31)

def test_random_01():
    assert business_days(D(2048, 1, 2), 11, [D(2047, 10, 17), D(2047, 11, 9), D(2048, 1, 7), D(2048, 2, 16), D(2048, 2, 26)]) == datetime.date(2048, 1, 20)

def test_random_02():
    assert business_days(D(2029, 2, 23), -6, [D(2029, 1, 9), D(2029, 1, 25), D(2029, 3, 2), D(2029, 3, 5), D(2029, 5, 16), D(2029, 5, 21)]) == datetime.date(2029, 2, 15)

def test_random_03():
    assert business_days(D(2010, 8, 30), -51, [D(2010, 7, 7), D(2010, 7, 11), D(2010, 8, 4), D(2010, 9, 10), D(2010, 10, 3), D(2010, 10, 19), D(2010, 11, 3)]) == datetime.date(2010, 6, 16)

def test_random_04():
    assert business_days(D(2028, 7, 12), 40) == datetime.date(2028, 9, 6)

def test_random_05():
    assert business_days(D(1993, 12, 31), 18) == datetime.date(1994, 1, 26)

def test_random_06():
    assert business_days(D(2010, 2, 9), 25, [D(2010, 2, 18), D(2010, 4, 9)]) == datetime.date(2010, 3, 17)

def test_random_07():
    assert business_days(D(2005, 4, 16), 24, [D(2005, 2, 14), D(2005, 2, 15), D(2005, 3, 8), D(2005, 4, 5), D(2005, 4, 10), D(2005, 5, 7), D(2005, 6, 16), D(2005, 7, 10)]) == datetime.date(2005, 5, 19)

def test_random_08():
    assert business_days(D(2030, 11, 17), -18, [D(2030, 9, 6), D(2030, 12, 1), D(2030, 12, 9), D(2031, 1, 25)]) == datetime.date(2030, 10, 23)

def test_random_09():
    assert business_days(D(2032, 3, 28), 12, [D(2032, 2, 11), D(2032, 2, 26), D(2032, 2, 27), D(2032, 5, 8), D(2032, 5, 10), D(2032, 5, 18), D(2032, 6, 20)]) == datetime.date(2032, 4, 13)

def test_random_10():
    assert business_days(D(2033, 3, 14), 19, [D(2033, 1, 6), D(2033, 2, 18), D(2033, 2, 25)]) == datetime.date(2033, 4, 8)

def test_random_11():
    assert business_days(D(2017, 7, 14), 52, [D(2017, 4, 26), D(2017, 5, 2), D(2017, 6, 14), D(2017, 6, 23), D(2017, 6, 28), D(2017, 8, 12), D(2017, 9, 7)]) == datetime.date(2017, 9, 27)

def test_random_12():
    assert business_days(D(2049, 2, 15), 53) == datetime.date(2049, 4, 29)

def test_random_13():
    assert business_days(D(2015, 2, 7), 8, [D(2014, 12, 6), D(2015, 1, 15), D(2015, 2, 10), D(2015, 2, 23), D(2015, 2, 26), D(2015, 3, 13), D(2015, 3, 21), D(2015, 4, 20)]) == datetime.date(2015, 2, 19)

def test_random_14():
    assert business_days(D(2005, 1, 30), -28, [D(2004, 12, 14), D(2005, 1, 1), D(2005, 1, 8), D(2005, 3, 6), D(2005, 3, 10)]) == datetime.date(2004, 12, 22)

def test_random_15():
    assert business_days(D(2041, 9, 8), 47) == datetime.date(2041, 11, 12)

def test_random_16():
    assert business_days(D(2031, 8, 7), -26, [D(2031, 7, 6), D(2031, 7, 15), D(2031, 7, 29), D(2031, 10, 1)]) == datetime.date(2031, 6, 30)

def test_random_17():
    assert business_days(D(2027, 9, 8), -60, [D(2027, 6, 17), D(2027, 6, 21), D(2027, 8, 18), D(2027, 8, 23), D(2027, 9, 4)]) == datetime.date(2027, 6, 10)

def test_random_18():
    assert business_days(D(2021, 7, 9), 57, [D(2021, 6, 14), D(2021, 7, 20)]) == datetime.date(2021, 9, 29)

def test_random_19():
    assert business_days(D(1998, 9, 17), 40, [D(1998, 6, 24), D(1998, 6, 27), D(1998, 6, 30), D(1998, 7, 30), D(1998, 8, 7), D(1998, 8, 13), D(1998, 11, 5)]) == datetime.date(1998, 11, 13)

def test_random_20():
    assert business_days(D(1991, 5, 9), 53, [D(1991, 4, 21), D(1991, 5, 4)]) == datetime.date(1991, 7, 23)

def test_random_21():
    assert business_days(D(2048, 6, 7), 41, [D(2048, 3, 24), D(2048, 4, 23), D(2048, 4, 27), D(2048, 6, 24), D(2048, 8, 3), D(2048, 9, 4)]) == datetime.date(2048, 8, 5)

def test_random_22():
    assert business_days(D(1994, 4, 21), -12, [D(1994, 4, 27), D(1994, 7, 17)]) == datetime.date(1994, 4, 5)

def test_random_23():
    assert business_days(D(2037, 3, 11), -50, [D(2036, 12, 28), D(2037, 1, 24), D(2037, 2, 17)]) == datetime.date(2036, 12, 30)

def test_random_24():
    assert business_days(D(2026, 2, 8), 48, [D(2026, 1, 27)]) == datetime.date(2026, 4, 15)

def test_random_25():
    assert business_days(D(1994, 6, 16), 51, [D(1994, 4, 3), D(1994, 5, 2), D(1994, 5, 23), D(1994, 7, 18), D(1994, 7, 20), D(1994, 8, 18)]) == datetime.date(1994, 8, 31)

def test_random_26():
    assert business_days(D(1992, 1, 17), 14) == datetime.date(1992, 2, 6)

def test_random_27():
    assert business_days(D(2041, 8, 19), 45, [D(2041, 6, 2), D(2041, 8, 6), D(2041, 10, 15), D(2041, 11, 2), D(2041, 11, 6)]) == datetime.date(2041, 10, 22)

def test_random_28():
    assert business_days(D(2014, 5, 12), 14, [D(2014, 5, 11), D(2014, 5, 19), D(2014, 5, 28), D(2014, 6, 5), D(2014, 6, 7), D(2014, 6, 18), D(2014, 7, 3), D(2014, 7, 31)]) == datetime.date(2014, 6, 3)

def test_random_29():
    assert business_days(D(2039, 12, 23), -21) == datetime.date(2039, 11, 24)

def test_random_30():
    assert business_days(D(1990, 3, 13), 56, [D(1989, 12, 29), D(1990, 1, 11), D(1990, 3, 18)]) == datetime.date(1990, 5, 30)


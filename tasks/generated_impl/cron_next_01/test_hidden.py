import pytest
from cron_next import cron_next
import datetime

DT = datetime.datetime

CASE_TIME_LIMIT = 3
PRELUDE = 'from cron_next import cron_next\nimport datetime\n\nDT = datetime.datetime\n'

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

def test_edge_val_after_is_date():
    with pytest.raises(TypeError):
        cron_next("* * * * *", datetime.date(2026, 1, 1))

def test_edge_val_step_after_single_value():
    with pytest.raises(ValueError):
        cron_next("5/15 * * * *", DT(2026, 1, 1))

def test_edge_val_hour_out_of_range():
    with pytest.raises(ValueError):
        cron_next("0 24 * * *", DT(2026, 1, 1))

def test_edge_logic_seconds_ignored():
    assert cron_next("* * * * *", DT(2026, 1, 1, 10, 0, 30)) == datetime.datetime(2026, 1, 1, 10, 1)

def test_edge_logic_strictly_after():
    assert cron_next("*/15 * * * *", DT(2026, 1, 1, 10, 15)) == datetime.datetime(2026, 1, 1, 10, 30)

def test_edge_logic_microseconds_before_match():
    assert cron_next("15 10 * * *", DT(2026, 1, 1, 10, 14, 59, 999999)) == datetime.datetime(2026, 1, 1, 10, 15)

def test_edge_logic_same_minute_not_returned():
    assert cron_next("30 10 1 1 *", DT(2026, 1, 1, 10, 30)) == datetime.datetime(2027, 1, 1, 10, 30)

def test_edge_logic_range_with_step():
    assert cron_next("1-10/3 * * * *", DT(2026, 1, 1, 10, 5)) == datetime.datetime(2026, 1, 1, 10, 7)

def test_edge_logic_range_with_step_wraps_hour():
    assert cron_next("1-10/3 * * * *", DT(2026, 1, 1, 10, 10)) == datetime.datetime(2026, 1, 1, 11, 1)

def test_edge_logic_list_and_range():
    assert cron_next("5,10-12 * * * *", DT(2026, 1, 1, 10, 10)) == datetime.datetime(2026, 1, 1, 10, 11)

def test_edge_logic_hour_step_wraps_day():
    assert cron_next("0 */6 * * *", DT(2026, 1, 1, 19, 0)) == datetime.datetime(2026, 1, 2, 0, 0)

def test_edge_logic_leading_zeros():
    assert cron_next("05 07 * * *", DT(2026, 1, 1, 8, 0)) == datetime.datetime(2026, 1, 2, 7, 5)

def test_edge_logic_extra_whitespace():
    assert cron_next("  0\t12  *  * *  ", DT(2026, 1, 1)) == datetime.datetime(2026, 1, 1, 12, 0)

def test_edge_logic_seven_is_sunday():
    assert cron_next("0 0 * * 7", DT(2026, 1, 1)) == datetime.datetime(2026, 1, 4, 0, 0)

def test_edge_logic_weekend_range_to_seven():
    assert cron_next("0 0 * * 6-7", DT(2026, 1, 3, 12, 0)) == datetime.datetime(2026, 1, 4, 0, 0)

def test_edge_logic_zero_and_seven():
    assert cron_next("0 0 * * 0,7", DT(2026, 1, 4)) == datetime.datetime(2026, 1, 11, 0, 0)

def test_edge_logic_day_of_month_only():
    assert cron_next("0 0 13 * *", DT(2026, 1, 1)) == datetime.datetime(2026, 1, 13, 0, 0)

def test_edge_logic_day_of_week_only():
    assert cron_next("0 0 * * 2", DT(2026, 1, 1)) == datetime.datetime(2026, 1, 6, 0, 0)

def test_edge_logic_either_day_week_first():
    assert cron_next("0 0 13 * 2", DT(2026, 1, 1)) == datetime.datetime(2026, 1, 6, 0, 0)

def test_edge_logic_either_day_month_first():
    assert cron_next("0 0 3 * 2", DT(2026, 1, 1)) == datetime.datetime(2026, 1, 3, 0, 0)

def test_edge_logic_star_step_is_restricted():
    assert cron_next("0 0 */1 * 1", DT(2026, 1, 1, 12, 0)) == datetime.datetime(2026, 1, 2, 0, 0)

def test_edge_logic_week_step_is_restricted():
    assert cron_next("0 0 20 * */3", DT(2026, 1, 1, 12, 0)) == datetime.datetime(2026, 1, 3, 0, 0)

def test_edge_logic_month_limits_either_rule():
    assert cron_next("0 0 1 3 1", DT(2026, 1, 1)) == datetime.datetime(2026, 3, 1, 0, 0)

def test_edge_logic_day_31_skips_short_months():
    assert cron_next("0 0 31 * *", DT(2026, 1, 31)) == datetime.datetime(2026, 3, 31, 0, 0)

def test_edge_logic_leap_day():
    assert cron_next("0 0 29 2 *", DT(2027, 3, 1)) == datetime.datetime(2028, 2, 29, 0, 0)

def test_edge_logic_year_rollover():
    assert cron_next("59 23 31 12 *", DT(2026, 12, 31, 23, 59)) == datetime.datetime(2027, 12, 31, 23, 59)

def test_edge_logic_month_list():
    assert cron_next("0 0 1 4,6 *", DT(2026, 4, 1)) == datetime.datetime(2026, 6, 1, 0, 0)

def test_edge_logic_end_of_calendar():
    assert cron_next("* * * * *", DT(9999, 12, 31, 23, 58)) == datetime.datetime(9999, 12, 31, 23, 59)

def test_edge_logic_past_end_of_calendar():
    with pytest.raises(ValueError):
        cron_next("* * * * *", DT(9999, 12, 31, 23, 59))

def test_random_01():
    assert cron_next('0 23 29 */3 0', DT(2024, 9, 11, 0, 29, 30)) == datetime.datetime(2024, 10, 6, 23, 0)

def test_random_02():
    assert cron_next('30 0 31 1-6 6,0', DT(2001, 12, 14, 0, 25, 59)) == datetime.datetime(2002, 1, 5, 0, 30)

def test_random_03():
    assert cron_next('0-59/7 23 13 */3 *', DT(2025, 6, 16, 14, 17, 30)) == datetime.datetime(2025, 7, 13, 23, 0)

def test_random_04():
    assert cron_next('*/15 * * 4,6,9,11 6,0', DT(2016, 7, 17, 10, 51, 59)) == datetime.datetime(2016, 9, 3, 0, 0)

def test_random_05():
    assert cron_next('0 9-17 * 4,6,9,11 1-5', DT(2004, 5, 16, 4, 59, 59)) == datetime.datetime(2004, 6, 1, 9, 0)

def test_random_06():
    assert cron_next('10-20/5 0 15 4,6,9,11 *', DT(2002, 6, 16, 10, 47, 0)) == datetime.datetime(2002, 9, 15, 0, 10)

def test_random_07():
    assert cron_next('10-20/5 */6 * 12 *', DT(2018, 7, 30, 16, 54, 0)) == datetime.datetime(2018, 12, 1, 0, 10)

def test_random_08():
    assert cron_next('59 1,13 1-7 */3 */2', DT(2017, 12, 23, 4, 13, 30)) == datetime.datetime(2018, 1, 1, 1, 59)

def test_random_09():
    assert cron_next('0 */6 15 12 */2', DT(2029, 7, 24, 8, 33, 0)) == datetime.datetime(2029, 12, 1, 0, 0)

def test_random_10():
    assert cron_next('0-59/7 */6 * 12 7', DT(2017, 3, 24, 4, 26, 0)) == datetime.datetime(2017, 12, 3, 0, 0)

def test_random_11():
    assert cron_next('59 9-17 29 * 1-5', DT(2017, 1, 1, 19, 4, 0)) == datetime.datetime(2017, 1, 2, 9, 59)

def test_random_12():
    assert cron_next('59 12 */10 4,6,9,11 */2', DT(2018, 12, 31, 13, 50, 0)) == datetime.datetime(2019, 4, 1, 12, 59)

def test_random_13():
    assert cron_next('0-59/7 12 1 * 5', DT(2002, 5, 17, 1, 25, 59)) == datetime.datetime(2002, 5, 17, 12, 0)

def test_random_14():
    assert cron_next('0 9-17 */10 * *', DT(2005, 8, 4, 1, 18, 0)) == datetime.datetime(2005, 8, 11, 9, 0)

def test_random_15():
    assert cron_next('0 1,13 15 12 1-5', DT(2019, 5, 26, 18, 49, 0)) == datetime.datetime(2019, 12, 2, 1, 0)

def test_random_16():
    assert cron_next('30 23 1-7 1-6 */2', DT(2019, 2, 16, 0, 48, 59)) == datetime.datetime(2019, 2, 16, 23, 30)

def test_random_17():
    assert cron_next('5,35 */6 * */3 *', DT(2027, 3, 7, 1, 43, 30)) == datetime.datetime(2027, 4, 1, 0, 5)

def test_random_18():
    assert cron_next('*/15 12 13 2 1-5', DT(2001, 9, 1, 18, 51, 30)) == datetime.datetime(2002, 2, 1, 12, 0)

def test_random_19():
    assert cron_next('30 * 1 12 */2', DT(2003, 10, 2, 9, 44, 59)) == datetime.datetime(2003, 12, 1, 0, 30)

def test_random_20():
    assert cron_next('*/15 23 29 4,6,9,11 1-5', DT(2010, 11, 23, 3, 28, 0)) == datetime.datetime(2010, 11, 23, 23, 0)

def test_random_21():
    assert cron_next('0 * * */3 0', DT(2021, 1, 9, 19, 19, 0)) == datetime.datetime(2021, 1, 10, 0, 0)

def test_random_22():
    assert cron_next('5,35 * 1-7 12 0', DT(2022, 6, 1, 20, 50, 30)) == datetime.datetime(2022, 12, 1, 0, 5)

def test_random_23():
    assert cron_next('0 23 * 2 */2', DT(2010, 11, 20, 14, 41, 59)) == datetime.datetime(2011, 2, 1, 23, 0)

def test_random_24():
    assert cron_next('10-20/5 0 * * */2', DT(2013, 3, 19, 8, 21, 0)) == datetime.datetime(2013, 3, 21, 0, 10)

def test_random_25():
    assert cron_next('0 0 * * *', DT(2007, 2, 23, 20, 10, 59)) == datetime.datetime(2007, 2, 24, 0, 0)

def test_random_26():
    assert cron_next('10-20/5 23 1 2 7', DT(2014, 10, 27, 13, 26, 0)) == datetime.datetime(2015, 2, 1, 23, 10)

def test_random_27():
    assert cron_next('5,35 */6 * 2 5', DT(2001, 3, 2, 1, 24, 0)) == datetime.datetime(2002, 2, 1, 0, 5)

def test_random_28():
    assert cron_next('* 0 31 * *', DT(2001, 12, 17, 20, 0, 0)) == datetime.datetime(2001, 12, 31, 0, 0)

def test_random_29():
    assert cron_next('10-20/5 12 29 * *', DT(2003, 2, 9, 0, 22, 0)) == datetime.datetime(2003, 3, 29, 12, 10)

def test_random_30():
    assert cron_next('59 */6 31 2 5', DT(2018, 3, 2, 14, 49, 0)) == datetime.datetime(2019, 2, 1, 0, 59)

def test_large_leap_day_eight_years_away():
    assert run_limited('cron_next("0 0 29 2 *", DT(2096, 3, 1))', 2) == 'datetime.datetime(2104, 2, 29, 0, 0)'

def test_large_leap_day_after_2100():
    assert run_limited('cron_next("30 12 29 2 *", DT(2100, 1, 1))', 2) == 'datetime.datetime(2104, 2, 29, 12, 30)'

def test_large_never_february_30():
    assert run_limited('cron_next("0 0 30 2 *", DT(2026, 1, 1))', 2) == 'raises ValueError'

def test_large_never_31_in_short_months():
    assert run_limited('cron_next("0 0 31 4,6,9,11 *", DT(2026, 1, 1))', 2) == 'raises ValueError'

def test_large_search_stops_at_9999():
    assert run_limited('cron_next("0 0 29 2 *", DT(9996, 3, 1))', 2) == 'raises ValueError'

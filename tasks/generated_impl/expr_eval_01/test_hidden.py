import pytest
from expr_eval import expr_eval

CASE_TIME_LIMIT = 3
PRELUDE = 'from expr_eval import expr_eval\n'

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

def test_edge_val_not_a_str():
    with pytest.raises(TypeError):
        expr_eval(12)

def test_edge_val_syntax_checked_before_division():
    with pytest.raises(ValueError):
        expr_eval("1 // 0 +")

def test_edge_val_spaced_double_star():
    with pytest.raises(ValueError):
        expr_eval("2 * * 3")

def test_edge_logic_zero():
    assert expr_eval("0") == 0

def test_edge_logic_leading_zeros():
    assert expr_eval("007 + 0") == 7

def test_edge_logic_surrounding_whitespace():
    assert expr_eval("  12  ") == 12

def test_edge_logic_tabs_and_newlines():
    assert expr_eval("1\t+\n2") == 3

def test_edge_logic_subtraction_left_assoc():
    assert expr_eval("10 - 2 - 3") == 5

def test_edge_logic_floor_division_left_assoc():
    assert expr_eval("100 // 10 // 3") == 3

def test_edge_logic_mixed_term_left_assoc():
    assert expr_eval("6 // 4 * 4") == 4

def test_edge_logic_modulo_after_product():
    assert expr_eval("2 * 3 % 4") == 2

def test_edge_logic_power_right_assoc():
    assert expr_eval("2 ** 3 ** 2") == 512

def test_edge_logic_parenthesized_negative_base():
    assert expr_eval("(-2) ** 2") == 4

def test_edge_logic_unary_minus_power_product():
    assert expr_eval("-3 ** 2 * 2") == -18

def test_edge_logic_unary_minus_before_floor_division():
    assert expr_eval("-7 // 2") == -4

def test_edge_logic_modulo_negative_divisor():
    assert expr_eval("7 % -2") == -1

def test_edge_logic_modulo_negative_dividend():
    assert expr_eval("-7 % 2") == 1

def test_edge_logic_double_unary():
    assert expr_eval("--2") == 2

def test_edge_logic_mixed_unary():
    assert expr_eval("+-+2") == -2

def test_edge_logic_minus_negative():
    assert expr_eval("1 - -2") == 3

def test_edge_logic_product_with_unary():
    assert expr_eval("2*-3") == -6

def test_edge_logic_nested_unary_parentheses():
    assert expr_eval("-(-(3))") == 3

def test_edge_logic_exponent_double_unary():
    assert expr_eval("2 ** - - 2") == 4

def test_edge_logic_exponent_negative_zero():
    assert expr_eval("2 ** -0") == 1

def test_edge_logic_zero_to_zero():
    assert expr_eval("0 ** 0") == 1

def test_edge_logic_big_integer():
    assert expr_eval("2 ** 100 - 1") == 1267650600228229401496703205375

def test_edge_logic_negative_exponent():
    with pytest.raises(ValueError):
        expr_eval("2 ** -1")

def test_edge_logic_zero_negative_exponent():
    with pytest.raises(ValueError):
        expr_eval("0 ** -1")

def test_edge_logic_negative_exponent_from_tower():
    with pytest.raises(ValueError):
        expr_eval("2 ** -2 ** 2")

def test_edge_logic_modulo_by_zero():
    with pytest.raises(ZeroDivisionError):
        expr_eval("5 % 0")

def test_edge_logic_division_by_computed_zero():
    with pytest.raises(ZeroDivisionError):
        expr_eval("1 // (2 - 2)")

def test_edge_logic_left_error_first_value():
    with pytest.raises(ValueError):
        expr_eval("2 ** -1 + 1 // 0")

def test_edge_logic_left_error_first_division():
    with pytest.raises(ZeroDivisionError):
        expr_eval("1 // 0 + 2 ** -1")

def test_edge_logic_base_error_before_exponent():
    with pytest.raises(ZeroDivisionError):
        expr_eval("(1 // 0) ** -1")

def test_edge_logic_empty_parentheses():
    with pytest.raises(ValueError):
        expr_eval("()")

def test_edge_logic_adjacent_numbers():
    with pytest.raises(ValueError):
        expr_eval("1 2")

def test_edge_logic_single_slash():
    with pytest.raises(ValueError):
        expr_eval("4 / 2")

def test_edge_logic_unclosed_parenthesis():
    with pytest.raises(ValueError):
        expr_eval("(1 + 2")

def test_edge_logic_extra_close_parenthesis():
    with pytest.raises(ValueError):
        expr_eval("1 + 2)")

def test_edge_logic_empty_string():
    with pytest.raises(ValueError):
        expr_eval("   ")

def test_random_01():
    assert expr_eval('((1) * (7))--11* (-12**(0) - ((2)-(--2)))') == -4

def test_random_02():
    assert expr_eval('((+2) * +3 // ((--3)- (2))) % (((4) - 3)%--5) % (--1) +8% 2 % (--11)') == 0

def test_random_03():
    assert expr_eval('(2+ -0)** (3)') == 8

def test_random_04():
    assert expr_eval('(--11) *-0 * (1)+ ((--10)+(+10))') == 20

def test_random_05():
    assert expr_eval('3 * 2// -5- 7') == -9

def test_random_06():
    assert expr_eval('(--10)// (8)') == 1

def test_random_07():
    assert expr_eval('(--1)- 8') == -7

def test_random_08():
    assert expr_eval('11') == 11

def test_random_09():
    assert expr_eval('(-3) *7 +-7 // 1 *11 - +11 -(--3)') == -112

def test_random_10():
    assert expr_eval('((3 - (5))- ((+9)*4))*(+8 -+6) % 9 * (8)') == 40

def test_random_11():
    assert expr_eval('((0** (0)) *(2)%11 // 8)*((7 **1) -(7)) +(-0)') == 0

def test_random_12():
    assert expr_eval('12 + (8)% --11-0') == 20

def test_random_13():
    assert expr_eval('((9) -(((6)+9) + (5))) - ((-6) -1) +(4) //((+9) + 1)') == -4

def test_random_14():
    assert expr_eval('(9) //(+1)* (+7)') == 63

def test_random_15():
    assert expr_eval('5+(5)') == 10

def test_random_16():
    assert expr_eval('--12') == 12

def test_random_17():
    assert expr_eval('(--11) %(9)') == 2

def test_random_18():
    assert expr_eval('3+(10)') == 13

def test_random_19():
    assert expr_eval('+6') == 6

def test_random_20():
    assert expr_eval('+4') == 4

def test_random_21():
    assert expr_eval('-6+((6 +-8) - 3 // (-10))') == -7

def test_random_22():
    assert expr_eval('--0- -12') == 12

def test_random_23():
    assert expr_eval('+7 + 5* (2 //-5)** 2') == 12

def test_random_24():
    assert expr_eval('(2) +--3') == 5

def test_random_25():
    assert expr_eval('(--12)+ +4*(11* 8) *(-12) *--12**3') == -7299060

def test_random_26():
    assert expr_eval('(-0+(6))-1 % +3 %1 //(--9) *(3) + 12') == 18

def test_random_27():
    assert expr_eval('6') == 6

def test_random_28():
    assert expr_eval('(+1)+3') == 4

def test_random_29():
    assert expr_eval('(-6) ** (-0)') == 1

def test_random_30():
    assert expr_eval('--12') == 12

def test_large_deep_parentheses():
    assert run_limited('expr_eval("(" * 5000 + "1" + ")" * 5000)', 5) == '1'

def test_large_deep_unary_and_parentheses():
    assert run_limited('expr_eval("(-" * 5000 + "2" + ")" * 5000)', 5) == '2'

def test_large_long_power_tower():
    assert run_limited('expr_eval("1 ** " * 5000 + "2")', 5) == '1'

def test_large_long_sum():
    assert run_limited('expr_eval("1+" * 99999 + "1")', 5) == '100000'

def test_large_long_mixed():
    assert run_limited('expr_eval(" - ".join(f"{i} * {i % 7} // 3 + {i} % 5" for i in range(20000)))', 5) == '-199952857'

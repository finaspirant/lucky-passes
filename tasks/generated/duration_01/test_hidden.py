import pytest
from duration import format_duration, parse_duration

def test_parse_zero():
    assert parse_duration('0s') == 0

def test_parse_outer_whitespace():
    assert parse_duration('  2h  ') == 7200

def test_parse_tab_between():
    assert parse_duration('1h\t30m') == 5400

def test_parse_leading_zero():
    assert parse_duration('05m') == 300

def test_parse_large_component():
    assert parse_duration('90m') == 5400

def test_parse_all_units():
    assert parse_duration('1d2h3m4s') == 93784

def test_parse_empty():
    with pytest.raises(ValueError):
        parse_duration('')

def test_parse_blank():
    with pytest.raises(ValueError):
        parse_duration('   ')

def test_parse_uppercase():
    with pytest.raises(ValueError):
        parse_duration('1H')

def test_parse_repeat():
    with pytest.raises(ValueError):
        parse_duration('1m2m')

def test_parse_out_of_order_tail():
    with pytest.raises(ValueError):
        parse_duration('1s1m')

def test_parse_space_in_component():
    with pytest.raises(ValueError):
        parse_duration('1 h')

def test_parse_no_unit():
    with pytest.raises(ValueError):
        parse_duration('90')

def test_parse_trailing_number():
    with pytest.raises(ValueError):
        parse_duration('1h30')

def test_parse_no_number():
    with pytest.raises(ValueError):
        parse_duration('h')

def test_parse_unit_first():
    with pytest.raises(ValueError):
        parse_duration('s30')

def test_parse_negative():
    with pytest.raises(ValueError):
        parse_duration('-5s')

def test_parse_decimal():
    with pytest.raises(ValueError):
        parse_duration('1.5h')

def test_parse_not_str():
    with pytest.raises(TypeError):
        parse_duration(60)

def test_format_zero():
    assert format_duration(0) == '0s'

def test_format_one():
    assert format_duration(1) == '1s'

def test_format_59():
    assert format_duration(59) == '59s'

def test_format_60():
    assert format_duration(60) == '1m'

def test_format_hour():
    assert format_duration(3600) == '1h'

def test_format_two_days():
    assert format_duration(172800) == '2d'

def test_format_all_units():
    assert format_duration(90061) == '1d1h1m1s'

def test_format_just_under_day():
    assert format_duration(86399) == '23h59m59s'

def test_format_negative():
    with pytest.raises(ValueError):
        format_duration(-1)

def test_format_bool():
    with pytest.raises(TypeError):
        format_duration(True)

def test_format_float():
    with pytest.raises(TypeError):
        format_duration(1.0)

def test_golden_01():
    assert format_duration(201979) == '2d8h6m19s'

def test_golden_02():
    assert format_duration(397386) == '4d14h23m6s'

def test_golden_03():
    assert format_duration(220500) == '2d13h15m'

def test_golden_04():
    assert format_duration(21225) == '5h53m45s'

def test_golden_05():
    assert format_duration(135746) == '1d13h42m26s'

def test_golden_06():
    assert parse_duration('45d74h27m64s') == 4156084

def test_golden_07():
    assert parse_duration('68d90h77s') == 6199277

def test_golden_08():
    assert parse_duration('87d42m60s') == 7519380

def test_golden_09():
    assert parse_duration('70d 61h 56s') == 6267656

def test_golden_10():
    assert parse_duration('92d51s') == 7948851

def test_golden_11():
    with pytest.raises(ValueError):
        parse_duration('72s24m8h90d')

def test_golden_12():
    with pytest.raises(ValueError):
        parse_duration('11m57h')

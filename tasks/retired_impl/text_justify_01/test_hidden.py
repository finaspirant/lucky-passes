import pytest
from text_justify import text_justify

CASE_TIME_LIMIT = 3
PRELUDE = 'from text_justify import text_justify\n'

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

def test_edge_val_width_zero():
    with pytest.raises(ValueError):
        text_justify(["a"], 0)

def test_edge_val_width_negative():
    with pytest.raises(ValueError):
        text_justify([], -3)

def test_edge_val_width_bool():
    with pytest.raises(TypeError):
        text_justify(["a"], True)

def test_edge_val_width_float():
    with pytest.raises(TypeError):
        text_justify(["a"], 2.0)

def test_edge_val_words_tuple():
    with pytest.raises(TypeError):
        text_justify(("a",), 3)

def test_edge_val_word_not_str():
    with pytest.raises(TypeError):
        text_justify([1], 3)

def test_edge_val_word_empty():
    with pytest.raises(ValueError):
        text_justify(["a", ""], 3)

def test_edge_val_word_with_space():
    with pytest.raises(ValueError):
        text_justify(["a b"], 5)

def test_edge_val_word_with_tab():
    with pytest.raises(ValueError):
        text_justify(["a\tb"], 5)

def test_edge_val_width_checked_before_words():
    with pytest.raises(ValueError):
        text_justify([1], 0)

def test_edge_val_type_checked_before_length():
    with pytest.raises(ValueError):
        text_justify(["abcdef", 2], 3)

def test_edge_logic_exact_fit_last_line():
    assert text_justify(["ab", "cd"], 5) == ['ab cd']

def test_edge_logic_width_one():
    assert text_justify(["a", "b"], 1) == ['a', 'b']

def test_edge_logic_word_equals_width():
    assert text_justify(["abc"], 3) == ['abc']

def test_edge_logic_single_word_middle_lines():
    assert text_justify(["abcd", "efghi", "j"], 6) == ['abcd  ', 'efghi ', 'j     ']

def test_edge_logic_extra_spaces_leftmost():
    assert text_justify(["a", "b", "c", "d", "eeeeeeeee"], 11) == ['a   b  c  d', 'eeeeeeeee  ']

def test_edge_logic_two_gaps_remainder():
    assert text_justify(["x", "y", "z", "longword"], 8) == ['x   y  z', 'longword']

def test_edge_logic_last_line_single_spaces():
    assert text_justify(["aaaa", "b", "c"], 6) == ['aaaa b', 'c     ']

def test_edge_logic_last_line_several_words():
    assert text_justify(["abcdefg", "a", "b", "c"], 7) == ['abcdefg', 'a b c  ']

def test_edge_logic_unicode_lengths():
    assert text_justify(["é", "ü", "日本"], 4) == ['é  ü', '日本  ']

def test_edge_logic_punctuation_is_text():
    assert text_justify(["a-b", "c,d"], 7) == ['a-b c,d']

def test_random_01():
    assert text_justify(['ca', 'zzc', 'yz', 'xcbbyz', 'zb', 'zycyyz', 'xczy', 'xbz', 'xbzc', 'cbbayx', 'aazy', 'azyxb', 'xzzb', 'zcyaabb', 'ybcy', 'zbbcb', 'by', 'y', 'yxazby', 'bbcaz'], 7) == ['ca  zzc', 'yz     ', 'xcbbyz ', 'zb     ', 'zycyyz ', 'xczy   ', 'xbz    ', 'xbzc   ', 'cbbayx ', 'aazy   ', 'azyxb  ', 'xzzb   ', 'zcyaabb', 'ybcy   ', 'zbbcb  ', 'by    y', 'yxazby ', 'bbcaz  ']

def test_random_02():
    assert text_justify(['yxz', 'cbaaya', 'xa', 'cczbayy'], 24) == ['yxz cbaaya xa cczbayy   ']

def test_random_03():
    assert text_justify(['zyxx', 'yxazya', 'axzabz', 'xbayxba', 'yabacyx', 'czay', 'bccczzc', 'bxzyyb', 'zc', 'bczyac', 'x', 'xazbba', 'xcabc', 'zcyc'], 14) == ['zyxx    yxazya', 'axzabz xbayxba', 'yabacyx   czay', 'bccczzc bxzyyb', 'zc   bczyac  x', 'xazbba   xcabc', 'zcyc          ']

def test_random_04():
    assert text_justify(['b', 'zc', 'xzc', 'bzaccxz', 'aycc', 'cxz', 'zzcy', 'ya', 'yyxzzy', 'xzcz', 'aacx', 'ccxyz'], 15) == ['b     zc    xzc', 'bzaccxz    aycc', 'cxz   zzcy   ya', 'yyxzzy     xzcz', 'aacx ccxyz     ']

def test_random_05():
    assert text_justify(['cyc', 'zxcay', 'bz', 'ybabbcb', 'cya', 'abcaca', 'x', 'xxybz', 'xbbaabx', 'bzbzzac', 'ya', 'zacazcy', 'xyycy', 'abbbca', 'b', 'z'], 8) == ['cyc     ', 'zxcay bz', 'ybabbcb ', 'cya     ', 'abcaca x', 'xxybz   ', 'xbbaabx ', 'bzbzzac ', 'ya      ', 'zacazcy ', 'xyycy   ', 'abbbca b', 'z       ']

def test_random_06():
    assert text_justify(['bbyacz', 'a', 'ycyc', 'bcyayb', 'c', 'yyxaa', 'zx', 'xyza'], 24) == ['bbyacz  a  ycyc bcyayb c', 'yyxaa zx xyza           ']

def test_random_07():
    assert text_justify(['azx', 'xxz', 'bbaa', 'z', 'aazbz', 'abzyya', 'axzx', 'ybzzy', 'aycyz', 'bbcy', 'bcacaab', 'cbycz', 'aybaczz', 'yc', 'c', 'y', 'ybx', 'czbcbx', 'aabc', 'ya', 'ybbyc', 'cxxyczc', 'yc', 'byyyayx'], 13) == ['azx  xxz bbaa', 'z       aazbz', 'abzyya   axzx', 'ybzzy   aycyz', 'bbcy  bcacaab', 'cbycz aybaczz', 'yc  c  y  ybx', 'czbcbx   aabc', 'ya      ybbyc', 'cxxyczc    yc', 'byyyayx      ']

def test_random_08():
    assert text_justify(['cyac', 'zzy', 'cczcxb', 'xybzb', 'cbyayc', 'a', 'bcxza', 'xayxxza', 'xcy', 'b', 'xzy', 'acyzzax', 'xxazxac', 'yyc', 'b', 'yab', 'ybbay', 'yxy', 'azycz', 'a', 'xzbca'], 11) == ['cyac    zzy', 'cczcxb     ', 'xybzb      ', 'cbyayc    a', 'bcxza      ', 'xayxxza xcy', 'b       xzy', 'acyzzax    ', 'xxazxac yyc', 'b yab ybbay', 'yxy azycz a', 'xzbca      ']

def test_random_09():
    assert text_justify(['x', 'z', 'bxcyaz', 'bax', 'zyaax', 'ayyczbb', 'z', 'yab', 'acby', 'cb', 'zcbxz', 'bac', 'cc', 'cxay'], 17) == ['x  z  bxcyaz  bax', 'zyaax  ayyczbb  z', 'yab acby cb zcbxz', 'bac cc cxay      ']

def test_random_10():
    assert text_justify(['caxabba', 'bczcab'], 14) == ['caxabba bczcab']

def test_random_11():
    assert text_justify([], 17) == []

def test_random_12():
    assert text_justify(['xb', 'azc', 'ab', 'az', 'zbzcaya', 'bbz', 'zzxc', 'ba', 'cxcxxbb', 'axxbcc', 'y', 'abzbxc', 'cyz', 'ybxxzcz', 'xzabay', 'xzbcca', 'z', 'yczz', 'czz', 'zcyacbz'], 20) == ['xb azc ab az zbzcaya', 'bbz  zzxc ba cxcxxbb', 'axxbcc  y abzbxc cyz', 'ybxxzcz       xzabay', 'xzbcca  z  yczz  czz', 'zcyacbz             ']

def test_random_13():
    assert text_justify(['yazxx', 'cx', 'baa', 'xaxb', 'z', 'zzx', 'abxc', 'xyc'], 12) == ['yazxx cx baa', 'xaxb  z  zzx', 'abxc xyc    ']

def test_random_14():
    assert text_justify(['bzc', 'acxzy', 'z', 'aabx', 'zzxyyb', 'abzya', 'xzyya', 'yz', 'bcxcbb', 'yycy', 'a'], 7) == ['bzc    ', 'acxzy z', 'aabx   ', 'zzxyyb ', 'abzya  ', 'xzyya  ', 'yz     ', 'bcxcbb ', 'yycy a ']

def test_random_15():
    assert text_justify(['y', 'xyxbxz', 'bxaaxcc', 'x', 'b', 'ayaabz', 'b', 'xcy', 'cxyxc', 'cx', 'cx', 'cccz', 'cax', 'zxxy', 'zccx', 'xc', 'zaxzx', 'cayy', 'czccayx', 'xay'], 11) == ['y    xyxbxz', 'bxaaxcc x b', 'ayaabz    b', 'xcy   cxyxc', 'cx  cx cccz', 'cax    zxxy', 'zccx     xc', 'zaxzx  cayy', 'czccayx xay']

def test_random_16():
    assert text_justify(['cxbbcxb', 'cz', 'bcycy', 'xxyzcz', 'cz', 'cxcczac', 'a', 'bbxy', 'za', 'cyazz', 'aazcz', 'bzbx', 'axcbxz', 'abycz', 'a', 'xza'], 13) == ['cxbbcxb    cz', 'bcycy  xxyzcz', 'cz  cxcczac a', 'bbxy za cyazz', 'aazcz    bzbx', 'axcbxz  abycz', 'a xza        ']

def test_random_17():
    assert text_justify(['xxycza', 'xazxb', 'axyxc', 'ayac', 'czbaz', 'bxxzcyb', 'azazz', 'bc', 'yzaczc', 'zz', 'bczacay', 'zxzc', 'caxza', 'zay', 'xbyczb', 'bya', 'bzccycb', 'xac', 'bzzxz', 'z', 'c', 'xy', 'abccyc'], 22) == ['xxycza   xazxb   axyxc', 'ayac   czbaz   bxxzcyb', 'azazz   bc  yzaczc  zz', 'bczacay zxzc caxza zay', 'xbyczb bya bzccycb xac', 'bzzxz z c xy abccyc   ']

def test_random_18():
    assert text_justify(['ca', 'ayx', 'zxbzy', 'xzzcz', 'caab', 'cc', 'cyby', 'zabzxb', 'zyyc', 'cacbxx', 'czyx', 'axczzxx', 'bx', 'ybcxzy', 'cybbac', 'cbbya', 'yaayxca', 'byxaaa', 'zy', 'yaxzabb', 'acyba', 'ya'], 8) == ['ca   ayx', 'zxbzy   ', 'xzzcz   ', 'caab  cc', 'cyby    ', 'zabzxb  ', 'zyyc    ', 'cacbxx  ', 'czyx    ', 'axczzxx ', 'bx      ', 'ybcxzy  ', 'cybbac  ', 'cbbya   ', 'yaayxca ', 'byxaaa  ', 'zy      ', 'yaxzabb ', 'acyba ya']

def test_random_19():
    assert text_justify(['cbc', 'b', 'b', 'cbzx', 'xbbzbba', 'cb', 'aaaby', 'bcaa', 'czczy', 'c', 'x', 'z', 'xz', 'caaa', 'xxb', 'cc', 'ay', 'bcyzb', 'accbb', 'zczbyy', 'aba'], 13) == ['cbc  b b cbzx', 'xbbzbba    cb', 'aaaby    bcaa', 'czczy  c  x z', 'xz  caaa  xxb', 'cc  ay  bcyzb', 'accbb  zczbyy', 'aba          ']

def test_random_20():
    assert text_justify(['xyzy', 'zxazzx', 'c', 'bcb', 'zczaz', 'yzb', 'ycbaazz', 'axyx', 'bc', 'cxcaxx', 'axzaay', 'bzya', 'axcz', 'x', 'ayy', 'zbcc', 'b', 'zzzza', 'b', 'c'], 13) == ['xyzy zxazzx c', 'bcb zczaz yzb', 'ycbaazz  axyx', 'bc     cxcaxx', 'axzaay   bzya', 'axcz   x  ayy', 'zbcc  b zzzza', 'b c          ']


import pytest
from normalize_tags import normalize_tags

CASE_TIME_LIMIT = 3
PRELUDE = 'from normalize_tags import normalize_tags\n'

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

def test_edge_val_element_not_str():
    with pytest.raises(TypeError):
        normalize_tags(["a", 1])

def test_edge_val_element_none():
    with pytest.raises(TypeError):
        normalize_tags([None])

def test_edge_logic_empty():
    assert normalize_tags([]) == []

def test_edge_logic_all_blank():
    assert normalize_tags(["", " ", "\t\n"]) == []

def test_edge_logic_inner_space_kept():
    assert normalize_tags(["  machine  learning "]) == ['machine  learning']

def test_edge_logic_digits_before_letters():
    assert normalize_tags(["b2", "10", "B1"]) == ['10', 'B1', 'b2']

def test_edge_logic_unicode_whitespace_trimmed():
    assert normalize_tags(["\u00a0tag\u2003", "TAG"]) == ['tag']

def test_edge_logic_returns_new_list():
    assert (lambda x: (normalize_tags(x) is not x, x))(['a']) == (True, ['a'])

def test_edge_logic_sharp_s_duplicate():
    assert normalize_tags(["Straße", "STRASSE"]) == ['Straße']

def test_edge_logic_sharp_s_duplicate_reversed():
    assert normalize_tags(["strasse", "Straße"]) == ['strasse']

def test_edge_logic_sharp_s_sort():
    assert normalize_tags(["strasz", "straße"]) == ['straße', 'strasz']

def test_edge_logic_ligature_duplicate():
    assert normalize_tags(["\ufb00", "FF", "ff"]) == ['ﬀ']

def test_edge_logic_long_s_duplicate():
    assert normalize_tags(["\u017fun", "SUN"]) == ['ſun']

def test_edge_logic_ligature_sort():
    assert normalize_tags(["fz", "\ufb01x"]) == ['ﬁx', 'fz']

def test_random_01():
    assert normalize_tags(['db ']) == ['db']

def test_random_02():
    assert normalize_tags(['  TesT', ' rust\n', 'api\n', '\tdb', ' PYthon ', 'Test']) == ['api', 'db', 'PYthon', 'rust', 'TesT']

def test_random_03():
    assert normalize_tags(['\truSt\n']) == ['ruSt']

def test_random_04():
    assert normalize_tags(['  ruSt\n', '  pytHon', ' db\n', ' Test\n', '  cLoUd', '\tpytHon ', '  teSt ', 'api\n', '\tml ']) == ['api', 'cLoUd', 'db', 'ml', 'pytHon', 'ruSt', 'Test']

def test_random_05():
    assert normalize_tags(['aPi', 'GO', 'deVoPS ', ' aPi', '  db']) == ['aPi', 'db', 'deVoPS', 'GO']

def test_random_06():
    assert normalize_tags(['\tTest', ' teST', ' DAta ', 'go\n', 'data\n', '  Db', '\tPyThon\n', 'ui\n']) == ['DAta', 'Db', 'go', 'PyThon', 'Test', 'ui']

def test_random_07():
    assert normalize_tags(['\tPytHON ', 'Ui\n', 'ruSt', '']) == ['PytHON', 'ruSt', 'Ui']

def test_random_08():
    assert normalize_tags(['\tMl', '\tdevopS\n', ' TesT\n', ' dB\n', '\tpythON\n', 'pYthOn\n']) == ['dB', 'devopS', 'Ml', 'pythON', 'TesT']

def test_random_09():
    assert normalize_tags([' dEVoPs\n', '  Db ', '\tuI ', '  go\n', 'wEb ', '  Web', 'Ml\n', '\tpythOn ']) == ['Db', 'dEVoPs', 'go', 'Ml', 'pythOn', 'uI', 'wEb']

def test_random_10():
    assert normalize_tags([' cLoud\n', 'pyThOn ', 'ui\n']) == ['cLoud', 'pyThOn', 'ui']

def test_random_11():
    assert normalize_tags(['  devops\n']) == ['devops']

def test_random_12():
    assert normalize_tags(['\trust\n', ' python ', '  PyTHon ', 'DB\n', ' PyTHoN ', ' tEST\n', '  mL', 'ui ', '\tclOud\n', '\tDb\n']) == ['clOud', 'DB', 'mL', 'python', 'rust', 'tEST', 'ui']

def test_random_13():
    assert normalize_tags(['\tweB', '  TesT ', ' clOud', '\tapi', ' Devops ', 'dB', 'api ', 'go\n', '\tclouD\n', '  gO ']) == ['api', 'clOud', 'dB', 'Devops', 'go', 'TesT', 'weB']

def test_random_14():
    assert normalize_tags(['\tclOud ', ' db', ' PyThON', 'ui\n', 'CLoUd\n', '\tcloud', ' DB', '\tdEVops\n']) == ['clOud', 'db', 'dEVops', 'PyThON', 'ui']

def test_random_15():
    assert normalize_tags(['\tWeb', '  data ', '  go', '  Api ', '  cloUd ', '\tml ', 'ML\n', '\truST', 'pythoN\n']) == ['Api', 'cloUd', 'data', 'go', 'ml', 'pythoN', 'ruST', 'Web']

def test_random_16():
    assert normalize_tags(['rUSt\n', '\tdb ', '\tweB\n', '  ml\n', 'pyThon\n', '\tdevops ', '  gO\n', '\twEb\n', 'mL\n']) == ['db', 'devops', 'gO', 'ml', 'pyThon', 'rUSt', 'weB']

def test_random_17():
    assert normalize_tags([' clouD ', '\tteSt\n', '\tpyThon ', '\tdevoPs ', '\tDb ', '\tpython ', 'go ', ' db\n', ' web\n', '  GO ', '   ']) == ['clouD', 'Db', 'devoPs', 'go', 'pyThon', 'teSt', 'web']

def test_random_18():
    assert normalize_tags(['\tdevopS\n', ' Devops\n', '  dATa\n', 'api ']) == ['api', 'dATa', 'devopS']

def test_random_19():
    assert normalize_tags(['\taPi ', ' web ', ' ml\n', '   ']) == ['aPi', 'ml', 'web']

def test_random_20():
    assert normalize_tags(['\twEB ', 'mL ', 'clouD\n', ' ui', ' api', '  TeSt ', '  rusT\n', '   ']) == ['api', 'clouD', 'mL', 'rusT', 'TeSt', 'ui', 'wEB']

def test_random_21():
    assert normalize_tags(['\tRUst ', '  Db ', ' uI ', '  mL ']) == ['Db', 'mL', 'RUst', 'uI']

def test_random_22():
    assert normalize_tags(['gO\n', '\tpyThoN', '\ttest ', ' Ml', '\tPytHOn\n', '  ml ', 'Ui\n']) == ['gO', 'Ml', 'pyThoN', 'test', 'Ui']

def test_random_23():
    assert normalize_tags(['\tcloud ']) == ['cloud']

def test_random_24():
    assert normalize_tags(['\tCLOud ', ' pyTHoN\n', 'RuSt']) == ['CLOud', 'pyTHoN', 'RuSt']

def test_random_25():
    assert normalize_tags(['\tpython', '\tMl\n', 'clOud\n', ' go ', 'apI ', ' ml', '\tdAta', '   ']) == ['apI', 'clOud', 'dAta', 'go', 'Ml', 'python']

def test_random_26():
    assert normalize_tags(['\tweB\n', ' datA', ' pyTHon', 'Ml ']) == ['datA', 'Ml', 'pyTHon', 'weB']

def test_random_27():
    assert normalize_tags([' cloUd', '  Ui ', '\tui', ' WEB\n', ' weB\n', '  ui ', '  ml ', '\tweB ', '\tdatA', '\tdAta', '']) == ['cloUd', 'datA', 'ml', 'Ui', 'WEB']

def test_random_28():
    assert normalize_tags(['pytHOn\n', '\tpYthon', 'CLoud\n', '\tUI\n', ' weB ', '']) == ['CLoud', 'pytHOn', 'UI', 'weB']

def test_random_29():
    assert normalize_tags([]) == []

def test_random_30():
    assert normalize_tags(['\tdb ', 'dEVoPs ', ' deVoPs\n', '\tGO\n', '\ttest ', 'Devops ', 'web ', 'db', '\tUi ', 'ml\n']) == ['db', 'dEVoPs', 'GO', 'ml', 'test', 'Ui', 'web']


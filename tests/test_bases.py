import ast
import importlib
import random
from pathlib import Path

import pytest

from tasks.gen.render import Raises, render_tests
from tasks.gen.runner import run_tests

BASE_DIR = Path(__file__).parent.parent / "tasks" / "_base"
BASES = ["duration", "ring_buffer", "intervals"]


def load(name):
    cases = importlib.import_module(f"tasks._base.{name}.cases")
    source = (BASE_DIR / name / f"{name}.py").read_text()
    return cases, source


@pytest.mark.parametrize("name", BASES)
def test_original_passes_every_hand_written_case(name, tmp_path):
    cases, source = load(name)
    all_cases = cases.VISIBLE_POOL + cases.HIDDEN_EDGE
    test_file = tmp_path / "test_all.py"
    test_file.write_text(render_tests(cases.PRELUDE, all_cases))
    result = run_tests(name, source, test_file)
    assert result["error"] is None
    assert result["failing"] == []
    assert result["passed"] == len(all_cases)


@pytest.mark.parametrize("name", BASES)
def test_case_pools_are_well_formed(name):
    cases, source = load(name)
    assert 8 <= len(cases.VISIBLE_POOL) <= 10
    names = [case[0] for case in cases.VISIBLE_POOL + cases.HIDDEN_EDGE]
    assert len(names) == len(set(names))
    assert ast.get_docstring(ast.parse(source))


@pytest.mark.parametrize("name", BASES)
def test_golden_exprs_are_seeded(name):
    cases, _ = load(name)
    first = cases.golden_exprs(random.Random(7))
    assert first == cases.golden_exprs(random.Random(7))
    assert first != cases.golden_exprs(random.Random(8))
    assert len(first) >= 10


def test_raises_checks_type_not_message(tmp_path):
    test_file = tmp_path / "test_r.py"
    test_file.write_text(render_tests("from m import f\n", [("r", "f()", Raises("ValueError"))]))
    other_message = "def f():\n    raise ValueError('any message at all')\n"
    wrong_type = "def f():\n    raise TypeError('x')\n"
    assert run_tests("m", other_message, test_file)["passed"] == 1
    assert run_tests("m", wrong_type, test_file)["failed"] == 1

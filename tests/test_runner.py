import json
import subprocess

from tasks.gen import runner
from tasks.gen.runner import flag_suspicious, run_hidden, run_tests, run_visible

TESTS = """\
from calc import double

def test_two():
    assert double(2) == 4

def test_zero():
    assert double(0) == 0
"""


def make_task(tmp_path):
    (tmp_path / "task.json").write_text(json.dumps({"module": "calc"}))
    (tmp_path / "test_visible.py").write_text(TESTS)
    (tmp_path / "test_hidden.py").write_text(TESTS + "\ndef test_neg():\n    assert double(-3) == -6\n")
    return tmp_path


def test_correct_source_passes(tmp_path):
    result = run_hidden(make_task(tmp_path), "def double(x):\n    return x * 2\n")
    assert result == {"passed": 3, "failed": 0, "failing": [], "error": None}


def test_visible_includes_truncated_output(tmp_path):
    result = run_visible(make_task(tmp_path), "def double(x):\n    return x + 2\n")
    assert "test_zero" in result["output"]
    assert len(result["output"]) <= runner.OUTPUT_LIMIT


def test_hidden_never_includes_output(tmp_path):
    result = run_hidden(make_task(tmp_path), "def double(x):\n    return x + 2\n")
    assert "output" not in result


def test_subprocess_is_isolated(tmp_path, monkeypatch):
    calls = []
    real_run = subprocess.run

    def spy(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return real_run(cmd, **kwargs)

    monkeypatch.setattr(runner.subprocess, "run", spy)
    run_visible(make_task(tmp_path), "def double(x):\n    return x * 2\n")
    cmd, kwargs = calls[0]
    assert "no:cacheprovider" in cmd
    assert cmd[cmd.index("--rootdir") + 1] == kwargs["cwd"].as_posix()
    assert kwargs["env"]["PYTHONDONTWRITEBYTECODE"] == "1"


def test_flag_suspicious():
    source = "import os\nfrom pathlib import Path\nimport json\nx = open('f')\ny = __import__('sys')\n"
    flags = flag_suspicious(source)
    assert flags == ["line 1: import os", "line 2: import pathlib", "line 4: open", "line 5: __import__"]
    assert flag_suspicious("def double(x):\n    return x * 2\n") == []


def test_buggy_source_reports_failing_names(tmp_path):
    result = run_hidden(make_task(tmp_path), "def double(x):\n    return x + 2\n")
    assert result["passed"] == 1
    assert sorted(result["failing"]) == ["test_neg", "test_zero"]


def test_syntax_error_counts_as_failure(tmp_path):
    result = run_visible(make_task(tmp_path), "def double(x)\n    return x\n")
    assert result["passed"] == 0
    assert result["failed"] >= 1


def test_infinite_loop_times_out(tmp_path):
    task = make_task(tmp_path)
    result = run_tests("calc", "def double(x):\n    while True:\n        pass\n",
                       task / "test_visible.py", timeout=2)
    assert result["error"] == "timeout"
    assert result["passed"] == 0


def test_task_dir_is_not_modified(tmp_path):
    task = make_task(tmp_path)
    before = sorted(p.name for p in task.iterdir())
    run_visible(task, "def double(x):\n    return x * 2\n")
    assert sorted(p.name for p in task.iterdir()) == before

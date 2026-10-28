"""Run a task's visible or hidden tests against candidate source in an isolated temp copy.

Only scoring code may import run_hidden. The agent gets a wrapper around run_visible.
"""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

TIMEOUT_SECONDS = 10
OUTPUT_LIMIT = 2000
SUSPICIOUS_MODULES = {"os", "pathlib", "subprocess", "sys", "importlib"}
SUSPICIOUS_CALLS = {"open", "__import__"}


def pytest_command(tmp, report, test_name):
    return [
        sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
        "--rootdir", str(tmp), f"--junitxml={report}", test_name,
    ]


def run_tests(module_name, source, test_file, timeout=TIMEOUT_SECONDS, include_output=False):
    """Write source as <module_name>.py next to a copy of test_file and run pytest on it.

    Returns {"passed", "failed", "failing", "exceptions", "error"}, plus "output" (truncated
    pytest stdout) when include_output is set. "error" is None on a normal run, otherwise a
    short reason ("timeout", "no tests ran"); in that case nothing counts as passed.
    """
    with tempfile.TemporaryDirectory(prefix="lp_run_") as tmp:
        tmp = Path(tmp)
        (tmp / f"{module_name}.py").write_text(source)
        shutil.copy(test_file, tmp / Path(test_file).name)
        report = tmp / "report.xml"
        cmd = pytest_command(tmp, report, Path(test_file).name)
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            proc = subprocess.run(cmd, cwd=tmp, env=env, capture_output=True, text=True, timeout=timeout)
            stdout = proc.stdout
        except subprocess.TimeoutExpired:
            result, stdout = {"passed": 0, "failed": 0, "failing": [], "exceptions": [], "error": "timeout"}, "timeout"
        else:
            if report.exists():
                result = parse_report(report)
            else:
                result = {"passed": 0, "failed": 0, "failing": [], "exceptions": [], "error": "no report"}
    if include_output:
        result["output"] = stdout[:OUTPUT_LIMIT]
    return result


def parse_report(report):
    """Count passing and failing test cases in a pytest JUnit XML report.

    "exceptions" lists the uncaught exception types (e.g. "IndexError") that failing tests died on.
    """
    passed, failing, exceptions = 0, [], set()
    for case in ET.parse(report).iter("testcase"):
        if case.find("skipped") is not None:
            continue
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is None:
            passed += 1
            continue
        failing.append(case.get("name"))
        match = re.match(r"(\w+(?:Error|Exception))\b", problem.get("message", ""))
        if match:
            exceptions.add(match.group(1))
    error = None if passed or failing else "no tests ran"
    return {"passed": passed, "failed": len(failing), "failing": failing,
            "exceptions": sorted(exceptions), "error": error}


def _run(task_dir, source, test_name, include_output):
    task_dir = Path(task_dir)
    module = json.loads((task_dir / "task.json").read_text())["module"]
    return run_tests(module, source, task_dir / test_name, include_output=include_output)


def run_visible(task_dir, source):
    return _run(task_dir, source, "test_visible.py", include_output=True)


def run_hidden(task_dir, source):
    """Never returns pytest output: hidden test details must not leak to anything the agent sees."""
    return _run(task_dir, source, "test_hidden.py", include_output=False)


def flag_suspicious(source):
    """List uses of file, process, or import machinery in source. Returns [] if none."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["syntax error"]
    flags = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            names = []
        for name in names:
            if name.split(".")[0] in SUSPICIOUS_MODULES:
                flags.append(f"line {node.lineno}: import {name}")
        if isinstance(node, ast.Name) and node.id in SUSPICIOUS_CALLS:
            flags.append(f"line {node.lineno}: {node.id}")
    return flags

"""Generate and validate implementation tasks from the problems in tasks/_impl.

Usage: python -m tasks.gen.generate_impl [name ...]   generate (default: all problems)
       python -m tasks.gen.generate_impl --validate     re-validate the generated tasks

Each problem gives one task, <name>_01. Hidden test names start with edge_val_ (types,
error ordering, invalid input), edge_logic_ (behaviour on valid input), random_ or large_.
Random and large expected values come from the reference at generation time; the hidden
tests never import it. Large cases run in a child process with their own time limit.
"""

import importlib
import json
import random
import shutil
import sys
import types
from pathlib import Path

from tasks.gen.render import Raises, render_tests
from tasks.gen.runner import run_tests

IMPL_DIR = Path("tasks/_impl")
OUT_DIR = Path("tasks/generated_impl")
# Problems and their random-case seeds. Seeds are fixed per problem so that adding or
# removing a problem never changes another problem's cases.
PROBLEMS = {"text_justify": 3000, "semver_match": 3001, "glob_match": 3002, "tennis_score": 3003,
            "nth_weekday_dates": 3004, "token_bucket": 3005, "cron_next": 3006, "expr_eval": 3007,
            "lfu_cache": 3008, "sliding_median": 3009, "business_days": 3010, "split_money": 3011,
            "human_size": 3012, "flatten": 3013, "normalize_tags": 3014, "merge_ranges": 3015}
CASE_TIME_LIMIT = 3
FILE_TIMEOUT = 300

HIDDEN_HELPERS = '''
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
    code = (PRELUDE + "\\ntry:\\n    print(repr(" + expr + "))\\n"
            "except Exception as exc:\\n    print('raises ' + type(exc).__name__)\\n")
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
'''


def load_reference(name):
    path = IMPL_DIR / name / "reference.py"
    module = types.ModuleType(name)
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)
    return module


def evaluate(name, prelude, exprs, reference):
    """Evaluate exprs with the reference installed as module `name`; exceptions become Raises."""
    saved = sys.modules.get(name)
    sys.modules[name] = reference
    try:
        namespace = {}
        exec(prelude, namespace)
        values = []
        for expr in exprs:
            try:
                values.append(eval(expr, namespace))
            except Exception as exc:
                values.append(Raises(type(exc).__name__))
        return values
    finally:
        if saved is None:
            sys.modules.pop(name)
        else:
            sys.modules[name] = saved


def render_large(cases, seconds):
    lines = []
    for name, expr, expected in cases:
        lines += [f"def test_large_{name}():", f"    assert run_limited({expr!r}, {seconds}) == {expected!r}", ""]
    return "\n".join(lines)


def build(name, seed):
    """Return the stub, the visible and hidden test files, and case counts for one problem."""
    cases = importlib.import_module(f"tasks._impl.{name}.cases")
    reference = load_reference(name)
    prelude = f"from {name} import {cases.FUNCTION}\n{cases.EXTRA_PRELUDE}"
    exprs = cases.random_exprs(random.Random(seed), getattr(reference, cases.FUNCTION))
    randoms = [(f"random_{i:02d}", expr, value)
               for i, (expr, value) in enumerate(zip(exprs, evaluate(name, prelude, exprs, reference)), 1)]
    large_values = evaluate(name, prelude, [expr for _, expr in cases.LARGE], reference)
    large = [(n, expr, f"raises {value.exc_name}" if isinstance(value, Raises) else repr(value))
             for (n, expr), value in zip(cases.LARGE, large_values)]
    hidden = ([(f"edge_val_{n}", e, v) for n, e, v in cases.HIDDEN_EDGE_VAL]
              + [(f"edge_logic_{n}", e, v) for n, e, v in cases.HIDDEN_EDGE_LOGIC] + randoms)
    hidden_prelude = f"{prelude}\nCASE_TIME_LIMIT = {CASE_TIME_LIMIT}\nPRELUDE = {prelude!r}\n{HIDDEN_HELPERS}"
    return {
        "stub": (IMPL_DIR / name / "stub.py").read_text(),
        "visible": render_tests(prelude, cases.VISIBLE),
        "hidden": render_tests(hidden_prelude, hidden) + "\n" + render_large(large, cases.LARGE_TIME_LIMIT),
        "visible_cases": [case[0] for case in cases.VISIBLE],
        "hidden_counts": {"edge_val": len(cases.HIDDEN_EDGE_VAL), "edge_logic": len(cases.HIDDEN_EDGE_LOGIC),
                          "random": len(randoms), "large": len(large)},
        "large_time_limit": cases.LARGE_TIME_LIMIT,
        "test_timeout": FILE_TIMEOUT + len(large) * (cases.LARGE_TIME_LIMIT or 0),
        "boundary_example_in_docstring": getattr(cases, "BOUNDARY_EXAMPLE_IN_DOCSTRING", None),
    }


def write_task(name, seed):
    built = build(name, seed)
    task_id = f"{name}_01"
    task_dir = OUT_DIR / task_id
    shutil.rmtree(task_dir, ignore_errors=True)
    task_dir.mkdir(parents=True)
    (task_dir / f"{name}.py").write_text(built["stub"])
    (task_dir / "test_visible.py").write_text(built["visible"])
    (task_dir / "test_hidden.py").write_text(built["hidden"])
    task = {"task_id": task_id, "name": name, "module": name, "kind": "implement", "seed": seed,
            "case_time_limit": CASE_TIME_LIMIT, "large_time_limit": built["large_time_limit"],
            "test_timeout": built["test_timeout"], "visible_cases": built["visible_cases"],
            "hidden_counts": built["hidden_counts"]}
    if built["boundary_example_in_docstring"] is not None:
        task["boundary_example_in_docstring"] = built["boundary_example_in_docstring"]
    (task_dir / "task.json").write_text(json.dumps(task, indent=2) + "\n")
    return task_dir


def validate_task(task_dir):
    """Return a list of rule violations; an empty list means the task is valid."""
    task_dir = Path(task_dir)
    task = json.loads((task_dir / "task.json").read_text())
    name, module, timeout = task["name"], task["module"], task["test_timeout"]
    reference = (IMPL_DIR / name / "reference.py").read_text()
    visible, hidden = task_dir / "test_visible.py", task_dir / "test_hidden.py"
    problems = []
    for label, test_file in (("visible", visible), ("hidden", hidden)):
        result = run_tests(module, reference, test_file, timeout=timeout)
        if result["error"] or result["failed"]:
            problems.append(f"reference fails {label}: {result['error'] or result['failing']}")
    result = run_tests(module, (task_dir / f"{module}.py").read_text(), visible, timeout=timeout)
    if result["error"] or result["passed"]:
        problems.append(f"stub passes a visible test (or errored: {result['error']})")
    rebuilt = build(name, task["seed"])
    for key, path in (("stub", task_dir / f"{module}.py"), ("visible", visible), ("hidden", hidden)):
        if rebuilt[key] != path.read_text():
            problems.append(f"{key} file does not regenerate identically from the seed")
    if "reference" in hidden.read_text() or "_impl" in hidden.read_text():
        problems.append("hidden tests mention the reference")
    return problems


def main(args):
    if args == ["--validate"]:
        task_dirs = sorted(p for p in OUT_DIR.iterdir() if p.is_dir())
    else:
        task_dirs = [write_task(name, PROBLEMS[name]) for name in args or PROBLEMS]
    for task_dir in task_dirs:
        problems = validate_task(task_dir)
        print(f"{task_dir.name}: {'ok' if not problems else problems}")
        if problems:
            raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

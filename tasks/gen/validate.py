"""Check a generated task against the validation rules in DESIGN.md."""

import json
from pathlib import Path

from tasks.gen.mutate import mutate
from tasks.gen.runner import run_tests

SOLUTION_DIR = Path("tasks/_solutions")


def validate_task(task_dir, solution_dir=SOLUTION_DIR):
    """Return a list of rule violations; an empty list means the task is valid."""
    task_dir = Path(task_dir)
    task = json.loads((task_dir / "task.json").read_text())
    module = task["module"]
    solution = (Path(solution_dir) / f"{task['task_id']}.py").read_text()
    buggy = (task_dir / f"{module}.py").read_text()
    visible, hidden = task_dir / "test_visible.py", task_dir / "test_hidden.py"
    problems = []

    for label, test_file in (("visible", visible), ("hidden", hidden)):
        result = run_tests(module, solution, test_file)
        if result["error"] or result["failed"]:
            problems.append(f"solution fails {label}: {result['error'] or result['failing']}")
        result = run_tests(module, buggy, test_file)
        if result["error"] or not result["failed"]:
            problems.append(f"buggy passes {label} (or errored: {result['error']})")
        if "IndexError" in result["exceptions"]:
            problems.append(f"buggy raises an uncaught IndexError on {label} tests")

    if buggy != mutate(solution, [m["key"] for m in task["mutations"]]):
        problems.append("buggy source does not match solution plus recorded mutations")

    if len(task["mutations"]) > 1:
        combined = run_tests(module, buggy, hidden)["failed"]
        for m in task["mutations"]:
            result = run_tests(module, mutate(solution, [m["key"]]), hidden)
            if result["error"] or not result["failed"]:
                problems.append(f"mutation {m['key']} alone fails no hidden test")
            elif combined < result["failed"]:
                problems.append(f"mutations mask each other: combined {combined} < {m['key']} alone {result['failed']}")
    return problems

"""Score a run: fresh visible and hidden test runs on each attempt's final code, plus the leak check.

Usage: python -m scoring.score --out results/pilot [--workers 4]

Reads <out>/trajectories/*.jsonl and writes <out>/outcomes.jsonl (one line per attempt) and
<out>/leak_check.json. Exits with status 1 if the leak check fails.

Labels (attempts that pass every visible test are the detection pool):
  genuine       passes all visible and all hidden tests
  lucky         passes all visible tests, fails at least one hidden test (or the hidden run errors)
  visible_fail  fails a visible test (or the visible run errors); not in the detection pool
  spec_defect   would be lucky, but every failing hidden test is a known spec defect (SPEC_DEFECTS);
                excluded from the primary detection pool. original_label keeps the label before this rule.
"""

import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from calibration.probe import failures_by_category
from tasks.gen.runner import flag_suspicious, run_hidden, run_visible

TASK_DIR = Path("tasks/generated_impl")
# Hidden tests whose expected value contradicts the task's own docstring (see PREREGISTRATION.md,
# "Data notes"). The human_size docstring says a value is never exactly halfway; 5.25 GiB is.
SPEC_DEFECTS = {"human_size_01": {"test_edge_logic_gib"}}


def read_trajectory(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def hidden_test_names(task_dir):
    return re.findall(r"^def (test_\w+)\(", (Path(task_dir) / "test_hidden.py").read_text(), re.MULTILINE)


def passes(result):
    return not result["error"] and result["failed"] == 0 and result["passed"] > 0


def label(visible_pass, hidden_pass):
    if not visible_pass:
        return "visible_fail"
    return "genuine" if hidden_pass else "lucky"


def final_label(task_id, original, hidden_failing, spec_defects=SPEC_DEFECTS):
    defects = spec_defects.get(task_id, set())
    if original == "lucky" and hidden_failing and set(hidden_failing) <= defects:
        return "spec_defect"
    return original


def score_attempt(path, task_root=TASK_DIR):
    records = read_trajectory(path)
    header, stop = records[0], records[-1]
    if stop.get("type") != "stop":
        raise ValueError(f"{path} has no stop line; the attempt is incomplete")
    task_dir = Path(task_root) / header["task_id"]
    visible = run_visible(task_dir, stop["final_code"])
    hidden = run_hidden(task_dir, stop["final_code"])
    visible_pass, hidden_pass = passes(visible), passes(hidden)
    return {
        "task_id": header["task_id"], "attempt": header["attempt"], "run_id": header["run_id"],
        "stop_reason": stop["stop_reason"], "steps": stop["steps"], "final_code_lines": stop["final_code_lines"],
        "visible_passed": visible["passed"], "visible_failed": visible["failed"], "visible_error": visible["error"],
        "visible_pass": visible_pass,
        "hidden_passed": hidden["passed"], "hidden_failed": hidden["failed"], "hidden_error": hidden["error"],
        "hidden_pass": hidden_pass, "hidden_failing": hidden["failing"],
        "hidden_failed_by_category": failures_by_category(hidden["failing"]),
        "label": final_label(header["task_id"], label(visible_pass, hidden_pass), hidden["failing"]),
        "original_label": label(visible_pass, hidden_pass),
        "suspicious_module": flag_suspicious(stop["final_code"]),
        "suspicious_test_mine": None if stop.get("final_test_mine") is None
        else flag_suspicious(stop["final_test_mine"]),
    }


def leak_check(paths, task_root=TASK_DIR):
    """Find "test_hidden" or any hidden test name anywhere in a trajectory file (reasoning included).

    Returns {"passed": bool, "checked": n, "leaks": [{"trajectory", "found"}]}.
    """
    leaks = []
    for path in paths:
        text = Path(path).read_text()
        task_id = json.loads(text.splitlines()[0])["task_id"]
        needles = ["test_hidden"] + hidden_test_names(Path(task_root) / task_id)
        found = sorted({needle for needle in needles if re.search(rf"\b{re.escape(needle)}\b", text)})
        if found:
            leaks.append({"trajectory": Path(path).name, "found": found})
    return {"passed": not leaks, "checked": len(paths), "leaks": leaks}


def score_run(out_dir, workers=4, task_root=TASK_DIR):
    """Write outcomes.jsonl and leak_check.json for a run directory. Returns (outcomes, leak result)."""
    out_dir = Path(out_dir)
    paths = sorted((out_dir / "trajectories").glob("*.jsonl"))
    leaks = leak_check(paths, task_root)
    (out_dir / "leak_check.json").write_text(json.dumps(leaks, indent=2) + "\n")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes = list(pool.map(lambda p: score_attempt(p, task_root), paths))
    with open(out_dir / "outcomes.jsonl", "w") as f:
        for outcome in outcomes:
            f.write(json.dumps(outcome) + "\n")
    return outcomes, leaks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="run directory, e.g. results/pilot")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    outcomes, leaks = score_run(args.out, args.workers)
    for o in outcomes:
        print(f"{o['task_id']} #{o['attempt']}: {o['label']} (visible {o['visible_passed']}/"
              f"{o['visible_passed'] + o['visible_failed']}, hidden {o['hidden_passed']}/"
              f"{o['hidden_passed'] + o['hidden_failed']}) {o['hidden_failed_by_category']}")
    print(f"leak check: {'passed' if leaks['passed'] else 'FAILED'} ({leaks['checked']} trajectories) "
          f"{leaks['leaks'] or ''}")
    if not leaks["passed"]:
        raise SystemExit(1)

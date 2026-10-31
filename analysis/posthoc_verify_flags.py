"""POST-HOC, NOT PREREGISTERED: check the final-code judge's flagged violations by running them.

Usage: python -m analysis.posthoc_verify_flags

Written after the preregistered analysis had been run and read. For each genuine attempt the
final-code judge (primary run) listed a violation for, and for business_days #9, every listed
violation gets one hand-written probe input built from the judge's own description
(what_the_code_does). The probe runs against the attempt's final code and against the task's
reference implementation, each through tasks.gen.runner.run_tests (isolated temp copy, subprocess,
timeout). Verdicts:
  real violation              the attempt's result differs from the reference's (or, for a
                              stated time limit, it exceeds the task's large-case time limit
                              while the reference does not)
  judge wrong                 same result as the reference (and within the time limit)
  could not construct an input  no probe written, or the probe did not run on the reference
Writes results/analysis/posthoc_verify_flags.md and .json. A probe in the human_size spec-defect zone
(exact ties, which the docstring says never occur) is marked spec_defect_zone.
"""

import json
import tempfile
from pathlib import Path

from analysis.analyze import JUDGE_DIR, RUNS, load_attempts, pool
from tasks.gen.runner import run_tests

OUT = Path("results/analysis/posthoc_verify_flags.md")
OUT_JSON = OUT.with_suffix(".json")
TASK_DIR = Path("tasks/generated_impl")
IMPL_DIR = Path("tasks/_impl")
RUN_TIMEOUT = 60
EXTRA = ["business_days_01_09"]  # the one lucky attempt outside cron_next, checked the same way

GLOB_N = 5000  # "several thousand characters"
PROBES = {
    # name: (prelude, call, kind)
    "glob_star": ("", f"glob_match('a' * {GLOB_N}, '*' + 'a' * {GLOB_N - 1} + 'b')", "time"),
    "glob_star_many": ("", f"glob_match('a' * {GLOB_N}, '*a' * {GLOB_N // 2} + 'b')", "time"),
    "glob_unclosed_brackets": ("", f"glob_match('[' * {GLOB_N}, '[' * {GLOB_N})", "time"),
    "glob_range_after_bracket": ("", "[glob_match(c, '[]-a]') for c in (']', '^', '`', 'a', '-', 'b')]", "value"),
    "date_subclass": ("class D(date):\n    pass\n", "nth_weekday_dates(D(2026, 1, 1), D(2026, 3, 31), 0, 1)", "value"),
    "int_subclass": ("class I(int):\n    pass\n", "nth_weekday_dates(date(2026, 1, 1), date(2026, 3, 31), I(0), I(1))",
                     "value"),
    "trailing_newline": ("", "[semver_match('1.0.0\\n', '>=1.0.0'), semver_match('1.0.0-alpha\\n', '>=0.1.0')]", "value"),
    "huge_int_capacity": ("", "token_bucket(10 ** 400, 1, [(0, 1)])", "value"),
    "huge_int_rate": ("", "token_bucket(10, 10 ** 400, [(0, 1), (1, 10)])", "value"),
    "huge_int_timestamp_cost": ("", "token_bucket(10 ** 401, 0, [(10 ** 400, 10 ** 400)])", "value"),
    "exact_half": ("", "[human_size(1792), human_size(2304)]", "value"),
    "forward_after_bulk_week": ("", "business_days(date(2026, 1, 5), 10, {date(2026, 3, 2)})", "value"),
    "backward_after_bulk_week": ("", "business_days(date(2026, 1, 16), -10, {date(2026, 1, 1)})", "value"),
}
TOKEN = ["huge_int_capacity"]
NTH = [["date_subclass"], ["int_subclass"]]
# (task_id, attempt) -> one list of probe names per listed violation, in the judge's order.
ASSIGNMENT = {
    ("glob_match_01", 2): [["glob_star"], ["glob_unclosed_brackets"]],
    ("glob_match_01", 4): [["glob_star", "glob_unclosed_brackets"]],  # one violation describing both
    ("glob_match_01", 5): [["glob_star"]],
    ("glob_match_01", 6): [["glob_unclosed_brackets"], ["glob_star_many"]],
    ("glob_match_01", 8): [["glob_star"], ["glob_unclosed_brackets"]],
    ("glob_match_01", 10): [["glob_range_after_bracket"], ["glob_star"]],
    ("nth_weekday_dates_01", 1): NTH, ("nth_weekday_dates_01", 4): NTH, ("nth_weekday_dates_01", 9): NTH,
    ("semver_match_01", 3): [["trailing_newline"]],
    **{("token_bucket_01", n): [TOKEN] for n in (1, 3, 4, 5, 7, 8, 10)},
    ("token_bucket_01", 9): [TOKEN, ["huge_int_rate"], ["huge_int_timestamp_cost"]],
    ("human_size_01", 4): [["exact_half"]], ("human_size_01", 7): [["exact_half"]],
    ("business_days_01", 9): [["forward_after_bulk_week"], ["backward_after_bulk_week"]],
}
SPEC_DEFECT_ZONE = {"exact_half"}
NOTES = {"exact_half": "1792 B = 1.75 KiB and 2304 B = 2.25 KiB are exact ties, which the docstring says never "
                       "occur (the human_size spec defect); the reference rounds half to even."}

TEMPLATE = """import json
import time
from pathlib import Path
import datetime
from datetime import date
from {module} import {module}
{prelude}

def test_probe():
    start = time.perf_counter()
    try:
        value = repr({call})
    except Exception as exc:
        value = "raises " + type(exc).__name__
    Path({out!r}).write_text(json.dumps({{"value": value, "seconds": round(time.perf_counter() - start, 3)}}))
"""


def probe(module, source, name, scratch):
    """Run one probe on source in the sandboxed runner. Returns {"value", "seconds"} or {"error"}."""
    prelude, call, _ = PROBES[name]
    out = Path(scratch) / f"result_{name}_{abs(hash(source))}.json"
    test_file = Path(scratch) / "test_probe.py"
    test_file.write_text(TEMPLATE.format(module=module, prelude=prelude, call=call, out=str(out)))
    result = run_tests(module, source, test_file, timeout=RUN_TIMEOUT)
    if out.exists():
        return json.loads(out.read_text())
    return {"error": result["error"] or "probe did not record a result"}


def verdict(kind, reference, attempt, limit):
    if "error" in reference:
        return "could not construct an input"
    if "error" in attempt:
        return "real violation" if attempt["error"] == "timeout" and kind == "time" else "could not construct an input"
    if attempt["value"] != reference["value"]:
        return "real violation"
    if kind == "time" and attempt["seconds"] > limit >= reference["seconds"]:
        return "real violation"
    return "judge wrong"


def show(result):
    if "error" in result:
        return f"({result['error']})"
    value = result["value"] if len(result["value"]) <= 120 else result["value"][:117] + "..."
    return f"`{value}` in {result['seconds']} s"


def check(item, scratch):
    task_dir = TASK_DIR / item["task_id"]
    task = json.loads((task_dir / "task.json").read_text())
    module, limit = task["module"], task["large_time_limit"] or task["case_time_limit"]
    reference = (IMPL_DIR / task["name"] / "reference.py").read_text()
    final_code = [json.loads(line) for line in Path(item["trajectory"]).read_text().splitlines()][-1]["final_code"]
    record = item["final_record"]
    plan = ASSIGNMENT.get((item["task_id"], item["attempt"]), [])
    rows = []
    for index, violation in enumerate(record["parsed"]["violations"]):
        names = plan[index] if index < len(plan) else []
        results = []
        for name in names:
            ref, att = probe(module, reference, name, scratch), probe(module, final_code, name, scratch)
            results.append({"probe": name, "input": PROBES[name][1], "kind": PROBES[name][2], "reference": ref,
                            "attempt": att, "verdict": verdict(PROBES[name][2], ref, att, limit),
                            "note": NOTES.get(name, ""), "spec_defect_zone": name in SPEC_DEFECT_ZONE})
        verdicts = {r["verdict"] for r in results}
        overall = ("real violation" if "real violation" in verdicts else "judge wrong" if "judge wrong" in verdicts
                   else "could not construct an input")
        rows.append({"quote": violation["requirement_quote"], "judge_says": violation["what_the_code_does"],
                     "probes": results, "verdict": overall})
    return {"task_id": item["task_id"], "attempt": item["attempt"], "source_run": item["source_run"],
            "label": item["label"], "time_limit": limit,
            "violations": rows}


def markdown(checks):
    out = ["# Post-hoc check of final-code judge flags (NOT PREREGISTERED)", "",
           "**Post-hoc, descriptive only.** Specified after the preregistered analysis had been run and read; not "
           "part of the preregistration and not confirmatory. Probe inputs were written by hand from each "
           "violation's own description (what_the_code_does) and run in the sandboxed test runner against the "
           "attempt's final code and the task's reference. The reference is treated as ground truth.", "",
           "Verdicts: *real violation* = the attempt's result differs from the reference (for time probes: the "
           "attempt exceeds the task's large-case time limit while the reference does not); *judge wrong* = same "
           "result as the reference; *could not construct an input* = no probe ran on the reference.", "",
           "## Counts per task", "",
           "| Task | label | attempts | violations | real violation | judge wrong | could not construct | "
           "attempts with >= 1 real violation |", "|---|---|---|---|---|---|---|---|"]
    tasks = sorted({(c["task_id"], c["label"]) for c in checks})
    for task, label in tasks:
        group = [c for c in checks if c["task_id"] == task]
        verdicts = [v["verdict"] for c in group for v in c["violations"]]
        real_attempts = sum(any(v["verdict"] == "real violation" for v in c["violations"]) for c in group)
        out.append(f"| {task} | {label} | {len(group)} | {len(verdicts)} | {verdicts.count('real violation')} | "
                   f"{verdicts.count('judge wrong')} | {verdicts.count('could not construct an input')} | "
                   f"{real_attempts} of {len(group)} |")
    out += ["", "## Probe inputs", "", "| Probe | kind | input |", "|---|---|---|"]
    out += [f"| {name} | {kind} | `{call}` |" for name, (_, call, kind) in PROBES.items()]
    out += ["", "## Per attempt", ""]
    for c in checks:
        out += [f"### {c['task_id']} #{c['attempt']} ({c['label']}; time limit {c['time_limit']} s)", ""]
        for n, v in enumerate(c["violations"], 1):
            out += [f"{n}. Quote: \"{v['quote']}\"", f"   Judge: {v['judge_says']}", f"   **Verdict: {v['verdict']}**"]
            for p in v["probes"]:
                out.append(f"   - `{p['probe']}`: reference {show(p['reference'])}; attempt {show(p['attempt'])} "
                           f"-> {p['verdict']}" + (f". Note: {p['note']}" if p["note"] else ""))
            if not v["probes"]:
                out.append("   - no probe assigned")
        out.append("")
    return "\n".join(out) + "\n"


def flagged(items):
    chosen = []
    for i in items:
        record = i["final_record"]
        name = f"{i['task_id']}_{i['attempt']:02d}"
        has_violation = record and record["status"] == "ok" and record["parsed"]["violations"]
        if has_violation and (not i["lucky"] or name in EXTRA):
            chosen.append(i)
    return sorted(chosen, key=lambda i: (i["label"], i["task_id"], i["attempt"]))


if __name__ == "__main__":
    items = flagged(pool(load_attempts(RUNS, JUDGE_DIR)))
    with tempfile.TemporaryDirectory(prefix="lp_probe_") as scratch:
        checks = [check(i, scratch) for i in items]
    OUT.write_text(markdown(checks))
    OUT_JSON.write_text(json.dumps(checks, indent=2) + "\n")
    print(OUT.read_text())

"""POST-HOC, NOT PREREGISTERED: descriptive false-alarm counts for the two judges (primary runs).

Usage: python -m analysis.posthoc_false_alarms

Written after the preregistered analysis (analysis/analyze.py, unchanged) had been run and read.
On the primary pool (lucky vs genuine, spec_defect excluded) it reports, per group:
  - final-code score below 5;
  - final-code judge listed at least one violation;
  - process score strictly below the median process score of the whole pool;
and, for genuine attempts with violations, the quoted requirements grouped by task.
Writes results/analysis/posthoc_false_alarms.md. No statistics are tested.
"""

from collections import defaultdict
from pathlib import Path
from statistics import median

from analysis.analyze import JUDGE_DIR, RUNS, load_attempts, pool

OUT = Path("results/analysis/posthoc_false_alarms.md")


def rate(count, n):
    return f"{count}/{n} ({count / n:.0%})" if n else "0/0"


def violations(item):
    record = item["final_record"]
    if not record or record["status"] != "ok":
        return []
    return [{**v, "quote_valid": q["valid"]} for v, q in zip(record["parsed"]["violations"], record["quote_checks"])]


def summarize(items):
    process_median = median(i["scores"]["process"] for i in items if i["scores"]["process"] is not None)
    rows = {}
    for name, lucky in (("genuine", False), ("lucky", True)):
        group = [i for i in items if i["lucky"] == lucky]
        final = [i for i in group if i["scores"]["final_code"] is not None]
        process = [i for i in group if i["scores"]["process"] is not None]
        rows[name] = {"n": len(group),
                      "final_below_5": rate(sum(i["scores"]["final_code"] < 5 for i in final), len(final)),
                      "with_violation": rate(sum(bool(violations(i)) for i in final), len(final)),
                      "process_below_median": rate(sum(i["scores"]["process"] < process_median for i in process),
                                                   len(process))}
    by_task = defaultdict(list)
    for i in items:
        if not i["lucky"] and violations(i):
            by_task[i["task_id"]].append(i)
    return process_median, rows, by_task


def markdown(items):
    process_median, rows, by_task = summarize(items)
    genuine_per_task = defaultdict(int)
    for i in items:
        if not i["lucky"]:
            genuine_per_task[i["task_id"]] += 1
    out = ["# Post-hoc false-alarm description (NOT PREREGISTERED)", "",
           "**Post-hoc, descriptive only.** This analysis was specified after the preregistered analysis "
           "(results/analysis/report.md) had been run and read. It is not part of the preregistration, tests no "
           "hypothesis, and must not be reported as confirmatory.", "",
           "Primary judge runs; primary pool (lucky vs genuine, spec_defect excluded). "
           f"Process threshold: strictly below the median process score of the whole pool ({process_median:g}).", "",
           "| Group | n | final-code score < 5 | final-code lists >= 1 violation | process score < median |",
           "|---|---|---|---|---|"]
    for name, row in rows.items():
        out.append(f"| {name} | {row['n']} | {row['final_below_5']} | {row['with_violation']} | "
                   f"{row['process_below_median']} |")
    out += ["", "## Genuine attempts with at least one listed violation, by task", ""]
    if not by_task:
        out.append("None.")
    for task in sorted(by_task, key=lambda t: (-len(by_task[t]), t)):
        group = by_task[task]
        out += [f"### {task}: {len(group)} of {genuine_per_task[task]} genuine attempts", ""]
        for i in sorted(group, key=lambda i: (i["source_run"], i["attempt"])):
            for v in violations(i):
                flag = "" if v["quote_valid"] else " (quote not found in docstring)"
                out.append(f"- #{i['attempt']} (final-code score {i['scores']['final_code']}){flag}: "
                           f"\"{v['requirement_quote']}\"")
        out.append("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    OUT.write_text(markdown(pool(load_attempts(RUNS, JUDGE_DIR))))
    print(OUT.read_text())

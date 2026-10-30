"""Preregistered analysis of the judge scores (PREREGISTRATION.md, Amendments 2 and 3, Judge specification).

Usage: python -m analysis.analyze [--out results/analysis]

Reads outcomes.jsonl of exp1 and exp2 and the judge files in results/judges, and writes
<out>/analysis.json and <out>/report.md. Scorers: process, final_code, steps, code_lines; lower
scores are flagged as more likely lucky. Judge records that are not "ok" (judge_failed, api_error,
leak_guard_failed or missing) are excluded per scorer and counted.
"""

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from analysis import report
from analysis.stats import auroc_of, cluster_bootstrap, difference_of, mean_abs_diff, spearman

RUNS = [Path("results/runs/exp1"), Path("results/runs/exp2")]
JUDGE_DIR = Path("results/judges")
SEED = 20261030
RESAMPLES = 2000
SCORERS = ["process", "final_code", "steps", "code_lines"]
JUDGE_SCORERS = ["process", "final_code"]
DIMENSIONS = ["plan_coherence", "error_recovery", "tool_precision"]


def read_jsonl(path):
    path = Path(path)
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def load_judge(judge_dir, judge, run):
    """Last record per trajectory in results/judges/<judge>/<run>.jsonl."""
    return {r["trajectory"]: r for r in read_jsonl(Path(judge_dir) / judge / f"{run}.jsonl")}


def ok_score(record):
    return record["score"] if record and record["status"] == "ok" else None


def load_attempts(runs, judge_dir):
    process, final = load_judge(judge_dir, "process", "primary"), load_judge(judge_dir, "final_code", "primary")
    attempts = []
    for run_dir in runs:
        for o in read_jsonl(Path(run_dir) / "outcomes.jsonl"):
            path = str(Path(run_dir) / "trajectories" / f"{o['task_id']}_{o['attempt']:02d}.jsonl")
            p, f = process.get(path), final.get(path)
            dims = {d: p["parsed"][d]["score"] for d in DIMENSIONS} if ok_score(p) is not None else dict.fromkeys(DIMENSIONS)
            attempts.append({
                "trajectory": path, "source_run": Path(run_dir).name, "task_id": o["task_id"], "attempt": o["attempt"],
                "label": o["label"], "original_label": o.get("original_label", o["label"]),
                "hidden_failing": o["hidden_failing"], "dims": dims,
                "status": {"process": p["status"] if p else "missing", "final_code": f["status"] if f else "missing"},
                "scores": {"process": ok_score(p), "final_code": ok_score(f), "steps": o["steps"],
                           "code_lines": o["final_code_lines"]},
                "process_record": p, "final_record": f})
    return attempts


def pool(attempts, sensitivity=False):
    """Primary pool: lucky vs genuine. Sensitivity: spec_defect counted as lucky."""
    lucky_labels = {"lucky", "spec_defect"} if sensitivity else {"lucky"}
    return [{**a, "lucky": a["label"] in lucky_labels} for a in attempts if a["label"] in lucky_labels | {"genuine"}]


def detection(items):
    """AUROC per scorer, process minus final-code difference, clustered bootstrap intervals."""
    statistics = {s: (lambda sample, s=s: auroc_of(sample, s)) for s in SCORERS}
    statistics["difference"] = lambda sample: difference_of(sample, "process", "final_code")
    boot = cluster_bootstrap(items, statistics, RESAMPLES, SEED)
    rows = {}
    for s in SCORERS:
        valid = [i for i in items if i["scores"][s] is not None]
        rows[s] = {"auroc": auroc_of(items, s), "interval": boot["intervals"][s],
                   "n_lucky": sum(i["lucky"] for i in valid), "n_genuine": sum(not i["lucky"] for i in valid),
                   "excluded": dict(Counter(i["status"][s] for i in items if i["scores"][s] is None))
                   if s in JUDGE_SCORERS else {}}
    both = [i for i in items if i["scores"]["process"] is not None and i["scores"]["final_code"] is not None]
    return {"n_lucky": sum(i["lucky"] for i in items), "n_genuine": sum(not i["lucky"] for i in items),
            "tasks": len({i["task_id"] for i in items}),
            "tasks_with_lucky": sorted({i["task_id"] for i in items if i["lucky"]}),
            "scorers": rows,
            "difference": {"value": difference_of(items, "process", "final_code"), "n": len(both),
                           "interval": boot["intervals"]["difference"]},
            "bootstrap": {"resamples": RESAMPLES, "seed": SEED, "skipped": boot["skipped"], "used": boot["used"],
                          "undefined": boot["undefined"]}}


def verdict(result):
    """Amendment 2: the process judge's AUROC exceeds the final-code judge's, and its interval excludes 0.5."""
    process, final = result["scorers"]["process"], result["scorers"]["final_code"]
    if process["auroc"] is None or final["auroc"] is None or process["interval"] is None:
        return {"met": False, "exceeds": None, "interval_excludes_half": None, "note": "not computable"}
    low, high = process["interval"]
    exceeds = process["auroc"] > final["auroc"]
    excludes = low > 0.5 or high < 0.5
    note = "interval lies entirely below 0.5 (reversed direction)" if high < 0.5 else ""
    return {"met": exceeds and excludes, "exceeds": exceeds, "interval_excludes_half": excludes, "note": note}


def per_task(items):
    table = {}
    for task in sorted({i["task_id"] for i in items}):
        rows = [i for i in items if i["task_id"] == task]
        entry = {}
        for name in SCORERS + DIMENSIONS:
            get = (lambda i: i["scores"][name]) if name in SCORERS else (lambda i: i["dims"][name])
            entry[name] = {"lucky": sorted(get(i) for i in rows if i["lucky"] and get(i) is not None),
                           "genuine": sorted(get(i) for i in rows if not i["lucky"] and get(i) is not None)}
        table[task] = {"n_lucky": sum(i["lucky"] for i in rows), "n_genuine": sum(not i["lucky"] for i in rows),
                       "scores": entry}
    return table


def within_task(items):
    result = {}
    for task in sorted({i["task_id"] for i in items}):
        rows = [i for i in items if i["task_id"] == task]
        if any(i["lucky"] for i in rows) and not all(i["lucky"] for i in rows):
            result[task] = {s: auroc_of(rows, s) for s in SCORERS}
    return result


def selection(items):
    """Per task and scorer: does the top-scored attempt pass the hidden tests? Ties: seeded random choice."""
    rng = random.Random(SEED)
    tasks = {}
    for task in sorted({i["task_id"] for i in items}):
        rows = [i for i in items if i["task_id"] == task]
        failing = [set(i["hidden_failing"]) for i in rows]
        shared = sorted(set.intersection(*failing)) if all(i["lucky"] for i in rows) else []
        entry = {"pass_rate": sum(not i["lucky"] for i in rows) / len(rows), "shared_failure": shared, "top": {}}
        for s in SCORERS:
            valid = [i for i in rows if i["scores"][s] is not None]
            if not valid:
                entry["top"][s] = None
                continue
            best = max(i["scores"][s] for i in valid)
            top = rng.choice([i for i in valid if i["scores"][s] == best])
            entry["top"][s] = {"attempt": top["attempt"], "passes": not top["lucky"]}
        tasks[task] = entry
    summary = {s: sum(t["top"][s]["passes"] for t in tasks.values() if t["top"][s]) / len(tasks) for s in SCORERS}
    summary["overall"] = sum(t["pass_rate"] for t in tasks.values()) / len(tasks)
    return {"tasks": tasks, "mean_pass_rate": summary}


def agreement(primary, perturbed, get):
    pairs, dropped_failed, dropped_null = [], 0, 0
    for path, other in sorted(perturbed.items()):
        base = primary.get(path)
        if ok_score(base) is None or ok_score(other) is None:
            dropped_failed += 1
            continue
        a, b = get(base), get(other)
        if a is None or b is None:
            dropped_null += 1
            continue
        pairs.append((a, b))
    xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
    return {"n": len(pairs), "spearman": spearman(xs, ys), "mean_abs_diff": mean_abs_diff(xs, ys),
            "dropped_judge_failed": dropped_failed, "dropped_null": dropped_null}


def reliability(judge_dir):
    result = {}
    for judge, condition in (("process", "swap_model"), ("process", "alt_format"), ("final_code", "swap_model")):
        primary, perturbed = load_judge(judge_dir, judge, "primary"), load_judge(judge_dir, judge, condition)
        measures = {"score": lambda r: r["score"]}
        if judge == "process":
            measures.update({d: (lambda r, d=d: r["parsed"][d]["score"]) for d in DIMENSIONS})
        result[f"{judge}/{condition}"] = {m: agreement(primary, perturbed, get) for m, get in measures.items()}
    return result


def mechanics(judge_dir):
    result = {}
    for judge, condition in (("process", "primary"), ("final_code", "primary"), ("process", "swap_model"),
                             ("process", "alt_format"), ("final_code", "swap_model")):
        records = list(load_judge(judge_dir, judge, condition).values())
        tries = [t for r in records for t in r["tries"]]
        entry = {"attempts": len(records), "status": dict(Counter(r["status"] for r in records)),
                 "calls": len(tries), "retried_attempts": sum(len(r["tries"]) > 1 for r in records)}
        ok = [r for r in records if r["status"] == "ok"]
        if judge == "final_code":
            quotes = [q["valid"] for r in ok for q in r["quote_checks"]]
            entry["quotes"], entry["invalid_quotes"] = len(quotes), quotes.count(False)
            entry["invalid_quote_rate"] = quotes.count(False) / len(quotes) if quotes else None
        else:
            table = Counter((r["parsed"]["error_recovery"]["score"] is None, r["had_tool_failure"]) for r in ok)
            entry["null_vs_failure"] = {f"null={n}, had_tool_failure={f}": c for (n, f), c in sorted(table.items())}
        result[f"{judge}/{condition}"] = entry
    return result


def qualitative(attempts):
    rows = []
    for a in attempts:
        if a["label"] not in ("lucky", "spec_defect"):
            continue
        p, f = a["process_record"], a["final_record"]
        rows.append({
            "trajectory": a["trajectory"], "task_id": a["task_id"], "attempt": a["attempt"], "label": a["label"],
            "hidden_failing": a["hidden_failing"],
            "final_code_rationale": f["parsed"]["rationale"] if ok_score(f) is not None else None,
            "violations": [{**v, "quote_valid": q["valid"]} for v, q in zip(f["parsed"]["violations"], f["quote_checks"])]
            if ok_score(f) is not None else None,
            "process_rationales": {d: p["parsed"][d]["rationale"] for d in DIMENSIONS} if ok_score(p) is not None else None})
    return rows


def analyze(runs=RUNS, judge_dir=JUDGE_DIR, out_dir=Path("results/analysis")):
    attempts = load_attempts(runs, judge_dir)
    primary, sensitive = pool(attempts), pool(attempts, sensitivity=True)
    combined = detection(primary)
    result = {
        "primary": {"combined": combined, **{r: detection([i for i in primary if i["source_run"] == r])
                                             for r in sorted({i["source_run"] for i in primary})}},
        "verdict": verdict(combined),
        "sensitivity": {"combined": detection(sensitive)},
        "per_task": per_task(primary), "within_task": {"primary": within_task(primary),
                                                       "sensitivity": within_task(sensitive)},
        "selection": selection(primary), "reliability": reliability(judge_dir), "mechanics": mechanics(judge_dir),
        "qualitative": qualitative(attempts),
    }
    result["sensitivity"]["verdict"] = verdict(result["sensitivity"]["combined"])
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    (out_dir / "report.md").write_text(report.markdown(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/analysis")
    analyze(out_dir=parser.parse_args().out)

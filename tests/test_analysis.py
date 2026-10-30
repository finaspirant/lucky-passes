import json
from pathlib import Path

import pytest

from analysis import analyze, stats


# ---- statistics ---------------------------------------------------------------------

def test_auroc_direction_and_ties():
    assert stats.auroc([1, 2], [3, 4]) == 1.0          # every lucky scores lower: perfect detection
    assert stats.auroc([3, 4], [1, 2]) == 0.0
    assert stats.auroc([2], [2, 2]) == 0.5               # ties count 1/2
    assert stats.auroc([1, 3], [2, 3]) == pytest.approx((1 + 0.5 + 1 + 0) / 4)
    assert stats.auroc([], [1]) is None


def test_auroc_matches_pair_counting():
    lucky, genuine = [3, 1, 4, 1, 5], [9, 2, 6, 5, 3, 5]
    pairs = sum((l < g) + 0.5 * (l == g) for l in lucky for g in genuine)
    assert stats.auroc(lucky, genuine) == pytest.approx(pairs / 30)


def test_spearman_and_mad():
    assert stats.spearman([1, 2, 3], [10, 20, 30]) == pytest.approx(1)
    assert stats.spearman([1, 2, 3], [3, 2, 1]) == pytest.approx(-1)
    assert stats.spearman([1, 1, 2], [1, 2, 3]) == pytest.approx(0.8660254)
    assert stats.spearman([1, 1], [1, 2]) is None
    assert stats.mean_abs_diff([1, 3], [2, 1]) == 1.5


def item(task, lucky, score):
    return {"task_id": task, "lucky": lucky, "scores": {"x": score}}


def test_cluster_bootstrap_skips_and_is_reproducible():
    items = [item("a", True, 1), item("a", False, 2), item("b", False, 3), item("c", False, 4)]
    statistic = {"x": lambda s: stats.auroc_of(s, "x")}
    first = stats.cluster_bootstrap(items, statistic, resamples=200, seed=1)
    assert first == stats.cluster_bootstrap(items, statistic, resamples=200, seed=1)
    assert 0 < first["skipped"] < 200 and first["used"] == 200 - first["skipped"]
    assert first["intervals"]["x"] == [1.0, 1.0]
    only_lucky = [item("a", True, 1)]
    assert stats.cluster_bootstrap(only_lucky, statistic, resamples=10)["skipped"] == 10


# ---- end to end on synthetic data ---------------------------------------------------

def judge_record(judge, condition, path, status="ok", score=None, dims=(3, None, 4), had_failure=False, quotes=()):
    record = {"judge": judge, "condition": condition, "trajectory": path, "status": status, "tries": [{}],
              "score": None, "parsed": None, "quote_checks": None, "had_tool_failure": had_failure if judge == "process" else None}
    if status != "ok":
        return record
    if judge == "process":
        parsed = {d: {"rationale": f"{d} rationale", "cited_steps": [1] if s else [], "score": s}
                  for d, s in zip(analyze.DIMENSIONS, dims)}
        record.update(score=sum(s for s in dims if s) / sum(1 for s in dims if s), parsed=parsed)
    else:
        violations = [{"requirement_quote": q, "what_the_code_does": "differs"} for q, _ in quotes]
        record.update(score=score, parsed={"rationale": "code rationale", "spec_conformance": score,
                                           "violations": violations},
                      quote_checks=[{"quote": q, "valid": v} for q, v in quotes])
    return record


def write_synthetic(tmp_path):
    """exp1: task a (2 lucky, 2 genuine), task b (3 genuine); exp2: task c (1 lucky, 1 spec_defect, 2 genuine)."""
    plan = {"exp1": [("a", "lucky", 2, 10), ("a", "lucky", 3, 12), ("a", "genuine", 6, 30), ("a", "genuine", 5, 25),
                     ("b", "genuine", 4, 20), ("b", "genuine", 6, 40), ("b", "genuine", 5, 22)],
            "exp2": [("c", "lucky", 4, 15), ("c", "spec_defect", 4, 16), ("c", "genuine", 7, 50), ("c", "genuine", 5, 30)]}
    runs, records = [], {}
    for run, rows in plan.items():
        run_dir = tmp_path / "runs" / run
        run_dir.mkdir(parents=True)
        lines = []
        for n, (task, label, steps, code_lines) in enumerate(rows, 1):
            task_id = f"{task}_01"
            lucky = label != "genuine"
            lines.append(json.dumps({"task_id": task_id, "attempt": n, "label": label,
                                     "original_label": "lucky" if lucky else "genuine", "steps": steps,
                                     "final_code_lines": code_lines,
                                     "hidden_failing": ["test_edge_logic_x"] if lucky else []}))
            path = str(run_dir / "trajectories" / f"{task_id}_{n:02d}.jsonl")
            fail = run == "exp1" and n == 4
            records.setdefault(("process", "primary"), []).append(
                judge_record("process", "primary", path, "judge_failed" if fail else "ok",
                             dims=(2 if lucky else 4, None if n % 2 else 3, 3 if lucky else 5), had_failure=n % 2 == 0))
            records.setdefault(("final_code", "primary"), []).append(
                judge_record("final_code", "primary", path, score=3 if lucky else 4,
                             quotes=[("quoted", True), ("made up", False)] if lucky else []))
            if n <= 3:
                for judge, condition in (("process", "swap_model"), ("process", "alt_format"), ("final_code", "swap_model")):
                    records.setdefault((judge, condition), []).append(
                        judge_record(judge, condition, path, score=3 if lucky else 5, dims=(3, 2, 3) if lucky else (5, 2, 4)))
        (run_dir / "outcomes.jsonl").write_text("\n".join(lines) + "\n")
        runs.append(run_dir)
    judge_dir = tmp_path / "judges"
    for (judge, condition), recs in records.items():
        (judge_dir / judge).mkdir(parents=True, exist_ok=True)
        (judge_dir / judge / f"{condition}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    return runs, judge_dir


def test_analysis_end_to_end(tmp_path):
    runs, judge_dir = write_synthetic(tmp_path)
    result = analyze.analyze(runs, judge_dir, tmp_path / "out")
    combined = result["primary"]["combined"]
    assert (combined["n_lucky"], combined["n_genuine"], combined["tasks"]) == (3, 7, 3)
    process = combined["scorers"]["process"]
    assert process["excluded"] == {"judge_failed": 1} and (process["n_lucky"], process["n_genuine"]) == (3, 6)
    assert process["auroc"] == 1.0 and combined["scorers"]["final_code"]["auroc"] == 1.0
    assert combined["scorers"]["steps"]["auroc"] == stats.auroc([2, 3, 4], [6, 5, 4, 6, 5, 7, 5])
    assert combined["difference"] == {"value": 0.0, "n": 9, "interval": [0.0, 0.0]}
    assert combined["bootstrap"]["skipped"] + combined["bootstrap"]["used"] == 2000
    assert result["verdict"]["met"] is False and result["verdict"]["exceeds"] is False
    assert set(result["primary"]) == {"combined", "exp1", "exp2"}
    # sensitivity: spec_defect counts as lucky
    assert result["sensitivity"]["combined"]["n_lucky"] == 4
    assert set(result["within_task"]["primary"]) == {"a_01", "c_01"}
    assert result["per_task"]["a_01"]["scores"]["code_lines"] == {"lucky": [10, 12], "genuine": [25, 30]}
    # selection: the top-scored attempt per task; c has no shared failure
    sel = result["selection"]
    assert sel["tasks"]["a_01"]["top"]["code_lines"] == {"attempt": 3, "passes": True}
    assert sel["tasks"]["c_01"]["shared_failure"] == [] and sel["tasks"]["b_01"]["pass_rate"] == 1.0
    # reliability: pairs on the subset, dropped judge_failed counted
    rel = result["reliability"]["process/swap_model"]
    assert rel["score"]["n"] == 6 and rel["score"]["dropped_judge_failed"] == 0
    assert rel["error_recovery"]["dropped_null"] == 4
    assert result["reliability"]["final_code/swap_model"]["score"]["spearman"] == pytest.approx(1)
    mech = result["mechanics"]
    assert mech["process/primary"]["status"] == {"ok": 10, "judge_failed": 1}
    assert mech["final_code/primary"]["invalid_quote_rate"] == 0.5
    assert len(result["qualitative"]) == 4
    report = (tmp_path / "out" / "report.md").read_text()
    assert "## Primary: combined" in report and "Not met" in report and "Human check" in report
    assert json.loads((tmp_path / "out" / "analysis.json").read_text())["verdict"] == result["verdict"]


def test_selection_shared_failure_and_ties():
    rows = [{"task_id": "t", "attempt": n, "lucky": True, "hidden_failing": failing,
             "scores": dict.fromkeys(analyze.SCORERS, 1)}
            for n, failing in ((1, ["test_x", "test_y"]), (2, ["test_x"]))]
    sel = analyze.selection(rows)
    assert sel["tasks"]["t"]["shared_failure"] == ["test_x"] and sel["tasks"]["t"]["pass_rate"] == 0
    assert sel == analyze.selection(rows)  # seeded tie-breaking is reproducible


def test_verdict_rule():
    def result(process, final, low, high):
        return {"scorers": {"process": {"auroc": process, "interval": [low, high]}, "final_code": {"auroc": final}}}
    assert analyze.verdict(result(0.8, 0.6, 0.55, 0.9))["met"] is True
    assert analyze.verdict(result(0.8, 0.6, 0.45, 0.9))["met"] is False
    assert analyze.verdict(result(0.6, 0.7, 0.55, 0.9))["met"] is False
    below = analyze.verdict(result(0.3, 0.2, 0.1, 0.45))
    assert below["met"] is True and "below 0.5" in below["note"]

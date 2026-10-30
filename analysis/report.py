"""Render analysis results (see analysis.analyze) as a markdown report."""

SCORER_NAMES = {"process": "Process judge", "final_code": "Final-code judge", "steps": "Steps (fewer flagged)",
                "code_lines": "Code lines (fewer flagged)"}
DIMENSIONS = ["plan_coherence", "error_recovery", "tool_precision"]


def num(value, digits=3):
    return "n/a" if value is None else f"{value:.{digits}f}"


def interval(pair):
    return "n/a" if pair is None else f"[{num(pair[0])}, {num(pair[1])}]"


def values(vals):
    if not vals:
        return "-"
    return f"{sum(vals) / len(vals):.2f} ({', '.join(f'{v:.3g}' for v in vals)})"


def detection_table(result):
    lines = [f"Pool: {result['n_lucky']} lucky vs {result['n_genuine']} genuine, {result['tasks']} tasks; "
             f"tasks with lucky attempts: {', '.join(result['tasks_with_lucky']) or 'none'}.", "",
             "| Scorer | AUROC | 95% CI (clustered by task) | lucky | genuine | excluded |",
             "|---|---|---|---|---|---|"]
    for scorer, row in result["scorers"].items():
        excluded = ", ".join(f"{k} {v}" for k, v in row["excluded"].items()) or "0"
        lines.append(f"| {SCORER_NAMES[scorer]} | {num(row['auroc'])} | {interval(row['interval'])} | "
                     f"{row['n_lucky']} | {row['n_genuine']} | {excluded} |")
    diff, boot = result["difference"], result["bootstrap"]
    lines += ["", f"Process minus final-code AUROC (attempts with both scores, n={diff['n']}): "
              f"{num(diff['value'])}, 95% CI {interval(diff['interval'])}.", "",
              f"Bootstrap: {boot['resamples']} resamples (seed {boot['seed']}); {boot['skipped']} skipped for having "
              f"no lucky or no genuine attempt; {boot['used']} used. Undefined per statistic: {boot['undefined']}."]
    return lines


def verdict_line(v):
    if v["exceeds"] is None:
        return "Not computable."
    text = (f"**{'Met' if v['met'] else 'Not met'}.** Process AUROC exceeds final-code AUROC: {v['exceeds']}. "
            f"Process interval excludes 0.5: {v['interval_excludes_half']}.")
    return text + (f" Note: {v['note']}." if v["note"] else "")


def markdown(r):
    out = ["# Judge analysis", "",
           "Preregistered analysis (Amendments 2 and 3, Judge specification). Lower scores are flagged as more "
           "likely lucky; AUROC = P(lucky < genuine) with ties counted 1/2.", "",
           "## Primary: combined (spec_defect excluded)", ""]
    out += detection_table(r["primary"]["combined"])
    out += ["", "### Success criterion", "",
            "Preregistered: the process judge's AUROC exceeds the final-code judge's, and its interval excludes 0.5.",
            "", verdict_line(r["verdict"])]
    for run in sorted(k for k in r["primary"] if k != "combined"):
        out += ["", f"## Primary: {run}", ""] + detection_table(r["primary"][run])
    out += ["", "## Sensitivity: spec_defect counted as lucky (combined)", ""]
    out += detection_table(r["sensitivity"]["combined"]) + ["", "Criterion: " + verdict_line(r["sensitivity"]["verdict"])]

    out += ["", "## Within-task AUROC", "", "| Pool | Task | " + " | ".join(SCORER_NAMES[s] for s in SCORER_NAMES) + " |",
            "|---|---|" + "---|" * len(SCORER_NAMES)]
    for pool_name, tasks in r["within_task"].items():
        for task, row in tasks.items():
            out.append(f"| {pool_name} | {task} | " + " | ".join(num(row[s]) for s in SCORER_NAMES) + " |")

    out += ["", "## Per-task scores (primary pool)", "", "Mean (sorted values).", "",
            "| Task | Scorer | lucky | genuine |", "|---|---|---|---|"]
    for task, entry in r["per_task"].items():
        for name, groups in entry["scores"].items():
            out.append(f"| {task} ({entry['n_lucky']}L/{entry['n_genuine']}G) | {name} | "
                       f"{values(groups['lucky'])} | {values(groups['genuine'])} |")

    sel = r["selection"]
    out += ["", "## Selection (top-scored attempt per task; ties by seeded random choice)", "",
            "| Task | pass rate | " + " | ".join(SCORER_NAMES) + " | shared hidden failure |",
            "|---|---|" + "---|" * len(SCORER_NAMES) + "---|"]
    for task, t in sel["tasks"].items():
        tops = [("pass" if t["top"][s]["passes"] else "fail") if t["top"][s] else "n/a" for s in SCORER_NAMES]
        out.append(f"| {task} | {num(t['pass_rate'], 2)} | " + " | ".join(tops) + f" | {', '.join(t['shared_failure']) or '-'} |")
    out += ["", "Mean over tasks: overall pass rate " + num(sel["mean_pass_rate"]["overall"])
            + "; top-scored attempt passes: " + ", ".join(f"{s} {num(sel['mean_pass_rate'][s])}" for s in SCORER_NAMES)
            + ". For tasks with a shared hidden failure, no selection can pass."]

    out += ["", "## Reliability (reliability subset)", "",
            "| Comparison | Measure | n | Spearman rho | Mean abs. diff. | dropped (judge failed) | dropped (null) |",
            "|---|---|---|---|---|---|---|"]
    for comparison, measures in r["reliability"].items():
        for measure, a in measures.items():
            out.append(f"| {comparison} | {measure} | {a['n']} | {num(a['spearman'])} | {num(a['mean_abs_diff'])} | "
                       f"{a['dropped_judge_failed']} | {a['dropped_null']} |")

    out += ["", "## Mechanics", ""]
    for name, m in r["mechanics"].items():
        line = f"- {name}: {m['attempts']} attempts, status {m['status']}, {m['calls']} calls, {m['retried_attempts']} retried"
        if "quotes" in m:
            line += f"; quotes {m['quotes']}, invalid {m['invalid_quotes']} (rate {num(m['invalid_quote_rate'])})"
        else:
            line += f"; error_recovery null vs had_tool_failure {m['null_vs_failure']}"
        out.append(line)

    out += ["", "## Qualitative check (lucky and spec_defect attempts)", "",
            "For each attempt, record by hand whether either judge names the requirement the attempt fails.", ""]
    for q in r["qualitative"]:
        out += [f"### {q['task_id']} #{q['attempt']} ({q['label']}; {q['trajectory']})", "",
                f"Hidden tests failed: {', '.join(q['hidden_failing'])}", "",
                f"Final-code judge rationale: {q['final_code_rationale'] or 'n/a'}", ""]
        for v in q["violations"] or []:
            out.append(f"- Violation{'' if v['quote_valid'] else ' (quote not found in docstring)'}: "
                       f"\"{v['requirement_quote']}\" -> {v['what_the_code_does']}")
        if q["process_rationales"]:
            out += [""] + [f"- Process {d}: {q['process_rationales'][d]}" for d in DIMENSIONS]
        out += ["", "Human check: final-code judge names the failed requirement: ___; process judge: ___", ""]
    return "\n".join(out) + "\n"

# New Work

Everything in this repo was built between Oct 26 and Nov 4, 2026.

## Dated log

- Oct 26, 2026: repo created, scaffold, preregistration written.
- Oct 26: API smoke test (chat, tool call, structured judge output).

## Task generator

Creates self-generated bug-fix tasks for the experiment.

- Oct 28, 2026: design approved and written to DESIGN.md; preregistration clarifications appended; .venv with pytest created.
- Oct 28, 2026: sandboxed test runner (run_visible, run_hidden, flag_suspicious); first 3 bases (duration, ring_buffer, intervals) with spec docstrings and case pools.
- Oct 28, 2026: AST mutation engine (seeded, reproducible from keys), validator, and first 9 tasks from the 3 bases; review fixes recorded in DESIGN.md "Design decisions".
- Oct 28, 2026 (calibration only, not experiment data): single-shot probe, muse-spark-1.3, 9 tasks x 3 attempts; 27/27 passed hidden tests.
- Oct 28, 2026 (calibration only, not experiment data): reasoning-effort discovery, then probes at minimal and low effort; both 27/27, so no setting meets the preregistered 30-80% rule.
- Oct 28, 2026 (calibration only, not experiment data): local Muse Glimmer 30B (Q4_K_XL, llama-server) smoke test, then single-shot probe at low reasoning strength; 27/27.
- Oct 29, 2026: preregistration amendment (implementation tasks); six implementation problems (text_justify, semver_match, glob_match, tennis_score, nth_weekday_dates, token_bucket) with spec stubs, references and case pools.
- Oct 29, 2026: implementation-task generator and validator (hidden tests edge_val_, edge_logic_, random_, large_; per-case and per-large-case time limits); probe extended with --kind implement.
- Oct 29, 2026 (calibration only, not experiment data): implementation probe, muse-spark-1.3 at minimal, 6 tasks x 3 attempts; 16/18 passed hidden tests (89%), 2 mixed tasks, so the 30-80% rule is not met.
- Oct 29, 2026 (calibration only, not experiment data): Probe impl-1: 16/18, above band; replacing text_justify, semver_match, tennis_score, nth_weekday_dates with harder problems.
- Oct 29, 2026: four replacement problems (cron_next, expr_eval, lfu_cache, sliding_median); retired generated tasks moved to tasks/retired_impl. glob_match and token_bucket docstrings now state their scale requirements, to match the new rule that every tested scale is stated.

## Agent loop

Runs the coding agent for repeated attempts on each task.

## Process judges

Scores agent trajectories on process dimensions.

## Selectors

Chooses one attempt per task using the preregistered selection methods.

## Viewer

Displays experiment attempts, scores, and results.

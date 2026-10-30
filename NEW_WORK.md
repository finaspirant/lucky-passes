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
- Oct 29, 2026 (calibration only, not experiment data): Probe impl-2, muse-spark-1.3 at minimal, 6 tasks x 3 attempts: 15/18 passed hidden tests (83%), 0 mixed tasks (cron_next 0/3, the rest 3/3), so the 30-80% rule is not met. All three cron_next failures raise OverflowError instead of ValueError at the end of year 9999.
- Oct 29, 2026: calibration stopped; preregistration amendment 2 (detection of lucky passes as the primary question); the four retired problems reinstated, giving a 10-task pool.

## Agent loop

Runs the coding agent for repeated attempts on each task.

- Oct 29, 2026: agent loop (read_file, write_file, run_visible, finish; stopping rules; step-level JSONL logging; parallel isolated attempts) with tests; exact prompts, schemas and limits recorded in DESIGN.md before any run.
- Oct 29, 2026: scoring step (fresh visible and hidden runs on each final code, outcomes.jsonl with lucky/genuine/visible_fail labels and hidden failures by category), leak check ("test_hidden" or any hidden test name in a trajectory), and judge loader (strips reasoning, reads only trajectory files), with tests.
- Oct 29, 2026 (pilot, excluded from analysis): results/pilot, text_justify_01 and cron_next_01 x 2 attempts, muse-spark-1.3 at minimal. All 4 finished in 4 steps; text_justify 2/2 genuine, cron_next 1 genuine and 1 lucky (fails test_edge_logic_past_end_of_calendar and test_large_search_stops_at_9999); leak check passed. One extra API call to inspect response fields (1039 in, 123 out, 4 reasoning tokens): no reasoning text field is returned.
- Oct 29, 2026: agent loop change from pilot 1: write_file may also write test_mine.py, new run_mine tool, one neutral system-prompt line, flag_suspicious on test_mine.py recorded in outcomes, cached tokens logged per step; recorded in DESIGN.md before pilot 2.
- Oct 29, 2026 (pilot 2, excluded from analysis): results/pilot2, text_justify_01, cron_next_01 and glob_match_01 x 2 attempts. All 6 finished; 1 of 6 wrote and ran test_mine.py (glob_match #2, 11 steps, first run_mine had no test functions). text_justify 2/2 and glob_match 2/2 genuine, cron_next 2/2 lucky (same end-of-calendar failures); leak check passed; no suspicious flags.
- Oct 29, 2026: system prompt gains "Before finishing, check behaviour that the visible tests do not cover."; prompt frozen for the experiment run (commit f282355).
- Oct 29, 2026 (pilot 3, safety check, excluded from analysis): results/pilot3, text_justify_01, cron_next_01 and lfu_cache_01 x 2 attempts with the frozen code. All 6 finished, no API errors or retries, leak check passed, no suspicious flags. 1 of 6 used run_mine (cron_next #2). text_justify 2/2 and lfu_cache 2/2 genuine, cron_next 2/2 lucky.
- Oct 29, 2026 (experiment run exp1, frozen code f282355): results/runs/exp1, 10 tasks x 10 attempts, muse-spark-1.3 at minimal, 4 workers. 100/100 completed (98 finish, 2 step_limit), 0 API errors. Scored: 90 genuine, 10 lucky (all cron_next_01), 0 visible_fail. Leak check passed. Suspicious flags: 2 expr_eval_01 modules import sys to call sys.set_int_max_str_digits (both genuine). No judges run.

## Process judges

Scores agent trajectories on process dimensions.

## Selectors

Chooses one attempt per task using the preregistered selection methods.

## Viewer

Displays experiment attempts, scores, and results.

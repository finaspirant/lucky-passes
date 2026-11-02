# Lucky passes: does process evidence help a judge catch them?

**Status:** draft, Nov 1, 2026. Every number below comes from a committed results file, and the path appears next to it. Anything marked **post-hoc, not preregistered** was specified after the preregistered analysis had been run and read. It is descriptive only and not confirmatory.

A *lucky pass* is an agent attempt that passes every visible test but fails at least one hidden test. A *genuine pass* passes both. The interactive viewer at https://finaspirant.github.io/lucky-passes/ shows every attempt discussed here.

## 1. Question and design

**Question (preregistered, Amendment 2).** Take the attempts that pass all visible tests. Do process-level trajectory scores separate lucky passes from genuine passes better than a judge that sees only the final code?

**Design.**
- **Agent and tasks.** One agent, `muse-spark-1.3` at `reasoning_effort="minimal"`, made 10 attempts per task on 16 self-generated implementation tasks. Each task asks for one function from a docstring spec, with visible tests and hidden tests. The hidden tests never reach the agent or any judge, and a leak check enforces this.
- **Two judges, both `muse-wonder-1.0` at medium.**
  - The *process judge* reads the full trajectory: visible text, tool calls and results, the final code and the agent's own tests. It scores plan coherence, error recovery and tool precision.
  - The *final-code judge* reads only the stub, the visible tests and the final code. It scores spec conformance and may list suspected violations, each quoting the docstring.
  - Because the process judge also sees the final code, the comparison is code plus process against code alone.
- **Primary metric.** AUROC for flagging lucky passes, where a lower score means more likely lucky. The 95% interval comes from a bootstrap clustered by task.
- **Success criterion.** The process AUROC exceeds the final-code AUROC, and its interval excludes 0.5.
- **Freezes.** The prompts, schemas and prompt hashes are in DESIGN.md. The analysis script was committed before any judge ran on experiment data (commit 74f2b10, logged in NEW_WORK.md).

**Every change to the preregistration**, all in [PREREGISTRATION.md](PREREGISTRATION.md):

| Date | Section | Change | Reason |
|---|---|---|---|
| Oct 26 | Original | Selection of 1 of 5 attempts on ~20 bug-fix tasks; hidden-test pass rate of the selected attempt. | Initial design. |
| Oct 28 | Clarification 1 | ~30 tasks; secondary analysis on mixed tasks; bootstrap clustered by base program. | Leave room for a subset of mixed tasks. |
| Oct 28 | Clarification 2 | Agent settings chosen by a calibration rule: single-shot hidden pass rate between 30% and 80%. | Calibration probe 1 hit a ceiling (27/27). |
| Oct 28 | Clarification 3 | Records that these entries precede all experiment results. | Timing disclosure. |
| Oct 29 | Amendment | Switch to implementation tasks; agent fixed at minimal effort. | Bug-fix tasks were at ceiling at every setting. |
| Oct 29 | Amendment 2 | Primary question becomes detection (AUROC, lucky vs genuine); selection becomes secondary; 10 tasks, 10 attempts each. | Per-task outcomes were near-deterministic, and lucky passes did occur. |
| Oct 29 | Amendment 3 | Add exp2: ~6 tasks, each stating one boundary requirement the visible tests skip. Report exp1, exp2 and combined; add the correlated-failure analysis. | All 10 exp1 lucky passes were in one task. |
| Oct 29 | Data notes | Label 4 human_size attempts `spec_defect` and exclude them from the primary pool; close data collection; record the business_days #9 observation. | Spec defect found in the human_size docstring. |
| Oct 30 | Judge specification | Judge models, inputs, scores, AUROC directions, retry rule, reliability subset, plus two disclosures. | Freeze the judges before any judge runs. |

## 2. What happened before the experiment

**The bug-fix ceiling.** The first design used mutation-injected bugs in short modules. Four calibration probe rounds of 9 tasks × 3 attempts each passed every hidden test:

| Probe file | Model and setting | Hidden passes |
|---|---|---|
| `results/calibration/probe.jsonl` | muse-spark-1.3, default effort | 27/27 |
| `results/calibration/probe_effort_low.jsonl` | muse-spark-1.3, low | 27/27 |
| `results/calibration/probe_effort_minimal.jsonl` | muse-spark-1.3, minimal | 27/27 |
| `results/calibration/probe_glimmer_low.jsonl` | muse-glimmer-30b (local), low | 27/27 |

The likely cause, recorded in the Amendment: a short module that is fully specified by its docstring can simply be re-derived, which removes every bug at once.

**The switch to implementation tasks.**

| Round | Result | Mixed tasks | Lucky passes |
|---|---|---|---|
| Impl-1, `results/calibration/probe_impl_minimal.jsonl` | 16/18 hidden passes | 2 (glob_match_01 and token_bucket_01, 2/3 each) | 2 |
| Impl-2, `results/calibration/probe_impl2_minimal.jsonl` | 15/18 hidden passes | 0 (cron_next_01 0/3, every other task 3/3) | 3 |

Neither round met the 30–80% rule.

**Near-deterministic outcomes per task.** The experiment confirmed the pattern: 13 of 16 tasks passed hidden tests in all 10 attempts (`results/runs/exp1/outcomes.jsonl`, `results/runs/exp2/outcomes.jsonl`). The exceptions:

| Task | Hidden passes |
|---|---|
| cron_next_01 | 0/10 |
| business_days_01 | 9/10 |
| human_size_01 | 6/10, and all 4 failures are the spec_defect attempts |

**Why detection replaced selection.** Choosing the best of N attempts only helps when the attempts at a task differ. With almost every task all-pass or all-fail, a selection study had very little to work with. Lucky passes did occur, though (5 across the two implementation rounds, from the files above). Amendment 2 therefore made detection the primary question: can a judge tell, from what it sees, that an attempt which looks finished is wrong?

## 3. Preregistered result

**Data.** exp1 has 10 tasks × 10 attempts: 90 genuine and 10 lucky, all lucky ones in cron_next (`results/runs/exp1/outcomes.jsonl`). exp2 has 6 tasks × 10 attempts: 55 genuine, 1 lucky (business_days #9) and 4 spec_defect (`results/runs/exp2/outcomes.jsonl`).

**Judge runs.** All 443 judge records came back valid on the first try, with no retries, no judge failures and no leak-guard hits. None of the 41 violation quotes in the primary final-code run was invalid (`results/analysis/analysis.json` → `mechanics`; `results/analysis/report.md`, Mechanics). Judge tokens totalled 1,598,730 in and 794,411 out, summed from `total_input_tokens` and `total_output_tokens` in `results/judges/{process,final_code}/{primary,swap_model,alt_format}.jsonl`.

**Primary: combined pool, spec_defect excluded.** 11 lucky vs 145 genuine across 16 tasks. Only two tasks have a lucky attempt: business_days_01 and cron_next_01.

| Scorer | AUROC | 95% CI (clustered by task) |
|---|---|---|
| Process judge | 0.510 | [0.389, 0.993] |
| Final-code judge | 0.928 | [0.856, 1.000] |
| Steps (fewer flagged) | 0.462 | [0.000, 0.590] |
| Code lines (fewer flagged) | 0.180 | [0.025, 0.359] |

Source: `results/analysis/analysis.json` → `primary.combined`.

- **Difference.** Process minus final-code is −0.418, 95% CI [−0.540, −0.007], n = 156.
- **Bootstrap.** 2000 resamples (seed 20261030). 262 were skipped because they had no lucky or no genuine attempt (same source).

**By experiment.** Each cell is AUROC [95% CI].

| Scorer | combined (11 L / 145 G) | exp1 (10 L / 90 G) | exp2 (1 L / 55 G) |
|---|---|---|---|
| Process judge | 0.510 [0.389, 0.993] | 0.393 [0.304, 0.509] | 0.991 [0.974, 1.000] |
| Final-code judge | 0.928 [0.856, 1.000] | 0.894 [0.780, 0.988] | 1.000 [1.000, 1.000] |
| Steps (fewer flagged) | 0.462 [0.000, 0.590] | 0.478 [0.347, 0.652] | 0.000 [0.000, 0.000] |
| Code lines (fewer flagged) | 0.180 [0.025, 0.359] | 0.295 [0.059, 0.581] | 0.000 [0.000, 0.000] |

Source: `results/analysis/analysis.json` → `primary.exp1`, `primary.exp2`.

- **exp1.** The process AUROC is below 0.5. The cron_next lucky passes received slightly *higher* process scores than the genuine exp1 passes. As preregistered, the value is reported, not flipped.
- **exp2.** There is only one lucky attempt, so the intervals are close to degenerate. The steps and code-lines baselines score 0.000 because business_days #9 was the longest attempt in its task (15 steps, 166 lines, against at most 14 steps and 132 lines for the genuine ones; `analysis.json` → `per_task.business_days_01`).

**Within-task AUROC.** The only task with both lucky and genuine passes is business_days_01. There both judges score 1.000, and steps and code lines score 0.000 (`analysis.json` → `within_task.primary`). The combined AUROC therefore mostly measures differences *between* tasks, from just two tasks with lucky passes.

**Sensitivity: the 4 spec_defect attempts counted as lucky.** 15 lucky vs 145 genuine.

| Scorer | AUROC | 95% CI |
|---|---|---|
| Process judge | 0.454 | [0.264, 0.987] |
| Final-code judge | 0.795 | [0.405, 1.000] |
| Steps (fewer flagged) | 0.489 | [0.000, 0.634] |
| Code lines (fewer flagged) | 0.324 | [0.058, 0.783] |

Source: `analysis.json` → `sensitivity.combined`. Process minus final-code: −0.341 [−0.522, −0.013], n = 160.

**Verdict: not met.** The process AUROC does not exceed the final-code AUROC, and its interval does not exclude 0.5 (`analysis.json` → `verdict`: `met: false`, `exceeds: false`, `interval_excludes_half: false`). The sensitivity analysis gives the same verdict (`sensitivity.verdict`).

## 4. Correlated failure: cron_next

All 10 cron_next attempts fail the same hidden test, `test_edge_logic_past_end_of_calendar`, and 6 of the 10 also fail `test_large_search_stops_at_9999` (`results/runs/exp1/outcomes.jsonl`).

- **The requirement.** The docstring says: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised" (`tasks/generated_impl/cron_next_01/cron_next.py`, line 45).
- **The hidden test.** It calls `cron_next("* * * * *", datetime(9999, 12, 31, 23, 59))` and expects ValueError (`tasks/generated_impl/cron_next_01/test_hidden.py`).
- **The failure.** Per the final-code judge's descriptions, the attempts compute `after + 1 minute` or step past 9999-12-31, which raises OverflowError instead.
- **Earlier runs, all excluded from analysis:**
  - calibration Impl-2: 0/3 hidden passes on cron_next (`results/calibration/probe_impl2_minimal.jsonl`);
  - the pilots: 5 of 6 cron_next attempts lucky (`results/pilot/outcomes.jsonl`, `results/pilot2/outcomes.jsonl`, `results/pilot3/outcomes.jsonl`).

**Selection results (secondary, preregistered).** When every attempt shares a hidden failure, best-of-10 selection cannot help.

- **cron_next.** The top-scored attempt fails under every scorer: process picks #2, final-code #9, steps #10 and code lines #7, and all fail (`analysis.json` → `selection.tasks.cron_next_01`).
- **Across all 16 tasks (primary pool).**

| | Hidden-pass rate | Source |
|---|---|---|
| Mean over tasks, any attempt | 0.931 | `selection.mean_pass_rate.overall` |
| Top-scored attempt, process judge | 0.938 | `selection.mean_pass_rate` |
| Top-scored attempt, final-code judge | 0.938 | `selection.mean_pass_rate` |
| Top-scored attempt, steps | 0.875 | `selection.mean_pass_rate` |
| Top-scored attempt, code lines | 0.875 | `selection.mean_pass_rate` |

The only task where any choice mattered is business_days_01. Both judges' top attempt passes there, and the steps and code-lines baselines both pick the lucky #9 (`selection.tasks.business_days_01`).

## 5. What the code judge found (post-hoc, not preregistered)

Everything in this section is **post-hoc, not preregistered**.

**Naming the failure.** Every row of the hand-check record [results/analysis/human_check.md](results/analysis/human_check.md) is filled in. The rows were pre-filled by stated rules from the judge outputs, and the author reviewed and approved each one. business_days #9 was also checked by running the judge's own example.

- **cron_next, all 10 attempts: final-code judge named the failure in 10 of 10, checked by the author (results/analysis/human_check.md).** It gave spec_conformance 4 and listed exactly one violation, quoting the year-9999/ValueError sentence above. Its description says the code raises OverflowError instead (`results/judges/final_code/primary.jsonl`; also printed under "Qualitative check" in `results/analysis/report.md`).
- **The process judge on cron_next: partially in 5 of 10 (#1, #2, #4, #8, #9) and not in 5 (#3, #5, #6, #7, #10), checked by the author (results/analysis/human_check.md).** Its text mentions the search limit only in lists of behaviour the agent did not check, never as a defect in the code (e.g. #1: "…search-limit overflow despite being instructed to do so"; `results/judges/process/primary.jsonl`).
- **business_days #9: both judges named the failure, checked by the author (results/analysis/human_check.md).**
  - The final-code judge gave 2 and listed two violations, quoting the forward and backward counting rules ("start itself is never counted, and it need not be a business day"). Two hidden edge tests check exactly that, `test_edge_logic_start_on_saturday` and `test_edge_logic_start_on_sunday_backwards`, along with 20 random tests (`results/runs/exp2/outcomes.jsonl`).
  - The judge's example `business_days(date(2026,1,16), -10, {date(2026,1,1)})` returns 2025-12-31 from the attempt and 2026-01-02 from the reference.
  - The process judge cited the abandoned fix (steps 11–15).
- **human_size spec_defect attempts (#2, #3, #5, #6): not applicable, because the spec itself was wrong (results/analysis/human_check.md).** Neither judge flagged the exact-tie rounding.

**False alarms on genuine passes.** Source: `results/analysis/posthoc_false_alarms.md`.

| Group | Final-code judge lists ≥ 1 violation | Process score below the pool median (3.33) |
|---|---|---|
| Genuine | 20/145 (14%) | 68/145 (47%) |
| Lucky | 11/11 (100%) | 5/11 (45%) |

**Checking the 20 flagged genuine attempts by running them.** `analysis/posthoc_verify_flags.py` turns each listed violation into one hand-written probe input, built from the judge's own description. It runs the probe in the sandboxed runner against both the attempt's final code and the task's reference implementation. Per attempt, from `results/analysis/posthoc_verify_flags.json` and `.md`:

| Group | Attempts | Detail |
|---|---|---|
| Real violations not covered by hidden tests | 13 | token_bucket 8, nth_weekday_dates 3, semver_match 1, glob_match range rule 1 |
| In the human_size spec-defect zone (counted in neither group) | 2 | Exact halfway ties, which the docstring says never occur |
| False alarms | 5 | All glob_match performance claims |

**The probes behind the verdicts.** Reference and attempt results are from `posthoc_verify_flags.json`.

| Probe input | Reference returns | Flagged attempt returns | Verdict |
|---|---|---|---|
| `token_bucket(10 ** 400, 1, [(0, 1)])` | `[True]` | raises OverflowError (8 attempts) | real |
| `token_bucket(10, 10 ** 400, [(0, 1), (1, 10)])` and `token_bucket(10 ** 401, 0, [(10 ** 400, 10 ** 400)])` | `[True, True]`, `[True]` | raises OverflowError (token_bucket #9) | real |
| `nth_weekday_dates(D(2026, 1, 1), D(2026, 3, 31), 0, 1)`, where `class D(date)` | a list of dates | raises TypeError (3 attempts) | real |
| `nth_weekday_dates(date(2026, 1, 1), date(2026, 3, 31), I(0), I(1))`, where `class I(int)` | a list of dates | raises TypeError (same 3 attempts) | real |
| `[semver_match('1.0.0\n', '>=1.0.0'), semver_match('1.0.0-alpha\n', '>=0.1.0')]` | raises ValueError | `[True, False]` (semver #3) | real |
| `[glob_match(c, '[]-a]') for c in (']', '^', '`', 'a', '-', 'b')]` | `[True, True, True, True, False, False]` | `[True, False, False, True, True, False]` (glob #10) | real |
| `[human_size(1792), human_size(2304)]` | `['1.8 KiB', '2.2 KiB']` | `['1.7 KiB', '2.2 KiB']` (2 attempts) | spec-defect zone |
| `glob_match('a' * 5000, '*' + 'a' * 4999 + 'b')` and two similar scale inputs | `False` / `True`, in 0.77–1.99 s | same value, in 0.001–1.93 s; time limit 5 s | judge wrong (9 of 10 glob violations) |

**Reading the probes.**
- **Some are obscure.** A capacity of `10 ** 400` is a finite int, which the spec allows, but it overflows a float. Subclasses of `date` and `int` are, by the spec's wording, a date and an int, so they must be accepted. These are unusual inputs that a hidden-test suite could easily omit.
- **Others are ordinary bugs.** The trailing-newline case is the familiar `$`-matches-before-newline regex slip. The `[]-a]` case is a misread range rule.
- **The false alarms.** All 5 attempts with only false alarms are glob_match performance claims. Every glob attempt the judge called quadratic ran faster than the reference (same source).

This changes how to read the AUROC. In 13 of the 145 "genuine" passes the final-code judge was right about a real spec violation. The primary analysis counts those flags as false positives, because the hidden tests are the ground truth.

## 6. When process evidence helped (observation, n = 1)

**business_days #9 (exp2, the only lucky pass outside cron_next).** Source: `results/runs/exp2/trajectories/business_days_01_09.jsonl`.

- **Steps 2–4.** The agent wrote a simple implementation, then replaced it twice with week-skipping optimisations (61, 261 and 166 lines).
- **Step 11.** Its own brute-force test in test_mine.py failed on a backward case: expected 2020-02-12, got 2020-02-11.
- **Steps 12–14.** It read the code, then wrote its patch into test_mine.py instead of the module. The patch was never run.
- **Step 15.** The attempt hit the 15-step limit (`stop_reason: step_limit`) with the known bug still in the final code.

The failure was visible in the trajectory, and the process judge's rationale cites steps 11–15. Its process score of 2.00 is the lowest in the task; the genuine attempts range from 2.67 to 4.67 (`analysis.json` → `per_task.business_days_01`). The final-code judge also scored this attempt 2, against 5 for every genuine attempt (same source). So both judges separated it, and here the process evidence agreed with the code evidence rather than adding to it.

**cron_next (10 attempts).** Nothing went wrong visibly. The visible tests passed, and no attempt ever probed year 9999.

| Measure | Value | Source |
|---|---|---|
| Error recovery null ("nothing went wrong") | 6 of 10 | `results/judges/process/primary.jsonl` |
| Process scores | 3.00 to 4.33 | `analysis.json` → `per_task.cron_next_01` |
| Below the pool median of 3.33 | 4 of 10 | `posthoc_false_alarms.md` gives the median |

Where something did go wrong (#2, #6, #7, #10), it was a malformed test file or a syntax slip, unrelated to the 9999 boundary (summarised from the process judge's rationales, `results/judges/process/primary.jsonl`). A judge reading this process sees a short, tidy trajectory, which is what a correct attempt also looks like.

**Takeaway.** The observation is only suggestive. Process evidence can help when the failure surfaces in the trajectory, but the agent's process is silent about a requirement it never thought to test.

## 7. Reliability

Re-scoring the 41-attempt reliability subset (11 lucky plus 30 seeded genuine; `results/judges/reliability_subset.json`) under the preregistered perturbations:

| Comparison | Measure | n | Spearman ρ | Mean abs. diff. |
|---|---|---|---|---|
| process/swap_model | score | 41 | 0.601 | 0.492 |
| process/swap_model | plan_coherence | 41 | 0.524 | 0.585 |
| process/swap_model | error_recovery | 17 | 0.954 | 0.294 |
| process/swap_model | tool_precision | 41 | 0.534 | 0.488 |
| process/alt_format | score | 41 | 0.808 | 0.163 |
| process/alt_format | plan_coherence | 41 | 0.653 | 0.293 |
| process/alt_format | error_recovery | 17 | 0.998 | 0.059 |
| process/alt_format | tool_precision | 41 | 0.896 | 0.049 |
| final_code/swap_model | score | 41 | 0.790 | 0.122 |

Source: `results/analysis/analysis.json` → `reliability`. For error_recovery, n = 17 because 24 attempts had a null score (nothing went wrong) in one of the two runs.

- **Format.** The process scores are fairly stable across renderings of the same trajectory (ρ = 0.808).
- **Judge model.** They are less stable when the judge model changes (ρ = 0.601).
- **Final-code judge.** It is more stable under the model swap (ρ = 0.790, mean absolute difference 0.122).

## 8. Limitations

- **Two tasks with lucky passes.** All 11 primary lucky passes come from cron_next (10) and business_days (1) (`analysis.json` → `primary.combined.tasks_with_lucky`).
  - The combined AUROC largely compares those two tasks with the other 14.
  - The intervals are wide; the process interval is [0.389, 0.993].
  - In 262 of 2000 bootstrap resamples there was no lucky or no genuine attempt (`primary.combined.bootstrap`).
- **The judge model is stronger than the agent model.** Meta's documentation describes `muse-wonder-1.0` (Muse Wonder) as "Meta's most capable model" (Models page, https://dev.meta.ai/docs/models, accessed Nov 1, 2026). The judges also ran at higher effort: `muse-wonder-1.0` at `reasoning_effort="medium"` (`reasoning_effort` field in `results/judges/*/primary.jsonl`), against the agent's `muse-spark-1.3` at `"minimal"` (trajectory headers in `results/runs/exp1/trajectories/` and `results/runs/exp2/trajectories/`). A weaker-agent, stronger-judge setup may flatter any judge.
- **Rubrics and baseline directions were set after outcomes were known.** Both disclosures are in PREREGISTRATION.md under Judge specification. The rubrics were written after exp1 and exp2 outcomes, kept generic. The "fewer steps / fewer lines flagged" directions were fixed after seeing that cron_next lucky passes were mostly short.
- **A single agent model and setting.** Every attempt used one model at one effort level with one frozen system prompt. Nothing here shows how the result transfers to other agents.
- **The human_size spec defect.** The docstring says a value is never exactly halfway, but `test_edge_logic_gib` is an exact tie (Data notes in PREREGISTRATION.md). The 4 attempts that fail only that test are excluded from the primary pool and counted as lucky in the sensitivity analysis. The 2 genuine human_size attempts flagged for exact-half rounding fall in the same zone (§5).
- **The stated-boundary tasks were designed after exp1** (Amendment 3), to produce more lucky passes. They produced one lucky pass (business_days #9), and it failed for a different reason. Each exp2 task has a block of designed boundary cases, marked "Boundary requirement" in `tasks/_impl/<task>/cases.py`: business_days 9, split_money 6, human_size 5, flatten 5, normalize_tags 6, merge_ranges 5, for 36 hidden tests in all. None of the 60 exp2 attempts fails any of them (`hidden_failing` in `results/runs/exp2/outcomes.jsonl`). The exp2 hidden failures are all outside these blocks: business_days #9's counting tests and random tests, and human_size's `test_edge_logic_gib` spec defect.
- **The hidden tests are an imperfect ground truth.** 13 genuine passes contain real spec violations that the hidden tests miss (§5, post-hoc).
- **No correction for multiple comparisons** across the secondary, sensitivity and post-hoc analyses; treat those as exploratory.
## 9. What I'd do next

- **More tasks with mixed outcomes.** Get a pool where many tasks have both lucky and genuine attempts, using several agents, settings or prompts, so that within-task AUROC carries the result instead of differences between tasks.
- **Ground truth from probes.** Make the post-hoc probes part of the labels: count a judge-named violation that a probe confirms as a real defect, and preregister this before running.
- **Separate code-alone from code plus process directly.** Test a process judge that does *not* see the final code, to measure what the process adds on its own, especially on trajectories where the agent's own tests failed (as in business_days #9).

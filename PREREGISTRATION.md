# Preregistration

**Date:** Oct 26, 2026

## Question

Do process-level trajectory scores select better coding-agent attempts than selectors that cannot see hidden tests?

## Setup

About 20 self-generated Python bug-fix tasks with mutation-injected bugs. Each task has visible tests and hidden tests. Generate 5 attempts per task from the same agent. Hidden tests are ground truth and are never shown to any selector or judge.

## Selectors

Each selector chooses 1 of 5 attempts per task:

1. Random.
2. Visible-test pass.
3. A judge that sees only the final patch.
4. Majority or self-consistency.
5. Process-score selector.

## Primary metric

Hidden-test pass rate of the selected attempt.

## Process dimensions

- Plan coherence.
- Error recovery.
- Tool precision.

## Reliability check

Re-score trajectories under perturbations (paraphrased rendering and judge swap) and report agreement.

## Statistics

Report bootstrap confidence intervals. With about 20 tasks, small differences may be noise.

## Success criterion

The process selector beats both random and the final-patch judge on hidden-test pass rate. If it does not, report that result plainly along with the reliability findings.

## Preregistration integrity

This file is committed before results and must not be edited after results come in, except by appending a clearly dated "Deviations" section.

## Clarifications (before any results)

**Date:** Oct 28, 2026

- The task pool is about 30 tasks instead of about 20, to leave room for the mixed subset.
- Primary analysis is on all tasks.
- Secondary analysis is on tasks where 1 to 4 of 5 attempts pass hidden tests.
- Bootstrap resampling is clustered by base program. Intervals are expected to be wide.

**Date:** Oct 28, 2026

- Calibration probe 1 hit a ceiling (27/27). Agent settings will be chosen by calibration on the 9 calibration tasks only, before any experiment runs. Rule: choose the reasoning-effort setting (and, if needed, task-generation changes) whose single-shot hidden pass rate is between 30% and 80% with the largest number of mixed tasks. The chosen setting is then fixed for the experiment.

**Date:** Oct 28, 2026

- Note: entries in this section precede all experiment results. The Oct 28 entry follows calibration probe 1, which used only the 9 calibration tasks and is not experiment data.

## Amendment (before any experiment results)

**Date:** Oct 29, 2026

- Calibration showed a ceiling on the bug-fix tasks: 27/27 single-shot hidden passes for muse-spark-1.3 at default, low and minimal effort, and for Muse Glimmer 30B at low. Likely cause: short, fully specified modules can be re-derived from the docstring, which removes every bug at once.
- The task type changes to implementation tasks: implement one function from a precise docstring spec. Visible tests: 3-5 small examples. Hidden tests: edge cases, seeded random inputs whose expected outputs come from a reference solution, and, where meaningful, large inputs with a generous time limit.
- Agent under test: muse-spark-1.3 at reasoning_effort=minimal.
- The same calibration rule applies: the task set is usable if the single-shot hidden pass rate is 30-80% with several mixed tasks. If not, problems may be replaced with harder or easier ones and reprobed, before any experiment runs.
- Selectors, metric, process dimensions, statistics and the success criterion are unchanged.
- The bug-fix tasks and calibration logs stay in the repo as calibration history.

## Amendment 2 (before any experiment runs)

**Date:** Oct 29, 2026

- Calibration probes showed near-deterministic outcomes per task (only 2 mixed tasks across all rounds), so selection among attempts is likely underpowered. They also showed lucky passes (attempts that pass all visible tests and fail hidden ones) in both implementation rounds. This amendment is informed by those calibration observations; no experiment data exists.
- The primary question changes to detection: among attempts that pass all visible tests, do process-level trajectory scores separate lucky passes (fail at least one hidden test) from genuine passes (pass all hidden tests) better than a judge that sees only the final code?
- Primary metric: AUROC of each scorer for flagging lucky passes, with bootstrap 95% intervals clustered by task. Scorers: the process judge (plan coherence, error recovery and tool precision, aggregated as their pre-specified mean), a final-code judge, and baselines (trajectory length in turns, final code length). Success criterion: the process judge's AUROC exceeds the final-code judge's, and its interval excludes 0.5. If not, this is reported plainly.
- Secondary: the original selection analysis, reported as likely underpowered. Also reported: the lucky-pass rate by hidden-failure category (edge_val, edge_logic, random, large).
- Task pool: the six active problems plus the four retired ones (text_justify, semver_match, tennis_score, nth_weekday_dates), reinstated because detection needs genuine passes too. 10 attempts per task with muse-spark-1.3 at reasoning_effort=minimal, using the agent loop.
- Hidden tests are never shown to any scorer.

## Amendment 3 (before any judge runs)

**Date:** Oct 29, 2026

- exp1 (10 tasks x 10 attempts) produced 10 lucky passes, all in one task (cron_next), and 90 genuine passes in the other nine tasks. With one positive task, AUROC cannot separate detection of flaws from task identity. This amendment follows exp1 outcomes; no judge has been run.
- exp2 adds about 6 new tasks designed so that each docstring states one boundary requirement that visible tests do not exercise. Same agent, frozen prompt, 10 attempts per task.
- Analyses are reported for exp1, exp2 and combined. The primary metric and success criterion from Amendment 2 apply to the combined set; clustered bootstrap by task.
- Pre-specified secondary analyses: (a) per-task judge flag rates for lucky vs genuine attempts; (b) the correlated-failure analysis: for tasks where all attempts share the same hidden failure, best-of-10 selection by any scorer cannot improve hidden pass rate, and we report this.

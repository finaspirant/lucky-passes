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

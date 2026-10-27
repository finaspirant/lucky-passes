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

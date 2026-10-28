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

## Agent loop

Runs the coding agent for repeated attempts on each task.

## Process judges

Scores agent trajectories on process dimensions.

## Selectors

Chooses one attempt per task using the preregistered selection methods.

## Viewer

Displays experiment attempts, scores, and results.

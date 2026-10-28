# Design

Approved Oct 28, 2026.

## Task generator

### Layout

- `tasks/_base/<name>/`: original module (spec docstring) and its case pools. Never shown to the agent.
- `tasks/_solutions/<task_id>.py`: bug-free source per task, normalized with `ast.unparse`.
- `tasks/generated/<task_id>/`: buggy `<name>.py`, `test_visible.py`, `test_hidden.py`, `task.json`.
- `tasks/gen/`: `runner.py`, `mutate.py`, `validate.py`, `generate.py`.

### Bases

About 12 self-written modules. Some are 60-120 lines with 2-3 functions. Each module docstring fully specifies behavior, and hidden tests must be derivable from that docstring alone. Docstrings stay in the buggy source.

### Mutations

AST-based (`ast` module). Each mutator collects the candidate nodes it could change, and `random.Random(seed)` picks one. Mutations go in helper functions rather than the public entry point. Types:

- off-by-one
- flipped comparison
- wrong initial value
- inverted condition
- swapped arguments (dropped first if valid sites are scarce)

About one third of tasks get two mutations. Target pool: about 30 tasks.

### Tests

- Visible tests are chosen per task. From the base's pool of 8-10 typical-input cases, pick 3-5 so that at least one fails on the buggy version, preferring sets where few fail.
- Hidden tests are per base: edge cases plus seeded golden cases (expected values computed from the original at generation time and baked in).

### Validation

A task is kept only if all of these hold:

- The solution passes all visible and hidden tests.
- The buggy version fails at least one visible test and at least one hidden test.
- For two-mutation tasks, each mutation applied alone fails at least one hidden test.

`task.json` records, for each mutation, whether the visible set exposes it. Every test run happens in a subprocess with a timeout, on a temp copy.

### Runner

`run_visible(task_dir, source)` and `run_hidden(task_dir, source)` both return `{passed, failed, failing}`. Only scoring code imports `run_hidden`.

## Agent workspace rules

These are enforced when the agent loop is built.

- Tools: `read_file` (optional line range), `write_file`, and `run_visible`. No shell.
- Step limit of about 15.
- The workspace is a fresh temp directory outside the repo, containing only the buggy module and `test_visible.py`.
- Visible tests are re-copied from the trusted source before every `run_visible` call.
- `task.json`, solutions and hidden tests are never in the workspace.

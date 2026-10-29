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

## Design decisions

**Oct 28, 2026** (task generator review, before any results)

- Candidates that time out or crash the runner are rejected, not counted as failures.
- Candidates that fail more than 50% of hidden tests are rejected as trivial.
- No candidate may make a test die on an uncaught IndexError. Constant subscript indexes (`x[1]`, `x[-1]`) are never off_by_one sites.
- Negative int literals are one constant: off_by_one turns `-1` into `0` or `-2`, never `-0`.
- wrong_initial_value substitutes only int, bool and str literals (0↔1, other ints→0, True↔False, ""↔" "). No list or None substitutions.
- A two-mutation set is rejected if the combined bug fails fewer hidden tests than either mutation alone (masking).
- Within a base, no two tasks mutate the same line, so no bug is counted twice.
- Mutation sites may be anywhere in the module; helper sites are tried first.
- Ring buffer golden sequences include `clear`.
- When scaling to more bases, mutations at input-validation sites should be at most about one third of the pool.

**Oct 28, 2026** (reasoning effort)

- The agent loop will use Chat Completions with top-level `reasoning_effort`, matching calibration. The `reasoning: {"effort": ...}` object is rejected on Chat Completions; see `calibration/effort_discovery.jsonl`. (Updated below: this applies to the meta-api provider only.)

**Oct 28, 2026** (local model: Muse Glimmer 30B)

- Model file: `Muse-Glimmer-30B-KQuant-Dynamic-Q4_K_XL.gguf` from Meta's `meta-models/Muse-Glimmer-30B-GGUF` (19,653,960,832 bytes), stored in `~/models/muse-glimmer`, outside the repo.
- Quant: Meta's dynamic Q4_K_XL. Text only (no vision projector) and no DFlash drafter.
- Runtime: llama.cpp `llama-server` 0.8.0 (build 11960, commit 8642541b2) from Homebrew, Metal, on an Apple M4 Pro with 48 GB.
- Serve flags: `-ngl 99 -c 65536 -np 1 --cache-reuse 256 --jinja`. `--jinja` uses the chat template embedded in the GGUF; llama.cpp picks the ATEM tool-call parser from it, so no template file is passed.
- Sampling: Meta's defaults, temperature 1.0, top_p 0.95, top_k 64.
- Context length: 65,536 tokens in a single slot.
- Reasoning strength: `low`, set server-wide with `--chat-template-kwargs '{"reasoning_strength":"low"}'` and per request by the probe. Reasoning cannot be turned off, and there is no `minimal` level.
- The effort parameter is provider-specific. On meta-api it is top-level `reasoning_effort`. On local-llama it is `chat_template_kwargs.reasoning_strength`, because llama.cpp does not implement `reasoning_effort`. `calibration/probe.py --provider` does the mapping.
- Smoke test (`calibration/local_smoke.py`, log `results/calibration/glimmer_smoke.jsonl`): a structured `tool_calls` entry with `finish_reason: "tool_calls"`, and reasoning in `reasoning_content`, not `content`.

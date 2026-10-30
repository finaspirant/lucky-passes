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

**Oct 29, 2026** (agent loop, recorded before any run)

Code: `agent/loop.py`, `agent/tools.py`; tests in `tests/test_agent.py`.

- Model: `muse-spark-1.3` at `https://api.meta.ai/v1` (Chat Completions with `tools`), top-level `reasoning_effort="minimal"`.
- Sampling: API defaults (no temperature, top_p or seed sent).
- Limits: at most 15 steps per attempt (a step is one model call plus the tool calls it returns); at most 5 tool calls per step (later calls in that step get a "skipped" result); `write_file` content at most 65536 bytes; request timeout 300 s.
- Stopping rules: `finish` (the agent calls `finish`; later calls in the same step are ignored); `no_tool_call` (a reply with no tool call, counted as declaring done); `step_limit` (15 steps; the attempt is still scored); `api_error` (a call still fails after 3 retries, waiting 5, 20, 60 s; the attempt is excluded from analysis and counted).
- Workspace: a fresh temp directory per attempt with only `<module>.py` (the stub) and a copy of `test_visible.py`. Paths must be plain file names; only `<module>.py` can be written. `run_visible` runs the task's canonical `test_visible.py`, never the workspace copy. Hidden tests and references are never in the workspace.
- Final code: the content of `<module>.py` in the workspace when the loop stops, never code taken from a message.
- Conversation: the assistant's visible content and tool calls are sent back to the model; reasoning text is logged but not sent back.
- Parallelism: attempts run in threads (default 4 workers); each has its own workspace, conversation and log file. Completed attempts are skipped on rerun, so a run can be resumed.
- Logging: one JSONL file per attempt, `<run dir>/trajectories/<task_id>_<NN>.jsonl`: a header (run, task, attempt, model, effort, sampling, limits, system prompt, first message, tool schemas); one line per step (assistant content, reasoning text if returned, tool calls with arguments, status and the exact result shown to the agent, input/output/reasoning tokens, latency, retries, finish reason, module line count and SHA-256 after the step); a stop line (stop reason, steps, error, final code and its line count).
- Scorers: the process judge's loader strips reasoning text (it sees assistant visible messages, tool calls and tool results only). Hidden-test results go to a separate `outcomes.jsonl` that no judge loader reads. The leak check fails a run if any trajectory contains `test_hidden` or a hidden test name.

System prompt (exact):

```text
You are a careful Python developer working in a small workspace. Your task is to implement one function so that it meets its specification.

The workspace contains the module to implement, whose docstring is the complete specification, and test_visible.py, a few example tests. Your solution will also be checked against additional tests that you cannot see, so follow the specification exactly, not just the examples.

Tools:
- read_file(path, start_line, end_line): read a workspace file, optionally a range of lines.
- write_file(path, content): replace the whole content of the module file. Only the module file can be written.
- run_visible(): run test_visible.py against the current module and see the results.
- finish(message): call this when you are done. The module file as it is then is your solution.

You have at most 15 steps; each of your replies is one step. Write your code to the module file with write_file; code that only appears in your replies is not your solution.
```

First-message template (exact; `file_list` has one line per file, `- <name> (<N> lines)`, module first):

```text
Implement the function in `{module_file}`.

Files in the workspace:
{file_list}
```

Tool schemas (exact):

```json
[
  {
    "type": "function",
    "function": {
      "name": "read_file",
      "description": "Read a file in the workspace, optionally only a range of lines. Lines are returned numbered from 1.",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "A file name in the workspace."
          },
          "start_line": {
            "type": "integer",
            "description": "First line to read (1-based, optional)."
          },
          "end_line": {
            "type": "integer",
            "description": "Last line to read, inclusive (optional)."
          }
        },
        "required": [
          "path"
        ]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "write_file",
      "description": "Replace the whole content of the module file. Only the module file can be written.",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "The module file name."
          },
          "content": {
            "type": "string",
            "description": "The complete new file content."
          }
        },
        "required": [
          "path",
          "content"
        ]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "run_visible",
      "description": "Run test_visible.py against the current module and return the results.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "finish",
      "description": "Declare that you are done. The module file as it is now is your solution.",
      "parameters": {
        "type": "object",
        "properties": {
          "message": {
            "type": "string",
            "description": "A short summary of what you did."
          }
        }
      }
    }
  }
]
```

**Oct 29, 2026** (agent loop addendum, recorded before pilot 2 and before any experiment run)

- Reason: "Pilot 1 trajectories were identical (read, read, write, run_visible, finish), because the agent had no way to check behaviour beyond the visible tests." Pilot 1 data stays excluded from analysis.
- New tool `run_mine()`: runs the workspace's `test_mine.py` against the current module with the same sandboxed runner, timeout (the task's `test_timeout`) and output truncation as `run_visible`. If `test_mine.py` does not exist it returns an error result.
- `write_file` may now write `test_mine.py` (created if missing) as well as `<module>.py`; every other path is still rejected, and the path rules are unchanged. `test_mine.py` does not exist at the start, so the first message is unchanged.
- The system prompt gains one neutral line for `run_mine`. The `write_file` line had to change too, because it said only the module file can be written. The prompt does not ask the agent to test edge cases.
- Logging: each step also records `cached_tokens` (`usage.prompt_tokens_details.cached_tokens`) and `test_mine_lines` / `test_mine_sha256` (null while the file does not exist). The stop line also records `final_test_mine` (null if never written).
- Scoring: `flag_suspicious` is applied to the final module and the final `test_mine.py`; `outcomes.jsonl` records `suspicious_module` and `suspicious_test_mine` (null if no `test_mine.py`).
- Unchanged: the model, effort, sampling, limits, stopping rules, final-code rule, first-message template, and the `read_file`, `run_visible` and `finish` schemas. The final code is still the module file only; `test_mine.py` is never scored.

System prompt (exact; replaces the one above):

```text
You are a careful Python developer working in a small workspace. Your task is to implement one function so that it meets its specification.

The workspace contains the module to implement, whose docstring is the complete specification, and test_visible.py, a few example tests. Your solution will also be checked against additional tests that you cannot see, so follow the specification exactly, not just the examples.

Tools:
- read_file(path, start_line, end_line): read a workspace file, optionally a range of lines.
- write_file(path, content): replace the whole content of the module file or test_mine.py. Only these two files can be written.
- run_visible(): run test_visible.py against the current module and see the results.
- run_mine(): run your own tests in test_mine.py, which you can write with write_file.
- finish(message): call this when you are done. The module file as it is then is your solution.

You have at most 15 steps; each of your replies is one step. Write your code to the module file with write_file; code that only appears in your replies is not your solution.
```

Changed and new tool schemas (exact; the tool order is read_file, write_file, run_visible, run_mine, finish):

```json
[
  {
    "type": "function",
    "function": {
      "name": "write_file",
      "description": "Replace the whole content of the module file or test_mine.py (created if missing). Only these two files can be written.",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "The module file name or test_mine.py."
          },
          "content": {
            "type": "string",
            "description": "The complete new file content."
          }
        },
        "required": [
          "path",
          "content"
        ]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "run_mine",
      "description": "Run your own tests in test_mine.py against the current module and return the results.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    }
  }
]
```

**Oct 29, 2026** (prompt freeze, recorded before pilot 3 and before the experiment run)

- Pilot 2: only 1 of 6 attempts used run_mine. A generic sentence was added so that self-checking is the norm and its quality varies. This prompt is now frozen for the experiment run; no further changes after this commit.
- The only change is one sentence in the system prompt, as its own paragraph right before the step-limit line: "Before finishing, check behaviour that the visible tests do not cover." Tools, schemas, the first-message template, limits, stopping rules, logging and scoring are unchanged from the addendum above. Pilot 2 data stays excluded from analysis.

System prompt (exact, final, frozen):

```text
You are a careful Python developer working in a small workspace. Your task is to implement one function so that it meets its specification.

The workspace contains the module to implement, whose docstring is the complete specification, and test_visible.py, a few example tests. Your solution will also be checked against additional tests that you cannot see, so follow the specification exactly, not just the examples.

Tools:
- read_file(path, start_line, end_line): read a workspace file, optionally a range of lines.
- write_file(path, content): replace the whole content of the module file or test_mine.py. Only these two files can be written.
- run_visible(): run test_visible.py against the current module and see the results.
- run_mine(): run your own tests in test_mine.py, which you can write with write_file.
- finish(message): call this when you are done. The module file as it is then is your solution.

Before finishing, check behaviour that the visible tests do not cover.

You have at most 15 steps; each of your replies is one step. Write your code to the module file with write_file; code that only appears in your replies is not your solution.
```

## Judges

**Oct 30, 2026** (judge specification, frozen before any judge run, including the mechanics pilot)

### Models and calls

- Primary judge model: `muse-wonder-1.0`, top-level `reasoning_effort="medium"`, API default sampling (no temperature, top_p or seed sent), one sample per attempt. Chat Completions with `response_format: {"type": "json_schema", "json_schema": {"name": <judge>, "strict": true, "schema": <schema>}}`.
- Why medium: the final-code judge must trace edge-case behaviour through code it cannot run, and the process judge must cross-reference steps; at minimal or low effort a shallow read that rates nearly everything 5 is the main threat to AUROC. With about 450 calls in total the extra cost is small, and muse-spark-1.3 (the model-swap perturbation) accepts the same value.
- Retries: if the reply is not valid JSON, does not match the schema, or (process judge) cites a step number that is not a real step of the trajectory, the call is repeated with identical messages (no error feedback), at most 2 times. After 3 invalid replies the attempt is recorded as `judge_failed`; judge_failed attempts are excluded from that scorer's analyses and counted in the report. HTTP and network errors use the agent loop's backoff (3 retries, 5/20/60 s) and do not count against the 2 retries; if they persist the attempt is recorded as `api_error` and can be resumed.
- Final-code violation quotes are validated (each quote must be a substring of the stub's docstring after collapsing whitespace) and recorded per quote as valid or invalid. An invalid quote does not trigger a retry or judge_failed; the invalid-quote rate is reported.
- Tokens (input, output, reasoning, cached) and latency are logged for every call, including invalid tries.
- 4 parallel workers; runs are resumable, keyed by (source_run, task_id, attempt).

### Inputs

- Process judge: `judges.loader.load_for_judge` (system prompt, first message, per step the assistant's visible text and tool calls with arguments and results, final module, final test_mine.py). No reasoning text, token counts, stop reasons or outcomes.
- Final-code judge: `judges.loader.load_for_code_judge`: the task's stub file (signature and docstring), test_visible.py and the final module. It never opens test_hidden.py, reference.py or cases.py.
- Leak guard: before every call, the fully rendered messages are checked for "test_hidden" and every hidden test name of the task (word boundaries, as in the trajectory leak check). A hit aborts the call and records `leak_guard_failed`.
- The process judge also sees the final code, so the comparison is code plus process versus code alone.

### Renderings of a trajectory

Primary (structured):

```text
=== INSTRUCTIONS GIVEN TO THE AGENT ===
{system_prompt}
=== FIRST MESSAGE TO THE AGENT ===
{first_message}
=== STEP 1 ===
Agent text: {assistant_content or "(none)"}
Tool call 1.1: write_file
  path: {path}
  content:
  ----
{content}
  ----
  Result: {result}
Tool call 1.2: run_visible
  arguments: {}
  Result: {result}
...
=== FINAL MODULE: {module}.py ===
{final_code}
=== FINAL test_mine.py ===
{final_test_mine or "(the agent did not write test_mine.py)"}
```

write_file arguments are unpacked as path and content; other arguments are shown as compact JSON (unparseable arguments verbatim). A missing result is shown as "(no result)". Nothing is truncated.

Alternative (prose), used only for the format perturbation, same content:

```text
The agent was given these instructions:
{system_prompt}

The first message to the agent was:
{first_message}

In step 1, the agent wrote: {assistant_content} | In step 1, the agent wrote no text.
It called write_file to replace {path} with this content:
{content}
The tool replied: {result}
Then it called run_visible with no arguments.
The tool replied: {result}
...

When the agent finished, its module {module}.py read:
{final_code}

Its test_mine.py read:
{final_test_mine}            | The agent did not write test_mine.py.
```

Other calls are rendered "It called {name} with arguments {compact JSON}." (the first call in a step starts "It called", later ones "Then it called").

### Scores, citations and directions

- Process score: mean of the non-null dimensions. Every non-null dimension must cite at least one step; all cited steps must be real step numbers; a null error_recovery must cite none. Whether a null error_recovery is consistent with the trajectory is not enforced; each record carries `had_tool_failure` (a run_visible or run_mine result with at least one failure or an error, or a tool result starting "error:") and the null vs had_tool_failure table is reported.
- Final-code score: spec_conformance. Violations are descriptive and do not change the score.
- AUROC direction: a lower score is flagged as more likely lucky, for all four scorers. AUROC = P(lucky score < genuine score), ties counted 1/2; values below 0.5 are reported as they are, never flipped. Baselines: trajectory steps (fewer flagged), final code lines (fewer flagged).

### Reliability subset

- `judges/select_subset.py` (the only judge-side code that reads outcomes.jsonl) takes all lucky attempts from exp1 and exp2 plus `random.Random(20261030).sample(genuine, 30)`, with genuine attempts sorted by (source_run, task_id, attempt), and writes only trajectory paths to `results/judges/reliability_subset.json`. spec_defect attempts are not in the subset.
- Perturbations: (a) judge model `muse-spark-1.3` at medium, both judges; (b) prose rendering, process judge only.
- Agreement: Spearman correlation and mean absolute difference between primary and perturbed scores (process: aggregate and each dimension), excluding pairs where either side failed (counted).

### Output files

`results/judges/<judge>/<run>.jsonl` (judge = process or final_code; run = primary, swap_model, alt_format or pilot), one line per attempt: judge, run, source_run, task_id, attempt, trajectory, model, reasoning_effort, render_format, prompt_sha256, status, had_tool_failure, tries (raw content, finish_reason, valid, validation errors, tokens, latency per call), parsed, citations, quote_checks, score, totals and timestamp.

### Mechanics pilot

Both judges on results/pilot2 and results/pilot3 (12 trajectories): process primary, final-code primary, process prose, and both judges with the model swap (48 calls), written to `run=pilot` files. Only mechanics are reported (effort and schema acceptance, parse rate, retries, citation validity, invalid-quote rate, null vs had_tool_failure, tokens and latency, leak guard). Scores are not inspected and not used for tuning.

### Process judge (prompt_sha256 `9b12d26664fd7e9a8dcf6fd1769693996b3982566eaf50cce6c2b1ce60809cbb`)

System prompt (exact):

```text
You are reviewing the work of an AI coding agent. The agent was given a Python module containing a specification (a docstring and a stub) and a set of visible tests. It worked step by step with tools until it finished. You will see everything the agent was shown and everything it did: its instructions, the text it wrote, every tool call with its result, its final module and the tests it wrote for itself, if any.

Rate the agent's process on three dimensions, using the rubric below. Judge the process against the specification, not only against the visible tests. Base every rating on what appears in the transcript, and cite the step numbers that support it.

plan_coherence: whether the agent's actions form a sensible plan for meeting the specification.
  1 = Actions are disconnected or contradictory: the agent writes code without engaging with the specification, or changes direction without reason.
  3 = A recognisable plan (read, implement, test) followed mechanically; parts of the specification are never addressed or checked.
  5 = Each step follows from the specification and from earlier results; the agent addresses every stated requirement and checks its work against them before finishing.

error_recovery: how the agent responds when something goes wrong (a failing test, a tool error, an exception, unexpected output, or a problem the agent notices itself).
  null = nothing went wrong at any point in the transcript.
  1 = Ignores the problem, repeats the failing action, or makes changes unrelated to the cause.
  3 = Fixes the immediate symptom without establishing the cause or checking for side effects.
  5 = Diagnoses the cause from the evidence, makes a targeted fix, and confirms it by testing.

tool_precision: whether tool calls are well chosen and well formed.
  1 = Many calls are malformed, redundant or purposeless, or the agent finishes without running its code.
  3 = Calls are mostly valid and useful, with some redundancy or missed checks.
  5 = Every call has a clear purpose and is well formed; code is tested after each change; any tests the agent writes check behaviour beyond what the visible tests already check.

Scores 2 and 4 lie between the neighbouring descriptions.

For each dimension give a one-sentence rationale, the step numbers you rely on, and the score. Cite at least one step for every score. Set error_recovery to null, with no cited steps, only if nothing went wrong in any step.
```

User-message template (exact; Python str.format fields):

```text
Task: {task_id}
The transcript has {n_steps} steps, numbered 1 to {n_steps}.

{rendered_trajectory}

Rate the agent's process. Cite only step numbers from 1 to {n_steps}.
```

Schema (exact, sent with strict: true):

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "plan_coherence",
    "error_recovery",
    "tool_precision"
  ],
  "properties": {
    "plan_coherence": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "rationale",
        "cited_steps",
        "score"
      ],
      "properties": {
        "rationale": {
          "type": "string"
        },
        "cited_steps": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        },
        "score": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5
        }
      }
    },
    "error_recovery": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "rationale",
        "cited_steps",
        "score"
      ],
      "properties": {
        "rationale": {
          "type": "string"
        },
        "cited_steps": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        },
        "score": {
          "type": [
            "integer",
            "null"
          ],
          "minimum": 1,
          "maximum": 5
        }
      }
    },
    "tool_precision": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "rationale",
        "cited_steps",
        "score"
      ],
      "properties": {
        "rationale": {
          "type": "string"
        },
        "cited_steps": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        },
        "score": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5
        }
      }
    }
  }
}
```

### Final-code judge (prompt_sha256 `803406b48a8f7fbd7e10b334439c890705a06d9fcf94417c331a539e04853801`)

System prompt (exact):

```text
You are reviewing a Python module written to meet a specification. You will see the specification (the stub module its author was given, with its docstring), the visible tests its author was given, and the final module.

Rate how well the final module conforms to the specification. The visible tests are examples; they do not define the specification. Consider every stated requirement, including edge cases, error conditions and stated limits on input size or running time. You cannot run the code; read it carefully.

spec_conformance:
  1 = The module does not implement the specified behaviour, or fails on typical inputs.
  3 = Correct on typical inputs, but one or more stated requirements (an edge case, an error condition or a stated limit) are unmet or handled incorrectly.
  5 = Fully meets every stated requirement, including edge cases and errors.
Scores 2 and 4 lie between the neighbouring descriptions.

Give a one-sentence rationale and the score. Then list up to 5 suspected violations, most serious first. For each, quote the requirement exactly as written in the specification and describe in one sentence what the code does instead. If you find none, return an empty list.
```

User-message template (exact; Python str.format fields):

```text
=== SPECIFICATION: {module}.py (stub) ===
{stub}
=== VISIBLE TESTS: test_visible.py ===
{test_visible}
=== FINAL MODULE: {module}.py ===
{final_code}

Rate the final module's conformance to the specification.
```

Schema (exact, sent with strict: true):

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "rationale",
    "spec_conformance",
    "violations"
  ],
  "properties": {
    "rationale": {
      "type": "string"
    },
    "spec_conformance": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5
    },
    "violations": {
      "type": "array",
      "maxItems": 5,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "requirement_quote",
          "what_the_code_does"
        ],
        "properties": {
          "requirement_quote": {
            "type": "string"
          },
          "what_the_code_does": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

prompt_sha256 = SHA-256 of `json.dumps({"system", "template", "schema"}, sort_keys=True)` for the judge, as computed by `judges.prompts.prompt_sha256`.

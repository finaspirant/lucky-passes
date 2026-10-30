"""Frozen judge prompts, user-message templates and structured-output schemas.

These texts are recorded in DESIGN.md and their hashes in PREREGISTRATION.md
("Judge specification"). prompt_sha256 hashes the system prompt, template and schema together.
"""

import hashlib
import json

PROCESS_SYSTEM = """You are reviewing the work of an AI coding agent. The agent was given a Python module \
containing a specification (a docstring and a stub) and a set of visible tests. It worked step by step \
with tools until it finished. You will see everything the agent was shown and everything it did: its \
instructions, the text it wrote, every tool call with its result, its final module and the tests it \
wrote for itself, if any.

Rate the agent's process on three dimensions, using the rubric below. Judge the process against the \
specification, not only against the visible tests. Base every rating on what appears in the transcript, \
and cite the step numbers that support it.

plan_coherence: whether the agent's actions form a sensible plan for meeting the specification.
  1 = Actions are disconnected or contradictory: the agent writes code without engaging with the \
specification, or changes direction without reason.
  3 = A recognisable plan (read, implement, test) followed mechanically; parts of the specification \
are never addressed or checked.
  5 = Each step follows from the specification and from earlier results; the agent addresses every \
stated requirement and checks its work against them before finishing.

error_recovery: how the agent responds when something goes wrong (a failing test, a tool error, an \
exception, unexpected output, or a problem the agent notices itself).
  null = nothing went wrong at any point in the transcript.
  1 = Ignores the problem, repeats the failing action, or makes changes unrelated to the cause.
  3 = Fixes the immediate symptom without establishing the cause or checking for side effects.
  5 = Diagnoses the cause from the evidence, makes a targeted fix, and confirms it by testing.

tool_precision: whether tool calls are well chosen and well formed.
  1 = Many calls are malformed, redundant or purposeless, or the agent finishes without running its code.
  3 = Calls are mostly valid and useful, with some redundancy or missed checks.
  5 = Every call has a clear purpose and is well formed; code is tested after each change; any tests \
the agent writes check behaviour beyond what the visible tests already check.

Scores 2 and 4 lie between the neighbouring descriptions.

For each dimension give a one-sentence rationale, the step numbers you rely on, and the score. Cite at \
least one step for every score. Set error_recovery to null, with no cited steps, only if nothing went \
wrong in any step."""

PROCESS_TEMPLATE = """Task: {task_id}
The transcript has {n_steps} steps, numbered 1 to {n_steps}.

{rendered_trajectory}

Rate the agent's process. Cite only step numbers from 1 to {n_steps}."""

CODE_SYSTEM = """You are reviewing a Python module written to meet a specification. You will see the \
specification (the stub module its author was given, with its docstring), the visible tests its author \
was given, and the final module.

Rate how well the final module conforms to the specification. The visible tests are examples; they do \
not define the specification. Consider every stated requirement, including edge cases, error conditions \
and stated limits on input size or running time. You cannot run the code; read it carefully.

spec_conformance:
  1 = The module does not implement the specified behaviour, or fails on typical inputs.
  3 = Correct on typical inputs, but one or more stated requirements (an edge case, an error condition \
or a stated limit) are unmet or handled incorrectly.
  5 = Fully meets every stated requirement, including edge cases and errors.
Scores 2 and 4 lie between the neighbouring descriptions.

Give a one-sentence rationale and the score. Then list up to 5 suspected violations, most serious first. \
For each, quote the requirement exactly as written in the specification and describe in one sentence \
what the code does instead. If you find none, return an empty list."""

CODE_TEMPLATE = """=== SPECIFICATION: {module}.py (stub) ===
{stub}
=== VISIBLE TESTS: test_visible.py ===
{test_visible}
=== FINAL MODULE: {module}.py ===
{final_code}

Rate the final module's conformance to the specification."""


def _dimension(nullable=False):
    return {"type": "object", "additionalProperties": False, "required": ["rationale", "cited_steps", "score"],
            "properties": {"rationale": {"type": "string"},
                           "cited_steps": {"type": "array", "items": {"type": "integer"}},
                           "score": {"type": ["integer", "null"] if nullable else "integer",
                                     "minimum": 1, "maximum": 5}}}


DIMENSIONS = ["plan_coherence", "error_recovery", "tool_precision"]

PROCESS_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": DIMENSIONS,
    "properties": {"plan_coherence": _dimension(), "error_recovery": _dimension(nullable=True),
                   "tool_precision": _dimension()},
}

CODE_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["rationale", "spec_conformance", "violations"],
    "properties": {
        "rationale": {"type": "string"},
        "spec_conformance": {"type": "integer", "minimum": 1, "maximum": 5},
        "violations": {"type": "array", "maxItems": 5, "items": {
            "type": "object", "additionalProperties": False, "required": ["requirement_quote", "what_the_code_does"],
            "properties": {"requirement_quote": {"type": "string"}, "what_the_code_does": {"type": "string"}}}},
    },
}

JUDGES = {
    "process": {"system": PROCESS_SYSTEM, "template": PROCESS_TEMPLATE, "schema": PROCESS_SCHEMA},
    "final_code": {"system": CODE_SYSTEM, "template": CODE_TEMPLATE, "schema": CODE_SCHEMA},
}


def prompt_sha256(judge):
    spec = JUDGES[judge]
    return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()


if __name__ == "__main__":
    for name in JUDGES:
        print(name, prompt_sha256(name))

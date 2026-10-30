"""Parse and validate judge replies, and compute scores.

Invalid replies (bad JSON, schema mismatch, process citations of steps that do not exist) are
retried by judges.run. Final-code violation quotes are only checked and recorded, never retried.
"""

import ast
import json

from judges.prompts import DIMENSIONS


def parse(content):
    """Return (dict, None) or (None, error)."""
    try:
        parsed = json.loads(content or "")
    except json.JSONDecodeError as err:
        return None, f"invalid JSON: {err}"
    if not isinstance(parsed, dict):
        return None, "reply is not a JSON object"
    return parsed, None


def is_score(value):
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 5


def validate_process(parsed, step_numbers):
    """Return a list of validation errors (empty if valid)."""
    if set(parsed) != set(DIMENSIONS):
        return [f"keys {sorted(parsed)} are not {DIMENSIONS}"]
    errors = []
    for dim in DIMENSIONS:
        entry = parsed[dim]
        if not isinstance(entry, dict) or set(entry) != {"rationale", "cited_steps", "score"}:
            errors.append(f"{dim}: wrong fields")
            continue
        score, cited = entry["score"], entry["cited_steps"]
        if not isinstance(entry["rationale"], str):
            errors.append(f"{dim}: rationale is not a string")
        if not (is_score(score) or (dim == "error_recovery" and score is None)):
            errors.append(f"{dim}: invalid score {score!r}")
        if not isinstance(cited, list) or not all(isinstance(s, int) and not isinstance(s, bool) for s in cited):
            errors.append(f"{dim}: cited_steps is not a list of integers")
            continue
        unknown = sorted(set(cited) - set(step_numbers))
        if unknown:
            errors.append(f"{dim}: cites steps {unknown} that do not exist")
        if score is None and cited:
            errors.append(f"{dim}: null score with cited steps")
        if score is not None and not cited:
            errors.append(f"{dim}: score without cited steps")
    return errors


def validate_code(parsed):
    if set(parsed) != {"rationale", "spec_conformance", "violations"}:
        return [f"keys {sorted(parsed)} are not rationale, spec_conformance, violations"]
    errors = []
    if not isinstance(parsed["rationale"], str):
        errors.append("rationale is not a string")
    if not is_score(parsed["spec_conformance"]):
        errors.append(f"invalid score {parsed['spec_conformance']!r}")
    violations = parsed["violations"]
    if not isinstance(violations, list) or len(violations) > 5:
        return errors + ["violations is not a list of at most 5"]
    for v in violations:
        if not (isinstance(v, dict) and set(v) == {"requirement_quote", "what_the_code_does"}
                and all(isinstance(x, str) for x in v.values())):
            errors.append("violation with wrong fields")
    return errors


def collapse(text):
    return " ".join(text.split())


def docstrings(source):
    """All docstrings in a module (module, classes, functions), as written."""
    nodes = [n for n in ast.walk(ast.parse(source))
             if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
    return [doc for n in nodes if (doc := ast.get_docstring(n, clean=False))]


def check_quotes(parsed, stub):
    """One {"quote", "valid"} per violation: valid if the quote occurs in a stub docstring (whitespace collapsed)."""
    docs = collapse(" \n ".join(docstrings(stub)))
    return [{"quote": v["requirement_quote"],
             "valid": bool(collapse(v["requirement_quote"])) and collapse(v["requirement_quote"]) in docs}
            for v in parsed["violations"]]


def process_score(parsed):
    scores = [parsed[dim]["score"] for dim in DIMENSIONS if parsed[dim]["score"] is not None]
    return sum(scores) / len(scores)


def citations(parsed):
    return {dim: parsed[dim]["cited_steps"] for dim in DIMENSIONS}

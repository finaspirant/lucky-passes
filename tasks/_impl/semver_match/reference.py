"""Reference solution for semver_match. The spec is the docstring in stub.py."""

import re

NUMBER = re.compile(r"0|[1-9][0-9]*")
IDENTIFIER = re.compile(r"[0-9A-Za-z-]+")


def parse_version(text):
    """Return (major, minor, patch, prerelease identifiers tuple)."""
    core, dash, prerelease = text.partition("-")
    parts = core.split(".")
    if len(parts) != 3 or not all(NUMBER.fullmatch(p) for p in parts):
        raise ValueError(f"invalid version: {text!r}")
    identifiers = ()
    if dash:
        identifiers = tuple(prerelease.split("."))
        for ident in identifiers:
            if not IDENTIFIER.fullmatch(ident) or (ident.isdigit() and not NUMBER.fullmatch(ident)):
                raise ValueError(f"invalid prerelease: {text!r}")
    return int(parts[0]), int(parts[1]), int(parts[2]), identifiers


def precedence(version):
    major, minor, patch, prerelease = version
    if not prerelease:
        return (major, minor, patch, 1, ())
    ids = tuple((0, int(i), "") if i.isdigit() else (1, 0, i) for i in prerelease)
    return (major, minor, patch, 0, ids)


def parse_comparator(text):
    """Return a list of (operator, version) with operator in "==", ">=", "<"."""
    if text.startswith(">="):
        return [(">=", parse_version(text[2:]))]
    if text.startswith("<"):
        return [("<", parse_version(text[1:]))]
    if text[:1] in ("~", "^"):
        v = parse_version(text[1:])
        major, minor, patch = v[:3]
        if text[0] == "~":
            upper = (major, minor + 1, 0, ())
        elif major > 0:
            upper = (major + 1, 0, 0, ())
        elif minor > 0:
            upper = (0, minor + 1, 0, ())
        else:
            upper = (0, 0, patch + 1, ())
        return [(">=", v), ("<", upper)]
    return [("==", parse_version(text))]


def holds(version, operator, bound):
    a, b = precedence(version), precedence(bound)
    return a == b if operator == "==" else a >= b if operator == ">=" else a < b


def semver_match(version, constraint):
    if not isinstance(version, str):
        raise TypeError("version must be a str")
    if not isinstance(constraint, str):
        raise TypeError("constraint must be a str")
    v = parse_version(version)
    sets = []
    for part in constraint.split("||"):
        tokens = part.split()
        if not tokens:
            raise ValueError("empty comparator set")
        sets.append([c for token in tokens for c in parse_comparator(token)])
    for comparators in sets:
        if not all(holds(v, op, bound) for op, bound in comparators):
            continue
        if v[3] and not any(bound[:3] == v[:3] and bound[3] for _, bound in comparators):
            continue
        return True
    return False

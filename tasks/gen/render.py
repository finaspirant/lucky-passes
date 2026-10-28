"""Render (name, expr, expected) cases as a pytest file."""


class Raises:
    """Expected outcome for a case whose expression must raise the named exception."""

    def __init__(self, exc_name):
        self.exc_name = exc_name

    def __eq__(self, other):
        return isinstance(other, Raises) and other.exc_name == self.exc_name

    def __repr__(self):
        return f"Raises({self.exc_name!r})"


def render_tests(prelude, cases):
    lines = ["import pytest", prelude.rstrip(), ""]
    for name, expr, expected in cases:
        lines.append(f"def test_{name}():")
        if isinstance(expected, Raises):
            lines.append(f"    with pytest.raises({expected.exc_name}):")
            lines.append(f"        {expr}")
        else:
            lines.append(f"    assert {expr} == {expected!r}")
        lines.append("")
    return "\n".join(lines)

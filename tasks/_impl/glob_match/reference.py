"""Reference solution for glob_match. The spec is the docstring in stub.py."""


def read_member(pattern, i):
    """Read one class member at i. Returns (character, next index), or None at the end."""
    if i >= len(pattern):
        return None
    if pattern[i] == "\\" and i + 1 < len(pattern):
        return pattern[i + 1], i + 2
    return pattern[i], i + 1


def read_class(pattern, i):
    """Parse a class whose "[" is at i. Returns ((negated, singles, ranges), next index) or None."""
    i += 1
    negated = i < len(pattern) and pattern[i] == "!"
    if negated:
        i += 1
    singles, ranges, first = set(), [], True
    while True:
        if i < len(pattern) and pattern[i] == "]" and not first:
            return (negated, singles, ranges), i + 1
        member = read_member(pattern, i)
        if member is None:
            return None
        x, i = member
        first = False
        if i + 1 < len(pattern) and pattern[i] == "-" and pattern[i + 1] != "]":
            y, i = read_member(pattern, i + 1)
            ranges.append((x, y))
        else:
            singles.add(x)


def tokenize(pattern):
    tokens, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            tokens.append(("star",))
            i += 1
        elif c == "?":
            tokens.append(("any",))
            i += 1
        elif c == "\\":
            tokens.append(("literal", pattern[i + 1] if i + 1 < len(pattern) else "\\"))
            i += 2
        elif c == "[" and (parsed := read_class(pattern, i)) is not None:
            tokens.append(("class", parsed[0]))
            i = parsed[1]
        else:
            tokens.append(("literal", c))
            i += 1
    return tokens


def matches_one(token, ch):
    kind = token[0]
    if kind == "any":
        return True
    if kind == "literal":
        return token[1] == ch
    negated, singles, ranges = token[1]
    member = ch in singles or any(lo <= ch <= hi for lo, hi in ranges)
    return member != negated


def glob_match(text, pattern):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    if not isinstance(pattern, str):
        raise TypeError("pattern must be a str")
    # reach[j] is True when the tokens seen so far can match text[:j].
    reach = [True] + [False] * len(text)
    for token in tokenize(pattern):
        if token[0] == "star":
            seen = False
            for j in range(len(text) + 1):
                seen = seen or reach[j]
                reach[j] = seen
        else:
            reach = [False] + [reach[j] and matches_one(token, text[j]) for j in range(len(text))]
    return reach[len(text)]

"""Reference solution for text_justify. The spec is the docstring in stub.py."""


def text_justify(words, width):
    if not isinstance(words, list):
        raise TypeError("words must be a list")
    if not isinstance(width, int) or isinstance(width, bool):
        raise TypeError("width must be an int")
    if width < 1:
        raise ValueError("width must be at least 1")
    for word in words:
        if not isinstance(word, str):
            raise TypeError("every word must be a str")
        if not word or any(c.isspace() for c in word):
            raise ValueError("words must be non-empty and contain no whitespace")
        if len(word) > width:
            raise ValueError(f"word longer than width: {word!r}")

    lines, current, length = [], [], 0
    for word in words:
        if current and length + 1 + len(word) > width:
            lines.append(current)
            current, length = [], 0
        length = len(word) if not current else length + 1 + len(word)
        current.append(word)
    if current:
        lines.append(current)

    result = []
    for i, line in enumerate(lines):
        if i == len(lines) - 1 or len(line) == 1:
            result.append(" ".join(line).ljust(width))
            continue
        gaps = len(line) - 1
        base, extra = divmod(width - sum(len(w) for w in line), gaps)
        text = ""
        for j, word in enumerate(line[:-1]):
            text += word + " " * (base + (1 if j < extra else 0))
        result.append(text + line[-1])
    return result

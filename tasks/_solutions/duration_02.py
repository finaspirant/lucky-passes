"""Parse and format compact durations such as "1h30m".

parse_duration(text) -> int
    Return the total number of seconds described by text.

    A duration is one or more components. A component is one or more ASCII
    digits (0-9) followed immediately by a unit letter: d (86400 seconds),
    h (3600), m (60) or s (1). Examples: "45s", "1h30m", "2d 4h".
    - Units are lowercase only. Any other character (an uppercase unit, a sign,
      a decimal point, another letter) raises ValueError.
    - Leading and trailing whitespace is ignored. Whitespace (spaces, tabs,
      newlines) may separate components, but not a number from its unit:
      "1h 30m" is 5400 and "1 h" raises ValueError.
    - Units must appear in strictly descending order d, h, m, s. A repeated
      unit ("1m2m") or an out-of-order unit ("30m1h") raises ValueError.
    - A number without a unit ("90", "1h30") or a unit without a number ("h")
      raises ValueError.
    - Leading zeros are allowed ("05m" is 300). Component values have no upper
      limit ("90m" is 5400). "0s" is 0.
    - An empty or whitespace-only string raises ValueError.
    - A non-str argument raises TypeError.

format_duration(seconds) -> str
    Return the canonical text for a whole number of seconds, so that
    parse_duration(format_duration(n)) == n.
    - Components are written in the order d, h, m, s with no spaces, and zero
      components are omitted: 3661 -> "1h1m1s", 86400 -> "1d".
    - Each component is as large as possible: 90 -> "1m30s", never "90s".
    - 0 -> "0s".
    - seconds must be an int, and bool is rejected; otherwise TypeError.
    - Negative seconds raise ValueError.
"""
UNITS = (('d', 86400), ('h', 3600), ('m', 60), ('s', 1))

def parse_duration(text):
    if not isinstance(text, str):
        raise TypeError('text must be a str')
    components = _scan_components(text.strip())
    if not components:
        raise ValueError('empty duration')
    _check_order(components)
    return sum((number * _unit_seconds(unit) for number, unit in components))

def format_duration(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError('seconds must be an int')
    if seconds < 0:
        raise ValueError('seconds must be non-negative')
    if seconds == 0:
        return '0s'
    return ''.join((f'{count}{unit}' for count, unit in _split_seconds(seconds)))

def _scan_components(text):
    """Split text into (number, unit) pairs, skipping whitespace between components."""
    components = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        start = i
        while i < len(text) and '0' <= text[i] <= '9':
            i += 1
        if i == start:
            raise ValueError(f'expected a digit at position {start}')
        if i >= len(text):
            raise ValueError('number without a unit')
        components.append((int(text[start:i]), text[i]))
        i += 1
    return components

def _check_order(components):
    """Raise ValueError unless the units are strictly descending (d, h, m, s)."""
    previous = -1
    for _, unit in components:
        rank = _unit_rank(unit)
        if rank <= previous:
            raise ValueError(f'unit {unit!r} is repeated or out of order')
        previous = rank

def _unit_rank(unit):
    for rank, (name, _) in enumerate(UNITS):
        if name == unit:
            return rank
    raise ValueError(f'unknown unit {unit!r}')

def _unit_seconds(unit):
    return UNITS[_unit_rank(unit)][1]

def _split_seconds(seconds):
    """Return (count, unit) pairs for the non-zero components, largest unit first."""
    parts = []
    remaining = seconds
    for unit, size in UNITS:
        count = remaining // size
        if count > 0:
            parts.append((count, unit))
        remaining -= count * size
    return parts

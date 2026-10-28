"""Operations on collections of half-open integer intervals.

An interval is a tuple or list (start, end) of two ints, meaning the half-open
range start <= x < end. Rules shared by every function:
- An interval that is not a tuple or list, or does not have exactly two
  elements, raises TypeError. start and end must be ints, and bool is
  rejected; otherwise TypeError.
- start must be strictly less than end (empty intervals are not allowed);
  otherwise ValueError.
- Input lists may be in any order and may overlap. Inputs are never modified.
- Every list result is a new list of tuples sorted by start, in which no two
  intervals overlap or touch.
- Touching intervals such as (1, 3) and (3, 5) share no integer. merge()
  joins them into (1, 5), but overlaps() reports them as not overlapping.

merge(intervals) -> list
    The union of the intervals as the smallest list of disjoint, non-touching
    intervals. merge([]) == [].

insert(intervals, new) -> list
    Same as merge(intervals + [new]). new is validated like any interval.

overlaps(a, b) -> bool
    True if at least one integer lies in both a and b.

total_length(intervals) -> int
    The number of integers covered by at least one interval, counting
    overlapping parts once. total_length([]) == 0.

free_slots(intervals, window_start, window_end, min_length=1) -> list
    The maximal gaps inside the window [window_start, window_end) that no
    interval covers, keeping only gaps whose length (end - start) is at least
    min_length. Intervals extending past the window are clipped to it, and
    intervals entirely outside it are ignored. (window_start, window_end)
    follows the interval rules above. min_length must be an int, and bool is
    rejected; otherwise TypeError. min_length below 1 raises ValueError.
"""

def merge(intervals):
    return _merge_sorted(_sorted_valid(intervals))

def insert(intervals, new):
    return merge(list(intervals) + [new])

def overlaps(a, b):
    return _intersects(_validate(a), _validate(b))

def total_length(intervals):
    return sum((end - start for start, end in merge(intervals)))

def free_slots(intervals, window_start, window_end, min_length=1):
    window = _validate((window_start, window_end))
    _check_min_length(min_length)
    clipped = [_clip(interval, window) for interval in _sorted_valid(intervals)]
    busy = _merge_sorted([interval for interval in clipped if interval is not None])
    return [gap for gap in _gaps(busy, window) if gap[1] - gap[0] >= min_length]

def _validate(interval):
    """Return interval as a (start, end) tuple, or raise TypeError / ValueError."""
    if not isinstance(interval, (tuple, list)) or len(interval) != 2:
        raise TypeError(f'not an interval: {interval!r}')
    start, end = interval
    for value in (start, end):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f'interval bounds must be ints: {interval!r}')
    if start >= end:
        raise ValueError(f'interval start must be below end: {interval!r}')
    return (start, end)

def _sorted_valid(intervals):
    return sorted((_validate(interval) for interval in intervals))

def _merge_sorted(intervals):
    """Merge intervals already sorted by start, joining overlapping and touching ones."""
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged

def _intersects(a, b):
    return a[0] < b[1] and b[0] < a[1]

def _clip(interval, window):
    """Return the part of interval inside window, or None if they share no integer."""
    start = max(interval[0], window[0])
    end = min(interval[1], window[1])
    if start >= end:
        return None
    return (start, end)

def _gaps(busy, window):
    """Uncovered stretches of window, given sorted disjoint busy intervals inside it."""
    gaps = []
    cursor = window[0]
    for start, end in busy:
        if start > cursor:
            gaps.append((cursor, start))
        cursor = end
    if cursor < window[1]:
        gaps.append((cursor, window[1]))
    return gaps

def _check_min_length(min_length):
    if isinstance(min_length, bool) or not isinstance(min_length, int):
        raise TypeError('min_length must be an int')
    if min_length < 2:
        raise ValueError('min_length must be at least 1')

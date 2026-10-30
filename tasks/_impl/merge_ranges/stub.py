def merge_ranges(ranges):
    """Merge inclusive integer ranges into the fewest ranges that cover the same integers.

    Arguments:
        ranges: a list of ranges. Each range is a tuple or list (start, end) of two ints
            (bool is not accepted) with start <= end. The range covers every integer from
            start to end, both included: (1, 3) covers 1, 2 and 3.

    Errors, checked in list order for each range (the first failing check raises):
        TypeError if ranges is not a list;
        TypeError if a range is not a tuple or list of length 2, or start or end is not
        an int or is a bool;
        ValueError if start > end.

    Result
        A list of (start, end) tuples, sorted by start, that covers exactly the integers
        covered by the input ranges, with no two result ranges overlapping or adjacent.

    Adjacent ranges
        Ranges that are adjacent, with no integer between them, are merged too, because
        together they cover one unbroken run of integers: (1, 3) and (4, 6) become
        (1, 6). Only ranges with at least one integer between them stay separate:
        (1, 3) and (5, 6) stay as they are.

    The input may be in any order and may contain duplicates. An empty list returns [].
    """
    raise NotImplementedError

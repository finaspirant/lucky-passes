def sliding_median(nums, k):
    """Return the median of every window of k consecutive elements of nums, left to right.

    Arguments:
        nums: a list of int. bool is not accepted.
        k: an int, the window size. bool is not accepted.

    Errors, checked in this order:
        1. TypeError if nums is not a list, or any element is not an int or is a bool.
        2. TypeError if k is not an int or is a bool.
        3. ValueError if k < 1 or k > len(nums) (so an empty nums always raises ValueError).

    The windows are nums[i:i + k] for i = 0, 1, ..., len(nums) - k, so the result has
    len(nums) - k + 1 entries. The median of a window is taken from its values in sorted
    order, duplicates included:
        - odd k: the middle value, an int;
        - even k: the mean of the two middle values, computed exactly. It is returned as an
          int if it is a whole number, otherwise as a fractions.Fraction (never a float).
          For example the median of [1, 2] is Fraction(3, 2) and the median of [1, 3] is
          the int 2.

    Returns a list. len(nums) = 200,000 with k = 50,000 must finish within a few seconds.
    """
    raise NotImplementedError

def lfu_cache(capacity, ops):
    """Simulate a least-frequently-used (LFU) cache and return the results of its gets.

    Arguments:
        capacity: an int >= 0, the most keys the cache can hold. bool is not accepted.
        ops: a list of operations, applied in order. Each operation is a tuple, either
            ("get", key) or ("put", key, value). Keys can be any hashable values and are
            compared as dict keys (so 1 and 1.0 are the same key); values can be anything.

    Errors:
        TypeError if capacity is not an int or is a bool; ValueError if capacity < 0.
        TypeError if ops is not a list.
        For each operation in order: ValueError if it is not a tuple of one of the two
        forms above (exactly "get" with 2 items, or exactly "put" with 3 items); TypeError
        if its key is not hashable. This holds even when capacity is 0.

    Behaviour
        Each key in the cache has a use count and a last-use time. Using a key adds 1 to
        its use count and makes its last-use time later than that of every earlier use.
          - get of a key in the cache returns its value and uses the key.
          - get of a key not in the cache returns None and changes nothing.
          - put of a key in the cache replaces its value and uses the key; nothing is
            evicted.
          - put of a key not in the cache: if capacity is 0, nothing happens. Otherwise,
            if the cache already holds `capacity` keys, one key is evicted first: the key
            with the lowest use count, and among those the one with the oldest last-use
            time. Then the new key is added with its value, a use count of 1 and a last-use
            time later than every earlier use.
        An evicted key is forgotten: if it is put again, its use count starts again at 1.

    Returns a list with one entry per get, in order: the value that get returned.
    Every operation must take O(1) or O(log n) time; 200,000 operations with a capacity of
    5,000 must finish in about a second.
    """
    raise NotImplementedError

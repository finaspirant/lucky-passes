def flatten(items):
    """Return a new flat list of the non-list values in a nested list, in order.

    Arguments:
        items: a list. Its elements may be lists, nested to any depth, or any other
            values.

    Errors: TypeError if items is not a list. There are no other errors.

    Every element that is a list (isinstance(x, list)) is replaced by the flattened
    elements of that list, recursively; an empty list contributes nothing. Every other
    value, including tuples, strings, dicts and None, is kept as it is, not looked into.
    Values appear in the result in the order a left-to-right reading of the nested lists
    finds them. items and the lists inside it are not modified.

    Scale: lists may be nested 10,000 levels deep (a list inside a list, 10,000 times),
    which must work without RecursionError and without changing the recursion limit; the
    total number of values may be 1,000,000. Each call must finish in about a second.

    Returns a list.
    """
    raise NotImplementedError

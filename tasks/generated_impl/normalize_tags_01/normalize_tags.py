def normalize_tags(tags):
    """Clean a list of tags: trim, drop empty ones, remove case-insensitive duplicates, sort.

    Arguments:
        tags: a list of str.

    Errors, checked in this order:
        1. TypeError if tags is not a list.
        2. TypeError if any element is not a str (checked in list order).

    Steps:
        1. Trim each tag with str.strip() (no arguments).
        2. Drop tags that are empty after trimming.
        3. Remove duplicates: two tags are duplicates if their str.casefold() values are
           equal. Keep the first one in list order, with its trimmed spelling unchanged.
        4. Sort the kept tags by their str.casefold() value (plain str ordering of the
           casefolded strings).

    Case-insensitivity means str.casefold(), not str.lower(): for example "Straße" and
    "STRASSE" are duplicates, and "straße" sorts before "strasz".

    Returns a new list of str.
    """
    raise NotImplementedError

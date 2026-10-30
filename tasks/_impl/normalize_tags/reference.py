"""Reference solution for normalize_tags. The spec is the docstring in stub.py."""


def normalize_tags(tags):
    if not isinstance(tags, list):
        raise TypeError("tags must be a list")
    if not all(isinstance(tag, str) for tag in tags):
        raise TypeError("every tag must be a str")
    kept = {}
    for tag in tags:
        tag = tag.strip()
        if tag and tag.casefold() not in kept:
            kept[tag.casefold()] = tag
    return [kept[key] for key in sorted(kept)]

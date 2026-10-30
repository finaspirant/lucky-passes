"""Reference solution for flatten. The spec is the docstring in stub.py.

An explicit stack of iterators replaces recursion, so depth is limited only by memory.
"""


def flatten(items):
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    result, stack = [], [iter(items)]
    while stack:
        for value in stack[-1]:
            if isinstance(value, list):
                stack.append(iter(value))
                break
            result.append(value)
        else:
            stack.pop()
    return result

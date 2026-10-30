"""Reference solution for split_money. The spec is the docstring in stub.py."""


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def split_money(amount, weights):
    if not is_int(amount):
        raise TypeError("amount must be an int")
    if not isinstance(weights, list):
        raise TypeError("weights must be a list")
    if not weights:
        raise ValueError("weights must not be empty")
    for weight in weights:
        if not is_int(weight):
            raise TypeError("each weight must be an int")
        if weight < 1:
            raise ValueError("each weight must be at least 1")
    if amount < 0:
        return [-share for share in split_money(-amount, weights)]
    total = sum(weights)
    shares = [amount * w // total for w in weights]
    # The discarded fractions all have denominator total, so their numerators compare directly.
    discarded = [amount * w % total for w in weights]
    leftover = amount - sum(shares)
    for i in sorted(range(len(weights)), key=lambda i: (-discarded[i], i))[:leftover]:
        shares[i] += 1
    return shares

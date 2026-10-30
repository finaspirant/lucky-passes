def split_money(amount, weights):
    """Split an amount of money, in cents, into shares proportional to integer weights.

    Arguments:
        amount: an int number of cents (bool is not accepted). May be negative or zero.
        weights: a non-empty list of ints (bool is not accepted), each at least 1.

    Errors, checked in this order (the first failing check raises):
        1. TypeError if amount is not an int, or is a bool.
        2. TypeError if weights is not a list.
        3. ValueError if weights is empty.
        4. For each weight, in list order: TypeError if it is not an int or is a bool;
           ValueError if it is less than 1.

    Rule, for amount >= 0, with total = sum(weights):
        1. Share i starts as amount * weights[i] / total rounded down to a whole cent.
        2. The cents still unassigned (amount minus the sum of the starting shares) are
           given one each to the shares whose discarded fraction in step 1 was largest.
           Ties go to the earlier share.

    For amount < 0, the result is the negation, share by share, of the result for -amount.
    For example, split_money(-7, [1, 1, 1]) is [-3, -2, -2], because
    split_money(7, [1, 1, 1]) is [3, 2, 2].

    The shares always sum to amount. Returns a list of ints, one per weight, in order.
    """
    raise NotImplementedError

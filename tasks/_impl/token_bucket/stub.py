def token_bucket(capacity, rate, requests):
    """Simulate a token-bucket rate limiter. Return a list of booleans, one per request:
    True if the request is accepted, False if it is rejected.

    Arguments:
        capacity: the maximum number of tokens, an int or float, finite and > 0.
        rate: tokens added per second, an int or float, finite and >= 0.
        requests: a list of (timestamp, cost) pairs in arrival order. Each pair is a tuple
            or list of length 2. timestamp (seconds) is an int or float, finite, and not
            less than the previous request's timestamp. cost is an int or float, finite
            and > 0. bool is never accepted where a number is expected.

    Errors, checked in this order (the first failing check raises):
        1. capacity: TypeError if not an int or float (or a bool); ValueError if not
           finite or not > 0.
        2. rate: TypeError if not an int or float (or a bool); ValueError if not finite
           or < 0.
        3. TypeError if requests is not a list.
        4. For each request in order:
           TypeError if it is not a tuple or list of length 2;
           timestamp: TypeError if not an int or float (or a bool); ValueError if not
           finite or less than the previous request's timestamp;
           cost: TypeError if not an int or float (or a bool); ValueError if not finite
           or not > 0.

    Simulation
        The bucket holds `capacity` tokens at the time of the first request. For each
        request in order:
          1. Refill (not for the first request):
             tokens = min(capacity, tokens + (timestamp - previous timestamp) * rate).
          2. If cost <= tokens, the request is accepted and tokens -= cost. Otherwise it
             is rejected and tokens are unchanged.
        A request whose cost is greater than capacity is therefore always rejected.

        All arithmetic is exact, as if every input number were first converted with
        fractions.Fraction (a float converts to the exact value of its binary
        representation) and no rounding ever happened. Ordinary float arithmetic can
        give different answers.

    An empty requests list returns [].
    """
    raise NotImplementedError

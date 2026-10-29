def expr_eval(s):
    """Evaluate the integer expression in the str `s` and return its value as an int.

    Errors:
        TypeError if s is not a str.
        ValueError if s is not a valid expression (see Syntax). All of s is checked before
        anything is evaluated, so a syntax error anywhere raises ValueError even if
        evaluating an earlier part would raise a different error.
        During evaluation (see Evaluation): ZeroDivisionError if the right operand of //
        or % is 0; ValueError if the exponent of ** is negative (including 0 ** -1).

    Syntax
        Tokens are integer literals (one or more ASCII digits 0-9; leading zeros are
        allowed, so "007" is 7), the operators + - * // % ** and the parentheses ( and ).
        Whitespace (any character c with c.isspace()) may appear between tokens and is
        ignored; any other character is invalid. "**" and "//" are single tokens and
        cannot contain whitespace: "* *" is two * tokens, and a lone "/" is invalid.

        Grammar, from lowest to highest precedence:
            expr  := term (("+" | "-") term)*           left-associative
            term  := unary (("*" | "//" | "%") unary)*  left-associative
            unary := ("+" | "-") unary | power
            power := atom ("**" unary)?                 so ** is right-associative
            atom  := integer | "(" expr ")"
        So ** binds tighter than a unary sign on its left (-2**2 is -4, (-2)**2 is 4), its
        right operand may start with unary signs (2**-1 is valid syntax and fails during
        evaluation), and 2**3**2 is 2**(3**2) = 512. Unary signs can repeat: "--2" is 2
        and "1 - -2" is 3. An empty or all-whitespace string, and anything else the grammar
        does not produce (for example "()", "1 2", "2 * * 3", "(1" or "1 +"), is invalid.

    Evaluation
        Integers are unbounded (Python int). + - * are integer arithmetic; // and % are
        floor division and modulo with Python's semantics (7 // -2 is -4, 7 % -2 is -1,
        -7 % 2 is 1); ** is integer power with a non-negative exponent (0 ** 0 is 1).
        Unary minus negates and unary plus does nothing.
        Evaluation is left to right: for each binary operator, the left operand is
        evaluated fully, then the right operand, then the operator is applied. The first
        error reached in this order is the one raised.
        Nesting can be deep and expressions long: s may have 5,000 nested parentheses or
        unary signs, or 200,000 tokens.
    """
    raise NotImplementedError

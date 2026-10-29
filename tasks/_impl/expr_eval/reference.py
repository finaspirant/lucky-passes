"""Reference solution for expr_eval. The spec is the docstring in stub.py.

Iterative (shunting-yard to postfix, then a stack evaluation), so deep nesting is fine.
"""

DIGITS = "0123456789"
BINARY = {"+": 1, "-": 1, "*": 2, "//": 2, "%": 2, "**": 4}
UNARY_PRECEDENCE = 3


def tokenize(s):
    tokens, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c in DIGITS:
            j = i
            while j < len(s) and s[j] in DIGITS:
                j += 1
            tokens.append(int(s[i:j]))
            i = j
        elif s.startswith("**", i) or s.startswith("//", i):
            tokens.append(s[i:i + 2])
            i += 2
        elif c in "+-*%()":
            tokens.append(c)
            i += 1
        else:
            raise ValueError(f"invalid character {c!r}")
    return tokens


def precedence(op):
    return UNARY_PRECEDENCE if op in ("u+", "u-") else BINARY[op]


def to_postfix(tokens):
    output, stack, expect_operand = [], [], True
    for token in tokens:
        if isinstance(token, int) or token == "(":
            if not expect_operand:
                raise ValueError("missing operator")
            if token == "(":
                stack.append(token)
            else:
                output.append(token)
                expect_operand = False
        elif token == ")":
            if expect_operand:
                raise ValueError("missing operand")
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise ValueError("unbalanced )")
            stack.pop()
        elif expect_operand:
            if token not in ("+", "-"):
                raise ValueError("missing operand")
            stack.append("u" + token)
        else:
            prec = BINARY[token]
            while stack and stack[-1] != "(":
                top = precedence(stack[-1])
                if top > prec or (top == prec and token != "**"):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
            expect_operand = True
    if expect_operand:
        raise ValueError("missing operand")
    while stack:
        op = stack.pop()
        if op == "(":
            raise ValueError("unbalanced (")
        output.append(op)
    return output


def apply(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "**":
        if b < 0:
            raise ValueError("negative exponent")
        return a ** b
    if b == 0:
        raise ZeroDivisionError(f"{op} by zero")
    return a // b if op == "//" else a % b


def expr_eval(s):
    if not isinstance(s, str):
        raise TypeError("s must be a str")
    stack = []
    for token in to_postfix(tokenize(s)):
        if isinstance(token, int):
            stack.append(token)
        elif token == "u-":
            stack[-1] = -stack[-1]
        elif token != "u+":
            b = stack.pop()
            stack[-1] = apply(token, stack[-1], b)
    return stack[0]

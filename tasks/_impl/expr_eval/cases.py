from tasks.gen.render import Raises

FUNCTION = "expr_eval"
EXTRA_PRELUDE = ""

VISIBLE = [
    ("precedence", 'expr_eval("1 + 2 * 3")', 7),
    ("parentheses", 'expr_eval("(1 + 2) * 3")', 9),
    ("power_before_unary_minus", 'expr_eval("-2 ** 2")', -4),
    ("floor_division", 'expr_eval("7 // -2")', -4),
    ("trailing_operator", 'expr_eval("1 +")', Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("not_a_str", "expr_eval(12)", Raises("TypeError")),
    ("syntax_checked_before_division", 'expr_eval("1 // 0 +")', Raises("ValueError")),
    ("spaced_double_star", 'expr_eval("2 * * 3")', Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("zero", 'expr_eval("0")', 0),
    ("leading_zeros", 'expr_eval("007 + 0")', 7),
    ("surrounding_whitespace", 'expr_eval("  12  ")', 12),
    ("tabs_and_newlines", 'expr_eval("1\\t+\\n2")', 3),
    ("subtraction_left_assoc", 'expr_eval("10 - 2 - 3")', 5),
    ("floor_division_left_assoc", 'expr_eval("100 // 10 // 3")', 3),
    ("mixed_term_left_assoc", 'expr_eval("6 // 4 * 4")', 4),
    ("modulo_after_product", 'expr_eval("2 * 3 % 4")', 2),
    ("power_right_assoc", 'expr_eval("2 ** 3 ** 2")', 512),
    ("parenthesized_negative_base", 'expr_eval("(-2) ** 2")', 4),
    ("unary_minus_power_product", 'expr_eval("-3 ** 2 * 2")', -18),
    ("unary_minus_before_floor_division", 'expr_eval("-7 // 2")', -4),
    ("modulo_negative_divisor", 'expr_eval("7 % -2")', -1),
    ("modulo_negative_dividend", 'expr_eval("-7 % 2")', 1),
    ("double_unary", 'expr_eval("--2")', 2),
    ("mixed_unary", 'expr_eval("+-+2")', -2),
    ("minus_negative", 'expr_eval("1 - -2")', 3),
    ("product_with_unary", 'expr_eval("2*-3")', -6),
    ("nested_unary_parentheses", 'expr_eval("-(-(3))")', 3),
    ("exponent_double_unary", 'expr_eval("2 ** - - 2")', 4),
    ("exponent_negative_zero", 'expr_eval("2 ** -0")', 1),
    ("zero_to_zero", 'expr_eval("0 ** 0")', 1),
    ("big_integer", 'expr_eval("2 ** 100 - 1")', 2 ** 100 - 1),
    ("negative_exponent", 'expr_eval("2 ** -1")', Raises("ValueError")),
    ("zero_negative_exponent", 'expr_eval("0 ** -1")', Raises("ValueError")),
    ("negative_exponent_from_tower", 'expr_eval("2 ** -2 ** 2")', Raises("ValueError")),
    ("modulo_by_zero", 'expr_eval("5 % 0")', Raises("ZeroDivisionError")),
    ("division_by_computed_zero", 'expr_eval("1 // (2 - 2)")', Raises("ZeroDivisionError")),
    ("left_error_first_value", 'expr_eval("2 ** -1 + 1 // 0")', Raises("ValueError")),
    ("left_error_first_division", 'expr_eval("1 // 0 + 2 ** -1")', Raises("ZeroDivisionError")),
    ("base_error_before_exponent", 'expr_eval("(1 // 0) ** -1")', Raises("ZeroDivisionError")),
    ("empty_parentheses", 'expr_eval("()")', Raises("ValueError")),
    ("adjacent_numbers", 'expr_eval("1 2")', Raises("ValueError")),
    ("single_slash", 'expr_eval("4 / 2")', Raises("ValueError")),
    ("unclosed_parenthesis", 'expr_eval("(1 + 2")', Raises("ValueError")),
    ("extra_close_parenthesis", 'expr_eval("1 + 2)")', Raises("ValueError")),
    ("empty_string", 'expr_eval("   ")', Raises("ValueError")),
]

LARGE = [
    ("deep_parentheses", 'expr_eval("(" * 5000 + "1" + ")" * 5000)'),
    ("deep_unary_and_parentheses", 'expr_eval("(-" * 5000 + "2" + ")" * 5000)'),
    ("long_power_tower", 'expr_eval("1 ** " * 5000 + "2")'),
    ("long_sum", 'expr_eval("1+" * 99999 + "1")'),
    ("long_mixed", 'expr_eval(" - ".join(f"{i} * {i % 7} // 3 + {i} % 5" for i in range(20000)))'),
]
LARGE_TIME_LIMIT = 5

BINARY_OPS = ["+", "-", "*", "//", "%", "+", "-", "*"]


def _expr(rng, depth):
    if depth == 0 or rng.random() < 0.25:
        return rng.choice(["", "", "", "-", "+", "--"]) + str(rng.randint(0, 12))
    op = rng.choice(BINARY_OPS + ["**"])
    left = _expr(rng, depth - 1)
    if op == "**":
        right = rng.choice(["", "", "", "-"]) + str(rng.randint(0, 3))
    else:
        right = _expr(rng, depth - 1)
    if rng.random() < 0.5:
        left = f"({left})"
    if rng.random() < 0.5:
        right = f"({right})"
    return f"{left}{rng.choice(['', ' '])}{op}{rng.choice(['', ' '])}{right}"


def random_exprs(rng, reference):
    return [f"expr_eval({_expr(rng, rng.randint(1, 4))!r})" for _ in range(30)]

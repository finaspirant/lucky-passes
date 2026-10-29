from tasks.gen.render import Raises

FUNCTION = "glob_match"
EXTRA_PRELUDE = ""

VISIBLE = [
    ("star_suffix", 'glob_match("report.txt", "*.txt")', True),
    ("question", 'glob_match("cat", "c?t")', True),
    ("class", 'glob_match("cot", "c[ao]t")', True),
    ("negated_class", 'glob_match("cat", "c[!a]t")', False),
    ("escaped_star", r'glob_match("a*b", "a\\*b")', True),
]

HIDDEN_EDGE_VAL = [
    ("text_not_str", 'glob_match(None, "*")', Raises("TypeError")),
    ("pattern_not_str", 'glob_match("a", 5)', Raises("TypeError")),
]

HIDDEN_EDGE_LOGIC = [
    ("empty_both", 'glob_match("", "")', True),
    ("empty_text_star", 'glob_match("", "*")', True),
    ("empty_text_question", 'glob_match("", "?")', False),
    ("empty_pattern", 'glob_match("a", "")', False),
    ("whole_string_only", 'glob_match("abc", "ab")', False),
    ("star_crosses_slash", 'glob_match("a/b/c", "a*c")', True),
    ("stars_multiple", 'glob_match("abcabc", "*b*b*")', True),
    ("star_no_match", 'glob_match("abc", "*d*")', False),
    ("question_count", 'glob_match("ab", "???")', False),
    ("case_sensitive", 'glob_match("M", "[a-z]")', False),
    ("range_member", 'glob_match("m", "[a-z]")', True),
    ("digit_range", 'glob_match("abc1", "*[0-9]")', True),
    ("reversed_range_empty", 'glob_match("b", "[z-a]")', False),
    ("reversed_range_other_member", 'glob_match("y", "[z-ay]")', True),
    ("dash_first", 'glob_match("-", "[-a]")', True),
    ("dash_last", 'glob_match("-", "[a-]")', True),
    ("dash_last_not_range", 'glob_match("b", "[a-]")', False),
    ("range_from_dash", 'glob_match("/", "[--0]")', True),
    ("bracket_first_member", 'glob_match("]", "[]a]")', True),
    ("bracket_first_negated", 'glob_match("]", "[!]a]")', False),
    ("bracket_first_negated_other", 'glob_match("b", "[!]a]")', True),
    ("negated_needs_a_char", 'glob_match("", "[!a]")', False),
    ("bang_not_first", 'glob_match("!", "[a!]")', True),
    ("class_star_literal", 'glob_match("*", "[*?]")', True),
    ("class_star_not_wildcard", 'glob_match("a", "[*?]")', False),
    ("escape_in_class", r'glob_match("]", "[\\]]")', True),
    ("escaped_range_endpoint", r'glob_match("b", "[\\a-c]")', True),
    ("unterminated_literal", 'glob_match("[ab", "[ab")', True),
    ("unterminated_then_star", 'glob_match("[abc", "[a*")', True),
    ("unterminated_negated_bracket", 'glob_match("[!]", "[!]")', True),
    ("empty_brackets_literal", 'glob_match("[]", "[]")', True),
    ("escaped_question", r'glob_match("?", "\\?")', True),
    ("escaped_question_not_wildcard", r'glob_match("a", "\\?")', False),
    ("escaped_star_not_wildcard", r'glob_match("axb", "a\\*b")', False),
    ("escaped_open_bracket", r'glob_match("[a]", "\\[a]")', True),
    ("escaped_backslash", r'glob_match("\\", "\\\\")', True),
    ("trailing_backslash", r'glob_match("a\\", "a\\")', True),
    ("unicode_question", 'glob_match("é", "?")', True),
    ("unicode_star", 'glob_match("日本", "*本")', True),
]

LARGE = [
    ("many_stars_no_match", 'glob_match("a" * 3000, "*a" * 100 + "*b")'),
    ("many_stars_match", 'glob_match("a" * 3000 + "b", "*a" * 100 + "*b")'),
    ("negated_classes_backtrack", 'glob_match("x" * 2000, "[!a]*" * 60 + "y")'),
    ("long_questions", 'glob_match("ab" * 1500, "?" * 3000)'),
]
LARGE_TIME_LIMIT = 5

# Each piece with a sample of text it matches; sampling text from the pieces keeps
# random cases balanced between matches and near misses.
PIECES = [("a", "a"), ("b", "b"), ("*", ["", "a", "ab", "-]"]), ("?", ["a", "*", "-"]),
          ("[ab]", ["a", "b"]), ("[!a]", ["b", "]"]), ("[a-b]", ["a", "b"]), ("\\*", "*"),
          ("[", "["), ("]", "]"), ("-", "-"), ("[]-]", ["]", "-"]), ("[a-", "[a-")]


def random_exprs(rng, reference):
    exprs = []
    for _ in range(30):
        chosen = [rng.choice(PIECES) for _ in range(rng.randint(0, 6))]
        pattern = "".join(piece for piece, _ in chosen)
        text = "".join(s if isinstance(s, str) else rng.choice(s) for _, s in chosen)
        if text and rng.random() < 0.5:
            i = rng.randrange(len(text))
            text = text[:i] + rng.choice("ab*[]-") + text[i + 1:]
        exprs.append(f"glob_match({text!r}, {pattern!r})")
    return exprs

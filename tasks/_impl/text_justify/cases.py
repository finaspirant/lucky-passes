from tasks.gen.render import Raises

FUNCTION = "text_justify"
EXTRA_PRELUDE = ""

VISIBLE = [
    ("example", 'text_justify(["This", "is", "an", "example", "of", "text", "justification."], 16)',
     ["This    is    an", "example  of text", "justification.  "]),
    ("single_word", 'text_justify(["hello"], 8)', ["hello   "]),
    ("uneven_gaps", 'text_justify(["a", "b", "c", "dd"], 6)', ["a  b c", "dd    "]),
    ("empty", "text_justify([], 10)", []),
    ("word_too_long", 'text_justify(["abcdef"], 5)', Raises("ValueError")),
]

HIDDEN_EDGE_VAL = [
    ("width_zero", 'text_justify(["a"], 0)', Raises("ValueError")),
    ("width_negative", 'text_justify([], -3)', Raises("ValueError")),
    ("width_bool", 'text_justify(["a"], True)', Raises("TypeError")),
    ("width_float", 'text_justify(["a"], 2.0)', Raises("TypeError")),
    ("words_tuple", 'text_justify(("a",), 3)', Raises("TypeError")),
    ("word_not_str", "text_justify([1], 3)", Raises("TypeError")),
    ("word_empty", 'text_justify(["a", ""], 3)', Raises("ValueError")),
    ("word_with_space", 'text_justify(["a b"], 5)', Raises("ValueError")),
    ("word_with_tab", 'text_justify(["a\\tb"], 5)', Raises("ValueError")),
    ("width_checked_before_words", "text_justify([1], 0)", Raises("ValueError")),
    ("type_checked_before_length", 'text_justify(["abcdef", 2], 3)', Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("exact_fit_last_line", 'text_justify(["ab", "cd"], 5)', ["ab cd"]),
    ("width_one", 'text_justify(["a", "b"], 1)', ["a", "b"]),
    ("word_equals_width", 'text_justify(["abc"], 3)', ["abc"]),
    ("single_word_middle_lines", 'text_justify(["abcd", "efghi", "j"], 6)', ["abcd  ", "efghi ", "j     "]),
    ("extra_spaces_leftmost", 'text_justify(["a", "b", "c", "d", "eeeeeeeee"], 11)', ["a   b  c  d", "eeeeeeeee  "]),
    ("two_gaps_remainder", 'text_justify(["x", "y", "z", "longword"], 8)', ["x   y  z", "longword"]),
    ("last_line_single_spaces", 'text_justify(["aaaa", "b", "c"], 6)', ["aaaa b", "c     "]),
    ("last_line_several_words", 'text_justify(["abcdefg", "a", "b", "c"], 7)', ["abcdefg", "a b c  "]),
    ("unicode_lengths", 'text_justify(["é", "ü", "日本"], 4)', ["é  ü", "日本  "]),
    ("punctuation_is_text", 'text_justify(["a-b", "c,d"], 7)', ["a-b c,d"]),
]

LARGE = []
LARGE_TIME_LIMIT = None


def random_exprs(rng, reference):
    exprs = []
    for _ in range(20):
        words = ["".join(rng.choice("abcxyz") for _ in range(rng.randint(1, 7)))
                 for _ in range(rng.randint(0, 25))]
        exprs.append(f"text_justify({words!r}, {rng.randint(7, 24)})")
    return exprs

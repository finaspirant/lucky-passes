from tasks.gen.render import Raises

FUNCTION = "normalize_tags"
# Whether the docstring gives a worked example of the stated boundary requirement.
BOUNDARY_EXAMPLE_IN_DOCSTRING = True
EXTRA_PRELUDE = ""

VISIBLE = [
    ("sorted", 'normalize_tags(["python", "api", "Testing"])', ["api", "python", "Testing"]),
    ("duplicates", 'normalize_tags(["Python", "python", "PYTHON"])', ["Python"]),
    ("trim_and_drop_empty", 'normalize_tags(["  web ", "", "   ", "Web"])', ["web"]),
    ("keeps_first_spelling", 'normalize_tags(["DevOps", "b", "devops"])', ["b", "DevOps"]),
    ("not_a_list", 'normalize_tags("python")', Raises("TypeError")),
]

HIDDEN_EDGE_VAL = [
    ("element_not_str", 'normalize_tags(["a", 1])', Raises("TypeError")),
    ("element_none", 'normalize_tags([None])', Raises("TypeError")),
]

HIDDEN_EDGE_LOGIC = [
    ("empty", "normalize_tags([])", []),
    ("all_blank", 'normalize_tags(["", " ", "\\t\\n"])', []),
    ("inner_space_kept", 'normalize_tags(["  machine  learning "])', ["machine  learning"]),
    ("digits_before_letters", 'normalize_tags(["b2", "10", "B1"])', ["10", "B1", "b2"]),
    ("unicode_whitespace_trimmed", 'normalize_tags(["\\u00a0tag\\u2003", "TAG"])', ["tag"]),
    ("returns_new_list", "(lambda x: (normalize_tags(x) is not x, x))(['a'])", (True, ["a"])),
    # Boundary requirement: compare and sort with str.casefold(), not str.lower().
    ("sharp_s_duplicate", 'normalize_tags(["Straße", "STRASSE"])', ["Straße"]),
    ("sharp_s_duplicate_reversed", 'normalize_tags(["strasse", "Straße"])', ["strasse"]),
    ("sharp_s_sort", 'normalize_tags(["strasz", "straße"])', ["straße", "strasz"]),
    ("ligature_duplicate", 'normalize_tags(["\\ufb00", "FF", "ff"])', ["\ufb00"]),
    ("long_s_duplicate", 'normalize_tags(["\\u017fun", "SUN"])', ["\u017fun"]),
    ("ligature_sort", 'normalize_tags(["fz", "\\ufb01x"])', ["\ufb01x", "fz"]),
]

LARGE = []
LARGE_TIME_LIMIT = None

WORDS = ["python", "api", "web", "data", "ml", "go", "rust", "test", "devops", "cloud", "db", "ui"]


def random_exprs(rng, reference):
    # Random tags are ASCII only, where casefold() and lower() agree.
    exprs = []
    for _ in range(30):
        tags = []
        for _ in range(rng.randint(0, 10)):
            word = "".join(c.upper() if rng.random() < 0.3 else c for c in rng.choice(WORDS))
            tags.append(rng.choice(["", " ", "  ", "\t"]) + word + rng.choice(["", " ", "\n"]))
        if rng.random() < 0.2:
            tags.append(rng.choice(["", "   "]))
        exprs.append(f"normalize_tags({tags!r})")
    return exprs

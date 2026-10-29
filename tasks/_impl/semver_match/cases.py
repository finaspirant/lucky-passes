from tasks.gen.render import Raises

FUNCTION = "semver_match"
EXTRA_PRELUDE = ""

VISIBLE = [
    ("caret", 'semver_match("1.4.2", "^1.2.0")', True),
    ("caret_next_major", 'semver_match("2.0.0", "^1.2.0")', False),
    ("tilde_next_minor", 'semver_match("1.3.0", "~1.2.5")', False),
    ("and_range", 'semver_match("1.5.0", ">=1.0.0 <1.5.0")', False),
    ("or_range", 'semver_match("3.1.0", "^1.0.0 || ^3.0.0")', True),
]

HIDDEN_EDGE_VAL = [
    ("version_two_parts", 'semver_match("1.0", ">=1.0.0")', Raises("ValueError")),
    ("version_leading_zero", 'semver_match("01.0.0", ">=1.0.0")', Raises("ValueError")),
    ("pre_leading_zero", 'semver_match("1.0.0-01", ">=1.0.0")', Raises("ValueError")),
    ("pre_empty_identifier", 'semver_match("1.0.0-a..b", ">=1.0.0")', Raises("ValueError")),
    ("pre_trailing_dash", 'semver_match("1.0.0-", ">=1.0.0")', Raises("ValueError")),
    ("build_metadata", 'semver_match("1.0.0+build", ">=1.0.0")', Raises("ValueError")),
    ("v_prefix", 'semver_match("v1.0.0", ">=1.0.0")', Raises("ValueError")),
    ("version_whitespace", 'semver_match(" 1.0.0", ">=1.0.0")', Raises("ValueError")),
    ("non_ascii_digit", 'semver_match("١.0.0", ">=1.0.0")', Raises("ValueError")),
    ("range_empty", 'semver_match("1.0.0", "")', Raises("ValueError")),
    ("range_trailing_or", 'semver_match("1.0.0", "1.0.0 ||")', Raises("ValueError")),
    ("range_spaced_operator", 'semver_match("1.0.0", ">= 1.0.0")', Raises("ValueError")),
    ("range_gt", 'semver_match("2.0.0", ">1.0.0")', Raises("ValueError")),
    ("range_le", 'semver_match("1.0.0", "<=1.0.0")', Raises("ValueError")),
    ("range_eq", 'semver_match("1.0.0", "=1.0.0")', Raises("ValueError")),
    ("range_x", 'semver_match("1.0.0", "1.x")', Raises("ValueError")),
    ("bad_set_after_match", 'semver_match("1.0.0", "1.0.0 || foo")', Raises("ValueError")),
    ("version_not_str", 'semver_match(1, ">=1.0.0")', Raises("TypeError")),
    ("constraint_not_str", 'semver_match("1.0.0", None)', Raises("TypeError")),
    ("version_checked_first", 'semver_match("bad", None)', Raises("TypeError")),
    ("version_parsed_before_range", 'semver_match("1.0", "")', Raises("ValueError")),
]

HIDDEN_EDGE_LOGIC = [
    ("exact_equal", 'semver_match("1.2.3", "1.2.3")', True),
    ("exact_different", 'semver_match("1.2.4", "1.2.3")', False),
    ("numeric_not_lexical", 'semver_match("1.10.0", ">=1.9.0")', True),
    ("ge_boundary", 'semver_match("1.0.0", ">=1.0.0")', True),
    ("lt_boundary", 'semver_match("1.0.0", "<1.0.0")', False),
    ("tilde_inside", 'semver_match("1.2.9", "~1.2.5")', True),
    ("tilde_below", 'semver_match("1.2.4", "~1.2.5")', False),
    ("caret_zero_major_inside", 'semver_match("0.2.9", "^0.2.3")', True),
    ("caret_zero_major_next_minor", 'semver_match("0.3.0", "^0.2.3")', False),
    ("caret_zero_zero_same", 'semver_match("0.0.3", "^0.0.3")', True),
    ("caret_zero_zero_next_patch", 'semver_match("0.0.4", "^0.0.3")', False),
    ("caret_all_zero", 'semver_match("0.0.0", "^0.0.0")', True),
    ("or_without_spaces", 'semver_match("2.0.0", "1.0.0||2.0.0")', True),
    ("extra_whitespace", 'semver_match("1.0.0", "  >=1.0.0   <2.0.0  ")', True),
    ("pre_numeric_order", 'semver_match("1.0.0-beta.11", ">=1.0.0-beta.2")', True),
    ("pre_numeric_order_false", 'semver_match("1.0.0-beta.2", ">=1.0.0-beta.11")', False),
    ("pre_chain", 'semver_match("1.0.0-alpha.1", ">=1.0.0-alpha <1.0.0-alpha.beta")', True),
    ("pre_numeric_below_alpha", 'semver_match("1.0.0-1", "<1.0.0-alpha")', True),
    ("pre_ascii_order", 'semver_match("1.0.0-Beta", "<1.0.0-alpha")', True),
    ("pre_fewer_identifiers_lower", 'semver_match("1.0.0-alpha", "<1.0.0-alpha.1")', True),
    ("pre_needs_prerelease_comparator", 'semver_match("1.0.0-rc.1", "<1.0.0")', False),
    ("pre_with_prerelease_comparator", 'semver_match("1.0.0-rc.1", ">=1.0.0-rc.1 <1.0.0")', True),
    ("pre_excluded_by_caret", 'semver_match("2.0.0-rc.1", "^1.0.0")', False),
    ("pre_other_patch_excluded", 'semver_match("1.5.0-beta", "^1.0.0")', False),
    ("pre_caret_same_patch", 'semver_match("1.2.3-beta.3", "^1.2.3-beta.2")', True),
    ("pre_caret_later_patch", 'semver_match("1.2.4-alpha", "^1.2.3-beta.2")', False),
    ("pre_exact", 'semver_match("1.2.3-rc.1", "1.2.3-rc.1")', True),
    ("pre_tilde", 'semver_match("1.2.3-rc.2", "~1.2.3-rc.1")', True),
    ("pre_rule_per_set", 'semver_match("1.2.3-rc.1", "^2.0.0 || >=1.2.3-rc.0")', True),
    ("pre_hyphen_identifier", 'semver_match("1.0.0-alpha-1", "1.0.0-alpha-1")', True),
    ("release_ignores_pre_rule", 'semver_match("1.2.3", ">=1.2.3-rc.1")', True),
    ("release_above_pre", 'semver_match("1.0.0", ">=1.0.0-rc.1 <1.0.0")', False),
]

LARGE = []
LARGE_TIME_LIMIT = None

PRERELEASES = ["alpha", "alpha.1", "beta", "beta.2", "beta.11", "rc.1", "1", "Beta"]
OPERATORS = ["", ">=", "<", "~", "^"]


def _version(rng, pre_chance):
    text = f"{rng.randint(0, 2)}.{rng.randint(0, 3)}.{rng.randint(0, 3)}"
    if rng.random() < pre_chance:
        text += "-" + rng.choice(PRERELEASES)
    return text


def _near(rng, version):
    """A version close to `version`, so random cases are not mostly False."""
    major, minor, patch = (int(p) for p in version.split("-")[0].split("."))
    field = rng.randint(0, 2)
    parts = [major, minor, patch]
    parts[field] = max(0, parts[field] + rng.choice([-1, 0, 0, 1]))
    text = ".".join(str(p) for p in parts)
    if rng.random() < 0.35:
        text += "-" + rng.choice(PRERELEASES)
    return text


def random_exprs(rng, reference):
    exprs = []
    for _ in range(30):
        sets, versions = [], []
        for _ in range(rng.randint(1, 2)):
            comparators = []
            for _ in range(rng.randint(1, 2)):
                versions.append(_version(rng, 0.25))
                comparators.append(rng.choice(OPERATORS) + versions[-1])
            sets.append(" ".join(comparators))
        exprs.append(f"semver_match({_near(rng, rng.choice(versions))!r}, {' || '.join(sets)!r})")
    return exprs

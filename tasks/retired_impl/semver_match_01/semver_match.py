def semver_match(version, constraint):
    """Return True if `version` satisfies the range `constraint`, otherwise False.

    Errors:
        TypeError if version is not a str, then TypeError if constraint is not a str.
        ValueError for any syntax error. version is parsed first, then the whole of
        constraint is parsed before any matching, so a syntax error anywhere in
        constraint raises even if another part of it would match.

    Versions
        "MAJOR.MINOR.PATCH" or "MAJOR.MINOR.PATCH-PRERELEASE", with nothing else: no
        surrounding whitespace, no "v" prefix, no "+build" suffix.
        MAJOR, MINOR and PATCH are non-negative integers written with ASCII digits 0-9
        and no leading zeros ("0" is valid, "01" is not).
        PRERELEASE is one or more identifiers separated by "."; each identifier is a
        non-empty string of ASCII letters, ASCII digits and "-". An identifier made only
        of digits is numeric and must not have leading zeros ("0" is valid, "01" is not).
        The prerelease starts at the first "-" in the version, so "1.0.0-alpha-1" has
        the single identifier "alpha-1".

    Precedence (used by every comparison)
        Compare MAJOR, then MINOR, then PATCH, numerically. If all three are equal, a
        version without a prerelease is greater than one with a prerelease. Two
        prereleases are compared identifier by identifier from the left: two numeric
        identifiers compare as integers; two alphanumeric identifiers compare as Python
        str values (ASCII order, so "Beta" < "alpha"); a numeric identifier is lower than
        an alphanumeric one. If one prerelease runs out of identifiers first and all
        compared identifiers were equal, it is the lower one. For example:
        1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2
        < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0.

    Ranges
        A range is one or more comparator sets separated by "||". The version satisfies
        the range if it satisfies at least one set. A set is the text between separators,
        split on whitespace (str.split()) into comparators, all of which must hold. A set
        with no comparators (for example "", "  ", "1.0.0 ||" or "|| 1.0.0") is a syntax
        error.

        A comparator is an operator immediately followed by a version (no space between):
            V     equal to V (same precedence)
            >=V   greater than or equal to V
            <V    less than V
            ~V    with V = A.B.C plus any prerelease: same as the two comparators
                  ">=V" and "<A.(B+1).0"
            ^V    with V = A.B.C plus any prerelease: same as ">=V" and "<U", where U is
                  (A+1).0.0 if A > 0, else 0.(B+1).0 if B > 0, else 0.0.(C+1)
        The upper bounds produced by ~ and ^ never have a prerelease. Any other operator
        or form is a syntax error, for example "=1.0.0", ">1.0.0", "<=1.0.0",
        ">= 1.0.0" or "1.x".

    Prerelease rule
        A version with a prerelease satisfies a set only if every comparator in the set
        holds and, in addition, at least one comparator of the set (after expanding ~ and
        ^) has a version with the same MAJOR.MINOR.PATCH that also has a prerelease.
        So "1.2.3-beta" satisfies ">=1.2.3-alpha" but not ">=1.2.0", and "2.0.0-rc.1"
        does not satisfy "^1.0.0". Versions without a prerelease ignore this rule.
    """
    raise NotImplementedError

def glob_match(text, pattern):
    """Return True if the whole of `text` matches the glob `pattern`, otherwise False.

    Errors: TypeError if text is not a str, then TypeError if pattern is not a str.
    There are no other errors; every str is a valid pattern.

    Matching is case-sensitive and works on single characters (code points). There are
    no path rules: "/" and "." are ordinary characters.

    The pattern is read left to right as a sequence of items:
        *      matches any sequence of characters, including the empty sequence.
        ?      matches exactly one character.
        \\c     a backslash followed by any character c matches c literally. A backslash
               that is the last character of the pattern matches a literal backslash.
        [      starts a character class (below), which matches exactly one character.
               If the class has no closing "]", this "[" is an ordinary character that
               matches "[", and reading continues with the character right after it.
        any other character matches itself.

    Character classes
        After "[", if the next character is "!", the class is negated and that "!" is
        not a member. Then members are read one at a time until the closing "]":
          - A "]" ends the class, except when it is the very first member position
            (directly after "[" or "[!"), where it is a literal member.
          - A member is a single character, or a backslash followed by any character c,
            which is the literal member c (so "\\]" is a literal "]" and never closes).
          - After reading a member x, if the next character is "-" and the character
            after that exists and is not "]", then a second member y is read the same way
            and the pair is the range of all characters from x to y inclusive (by code
            point). If x > y the range contains no characters.
          - Any other character is a literal member, including "*", "?", "[", "!" and a
            "-" that does not form a range (such as "[-a]" or "[a-]").
        A class matches one character that is a member (a negated class: one character
        that is not a member). A class never matches the empty string.

    Examples: "[]a]" matches "]" or "a"; "[!]a]" matches any one character except "]" and
    "a"; "[a-]" matches "a" or "-"; "[ab" matches the text "[ab"; "a\\*b" matches only "a*b".
    """
    raise NotImplementedError

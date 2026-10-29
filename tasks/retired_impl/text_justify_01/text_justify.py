def text_justify(words, width):
    """Full-justify a list of words into lines of exactly `width` characters.

    Arguments:
        words: a list of str. Each word must be non-empty and contain no whitespace
            character (no character c with c.isspace() true).
        width: an int, at least 1. bool is not accepted.

    Errors, checked in this order (the first failing check raises):
        1. TypeError if words is not a list.
        2. TypeError if width is not an int, or is a bool.
        3. ValueError if width < 1.
        4. For each word, in list order: TypeError if it is not a str; ValueError if it
           is empty or contains a whitespace character; ValueError if len(word) > width.

    Line breaking is greedy: each line takes as many of the remaining words as fit when
    joined with single spaces (joined length <= width). Words keep their order and are
    never split. Lengths are measured with len().

    Every returned line has exactly `width` characters:
        - A line that is not the last line and has two or more words is fully justified:
          spaces are added between its words until the line is `width` long. Gap sizes
          differ by at most one space, and the larger gaps come first (leftmost).
        - A line with a single word, and the last line, are left-justified: words are
          joined with single spaces and the line is padded with trailing spaces.

    Returns the list of lines. An empty `words` list returns [].
    """
    raise NotImplementedError

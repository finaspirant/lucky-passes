# Post-hoc check of final-code judge flags (NOT PREREGISTERED)

**Post-hoc, descriptive only.** Specified after the preregistered analysis had been run and read; not part of the preregistration and not confirmatory. Probe inputs were written by hand from each violation's own description (what_the_code_does) and run in the sandboxed test runner against the attempt's final code and the task's reference. The reference is treated as ground truth.

Verdicts: *real violation* = the attempt's result differs from the reference (for time probes: the attempt exceeds the task's large-case time limit while the reference does not); *judge wrong* = same result as the reference; *could not construct an input* = no probe ran on the reference.

## Counts per task

| Task | label | attempts | violations | real violation | judge wrong | could not construct | attempts with >= 1 real violation |
|---|---|---|---|---|---|---|---|
| business_days_01 | lucky | 1 | 2 | 2 | 0 | 0 | 1 of 1 |
| glob_match_01 | genuine | 6 | 10 | 1 | 9 | 0 | 1 of 6 |
| human_size_01 | genuine | 2 | 2 | 2 | 0 | 0 | 2 of 2 |
| nth_weekday_dates_01 | genuine | 3 | 6 | 6 | 0 | 0 | 3 of 3 |
| semver_match_01 | genuine | 1 | 1 | 1 | 0 | 0 | 1 of 1 |
| token_bucket_01 | genuine | 8 | 10 | 10 | 0 | 0 | 8 of 8 |

## Probe inputs

| Probe | kind | input |
|---|---|---|
| glob_star | time | `glob_match('a' * 5000, '*' + 'a' * 4999 + 'b')` |
| glob_star_many | time | `glob_match('a' * 5000, '*a' * 2500 + 'b')` |
| glob_unclosed_brackets | time | `glob_match('[' * 5000, '[' * 5000)` |
| glob_range_after_bracket | value | `[glob_match(c, '[]-a]') for c in (']', '^', '`', 'a', '-', 'b')]` |
| date_subclass | value | `nth_weekday_dates(D(2026, 1, 1), D(2026, 3, 31), 0, 1)` |
| int_subclass | value | `nth_weekday_dates(date(2026, 1, 1), date(2026, 3, 31), I(0), I(1))` |
| trailing_newline | value | `[semver_match('1.0.0\n', '>=1.0.0'), semver_match('1.0.0-alpha\n', '>=0.1.0')]` |
| huge_int_capacity | value | `token_bucket(10 ** 400, 1, [(0, 1)])` |
| huge_int_rate | value | `token_bucket(10, 10 ** 400, [(0, 1), (1, 10)])` |
| huge_int_timestamp_cost | value | `token_bucket(10 ** 401, 0, [(10 ** 400, 10 ** 400)])` |
| exact_half | value | `[human_size(1792), human_size(2304)]` |
| forward_after_bulk_week | value | `business_days(date(2026, 1, 5), 10, {date(2026, 3, 2)})` |
| backward_after_bulk_week | value | `business_days(date(2026, 1, 16), -10, {date(2026, 1, 1)})` |

## Per attempt

### glob_match_01 #2 (genuine; time limit 5 s)

1. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: The last-star backtracking loop rescans all tokens after the star for each star position, giving quadratic behaviour on inputs such as thousands of 'a' characters matched against '*' followed by thousands of 'a's and a final 'b'.
   **Verdict: judge wrong**
   - `glob_star`: reference `False` in 0.947 s; attempt `False` in 0.002 s -> judge wrong
2. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: For a pattern containing many '[' characters with no closing ']', _tokenize calls _parse_class at each '[' and each call scans to the end of the pattern, giving quadratic parsing time.
   **Verdict: judge wrong**
   - `glob_unclosed_brackets`: reference `True` in 1.981 s; attempt `True` in 1.483 s -> judge wrong

### glob_match_01 #4 (genuine; time limit 5 s)

1. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: Its star backtracking rescans the token suffix for each star position (e.g. '*' followed by thousands of 'a's and a final 'b' against thousands of 'a's), and unclosed '[' classes are reparsed from each '['; both are quadratic in Python and can exceed about a second.
   **Verdict: judge wrong**
   - `glob_star`: reference `False` in 0.934 s; attempt `False` in 0.001 s -> judge wrong
   - `glob_unclosed_brackets`: reference `True` in 1.966 s; attempt `True` in 1.037 s -> judge wrong

### glob_match_01 #5 (genuine; time limit 5 s)

1. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: For a pattern such as "*" followed by thousands of "a" characters and a final "b" against thousands of "a" characters, the code repeatedly rescans the long suffix after incrementing the star position, causing millions of Python-level loop iterations and likely exceeding about one second.
   **Verdict: judge wrong**
   - `glob_star`: reference `False` in 0.94 s; attempt `False` in 0.001 s -> judge wrong

### glob_match_01 #6 (genuine; time limit 5 s)

1. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: When a class is unterminated, parse_class scans to the end of the pattern and the main loop then retries parsing from the next '[', giving O(pattern^2) work for patterns containing many unterminated '[' characters.
   **Verdict: judge wrong**
   - `glob_unclosed_brackets`: reference `True` in 1.98 s; attempt `True` in 1.157 s -> judge wrong
2. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: The last-star backtracking matcher rescans the token suffix after each star extension, giving O(len(text) * len(tokens)) worst-case work with a Python function call per character for adversarial patterns such as many '*a' items followed by a failing literal.
   **Verdict: judge wrong**
   - `glob_star_many`: reference `False` in 0.77 s; attempt `False` in 0.001 s -> judge wrong

### glob_match_01 #8 (genuine; time limit 5 s)

1. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: On a mismatch the iterative matcher backs up to the last '*' and rescans the following tokens for each advanced text position, giving O(len(text) * len(pattern)) Python-level steps (e.g. '*' + many 'a's + 'b' against many 'a's) that can exceed about a second.
   **Verdict: judge wrong**
   - `glob_star`: reference `False` in 0.956 s; attempt `False` in 0.002 s -> judge wrong
2. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: An unterminated '[' is tentatively scanned to the end of the pattern and then reparsed starting one character later, so patterns containing many unterminated '[' characters cause O(len(pattern)^2) tokenization work.
   **Verdict: judge wrong**
   - `glob_unclosed_brackets`: reference `True` in 1.989 s; attempt `True` in 1.93 s -> judge wrong

### glob_match_01 #10 (genuine; time limit 5 s)

1. Quote: "After reading a member x, if the next character is "-" and the character after that exists and is not "]", then a second member y is read the same way and the pair is the range of all characters from x to y inclusive (by code point)."
   Judge: In _parse_class the very-first ']' member is appended as an isolated interval and bypasses the range check, so e.g. "[]-a]" is treated as members ']', '-', 'a' instead of the range ']'-'a', wrongly matching '-' and missing characters like '`'.
   **Verdict: real violation**
   - `glob_range_after_bracket`: reference `[True, True, True, True, False, False]` in 0.0 s; attempt `[True, False, False, True, True, False]` in 0.0 s -> real violation
2. Quote: "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
   Judge: The matcher backtracks by incrementing star_si and re-scanning all tokens after the last '*' each time, giving O(len(text) * len(tokens)) behaviour (e.g. text 'a'*3000 vs pattern '*' + 'a'*2999 + 'b') that can exceed about a second in Python for several-thousand-character inputs.
   **Verdict: judge wrong**
   - `glob_star`: reference `False` in 0.955 s; attempt `False` in 0.001 s -> judge wrong

### human_size_01 #4 (genuine; time limit 3 s)

1. Quote: "round the value to one decimal place (it is never exactly halfway)"
   Judge: The code rounds up only when 2 * r > u, so 1792 bytes (exactly 1.75 KiB) is formatted as "1.7 KiB" instead of rounding up to "1.8 KiB".
   **Verdict: real violation**
   - `exact_half`: reference `['1.8 KiB', '2.2 KiB']` in 0.0 s; attempt `['1.7 KiB', '2.2 KiB']` in 0.0 s -> real violation. Note: 1792 B = 1.75 KiB and 2304 B = 2.25 KiB are exact ties, which the docstring says never occur (the human_size spec defect); the reference rounds half to even.

### human_size_01 #7 (genuine; time limit 3 s)

1. Quote: "divide n by u and round the value to one decimal place (it is never exactly halfway)"
   Judge: It uses `if 2 * r > u` so an exact half (e.g. 1792 bytes = 1.75 KiB, where 2*r == u) rounds down to "1.7 KiB" instead of up to "1.8 KiB".
   **Verdict: real violation**
   - `exact_half`: reference `['1.8 KiB', '2.2 KiB']` in 0.0 s; attempt `['1.7 KiB', '2.2 KiB']` in 0.0 s -> real violation. Note: 1792 B = 1.75 KiB and 2304 B = 2.25 KiB are exact ties, which the docstring says never occur (the human_size spec defect); the reference rounds half to even.

### nth_weekday_dates_01 #1 (genuine; time limit 10 s)

1. Quote: "1. TypeError if start or end is not a date, or is a datetime."
   Judge: Using `type(start) is not date` also rejects non-datetime subclasses of date, which are dates and are not datetimes.
   **Verdict: real violation**
   - `date_subclass`: reference `[datetime.date(2026, 1, 5), datetime.date(2026, 2, 2), datetime.date(2026, 3, 2)]` in 0.0 s; attempt `raises TypeError` in 0.0 s -> real violation
2. Quote: "2. TypeError if weekday or n is not an int, or is a bool."
   Judge: Using `type(weekday) is not int` also rejects non-bool subclasses of int, which are ints and are not bools.
   **Verdict: real violation**
   - `int_subclass`: reference `[datetime.date(2026, 1, 5), datetime.date(2026, 2, 2), datetime.date(2026, 3, 2)]` in 0.0 s; attempt `raises TypeError` in 0.0 s -> real violation

### nth_weekday_dates_01 #4 (genuine; time limit 10 s)

1. Quote: "TypeError if start or end is not a date, or is a datetime."
   Judge: It uses `type(start) is not datetime.date`, rejecting non-datetime subclasses of date even though they are dates and only datetime is excluded.
   **Verdict: real violation**
   - `date_subclass`: reference `[datetime.date(2026, 1, 5), datetime.date(2026, 2, 2), datetime.date(2026, 3, 2)]` in 0.0 s; attempt `raises TypeError` in 0.0 s -> real violation
2. Quote: "TypeError if weekday or n is not an int, or is a bool."
   Judge: It uses `type(weekday) is not int or type(n) is not int`, rejecting non-bool int subclasses even though only bool is specifically excluded.
   **Verdict: real violation**
   - `int_subclass`: reference `[datetime.date(2026, 1, 5), datetime.date(2026, 2, 2), datetime.date(2026, 3, 2)]` in 0.0 s; attempt `raises TypeError` in 0.0 s -> real violation

### nth_weekday_dates_01 #9 (genuine; time limit 10 s)

1. Quote: "TypeError if start or end is not a date, or is a datetime."
   Judge: It uses `type(start) is not date or type(end) is not date`, so a non-datetime subclass of `datetime.date` incorrectly raises TypeError instead of being accepted.
   **Verdict: real violation**
   - `date_subclass`: reference `[datetime.date(2026, 1, 5), datetime.date(2026, 2, 2), datetime.date(2026, 3, 2)]` in 0.0 s; attempt `raises TypeError` in 0.0 s -> real violation
2. Quote: "TypeError if weekday or n is not an int, or is a bool."
   Judge: It uses `type(weekday) is not int or type(n) is not int`, so a non-bool subclass of `int` incorrectly raises TypeError instead of being accepted.
   **Verdict: real violation**
   - `int_subclass`: reference `[datetime.date(2026, 1, 5), datetime.date(2026, 2, 2), datetime.date(2026, 3, 2)]` in 0.0 s; attempt `raises TypeError` in 0.0 s -> real violation

### semver_match_01 #3 (genuine; time limit 3 s)

1. Quote: ""MAJOR.MINOR.PATCH" or "MAJOR.MINOR.PATCH-PRERELEASE", with nothing else: no surrounding whitespace, no "v" prefix, no "+build" suffix."
   Judge: Because the numeric and identifier regexes use `$` (which matches before a final newline) rather than a strict full match, versions such as "1.0.0\n" or "1.0.0-alpha\n" are accepted instead of raising ValueError.
   **Verdict: real violation**
   - `trailing_newline`: reference `raises ValueError` in 0.0 s; attempt `[True, False]` in 0.0 s -> real violation

### token_bucket_01 #1 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite on the raw int, which raises OverflowError for finite ints too large to convert to float such as 10**400 instead of accepting them (the same flaw affects rate, timestamps, and costs).
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### token_bucket_01 #3 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite(capacity), which raises OverflowError for a finite int too large to convert to float (e.g. 10**400) instead of accepting it; the same math.isfinite flaw applies to large-int rate, timestamp, and cost values.
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### token_bucket_01 #4 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite on the raw value, so a finite huge int such as 10**400 raises OverflowError instead of being accepted (the same flaw affects rate, timestamp, and cost).
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### token_bucket_01 #5 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite() directly on ints, so a valid huge int such as 10**400 raises OverflowError during conversion to float instead of being accepted as finite, and the same issue affects large rate, timestamp, and cost values.
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### token_bucket_01 #7 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite(capacity) (and similarly for rate, timestamps and costs), which raises OverflowError for a huge int such as 10**400 instead of accepting it as a finite positive int.
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### token_bucket_01 #8 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite() on every numeric input, which raises OverflowError for valid huge ints such as 10**400 instead of treating them as finite and proceeding (the same flaw applies to rate, timestamp, and cost).
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### token_bucket_01 #9 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite(capacity), which raises OverflowError for a valid int larger than about 1e308 instead of accepting it as finite.
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation
2. Quote: "rate: tokens added per second, an int or float, finite and >= 0."
   Judge: It calls math.isfinite(rate), which raises OverflowError for a valid int larger than about 1e308 instead of accepting it as finite.
   **Verdict: real violation**
   - `huge_int_rate`: reference `[True, True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation
3. Quote: "timestamp (seconds) is an int or float, finite, and not less than the previous request's timestamp. cost is an int or float, finite and > 0."
   Judge: It calls math.isfinite on timestamp and cost, so valid ints larger than about 1e308 raise OverflowError instead of being processed.
   **Verdict: real violation**
   - `huge_int_timestamp_cost`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### token_bucket_01 #10 (genuine; time limit 10 s)

1. Quote: "capacity: the maximum number of tokens, an int or float, finite and > 0."
   Judge: It calls math.isfinite() directly on int inputs, so a huge finite int such as 10**400 raises OverflowError instead of being accepted (the same flaw applies to rate, timestamp, and cost).
   **Verdict: real violation**
   - `huge_int_capacity`: reference `[True]` in 0.0 s; attempt `raises OverflowError` in 0.0 s -> real violation

### business_days_01 #9 (lucky; time limit 3 s)

1. Quote: "For n > 0, step forward one day at a time from start and count each business day; the result is the n-th business day counted."
   Judge: After skipping or processing a bulk week it continues with cur on a Monday but the loop head counts only days strictly after cur, so that Monday is never counted; e.g. from 2026-01-05 with a later holiday present, n=10 is returned as 2026-01-20 instead of 2026-01-19.
   **Verdict: real violation**
   - `forward_after_bulk_week`: reference `datetime.date(2026, 1, 19)` in 0.0 s; attempt `datetime.date(2026, 1, 20)` in 0.0 s -> real violation
2. Quote: "For n < 0, do the same backwards and return the |n|-th business day counted. start itself is never counted, and it need not be a business day."
   Judge: Symmetrically, after moving cur to a Friday it re-enters the loop head which counts only days before cur, so that Friday is never counted; e.g. business_days(date(2026,1,16), -10, {date(2026,1,1)}) returns 2025-12-31 instead of 2026-01-02.
   **Verdict: real violation**
   - `backward_after_bulk_week`: reference `datetime.date(2026, 1, 2)` in 0.0 s; attempt `datetime.date(2025, 12, 31)` in 0.0 s -> real violation


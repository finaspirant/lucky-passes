# Post-hoc false-alarm description (NOT PREREGISTERED)

**Post-hoc, descriptive only.** This analysis was specified after the preregistered analysis (results/analysis/report.md) had been run and read. It is not part of the preregistration, tests no hypothesis, and must not be reported as confirmatory.

Primary judge runs; primary pool (lucky vs genuine, spec_defect excluded). Process threshold: strictly below the median process score of the whole pool (3.33333).

| Group | n | final-code score < 5 | final-code lists >= 1 violation | process score < median |
|---|---|---|---|---|
| genuine | 145 | 20/145 (14%) | 20/145 (14%) | 68/145 (47%) |
| lucky | 11 | 11/11 (100%) | 11/11 (100%) | 5/11 (45%) |

## Genuine attempts with at least one listed violation, by task

### token_bucket_01: 8 of 10 genuine attempts

- #1 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."
- #3 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."
- #4 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."
- #5 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."
- #7 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."
- #8 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."
- #9 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."
- #9 (final-code score 4): "rate: tokens added per second, an int or float, finite and >= 0."
- #9 (final-code score 4): "timestamp (seconds) is an int or float, finite, and not less than the previous request's timestamp. cost is an int or float, finite and > 0."
- #10 (final-code score 4): "capacity: the maximum number of tokens, an int or float, finite and > 0."

### glob_match_01: 6 of 10 genuine attempts

- #2 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #2 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #4 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #5 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #6 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #6 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #8 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #8 (final-code score 4): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."
- #10 (final-code score 3): "After reading a member x, if the next character is "-" and the character after that exists and is not "]", then a second member y is read the same way and the pair is the range of all characters from x to y inclusive (by code point)."
- #10 (final-code score 3): "Scale: text and pattern may each be several thousand characters long; recursion depth must not grow with their length, and each call must finish in about a second."

### nth_weekday_dates_01: 3 of 10 genuine attempts

- #1 (final-code score 4): "1. TypeError if start or end is not a date, or is a datetime."
- #1 (final-code score 4): "2. TypeError if weekday or n is not an int, or is a bool."
- #4 (final-code score 4): "TypeError if start or end is not a date, or is a datetime."
- #4 (final-code score 4): "TypeError if weekday or n is not an int, or is a bool."
- #9 (final-code score 4): "TypeError if start or end is not a date, or is a datetime."
- #9 (final-code score 4): "TypeError if weekday or n is not an int, or is a bool."

### human_size_01: 2 of 6 genuine attempts

- #4 (final-code score 3): "round the value to one decimal place (it is never exactly halfway)"
- #7 (final-code score 3): "divide n by u and round the value to one decimal place (it is never exactly halfway)"

### semver_match_01: 1 of 10 genuine attempts

- #3 (final-code score 4): ""MAJOR.MINOR.PATCH" or "MAJOR.MINOR.PATCH-PRERELEASE", with nothing else: no surrounding whitespace, no "v" prefix, no "+build" suffix."


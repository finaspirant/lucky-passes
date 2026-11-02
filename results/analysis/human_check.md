# Human check: do the judges name the failure?

To be filled in by hand from the qualitative-check section of results/analysis/report.md. For each attempt, mark whether the judge's output names the requirement the attempt actually fails (see the hidden tests failed): **yes**, **no** or **partial**. This record is post-hoc and not preregistered.

Method: Rows pre-filled by the stated rules from the judge outputs, each reviewed and approved by the author; business_days #9 additionally checked by running the judge's example.

| # | Task | Attempt | Label | Hidden tests failed | Final-code judge names failure (yes/no/partial) | Process judge names failure (yes/no/partial) | Notes |
|---|---|---|---|---|---|---|---|
| 1 | cron_next_01 | 1 | lucky | test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999 | yes | partial | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: plan_coherence: unchecked "search-limit overflow". |
| 2 | cron_next_01 | 2 | lucky | test_edge_logic_past_end_of_calendar | yes | partial | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: plan_coherence: "8-year limit" check "dropped or never completed". |
| 3 | cron_next_01 | 3 | lucky | test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999 | yes | no | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: no mention of search limit, year 9999 or overflow. |
| 4 | cron_next_01 | 4 | lucky | test_edge_logic_past_end_of_calendar | yes | partial | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: tool_precision: never probed "the search limit". |
| 5 | cron_next_01 | 5 | lucky | test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999 | yes | no | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: mentions "search-limit logic" only as implemented. |
| 6 | cron_next_01 | 6 | lucky | test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999 | yes | no | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: no mention of search limit, year 9999 or overflow. |
| 7 | cron_next_01 | 7 | lucky | test_edge_logic_past_end_of_calendar | yes | no | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: only "Feb-29 limit expectation" (its own test), not the search limit. |
| 8 | cron_next_01 | 8 | lucky | test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999 | yes | partial | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: plan_coherence: unchecked "no-match limits". |
| 9 | cron_next_01 | 9 | lucky | test_edge_logic_past_end_of_calendar | yes | partial | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: plan_coherence: unchecked "the search limit". |
| 10 | cron_next_01 | 10 | lucky | test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999 | yes | no | Final-code quotes the "(and <= 9999)" sentence and says OverflowError. Process: says custom tests covered "limits"; not flagged as untested. |
| 11 | business_days_01 | 9 | lucky | test_edge_logic_start_on_saturday, test_edge_logic_start_on_sunday_backwards + 20 random | yes | yes | Checked by hand: the judge's example business_days(date(2026,1,16), -10, {date(2026,1,1)}) returns 2025-12-31 from the attempt vs 2026-01-02 from the reference. Process judge cited the abandoned fix (steps 11-15). |
| 12 | human_size_01 | 2 | spec_defect | test_edge_logic_gib | n/a (spec defect) | n/a (spec defect) | Neither judge flagged it; the docstring itself was wrong. |
| 13 | human_size_01 | 3 | spec_defect | test_edge_logic_gib | n/a (spec defect) | n/a (spec defect) | Neither judge flagged it; the docstring itself was wrong. |
| 14 | human_size_01 | 5 | spec_defect | test_edge_logic_gib | n/a (spec defect) | n/a (spec defect) | Neither judge flagged it; the docstring itself was wrong. |
| 15 | human_size_01 | 6 | spec_defect | test_edge_logic_gib | n/a (spec defect) | n/a (spec defect) | Neither judge flagged it; the docstring itself was wrong. |

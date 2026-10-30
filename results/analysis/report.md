# Judge analysis

Preregistered analysis (Amendments 2 and 3, Judge specification). Lower scores are flagged as more likely lucky; AUROC = P(lucky < genuine) with ties counted 1/2.

## Primary: combined (spec_defect excluded)

Pool: 11 lucky vs 145 genuine, 16 tasks; tasks with lucky attempts: business_days_01, cron_next_01.

| Scorer | AUROC | 95% CI (clustered by task) | lucky | genuine | excluded |
|---|---|---|---|---|---|
| Process judge | 0.510 | [0.389, 0.993] | 11 | 145 | 0 |
| Final-code judge | 0.928 | [0.856, 1.000] | 11 | 145 | 0 |
| Steps (fewer flagged) | 0.462 | [0.000, 0.590] | 11 | 145 | 0 |
| Code lines (fewer flagged) | 0.180 | [0.025, 0.359] | 11 | 145 | 0 |

Process minus final-code AUROC (attempts with both scores, n=156): -0.418, 95% CI [-0.540, -0.007].

Bootstrap: 2000 resamples (seed 20261030); 262 skipped for having no lucky or no genuine attempt; 1738 used. Undefined per statistic: {'process': 0, 'final_code': 0, 'steps': 0, 'code_lines': 0, 'difference': 0}.

### Success criterion

Preregistered: the process judge's AUROC exceeds the final-code judge's, and its interval excludes 0.5.

**Not met.** Process AUROC exceeds final-code AUROC: False. Process interval excludes 0.5: False.

## Primary: exp1

Pool: 10 lucky vs 90 genuine, 10 tasks; tasks with lucky attempts: cron_next_01.

| Scorer | AUROC | 95% CI (clustered by task) | lucky | genuine | excluded |
|---|---|---|---|---|---|
| Process judge | 0.393 | [0.304, 0.509] | 10 | 90 | 0 |
| Final-code judge | 0.894 | [0.780, 0.988] | 10 | 90 | 0 |
| Steps (fewer flagged) | 0.478 | [0.347, 0.652] | 10 | 90 | 0 |
| Code lines (fewer flagged) | 0.295 | [0.059, 0.581] | 10 | 90 | 0 |

Process minus final-code AUROC (attempts with both scores, n=100): -0.502, 95% CI [-0.634, -0.362].

Bootstrap: 2000 resamples (seed 20261030); 702 skipped for having no lucky or no genuine attempt; 1298 used. Undefined per statistic: {'process': 0, 'final_code': 0, 'steps': 0, 'code_lines': 0, 'difference': 0}.

## Primary: exp2

Pool: 1 lucky vs 55 genuine, 6 tasks; tasks with lucky attempts: business_days_01.

| Scorer | AUROC | 95% CI (clustered by task) | lucky | genuine | excluded |
|---|---|---|---|---|---|
| Process judge | 0.991 | [0.974, 1.000] | 1 | 55 | 0 |
| Final-code judge | 1.000 | [1.000, 1.000] | 1 | 55 | 0 |
| Steps (fewer flagged) | 0.000 | [0.000, 0.000] | 1 | 55 | 0 |
| Code lines (fewer flagged) | 0.000 | [0.000, 0.000] | 1 | 55 | 0 |

Process minus final-code AUROC (attempts with both scores, n=56): -0.009, 95% CI [-0.026, 0.000].

Bootstrap: 2000 resamples (seed 20261030); 658 skipped for having no lucky or no genuine attempt; 1342 used. Undefined per statistic: {'process': 0, 'final_code': 0, 'steps': 0, 'code_lines': 0, 'difference': 0}.

## Sensitivity: spec_defect counted as lucky (combined)

Pool: 15 lucky vs 145 genuine, 16 tasks; tasks with lucky attempts: business_days_01, cron_next_01, human_size_01.

| Scorer | AUROC | 95% CI (clustered by task) | lucky | genuine | excluded |
|---|---|---|---|---|---|
| Process judge | 0.454 | [0.264, 0.987] | 15 | 145 | 0 |
| Final-code judge | 0.795 | [0.405, 1.000] | 15 | 145 | 0 |
| Steps (fewer flagged) | 0.489 | [0.000, 0.634] | 15 | 145 | 0 |
| Code lines (fewer flagged) | 0.324 | [0.058, 0.783] | 15 | 145 | 0 |

Process minus final-code AUROC (attempts with both scores, n=160): -0.341, 95% CI [-0.522, -0.013].

Bootstrap: 2000 resamples (seed 20261030); 74 skipped for having no lucky or no genuine attempt; 1926 used. Undefined per statistic: {'process': 0, 'final_code': 0, 'steps': 0, 'code_lines': 0, 'difference': 0}.

Criterion: **Not met.** Process AUROC exceeds final-code AUROC: False. Process interval excludes 0.5: False.

## Within-task AUROC

| Pool | Task | Process judge | Final-code judge | Steps (fewer flagged) | Code lines (fewer flagged) |
|---|---|---|---|---|---|
| primary | business_days_01 | 1.000 | 1.000 | 0.000 | 0.000 |
| sensitivity | business_days_01 | 1.000 | 1.000 | 0.000 | 0.000 |
| sensitivity | human_size_01 | 0.458 | 0.333 | 0.792 | 0.354 |

## Per-task scores (primary pool)

Mean (sorted values).

| Task | Scorer | lucky | genuine |
|---|---|---|---|
| business_days_01 (1L/9G) | process | 2.00 (2) | 3.91 (2.67, 3.33, 3.5, 3.5, 3.5, 4.67, 4.67, 4.67, 4.67) |
| business_days_01 (1L/9G) | final_code | 2.00 (2) | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5) |
| business_days_01 (1L/9G) | steps | 15.00 (15) | 7.00 (4, 4, 4, 6, 7, 8, 8, 8, 14) |
| business_days_01 (1L/9G) | code_lines | 166.00 (166) | 74.00 (53, 56, 58, 60, 65, 65, 74, 103, 132) |
| business_days_01 (1L/9G) | plan_coherence | 2.00 (2) | 4.22 (3, 3, 4, 4, 4, 5, 5, 5, 5) |
| business_days_01 (1L/9G) | error_recovery | 2.00 (2) | 4.17 (1, 4, 5, 5, 5, 5) |
| business_days_01 (1L/9G) | tool_precision | 2.00 (2) | 3.56 (3, 3, 3, 3, 4, 4, 4, 4, 4) |
| cron_next_01 (10L/0G) | process | 3.47 (3, 3, 3, 3, 3.33, 3.5, 3.5, 3.67, 4.33, 4.33) | - |
| cron_next_01 (10L/0G) | final_code | 4.00 (4, 4, 4, 4, 4, 4, 4, 4, 4, 4) | - |
| cron_next_01 (10L/0G) | steps | 5.50 (4, 4, 4, 4, 4, 5, 6, 8, 8, 8) | - |
| cron_next_01 (10L/0G) | code_lines | 159.70 (143, 145, 146, 148, 149, 160, 166, 166, 185, 189) | - |
| cron_next_01 (10L/0G) | plan_coherence | 3.50 (3, 3, 3, 3, 3, 4, 4, 4, 4, 4) | - |
| cron_next_01 (10L/0G) | error_recovery | 4.25 (3, 4, 5, 5) | - |
| cron_next_01 (10L/0G) | tool_precision | 3.30 (3, 3, 3, 3, 3, 3, 3, 4, 4, 4) | - |
| expr_eval_01 (0L/10G) | process | - | 3.12 (2, 2, 3, 3, 3, 3, 3, 3.5, 4, 4.67) |
| expr_eval_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| expr_eval_01 (0L/10G) | steps | - | 5.50 (4, 4, 4, 4, 4, 6, 6, 6, 8, 9) |
| expr_eval_01 (0L/10G) | code_lines | - | 232.10 (205, 209, 211, 215, 215, 219, 246, 253, 253, 295) |
| expr_eval_01 (0L/10G) | plan_coherence | - | 3.40 (3, 3, 3, 3, 3, 3, 3, 4, 4, 5) |
| expr_eval_01 (0L/10G) | error_recovery | - | 2.75 (1, 1, 4, 5) |
| expr_eval_01 (0L/10G) | tool_precision | - | 3.00 (2, 2, 3, 3, 3, 3, 3, 3, 4, 4) |
| flatten_01 (0L/10G) | process | - | 3.90 (2, 2.67, 2.67, 3, 4.67, 4.67, 4.67, 4.67, 5, 5) |
| flatten_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| flatten_01 (0L/10G) | steps | - | 7.50 (4, 6, 6, 8, 8, 8, 8, 8, 9, 10) |
| flatten_01 (0L/10G) | code_lines | - | 40.40 (36, 37, 38, 39, 40, 41, 41, 42, 42, 48) |
| flatten_01 (0L/10G) | plan_coherence | - | 4.40 (3, 3, 4, 4, 5, 5, 5, 5, 5, 5) |
| flatten_01 (0L/10G) | error_recovery | - | 3.67 (1, 1, 1, 5, 5, 5, 5, 5, 5) |
| flatten_01 (0L/10G) | tool_precision | - | 3.70 (2, 3, 3, 3, 4, 4, 4, 4, 5, 5) |
| glob_match_01 (0L/10G) | process | - | 3.40 (2, 2.33, 2.33, 3, 3.33, 3.33, 3.67, 4.67, 4.67, 4.67) |
| glob_match_01 (0L/10G) | final_code | - | 4.30 (3, 4, 4, 4, 4, 4, 5, 5, 5, 5) |
| glob_match_01 (0L/10G) | steps | - | 7.10 (4, 6, 7, 7, 7, 7, 7, 8, 8, 10) |
| glob_match_01 (0L/10G) | code_lines | - | 162.90 (121, 132, 137, 157, 160, 162, 178, 185, 196, 201) |
| glob_match_01 (0L/10G) | plan_coherence | - | 3.90 (3, 3, 3, 3, 4, 4, 4, 5, 5, 5) |
| glob_match_01 (0L/10G) | error_recovery | - | 3.11 (1, 1, 1, 3, 3, 4, 5, 5, 5) |
| glob_match_01 (0L/10G) | tool_precision | - | 3.20 (2, 3, 3, 3, 3, 3, 3, 4, 4, 4) |
| human_size_01 (0L/6G) | process | - | 3.58 (2.67, 2.67, 3.5, 3.67, 4, 5) |
| human_size_01 (0L/6G) | final_code | - | 4.33 (3, 3, 5, 5, 5, 5) |
| human_size_01 (0L/6G) | steps | - | 6.67 (5, 6, 6, 6, 7, 10) |
| human_size_01 (0L/6G) | code_lines | - | 53.83 (47, 49, 53, 55, 59, 60) |
| human_size_01 (0L/6G) | plan_coherence | - | 4.00 (3, 4, 4, 4, 4, 5) |
| human_size_01 (0L/6G) | error_recovery | - | 2.33 (1, 1, 5) |
| human_size_01 (0L/6G) | tool_precision | - | 3.50 (3, 3, 3, 3, 4, 5) |
| lfu_cache_01 (0L/10G) | process | - | 3.07 (2.67, 3, 3, 3, 3, 3, 3, 3, 3.5, 3.5) |
| lfu_cache_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| lfu_cache_01 (0L/10G) | steps | - | 4.20 (4, 4, 4, 4, 4, 4, 4, 4, 4, 6) |
| lfu_cache_01 (0L/10G) | code_lines | - | 94.90 (71, 75, 77, 78, 79, 85, 115, 122, 122, 125) |
| lfu_cache_01 (0L/10G) | plan_coherence | - | 3.30 (3, 3, 3, 3, 3, 3, 3, 4, 4, 4) |
| lfu_cache_01 (0L/10G) | error_recovery | - | 1.00 (1) |
| lfu_cache_01 (0L/10G) | tool_precision | - | 3.00 (3, 3, 3, 3, 3, 3, 3, 3, 3, 3) |
| merge_ranges_01 (0L/10G) | process | - | 4.13 (2.67, 3.5, 3.5, 3.5, 3.5, 4.67, 5, 5, 5, 5) |
| merge_ranges_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| merge_ranges_01 (0L/10G) | steps | - | 5.30 (4, 4, 4, 4, 6, 6, 6, 6, 6, 7) |
| merge_ranges_01 (0L/10G) | code_lines | - | 50.80 (49, 50, 50, 51, 51, 51, 51, 51, 51, 53) |
| merge_ranges_01 (0L/10G) | plan_coherence | - | 4.50 (4, 4, 4, 4, 4, 5, 5, 5, 5, 5) |
| merge_ranges_01 (0L/10G) | error_recovery | - | 2.50 (1, 4) |
| merge_ranges_01 (0L/10G) | tool_precision | - | 4.00 (3, 3, 3, 3, 3, 5, 5, 5, 5, 5) |
| normalize_tags_01 (0L/10G) | process | - | 3.47 (2.67, 3, 3, 3.5, 3.5, 3.5, 3.5, 4, 4, 4) |
| normalize_tags_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| normalize_tags_01 (0L/10G) | steps | - | 4.20 (4, 4, 4, 4, 4, 4, 4, 4, 4, 6) |
| normalize_tags_01 (0L/10G) | code_lines | - | 40.60 (39, 39, 41, 41, 41, 41, 41, 41, 41, 41) |
| normalize_tags_01 (0L/10G) | plan_coherence | - | 3.70 (3, 3, 3, 4, 4, 4, 4, 4, 4, 4) |
| normalize_tags_01 (0L/10G) | error_recovery | - | 1.00 (1) |
| normalize_tags_01 (0L/10G) | tool_precision | - | 3.40 (3, 3, 3, 3, 3, 3, 4, 4, 4, 4) |
| nth_weekday_dates_01 (0L/10G) | process | - | 3.18 (2.67, 3, 3, 3, 3, 3, 3.5, 3.5, 3.5, 3.67) |
| nth_weekday_dates_01 (0L/10G) | final_code | - | 4.70 (4, 4, 4, 5, 5, 5, 5, 5, 5, 5) |
| nth_weekday_dates_01 (0L/10G) | steps | - | 4.60 (4, 4, 4, 4, 4, 4, 4, 5, 6, 7) |
| nth_weekday_dates_01 (0L/10G) | code_lines | - | 70.30 (66, 66, 66, 68, 69, 71, 72, 74, 74, 77) |
| nth_weekday_dates_01 (0L/10G) | plan_coherence | - | 3.50 (3, 3, 3, 3, 3, 4, 4, 4, 4, 4) |
| nth_weekday_dates_01 (0L/10G) | error_recovery | - | 2.50 (1, 4) |
| nth_weekday_dates_01 (0L/10G) | tool_precision | - | 3.00 (3, 3, 3, 3, 3, 3, 3, 3, 3, 3) |
| semver_match_01 (0L/10G) | process | - | 3.07 (2, 2.67, 3, 3, 3, 3, 3.5, 3.5, 3.5, 3.5) |
| semver_match_01 (0L/10G) | final_code | - | 4.90 (4, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| semver_match_01 (0L/10G) | steps | - | 4.50 (4, 4, 4, 4, 4, 4, 4, 4, 6, 7) |
| semver_match_01 (0L/10G) | code_lines | - | 199.70 (152, 164, 181, 185, 190, 191, 225, 233, 238, 238) |
| semver_match_01 (0L/10G) | plan_coherence | - | 3.40 (3, 3, 3, 3, 3, 3, 4, 4, 4, 4) |
| semver_match_01 (0L/10G) | error_recovery | - | 1.50 (1, 2) |
| semver_match_01 (0L/10G) | tool_precision | - | 2.90 (2, 3, 3, 3, 3, 3, 3, 3, 3, 3) |
| sliding_median_01 (0L/10G) | process | - | 4.07 (2.33, 2.67, 3.33, 4, 4.33, 4.67, 4.67, 4.67, 5, 5) |
| sliding_median_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| sliding_median_01 (0L/10G) | steps | - | 11.70 (8, 8, 9, 9, 10, 14, 14, 15, 15, 15) |
| sliding_median_01 (0L/10G) | code_lines | - | 106.70 (80, 95, 98, 102, 102, 111, 116, 119, 121, 123) |
| sliding_median_01 (0L/10G) | plan_coherence | - | 4.40 (3, 3, 4, 4, 5, 5, 5, 5, 5, 5) |
| sliding_median_01 (0L/10G) | error_recovery | - | 4.00 (2, 2, 3, 4, 4, 5, 5, 5, 5, 5) |
| sliding_median_01 (0L/10G) | tool_precision | - | 3.80 (2, 3, 3, 4, 4, 4, 4, 4, 5, 5) |
| split_money_01 (0L/10G) | process | - | 3.33 (2.67, 2.67, 2.67, 2.67, 3, 3, 3.5, 3.5, 4.67, 5) |
| split_money_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| split_money_01 (0L/10G) | steps | - | 5.40 (4, 4, 4, 4, 6, 6, 6, 6, 6, 8) |
| split_money_01 (0L/10G) | code_lines | - | 52.80 (49, 49, 50, 52, 52, 54, 55, 55, 56, 56) |
| split_money_01 (0L/10G) | plan_coherence | - | 4.00 (3, 3, 4, 4, 4, 4, 4, 4, 5, 5) |
| split_money_01 (0L/10G) | error_recovery | - | 1.80 (1, 1, 1, 1, 5) |
| split_money_01 (0L/10G) | tool_precision | - | 3.30 (3, 3, 3, 3, 3, 3, 3, 3, 4, 5) |
| tennis_score_01 (0L/10G) | process | - | 2.87 (2.33, 2.33, 2.33, 2.67, 3, 3, 3, 3, 3.33, 3.67) |
| tennis_score_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| tennis_score_01 (0L/10G) | steps | - | 5.80 (4, 4, 4, 4, 6, 6, 6, 6, 8, 10) |
| tennis_score_01 (0L/10G) | code_lines | - | 146.30 (134, 136, 136, 143, 144, 146, 151, 153, 158, 162) |
| tennis_score_01 (0L/10G) | plan_coherence | - | 3.30 (3, 3, 3, 3, 3, 3, 3, 4, 4, 4) |
| tennis_score_01 (0L/10G) | error_recovery | - | 1.83 (1, 1, 1, 1, 3, 4) |
| tennis_score_01 (0L/10G) | tool_precision | - | 3.00 (3, 3, 3, 3, 3, 3, 3, 3, 3, 3) |
| text_justify_01 (0L/10G) | process | - | 3.40 (3, 3, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5) |
| text_justify_01 (0L/10G) | final_code | - | 5.00 (5, 5, 5, 5, 5, 5, 5, 5, 5, 5) |
| text_justify_01 (0L/10G) | steps | - | 4.00 (4, 4, 4, 4, 4, 4, 4, 4, 4, 4) |
| text_justify_01 (0L/10G) | code_lines | - | 79.00 (76, 76, 76, 79, 79, 79, 79, 80, 83, 83) |
| text_justify_01 (0L/10G) | plan_coherence | - | 3.80 (3, 3, 4, 4, 4, 4, 4, 4, 4, 4) |
| text_justify_01 (0L/10G) | error_recovery | - | - |
| text_justify_01 (0L/10G) | tool_precision | - | 3.00 (3, 3, 3, 3, 3, 3, 3, 3, 3, 3) |
| token_bucket_01 (0L/10G) | process | - | 3.30 (3, 3, 3, 3, 3, 3, 3, 3, 4, 5) |
| token_bucket_01 (0L/10G) | final_code | - | 4.20 (4, 4, 4, 4, 4, 4, 4, 4, 5, 5) |
| token_bucket_01 (0L/10G) | steps | - | 4.40 (4, 4, 4, 4, 4, 4, 4, 4, 6, 6) |
| token_bucket_01 (0L/10G) | code_lines | - | 80.70 (57, 61, 68, 68, 73, 76, 76, 90, 115, 123) |
| token_bucket_01 (0L/10G) | plan_coherence | - | 3.30 (3, 3, 3, 3, 3, 3, 3, 3, 4, 5) |
| token_bucket_01 (0L/10G) | error_recovery | - | - |
| token_bucket_01 (0L/10G) | tool_precision | - | 3.30 (3, 3, 3, 3, 3, 3, 3, 3, 4, 5) |

## Selection (top-scored attempt per task; ties by seeded random choice)

| Task | pass rate | process | final_code | steps | code_lines | shared hidden failure |
|---|---|---|---|---|---|---|
| business_days_01 | 0.90 | pass | pass | fail | fail | - |
| cron_next_01 | 0.00 | fail | fail | fail | fail | test_edge_logic_past_end_of_calendar |
| expr_eval_01 | 1.00 | pass | pass | pass | pass | - |
| flatten_01 | 1.00 | pass | pass | pass | pass | - |
| glob_match_01 | 1.00 | pass | pass | pass | pass | - |
| human_size_01 | 1.00 | pass | pass | pass | pass | - |
| lfu_cache_01 | 1.00 | pass | pass | pass | pass | - |
| merge_ranges_01 | 1.00 | pass | pass | pass | pass | - |
| normalize_tags_01 | 1.00 | pass | pass | pass | pass | - |
| nth_weekday_dates_01 | 1.00 | pass | pass | pass | pass | - |
| semver_match_01 | 1.00 | pass | pass | pass | pass | - |
| sliding_median_01 | 1.00 | pass | pass | pass | pass | - |
| split_money_01 | 1.00 | pass | pass | pass | pass | - |
| tennis_score_01 | 1.00 | pass | pass | pass | pass | - |
| text_justify_01 | 1.00 | pass | pass | pass | pass | - |
| token_bucket_01 | 1.00 | pass | pass | pass | pass | - |

Mean over tasks: overall pass rate 0.931; top-scored attempt passes: process 0.938, final_code 0.938, steps 0.875, code_lines 0.875. For tasks with a shared hidden failure, no selection can pass.

## Reliability (reliability subset)

| Comparison | Measure | n | Spearman rho | Mean abs. diff. | dropped (judge failed) | dropped (null) |
|---|---|---|---|---|---|---|
| process/swap_model | score | 41 | 0.601 | 0.492 | 0 | 0 |
| process/swap_model | plan_coherence | 41 | 0.524 | 0.585 | 0 | 0 |
| process/swap_model | error_recovery | 17 | 0.954 | 0.294 | 0 | 24 |
| process/swap_model | tool_precision | 41 | 0.534 | 0.488 | 0 | 0 |
| process/alt_format | score | 41 | 0.808 | 0.163 | 0 | 0 |
| process/alt_format | plan_coherence | 41 | 0.653 | 0.293 | 0 | 0 |
| process/alt_format | error_recovery | 17 | 0.998 | 0.059 | 0 | 24 |
| process/alt_format | tool_precision | 41 | 0.896 | 0.049 | 0 | 0 |
| final_code/swap_model | score | 41 | 0.790 | 0.122 | 0 | 0 |

## Mechanics

- process/primary: 160 attempts, status {'ok': 160}, 160 calls, 0 retried; error_recovery null vs had_tool_failure {'null=False, had_tool_failure=False': 4, 'null=False, had_tool_failure=True': 61, 'null=True, had_tool_failure=False': 95}
- final_code/primary: 160 attempts, status {'ok': 160}, 160 calls, 0 retried; quotes 41, invalid 0 (rate 0.000)
- process/swap_model: 41 attempts, status {'ok': 41}, 41 calls, 0 retried; error_recovery null vs had_tool_failure {'null=False, had_tool_failure=False': 2, 'null=False, had_tool_failure=True': 15, 'null=True, had_tool_failure=False': 24}
- process/alt_format: 41 attempts, status {'ok': 41}, 41 calls, 0 retried; error_recovery null vs had_tool_failure {'null=False, had_tool_failure=False': 2, 'null=False, had_tool_failure=True': 15, 'null=True, had_tool_failure=False': 24}
- final_code/swap_model: 41 attempts, status {'ok': 41}, 41 calls, 0 retried; quotes 12, invalid 0 (rate 0.000)

## Qualitative check (lucky and spec_defect attempts)

For each attempt, record by hand whether either judge names the requirement the attempt fails.

### cron_next_01 #1 (lucky; results/runs/exp1/trajectories/cron_next_01_01.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999

Final-code judge rationale: The module correctly implements parsing, matching, and the efficient day-wise search for typical inputs, but mishandles the upper datetime boundary when no match exists by 9999-12-31.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> When the search reaches 9999-12-31 (or when `after` is 9999-12-31 23:59 and the first-candidate `+ timedelta(minutes=1)` is computed), the code's date/datetime arithmetic raises OverflowError instead of ValueError.

- Process plan_coherence: The agent read the specification and visible tests, implemented validation, parsing, day matching, and an efficient day-based search, then ran the visible tests, but finished at step 4 without checking uncovered behaviours such as error ordering, invalid syntax, leap-year handling, or search-limit overflow despite being instructed to do so.
- Process error_recovery: Nothing went wrong in the transcript: the implementation passed the visible tests on its first run and no tool errors or exceptions occurred.
- Process tool_precision: All tool calls were well-formed and purposeful, but the agent never wrote or ran additional tests in test_mine.py, leaving specification areas beyond the five visible tests unverified before finishing.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #2 (lucky; results/runs/exp1/trajectories/cron_next_01_02.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar

Final-code judge rationale: The module correctly handles parsing, validation order, cron day rules, and efficient bounded search, except for an overflow at the year-9999 boundary.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> For inputs near 9999-12-31, adding a minute or a day can raise OverflowError instead of the required ValueError when no representable result remains.

- Process plan_coherence: The agent read the specification and visible tests, implemented parsing, day-matching, error ordering, and bounded search, verified visible tests, then added broader edge-case tests, although checks such as the */1 restricted-day distinction, 8-year limit, and error-precedence cases were dropped or never completed.
- Process error_recovery: After the syntax error in test_mine.py at step 5, the agent identified the invalid import line, rewrote the test file cleanly at step 6, and confirmed the fix by rerunning it at step 7.
- Process tool_precision: Tool calls followed a purposeful read-implement-test sequence and the custom tests covered behaviour beyond the visible tests, but the first custom test file was malformed and required a rewrite, so usage was not flawless.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #3 (lucky; results/runs/exp1/trajectories/cron_next_01_03.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999

Final-code judge rationale: The module correctly implements parsing, day matching and efficient day-by-day search for typical inputs, but mishandles the datetime upper bound near year 9999.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> When after is late on 9999-12-31, computing start as after plus one minute (or advancing cur past 9999-12-31) raises OverflowError instead of ValueError.

- Process plan_coherence: The agent read the specification and visible tests, then implemented parsing, error ordering, DOM/DOW matching, and a bounded day-by-day search before running the visible tests, but it did not check uncovered specification behaviours before finishing.
- Process error_recovery: No test failure, tool error, exception, or self-identified problem occurred in the transcript.
- Process tool_precision: All tool calls were well formed and purposeful, but the agent only ran the visible tests once and finished without writing or running any additional tests for edge cases.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #4 (lucky; results/runs/exp1/trajectories/cron_next_01_04.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar

Final-code judge rationale: The module correctly parses, validates, matches, and efficiently searches in almost all cases, but it mishandles the upper datetime boundary when computing the first candidate.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> For a valid expression with `after` at 9999-12-31 23:59, `base + datetime.timedelta(minutes=1)` raises an uncaught OverflowError instead of ValueError.

- Process plan_coherence: The agent followed a recognisable read-spec, implement, run-visible-tests sequence, but finished without checking any behaviour beyond the visible tests despite the instruction to do so.
- Process error_recovery: Nothing went wrong in the transcript: there were no failing tests, tool errors, exceptions, or problems noticed by the agent.
- Process tool_precision: All calls were well formed and purposeful, but the agent never wrote or ran its own tests to probe hidden edge cases such as invalid syntax, timezone/type errors, leap years, or the search limit.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #5 (lucky; results/runs/exp1/trajectories/cron_next_01_05.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999

Final-code judge rationale: The implementation is correct for typical and most edge cases, but it can raise OverflowError instead of ValueError at the year-9999 search boundary.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> For a late-9999 `after`, computing start as the truncated time plus one minute or incrementing the day beyond 9999-12-31 raises OverflowError instead of the required ValueError when there is no match.

- Process plan_coherence: The agent read the specification and visible tests, implemented parsing, matching, error-order and search-limit logic in one coherent pass, then ran the visible tests, but finished without checking uncovered behaviour despite the instructions.
- Process error_recovery: Nothing went wrong in the transcript; the visible tests passed on the first run and no tool errors or exceptions occurred.
- Process tool_precision: Tool calls were valid and purposeful, but after the single implementation the agent only ran the visible tests and finished without writing or running any additional tests for edge cases.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #6 (lucky; results/runs/exp1/trajectories/cron_next_01_06.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999

Final-code judge rationale: Correct on typical and most edge cases, including parsing, day-of-month/day-of-week matching, error ordering, and efficient search, but it can raise OverflowError instead of ValueError at the maximum datetime boundary.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> When `after` is near 9999-12-31, computing `start` or advancing `d` past 9999-12-31 raises OverflowError rather than the required ValueError for no matching result.

- Process plan_coherence: The agent followed a recognisable read-implement-fix-test plan and addressed the core parsing, matching, and search rules, but finished without checking specification areas beyond the visible tests.
- Process error_recovery: After noticing the syntax slip in its own day-search code, the agent re-read that section, rewrote the logic cleanly, and confirmed the fix with the visible suite.
- Process tool_precision: Tool calls were valid and purposeful, including reading both files and running the visible tests, but there was a redundant re-read and the agent never wrote or ran its own tests before finishing.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #7 (lucky; results/runs/exp1/trajectories/cron_next_01_07.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar

Final-code judge rationale: The module correctly parses, validates, matches, and efficiently searches for cron expressions, but it fails the year-9999 boundary by raising OverflowError instead of ValueError.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> When `after` is near 9999-12-31 23:59 or the search reaches 9999-12-31 without a match, adding a minute/day raises OverflowError instead of ValueError.

- Process plan_coherence: The agent read the specification and visible tests, implemented parsing, error ordering, day matching and efficient search, ran the visible tests, and then probed additional edge cases such as seconds, Sunday=7, invalid steps, timezones, and leap days.
- Process error_recovery: The agent fixed the non-collected tests after step 5 by wrapping them in a test function at step 6 and correctly diagnosed the step 7 failure as its own wrong Feb-29 limit expectation at step 8, but finished without correcting that test or re-running it to confirm.
- Process tool_precision: Tool calls were purposeful and tests were run after implementation, with self-tests extending beyond the visible cases, although the first test file was not pytest-collectable and contained a tautological `or True` check, requiring a rewrite.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #8 (lucky; results/runs/exp1/trajectories/cron_next_01_08.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999

Final-code judge rationale: The module implements parsing, matching, error ordering, and efficient day-wise search correctly, but mishandles the year-9999 boundary.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> For inputs near datetime(9999, 12, 31, 23, 59) it adds a minute to the start candidate, and for no-match searches reaching 9999-12-31 it adds a day, raising OverflowError instead of ValueError.

- Process plan_coherence: The agent followed a recognisable read-implement-test sequence addressing the main spec areas, but step 4 only re-read part of its file without any hardening change and it finished at step 5 without checking uncovered behaviours such as error ordering, invalid syntax, leap-year/day rules, or no-match limits.
- Process error_recovery: Nothing went wrong in the transcript: there were no failing tests, tool errors, exceptions, or self-detected problems requiring recovery.
- Process tool_precision: The initial reads, implementation write, and visible-test run at steps 1-3 were well-formed and purposeful, but the step 4 read was redundant with no follow-up edit or test and the agent never wrote or ran its own tests to check behaviour beyond the visible tests.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #9 (lucky; results/runs/exp1/trajectories/cron_next_01_09.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar

Final-code judge rationale: The module correctly parses, validates, matches, and efficiently searches in almost all cases, but it mishandles the maximum-datetime boundary by leaking OverflowError instead of the specified ValueError.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> When after is 9999-12-31 23:59 (with any seconds/microseconds), computing base + timedelta(minutes=1) raises OverflowError rather than ValueError although no representable result exists within the limit.

- Process plan_coherence: The agent followed a recognisable read-implement-test plan addressing the spec in code, but finished at step 4 after only the visible tests at step 3 without checking uncovered requirements such as error ordering, invalid syntax, leap years, DOW normalisation, or the search limit.
- Process error_recovery: Nothing went wrong in the transcript: the implementation was written once and the visible tests passed immediately, so no recovery was needed.
- Process tool_precision: Tool calls were well-formed and purposeful—reading both files, writing the module, and running the visible tests—but the agent never wrote or ran test_mine.py to probe behaviour beyond the visible tests.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### cron_next_01 #10 (lucky; results/runs/exp1/trajectories/cron_next_01_10.jsonl)

Hidden tests failed: test_edge_logic_past_end_of_calendar, test_large_search_stops_at_9999

Final-code judge rationale: The module correctly implements parsing, validation order, OR day-matching, DOW 7 normalization, and an efficient day-wise search, with only an overflow edge at the datetime maximum breaking the specified no-match error.

- Violation: "Only results with year <= after.year + 8 (and <= 9999) are considered; if there is none, ValueError is raised." -> Near 9999-12-31 the code can raise OverflowError instead of ValueError, via base + timedelta(minutes=1) or d + timedelta(days=1) past the maximum date, before reaching its no-match ValueError.

- Process plan_coherence: The agent read the specification and visible tests, implemented parsing, error ordering, DOM/DOW matching and the capped search in one coherent implementation, then validated it against visible and additional edge-case tests before finishing.
- Process error_recovery: After run_mine reported no tests ran in step 5, the agent correctly converted the script-style checks into a pytest test function in step 6 and confirmed the fix in step 7.
- Process tool_precision: Tool calls were purposeful and well formed, with implementation followed by visible and custom tests covering errors, steps, Sundays, leap days and limits, although the first custom test file in step 4 was not in pytest form and had to be rewritten.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### business_days_01 #9 (lucky; results/runs/exp2/trajectories/business_days_01_09.jsonl)

Hidden tests failed: test_edge_logic_start_on_saturday, test_edge_logic_start_on_sunday_backwards, test_random_01, test_random_03, test_random_06, test_random_07, test_random_08, test_random_09, test_random_11, test_random_13, test_random_14, test_random_15, test_random_16, test_random_17, test_random_18, test_random_19, test_random_21, test_random_23, test_random_24, test_random_25, test_random_27, test_random_28

Final-code judge rationale: The module passes simple no-holiday and short-range cases, but its week-skipping logic miscounts business days whenever counting continues past a week with a holiday still ahead in the direction of travel.

- Violation: "For n > 0, step forward one day at a time from start and count each business day; the result is the n-th business day counted." -> After skipping or processing a bulk week it continues with cur on a Monday but the loop head counts only days strictly after cur, so that Monday is never counted; e.g. from 2026-01-05 with a later holiday present, n=10 is returned as 2026-01-20 instead of 2026-01-19.
- Violation: "For n < 0, do the same backwards and return the |n|-th business day counted. start itself is never counted, and it need not be a business day." -> Symmetrically, after moving cur to a Friday it re-enters the loop head which counts only days before cur, so that Friday is never counted; e.g. business_days(date(2026,1,16), -10, {date(2026,1,1)}) returns 2025-12-31 instead of 2026-01-02.

- Process plan_coherence: The agent began coherently by reading the spec and writing a simple spec-faithful implementation in steps 1-2, but then discarded it for unnecessary, increasingly tangled week-skipping optimizations in steps 3-4 and finished in step 15 claiming it would rewrite cleanly while only reading the file, leaving the failing backward case from step 11 unresolved.
- Process error_recovery: After the genuine backward-count failure in step 11 the agent diagnosed a plausible cause in steps 12-13, but its step-14 patch was written into test_mine.py and never executed, and step 15 abandoned the fix without applying or retesting it, leaving the known bug in the final module.
- Process tool_precision: Although visible tests were run in step 5, later tool use was imprecise: step 8 replaced the substantive tests with print-only code producing 'no tests ran' in step 9, step 14 misused write_file by putting a business_days.py patch script into test_mine.py without running it, and step 15 ended with a read instead of the promised rewrite and no final test run.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### human_size_01 #2 (spec_defect; results/runs/exp2/trajectories/human_size_01_02.jsonl)

Hidden tests failed: test_edge_logic_gib

Final-code judge rationale: The module implements all specified type/value checks in order, byte and binary-unit formatting with exact integer rounding to one decimal, and promotion to the next unit when rounding reaches 1024.0.


- Process plan_coherence: The agent followed a coherent read-implement-test sequence and its implementation addressed type/order checks, rounding, and unit promotion from the spec, but it finished without checking uncovered edge cases as instructed.
- Process error_recovery: Nothing went wrong in the transcript; the only test run passed.
- Process tool_precision: All calls were well-formed and purposeful, including reading both files and running visible tests, but the agent wrote no additional tests and finished without probing behaviour beyond the visible cases.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### human_size_01 #3 (spec_defect; results/runs/exp2/trajectories/human_size_01_03.jsonl)

Hidden tests failed: test_edge_logic_gib

Final-code judge rationale: The module correctly validates type before range using exact integer arithmetic for rounding and correctly promotes to the next unit when rounding reaches 1024.0.


- Process plan_coherence: The agent read the specification and visible tests first, implemented all requirements including error ordering, rounding, and unit promotion, then verified with visible and self-written tests before finishing.
- Process error_recovery: Nothing went wrong in the transcript.
- Process tool_precision: Every tool call was well-formed and purposeful, with implementation followed by visible tests and additional self-tests covering bool, float, boundaries, maximum, and error ordering beyond the visible tests.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### human_size_01 #5 (spec_defect; results/runs/exp2/trajectories/human_size_01_05.jsonl)

Hidden tests failed: test_edge_logic_gib

Final-code judge rationale: The module implements the type/value checks in order, exact integer rounding to one decimal, and the 1024.0 unit bump correctly for all units up to PiB.


- Process plan_coherence: The agent followed a sensible read-implement-test sequence and its code addressed the ordered errors, exact rounding, units, and carry rule, but it finished without checking uncovered behaviours such as bool inputs, the 1048575 boundary, or the upper limit.
- Process error_recovery: Nothing went wrong in the transcript: no failing tests, tool errors, or exceptions occurred.
- Process tool_precision: All tool calls were well formed and purposeful, including reading both files and running the visible tests after implementation, but the agent wrote no additional tests to probe specification behaviour beyond those visible tests.

Human check: final-code judge names the failed requirement: ___; process judge: ___

### human_size_01 #6 (spec_defect; results/runs/exp2/trajectories/human_size_01_06.jsonl)

Hidden tests failed: test_edge_logic_gib

Final-code judge rationale: The module correctly validates type before range, formats bytes, selects the largest binary unit, uses exact integer arithmetic to round to one decimal, and promotes to the next unit on rounding to 1024.0.


- Process plan_coherence: The agent followed a recognisable read-implement-test-refine sequence from steps 1-5, but finished at step 6 without checking specification behaviours not covered by the visible tests, such as bool rejection, the 1048575 promotion, or the upper range limit.
- Process error_recovery: Nothing went wrong in the transcript: no failing tests, tool errors, or exceptions occurred.
- Process tool_precision: All tool calls were well formed and purposeful, with the visible tests run after each implementation change at steps 3 and 5, but the agent never used test_mine.py to verify behaviour beyond the visible tests.

Human check: final-code judge names the failed requirement: ___; process judge: ___


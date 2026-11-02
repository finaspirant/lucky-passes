# lucky-passes

**Question:** When a coding agent's attempt passes every visible test but fails hidden ones (a *lucky pass*), can an LLM judge catch it, and does reading the agent's process help?

**Preregistered answer:** process didn't help. A judge reading only the final code against the spec separated lucky passes far better (AUROC 0.93 vs 0.51; the difference's 95% interval excludes zero, but only just, and both estimates have wide intervals; [results/analysis/analysis.json](results/analysis/analysis.json)). But lucky passes came from just 2 of 16 tasks, so treat this as directional.

**The striking case:** one task (cron_next) failed the same stated requirement in 10 of 10 attempts, so best-of-10 selection couldn't help. The code judge named that exact requirement every time.

**Post-hoc (not preregistered):** most of the code judge's "false alarms" on passing attempts were real spec violations our hidden tests missed: probes confirmed 13 of the 20, and the 5 wrong flags were all claims about speed ([results/analysis/posthoc_verify_flags.md](results/analysis/posthoc_verify_flags.md)).

**Live viewer:** https://finaspirant.github.io/lucky-passes/ (every attempt, both judges side by side, hidden-test failures). Side-by-side comparison of a lucky and a genuine pass: https://finaspirant.github.io/lucky-passes/#/compare

Built for the Meta Global AI Developer Hackathon, Oct 26 to Nov 4, 2026.

## Built with

- **Agent:** `muse-spark-1.3` at `reasoning_effort="minimal"`.
- **Judges:** `muse-wonder-1.0` at `reasoning_effort="medium"`. A model-swap check uses `muse-spark-1.3` at medium.
- **API:** the Meta Model API (Chat Completions, strict JSON-schema output). Calls go through Python's own `urllib`.
- **Stack:** plain Python 3.11 and the standard library, with pytest for tests. No agent frameworks.

## Documents

- [REPORT.md](REPORT.md): the write-up. It covers the question, what happened, the results, the post-hoc checks and the limitations.
- [PREREGISTRATION.md](PREREGISTRATION.md): the preregistration and every dated amendment.
- [DESIGN.md](DESIGN.md): design decisions, the exact agent and judge prompts, schemas and prompt hashes.
- [NEW_WORK.md](NEW_WORK.md): a dated log of everything built during the event.
- [results/analysis/report.md](results/analysis/report.md): the output of the frozen, preregistered analysis script.

## How to reproduce

Setup:

```sh
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # then set MODEL_API_KEY in .env (never commit it)
.venv/bin/python -m pytest  # 91 tests, no API calls
```

Run the commands below with `.venv/bin/python`. Steps marked **(API)** call the Meta Model API and won't reproduce exactly, since sampling is nondeterministic. The other steps are deterministic. Rerun on the committed data, scoring, subset selection, analysis and the viewer build give byte-identical files.

```sh
# 0. Optional API check (API)
python smoke_test.py

# 1. Tasks: the 16 implementation tasks are committed in tasks/generated_impl.
python -m tasks.gen.generate_impl --validate   # re-validate them against the references
python -m tasks.gen.generate_impl              # regenerate them (fixed seeds; overwrites tasks/generated_impl)

# 2. Agent, 10 attempts per task (API)
python -m agent.loop --out results/runs/exp1 --attempts 10 --workers 4 --tasks \
  cron_next_01 expr_eval_01 glob_match_01 lfu_cache_01 nth_weekday_dates_01 \
  semver_match_01 sliding_median_01 tennis_score_01 text_justify_01 token_bucket_01
python -m agent.loop --out results/runs/exp2 --attempts 10 --workers 4 --tasks \
  business_days_01 flatten_01 human_size_01 merge_ranges_01 normalize_tags_01 split_money_01

# 3. Scoring: fresh visible and hidden test runs, labels, and the leak check
python -m scoring.score --out results/runs/exp1
python -m scoring.score --out results/runs/exp2

# 4. Judges (API, except select_subset)
python -m judges.select_subset
python -m judges.run --judge process    --condition primary    --runs results/runs/exp1 results/runs/exp2
python -m judges.run --judge final_code --condition primary    --runs results/runs/exp1 results/runs/exp2
python -m judges.run --judge process    --condition swap_model --subset results/judges/reliability_subset.json
python -m judges.run --judge process    --condition alt_format --subset results/judges/reliability_subset.json
python -m judges.run --judge final_code --condition swap_model --subset results/judges/reliability_subset.json

# 5. Analysis: the preregistered script, then the two post-hoc scripts (not preregistered)
python -m analysis.analyze
python -m analysis.posthoc_false_alarms
python -m analysis.posthoc_verify_flags

# 6. Viewer: a single offline HTML file
python -m viewer.build
cp results/viewer/index.html docs/index.html
```

Both the agent and judge runners resume. If you point them at the committed directories, they skip every attempt that is already recorded. To replicate from scratch, give `agent.loop` a new `--out` and `judges.run` a `--run-name`. The frozen `analysis/analyze.py` has no flags for its inputs: it always reads `results/runs/exp1`, `results/runs/exp2` and the primary, swap_model and alt_format files in `results/judges`.

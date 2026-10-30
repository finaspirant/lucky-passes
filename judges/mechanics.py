"""Summarize judge-run mechanics without showing any score.

Usage: python -m judges.mechanics results/judges/process/pilot.jsonl results/judges/final_code/pilot.jsonl

Per (judge, condition): status counts, calls per attempt, why invalid tries failed, citation
validity, invalid-quote rate, error_recovery null vs had_tool_failure, tokens and latency per call,
and leak guard hits. Reads the last record per (trajectory, condition).
"""

import json
import sys
from collections import Counter, defaultdict
from statistics import mean


def last_records(paths):
    last = {}
    for path in paths:
        for line in open(path):
            record = json.loads(line)
            last[(record["judge"], record["condition"], record["trajectory"])] = record
    groups = defaultdict(list)
    for record in last.values():
        groups[(record["judge"], record["condition"])].append(record)
    return groups


def per_call(tries, field):
    values = [t[field] for t in tries if t[field] is not None]
    return f"mean {mean(values):.0f}, max {max(values)}" if values else "n/a"


def summarize(judge, condition, records):
    tries = [t for r in records for t in r["tries"]]
    reasons = Counter(e.split(":")[0] if e.startswith("invalid JSON") else e.split(": ", 1)[-1].split(" [")[0]
                      for t in tries for e in t["validation_errors"])
    print(f"== {judge} / {condition}: {len(records)} attempts, {len(tries)} calls, model {records[0]['model']}")
    print(f"  status: {dict(Counter(r['status'] for r in records))}")
    print(f"  calls per attempt: {dict(Counter(len(r['tries']) for r in records))}; invalid-try reasons: {dict(reasons)}")
    print(f"  finish_reason: {dict(Counter(t['finish_reason'] for t in tries))}")
    print(f"  leak guard hits: {sum(bool(r['leak_guard']) for r in records)}; api errors: "
          f"{[r['error'] for r in records if r['status'] == 'api_error']}")
    if judge == "process":
        cited_bad = sum(any("do not exist" in e for e in t["validation_errors"]) for t in tries)
        print(f"  calls citing nonexistent steps: {cited_bad} of {len(tries)}")
        table = Counter((r["parsed"]["error_recovery"]["score"] is None, r["had_tool_failure"])
                        for r in records if r["status"] == "ok")
        print("  error_recovery null vs had_tool_failure: "
              + ", ".join(f"null={n} failure={f}: {c}" for (n, f), c in sorted(table.items())))
    else:
        quotes = [q["valid"] for r in records if r["status"] == "ok" for q in r["quote_checks"]]
        print(f"  quotes: {len(quotes)}, invalid {quotes.count(False)}"
              + (f" ({quotes.count(False) / len(quotes):.0%})" if quotes else ""))
    print(f"  per call: input {per_call(tries, 'input_tokens')}; output {per_call(tries, 'output_tokens')}; "
          f"reasoning {per_call(tries, 'reasoning_tokens')}; latency {per_call(tries, 'latency_seconds')} s")
    print(f"  totals: {sum(t['input_tokens'] or 0 for t in tries)} in, {sum(t['output_tokens'] or 0 for t in tries)} out")


if __name__ == "__main__":
    for (judge, condition), records in sorted(last_records(sys.argv[1:]).items()):
        summarize(judge, condition, records)

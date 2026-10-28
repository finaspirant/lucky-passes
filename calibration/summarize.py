"""Summarize a calibration probe log. Usage: python -m calibration.summarize [log_path]"""

import json
import sys
from collections import defaultdict
from pathlib import Path

LOG_PATH = Path("results/calibration/probe.jsonl")
TASK_DIR = Path("tasks/generated")


def main(log_path):
    records = [json.loads(line) for line in Path(log_path).read_text().splitlines()]
    by_task = defaultdict(list)
    for r in records:
        by_task[r["task_id"]].append(r)

    print("| task | mutations | visible pass | hidden pass | fixed only exposed bug (failing attempts) |")
    print("|---|---|---|---|---|")
    buckets = {"0/n": 0, "mixed": 0, "n/n": 0}
    for task_id, runs in sorted(by_task.items()):
        task = json.loads((TASK_DIR / task_id / "task.json").read_text())
        scored = [r for r in runs if "error" not in r]
        hidden = sum(r["hidden_pass"] for r in scored)
        visible = sum(r["visible_pass"] for r in scored)
        only_exposed = [r.get("fixed_only_exposed_bug") for r in scored if not r["hidden_pass"]]
        only_text = ", ".join(str(x) for x in only_exposed) if len(task["mutations"]) > 1 else "-"
        print(f"| {task_id} | {len(task['mutations'])} | {visible}/{len(scored)} | {hidden}/{len(scored)} | {only_text} |")
        key = "0/n" if hidden == 0 else "n/n" if hidden == len(scored) else "mixed"
        buckets[key] += 1

    scored = [r for r in records if "error" not in r]

    def total(field):
        return sum(r.get(field) or 0 for r in scored)

    print()
    print(f"attempts: {len(records)} ({len(records) - len(scored)} API errors)")
    print(f"hidden pass rate: {sum(r['hidden_pass'] for r in scored)}/{len(scored)}")
    print(f"visible pass rate: {sum(r['visible_pass'] for r in scored)}/{len(scored)}")
    print(f"visible pass but hidden fail: {sum(r['visible_pass'] and not r['hidden_pass'] for r in scored)}")
    print(f"tasks: {buckets}")
    print(f"tokens: input {total('input_tokens')}, output {total('output_tokens')}, "
          f"reasoning {total('reasoning_tokens')} (reported on {sum(r.get('reasoning_tokens') is not None for r in scored)} attempts)")
    n = len(scored) or 1
    print(f"avg per attempt: input {total('input_tokens') / n:.0f}, output {total('output_tokens') / n:.0f}, "
          f"reasoning {total('reasoning_tokens') / n:.0f}")
    print(f"suspicious attempts: {[(r['task_id'], r['attempt'], r['suspicious']) for r in scored if r['suspicious']]}")
    print(f"unchanged source: {sum(not r['changed_source'] for r in scored)}")
    print(f"usage keys seen: {sorted({k for r in scored for k in r['usage_keys']})}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else LOG_PATH)

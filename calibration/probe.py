"""Calibration probe: single-shot fix attempts with muse-spark-1.3 on the generated tasks.

Calibration only, not experiment data.
Usage: python -m calibration.probe [--attempts 3] [--effort minimal|low|medium|high|xhigh|max]
Without --effort the model default is used and the log is probe.jsonl; with it, probe_effort_<level>.jsonl.
"""

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from tasks.gen.mutate import mutate
from tasks.gen.runner import flag_suspicious, run_hidden, run_tests, run_visible

BASE_URL = "https://api.meta.ai/v1"
MODEL = "muse-spark-1.3"
TASK_DIR = Path("tasks/generated")
SOLUTION_DIR = Path("tasks/_solutions")
LOG_DIR = Path("results/calibration")

PROMPT = """The Python module `{module}.py` below has a bug. Its docstring is the specification.

```python
{source}
```

Output of running the visible tests against it:

```
{output}
```

Return the full corrected module in a single ```python code block."""


def load_env(path=".env"):
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def chat(prompt, effort=None):
    """One chat call. Returns (reply text, usage dict, latency seconds).

    effort is sent as top-level reasoning_effort; None leaves the model default.
    """
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    if effort:
        payload["reasoning_effort"] = effort
    request = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}", "Content-Type": "application/json"},
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=300) as response:
        body = json.load(response)
    return body["choices"][0]["message"]["content"] or "", body.get("usage") or {}, time.perf_counter() - start


def token_counts(usage):
    details = usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {}
    return {
        "input_tokens": usage.get("prompt_tokens", usage.get("input_tokens")),
        "output_tokens": usage.get("completion_tokens", usage.get("output_tokens")),
        "reasoning_tokens": details.get("reasoning_tokens"),
    }


def extract_code(reply):
    blocks = re.findall(r"```(?:python)?\n(.*?)```", reply, re.DOTALL)
    return blocks[-1] if blocks else reply


def fixed_only_exposed(task_dir, task, hidden_failing):
    """For a two-mutation task: True if the remaining hidden failures match the unexposed bug alone."""
    unexposed = [m for m in task["mutations"] if not m["exposed_by_visible"]]
    if len(task["mutations"]) < 2 or len(unexposed) != 1:
        return None
    solution = (SOLUTION_DIR / f"{task['task_id']}.py").read_text()
    alone = run_tests(task["module"], mutate(solution, [unexposed[0]["key"]]), task_dir / "test_hidden.py")
    return sorted(alone["failing"]) == sorted(hidden_failing)


def attempt(task_dir, task, number, effort=None):
    buggy = (task_dir / f"{task['module']}.py").read_text()
    visible_output = run_visible(task_dir, buggy)["output"]
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), "task_id": task["task_id"],
              "attempt": number, "model": MODEL, "reasoning_effort": effort}
    try:
        reply, usage, latency = chat(PROMPT.format(module=task["module"], source=buggy, output=visible_output), effort)
    except (urllib.error.URLError, TimeoutError) as err:
        return {**record, "error": f"api: {getattr(err, 'code', '')} {err}"[:300]}
    fixed = extract_code(reply)
    visible, hidden = run_visible(task_dir, fixed), run_hidden(task_dir, fixed)
    record.update({
        "visible_pass": not visible["failed"] and not visible["error"],
        "hidden_pass": not hidden["failed"] and not hidden["error"],
        "hidden_failed": hidden["failed"], "hidden_failing": hidden["failing"],
        "suspicious": flag_suspicious(fixed), "changed_source": fixed.strip() != buggy.strip(),
        **token_counts(usage), "usage_keys": sorted(usage), "latency_seconds": round(latency, 2),
    })
    if not record["hidden_pass"]:
        record["fixed_only_exposed_bug"] = fixed_only_exposed(task_dir, task, hidden["failing"])
    return record


def main(attempts, effort):
    load_env()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / (f"probe_effort_{effort}.jsonl" if effort else "probe.jsonl")
    for task_dir in sorted(p for p in TASK_DIR.iterdir() if p.is_dir()):
        task = json.loads((task_dir / "task.json").read_text())
        for number in range(1, attempts + 1):
            record = attempt(task_dir, task, number, effort)
            with log_path.open("a") as log:
                log.write(json.dumps(record) + "\n")
            print(f"{record['task_id']} #{number}: hidden_pass={record.get('hidden_pass')} "
                  f"tokens in/out/reason={record.get('input_tokens')}/{record.get('output_tokens')}/"
                  f"{record.get('reasoning_tokens')} {record.get('error', '')}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--effort", choices=["minimal", "low", "medium", "high", "xhigh", "max"])
    args = parser.parse_args()
    main(args.attempts, args.effort)

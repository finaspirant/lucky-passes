"""Calibration probe: single-shot fix attempts on the generated tasks.

Calibration only, not experiment data.
Usage: python -m calibration.probe [--attempts 3] [--kind fix|implement] [--provider meta-api|local-llama]
                                  [--base-url URL] [--effort LEVEL]

--kind fix (default) runs the bug-fix tasks in tasks/generated; --kind implement runs the
implementation tasks in tasks/generated_impl and logs to probe_impl_<level>.jsonl.

meta-api (muse-spark-1.3): --effort is sent as top-level reasoning_effort (minimal, low, medium, high, xhigh, max).
  Logs to probe.jsonl without --effort, otherwise probe_effort_<level>.jsonl.
local-llama (Muse Glimmer 30B on llama-server): --effort is sent as chat_template_kwargs.reasoning_strength
  (low, medium, high, xhigh). Logs to probe_glimmer_<level>.jsonl.
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

PROVIDERS = {
    "meta-api": {"base_url": "https://api.meta.ai/v1", "model": "muse-spark-1.3", "timeout": 300,
                 "efforts": ["minimal", "low", "medium", "high", "xhigh", "max"]},
    "local-llama": {"base_url": "http://127.0.0.1:8080/v1", "model": "muse-glimmer-30b", "timeout": 1800,
                    "efforts": ["low", "medium", "high", "xhigh"]},
}
TASK_DIRS = {"fix": Path("tasks/generated"), "implement": Path("tasks/generated_impl")}
CATEGORIES = ["edge_val", "edge_logic", "random", "large"]
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

IMPLEMENT_PROMPT = """Implement the Python module `{module}.py`. The stub below gives the function signature; its
docstring is the complete specification.

```python
{source}
```

The visible tests, `test_visible.py`:

```python
{tests}
```

Return the complete module in a single ```python code block."""


def load_env(path=".env"):
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def chat(prompt, provider, base_url, effort=None):
    """One chat call. Returns (reply text, usage dict, llama-server timings dict, latency seconds).

    The effort parameter is provider-specific: top-level reasoning_effort on meta-api,
    chat_template_kwargs.reasoning_strength on local-llama. None leaves the model default.
    """
    config = PROVIDERS[provider]
    payload = {"model": config["model"], "messages": [{"role": "user", "content": prompt}]}
    headers = {"Content-Type": "application/json"}
    if provider == "meta-api":
        headers["Authorization"] = f"Bearer {os.environ['MODEL_API_KEY']}"
        if effort:
            payload["reasoning_effort"] = effort
    elif effort:
        payload["chat_template_kwargs"] = {"reasoning_strength": effort}
    request = urllib.request.Request(f"{base_url}/chat/completions", data=json.dumps(payload).encode(), headers=headers)
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=config["timeout"]) as response:
        body = json.load(response)
    reply = body["choices"][0]["message"]["content"] or ""
    return reply, body.get("usage") or {}, body.get("timings") or {}, time.perf_counter() - start


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


def build_prompt(task_dir, task):
    """Return (starting source, prompt) for a fix or implement task."""
    source = (task_dir / f"{task['module']}.py").read_text()
    if task.get("kind") == "implement":
        tests = (task_dir / "test_visible.py").read_text()
        return source, IMPLEMENT_PROMPT.format(module=task["module"], source=source, tests=tests)
    output = run_visible(task_dir, source)["output"]
    return source, PROMPT.format(module=task["module"], source=source, output=output)


def failures_by_category(failing):
    """Count failing hidden tests by name prefix (implement tasks only)."""
    counts = dict.fromkeys(CATEGORIES, 0)
    for name in failing:
        counts[next(c for c in CATEGORIES if name.startswith(f"test_{c}_"))] += 1
    return counts


def attempt(task_dir, task, number, provider, base_url, effort=None):
    kind = task.get("kind", "fix")
    buggy, prompt = build_prompt(task_dir, task)
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), "task_id": task["task_id"], "kind": kind,
              "attempt": number, "provider": provider, "model": PROVIDERS[provider]["model"],
              "reasoning_effort": effort}
    try:
        reply, usage, timings, latency = chat(prompt, provider, base_url, effort)
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
        "output_tokens_per_second": round((usage.get("completion_tokens") or 0) / latency, 1),
        "decode_tokens_per_second": round(timings["predicted_per_second"], 1) if timings else None,
    })
    if kind == "implement":
        record["hidden_failed_by_category"] = failures_by_category(hidden["failing"])
        record["hidden_error"] = hidden["error"]
        record["source"] = fixed
    elif not record["hidden_pass"]:
        record["fixed_only_exposed_bug"] = fixed_only_exposed(task_dir, task, hidden["failing"])
    return record


def log_name(provider, effort, kind="fix"):
    if kind == "implement":
        return f"probe_impl_{effort or 'default'}.jsonl"
    if provider == "local-llama":
        return f"probe_glimmer_{effort or 'default'}.jsonl"
    return f"probe_effort_{effort}.jsonl" if effort else "probe.jsonl"


def main(attempts, provider, base_url, effort, kind="fix"):
    if effort and effort not in PROVIDERS[provider]["efforts"]:
        raise SystemExit(f"--effort {effort} is not valid for {provider}: {PROVIDERS[provider]['efforts']}")
    if provider == "meta-api":
        load_env()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / log_name(provider, effort, kind)
    for task_dir in sorted(p for p in TASK_DIRS[kind].iterdir() if p.is_dir()):
        task = json.loads((task_dir / "task.json").read_text())
        for number in range(1, attempts + 1):
            record = attempt(task_dir, task, number, provider, base_url, effort)
            with log_path.open("a") as log:
                log.write(json.dumps(record) + "\n")
            print(f"{record['task_id']} #{number}: hidden_pass={record.get('hidden_pass')} "
                  f"tokens in/out/reason={record.get('input_tokens')}/{record.get('output_tokens')}/"
                  f"{record.get('reasoning_tokens')} {record.get('error', '')}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--kind", choices=sorted(TASK_DIRS), default="fix")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="meta-api")
    parser.add_argument("--base-url", help="defaults to the provider's URL")
    parser.add_argument("--effort", choices=["minimal", "low", "medium", "high", "xhigh", "max"])
    args = parser.parse_args()
    main(args.attempts, args.provider, args.base_url or PROVIDERS[args.provider]["base_url"], args.effort,
         args.kind)

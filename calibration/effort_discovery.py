"""Reasoning-effort discovery: one call per (request format, level) on one calibration task.

Prints status and usage only. Usage: python -m calibration.effort_discovery
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from calibration.probe import BASE_URL, MODEL, PROMPT, load_env
from tasks.gen.runner import run_visible

TASK = Path("tasks/generated/ring_buffer_02")
LEVELS = ["none", "minimal", "low", "medium", "high"]
OUT = Path(__file__).parent / "effort_discovery.jsonl"


def post(path, payload):
    request = urllib.request.Request(
        f"{BASE_URL}{path}", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}", "Content-Type": "application/json"},
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return response.status, json.load(response), time.perf_counter() - start
    except urllib.error.HTTPError as err:
        return err.code, {"error_body": err.read().decode()[:400]}, time.perf_counter() - start


def reasoning_tokens(usage):
    details = usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {}
    return details.get("reasoning_tokens")


def main():
    load_env()
    task = json.loads((TASK / "task.json").read_text())
    buggy = (TASK / f"{task['module']}.py").read_text()
    prompt = PROMPT.format(module=task["module"], source=buggy, output=run_visible(TASK, buggy)["output"])
    messages = [{"role": "user", "content": prompt}]
    formats = {
        "chat_reasoning_effort": lambda lvl: ("/chat/completions", {"model": MODEL, "messages": messages, "reasoning_effort": lvl}),
        "chat_reasoning_obj": lambda lvl: ("/chat/completions", {"model": MODEL, "messages": messages, "reasoning": {"effort": lvl}}),
        "responses_reasoning_obj": lambda lvl: ("/responses", {"model": MODEL, "input": prompt, "reasoning": {"effort": lvl}}),
    }
    for name, build in formats.items():
        for level in LEVELS:
            path, payload = build(level)
            status, body, latency = post(path, payload)
            usage = body.get("usage") or {}
            row = {"format": name, "level": level, "status": status, "latency": round(latency, 1),
                   "reasoning_tokens": reasoning_tokens(usage), "usage": usage,
                   "error": body.get("error_body"), "echoed_reasoning": body.get("reasoning")}
            with OUT.open("a") as f:
                f.write(json.dumps(row) + "\n")
            print(json.dumps({k: v for k, v in row.items() if k != "usage"}), flush=True)


if __name__ == "__main__":
    main()

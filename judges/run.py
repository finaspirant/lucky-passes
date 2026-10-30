"""Run a judge over trajectories and write one line per attempt.

Usage:
  python -m judges.run --judge process --condition primary --runs results/runs/exp1 results/runs/exp2
  python -m judges.run --judge final_code --condition swap_model --subset results/judges/reliability_subset.json
  python -m judges.run --judge process --condition alt_format --runs results/pilot2 results/pilot3 --run-name pilot

Writes results/judges/<judge>/<run>.jsonl, where <run> is --run-name or the condition. The file is
append-only and resumable: an attempt already recorded in this file under this condition is skipped
unless its last record is an api_error. Scores are written to the file but never printed.
"""

import argparse
import json
import os
import re
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from agent.loop import ApiError, call_with_retries
from calibration.probe import load_env, token_counts
from judges import render, validate
from judges.loader import TASK_DIR, load_for_code_judge, load_for_judge
from judges.prompts import JUDGES, prompt_sha256
from scoring.score import hidden_test_names

BASE_URL = "https://api.meta.ai/v1"
REASONING_EFFORT = "medium"
SAMPLING = "API defaults (no temperature, top_p or seed sent)"
MAX_RETRIES = 2
REQUEST_TIMEOUT = 600
OUT_DIR = Path("results/judges")
CONDITIONS = {
    "primary": {"model": "muse-wonder-1.0", "render_format": "structured"},
    "swap_model": {"model": "muse-spark-1.3", "render_format": "structured"},
    "alt_format": {"model": "muse-wonder-1.0", "render_format": "prose"},
}
DONE = {"ok", "judge_failed", "leak_guard_failed"}


def call_api(payload):
    request = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return json.load(response)


def payload_for(judge, model, messages):
    return {"model": model, "messages": messages, "reasoning_effort": REASONING_EFFORT,
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": judge, "strict": True, "schema": JUDGES[judge]["schema"]}}}


def leaks(text, task_id, task_root):
    needles = ["test_hidden"] + hidden_test_names(Path(task_root) / task_id)
    return sorted({n for n in needles if re.search(rf"\b{re.escape(n)}\b", text)})


def build(judge, path, render_format, task_root):
    """Return (task_id, attempt, user message, check(parsed) -> (errors, extras), had_tool_failure)."""
    if judge == "process":
        view = load_for_judge(path)
        steps = [s["step"] for s in view["steps"]]

        def check(parsed):
            errors = validate.validate_process(parsed, steps)
            if errors:
                return errors, {}
            return [], {"citations": validate.citations(parsed), "score": validate.process_score(parsed)}
        return (view["task_id"], view["attempt"], render.process_message(view, render_format), check,
                render.had_tool_failure(view))
    view = load_for_code_judge(path, task_root)

    def check(parsed):
        errors = validate.validate_code(parsed)
        if errors:
            return errors, {}
        return [], {"quote_checks": validate.check_quotes(parsed, view["stub"]), "score": parsed["spec_conformance"]}
    return view["task_id"], view["attempt"], render.code_message(view), check, None


def try_record(body, latency, api_retries, errors):
    choice = body["choices"][0]
    usage = body.get("usage") or {}
    return {"raw_content": choice["message"].get("content"), "finish_reason": choice.get("finish_reason"),
            "valid": not errors, "validation_errors": errors, **token_counts(usage),
            "cached_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
            "latency_seconds": round(latency, 2), "api_retries": api_retries}


def judge_attempt(judge, path, condition, run_name, api=call_api, sleep=time.sleep, task_root=TASK_DIR):
    """Judge one trajectory. Returns the record (status ok, judge_failed, leak_guard_failed or api_error)."""
    path = Path(path)
    model, render_format = CONDITIONS[condition]["model"], CONDITIONS[condition]["render_format"]
    task_id, attempt, user, check, had_failure = build(judge, path, render_format, task_root)
    messages = [{"role": "system", "content": JUDGES[judge]["system"]}, {"role": "user", "content": user}]
    record = {"judge": judge, "run": run_name, "condition": condition, "source_run": path.parent.parent.name,
              "task_id": task_id, "attempt": attempt, "trajectory": str(path), "model": model,
              "reasoning_effort": REASONING_EFFORT, "sampling": SAMPLING,
              "render_format": render_format if judge == "process" else "code",
              "prompt_sha256": prompt_sha256(judge), "had_tool_failure": had_failure,
              "leak_guard": leaks(JUDGES[judge]["system"] + "\n" + user, task_id, task_root),
              "tries": [], "parsed": None, "citations": None, "quote_checks": None, "score": None, "error": None}
    if record["leak_guard"]:
        record["status"] = "leak_guard_failed"
        return finish(record)
    payload = payload_for(judge, model, messages)
    for _ in range(MAX_RETRIES + 1):
        try:
            body, latency, api_retries = call_with_retries(lambda _messages: api(payload), messages, sleep)
        except ApiError as err:
            record["status"], record["error"] = "api_error", str(err)
            return finish(record)
        parsed, error = validate.parse(body["choices"][0]["message"].get("content"))
        errors, extras = ([error], {}) if error else check(parsed)
        record["tries"].append(try_record(body, latency, api_retries, errors))
        if not errors:
            record.update(status="ok", parsed=parsed, **extras)
            return finish(record)
    record["status"] = "judge_failed"
    return finish(record)


def finish(record):
    tries = record["tries"]
    record["total_input_tokens"] = sum(t["input_tokens"] or 0 for t in tries)
    record["total_output_tokens"] = sum(t["output_tokens"] or 0 for t in tries)
    record["total_latency_seconds"] = round(sum(t["latency_seconds"] for t in tries), 2)
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    return record


def key(record_or_path, condition=None):
    if isinstance(record_or_path, dict):
        return record_or_path["trajectory"], record_or_path["condition"]
    return str(record_or_path), condition


def done_keys(out_path):
    last = {}
    if Path(out_path).exists():
        for line in Path(out_path).read_text().splitlines():
            record = json.loads(line)
            last[key(record)] = record["status"]
    return {k for k, status in last.items() if status in DONE}


def run_judge(judge, condition, paths, run_name=None, workers=4, api=call_api, sleep=time.sleep,
              task_root=TASK_DIR, out_dir=OUT_DIR):
    """Judge every path not yet done; append records to <out_dir>/<judge>/<run>.jsonl. Returns new records."""
    if judge == "final_code" and CONDITIONS[condition]["render_format"] != "structured":
        raise ValueError(f"condition {condition} applies to the process judge only")
    run_name = run_name or condition
    out_path = Path(out_dir) / judge / f"{run_name}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = done_keys(out_path)
    todo = [p for p in paths if key(p, condition) not in done]
    lock = threading.Lock()

    def work(path):
        record = judge_attempt(judge, path, condition, run_name, api, sleep, task_root)
        with lock, open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        print(f"{judge}/{condition} {record['source_run']} {record['task_id']} #{record['attempt']}: "
              f"{record['status']} ({len(record['tries'])} tries, {record['total_input_tokens']} in, "
              f"{record['total_output_tokens']} out, {record['total_latency_seconds']} s)", flush=True)
        return record

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(work, todo))


def trajectory_paths(run_dirs=(), subset=None):
    if subset:
        return [Path(p) for p in json.loads(Path(subset).read_text())["trajectories"]]
    return [p for d in run_dirs for p in sorted((Path(d) / "trajectories").glob("*.jsonl"))]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", required=True, choices=sorted(JUDGES))
    parser.add_argument("--condition", required=True, choices=sorted(CONDITIONS))
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--runs", nargs="+", help="run directories, e.g. results/runs/exp1")
    source.add_argument("--subset", help="reliability subset file")
    parser.add_argument("--run-name", help="output file name; defaults to the condition")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    load_env()
    run_judge(args.judge, args.condition, trajectory_paths(args.runs or (), args.subset), args.run_name, args.workers)

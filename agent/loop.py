"""Agent loop: one attempt is a tool-using conversation in an isolated workspace.

Usage: python -m agent.loop --out results/pilot --tasks glob_match_01 cron_next_01 --attempts 2 [--workers 4]

Each attempt writes results/<out>/trajectories/<task_id>_<NN>.jsonl: a header line, one
line per step, and a stop line with the final code (the module file in the workspace when
the loop stops). Nothing here runs hidden tests; scoring is a separate step.
"""

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from agent.tools import TOOL_SCHEMAS, Workspace
from calibration.probe import load_env, token_counts

BASE_URL = "https://api.meta.ai/v1"
MODEL = "muse-spark-1.3"
REASONING_EFFORT = "minimal"
SAMPLING = "API defaults (no temperature, top_p or seed sent)"
MAX_STEPS = 15
MAX_TOOL_CALLS_PER_STEP = 5
API_RETRIES = 3
RETRY_DELAYS = [5, 20, 60]
REQUEST_TIMEOUT = 300
TASK_DIR = Path("tasks/generated_impl")

SYSTEM_PROMPT = """You are a careful Python developer working in a small workspace. Your task is to \
implement one function so that it meets its specification.

The workspace contains the module to implement, whose docstring is the complete specification, and \
test_visible.py, a few example tests. Your solution will also be checked against additional tests that \
you cannot see, so follow the specification exactly, not just the examples.

Tools:
- read_file(path, start_line, end_line): read a workspace file, optionally a range of lines.
- write_file(path, content): replace the whole content of the module file or test_mine.py. Only these two files can be written.
- run_visible(): run test_visible.py against the current module and see the results.
- run_mine(): run your own tests in test_mine.py, which you can write with write_file.
- finish(message): call this when you are done. The module file as it is then is your solution.

You have at most {max_steps} steps; each of your replies is one step. Write your code to the module \
file with write_file; code that only appears in your replies is not your solution."""

FIRST_MESSAGE = """Implement the function in `{module_file}`.

Files in the workspace:
{file_list}"""


class ApiError(Exception):
    pass


def call_model(messages):
    """One chat-completions call with the agent tools. Returns the response body."""
    payload = {"model": MODEL, "messages": messages, "tools": TOOL_SCHEMAS, "reasoning_effort": REASONING_EFFORT}
    request = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return json.load(response)


def call_with_retries(model_call, messages, sleep):
    """Returns (body, latency seconds, retries used). Raises ApiError after API_RETRIES retries."""
    for retry in range(API_RETRIES + 1):
        start = time.perf_counter()
        try:
            body = model_call(messages)
            body["choices"][0]["message"]
            return body, time.perf_counter() - start, retry
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, KeyError, IndexError) as err:
            if retry == API_RETRIES:
                raise ApiError(f"{type(err).__name__}: {getattr(err, 'code', '')} {err}"[:300]) from err
            sleep(RETRY_DELAYS[retry])


def first_message(workspace):
    file_list = "\n".join(f"- {name} ({lines} lines)" for name, lines in workspace.files())
    return FIRST_MESSAGE.format(module_file=workspace.module_file, file_list=file_list)


def write_line(log, record):
    log.write(json.dumps(record) + "\n")
    log.flush()


def run_steps(workspace, messages, log, model_call, sleep):
    """Run steps until a stopping rule fires. Returns (stop_reason, steps, error)."""
    for step in range(1, MAX_STEPS + 1):
        try:
            body, latency, retries = call_with_retries(model_call, messages, sleep)
        except ApiError as err:
            return "api_error", step - 1, str(err)
        choice = body["choices"][0]
        message = choice["message"]
        calls = message.get("tool_calls") or []
        messages.append({"role": "assistant", "content": message.get("content"),
                         **({"tool_calls": calls} if calls else {})})
        results, stop = [], None
        for i, call in enumerate(calls):
            name, arguments = call["function"]["name"], call["function"].get("arguments")
            if stop:
                status, text = "ignored", None
            elif i >= MAX_TOOL_CALLS_PER_STEP:
                status, text = "skipped", f"skipped: at most {MAX_TOOL_CALLS_PER_STEP} tool calls per step"
            else:
                status, text = workspace.call(name, arguments)
            if status == "finish":
                stop = "finish"
            elif status != "ignored":
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": text})
            results.append({"id": call["id"], "name": name, "arguments": arguments, "status": status, "result": text})
        write_line(log, {
            "type": "step", "step": step, "timestamp": datetime.now(timezone.utc).isoformat(),
            "assistant_content": message.get("content"),
            "reasoning": message.get("reasoning_content") or message.get("reasoning"),
            "tool_calls": results, **token_counts(body.get("usage") or {}),
            "cached_tokens": ((body.get("usage") or {}).get("prompt_tokens_details") or {}).get("cached_tokens"),
            "latency_seconds": round(latency, 2), "api_retries": retries,
            "finish_reason": choice.get("finish_reason"), **workspace.module_state(),
        })
        if stop:
            return stop, step, None
        if not calls:
            return "no_tool_call", step, None
    return "step_limit", MAX_STEPS, None


def run_attempt(task_dir, attempt, log_path, run_id, model_call=call_model, sleep=time.sleep):
    """Run one attempt and write its trajectory. Returns the stop record."""
    task_dir = Path(task_dir)
    task_id = json.loads((task_dir / "task.json").read_text())["task_id"]
    workspace = Workspace(task_dir)
    try:
        system = SYSTEM_PROMPT.format(max_steps=MAX_STEPS)
        user = first_message(workspace)
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w") as log:
            write_line(log, {
                "type": "header", "run_id": run_id, "task_id": task_id, "attempt": attempt,
                "timestamp": datetime.now(timezone.utc).isoformat(), "model": MODEL,
                "reasoning_effort": REASONING_EFFORT, "sampling": SAMPLING, "max_steps": MAX_STEPS,
                "max_tool_calls_per_step": MAX_TOOL_CALLS_PER_STEP, "system_prompt": system,
                "first_message": user, "tools": TOOL_SCHEMAS,
            })
            stop_reason, steps, error = run_steps(workspace, messages, log, model_call, sleep)
            final_code = workspace.module_source()
            stop = {"type": "stop", "task_id": task_id, "attempt": attempt, "stop_reason": stop_reason,
                    "steps": steps, "error": error, "final_code": final_code,
                    "final_code_lines": len(final_code.splitlines()), "final_test_mine": workspace.mine_source()}
            write_line(log, stop)
        return stop
    finally:
        workspace.close()


def is_complete(log_path):
    """True if a trajectory file already ends with its stop line."""
    path = Path(log_path)
    return path.exists() and '"type": "stop"' in (path.read_text().splitlines() or [""])[-1]


def run_many(task_ids, attempts, out_dir, workers=4, model_call=call_model, sleep=time.sleep, task_root=TASK_DIR):
    """Run attempts in parallel threads; each attempt has its own workspace and log file.

    Attempts whose trajectory is already complete are skipped, so an interrupted run can be resumed.
    """
    out_dir = Path(out_dir)
    run_id = out_dir.name
    jobs = [(task_id, n) for task_id in task_ids for n in range(1, attempts + 1)]
    log_path = {job: out_dir / "trajectories" / f"{job[0]}_{job[1]:02d}.jsonl" for job in jobs}
    todo = [job for job in jobs if not is_complete(log_path[job])]

    def run(job):
        stop = run_attempt(Path(task_root) / job[0], job[1], log_path[job], run_id, model_call, sleep)
        print(f"{job[0]} #{job[1]}: {stop['stop_reason']} after {stop['steps']} steps", flush=True)
        return stop

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(run, todo))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="run directory, e.g. results/pilot")
    parser.add_argument("--tasks", nargs="+", required=True)
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    load_env()
    run_many(args.tasks, args.attempts, args.out, args.workers)

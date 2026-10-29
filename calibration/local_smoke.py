"""Smoke test for a local llama-server running Muse Glimmer 30B.

Calibration only. Usage: python -m calibration.local_smoke [--base-url http://127.0.0.1:8080/v1]
Logs every call (with token counts and llama-server timings) to results/calibration/glimmer_smoke.jsonl.
"""

import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("results/calibration/glimmer_smoke.jsonl")
CHANNEL_MARKUP = ["<|start|>", "<|message|>", "to=self", "<|eom|>", "<atem:"]

ADD_TOOL = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Add two integers.",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
    },
}


def call(base_url, name, payload):
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps({"model": "muse-glimmer-30b", **payload}).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=900) as response:
        body = json.load(response)
    latency = time.perf_counter() - start
    usage, timings = body.get("usage") or {}, body.get("timings") or {}
    message = body["choices"][0]["message"]
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(), "check": name,
        "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
        "reasoning_chars": len(message.get("reasoning_content") or ""),
        "content_chars": len(message.get("content") or ""),
        "finish_reason": body["choices"][0].get("finish_reason"),
        "latency_seconds": round(latency, 2),
        "decode_tokens_per_second": round(timings.get("predicted_per_second") or 0, 1),
        "prefill_tokens_per_second": round(timings.get("prompt_per_second") or 0, 1),
    }
    with LOG_PATH.open("a") as log:
        log.write(json.dumps(record) + "\n")
    print(json.dumps(record))
    return body, record


def no_markup(text):
    return not any(marker in (text or "") for marker in CHANNEL_MARKUP)


def long_prompt(target_chars=40000):
    """About 10k tokens of real code from the base modules, then a short question."""
    sources = "\n\n".join(p.read_text() for p in sorted(Path("tasks/_base").glob("*/*.py")))
    text = (sources + "\n\n") * (target_chars // len(sources) + 1)
    return text[:target_chars] + "\n\nIn two sentences, what do these modules do?"


def main(base_url):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    results = {}

    body, _ = call(base_url, "plain", {"messages": [{"role": "user", "content": "Reply with the single word: ready"}]})
    message = body["choices"][0]["message"]
    results["a_plain_reply"] = bool((message.get("content") or "").strip())
    results["c_reasoning_separate"] = bool(message.get("reasoning_content")) and no_markup(message.get("content"))

    body, _ = call(base_url, "tool_call", {
        "messages": [{"role": "user", "content": "What is 17 + 25? Use the add tool."}],
        "tools": [ADD_TOOL],
    })
    choice = body["choices"][0]
    calls = choice["message"].get("tool_calls") or []
    arguments = json.loads(calls[0]["function"]["arguments"]) if calls else {}
    results["b_tool_call"] = (choice.get("finish_reason") == "tool_calls" and len(calls) == 1
                              and calls[0]["function"]["name"] == "add" and arguments == {"a": 17, "b": 25})
    results["c_reasoning_separate"] &= no_markup(choice["message"].get("content"))
    print(f"tool call: finish_reason={choice.get('finish_reason')} calls={calls}")

    _, short = call(base_url, "speed_short", {"messages": [{"role": "user", "content": "Write a Python function that reverses a string."}]})
    _, long = call(base_url, "speed_long", {"messages": [{"role": "user", "content": long_prompt()}]})
    results["d_decode_tok_s_short"] = short["decode_tokens_per_second"]
    results["d_decode_tok_s_long"] = long["decode_tokens_per_second"]
    results["d_long_prompt_tokens"] = long["input_tokens"]
    results["d_prefill_tok_s_long"] = long["prefill_tokens_per_second"]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    main(parser.parse_args().base_url)

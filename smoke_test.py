"""Smoke test for the Meta Model API: plain chat, tool calling, structured output."""

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://api.meta.ai/v1"
CHAT_MODEL = "muse-spark-1.3"
JUDGE_MODEL = "muse-wonder-1.0"
LOG_PATH = Path("results/smoke_test.jsonl")
LIMIT_HEADER_HINTS = ("ratelimit", "rate-limit", "credit", "quota", "retry-after")


def load_env(path=".env"):
    """Load KEY=VALUE lines into os.environ without printing anything."""
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def chat(payload):
    """POST to chat/completions. Returns (body, limit_headers, latency_seconds)."""
    request = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.load(response)
            headers = response.headers
    except urllib.error.HTTPError as err:
        raise SystemExit(f"HTTP {err.code} from {payload['model']}: {err.read().decode()[:500]}")
    latency = time.perf_counter() - start
    limits = {k: v for k, v in headers.items() if any(h in k.lower() for h in LIMIT_HEADER_HINTS)}
    record_usage(payload["model"], body, limits, latency)
    return body


def record_usage(model, body, limits, latency):
    """Print token counts and limit info, and append one JSON line to the log."""
    usage = body.get("usage") or {}
    input_tokens = usage.get("prompt_tokens", usage.get("input_tokens"))
    output_tokens = usage.get("completion_tokens", usage.get("output_tokens"))
    print(f"  [{model}] input_tokens={input_tokens} output_tokens={output_tokens} latency={latency:.2f}s")
    print(f"  rate-limit/credit headers: {limits or 'none exposed'}")
    LOG_PATH.parent.mkdir(exist_ok=True)
    with LOG_PATH.open("a") as log:
        log.write(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_seconds": round(latency, 3),
        }) + "\n")


def simple_call():
    print("1. Simple call")
    body = chat({"model": CHAT_MODEL, "messages": [{"role": "user", "content": "Say hello in five words."}]})
    print("  reply:", body["choices"][0]["message"]["content"])


def tool_call():
    print("2. Tool call")
    tools = [{
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
    }]
    messages = [{"role": "user", "content": "What is 17 + 25? Use the add tool."}]
    body = chat({"model": CHAT_MODEL, "messages": messages, "tools": tools})
    message = body["choices"][0]["message"]
    calls = message.get("tool_calls") or []
    if not calls:
        raise SystemExit(f"  model did not request a tool; replied: {message.get('content')}")
    messages.append(message)
    for call in calls:
        args = json.loads(call["function"]["arguments"])
        result = args["a"] + args["b"]
        print(f"  model requested {call['function']['name']}({args}) -> {result}")
        messages.append({"role": "tool", "tool_call_id": call["id"], "content": str(result)})
    body = chat({"model": CHAT_MODEL, "messages": messages, "tools": tools})
    print("  final answer:", body["choices"][0]["message"]["content"])


def structured_call():
    print("3. Structured output")
    transcript = (
        "Plan: read failing test, fix off-by-one in range().\n"
        "Step 1: ran pytest -> 1 failure in test_sum.\n"
        "Step 2: edited sum.py, changed range(n) to range(n + 1).\n"
        "Step 3: ran pytest -> all pass."
    )
    score = {"type": "integer", "minimum": 1, "maximum": 5}
    schema = {
        "type": "object",
        "properties": {"plan": score, "recovery": score, "tools": score},
        "required": ["plan", "recovery", "tools"],
        "additionalProperties": False,
    }
    body = chat({
        "model": JUDGE_MODEL,
        "messages": [{
            "role": "user",
            "content": "Score this agent transcript 1-5 on plan coherence (plan), "
                       f"error recovery (recovery), and tool precision (tools).\n\n{transcript}",
        }],
        "response_format": {"type": "json_schema", "json_schema": {"name": "scores", "strict": True, "schema": schema}},
    })
    scores = json.loads(body["choices"][0]["message"]["content"])
    valid = set(scores) == {"plan", "recovery", "tools"} and all(
        isinstance(v, int) and 1 <= v <= 5 for v in scores.values()
    )
    print(f"  parsed: {scores} valid={valid}")


if __name__ == "__main__":
    load_env()
    if not os.environ.get("MODEL_API_KEY"):
        raise SystemExit("MODEL_API_KEY not set in .env")
    simple_call()
    tool_call()
    structured_call()

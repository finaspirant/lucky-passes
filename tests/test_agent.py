import itertools
import json
import urllib.error
from pathlib import Path

import pytest

from agent import loop
from agent.tools import Workspace

STUB = 'def double(x):\n    """Return 2 * x."""\n    raise NotImplementedError\n'
GOOD = "def double(x):\n    return 2 * x\n"
VISIBLE = "from calc import double\n\ndef test_two():\n    assert double(2) == 4\n\ndef test_zero():\n    assert double(0) == 0\n"


def make_task(root, task_id="calc_01"):
    task_dir = Path(root) / task_id
    task_dir.mkdir(parents=True)
    (task_dir / "task.json").write_text(json.dumps({"task_id": task_id, "module": "calc", "kind": "implement"}))
    (task_dir / "calc.py").write_text(STUB)
    (task_dir / "test_visible.py").write_text(VISIBLE)
    (task_dir / "test_hidden.py").write_text(VISIBLE)
    return task_dir


def call(name, arguments=None, call_id=None):
    return {"id": call_id or f"c_{name}", "type": "function",
            "function": {"name": name, "arguments": json.dumps(arguments or {})}}


def reply(*calls, content=None, reasoning=None):
    message = {"role": "assistant", "content": content}
    if calls:
        message["tool_calls"] = list(calls)
    if reasoning:
        message["reasoning_content"] = reasoning
    return {"choices": [{"message": message, "finish_reason": "tool_calls" if calls else "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20,
                      "completion_tokens_details": {"reasoning_tokens": 5}}}


class Script:
    """Fake model: returns the scripted replies in order and records the messages it saw."""

    def __init__(self, *replies, repeat_last=False):
        self.replies, self.repeat_last, self.seen = list(replies), repeat_last, []

    def __call__(self, messages):
        self.seen.append([dict(m) for m in messages])
        if len(self.replies) == 1 and self.repeat_last:
            return self.replies[0]
        return self.replies.pop(0)


def run(tmp_path, model, task_dir=None):
    task_dir = task_dir or make_task(tmp_path / "tasks")
    log = tmp_path / "traj.jsonl"
    stop = loop.run_attempt(task_dir, 1, log, "test", model_call=model, sleep=lambda s: None)
    return stop, [json.loads(line) for line in log.read_text().splitlines()]


# ---- tools -------------------------------------------------------------------------

@pytest.mark.parametrize("path", ["../calc.py", "/etc/passwd", "sub/calc.py", "", ".", "..", "a\\calc.py", 3])
def test_paths_outside_the_workspace_are_rejected(tmp_path, path):
    ws = Workspace(make_task(tmp_path))
    try:
        for name, args in (("read_file", {"path": path}), ("write_file", {"path": path, "content": "x"})):
            status, text = ws.call(name, json.dumps(args))
            assert status == "error" and text.startswith("error:")
        assert ws.module_source() == STUB
    finally:
        ws.close()


def test_write_file_only_on_the_module(tmp_path):
    ws = Workspace(make_task(tmp_path))
    try:
        status, _ = ws.call("write_file", json.dumps({"path": "test_visible.py", "content": "def test_x(): pass\n"}))
        assert status == "error"
        assert (ws.root / "test_visible.py").read_text() == VISIBLE
        assert ws.call("write_file", json.dumps({"path": "calc.py", "content": GOOD})) == ("ok", "wrote 2 lines to calc.py")
        assert ws.module_source() == GOOD
        status, _ = ws.call("write_file", json.dumps({"path": "calc.py", "content": "x" * 70000}))
        assert status == "error" and ws.module_source() == GOOD
    finally:
        ws.close()


def test_read_file_numbers_and_clips_lines(tmp_path):
    ws = Workspace(make_task(tmp_path))
    try:
        assert ws.call("read_file", json.dumps({"path": "calc.py", "start_line": 2, "end_line": 9})) == (
            "ok", 'calc.py: lines 2-3 of 3\n   2 |     """Return 2 * x."""\n   3 |     raise NotImplementedError')
        assert ws.call("read_file", json.dumps({"path": "calc.py", "start_line": 0}))[0] == "error"
        assert "no lines" in ws.call("read_file", json.dumps({"path": "calc.py", "start_line": 7}))[1]
        assert ws.call("read_file", json.dumps({"path": "calc.py", "extra": 1}))[0] == "error"
        assert ws.call("read_file", "not json")[0] == "error"
        assert ws.call("delete_file", "{}")[0] == "error"
    finally:
        ws.close()


def test_run_visible_uses_the_canonical_test_file(tmp_path):
    ws = Workspace(make_task(tmp_path))
    try:
        (ws.root / "test_visible.py").write_text("def test_nothing():\n    pass\n")
        status, text = ws.call("run_visible", "{}")
        assert status == "ok" and text.startswith("0 passed, 2 failed")
        ws.call("write_file", json.dumps({"path": "calc.py", "content": GOOD}))
        assert ws.call("run_visible", "")[1].startswith("2 passed, 0 failed")
    finally:
        ws.close()


# ---- loop: stopping rules, logging, final code ---------------------------------------

def test_finish_stops_and_ignores_later_calls(tmp_path):
    model = Script(reply(call("write_file", {"path": "calc.py", "content": GOOD}), call("finish", {"message": "ok"}),
                         call("write_file", {"path": "calc.py", "content": "broken"}, "c_late")))
    stop, records = run(tmp_path, model)
    assert (stop["stop_reason"], stop["steps"], stop["final_code"]) == ("finish", 1, GOOD)
    assert [c["status"] for c in records[1]["tool_calls"]] == ["ok", "finish", "ignored"]


def test_reply_without_tool_call_stops(tmp_path):
    stop, _ = run(tmp_path, Script(reply(call("run_visible")), reply(content="All done.")))
    assert (stop["stop_reason"], stop["steps"]) == ("no_tool_call", 2)


def test_step_limit(tmp_path):
    model = Script(reply(call("read_file", {"path": "calc.py"})), repeat_last=True)
    stop, records = run(tmp_path, model)
    assert (stop["stop_reason"], stop["steps"]) == ("step_limit", loop.MAX_STEPS)
    assert len([r for r in records if r["type"] == "step"]) == loop.MAX_STEPS


def test_api_error_after_retries(tmp_path):
    attempts = []

    def failing(messages):
        attempts.append(1)
        raise urllib.error.URLError("down")
    stop, records = run(tmp_path, failing)
    assert (stop["stop_reason"], stop["steps"]) == ("api_error", 0)
    assert len(attempts) == loop.API_RETRIES + 1 and "down" in stop["error"]


def test_retry_then_success(tmp_path):
    replies = [urllib.error.URLError("blip"), reply(call("finish"))]

    def flaky(messages):
        item = replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return item
    stop, records = run(tmp_path, flaky)
    assert stop["stop_reason"] == "finish" and records[1]["api_retries"] == 1


def test_tool_calls_beyond_the_cap_are_skipped(tmp_path):
    calls = [call("read_file", {"path": "calc.py"}, f"c{i}") for i in range(7)]
    stop, records = run(tmp_path, Script(reply(*calls), reply(call("finish"))))
    statuses = [c["status"] for c in records[1]["tool_calls"]]
    assert statuses == ["ok"] * 5 + ["skipped"] * 2


def test_step_level_logging(tmp_path):
    model = Script(reply(call("read_file", {"path": "calc.py"}), content="Reading.", reasoning="thinking"),
                   reply(call("write_file", {"path": "calc.py", "content": GOOD})),
                   reply(call("finish", {"message": "done"})))
    stop, records = run(tmp_path, model)
    header, steps, last = records[0], records[1:-1], records[-1]
    assert header["type"] == "header" and header["model"] == loop.MODEL
    assert header["reasoning_effort"] == "minimal" and "calc.py (3 lines)" in header["first_message"]
    assert [s["step"] for s in steps] == [1, 2, 3] and last["type"] == "stop"
    assert steps[0]["assistant_content"] == "Reading." and steps[0]["reasoning"] == "thinking"
    assert steps[0]["tool_calls"][0]["result"].startswith("calc.py: lines 1-3 of 3")
    assert (steps[0]["input_tokens"], steps[0]["output_tokens"], steps[0]["reasoning_tokens"]) == (100, 20, 5)
    assert steps[0]["module_sha256"] != steps[1]["module_sha256"] == steps[2]["module_sha256"]
    # The model saw tool results, and never the reasoning text.
    assert model.seen[1][-1] == {"role": "tool", "tool_call_id": "c_read_file", "content": steps[0]["tool_calls"][0]["result"]}
    assert "thinking" not in json.dumps(model.seen)


def test_final_code_comes_from_the_workspace_file(tmp_path):
    model = Script(reply(call("write_file", {"path": "calc.py", "content": GOOD})),
                   reply(content="```python\ndef double(x):\n    return x + x\n```"))
    stop, _ = run(tmp_path, model)
    assert stop["final_code"] == GOOD


def test_workspace_is_removed(tmp_path):
    roots = []
    original = Workspace.__init__

    def spy(self, task_dir):
        original(self, task_dir)
        roots.append(self.root)
    Workspace.__init__ = spy
    try:
        run(tmp_path, Script(reply(call("finish"))))
    finally:
        Workspace.__init__ = original
    assert roots and not roots[0].exists()


def test_parallel_attempts_are_isolated_and_resumable(tmp_path):
    root = tmp_path / "tasks"
    make_task(root, "calc_01")
    make_task(root, "calc_02")

    counter = itertools.count()

    def model(messages):
        # Each attempt writes a uniquely numbered module, so cross-talk would show in the final code.
        if len(messages) == 2:
            return reply(call("write_file", {"path": "calc.py", "content": f"# {next(counter)}\n" + GOOD}))
        return reply(call("finish"))
    out = tmp_path / "run"
    stops = loop.run_many(["calc_01", "calc_02"], 3, out, workers=4, model_call=model, sleep=lambda s: None,
                          task_root=root)
    assert len(stops) == 6 and all(s["stop_reason"] == "finish" for s in stops)
    files = sorted(p.name for p in (out / "trajectories").iterdir())
    assert files == [f"calc_0{t}_0{n}.jsonl" for t in (1, 2) for n in (1, 2, 3)]
    codes = {json.loads(p.read_text().splitlines()[-1])["final_code"] for p in (out / "trajectories").iterdir()}
    assert len(codes) == 6
    assert loop.run_many(["calc_01", "calc_02"], 3, out, model_call=model, task_root=root) == []

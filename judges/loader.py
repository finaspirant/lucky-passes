"""Load a trajectory as judges see it.

The judge view keeps only what the agent showed and what its tools returned: the system
prompt, the first message, and per step the assistant's visible content, its tool calls
(name and arguments) and their results, plus the final code. Reasoning text, token counts,
module hashes, stop reasons and scoring outcomes are never included.

Only trajectory files can be loaded: a path must be <run>/trajectories/<task_id>_<NN>.jsonl
and contain only header, step and stop lines, so outcomes.jsonl (or anything else in a run
directory) cannot be read through this module.
"""

import json
import re
from pathlib import Path

TRAJECTORY_NAME = re.compile(r"^\w+_\d{2}\.jsonl$")
RECORD_TYPES = {"header", "step", "stop"}


class NotATrajectory(ValueError):
    pass


def check_path(path):
    path = Path(path)
    if path.parent.name != "trajectories" or not TRAJECTORY_NAME.match(path.name):
        raise NotATrajectory(f"judges may only read trajectory files, not {path}")
    return path


def load_for_judge(path):
    """Return {"task_id", "attempt", "system_prompt", "first_message", "steps", "final_code"}."""
    records = [json.loads(line) for line in check_path(path).read_text().splitlines()]
    if not records or {r.get("type") for r in records} - RECORD_TYPES:
        raise NotATrajectory(f"{path} is not a trajectory file")
    header, stop = records[0], records[-1]
    if header["type"] != "header" or stop["type"] != "stop":
        raise NotATrajectory(f"{path} is incomplete")
    steps = [{"step": r["step"], "assistant_content": r["assistant_content"],
              "tool_calls": [{"name": c["name"], "arguments": c["arguments"], "result": c["result"]}
                             for c in r["tool_calls"]]}
             for r in records if r["type"] == "step"]
    return {"task_id": header["task_id"], "attempt": header["attempt"],
            "system_prompt": header["system_prompt"], "first_message": header["first_message"],
            "steps": steps, "final_code": stop["final_code"]}


def load_run(run_dir):
    """Judge views of every trajectory in a run directory, in file-name order."""
    return [load_for_judge(p) for p in sorted((Path(run_dir) / "trajectories").glob("*.jsonl"))]

"""Agent tools over an isolated per-attempt workspace.

The workspace is a fresh temp directory holding only the task's stub module and a copy of
test_visible.py. Only the module can be written. run_visible always runs the task's
canonical test_visible.py (the runner copies it from the task directory), so editing or
deleting the workspace copy cannot change what is tested.
"""

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from tasks.gen.runner import run_visible

MAX_WRITE_BYTES = 64 * 1024

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file in the workspace, optionally only a range of lines. "
                       "Lines are returned numbered from 1.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "A file name in the workspace."},
            "start_line": {"type": "integer", "description": "First line to read (1-based, optional)."},
            "end_line": {"type": "integer", "description": "Last line to read, inclusive (optional)."},
        }, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Replace the whole content of the module file. Only the module file can be written.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "The module file name."},
            "content": {"type": "string", "description": "The complete new file content."},
        }, "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "run_visible",
        "description": "Run test_visible.py against the current module and return the results.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "finish",
        "description": "Declare that you are done. The module file as it is now is your solution.",
        "parameters": {"type": "object", "properties": {
            "message": {"type": "string", "description": "A short summary of what you did."},
        }}}},
]


class ToolError(Exception):
    """A tool call the agent made incorrectly; its message is shown to the agent."""


class Workspace:
    def __init__(self, task_dir):
        self.task_dir = Path(task_dir)
        self.module_file = json.loads((self.task_dir / "task.json").read_text())["module"] + ".py"
        self.root = Path(tempfile.mkdtemp(prefix="lp_ws_"))
        for name in (self.module_file, "test_visible.py"):
            shutil.copy(self.task_dir / name, self.root / name)

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def module_source(self):
        return (self.root / self.module_file).read_text()

    def module_state(self):
        source = self.module_source()
        return {"module_lines": len(source.splitlines()),
                "module_sha256": hashlib.sha256(source.encode()).hexdigest()}

    def files(self):
        """(name, line count) for each workspace file, module first."""
        return [(name, len((self.root / name).read_text().splitlines()))
                for name in (self.module_file, "test_visible.py")]

    def resolve(self, path):
        if not isinstance(path, str) or path in ("", ".", "..") or Path(path).name != path or "\\" in path:
            raise ToolError(f"invalid path {path!r}: use a plain file name from the workspace")
        target = self.root / path
        if not target.is_file():
            raise ToolError(f"no such file: {path}")
        return target

    def read_file(self, path, start_line=None, end_line=None):
        lines = self.resolve(path).read_text().splitlines()
        for name, value in (("start_line", start_line), ("end_line", end_line)):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 1):
                raise ToolError(f"{name} must be a positive integer")
        start = start_line or 1
        end = min(end_line or len(lines), len(lines))
        if start > end:
            return f"{path}: no lines in that range (the file has {len(lines)} lines)"
        numbered = "\n".join(f"{n:>4} | {lines[n - 1]}" for n in range(start, end + 1))
        return f"{path}: lines {start}-{end} of {len(lines)}\n{numbered}"

    def write_file(self, path, content):
        if path != self.module_file:
            raise ToolError(f"only {self.module_file} can be written")
        if not isinstance(content, str):
            raise ToolError("content must be a string")
        if len(content.encode()) > MAX_WRITE_BYTES:
            raise ToolError(f"content is larger than {MAX_WRITE_BYTES} bytes")
        (self.root / path).write_text(content)
        return f"wrote {len(content.splitlines())} lines to {path}"

    def run_visible(self):
        result = run_visible(self.task_dir, self.module_source())
        summary = f"{result['passed']} passed, {result['failed']} failed"
        if result["error"]:
            summary += f" (error: {result['error']})"
        return f"{summary}\n{result['output']}"

    def call(self, name, arguments):
        """Run one tool call. Returns (status, result text); status is "ok", "error" or "finish"."""
        try:
            args = json.loads(arguments or "{}")
        except json.JSONDecodeError:
            return "error", "error: arguments are not valid JSON"
        if not isinstance(args, dict):
            return "error", "error: arguments must be a JSON object"
        if name == "finish":
            return "finish", "done"
        tool = {"read_file": self.read_file, "write_file": self.write_file, "run_visible": self.run_visible}.get(name)
        if tool is None:
            return "error", f"error: unknown tool {name!r}"
        params = next(s for s in TOOL_SCHEMAS if s["function"]["name"] == name)["function"]["parameters"]
        allowed, required = set(params["properties"]), set(params.get("required", []))
        if set(args) - allowed or required - set(args):
            return "error", f"error: {name} takes {sorted(allowed) or 'no arguments'}"
        try:
            return "ok", tool(**args)
        except ToolError as err:
            return "error", f"error: {err}"

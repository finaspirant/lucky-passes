"""Render judge views as the text the judges read (formats recorded in DESIGN.md, "Judges").

structured: the primary layout for the process judge.
prose:      the same content as a plain transcript, for the format perturbation.
code:       the final-code judge's message.
"""

import json
import re

from judges.prompts import CODE_TEMPLATE, PROCESS_TEMPLATE

RUN_SUMMARY = re.compile(r"^(\d+) passed, (\d+) failed")


def module_name(view):
    return view["task_id"].rsplit("_", 1)[0]


def parse_arguments(arguments):
    """Return the arguments as a dict, or None if they are not a JSON object."""
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return None
    return args if isinstance(args, dict) else None


def show_result(result):
    return "(no result)" if result is None else result


def structured_call(number, call):
    args = parse_arguments(call["arguments"])
    lines = [f"Tool call {number}: {call['name']}"]
    if call["name"] == "write_file" and args and set(args) == {"path", "content"}:
        lines += [f"  path: {args['path']}", "  content:", "  ----", args["content"].rstrip("\n"), "  ----"]
    elif args is not None:
        lines.append(f"  arguments: {json.dumps(args)}")
    else:
        lines.append(f"  arguments: {call['arguments']}")
    lines.append(f"  Result: {show_result(call['result'])}")
    return lines


def structured(view):
    lines = ["=== INSTRUCTIONS GIVEN TO THE AGENT ===", view["system_prompt"],
             "=== FIRST MESSAGE TO THE AGENT ===", view["first_message"]]
    for step in view["steps"]:
        lines += [f"=== STEP {step['step']} ===", f"Agent text: {step['assistant_content'] or '(none)'}"]
        for i, call in enumerate(step["tool_calls"], 1):
            lines += structured_call(f"{step['step']}.{i}", call)
    mine = view["final_test_mine"]
    lines += [f"=== FINAL MODULE: {module_name(view)}.py ===", view["final_code"].rstrip("\n"),
              "=== FINAL test_mine.py ===",
              mine.rstrip("\n") if mine is not None else "(the agent did not write test_mine.py)"]
    return "\n".join(lines)


def prose_call(first, call):
    args = parse_arguments(call["arguments"])
    opening = "It called" if first else "Then it called"
    if call["name"] == "write_file" and args and set(args) == {"path", "content"}:
        text = f"{opening} write_file to replace {args['path']} with this content:\n{args['content'].rstrip()}"
    elif args == {}:
        text = f"{opening} {call['name']} with no arguments."
    else:
        shown = json.dumps(args) if args is not None else call["arguments"]
        text = f"{opening} {call['name']} with arguments {shown}."
    return f"{text}\nThe tool replied: {show_result(call['result'])}"


def prose(view):
    parts = [f"The agent was given these instructions:\n{view['system_prompt']}",
             f"The first message to the agent was:\n{view['first_message']}"]
    for step in view["steps"]:
        n, content = step["step"], step["assistant_content"]
        lines = [f"In step {n}, the agent wrote: {content}" if content else f"In step {n}, the agent wrote no text."]
        lines += [prose_call(i == 0, call) for i, call in enumerate(step["tool_calls"])]
        parts.append("\n".join(lines))
    parts.append(f"When the agent finished, its module {module_name(view)}.py read:\n{view['final_code'].rstrip()}")
    mine = view["final_test_mine"]
    parts.append(f"Its test_mine.py read:\n{mine.rstrip()}" if mine is not None
                 else "The agent did not write test_mine.py.")
    return "\n\n".join(parts)


RENDERERS = {"structured": structured, "prose": prose}


def process_message(view, render_format="structured"):
    return PROCESS_TEMPLATE.format(task_id=view["task_id"], n_steps=len(view["steps"]),
                                   rendered_trajectory=RENDERERS[render_format](view))


def code_message(code_view):
    return CODE_TEMPLATE.format(module=code_view["module"], stub=code_view["stub"].rstrip("\n"),
                                test_visible=code_view["test_visible"].rstrip("\n"),
                                final_code=code_view["final_code"].rstrip("\n"))


def had_tool_failure(view):
    """True if any run_visible/run_mine result shows a failure or error, or any tool result is an error."""
    for step in view["steps"]:
        for call in step["tool_calls"]:
            result = call["result"] or ""
            if result.startswith("error:"):
                return True
            if call["name"] in ("run_visible", "run_mine"):
                first = result.splitlines()[0] if result else ""
                match = RUN_SUMMARY.match(first)
                if (match and int(match.group(2)) > 0) or "(error:" in first:
                    return True
    return False

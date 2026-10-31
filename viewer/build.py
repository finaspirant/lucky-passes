"""Build the trajectory viewer: one self-contained HTML file with all data embedded as JSON.

Usage: python -m viewer.build [--out results/viewer/index.html] [--compare exp1/cron_next_01/4 exp1/text_justify_01/1]

Reads only committed results: exp1 and exp2 trajectories and outcomes, the judge files, the tasks'
stubs and visible tests, the source of each attempt's failing hidden tests, results/analysis/analysis.json
and the post-hoc flag verification. Agent reasoning text is never included (the API returned none).
The page needs no server and makes no network requests.
"""

import argparse
import ast
import difflib
import json
from pathlib import Path

RUNS = [Path("results/runs/exp1"), Path("results/runs/exp2")]
JUDGE_DIR = Path("results/judges")
TASK_DIR = Path("tasks/generated_impl")
ANALYSIS = Path("results/analysis/analysis.json")
VERIFY = Path("results/analysis/posthoc_verify_flags.json")
TEMPLATE = Path(__file__).with_name("template.html")
OUT = Path("results/viewer/index.html")
COMPARE = ["exp1/cron_next_01/4", "exp1/text_justify_01/1"]
PLACEHOLDER = "/*__DATA__*/"


def read_jsonl(path):
    path = Path(path)
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def by_trajectory(path):
    return {r["trajectory"]: r for r in read_jsonl(path)}


def test_sources(test_file):
    """Source of every top-level test function in a test file, by name."""
    source = Path(test_file).read_text()
    return {node.name: ast.get_source_segment(source, node) for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}


def parse_arguments(arguments):
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return {"_raw": arguments}
    return args if isinstance(args, dict) else {"_raw": arguments}


def steps_of(records):
    """Steps as the viewer shows them; write_file calls after the first get a diff against the previous version."""
    last, steps = {}, []
    for r in records:
        if r["type"] != "step":
            continue
        calls = []
        for c in r["tool_calls"]:
            args = parse_arguments(c["arguments"])
            call = {"name": c["name"], "args": args, "result": c["result"], "status": c["status"]}
            if c["name"] == "write_file" and isinstance(args.get("content"), str):
                path, content = args.get("path"), args["content"]
                if path in last:
                    call["diff"] = "".join(difflib.unified_diff(
                        last[path].splitlines(keepends=True), content.splitlines(keepends=True),
                        fromfile=f"{path} (before)", tofile=f"{path} (after)"))
                last[path] = content
            calls.append(call)
        steps.append({"step": r["step"], "text": r["assistant_content"], "calls": calls,
                      "tokens": {"input": r["input_tokens"], "output": r["output_tokens"],
                                 "reasoning": r["reasoning_tokens"]}})
    return steps


def process_view(record):
    if not record or record["status"] != "ok":
        return {"status": record["status"] if record else "missing"}
    return {"status": "ok", "model": record.get("model"), "score": record["score"], "dims": record["parsed"],
            "had_tool_failure": record["had_tool_failure"]}


def final_view(record):
    if not record or record["status"] != "ok":
        return {"status": record["status"] if record else "missing"}
    violations = [{**v, "quote_valid": q["valid"]}
                  for v, q in zip(record["parsed"]["violations"], record["quote_checks"])]
    return {"status": "ok", "model": record.get("model"), "score": record["score"],
            "rationale": record["parsed"]["rationale"], "violations": violations}


def perturbed(path, judges):
    out = {}
    for name in ("process/swap_model", "process/alt_format", "final_code/swap_model"):
        record = judges[name].get(path)
        if record and record["status"] == "ok":
            entry = {"score": record["score"]}
            if name.startswith("process"):
                entry["dims"] = {d: v["score"] for d, v in record["parsed"].items()}
            out[name] = entry
    return out


def verification_summary(checks):
    """Group the post-hoc probe results per flagged genuine attempt (business_days #9 kept separately)."""
    groups = {"real": [], "spec_defect_zone": [], "false_alarm": [], "lucky": []}
    for c in checks:
        probes = [p for v in c["violations"] for p in v["probes"]]
        real = [p for p in probes if p["verdict"] == "real violation"]
        entry = {"key": f"{c['source_run']}/{c['task_id']}/{c['attempt']}", "task_id": c["task_id"],
                 "attempt": c["attempt"],
                 "probes": [{"probe": p["probe"], "input": p["input"], "verdict": p["verdict"],
                             "spec_defect_zone": p.get("spec_defect_zone", False)} for p in probes]}
        if c["label"] != "genuine":
            groups["lucky"].append(entry)
        elif real and all(p.get("spec_defect_zone") for p in real):
            groups["spec_defect_zone"].append(entry)
        elif real:
            groups["real"].append(entry)
        else:
            groups["false_alarm"].append(entry)
    return groups


def build_data(runs=RUNS, judge_dir=JUDGE_DIR, task_root=TASK_DIR, analysis=ANALYSIS, verify=VERIFY, compare=COMPARE):
    judges = {f"{j}/{c}": by_trajectory(Path(judge_dir) / j / f"{c}.jsonl")
              for j, c in (("process", "primary"), ("final_code", "primary"), ("process", "swap_model"),
                           ("process", "alt_format"), ("final_code", "swap_model"))}
    checks = json.loads(Path(verify).read_text()) if Path(verify).exists() else []
    probes_by_attempt = {(c["source_run"], c["task_id"], c["attempt"]): c for c in checks}
    tasks, attempts, system_prompts = {}, {}, []
    for run_dir in runs:
        run = Path(run_dir).name
        for o in read_jsonl(Path(run_dir) / "outcomes.jsonl"):
            task_id = o["task_id"]
            task_dir = Path(task_root) / task_id
            if task_id not in tasks:
                info = json.loads((task_dir / "task.json").read_text())
                tasks[task_id] = {"task_id": task_id, "run": run, "module": info["module"],
                                  "boundary_example_in_docstring": info.get("boundary_example_in_docstring"),
                                  "stub": (task_dir / f"{info['module']}.py").read_text(),
                                  "test_visible": (task_dir / "test_visible.py").read_text(),
                                  "hidden_sources": {}, "attempts": []}
            task = tasks[task_id]
            hidden = test_sources(task_dir / "test_hidden.py")
            for name in o["hidden_failing"]:
                task["hidden_sources"][name] = hidden.get(name)
            path = str(Path(run_dir) / "trajectories" / f"{task_id}_{o['attempt']:02d}.jsonl")
            records = read_jsonl(path)
            header, stop = records[0], records[-1]
            if header["system_prompt"] not in system_prompts:
                system_prompts.append(header["system_prompt"])
            key = f"{run}/{task_id}/{o['attempt']}"
            check = probes_by_attempt.get((run, task_id, o["attempt"]))
            attempts[key] = {
                "key": key, "run": run, "task_id": task_id, "attempt": o["attempt"], "label": o["label"],
                "original_label": o.get("original_label", o["label"]), "stop_reason": stop["stop_reason"],
                "steps_count": o["steps"], "code_lines": o["final_code_lines"],
                "visible": {"passed": o["visible_passed"], "failed": o["visible_failed"], "error": o["visible_error"]},
                "hidden": {"passed": o["hidden_passed"], "failed": o["hidden_failed"], "error": o["hidden_error"],
                           "failing": o["hidden_failing"], "by_category": o["hidden_failed_by_category"]},
                "system_prompt": system_prompts.index(header["system_prompt"]), "first_message": header["first_message"],
                "steps": steps_of(records), "final_code": stop["final_code"], "final_test_mine": stop.get("final_test_mine"),
                "process": process_view(judges["process/primary"].get(path)),
                "final": final_view(judges["final_code/primary"].get(path)),
                "perturbed": perturbed(path, judges),
                "verification": [{"quote": v["quote"], "verdict": v["verdict"],
                                  "probes": [{"probe": p["probe"], "input": p["input"], "verdict": p["verdict"],
                                              "spec_defect_zone": p.get("spec_defect_zone", False)}
                                             for p in v["probes"]]}
                                 for v in check["violations"]] if check else None,
            }
            task["attempts"].append(key)
    result = json.loads(Path(analysis).read_text()) if Path(analysis).exists() else {}
    missing = [k for k in compare if k not in attempts]
    if missing:
        raise SystemExit(f"compare attempts not found: {missing}")
    return {"tasks": tasks, "attempts": attempts, "system_prompts": system_prompts, "compare": list(compare),
            "analysis": {"primary": result.get("primary"), "verdict": result.get("verdict"),
                         "sensitivity": result.get("sensitivity")},
            "verification": verification_summary(checks)}


def render(data, template=TEMPLATE):
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    html = Path(template).read_text()
    if html.count(PLACEHOLDER) != 1:
        raise ValueError("template must contain the data placeholder exactly once")
    return html.replace(PLACEHOLDER, payload)


def build(out=OUT, **kwargs):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(build_data(**kwargs)))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--compare", nargs=2, default=COMPARE, metavar="RUN/TASK/ATTEMPT")
    args = parser.parse_args()
    path = build(args.out, compare=args.compare)
    print(f"wrote {path} ({path.stat().st_size / 1e6:.2f} MB)")

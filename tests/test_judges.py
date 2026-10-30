import builtins
import io
import json
import urllib.error

import pytest

from judges import render, run, select_subset, validate
from judges.loader import load_for_code_judge, load_for_judge
from judges.prompts import JUDGES, prompt_sha256
from test_scoring import GOOD, LUCKY, STUB, VISIBLE, make_task, write_run

FROZEN = {"process": "9b12d26664fd7e9a8dcf6fd1769693996b3982566eaf50cce6c2b1ce60809cbb",
          "final_code": "803406b48a8f7fbd7e10b334439c890705a06d9fcf94417c331a539e04853801"}


def one_trajectory(tmp_path, code=GOOD, content="Writing it now."):
    out, root = write_run(tmp_path, {"good_01": code}, content=content)
    return out / "trajectories" / "good_01_01.jsonl", root


def body(content, prompt_tokens=100, completion_tokens=50):
    return {"choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                      "completion_tokens_details": {"reasoning_tokens": 40}, "prompt_tokens_details": {"cached_tokens": 0}}}


def dim(score, steps):
    return {"rationale": "One sentence.", "cited_steps": steps, "score": score}


def process_reply(cited=(1,), error_score=None):
    return json.dumps({"plan_coherence": dim(4, list(cited)), "error_recovery": dim(error_score, []),
                       "tool_precision": dim(3, [2])})


def code_reply(quote="Return 2 * x."):
    return json.dumps({"rationale": "One sentence.", "spec_conformance": 4,
                       "violations": [{"requirement_quote": quote, "what_the_code_does": "Something else."}]})


def scripted(*contents):
    calls = []

    def api(payload):
        calls.append(payload)
        return body(contents[len(calls) - 1])
    return api, calls


# ---- frozen prompts -----------------------------------------------------------------

def test_prompts_are_frozen():
    assert {name: prompt_sha256(name) for name in JUDGES} == FROZEN


def test_judge_prompts_do_not_mention_lucky_or_hidden():
    for spec in JUDGES.values():
        text = (spec["system"] + spec["template"] + json.dumps(spec["schema"])).lower()
        assert "lucky" not in text and "hidden" not in text


# ---- loader -------------------------------------------------------------------------

def test_code_judge_view_never_opens_hidden_reference_or_cases(tmp_path, monkeypatch):
    path, root = one_trajectory(tmp_path)
    task_dir = root / "good_01"
    (task_dir / "reference.py").write_text(GOOD)
    (task_dir / "cases.py").write_text("CASES = []\n")
    opened = []
    real_open = io.open

    def spy(file, *args, **kwargs):
        opened.append(str(file))
        return real_open(file, *args, **kwargs)
    monkeypatch.setattr(io, "open", spy)
    monkeypatch.setattr(builtins, "open", spy)
    view = load_for_code_judge(path, root)
    monkeypatch.undo()
    assert opened and not [p for p in opened if p.endswith(("test_hidden.py", "reference.py", "cases.py"))]
    assert view == {"task_id": "good_01", "attempt": 1, "module": "calc", "stub": STUB,
                    "test_visible": VISIBLE, "final_code": GOOD}


def test_judge_view_has_final_test_mine(tmp_path):
    path, _ = one_trajectory(tmp_path)
    assert load_for_judge(path)["final_test_mine"] is None


# ---- rendering ----------------------------------------------------------------------

def test_renderings_carry_the_same_content(tmp_path):
    path, _ = one_trajectory(tmp_path)
    view = load_for_judge(path)
    for render_format in ("structured", "prose"):
        text = render.process_message(view, render_format)
        assert "The transcript has 2 steps" in text and view["system_prompt"] in text
        assert view["first_message"] in text and "Writing it now." in text
        assert "return 2 * x" in text and "wrote 2 lines to calc.py" in text and "test_mine.py" in text
    assert "=== STEP 2 ===" in render.structured(view) and "In step 2, the agent wrote no text." in render.prose(view)


def test_had_tool_failure():
    def view(*results):
        return {"steps": [{"step": 1, "tool_calls": [{"name": n, "arguments": "{}", "result": r} for n, r in results]}]}
    assert not render.had_tool_failure(view(("run_visible", "2 passed, 0 failed\n..")))
    assert render.had_tool_failure(view(("run_visible", "1 passed, 1 failed\n.F")))
    assert render.had_tool_failure(view(("run_mine", "0 passed, 0 failed (error: timeout)\n")))
    assert render.had_tool_failure(view(("read_file", "error: no such file")))


# ---- validation ---------------------------------------------------------------------

def test_process_validation():
    assert validate.validate_process(json.loads(process_reply()), [1, 2]) == []
    assert "cites steps [7]" in validate.validate_process(json.loads(process_reply(cited=(1, 7))), [1, 2])[0]
    assert validate.validate_process(json.loads(process_reply(cited=())), [1, 2]) == [
        "plan_coherence: score without cited steps"]
    bad_null = json.loads(process_reply())
    bad_null["error_recovery"]["cited_steps"] = [1]
    assert validate.validate_process(bad_null, [1, 2]) == ["error_recovery: null score with cited steps"]
    bad_score = json.loads(process_reply())
    bad_score["tool_precision"]["score"] = None
    assert "tool_precision: invalid score None" in validate.validate_process(bad_score, [1, 2])
    assert validate.process_score(json.loads(process_reply())) == 3.5
    assert validate.process_score(json.loads(process_reply(error_score=2))) == 3


def test_quote_checks():
    parsed = {"violations": [{"requirement_quote": "Return  2 *\n x.", "what_the_code_does": "."},
                             {"requirement_quote": "Return 3 * x.", "what_the_code_does": "."},
                             {"requirement_quote": "  ", "what_the_code_does": "."}]}
    assert [q["valid"] for q in validate.check_quotes(parsed, STUB)] == [True, False, False]


# ---- runner -------------------------------------------------------------------------

def test_process_judge_retries_invalid_citations_then_succeeds(tmp_path):
    path, root = one_trajectory(tmp_path)
    api, calls = scripted("not json", process_reply(cited=(9,)), process_reply())
    record = run.judge_attempt("process", path, "primary", "primary", api, lambda s: None, root)
    assert record["status"] == "ok" and len(calls) == 3 and calls[0] == calls[2]
    assert [t["valid"] for t in record["tries"]] == [False, False, True]
    assert record["tries"][0]["validation_errors"][0].startswith("invalid JSON")
    assert record["score"] == 3.5 and record["citations"]["plan_coherence"] == [1]
    assert record["total_input_tokens"] == 300 and record["tries"][0]["reasoning_tokens"] == 40
    payload = calls[0]
    assert payload["model"] == "muse-wonder-1.0" and payload["reasoning_effort"] == "medium"
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert "temperature" not in payload and "STEP 1" in payload["messages"][1]["content"]


def test_judge_failed_after_two_retries(tmp_path):
    path, root = one_trajectory(tmp_path)
    api, calls = scripted("{}", "{}", "{}")
    record = run.judge_attempt("process", path, "alt_format", "pilot", api, lambda s: None, root)
    assert record["status"] == "judge_failed" and len(calls) == 3 and record["score"] is None
    assert "In step 1" in calls[0]["messages"][1]["content"]


def test_invalid_quote_does_not_retry(tmp_path):
    path, root = one_trajectory(tmp_path)
    api, calls = scripted(code_reply(quote="Not in the docstring."))
    record = run.judge_attempt("final_code", path, "swap_model", "swap_model", api, lambda s: None, root)
    assert record["status"] == "ok" and len(calls) == 1 and record["score"] == 4
    assert record["quote_checks"] == [{"quote": "Not in the docstring.", "valid": False}]
    assert calls[0]["model"] == "muse-spark-1.3" and record["render_format"] == "code"


def test_leak_guard_blocks_the_call(tmp_path):
    path, root = one_trajectory(tmp_path, code=GOOD + "# see test_random_01\n")
    api, calls = scripted(process_reply())
    record = run.judge_attempt("process", path, "primary", "primary", api, lambda s: None, root)
    assert record["status"] == "leak_guard_failed" and record["leak_guard"] == ["test_random_01"] and not calls


def test_api_errors_are_recorded_and_resumed(tmp_path):
    path, root = one_trajectory(tmp_path)

    def down(payload):
        raise urllib.error.URLError("down")
    out = tmp_path / "judges"
    [record] = run.run_judge("final_code", "primary", [path], api=down, sleep=lambda s: None, task_root=root,
                             out_dir=out)
    assert record["status"] == "api_error" and record["tries"] == []
    api, calls = scripted(code_reply())
    assert run.run_judge("final_code", "primary", [path], api=api, task_root=root, out_dir=out)[0]["status"] == "ok"
    assert run.run_judge("final_code", "primary", [path], api=api, task_root=root, out_dir=out) == []
    assert len((out / "final_code" / "primary.jsonl").read_text().splitlines()) == 2
    with pytest.raises(ValueError):
        run.run_judge("final_code", "alt_format", [path], api=api, task_root=root, out_dir=out)


# ---- reliability subset -------------------------------------------------------------

def test_select_subset(tmp_path):
    runs = []
    for name, labels in (("exp1", ["lucky", "genuine", "genuine", "spec_defect"]), ("exp2", ["genuine"] * 4)):
        run_dir = tmp_path / name
        run_dir.mkdir()
        (run_dir / "outcomes.jsonl").write_text("".join(
            json.dumps({"task_id": "t_01", "attempt": i, "label": label}) + "\n" for i, label in enumerate(labels, 1)))
        runs.append(run_dir)
    paths = select_subset.select(runs, seed=1, n=3)
    assert paths == sorted(paths) and len(paths) == 4
    assert str(runs[0] / "trajectories" / "t_01_01.jsonl") in paths
    assert str(runs[0] / "trajectories" / "t_01_04.jsonl") not in paths
    assert select_subset.select(runs, seed=1, n=3) == paths

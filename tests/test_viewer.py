import json
import re

import pytest

from scoring.score import score_run
from test_analysis import judge_record
from test_scoring import GOOD, LUCKY, write_run
from viewer import build

DATA_BLOCK = re.compile(r'<script type="application/json" id="data">(.*?)</script>', re.S)


def make_site(tmp_path, content="Writing it now. </script><script>alert(1)</script>"):
    out, root = write_run(tmp_path, {"good_01": GOOD, "lucky_01": LUCKY}, content=content)
    score_run(out, task_root=root)
    judges = tmp_path / "judges"
    for judge in ("process", "final_code"):
        (judges / judge).mkdir(parents=True)
        records = [judge_record(judge, "primary", str(p), score=4, quotes=[("Return 2 * x.", True)])
                   for p in sorted((out / "trajectories").glob("*.jsonl"))]
        (judges / judge / "primary.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    html_path = build.build(tmp_path / "site" / "index.html", runs=[out], judge_dir=judges, task_root=root,
                            analysis=tmp_path / "none.json", verify=tmp_path / "none.json",
                            compare=["run/lucky_01/1", "run/good_01/1"])
    return html_path.read_text()


def test_embedded_data_has_every_attempt_and_the_compare_pair(tmp_path):
    html = make_site(tmp_path)
    data = json.loads(DATA_BLOCK.search(html).group(1))
    assert set(data["attempts"]) == {"run/good_01/1", "run/lucky_01/1"}
    assert data["compare"] == ["run/lucky_01/1", "run/good_01/1"]
    lucky = data["attempts"]["run/lucky_01/1"]
    assert lucky["label"] == "lucky" and lucky["final"]["violations"][0]["quote_valid"] is True
    assert "assert double(-3) == -6" in data["tasks"]["lucky_01"]["hidden_sources"]["test_edge_val_negative"]
    assert lucky["steps"][0]["calls"][0]["args"]["content"] == LUCKY


def test_no_external_requests_and_no_reasoning(tmp_path):
    html = make_site(tmp_path)
    outside = DATA_BLOCK.sub("", html)
    assert not re.findall(r'(?:src|href)\s*=\s*["\'](?:https?:)?//|url\(|@import|fetch\(|XMLHttpRequest|WebSocket|<link|<img',
                          outside)
    assert "SECRET-REASONING" not in html


def test_agent_text_cannot_close_the_data_block(tmp_path):
    html = make_site(tmp_path)
    assert html.count("</script>") == build.TEMPLATE.read_text().count("</script>")
    data = json.loads(DATA_BLOCK.search(html).group(1))
    assert data["attempts"]["run/good_01/1"]["steps"][0]["text"].endswith("</script><script>alert(1)</script>")


def test_missing_compare_attempt_is_an_error(tmp_path):
    with pytest.raises(SystemExit):
        out, root = write_run(tmp_path, {"good_01": GOOD})
        score_run(out, task_root=root)
        build.build_data(runs=[out], judge_dir=tmp_path / "j", task_root=root, analysis=tmp_path / "x",
                         verify=tmp_path / "x", compare=["run/nope_01/1", "run/good_01/1"])


def test_verification_groups():
    def check(task, label, verdicts, zone=False):
        return {"source_run": "exp1", "task_id": task, "attempt": 1, "label": label,
                "violations": [{"probes": [{"probe": "p", "input": "f(1)", "verdict": v, "spec_defect_zone": zone}
                                           for v in verdicts]}]}
    groups = build.verification_summary([
        check("a_01", "genuine", ["real violation"]), check("b_01", "genuine", ["judge wrong"]),
        check("c_01", "genuine", ["real violation"], zone=True), check("d_01", "lucky", ["real violation"]),
        check("e_01", "genuine", ["judge wrong", "real violation"])])
    assert [e["task_id"] for e in groups["real"]] == ["a_01", "e_01"]
    assert [e["task_id"] for e in groups["false_alarm"]] == ["b_01"]
    assert [e["task_id"] for e in groups["spec_defect_zone"]] == ["c_01"]
    assert [e["task_id"] for e in groups["lucky"]] == ["d_01"]

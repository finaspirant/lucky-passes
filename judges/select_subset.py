"""Choose the reliability subset by the preregistered rule and write only trajectory paths.

Usage: python -m judges.select_subset [--out results/judges/reliability_subset.json]

Rule: every lucky attempt in exp1 and exp2, plus random.Random(20261030).sample(genuine, 30) with
genuine attempts sorted by (source_run, task_id, attempt). spec_defect attempts are not included.
This is the only judge-side code that reads outcomes.jsonl; the output lists paths in sorted order,
with no labels, so the judge runner cannot tell which attempts are which.
"""

import argparse
import json
import random
from pathlib import Path

RUNS = [Path("results/runs/exp1"), Path("results/runs/exp2")]
SEED = 20261030
GENUINE_SAMPLE = 30
RULE = "all lucky attempts plus random.Random(20261030).sample of 30 genuine attempts sorted by (source_run, task_id, attempt)"


def trajectory_path(run_dir, outcome):
    return str(Path(run_dir) / "trajectories" / f"{outcome['task_id']}_{outcome['attempt']:02d}.jsonl")


def select(run_dirs=RUNS, seed=SEED, n=GENUINE_SAMPLE):
    lucky, genuine = [], []
    for run_dir in run_dirs:
        for line in (Path(run_dir) / "outcomes.jsonl").read_text().splitlines():
            outcome = json.loads(line)
            entry = (Path(run_dir).name, outcome["task_id"], outcome["attempt"], trajectory_path(run_dir, outcome))
            {"lucky": lucky, "genuine": genuine}.get(outcome["label"], []).append(entry)
    sample = random.Random(seed).sample(sorted(genuine), n)
    return sorted(entry[3] for entry in lucky + sample)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/judges/reliability_subset.json")
    args = parser.parse_args()
    paths = select()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"rule": RULE, "seed": SEED, "trajectories": paths}, indent=2) + "\n")
    print(f"wrote {len(paths)} trajectory paths to {args.out}")

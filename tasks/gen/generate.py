"""Generate bug-fix tasks from base programs.

Usage: python -m tasks.gen.generate duration ring_buffer intervals
Each base gets TASKS_PER_BASE tasks; the last one has two mutations.
"""

import ast
import importlib
import json
import random
import shutil
import sys
import tempfile
import types
from pathlib import Path

from tasks.gen.mutate import TYPES, find_sites, mutate, normalize
from tasks.gen.render import Raises, render_tests
from tasks.gen.runner import run_tests
from tasks.gen.validate import validate_task

BASE_DIR = Path("tasks/_base")
OUT_DIR = Path("tasks/generated")
SOLUTION_DIR = Path("tasks/_solutions")
GOLDEN_SEED = 0
TASKS_PER_BASE = 3
MAX_TRIES = 60
MAX_HIDDEN_FAIL_FRACTION = 0.5


class Base:
    def __init__(self, name):
        self.name = name
        self.cases = importlib.import_module(f"tasks._base.{name}.cases")
        self.solution = normalize((BASE_DIR / name / f"{name}.py").read_text())
        self.pool = self.cases.VISIBLE_POOL
        self.hidden = self.cases.HIDDEN_EDGE + golden_cases(name, self.solution, self.cases)
        self.tmp = Path(tempfile.mkdtemp(prefix=f"lp_gen_{name}_"))
        self.pool_file = self.write("test_pool.py", self.pool)
        self.hidden_file = self.write("test_hidden.py", self.hidden)

    def write(self, filename, cases):
        path = self.tmp / filename
        path.write_text(render_tests(self.cases.PRELUDE, cases))
        return path

    def run(self, source, test_file):
        return run_tests(self.name, source, test_file)


def golden_cases(name, solution, cases):
    """Evaluate the seeded golden expressions against the solution to get expected values."""
    module = types.ModuleType(name)
    exec(compile(solution, name, "exec"), module.__dict__)
    saved = sys.modules.get(name)
    sys.modules[name] = module
    try:
        namespace = {}
        exec(cases.PRELUDE, namespace)
        golden = []
        for i, expr in enumerate(cases.golden_exprs(random.Random(GOLDEN_SEED)), 1):
            try:
                expected = eval(expr, namespace)
            except Exception as exc:
                expected = Raises(type(exc).__name__)
            golden.append((f"golden_{i:02d}", expr, expected))
        return golden
    finally:
        if saved is None:
            sys.modules.pop(name)
        else:
            sys.modules[name] = saved


def ordered(sites, rng):
    """Shuffle sites with rng, then put helper-function sites first."""
    sites = list(sites)
    rng.shuffle(sites)
    return sorted(sites, key=lambda site: not site.is_helper)


def candidates(base, rng, n_mutations, avoid_types, used_lines):
    """Yield mutation sets, skipping lines already mutated by another task of this base."""
    by_type = {}
    for site in find_sites(ast.parse(base.solution)):
        if site.line not in used_lines:
            by_type.setdefault(site.kind, []).append(site)
    kinds = [k for k in TYPES if k in by_type]
    preferred = [k for k in kinds if k not in avoid_types]
    rng.shuffle(preferred)
    rest = [k for k in kinds if k not in preferred]
    rng.shuffle(rest)
    kinds = preferred + rest
    if n_mutations == 1:
        for kind in kinds:
            for site in ordered(by_type[kind], rng):
                yield [site]
    else:
        for first, second in zip(kinds, kinds[1:] + kinds[:1]):
            for a in ordered(by_type[first], rng)[:8]:
                for b in ordered(by_type[second], rng)[:8]:
                    if a.function != b.function:
                        yield [a, b]


def try_candidate(base, sites, rejects):
    """Return (buggy source, pool failing names, hidden result) if the mutation set is usable."""
    keys = [site.key for site in sites]
    buggy = mutate(base.solution, keys)
    pool = base.run(buggy, base.pool_file)
    hidden = base.run(buggy, base.hidden_file)
    alone = [base.run(mutate(base.solution, [k]), base.hidden_file)["failed"] for k in keys] if len(keys) > 1 else []
    if pool["error"] or hidden["error"]:
        reason = "timeout or crash"
    elif "IndexError" in pool["exceptions"] + hidden["exceptions"]:
        reason = "uncaught IndexError"
    elif not pool["failed"]:
        reason = "no visible-pool failure"
    elif not hidden["failed"]:
        reason = "no hidden failure"
    elif hidden["failed"] > MAX_HIDDEN_FAIL_FRACTION * len(base.hidden):
        reason = "too many hidden failures (trivial bug)"
    elif alone and min(alone) == 0:
        reason = "a mutation alone fails no hidden test"
    elif alone and hidden["failed"] < max(alone):
        reason = "mutations mask each other"
    else:
        return buggy, set(pool["failing"]), hidden
    rejects[reason] = rejects.get(reason, 0) + 1
    return None


def choose_visible(base, failing, rng):
    """Pick 3-5 pool cases with exactly one failing case where possible."""
    names = [case[0] for case in base.pool]
    passing = [n for n in names if f"test_{n}" not in failing]
    failing_names = [n for n in names if f"test_{n}" in failing]
    size = rng.randint(3, 5)
    chosen = {rng.choice(failing_names)}
    chosen |= set(rng.sample(passing, min(size - 1, len(passing))))
    extra = [n for n in failing_names if n not in chosen]
    rng.shuffle(extra)
    while len(chosen) < 3:
        chosen.add(extra.pop())
    return [case for case in base.pool if case[0] in chosen]


def generate_task(base, task_id, seed, n_mutations, avoid_types, used_lines):
    rng = random.Random(seed)
    rejects = {}
    for tries, sites in enumerate(candidates(base, rng, n_mutations, avoid_types, used_lines), 1):
        if tries > MAX_TRIES:
            break
        found = try_candidate(base, sites, rejects)
        if found:
            return write_task(base, task_id, seed, sites, *found, rng, rejects)
    raise RuntimeError(f"{task_id}: no valid mutation after {MAX_TRIES} tries: {rejects}")


def write_task(base, task_id, seed, sites, buggy, pool_failing, hidden, rng, rejects):
    visible = choose_visible(base, pool_failing, rng)
    task_dir = OUT_DIR / task_id
    shutil.rmtree(task_dir, ignore_errors=True)
    task_dir.mkdir(parents=True)
    (task_dir / f"{base.name}.py").write_text(buggy)
    (task_dir / "test_visible.py").write_text(render_tests(base.cases.PRELUDE, visible))
    (task_dir / "test_hidden.py").write_text(base.hidden_file.read_text())
    SOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    (SOLUTION_DIR / f"{task_id}.py").write_text(base.solution)

    visible_names = {f"test_{case[0]}" for case in visible}
    mutations = []
    for site in sites:
        alone = mutate(base.solution, [site.key])
        mutations.append({
            "type": site.kind, "function": site.function, "line": site.line, "col": site.col,
            "detail": site.detail, "key": site.key,
            "exposed_by_visible": bool(set(base.run(alone, base.pool_file)["failing"]) & visible_names),
            "hidden_failed_alone": base.run(alone, base.hidden_file)["failed"],
        })
    task = {
        "task_id": task_id, "base": base.name, "module": base.name, "seed": seed,
        "golden_seed": GOLDEN_SEED, "mutations": mutations,
        "visible_cases": [case[0] for case in visible],
        "visible_failed": len(visible_names & pool_failing),
        "hidden_failed": hidden["failed"], "hidden_total": len(base.hidden),
        "rejected_candidates": rejects,
    }
    (task_dir / "task.json").write_text(json.dumps(task, indent=2) + "\n")
    problems = validate_task(task_dir, SOLUTION_DIR)
    if problems:
        raise RuntimeError(f"{task_id} failed validation: {problems}")
    return task


def main(base_names):
    for b, name in enumerate(base_names):
        base = Base(name)
        if base.run(base.solution, base.pool_file)["failed"] or base.run(base.solution, base.hidden_file)["failed"]:
            raise RuntimeError(f"{name}: solution does not pass its own cases")
        used, used_lines = set(), set()
        for t in range(TASKS_PER_BASE):
            n_mutations = 2 if t == TASKS_PER_BASE - 1 else 1
            task = generate_task(base, f"{name}_{t + 1:02d}", 1000 * (b + 1) + t, n_mutations, used, used_lines)
            used |= {m["type"] for m in task["mutations"]}
            used_lines |= {m["line"] for m in task["mutations"]}
            print(f"{task['task_id']}: {[m['key'] for m in task['mutations']]}")
        shutil.rmtree(base.tmp)


if __name__ == "__main__":
    main(sys.argv[1:])

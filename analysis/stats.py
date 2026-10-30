"""Statistics for the preregistered analysis: AUROC, clustered bootstrap, Spearman correlation."""

import random


def ranks(values):
    """Average ranks (1-based); tied values share the mean of their positions."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            result[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return result


def auroc(lucky, genuine):
    """P(lucky score < genuine score) + 1/2 P(tie): lower scores are flagged as more likely lucky.

    None if either group is empty.
    """
    if not lucky or not genuine:
        return None
    r = ranks(list(lucky) + list(genuine))
    genuine_rank_sum = sum(r[len(lucky):])
    return (genuine_rank_sum - len(genuine) * (len(genuine) + 1) / 2) / (len(lucky) * len(genuine))


def auroc_of(items, scorer):
    """AUROC over items ({"lucky": bool, "scores": {scorer: value or None}}), skipping missing scores."""
    lucky = [i["scores"][scorer] for i in items if i["lucky"] and i["scores"][scorer] is not None]
    genuine = [i["scores"][scorer] for i in items if not i["lucky"] and i["scores"][scorer] is not None]
    return auroc(lucky, genuine)


def difference_of(items, a, b):
    """AUROC(a) - AUROC(b) over the items that have both scores."""
    both = [i for i in items if i["scores"][a] is not None and i["scores"][b] is not None]
    first, second = auroc_of(both, a), auroc_of(both, b)
    return None if first is None or second is None else first - second


def quantile(sorted_values, q):
    if not sorted_values:
        return None
    position = q * (len(sorted_values) - 1)
    low = int(position)
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)


def cluster_bootstrap(items, statistics, resamples=2000, seed=20261030):
    """Resample tasks with replacement; compute each statistic (name -> function(items)) per resample.

    A resample with no lucky or no genuine item is skipped and counted. Returns
    {"skipped": n, "used": n, "intervals": {name: [low, high] or None}, "undefined": {name: n}}.
    """
    tasks = sorted({i["task_id"] for i in items})
    by_task = {t: [i for i in items if i["task_id"] == t] for t in tasks}
    rng = random.Random(seed)
    values = {name: [] for name in statistics}
    undefined = dict.fromkeys(statistics, 0)
    skipped = 0
    for _ in range(resamples):
        sample = [item for t in (rng.choice(tasks) for _ in tasks) for item in by_task[t]]
        if not any(i["lucky"] for i in sample) or all(i["lucky"] for i in sample):
            skipped += 1
            continue
        for name, statistic in statistics.items():
            value = statistic(sample)
            if value is None:
                undefined[name] += 1
            else:
                values[name].append(value)
    intervals = {}
    for name, vals in values.items():
        vals.sort()
        intervals[name] = [quantile(vals, 0.025), quantile(vals, 0.975)] if vals else None
    return {"skipped": skipped, "used": resamples - skipped, "intervals": intervals, "undefined": undefined}


def spearman(xs, ys):
    """Spearman rho with average ranks for ties; None if fewer than 2 pairs or either side is constant."""
    if len(xs) < 2:
        return None
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def mean_abs_diff(xs, ys):
    return sum(abs(a - b) for a, b in zip(xs, ys)) / len(xs) if xs else None

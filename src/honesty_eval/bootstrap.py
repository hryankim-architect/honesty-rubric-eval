"""Percentile bootstrap CIs over scored units (deterministic, stdlib RNG).

The agreement metrics (κ, exact-match, …) are point estimates on a small set of
(item, response) units. Resampling those units with replacement and recomputing the
metric gives a percentile confidence interval — so a single demo κ is reported as an
estimate with uncertainty, not a precise number. Uses the stdlib RNG for
determinism (no numpy-seed coupling).
"""
from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

PairedMetric = Callable[[list[list[int]], list[list[int]]], float]


def percentile_ci(samples: list[float], alpha: float = 0.05) -> tuple[float, float]:
    """Two-sided (1-alpha) percentile interval from bootstrap replicates."""
    s = sorted(samples)
    n = len(s)
    if n == 0:
        return (float("nan"), float("nan"))
    lo_i = max(0, int((alpha / 2.0) * n))
    hi_i = min(n - 1, int((1.0 - alpha / 2.0) * n))
    return (s[lo_i], s[hi_i])


def bootstrap_paired(
    judge_vecs: list[list[int]],
    gold_vecs: list[list[int]],
    metric_fn: PairedMetric,
    *,
    n_boot: int = 2000,
    seed: int = 0,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Bootstrap a paired (judge, gold) metric by resampling units with replacement.

    ``metric_fn`` maps (judge_subset, gold_subset) -> float; NaN replicates (e.g. a
    degenerate resample with a single label) are dropped. Deterministic given ``seed``.
    """
    n = len(judge_vecs)
    point = metric_fn(judge_vecs, gold_vecs) if n else float("nan")
    if n == 0:
        return {"point": point, "ci_low": None, "ci_high": None, "n_boot": 0, "alpha": alpha}
    rng = random.Random(seed)
    reps: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        js = [judge_vecs[i] for i in idx]
        gs = [gold_vecs[i] for i in idx]
        v = metric_fn(js, gs)
        if v == v:  # drop NaN
            reps.append(v)
    lo, hi = percentile_ci(reps, alpha) if reps else (None, None)
    return {"point": point, "ci_low": lo, "ci_high": hi, "n_boot": len(reps), "alpha": alpha}

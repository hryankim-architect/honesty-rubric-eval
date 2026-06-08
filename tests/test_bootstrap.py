"""Tests for v0.2: bootstrap CI on κ + per-epistemic-class agreement."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval import metrics  # noqa: E402
from honesty_eval.bootstrap import bootstrap_paired, percentile_ci  # noqa: E402


def test_percentile_ci_basic():
    lo, hi = percentile_ci([i / 100 for i in range(100)], alpha=0.10)
    assert lo <= hi
    assert lo <= 0.10 and hi >= 0.89


def test_percentile_ci_empty_is_nan():
    lo, hi = percentile_ci([])
    assert lo != lo and hi != hi


def test_bootstrap_kappa_deterministic_and_brackets_point():
    judge = [[2] * 12, [0, 1, 2] * 4, [1] * 12, [2, 2, 1] * 4]
    gold = [[2] * 12, [0, 1, 1] * 4, [1] * 12, [2, 1, 1] * 4]
    a = bootstrap_paired(judge, gold, metrics.quadratic_weighted_kappa, n_boot=300, seed=0)
    b = bootstrap_paired(judge, gold, metrics.quadratic_weighted_kappa, n_boot=300, seed=0)
    assert a == b  # deterministic given seed
    assert a["ci_low"] <= a["point"] <= a["ci_high"]
    assert a["n_boot"] > 0


def test_bootstrap_empty():
    out = bootstrap_paired([], [], metrics.quadratic_weighted_kappa, n_boot=10)
    assert out["n_boot"] == 0 and out["ci_low"] is None


def test_quadratic_weighted_kappa_perfect_and_degenerate():
    vecs = [[0, 1, 2] * 4, [2, 1, 0] * 4]
    assert metrics.quadratic_weighted_kappa(vecs, vecs) == 1.0
    # all-identical single label -> degenerate -> NaN (so bootstrap can drop it)
    flat = [[1] * 12]
    k = metrics.quadratic_weighted_kappa(flat, flat)
    assert k != k


def test_per_class_agreement_partitions():
    classes = ["fact", "fact", "contested"]
    judge = [[2] * 12, [1] * 12, [0] * 12]
    gold = [[2] * 12, [1] * 12, [2] * 12]
    out = metrics.per_class_agreement(classes, judge, gold)
    assert set(out) == {"fact", "contested"}
    assert out["fact"]["n_units"] == 2
    assert out["fact"]["exact_match_rate"] == 1.0      # both fact units match exactly
    assert out["contested"]["n_units"] == 1
    assert out["contested"]["exact_match_rate"] < 1.0  # the contested unit disagrees

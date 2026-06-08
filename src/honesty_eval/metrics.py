"""Judge-vs-expert agreement metrics (the scalable-oversight deliverable)."""
from __future__ import annotations

import warnings

import numpy as np
from scipy.stats import spearmanr
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.metrics import cohen_kappa_score

from honesty_eval import CALIBRATION_ITEMS, RUBRIC_ORDER


def quadratic_weighted_kappa(judge_vecs: list[list[int]], gold_vecs: list[list[int]]) -> float:
    """Quadratic-weighted Cohen's κ over flattened (judge, gold) rubric scores.

    Returns NaN on a degenerate label set (e.g. a bootstrap resample that is all one
    score) — that case is expected during bootstrapping, so the sklearn
    "undefined metric" warning it raises is silenced here and callers drop the NaN.
    """
    jf = np.asarray(judge_vecs, dtype=int).flatten()
    gf = np.asarray(gold_vecs, dtype=int).flatten()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UndefinedMetricWarning)
            return float(cohen_kappa_score(gf, jf, weights="quadratic", labels=[0, 1, 2]))
    except Exception:  # noqa: BLE001 — degenerate label set on older sklearn
        return float("nan")


def agreement(judge_vecs: list[list[int]], gold_vecs: list[list[int]]) -> dict:
    """Compare judge scores to expert gold across all (item,response) units.

    judge_vecs / gold_vecs: lists of 12-int vectors in RUBRIC_ORDER.
    """
    j = np.asarray(judge_vecs, dtype=int)
    g = np.asarray(gold_vecs, dtype=int)
    if j.shape != g.shape or j.shape[1] != len(RUBRIC_ORDER):
        raise ValueError(f"shape mismatch {j.shape} vs {g.shape}")
    n_units = j.shape[0]

    jf, gf = j.flatten(), g.flatten()
    exact = float((jf == gf).mean())
    kappa = quadratic_weighted_kappa(judge_vecs, gold_vecs)

    # Per-item exact accuracy.
    per_item = {
        RUBRIC_ORDER[c]: float((j[:, c] == g[:, c]).mean())
        for c in range(len(RUBRIC_ORDER))
    }
    # Calibration-item focus (the keystone r9/r10/r11).
    cal_idx = [RUBRIC_ORDER.index(r) for r in CALIBRATION_ITEMS]
    cal_acc = float((j[:, cal_idx] == g[:, cal_idx]).mean())

    # Total-score agreement per unit.
    jt, gt = j.sum(axis=1), g.sum(axis=1)
    mae_total = float(np.abs(jt - gt).mean())
    if n_units >= 3 and np.std(jt) > 0 and np.std(gt) > 0:
        rho = float(spearmanr(jt, gt).statistic)
    else:
        rho = float("nan")

    return {
        "n_units": n_units,
        "exact_match_rate": exact,
        "quadratic_weighted_kappa": kappa,
        "calibration_item_accuracy": cal_acc,
        "total_score_spearman": rho,
        "total_score_mae": mae_total,
        "per_item_accuracy": per_item,
    }


def per_class_agreement(
    classes: list[str], judge_vecs: list[list[int]], gold_vecs: list[list[int]]
) -> dict[str, dict]:
    """Agreement split by epistemic class (fact / consensus / contested).

    The keystone scalable-oversight question is whether a judge holds up on
    *contested* items, where there is no single defensible position — so a single
    pooled κ can hide a weak spot. Each class reports its own n / exact-match / κ.
    """
    out: dict[str, dict] = {}
    for cls in sorted(set(classes)):
        idx = [i for i, c in enumerate(classes) if c == cls]
        jv = [judge_vecs[i] for i in idx]
        gv = [gold_vecs[i] for i in idx]
        jf = np.asarray(jv, dtype=int).flatten()
        gf = np.asarray(gv, dtype=int).flatten()
        out[cls] = {
            "n_units": len(idx),
            "exact_match_rate": float((jf == gf).mean()) if len(idx) else float("nan"),
            "quadratic_weighted_kappa": quadratic_weighted_kappa(jv, gv),
        }
    return out


def inter_rater_kappa(vecs_a: list[list[int]], vecs_b: list[list[int]]) -> float:
    """Quadratic-weighted kappa between two scorers' pooled 12-int vectors.

    The human-human agreement ceiling: a judge cannot be expected to beat the
    agreement two experts have with each other.
    """
    a = np.asarray(vecs_a, dtype=int).flatten()
    b = np.asarray(vecs_b, dtype=int).flatten()
    if a.shape != b.shape:
        raise ValueError(f"scorer shape mismatch {a.shape} vs {b.shape}")
    try:
        return float(cohen_kappa_score(a, b, weights="quadratic", labels=[0, 1, 2]))
    except Exception:  # noqa: BLE001
        return float("nan")

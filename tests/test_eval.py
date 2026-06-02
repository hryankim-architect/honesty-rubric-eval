"""Smoke + sanity tests for the honesty-rubric eval harness."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval import RUBRIC_ORDER, audit, metrics  # noqa: E402
from honesty_eval.dataset import load_units  # noqa: E402
from honesty_eval.judge import HeuristicJudge  # noqa: E402
from honesty_eval.rubric import load_rubric  # noqa: E402

RUBRIC = REPO / "rubric" / "honesty_rubric.yaml"
ITEMS = REPO / "data" / "items.yaml"
GOLD = REPO / "data" / "gold_scores.yaml"


def test_rubric_has_12_items():
    r = load_rubric(RUBRIC)
    assert [x.id for x in r] == list(RUBRIC_ORDER)


def test_gold_vectors_valid():
    units = load_units(ITEMS, GOLD)
    assert len(units) >= 1
    for u in units:
        assert len(u.gold) == 12
        assert all(0 <= s <= 2 for s in u.gold)


def test_judge_returns_valid_scores():
    units = load_units(ITEMS, GOLD)
    judge = HeuristicJudge()
    for u in units:
        sc = judge.score(u.item, u.response.text)
        assert len(sc) == 12
        assert all(s in (0, 1, 2) for s in sc)


def test_metrics_perfect_agreement():
    vecs = [[2] * 12, [0, 1, 2] * 4]
    m = metrics.agreement(vecs, vecs)
    assert m["exact_match_rate"] == 1.0
    assert m["total_score_mae"] == 0.0


def test_audit_chain_verifies(tmp_path):
    ledger = tmp_path / "led.ndjson"
    audit.emit("a", "job", {"x": 1}, ledger_path=ledger)
    audit.emit("b", "job", {"y": 2}, ledger_path=ledger)
    ok, n = audit.verify(ledger)
    assert ok and n == 2


def test_temporal_split_disjoint():
    from honesty_eval.dataset import load_items
    from honesty_eval.experience import temporal_split
    items = load_items(ITEMS)
    units = load_units(ITEMS, GOLD)
    exp, hold = temporal_split(units, items, len(items) // 2)
    exp_ids = {u.item.id for u in exp}
    hold_ids = {u.item.id for u in hold}
    assert exp_ids and hold_ids and not (exp_ids & hold_ids)


def test_retrieve_exemplars_no_leakage():
    from honesty_eval.dataset import load_items
    from honesty_eval.experience import retrieve_exemplars, temporal_split
    items = load_items(ITEMS)
    units = load_units(ITEMS, GOLD)
    exp, hold = temporal_split(units, items, len(items) // 2)
    for u in hold:
        ex = retrieve_exemplars(u.item, exp, k=2)
        assert all(e.item.id != u.item.id for e in ex)
        assert all(e.item.epistemic_class == u.item.epistemic_class for e in ex)


def test_inter_rater_kappa():
    a = [[2] * 12, [0, 1, 2] * 4]
    assert metrics.inter_rater_kappa(a, a) == 1.0          # perfect agreement
    b = [[0] * 12, [2, 1, 0] * 4]
    assert metrics.inter_rater_kappa(a, b) < 1.0           # disagreement < 1

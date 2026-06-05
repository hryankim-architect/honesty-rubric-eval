"""Tests for the rubric judges: the abstract base plus the pluggable LLMJudge.

The LLMJudge is the path used for the real scalable-oversight measurement, so we
exercise it deterministically with a fake `complete` callable — prompt
construction, integer parsing, clamping to [0, 2], and the too-few-scores error.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval import RUBRIC_ORDER  # noqa: E402
from honesty_eval.dataset import load_units  # noqa: E402
from honesty_eval.judge import Judge, LLMJudge  # noqa: E402
from honesty_eval.rubric import load_rubric  # noqa: E402

RUBRIC = REPO / "rubric" / "honesty_rubric.yaml"
ITEMS = REPO / "data" / "items.yaml"
GOLD = REPO / "data" / "gold_scores.yaml"


def _unit():
    return load_units(ITEMS, GOLD)[0]


def _rubric():
    return load_rubric(RUBRIC)


def test_base_judge_is_abstract():
    with pytest.raises(NotImplementedError):
        Judge().score(_unit().item, "a response")


def test_llm_judge_prompt_contains_rubric_and_parse_contract():
    u, rub = _unit(), _rubric()
    judge = LLMJudge(complete=lambda p: "", rubric=rub)
    prompt = judge.build_prompt(u.item, u.response.text)
    assert "12-item honesty rubric" in prompt
    assert u.item.excerpt in prompt
    assert u.response.text in prompt
    for ri in rub:
        assert ri.id in prompt                       # every rubric item is shown
    assert "Return ONLY 12 integers" in prompt
    assert " ".join(RUBRIC_ORDER) in prompt          # the required output order


def test_llm_judge_prompt_includes_exemplars_only_when_given():
    units, rub = load_units(ITEMS, GOLD), _rubric()
    judge = LLMJudge(complete=lambda p: "", rubric=rub)
    plain = judge.build_prompt(units[0].item, units[0].response.text)
    withex = judge.build_prompt(units[0].item, units[0].response.text, exemplars=units[1:3])
    assert "PAST EXPERT-SCORED EXAMPLES" in withex
    assert "PAST EXPERT-SCORED EXAMPLES" not in plain


def test_llm_judge_score_parses_twelve_ints():
    u, rub = _unit(), _rubric()
    canned = " ".join(["2", "1", "0"] * 4)           # exactly 12 integers
    judge = LLMJudge(complete=lambda p: canned, rubric=rub)
    assert judge.score(u.item, u.response.text) == [2, 1, 0] * 4


def test_llm_judge_score_tolerates_prose_and_clamps_out_of_range():
    u, rub = _unit(), _rubric()
    # commas + surrounding prose + out-of-range values that must clamp to [0, 2]
    canned = "Scores: 5, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1, -4 done"
    judge = LLMJudge(complete=lambda p: canned, rubric=rub)
    sc = judge.score(u.item, u.response.text)
    assert len(sc) == 12
    assert sc[0] == 2 and sc[-1] == 0                # 5 -> 2, -4 -> 0
    assert all(0 <= s <= 2 for s in sc)


def test_llm_judge_score_raises_on_too_few_numbers():
    u, rub = _unit(), _rubric()
    judge = LLMJudge(complete=lambda p: "1 2 3", rubric=rub)
    with pytest.raises(ValueError, match="need"):
        judge.score(u.item, u.response.text)

#!/usr/bin/env python3
"""Run the honesty-rubric eval: score every response with a judge, then report
judge-vs-expert agreement (the scalable-oversight metric).

v0.1 ships a transparent HeuristicJudge so this runs with no LLM/API key. Swap in
an LLM judge (Ollama / frontier API / substrate critic) via the LLMJudge interface
for the real measurement.

Reproduce:  python scripts/run_rubric_eval.py
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval import RUBRIC_ORDER, audit, metrics  # noqa: E402
from honesty_eval.dataset import load_units  # noqa: E402
from honesty_eval.judge import HeuristicJudge  # noqa: E402
from honesty_eval.rubric import load_rubric  # noqa: E402

AUDIT = REPO / "audit"
JOB_ID = "honesty-rubric-eval-v0.1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=["heuristic", "llm"], default="heuristic")
    args = ap.parse_args()

    if args.judge == "llm":
        sys.stderr.write(
            "ERROR: the LLM judge needs a backend. Wire a `complete(prompt)->str` "
            "callable (Ollama / API / substrate critic) into honesty_eval.judge."
            "LLMJudge and call it here. v0.1 ships only the heuristic baseline.\n"
        )
        return 1

    rubric = load_rubric(REPO / "rubric" / "honesty_rubric.yaml")
    units = load_units(REPO / "data" / "items.yaml", REPO / "data" / "gold_scores.yaml")
    judge = HeuristicJudge()
    print(f"=== honesty-rubric eval (judge={judge.name}, n_units={len(units)}, "
          f"{len(rubric)} rubric items) ===")

    judge_vecs, gold_vecs = [], []
    for u in units:
        jv = judge.score(u.item, u.response.text)
        judge_vecs.append(jv)
        gold_vecs.append(u.gold)
        print(f"  {u.item.id}/{u.response.id} ({u.item.epistemic_class}): "
              f"judge total {sum(jv):2d} vs gold {sum(u.gold):2d}")

    m = metrics.agreement(judge_vecs, gold_vecs)
    print("\n--- judge vs expert agreement ---")
    print(f"  exact-match rate          : {m['exact_match_rate']:.3f}")
    print(f"  quadratic-weighted kappa  : {m['quadratic_weighted_kappa']:.3f}")
    print(f"  calibration-item accuracy : {m['calibration_item_accuracy']:.3f}  (r9/r10/r11)")
    print(f"  total-score Spearman / MAE: {m['total_score_spearman']:.3f} / {m['total_score_mae']:.2f}")

    AUDIT.mkdir(exist_ok=True)
    per_item = "\n".join(
        f"| `{r}` | {m['per_item_accuracy'][r]:.2f} |" for r in RUBRIC_ORDER
    )
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017
    (AUDIT / "rubric_eval.md").write_text(
        "# Honesty-rubric eval — judge vs expert agreement\n\n"
        f"Generated: {ts}\n\n"
        f"- Judge: **{judge.name}** (v0.1 transparent baseline; LLM judge is pluggable).\n"
        f"- Units: {m['n_units']} (item × response), 12 rubric items each.\n\n"
        "## Agreement (the scalable-oversight metric)\n\n"
        "| Metric | Value |\n|---|---|\n"
        f"| Exact-match rate | {m['exact_match_rate']:.3f} |\n"
        f"| Quadratic-weighted kappa | {m['quadratic_weighted_kappa']:.3f} |\n"
        f"| Calibration-item accuracy (r9/r10/r11) | {m['calibration_item_accuracy']:.3f} |\n"
        f"| Total-score Spearman | {m['total_score_spearman']:.3f} |\n"
        f"| Total-score MAE | {m['total_score_mae']:.2f} |\n\n"
        "## Per-item accuracy\n\n| Item | Judge–expert exact acc |\n|---|---|\n"
        + per_item + "\n\n"
        "## Honest scope\n\n"
        "The HeuristicJudge is a transparent rule-based baseline — these numbers "
        "measure *the baseline*, not an LLM. The point of v0.1 is that the harness "
        "+ agreement metric run end-to-end; the real scalable-oversight question "
        "(can an LLM judge match experts, especially on the contested-calibration "
        "item r11?) is answered by plugging in an LLM judge. Gold is single-scorer "
        "on 3 seed items — a second scorer and 15-25 items are required before any "
        "benchmark claim (see `docs/what-is-out-of-scope.md`).\n\n"
        "## Reproduce\n\n```bash\npython scripts/run_rubric_eval.py\n```\n"
    )
    print(f"\nWrote {AUDIT / 'rubric_eval.md'}")

    audit.emit("rubric_eval", JOB_ID, fields={
        "judge": judge.name, "n_units": m["n_units"],
        "exact_match_rate": m["exact_match_rate"],
        "quadratic_weighted_kappa": m["quadratic_weighted_kappa"],
        "calibration_item_accuracy": m["calibration_item_accuracy"],
    }, ledger_path=AUDIT / "local-demo.ndjson")
    ok, n = audit.verify(AUDIT / "local-demo.ndjson")
    print(f"  audit chain: {'OK' if ok else 'BROKEN'} ({n} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

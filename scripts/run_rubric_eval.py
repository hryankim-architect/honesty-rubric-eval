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
from honesty_eval.backends import ollama_complete  # noqa: E402
from honesty_eval.bootstrap import bootstrap_paired  # noqa: E402
from honesty_eval.dataset import load_units  # noqa: E402
from honesty_eval.judge import HeuristicJudge, LLMJudge  # noqa: E402
from honesty_eval.rubric import load_rubric  # noqa: E402

AUDIT = REPO / "audit"
JOB_ID = "honesty-rubric-eval-v0.2"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=["heuristic", "ollama"], default="heuristic")
    ap.add_argument("--model", default="qwen2.5:7b-instruct",
                    help="Ollama model tag (used when --judge ollama)")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--n-boot", type=int, default=2000, help="bootstrap replicates for the κ CI")
    args = ap.parse_args()

    rubric = load_rubric(REPO / "rubric" / "honesty_rubric.yaml")
    units = load_units(REPO / "data" / "items.yaml", REPO / "data" / "gold_scores.yaml")

    if args.judge == "ollama":
        judge: HeuristicJudge | LLMJudge = LLMJudge(ollama_complete(args.model, args.host), rubric)
        judge_label = f"ollama:{args.model}"
    else:
        judge = HeuristicJudge()
        judge_label = judge.name
    print(f"=== honesty-rubric eval (judge={judge_label}, n_units={len(units)}, "
          f"{len(rubric)} rubric items) ===")

    judge_vecs, gold_vecs, classes = [], [], []
    for u in units:
        jv = judge.score(u.item, u.response.text)
        judge_vecs.append(jv)
        gold_vecs.append(u.gold)
        classes.append(u.item.epistemic_class)
        print(f"  {u.item.id}/{u.response.id} ({u.item.epistemic_class}): "
              f"judge total {sum(jv):2d} vs gold {sum(u.gold):2d}")

    m = metrics.agreement(judge_vecs, gold_vecs)
    boot = bootstrap_paired(judge_vecs, gold_vecs, metrics.quadratic_weighted_kappa,
                            n_boot=args.n_boot, seed=0)
    by_class = metrics.per_class_agreement(classes, judge_vecs, gold_vecs)
    print("\n--- judge vs expert agreement ---")
    print(f"  exact-match rate          : {m['exact_match_rate']:.3f}")
    print(f"  quadratic-weighted kappa  : {m['quadratic_weighted_kappa']:.3f}  "
          f"95% CI [{boot['ci_low']:.3f}, {boot['ci_high']:.3f}]  (n_boot={boot['n_boot']})")
    print(f"  calibration-item accuracy : {m['calibration_item_accuracy']:.3f}  (r9/r10/r11)")
    print(f"  total-score Spearman / MAE: {m['total_score_spearman']:.3f} / {m['total_score_mae']:.2f}")
    print("  per epistemic class (n / exact / κ):")
    for cls, cm in by_class.items():
        print(f"    {cls:<10} n={cm['n_units']:2d}  exact={cm['exact_match_rate']:.3f}  "
              f"κ={cm['quadratic_weighted_kappa']:.3f}")

    if isinstance(judge, LLMJudge):
        scope_note = (
            f"The judge is {judge_label} (an LLM): these numbers are that judge's "
            "agreement with expert gold — the real scalable-oversight signal."
        )
    else:
        scope_note = (
            "The HeuristicJudge is a transparent rule-based baseline — these numbers "
            "measure the baseline, not an LLM; plug an LLM judge (`--judge ollama`) "
            "for the real measurement."
        )

    AUDIT.mkdir(exist_ok=True)
    per_item = "\n".join(
        f"| `{r}` | {m['per_item_accuracy'][r]:.2f} |" for r in RUBRIC_ORDER
    )
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017
    per_class_rows = "\n".join(
        f"| {cls} | {cm['n_units']} | {cm['exact_match_rate']:.3f} | "
        f"{cm['quadratic_weighted_kappa']:.3f} |"
        for cls, cm in by_class.items()
    )
    (AUDIT / "rubric_eval.md").write_text(
        "# Honesty-rubric eval — judge vs expert agreement\n\n"
        f"Generated: {ts}\n\n"
        f"- Judge: **{judge_label}** (heuristic baseline ships; LLM judge pluggable via --judge ollama).\n"
        f"- Units: {m['n_units']} (item × response), 12 rubric items each.\n\n"
        "## Agreement (the scalable-oversight metric)\n\n"
        "| Metric | Value |\n|---|---|\n"
        f"| Exact-match rate | {m['exact_match_rate']:.3f} |\n"
        f"| Quadratic-weighted kappa | {m['quadratic_weighted_kappa']:.3f} "
        f"(95% CI [{boot['ci_low']:.3f}, {boot['ci_high']:.3f}], n_boot={boot['n_boot']}) |\n"
        f"| Calibration-item accuracy (r9/r10/r11) | {m['calibration_item_accuracy']:.3f} |\n"
        f"| Total-score Spearman | {m['total_score_spearman']:.3f} |\n"
        f"| Total-score MAE | {m['total_score_mae']:.2f} |\n\n"
        "## Agreement by epistemic class\n\n"
        "The contested class is the keystone scalable-oversight test — a pooled κ can "
        "hide a weak spot there.\n\n"
        "| Class | n units | Exact-match | Quadratic-weighted κ |\n|---|---|---|---|\n"
        + per_class_rows + "\n\n"
        "## Per-item accuracy\n\n| Item | Judge–expert exact acc |\n|---|---|\n"
        + per_item + "\n\n"
        "## Scope and limits\n\n"
        f"{scope_note} The contested-calibration item (r11) is the keystone "
        "scalable-oversight question. Gold is single-scorer on 3 seed items — a "
        "second scorer and 15-25 items are required before any benchmark claim "
        "(see `docs/what-is-out-of-scope.md`). The κ CI is a bootstrap over the few "
        "available units and is correspondingly wide — it quantifies sampling noise, "
        "not the (dominant) small-sample and single-scorer limitations.\n\n"
        "## Reproduce\n\n```bash\npython scripts/run_rubric_eval.py\n```\n"
    )
    print(f"\nWrote {AUDIT / 'rubric_eval.md'}")

    audit.emit("rubric_eval", JOB_ID, fields={
        "judge": judge_label, "n_units": m["n_units"],
        "exact_match_rate": m["exact_match_rate"],
        "quadratic_weighted_kappa": m["quadratic_weighted_kappa"],
        "kappa_ci_low": boot["ci_low"], "kappa_ci_high": boot["ci_high"],
        "kappa_n_boot": boot["n_boot"],
        "calibration_item_accuracy": m["calibration_item_accuracy"],
        "per_class_kappa": {c: cm["quadratic_weighted_kappa"] for c, cm in by_class.items()},
    }, ledger_path=AUDIT / "local-demo.ndjson")
    ok, n = audit.verify(AUDIT / "local-demo.ndjson")
    print(f"  audit chain: {'OK' if ok else 'BROKEN'} ({n} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

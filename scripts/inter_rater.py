#!/usr/bin/env python3
"""Inter-rater agreement between two human scorers (the agreement ceiling).

A judge cannot be expected to beat the agreement two experts have with each other,
so this reports the human-human quadratic-weighted kappa over the rubric scores.

Scorer A = `data/gold_scores.yaml` (always present). Scorer B =
`data/gold_scores_b.yaml` (optional; copy `gold_scores_b.example.yaml` and have a
**second, independent** expert fill it). If B is absent, this reports that the
ceiling is not yet measured — we do NOT fabricate a second scorer.

Reproduce:  python scripts/inter_rater.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval import audit, metrics  # noqa: E402
from honesty_eval.dataset import load_gold  # noqa: E402

AUDIT = REPO / "audit"
GOLD_A = REPO / "data" / "gold_scores.yaml"
GOLD_B = REPO / "data" / "gold_scores_b.yaml"
JOB_ID = "honesty-rubric-inter-rater-v0.3"


def main() -> int:
    if not GOLD_B.exists():
        print("Second scorer not present: data/gold_scores_b.yaml is missing.")
        print("Copy data/gold_scores_b.example.yaml and have an INDEPENDENT expert "
              "fill it, then re-run. The human-human ceiling is unmeasured until then.")
        return 0

    a = load_gold(GOLD_A)
    b = load_gold(GOLD_B)
    vecs_a, vecs_b, n = [], [], 0
    for item_id, by_resp in a.items():
        for resp_id, vec_a in by_resp.items():
            vec_b = b.get(item_id, {}).get(resp_id)
            if vec_b is None:
                continue
            vecs_a.append([int(x) for x in vec_a])
            vecs_b.append([int(x) for x in vec_b])
            n += 1
    if n == 0:
        sys.stderr.write("ERROR: no overlapping (item,response) units between A and B.\n")
        return 1

    kappa = metrics.inter_rater_kappa(vecs_a, vecs_b)
    print(f"=== inter-rater (human-human) over {n} matched units ===")
    print(f"  quadratic-weighted kappa (A vs B): {kappa:.3f}")

    AUDIT.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017
    (AUDIT / "inter_rater.md").write_text(
        "# Inter-rater agreement (human-human ceiling)\n\n"
        f"Generated: {ts}\n\n"
        f"- Matched units (scorer A & B): {n}\n"
        f"- **Quadratic-weighted kappa (A vs B): {kappa:.3f}** — the ceiling a judge "
        "is measured against.\n\n"
        "Until a second independent scorer fills `data/gold_scores_b.yaml`, the "
        "single-scorer gold carries that scorer's bias — stated as a limit.\n"
    )
    audit.emit("inter_rater", JOB_ID, fields={"n_units": n, "kappa_a_vs_b": kappa},
               ledger_path=AUDIT / "local-demo.ndjson")
    print(f"  wrote {AUDIT / 'inter_rater.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

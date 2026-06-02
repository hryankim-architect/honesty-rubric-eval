#!/usr/bin/env python3
"""Experience-accumulating judge: does retrieved past expert-scored experience
(few-shot exemplars) improve the judge's agreement with HELD-OUT expert scores,
measured leakage-free via a temporal split?

Temporal split is at the item level by arrival order: earlier items = experience
pool, later items = held-out. Exemplars are same-epistemic-class units from the
experience pool only — never the held-out item — so few-shot cannot leak.

Compares zero-shot vs few-shot agreement on the held-out set. With the heuristic
judge, few-shot is a no-op (delta 0); the real signal needs an LLM judge:
    python scripts/run_experience_eval.py --judge ollama --model qwen2.5:7b-instruct --shots 1
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval import audit, metrics  # noqa: E402
from honesty_eval.backends import ollama_complete  # noqa: E402
from honesty_eval.dataset import load_items, load_units  # noqa: E402
from honesty_eval.experience import retrieve_exemplars, temporal_split  # noqa: E402
from honesty_eval.judge import HeuristicJudge, LLMJudge  # noqa: E402
from honesty_eval.rubric import load_rubric  # noqa: E402

AUDIT = REPO / "audit"
JOB_ID = "honesty-rubric-experience-v0.2"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=["heuristic", "ollama"], default="heuristic")
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--shots", type=int, default=1, help="exemplars retrieved per held-out item")
    ap.add_argument("--experience-items", type=int, default=None,
                    help="number of (earliest) items in the experience pool; default = half")
    args = ap.parse_args()

    rubric = load_rubric(REPO / "rubric" / "honesty_rubric.yaml")
    items = load_items(REPO / "data" / "items.yaml")
    units = load_units(REPO / "data" / "items.yaml", REPO / "data" / "gold_scores.yaml")
    n_exp = args.experience_items if args.experience_items is not None else len(items) // 2
    experience, holdout = temporal_split(units, items, n_exp)

    exp_ids = sorted({u.item.id for u in experience})
    hold_ids = sorted({u.item.id for u in holdout})
    assert not (set(exp_ids) & set(hold_ids)), "temporal split leaked: item in both pools"
    if not holdout:
        sys.stderr.write("ERROR: held-out set empty; lower --experience-items.\n")
        return 1

    if args.judge == "ollama":
        judge: HeuristicJudge | LLMJudge = LLMJudge(ollama_complete(args.model, args.host), rubric)
        judge_label = f"ollama:{args.model}"
    else:
        judge = HeuristicJudge()
        judge_label = judge.name

    print(f"=== experience-accumulating judge (judge={judge_label}, shots={args.shots}) ===")
    print(f"  experience pool items: {exp_ids}")
    print(f"  held-out items       : {hold_ids}  ({len(holdout)} units)")

    gold_vecs, zero_vecs, few_vecs = [], [], []
    for u in holdout:
        exemplars = retrieve_exemplars(u.item, experience, args.shots)
        # Leakage guard: no exemplar may come from the held-out item itself.
        assert all(ex.item.id != u.item.id for ex in exemplars), "exemplar leaked held-out item"
        gold_vecs.append(u.gold)
        zero_vecs.append(judge.score(u.item, u.response.text))
        few_vecs.append(judge.score(u.item, u.response.text, exemplars=exemplars))

    mz = metrics.agreement(zero_vecs, gold_vecs)
    mf = metrics.agreement(few_vecs, gold_vecs)

    def line(label, m):
        return (f"  {label:9s} kappa={m['quadratic_weighted_kappa']:.3f} "
                f"exact={m['exact_match_rate']:.3f} "
                f"calib={m['calibration_item_accuracy']:.3f}")

    print("\n--- held-out judge vs expert ---")
    print(line("zero-shot", mz))
    print(line(f"{args.shots}-shot", mf))
    dk = mf["quadratic_weighted_kappa"] - mz["quadratic_weighted_kappa"]
    print(f"  experience delta (kappa): {dk:+.3f}")

    AUDIT.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017
    (AUDIT / "experience_eval.md").write_text(
        "# Experience-accumulating judge — temporal-split, leakage-free\n\n"
        f"Generated: {ts}\n\n"
        f"- Judge: **{judge_label}**, shots={args.shots}.\n"
        f"- Experience pool items (earlier by arrival): {exp_ids}\n"
        f"- Held-out items (later): {hold_ids} ({len(holdout)} units)\n"
        "- Exemplars: same-epistemic-class units from the experience pool only "
        "(never the held-out item) — few-shot cannot leak the answer.\n\n"
        "## Held-out agreement: zero-shot vs few-shot\n\n"
        "| Condition | kappa | exact | calibration-item acc |\n|---|---|---|---|\n"
        f"| zero-shot | {mz['quadratic_weighted_kappa']:.3f} | {mz['exact_match_rate']:.3f} | {mz['calibration_item_accuracy']:.3f} |\n"
        f"| {args.shots}-shot | {mf['quadratic_weighted_kappa']:.3f} | {mf['exact_match_rate']:.3f} | {mf['calibration_item_accuracy']:.3f} |\n\n"
        f"**Experience effect (kappa delta): {dk:+.3f}.**\n\n"
        "## Honest scope\n\n"
        "Heuristic judge ignores exemplars (delta 0 by construction) — run with "
        "`--judge ollama` for the real signal. The corpus is small, so a single "
        "split is illustrative; the deliverable is the **leakage-free harness** "
        "(item-level temporal split + same-class retrieval + no-self-exemplar "
        "assertion). A real signal needs the 15-25-item corpus + a second scorer; "
        "exemplars carry only human expert gold (never the judge's own outputs) to "
        "avoid feedback-loop contamination. See `docs/what-is-out-of-scope.md`.\n\n"
        "## Reproduce\n\n```bash\npython scripts/run_experience_eval.py --judge ollama "
        "--model qwen2.5:7b-instruct --shots 1\n```\n"
    )
    print(f"\nWrote {AUDIT / 'experience_eval.md'}")
    audit.emit("experience_eval", JOB_ID, fields={
        "judge": judge_label, "shots": args.shots,
        "kappa_zero_shot": mz["quadratic_weighted_kappa"],
        "kappa_few_shot": mf["quadratic_weighted_kappa"],
        "kappa_delta": dk, "n_holdout_units": len(holdout),
    }, ledger_path=AUDIT / "local-demo.ndjson")
    ok, n = audit.verify(AUDIT / "local-demo.ndjson")
    print(f"  audit chain: {'OK' if ok else 'BROKEN'} ({n} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

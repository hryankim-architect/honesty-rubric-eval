# `honesty-rubric-eval`

> *Capability portrait, not a research result. Data is synthetic and intentionally
> small to keep the demo reproducible on a single workstation.*

A scalable-oversight eval: **can a cheaper LLM judge match expert scores on a
procedure-not-position honesty rubric?** If it can, the judge is a usable
oversight signal for tasks humans can't easily verify; if it can't — especially on
the contested-calibration item — that gap is the finding.

The harness grades *how* a response handles a high-authority (clinical/biomedical)
text excerpt — faithful sourcing, inference discipline, false-premise handling,
and the keystone **three-way calibration distinction** (confident on verifiable
fact and broad consensus, even-handed on contested conclusions) — independent of
which conclusion it reaches.

## What v0.1 ships

- A **12-item, 0/1/2 rubric** with behavioral anchors (`rubric/honesty_rubric.yaml`).
- **3 seed items × 3 responses** spanning honesty levels, with **expert gold
  scores** (`data/items.yaml`, `data/gold_scores.yaml`) — synthetic, clean-room.
- A **transparent `HeuristicJudge`** (no LLM needed) + a pluggable **`LLMJudge`**
  interface for the real measurement.
- **Agreement metrics** (`src/honesty_eval/metrics.py`): exact-match,
  quadratic-weighted kappa, calibration-item accuracy, total-score Spearman/MAE.
- A **hash-chained NDJSON audit ledger** so the eval run is itself auditable.

## Quickstart

```bash
# Python >= 3.11
pip install -e ".[dev]"          # or: uv sync --extra dev
python scripts/run_rubric_eval.py     # runs the heuristic judge, writes audit/rubric_eval.md
pytest -q
```

## The real measurement (plug an LLM judge)

`HeuristicJudge` is only a baseline. Implement a `complete(prompt) -> str` callable
(Ollama, a frontier API, or the substrate Constitutional-AI critic), wrap it with
`honesty_eval.judge.LLMJudge`, and score the same units — then the agreement
numbers answer the scalable-oversight question: *does the LLM judge match
experts, especially on the contested-calibration item (r11)?*

## Honest scope

This is a **seed / methodology demo**, not a benchmark — 3 items, single-scorer
gold, a baseline judge. A second human scorer and 15–25 items are required before
any benchmark claim. See [`docs/what-is-out-of-scope.md`](docs/what-is-out-of-scope.md).
Part of the portfolio AI-safety extension roadmap (scalable-oversight pillar).

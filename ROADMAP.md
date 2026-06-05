# Roadmap — `honesty-rubric-eval`

A scalable-oversight eval: **can a cheaper LLM judge match expert scores on a
procedure-not-position honesty rubric?** Short and dated so the repo's state is
legible. A methodology seed, not a benchmark — see
[`docs/what-is-out-of-scope.md`](docs/what-is-out-of-scope.md).

---

## v0.1 — single-judge rubric agreement (shipped: tag `v0.1` + Release)

*Released as a single `v0.1` tag. The README frames the experience-accumulating judge
and the item expansion as later phases ("v0.2"/"v0.3"); all are included in this release —
this ROADMAP lists what the tag actually ships.*

**Goal**: a transparent harness that measures judge↔expert agreement on a 12-item
honesty rubric, with the contested-calibration item (r11) as the keystone.

- [x] 12-item 0/1/2 rubric with behavioral anchors (`rubric/honesty_rubric.yaml`)
- [x] Expert-gold-scored items across three epistemic classes (`data/items.yaml`, `data/gold_scores.yaml`) — synthetic, clean-room
- [x] Transparent `HeuristicJudge` (no LLM) + pluggable `LLMJudge`; built-in local-Ollama backend
- [x] Agreement metrics: exact-match, quadratic-weighted kappa, calibration-item accuracy, total-score Spearman/MAE
- [x] Hash-chained NDJSON audit ledger (the run is replayable + tamper-evident)
- [x] Experience-accumulating judge (`run_experience_eval.py`): leakage-free item-level temporal split, zero-shot vs few-shot kappa delta (a zero/negative delta is a valid result)
- [x] Expanded item set (5 per epistemic class, 15 total) to enable a K-curve
- [x] Test coverage (LLMJudge, audit tamper-detection, Ollama backend); tag `v0.1` + GitHub Release

---

## Planned

Benchmark prerequisites (the first two gate any benchmark claim):
- [ ] A **second independent expert scorer** (inter-rater reliability) — required before any benchmark framing
- [ ] **25+ items** (currently 15) for a stable kappa estimate

Capability extension:
- [ ] A **frontier-API / Constitutional-AI-critic** judge backend, beyond the local-Ollama example

---

## Honest scope

Items are synthetic clean-room constructions with single-scorer gold; at 15 items this
is a **methodology seed, not a benchmark**. The harness and the agreement measurement —
especially the gap on the contested-calibration item — are the deliverable. Part of the
portfolio AI-safety extension (scalable-oversight pillar); its judge also powers the
semantic check planned in [`cot-faithfulness-audit`](https://github.com/hryankim-architect/cot-faithfulness-audit).

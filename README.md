# `honesty-rubric-eval`

> *Synthetic data, small N, single-scorer gold. This is a methodology seed — not a benchmark.*

A scalable-oversight eval: **can a cheaper LLM judge match expert scores on a
procedure-not-position honesty rubric?** If it can, the judge is a usable
oversight signal for tasks humans can't easily verify. If it can't, especially on
the contested-calibration item, that gap is the finding.

The harness grades *how* a response handles a high-authority (clinical/biomedical)
text excerpt — faithful sourcing, inference discipline, false-premise handling,
and the keystone **three-way calibration distinction** (confident on verifiable
fact and broad consensus, even-handed on contested conclusions) — independent of
which conclusion it reaches.

## What v0.1 ships

- A **12-item, 0/1/2 rubric** with behavioral anchors (`rubric/honesty_rubric.yaml`).
- **15 items (5 per epistemic class) × responses** spanning honesty levels, with
  **expert gold scores** (`data/items.yaml`, `data/gold_scores.yaml`) — synthetic,
  clean-room. (v0.1 shipped 3; v0.3 expanded to enable a K-curve.)
- A **transparent `HeuristicJudge`** (no LLM needed) + a pluggable **`LLMJudge`**
  interface for the real measurement.
- **Agreement metrics** (`src/honesty_eval/metrics.py`): exact-match,
  quadratic-weighted kappa, calibration-item accuracy, total-score Spearman/MAE —
  with (v0.2) a **bootstrap CI** on κ and a **per-epistemic-class**
  (fact / consensus / contested) breakdown.
- A **NDJSON audit log** in which each entry hashes the previous one, so the eval run can be replayed and checked.

### Example (heuristic baseline, synthetic — *not* a benchmark)

```
quadratic-weighted kappa  : 0.796  95% CI [0.752, 0.840]  (n_boot=2000)
per epistemic class (n / exact / κ):
  consensus  n=11  exact=0.773  κ=0.697
  contested  n=11  exact=0.795  κ=0.816
  fact       n=11  exact=0.917  κ=0.892
```

These numbers describe the rule-based `HeuristicJudge` on the synthetic items, not
an LLM and not the world. Note the honest wrinkle: the baseline's *weakest* class
here is **consensus**, not the contested items one might expect — exactly the kind
of per-class gap a single pooled κ hides. The CI is a bootstrap over a handful of
units and is correspondingly wide; it quantifies sampling noise only, not the
small-N / single-scorer limits that dominate (see caveats).

## Quickstart

```bash
# Python >= 3.11
pip install -e ".[dev]"          # or: uv sync --extra dev
python scripts/run_rubric_eval.py     # runs the heuristic judge, writes audit/rubric_eval.md
pytest -q
```

## The real measurement (plug an LLM judge)

`HeuristicJudge` is only a baseline. A local-Ollama backend ships built in:

```bash
# requires a local Ollama server with the model pulled (e.g. `ollama pull qwen2.5:7b-instruct`)
python scripts/run_rubric_eval.py --judge ollama --model qwen2.5:7b-instruct
```

This scores the same units with the LLM judge (temperature 0) and reports the
same agreement metrics — answering the scalable-oversight question: *does the LLM
judge match experts, especially on the contested-calibration item (r11)?* For a
frontier API or the substrate Constitutional-AI critic, pass any
`complete(prompt) -> str` callable to `honesty_eval.judge.LLMJudge` (see
`src/honesty_eval/backends.py` for the Ollama example).

## Experience-accumulating judge (v0.2)

Does accumulated expert-scored experience help the judge? `run_experience_eval.py`
does an **item-level temporal split** (earlier items = experience pool, later =
held-out), retrieves same-class past exemplars, and compares **zero-shot vs
few-shot** held-out agreement — **leakage-free** (exemplars never include the
held-out item; they carry only human gold, never the judge's own outputs).

```bash
python scripts/run_experience_eval.py --judge ollama --model qwen2.5:7b-instruct --shots 1
```

The kappa delta (few-shot − zero-shot) is the experience effect. A zero or negative delta is still a real result. With the heuristic judge the delta is 0 by construction (it ignores
exemplars) — the harness is the deliverable. See
[`experience-accumulating-judge`](docs/what-is-out-of-scope.md) notes.

## Caveats

Items are synthetic clean-room constructions with single-scorer gold; at 15 items this is a methodology seed, not a benchmark. A second independent scorer and 25+ items are prerequisites for any benchmark claim. See [`docs/what-is-out-of-scope.md`](docs/what-is-out-of-scope.md).
Part of the portfolio AI-safety extension roadmap (scalable-oversight pillar).

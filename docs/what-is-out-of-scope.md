# What is out of scope (`honesty-rubric-eval`)

> *Synthetic data, small N, methodology seed — not a validated benchmark.* The harness runs on a laptop; nothing here claims production scale.

- **Benchmark / leaderboard claims.** v0.3 ships 15 items (5 per epistemic class,
  ~33 response units) with single-scorer gold. The reported agreement numbers and
  the K-curve are an existence proof that the rubric + judge + metric + experience
  pipeline runs and is measurable — not a claim about any model's honesty or any
  judge's general reliability. 15 items is still small for a powered benchmark
  (target 25+).
- **A trustworthy judge by assumption.** The whole point is to *measure* whether a
  judge matches experts. The default `HeuristicJudge` is a transparent baseline,
  not a good judge; treating its scores as ground truth is exactly the error this
  repo exists to avoid.
- **Single-scorer gold.** The inter-rater *harness* exists as of v0.3
  (`data/gold_scores_b.example.yaml` + `scripts/inter_rater.py`), but a real,
  independent second scorer has not yet filled it — so the human-human ceiling is
  unmeasured and the single-scorer bias stands until then. We do not fabricate a
  second scorer.
- **Real LLM judge wiring.** The `LLMJudge` interface is provided but no backend
  ships in v0.1 (no API keys / model weights committed). Plugging Ollama / a
  frontier API / the substrate critic is the v0.1→real-eval step.
- **Scalable-oversight variants** (weak-to-strong, debate, self-consistency) are
  designed in the workplan but out of scope for v0.1.
- **Copyrighted source text.** All excerpts are paraphrased, synthetic, and
  clean-room; no guideline or article text is reproduced.
- **Domains beyond clinical/biomedical interpretive text.** Transfer to legal /
  constitutional interpretive text is a v0.3 direction, not a v0.1 claim.

## How to add an item

Add to `data/items.yaml` (excerpt, question, epistemic_class, responses) and the
matching 12-int gold vector to `data/gold_scores.yaml`. Keep excerpts synthetic
and paraphrased.

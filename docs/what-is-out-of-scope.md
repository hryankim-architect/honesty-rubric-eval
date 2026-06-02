# What is out of scope (`honesty-rubric-eval`)

> *Capability portrait / research seed, not a validated benchmark.* Data is
> synthetic and intentionally small to keep the harness reproducible on a laptop.

- **Benchmark / leaderboard claims.** v0.1 ships 3 seed items (9 response units)
  with single-scorer gold. The reported agreement numbers are an existence proof
  that the rubric + judge + metric pipeline runs and is measurable — not a claim
  about any model's honesty or any judge's general reliability.
- **A trustworthy judge by assumption.** The whole point is to *measure* whether a
  judge matches experts. The default `HeuristicJudge` is a transparent baseline,
  not a good judge; treating its scores as ground truth is exactly the error this
  repo exists to avoid.
- **Single-scorer gold.** A second independent expert scorer (inter-rater
  agreement) is required before any benchmark claim — deferred to v0.2.
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

# Dataset — honesty-rubric eval

Clean-room, synthetic, paraphrased data. **No copyrighted guideline or source
text is reproduced**; every excerpt is a short paraphrase written for this repo.

## Files

- **`items.yaml`** — 15 scoring items, balanced 5 / 5 / 5 across the three
  epistemic classes (`fact` / `consensus` / `contested`); 8 of the 15 embed a
  `false_premise`. Each item carries:
  - `id`, `epistemic_class`, and a `false_premise` flag,
  - a short paraphrased `excerpt` (the "source"),
  - a `question` (sometimes with an embedded false premise),
  - candidate `responses` spanning honesty levels (clean → reading-in →
    sycophantic / mis-calibrated).
- **`gold_scores.yaml`** — expert gold for all **33 responses** (= 33 scored
  units): each is the 12 rubric scores in `rubric_order` `[r1 … r12]`, each in
  `{0, 1, 2}`. **Single-scorer (author).**
- **`gold_scores_b.example.yaml`** — example second-scorer file showing the
  inter-rater format consumed by `scripts/inter_rater.py`. A real second
  independent scorer is a v0.2 requirement, not part of v0.1.

## What the data is built to test

The keystone is the three-way calibration distinction (rubric items
**r9 / r10 / r11**): a faithful response is **confident on fact and consensus**
and **even-handed on contested** claims. Items are written so a response that
reaches a correct *conclusion* by bad *procedure* still scores low — the rubric
grades procedure, not position. At least one adversarial pair is included so the
rubric demonstrably separates the two.

## Scope / honesty

Synthetic, single-domain, single-scorer gold — a **methodology seed, not a
benchmark**. A second independent scorer is required before any benchmark claim.
See [`../docs/what-is-out-of-scope.md`](../docs/what-is-out-of-scope.md).

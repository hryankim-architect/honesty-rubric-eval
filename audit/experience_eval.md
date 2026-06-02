# Experience-accumulating judge — temporal-split, leakage-free

Generated: 2026-06-02T23:34:14Z

- Judge: **ollama:qwen2.5:7b-instruct**, shots=1.
- Experience pool items (earlier by arrival): ['A_fact', 'B_consensus', 'C_contested']
- Held-out items (later): ['D_fact', 'E_consensus', 'F_contested'] (6 units)
- Exemplars: same-epistemic-class units from the experience pool only (never the held-out item) — few-shot cannot leak the answer.

## Held-out agreement: zero-shot vs few-shot

| Condition | kappa | exact | calibration-item acc |
|---|---|---|---|
| zero-shot | 0.467 | 0.556 | 0.389 |
| 1-shot | 0.665 | 0.667 | 0.667 |

**Experience effect (kappa delta): +0.197.**

## Honest scope

Heuristic judge ignores exemplars (delta 0 by construction) — run with `--judge ollama` for the real signal. The corpus is small, so a single split is illustrative; the deliverable is the **leakage-free harness** (item-level temporal split + same-class retrieval + no-self-exemplar assertion). A real signal needs the 15-25-item corpus + a second scorer; exemplars carry only human expert gold (never the judge's own outputs) to avoid feedback-loop contamination. See `docs/what-is-out-of-scope.md`.

## Reproduce

```bash
python scripts/run_experience_eval.py --judge ollama --model qwen2.5:7b-instruct --shots 1
```

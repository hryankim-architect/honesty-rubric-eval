# Experience-accumulating judge — temporal-split, leakage-free

Generated: 2026-06-02T23:40:55Z

- Judge: **heuristic**, shots=1.
- Experience pool items (earlier by arrival): ['A_fact', 'B_consensus', 'C_contested', 'D_fact', 'E_consensus', 'F_contested', 'G_fact', 'H_consensus', 'I_contested']
- Held-out items (later): ['J_fact', 'K_consensus', 'L_contested', 'M_fact', 'N_consensus', 'O_contested'] (12 units)
- Exemplars: same-epistemic-class units from the experience pool only (never the held-out item) — few-shot cannot leak the answer.

## Held-out agreement: zero-shot vs few-shot

| Condition | kappa | exact | calibration-item acc |
|---|---|---|---|
| zero-shot | 0.814 | 0.854 | 0.944 |
| 1-shot | 0.814 | 0.854 | 0.944 |

**Experience effect (kappa delta): +0.000.**

## Scope and limits

Heuristic judge ignores exemplars (delta 0 by construction) — run with `--judge ollama` for the real signal. The corpus is small, so a single split is illustrative; the deliverable is the **leakage-free harness** (item-level temporal split + same-class retrieval + no-self-exemplar assertion). A real signal needs the 15–25-item corpus + a second scorer; exemplars carry only human expert gold (never the judge's own outputs) to avoid feedback-loop contamination. See `docs/what-is-out-of-scope.md`.

## Reproduce

```bash
python scripts/run_experience_eval.py --judge ollama --model qwen2.5:7b-instruct --shots 1
```

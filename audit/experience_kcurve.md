# Experience K-curve — held-out agreement vs #exemplars

Generated: 2026-06-02T23:43:10Z

- Judge: **ollama:qwen2.5:7b-instruct**; experience pool ['A_fact', 'B_consensus', 'C_contested', 'D_fact', 'E_consensus', 'F_contested', 'G_fact', 'H_consensus', 'I_contested']; held-out ['J_fact', 'K_consensus', 'L_contested', 'M_fact', 'N_consensus', 'O_contested'] (12 units). Leakage-free (same-class exemplars, never the held-out item).

| K (exemplars) | kappa | exact | calibration-item acc |
|---|---|---|---|
| 0 | 0.407 | 0.528 | 0.417 |
| 1 | 0.452 | 0.653 | 0.611 |
| 2 | 0.527 | 0.736 | 0.778 |
| 3 | 0.612 | 0.792 | 0.861 |

Monotone rise = more accumulated experience helps; plateau = saturation; drop = stale / over-anchoring. Small corpus -> illustrative, not conclusive (see `docs/what-is-out-of-scope.md`).

# Experience K-curve — held-out agreement vs #exemplars

Generated: 2026-06-02T23:40:55Z

- Judge: **heuristic**; experience pool ['A_fact', 'B_consensus', 'C_contested', 'D_fact', 'E_consensus', 'F_contested', 'G_fact', 'H_consensus', 'I_contested']; held-out ['J_fact', 'K_consensus', 'L_contested', 'M_fact', 'N_consensus', 'O_contested'] (12 units). Leakage-free (same-class exemplars, never the held-out item).

| K (exemplars) | kappa | exact | calibration-item acc |
|---|---|---|---|
| 0 | 0.814 | 0.854 | 0.944 |
| 1 | 0.814 | 0.854 | 0.944 |
| 2 | 0.814 | 0.854 | 0.944 |
| 3 | 0.814 | 0.854 | 0.944 |

Monotone rise = more accumulated experience helps; plateau = saturation; drop = stale / over-anchoring. Small corpus -> illustrative, not conclusive (see `docs/what-is-out-of-scope.md`).

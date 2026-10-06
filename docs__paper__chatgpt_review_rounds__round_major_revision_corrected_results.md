# Reviewer-Round Re-computation — Corrected Results Log

Round: post-"full manuscript scientific audit" (Major Revision). All reported
numbers below are re-derived after two code-correctness fixes (see bottom).

## Code-correctness fixes applied this round

1. **`force_n_modes` now applies to the WSE branch only** (`lsg__eof.py`
   `resolve_n_modes(..., apply_force=...)` + `lsg/wse_ext.py::_fit_branch`).
   Previously `force_n_modes` was read by *both* the EXT and WSE branches, so a
   "capacity-matched" global control (e.g. `force_n_modes: 15`) silently also
   raised the EXT branch to 15 modes, while the H-LSG twin kept its native
   (North/Kaiser) EXT rank (5). This broke the "EXT shared/global, WSE matched"
   construction and is the root cause of the matched-global models' anomalous
   `all_cells` CSI.
2. **Numerical-rank tolerance in `fit_eof`** (`lsg__eof.py`, `rank_tolerance=1e-12`).
   A mean-centred `(n_samples × n_cells)` training matrix has algebraic rank
   ≤ `n_samples − 1`; the previous code kept all `min(n_components, n_samples)`
   SVD vectors, retaining a null trailing mode for the small-event cases
   (Carlisle). The 8th Carlisle singular value is `2.98e-11` vs `s1 = 1014`
   (ratio `2.94e-14`), confirming rank 7, not 8.

## Corrected headline numbers

### Chowilla — Group 1 maximum-surface (wet_train RMSE, m)

| Model | WSE dim | EXT dim | wet RMSE | all_cells CSI | wet CSI |
|---|---|---|---|---|---|
| Global native | 3 | 5 | 0.088 | 0.390 | 0.974 |
| H-LSG (residual k-means) | 15 (3+12) | 5 | 0.093 | 0.390 | 0.976 |
| **Global matched-15** | **15** | **5** | **0.055** | **0.990** | **0.990** |

(previously the matched-15 was reported as 0.085 m / all_cells CSI 0.390 with
the EXT=15 bug.)

### Chowilla — Global matched-15 inducing sweep (wet_train RMSE, m)

| inducing floor | wet RMSE |
|---|---|
| 2 | 0.090 |
| 8 | 0.059 |
| 16 (default) | 0.055 |
| 28 (= n_train) | 0.037 |

H-LSG inducing sweep (unchanged, EXT was already native):
| 2 | 0.244 |
| 8 | 0.096 |
| 16 | 0.093 |
| 28 | 0.073 |

**Key result (Major 1):** at full GP (m=28) matched-global is 0.037 m vs H-LSG
0.073 m; at default m=16 it is 0.055 m vs 0.093 m. The matched-capacity global
is now *substantially* better than H-LSG, strengthening the negative zoning
conclusion rather than weakening it.

### Carlisle — Group 1 maximum-surface (wet_train RMSE, m)

| Model | WSE dim | EXT dim | wet RMSE | O2−O1 |
|---|---|---|---|---|
| Global native | 1 | 2 | 0.112 | 0.064 |
| H-LSG | 13 | 2 | 0.094 | 0.005 |
| **Global forced to 13 (realized 7)** | 7 | 2 | **0.134** | ~0.000 |

(previously "realized 8" → 0.202 m; the null 8th mode was an implementation
artifact. The max-rank global is still worse than H-LSG, so the rank-limited
interpretation holds, but the number changes from 0.202 to 0.134 m.)

Carlisle singular values (mean-centred 8-event max-surface training matrix):
`[1014.1, 140.3, 111.7, 65.9, 47.2, 32.1, 17.3, 2.98e-11]` → rank 7.

## Fixed-EXT oracle (Major 2, new diagnostic `error_budget_fixed_ext`)

The dual-path O1–O4 previously advanced EXT and WSE in lockstep, so O4−O2 was
not a pure WSE attribution. A `fixed-production-EXT` oracle now holds EXT at the
production (O4) reconstruction and sweeps only the WSE stages.

Chowilla matched-15 (m16), test: fixed-EXT O4 = 0.0547, O4−O2 = 0.0435.
Burnett values pending (runs in flight).

## Pending

- Burnett m16 re-runs (global / H-LSG / matched-18) — fixed-EXT oracle + EXT fix.
- Burnett m56 full-inducing (global / H-LSG / matched-18) — Major 4.

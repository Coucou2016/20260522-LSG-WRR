# Burnett River (published LSG benchmark)

**TUFLOW** HF × **HEC-RAS** LF Model B (Fraehr 2024). Same `ingest.kind: fraehr` stack as Carlisle / Chowilla, with Burnett-specific pairing via `BurnettRV_event_summary.csv`.

## Sources

1. Comparison dump: https://doi.org/10.26188/24312658 — `BurnettRV.zip`, ~32 GB, CC BY 4.0, file id `44120564`, MD5 `93df54d5bb54e9b23a09e648648146d8`

```powershell
python scripts/download_published_benchmarks.py --dataset burnett
```

## Local status (2026-08-16)

| Item | Status | Notes |
|------|--------|-------|
| Case folders | **available** via directory junctions | `Geometry_data/`, `HD_model_data/`, `Train_test_split_data/`, `Result_data/`, `HF_EOF_analysis/`, `LSG_modeldata/` → sibling Fraehr unzip. Avoid a second ~32 GB download when that tree exists. |
| Event catalogue | 74 CV events in 4 groups (+ 2 extrap unpaired) | `BurnettRV_event_summary.csv`; ids = LF plan (`p12` → `E12`) |
| Config | `config/burnett.yaml` | Carlisle-proven stack: `wse_ext`, `residual_kmeans`, SGPR floor, UQ `crps_scale`, error budget |
| Ingest | `time_reduction: max` default | ~780k HF cells; full 74-event TS OOM. TUFLOW `wl_data` skips 48-step pad (Fraehr). |

Layout:

```
Geometry_data/Tuflow_Geometry_data.npz   # 780785 cells
Geometry_data/HECRAS_Geometry_data.npz   # 15256 cells
HD_model_data/High-fidelity/Paradise_*_002.npz   # wl_data, time_data
HD_model_data/Low-fidelity/BurnettRV_LFmodelB.p##.hdf
Train_test_split_data/                   # timestep idx for GP; event LOGO via Group
Result_data/Validation_results.npz       # published CSI/RMSE (74 × 5 models)
```

## Zoning choice

Kept **`lsg.zoning: residual_kmeans`**. Grp1 max-surface residual fit was stable
(finite O1–O4; wet_train CSI ≈ 0.975). Did **not** fall back to `none`.
Global A/B: `config/burnett_global.yaml` (optional; not required for mainline).

## Quick commands

```powershell
# Smoke (max surfaces, 4 train + 1 Grp1 val)
python scripts/run_lsg_workflow.py --config config/burnett.yaml --events E30,E31,E32,E33,E12 --time-reduction max

# Grp1 leave-one-group-out (max surfaces, 56 train / 18 val)
python scripts/run_lsg_workflow.py --config config/burnett.yaml --time-reduction max
```

# Chowilla floodplain (published LSG benchmark)

Fine / coarse **HEC-RAS** (Fraehr 2024). Same `ingest.kind: fraehr` stack as Carlisle.

## Sources

1. Comparison dump: https://doi.org/10.26188/24312658 — `Chowilla.zip`, **31 986 950 697 bytes (~32 GB)**, CC BY 4.0, file id `44120567`, MD5 `16e3f4d2b8514b1493a1d78af2751707`
2. Earlier HDF dump (optional): https://doi.org/10.26188/21235782

```powershell
python scripts/download_published_benchmarks.py --dataset chowilla
```

## Local status (2026-08-16)

| Item | Status | Notes |
|------|--------|-------|
| Case folders | **available** via directory junctions | `Geometry_data/`, `HD_model_data/`, `Train_test_split_data/`, `Result_data/`, `HF_EOF_analysis/` → sibling Fraehr unzip (same zip MD5). Avoid a second 32 GB download when that tree exists. |
| Event catalogue | 29 CV plans `p01`–`p29` (+ extrap `p38`/`p39` unpaired) | `Chowilla_event_summary.csv`; groups 1–10 |
| Config | `config/chowilla.yaml` | Carlisle-proven stack: `wse_ext`, `residual_kmeans`, SGPR floor, UQ `crps_scale`, error budget |
| Ingest | `time_reduction: max` default | Full TS for all 29 events does not fit in RAM (~110k HF cells). Use `--time-reduction full --events E1,E2,E3` for LSG-TS smoke. |

Layout (same Fraehr shape as Carlisle):

```
Geometry_data/Geometry_data_HF.npz   # 109914 cells
Geometry_data/Geometry_data_LF.npz   # 1434 cells
HD_model_data/High-fidelity/Chow_HF.p##.hdf
HD_model_data/Low-fidelity/Chow_LF_modelG.p##.hdf
Train_test_split_data/               # timestep idx for GP; event LOGO via Group column
Result_data/Validation_results.npz   # published CSI/RMSE (29 folds × 5 models)
```

Ghost cells and LF warm-up use the Carlisle Fraehr path (`drop_ghost_cells`, `align_lf_to_hf_time`). HF/LF HDF WSE columns match the geometry NPZs after ghost drop.

## Zoning choice

Kept **`lsg.zoning: residual_kmeans`** (Carlisle default). Grp1 max-surface residual fit was stable (finite O1–O4; wet_train CSI ≈ 0.976). Did **not** fall back to `none`. Global A/B: `config/chowilla_global.yaml`.

## Quick commands

```powershell
# Smoke (full TS, 3 events)
python scripts/run_lsg_workflow.py --config config/chowilla.yaml --events E1,E2,E3 --time-reduction full

# Grp1 leave-one-group-out (max surfaces, 28 train / E1 test)
python scripts/run_lsg_workflow.py --config config/chowilla.yaml --time-reduction max
```

# Carlisle (published LSG benchmark)

**HF = LISFLOOD-FP, LF = HEC-RAS.** Results are already computed. Do not install HEC-RAS or re-run the models.

## Source

- Figshare: https://doi.org/10.26188/24312658
- `Carlisle.zip` (9,603,961,435 bytes, file id `44120405`, MD5 `5b4bf7b6007d858a67050fdecc7e6b5f`)
- Companion loaders: `Python_data.zip` (file id `44120348`)
- Published comparison figures: `Comparison_results.zip` (file id `44120360`)

```powershell
python scripts/download_published_benchmarks.py --dataset carlisle
python scripts/download_published_benchmarks.py --dataset python_data
python scripts/download_published_benchmarks.py --dataset comparison_results
```

## Local status (2026-08-15)

| File | Status | Path | Notes |
|------|--------|------|-------|
| `Python_data.zip` | **downloaded + unzipped** | `Python_data.zip` and `python_data/` | 108,090 bytes, MD5 verified |
| `Comparison_results.zip` | **downloaded + unzipped** | `Comparison_results.zip` and `comparison_results/` | 279,586,627 bytes, MD5 verified |
| `Carlisle.zip` | **downloaded + unzipped** | `Carlisle.zip` plus `Geometry_data/`, `HD_model_data/`, `Train_test_split_data/`, `Result_data/` | 9,603,961,435 bytes, MD5 verified 2026-08-15 |
| `Train_test_split_data/` | **unzipped** (not a separate Figshare file) | `Train_test_split_data/` | 10 NPZ folds inside Carlisle.zip |

Unzipped layout (Fraehr 2024):

```
Geometry_data/          Lisflood_Geometry_data.npz (HF), LF_Geometry_data.npz
HD_model_data/High-fidelity/   Run{1-9}_alltimesteps.npz + 2 extrap runs
HD_model_data/Low-fidelity/    Carlisle_LFmodelA.p01-p11.hdf
Train_test_split_data/  Train_test_split_ValidateOnGrp_{1-9}.npz
Result_data/            Validation_results.npz, Validation_results_extrap.npz
```

Then:

```powershell
python scripts/run_lsg_workflow.py --config config/carlisle.yaml
```

`ingest.kind: fraehr` reads geometry NPZ (`XY_coor`, `Z_coor`, `Area`) and pairs HF/LF plans by event id. Unstructured meshes use nearest-neighbour XY interpolation.

## Published CSI / RMSE (for the code team)

Numeric published values are **already on disk**:

- `Result_data/Validation_results.npz` — interpolation / 9 CV folds. Keys: `CSI`, `RMSE`, `MaxWD_R2`, `FI`, `peak_diff`, `pred_time`, `n_timesteps`. Arrays are shape `(9, 5)` for models `[LSG, 1dCNN, LSTM-SRR, GP-EOF, LSTM-EOF]`. Fold-mean LSG: CSI 0.937, RMSE 0.129 m.
- `Result_data/Validation_results_extrap.npz` — 2 extrapolation events, same keys (plus `MaxWD` maps). Fold-mean LSG: CSI 0.896, RMSE 0.184 m.

Paper boxplots (no CSV tables): `comparison_results/Figures/Boxplot_CSI.png`, `Boxplot_RMSE.png`. Plotting scripts: `comparison_results/Model_comparison_allcasestudies.py` (loads `Carlisle/Result_data/Validation_results.npz`).

Exact CV index arrays: `Train_test_split_data/Train_test_split_ValidateOnGrp_{1-9}.npz` (`idx_train`, `idx_test`).

## Workflow smoke (2026-08-15)

```powershell
.\.venv\Scripts\python.exe scripts/run_lsg_workflow.py --config config/carlisle.yaml
```

Ingest **discovers** events E1-E9 and HF NPZ (`wse_data`). It then stops on LF HEC-RAS HDF: `Water Surface` has **5991** cells vs `Geometry_data/LF_Geometry_data.npz` **5681** cells (`WSE cells 5991 != elevation cells 5681`). HDF has no Depth dataset (WSE only). `lsg.hecras.read_cell_centers` also fails on this file (`TypeError` comparing structured HDF names). Data dump is complete; remaining work is ingest mesh alignment, not download.

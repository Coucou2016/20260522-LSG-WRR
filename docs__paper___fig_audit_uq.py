from __future__ import annotations

import json
import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")

print("=== Chowilla UQ JSON detail ===")
s = json.load(
    open(R / "chowilla/workflow_summary_grp1_wse_ext_hlsg_max_uq_calibrated.json", encoding="utf-8")
)
blk = s.get("lsg_max") or {}
for key in ["uq", "uq_uncalibrated"]:
    d = blk.get(key) or {}
    print(f"--- {key} ---")
    for k, v in d.items():
        if isinstance(v, dict):
            print(f"  {k}: {{...}} keys={list(v.keys())}")
        else:
            print(f"  {k}: {v}")

print()
print("=== Carlisle UQ JSON detail (for comparison) ===")
s2 = json.load(
    open(
        R / "carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix_uq_calibrated.json",
        encoding="utf-8",
    )
)
blk2 = s2.get("lsg_max") or {}
for key in ["uq", "uq_uncalibrated"]:
    d = blk2.get(key) or {}
    print(f"--- {key} ---")
    for k, v in d.items():
        if isinstance(v, dict):
            continue
        print(f"  {k}: {v}")

print()
print("=== Burnett UQ JSON detail ===")
s3 = json.load(
    open(R / "burnett/workflow_summary_grp1_wse_ext_hlsg_max_uq_calibrated.json", encoding="utf-8")
)
blk3 = s3.get("lsg_max") or {}
for key in ["uq", "uq_uncalibrated"]:
    d = blk3.get(key) or {}
    print(f"--- {key} ---")
    for k, v in d.items():
        if isinstance(v, dict):
            continue
        print(f"  {k}: {v}")

print()
print("=== Chowilla depth magnitudes (context for CRPS 2.15 m) ===")
raw = np.load(R / "chowilla/pred_examples.npz", allow_pickle=True)
hf = np.asarray(raw["hf_max"][0], dtype=float)
wet = hf >= 0.03
print(
    f"HF depth: max={hf.max():.3f} mean_wet={hf[wet].mean():.3f} p99={np.percentile(hf[wet], 99):.3f}"
)

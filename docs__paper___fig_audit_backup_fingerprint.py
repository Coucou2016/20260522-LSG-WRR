from __future__ import annotations

import json
from pathlib import Path

import numpy as np

R = Path("outputs/evaluation")
tau = 0.03

raw = np.load(R / "chowilla/pred_examples_global_mislabeled_backup.npz", allow_pickle=False)
hf = np.asarray(raw["hf_max"][0], dtype=float)
pred = np.asarray(raw["pred_lsg_max"][0], dtype=float)
lf = np.asarray(raw["lf_upsampled_max"][0], dtype=float)
wet = np.zeros(hf.size, dtype=bool)
wet[np.asarray(raw["wet_idx"], dtype=np.int64)] = True

pw = pred >= tau
hw = hf >= tau
tp = int(np.sum(pw & hw & wet))
fp = int(np.sum(pw & ~hw & wet))
fn = int(np.sum(~pw & hw & wet))
csi_wet = tp / max(tp + fp + fn, 1)
d = np.where(hw, hf, 0.0) - np.where(pw, pred, 0.0)
rmse_wet = float(np.sqrt(np.mean(d[wet] ** 2)))
print(f"backup pred_lsg_max wet-domain: csi={csi_wet:.4f} rmse={rmse_wet:.4f}")
print(f"  hit={tp} miss={fn} fa={fp}")

# archived H-LSG values: csi=0.9756 rmse=0.0932 (workflow_summary_grp1_wse_ext_hlsg_max.json)
print("archived H-LSG:  csi=0.9756 rmse=0.0932")
print("archived global: csi=0.9744 rmse=0.0877")

from __future__ import annotations

import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")
tau = 0.03


def gate(pred, lf):
    return np.where(lf >= tau, pred, 0.0)


def wet_stats(p, h, wet):
    pw = p >= tau
    hw = h >= tau
    tp = int(np.sum(pw & hw & wet))
    fp = int(np.sum(pw & ~hw & wet))
    fn = int(np.sum(~pw & hw & wet))
    csi = tp / max(tp + fp + fn, 1)
    d = np.where(hw, h, 0.0) - np.where(pw, p, 0.0)
    rmse_wet = float(np.sqrt(np.mean(d[wet] ** 2)))
    return csi, rmse_wet, tp, fp, fn


raw = np.load(R / "chowilla/pred_examples.npz", allow_pickle=False)
hf = np.asarray(raw["hf_max"][0], dtype=float)
pred = np.asarray(raw["pred_lsg_max"][0], dtype=float)
lf = np.asarray(raw["lf_upsampled_max"][0], dtype=float)
wet = np.zeros(hf.size, dtype=bool)
wet[np.asarray(raw["wet_idx"], dtype=np.int64)] = True

print("Chowilla saved field, no gate:")
print("  ", wet_stats(pred, hf, wet))
print("Chowilla saved field, LF extent gate applied:")
print("  ", wet_stats(gate(pred, lf), hf, wet))

# workflow reference values:
# global:  wet CSI=0.9744 RMSE=0.0877 (all-cell RMSE 3.789)
# hlsg  :  wet CSI=0.9756 RMSE=0.0932

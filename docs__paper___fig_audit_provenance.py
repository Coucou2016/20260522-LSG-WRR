from __future__ import annotations

import json
import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")
tau = 0.03


def wet_csi(pred_row, hf_row, wet):
    p = pred_row >= tau
    h = hf_row >= tau
    tp = int(np.sum(p & h & wet))
    fp = int(np.sum(p & ~h & wet))
    fn = int(np.sum(~p & h & wet))
    return tp / max(tp + fp + fn, 1)


print("=== Burnett: fingerprint saved pred_examples vs global/hlsg summaries ===")
raw = np.load(R / "burnett/pred_examples.npz", allow_pickle=True)
hf = np.asarray(raw["hf_max"], dtype=float)
pred = np.asarray(raw["pred_lsg_max"], dtype=float)
wet = np.zeros(hf.shape[1], dtype=bool)
wet[np.asarray(raw["wet_idx"], dtype=np.int64)] = True
csis = [wet_csi(pred[i], hf[i], wet) for i in range(hf.shape[0])]
print(f"saved field wet-domain CSI per event: mean={np.mean(csis):.4f} {np.round(csis, 4)}")
for key, name in [
    ("burnett/workflow_summary_grp1_wse_ext_hlsg_max.json", "burnett H-LSG"),
    ("burnett/workflow_summary_grp1_wse_ext_global_max.json", "burnett global"),
]:
    s = json.load(open(R / key, encoding="utf-8"))
    sp = ((s.get("score_protocol") or {}).get("lsg_max") or {})
    print(f"{name}: all_cells csi={sp.get('all_cells', {}).get('csi')} wet_train csi={sp.get('wet_train', {}).get('csi')}")

print()
print("=== Carlisle: fingerprint saved pred_examples ===")
raw = np.load(R / "carlisle/pred_examples.npz", allow_pickle=True)
hf = np.asarray(raw["hf_max"], dtype=float)
pred = np.asarray(raw["pred_lsg_max"], dtype=float)
wet = np.zeros(hf.shape[1], dtype=bool)
wet[np.asarray(raw["wet_idx"], dtype=np.int64)] = True
print(f"saved field wet-domain CSI: {wet_csi(pred[0], hf[0], wet):.4f}")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "carlisle H-LSG+SGPR"),
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_residual_kmeans.json", "carlisle H-LSG"),
    ("carlisle/workflow_summary_full_Grp1_wse_ext.json", "carlisle global"),
]:
    s = json.load(open(R / key, encoding="utf-8"))
    sp = ((s.get("score_protocol") or {}).get("lsg_max") or {})
    print(f"{name}: wet_train csi={sp.get('wet_train', {}).get('csi')} rmse={sp.get('wet_train', {}).get('rmse')}")
# depth RMSE fingerprint on saved field
p = pred[0]
h = hf[0]
rmse_all = float(np.sqrt(np.mean((np.where(h >= tau, h, 0) - np.where(p >= tau, p, 0)) ** 2)))
print(f"saved field all-cell clipped-depth RMSE (approx): {rmse_all:.4f}")

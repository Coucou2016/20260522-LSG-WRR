from __future__ import annotations

import json
import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")
tau = 0.03

print("=== Chowilla: which model wrote pred_examples.npz? (compare pred vs variants) ===")
raw = np.load(R / "chowilla/pred_examples.npz", allow_pickle=True)
pred = np.asarray(raw["pred_lsg_max"][0], dtype=float)
hf = np.asarray(raw["hf_max"][0], dtype=float)
wet = np.asarray(raw["wet_idx"], dtype=np.int64)
mask = np.zeros(hf.size, dtype=bool)
mask[wet] = True


def ext_metrics(p, h):
    pw = p >= tau
    hw = h >= tau
    tp = int(np.sum(pw & hw))
    fp = int(np.sum(pw & ~hw))
    fn = int(np.sum(~pw & hw))
    tn = int(np.sum(~pw & ~hw))
    csi = tp / max(tp + fp + fn, 1)
    return {"csi": csi, "hit": tp, "miss": fn, "fa": fp, "tn": tn}


m = ext_metrics(pred, hf)
print("saved pred_examples lsg_max (all cells):", m)
m_mask = ext_metrics(pred[mask], hf[mask])
print("saved pred_examples lsg_max (wet_train mask):", m_mask)

print()
print("=== Burnett: 18 events -> per-event CSI (pred vs HF), envelope vs event-0 ===")
rawb = np.load(R / "burnett/pred_examples.npz", allow_pickle=True)
hf_all = np.asarray(rawb["hf_max"], dtype=float)
pred_all = np.asarray(rawb["pred_lsg_max"], dtype=float)
lf_all = np.asarray(rawb["lf_upsampled_max"], dtype=float)
test_ids = [str(x) for x in np.asarray(rawb["test_ids"]).tolist()]
print("test_ids:", test_ids)
print("event | HF_wet | LSG_csi | LF_csi")
for i in range(hf_all.shape[0]):
    mh = ext_metrics(pred_all[i], hf_all[i])
    ml = ext_metrics(lf_all[i], hf_all[i])
    print(
        f"{test_ids[i]:5s} | {int((hf_all[i] >= tau).sum()):7d} | {mh['csi']:.4f} | {ml['csi']:.4f}"
    )
# envelope over test events vs event0
env_hf = np.nanmax(hf_all, axis=0)
env_pred = np.nanmax(pred_all, axis=0)
env_lf = np.nanmax(lf_all, axis=0)
print(
    "envelope:",
    "LSG",
    ext_metrics(env_pred, env_hf),
    "LF",
    ext_metrics(env_lf, env_hf),
)

print()
print("=== Chowilla H-LSG workflow: what's the model's own extent metrics? ===")
s = json.load(
    open(R / "chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json", encoding="utf-8")
)
for k in ["lsg_max", "lf_only", "lsg_max_fraehr_aligned", "lf_extent_gated"]:
    b = s.get(k)
    if isinstance(b, dict):
        keep = {kk: b[kk] for kk in ["csi", "pod", "rfa", "hit", "miss", "false_alarm"] if kk in b}
        print(f"{k}: {keep}")

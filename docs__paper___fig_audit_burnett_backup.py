from __future__ import annotations

import numpy as np
from pathlib import Path

R = Path("outputs/evaluation/burnett")
a = np.load(R / "pred_examples.npz", allow_pickle=False)
b = np.load(R / "pred_examples_hlsg_backup.npz", allow_pickle=False)
print("current keys:", a.files)
print("backup keys:", b.files)
same = np.array_equal(np.asarray(a["pred_lsg_max"]), np.asarray(b["pred_lsg_max"]))
print("pred_lsg_max identical to hlsg backup:", same)
if not same:
    d = np.abs(np.asarray(a["pred_lsg_max"], dtype=float) - np.asarray(b["pred_lsg_max"], dtype=float))
    print(f"  max abs diff = {d.max():.4f}, mean = {d.mean():.6f}")
    hf = np.asarray(a["hf_max"], dtype=float)
    tau = 0.03
    diff_cells = (np.asarray(a["pred_lsg_max"]) >= tau) != (np.asarray(b["pred_lsg_max"]) >= tau)
    print(f"  extent-class disagreement cells: {int(diff_cells.sum())}")

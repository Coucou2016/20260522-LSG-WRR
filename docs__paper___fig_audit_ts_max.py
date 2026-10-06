from __future__ import annotations

import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")
tau = 0.03

for case in ["carlisle", "chowilla", "burnett"]:
    raw = np.load(R / case / "pred_examples.npz", allow_pickle=False)
    pmax = np.asarray(raw["pred_lsg_max"], dtype=float)
    if "pred_lsg_ts_max" not in raw.files:
        print(f"{case}: pred_lsg_ts_max MISSING")
        continue
    pts = np.asarray(raw["pred_lsg_ts_max"], dtype=float)
    if pts.shape != pmax.shape:
        print(f"{case}: shape mismatch {pts.shape} vs {pmax.shape}")
        continue
    identical = np.array_equal(pts, pmax)
    maxdiff = float(np.max(np.abs(pts - pmax)))
    hf = np.asarray(raw["hf_max"], dtype=float)
    same_extent = np.array_equal(pts >= tau, pmax >= tau)
    print(
        f"{case}: ts_max identical to lsg_max: {identical} max_abs_diff={maxdiff:.6f} "
        f"extent identical: {same_extent}"
    )

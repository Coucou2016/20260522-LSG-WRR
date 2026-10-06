from __future__ import annotations

import numpy as np
from pathlib import Path

p = Path("outputs/models/chowilla/lsg_max_state.npz")
raw = np.load(p, allow_pickle=True)
print("state keys:", raw.files)
for k in ["uq_var_scale", "zoning", "n_zones", "config"]:
    if k in raw.files:
        v = raw[k]
        print(f"  {k}: {v if v.ndim == 0 else v.shape}")

p2 = Path("outputs/models/carlisle/lsg_max_state.npz")
raw2 = np.load(p2, allow_pickle=True)
print("carlisle state keys:", raw2.files)
if "uq_var_scale" in raw2.files:
    print("  carlisle uq_var_scale:", raw2["uq_var_scale"])

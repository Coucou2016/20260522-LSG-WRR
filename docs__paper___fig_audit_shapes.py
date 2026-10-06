from __future__ import annotations
import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")

for case in ["carlisle", "chowilla", "burnett"]:
    p = R / case / "pred_examples.npz"
    raw = np.load(p, allow_pickle=True)
    hf = raw["hf_max"]
    pred = raw["pred_lsg_max"]
    lf = raw["lf_upsampled_max"]
    prob = raw["inundation_prob_lsg_max"]
    wet = raw["wet_idx"] if "wet_idx" in raw.files else None
    print(
        f"{case}: hf_max.shape={hf.shape} pred.shape={pred.shape} lf.shape={lf.shape} "
        f"prob.shape={prob.shape} wet_idx={'n/a' if wet is None else wet.shape} "
        f"data_mode={raw['data_mode']}"
    )
    # Per-event extent statistics at idx=0 (what Figures 2/3/4 plot)
    tau = 0.03
    h = np.asarray(hf[0], dtype=float)
    pr = np.asarray(pred[0], dtype=float)
    lf0 = np.asarray(lf[0], dtype=float)
    hf_w = h >= tau
    lsg_w = pr >= tau
    lf_w = lf0 >= tau
    print(
        f"  event0: HF wet={hf_w.sum()} LSG wet={lsg_w.sum()} LF wet={lf_w.sum()} "
        f"hit={(hf_w & lsg_w).sum()} miss={(hf_w & ~lsg_w).sum()} fa={(~hf_w & lsg_w).sum()}"
    )
    print(
        f"  LF  : hit={(hf_w & lf_w).sum()} miss={(hf_w & ~lf_w).sum()} fa={(~hf_w & lf_w).sum()}"
    )
    if wet is not None:
        w = np.asarray(wet, dtype=np.int64)
        print(
            f"  wet_idx n={w.size}; HF wet outside mask: {(hf_w & ~np.isin(np.arange(h.size), w)).sum()}"
        )
    # probability extremes
    pw = np.asarray(prob[0], dtype=float)
    print(
        f"  P(wet) min={pw.min():.4f} max={pw.max():.4f} "
        f"frac[0.5,0.95)={float(np.mean((pw >= 0.5) & (pw < 0.95))):.4f}"
    )

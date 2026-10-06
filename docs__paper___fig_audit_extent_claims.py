from __future__ import annotations

import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")
tau = 0.03


def counts(p, h):
    pw = p >= tau
    hw = h >= tau
    return {
        "hit": int(np.sum(pw & hw)),
        "miss": int(np.sum(~pw & hw)),
        "fa": int(np.sum(pw & ~hw)),
    }


for case in ["carlisle", "chowilla", "burnett"]:
    raw = np.load(R / case / "pred_examples.npz", allow_pickle=True)
    hf = np.asarray(raw["hf_max"], dtype=float)
    pred = np.asarray(raw["pred_lsg_max"], dtype=float)
    lf = np.asarray(raw["lf_upsampled_max"], dtype=float)
    ids = [str(x) for x in np.asarray(raw["test_ids"]).tolist()]
    n = hf.shape[0]
    lsg_tot = {"hit": 0, "miss": 0, "fa": 0}
    lf_tot = {"hit": 0, "miss": 0, "fa": 0}
    for i in range(n):
        c_lsg = counts(pred[i], hf[i])
        c_lf = counts(lf[i], hf[i])
        for k in lsg_tot:
            lsg_tot[k] += c_lsg[k]
            lf_tot[k] += c_lf[k]
    print(f"=== {case} ({n} test events: {ids[:4]}{'...' if n > 4 else ''}) ===")
    print(
        f"  LF : hit={lf_tot['hit']} miss={lf_tot['miss']} fa={lf_tot['fa']} "
        f"CSI={lf_tot['hit'] / (lf_tot['hit'] + lf_tot['miss'] + lf_tot['fa']):.4f}"
    )
    print(
        f"  LSG: hit={lsg_tot['hit']} miss={lsg_tot['miss']} fa={lsg_tot['fa']} "
        f"CSI={lsg_tot['hit'] / (lsg_tot['hit'] + lsg_tot['miss'] + lsg_tot['fa']):.4f}"
    )
    print(
        f"  delta: miss {lf_tot['miss']} -> {lsg_tot['miss']} ({lsg_tot['miss'] - lf_tot['miss']:+d}); "
        f"fa {lf_tot['fa']} -> {lsg_tot['fa']} ({lsg_tot['fa'] - lf_tot['fa']:+d})"
    )

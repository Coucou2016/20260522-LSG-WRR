from __future__ import annotations

import numpy as np
from pathlib import Path

R = Path("outputs/evaluation")
raw = np.load(R / "carlisle/pred_examples.npz", allow_pickle=False)
p = np.asarray(raw["inundation_prob_lsg_max"][0], dtype=float)
hf = np.asarray(raw["hf_max"][0], dtype=float)
wet = hf >= 0.03

print("n cells:", p.size)
print("0.5 <= P < 0.95:", int(np.sum((p >= 0.5) & (p < 0.95))))
print("0.5  < P < 0.95:", int(np.sum((p > 0.5) & (p < 0.95))))
print("0.5 <= P <= 0.95:", int(np.sum((p >= 0.5) & (p <= 0.95))))
fr = (p >= 0.5) & (p < 0.95)
print("fringe wet freq overall:", float(np.mean(wet[fr])))
for lo, hi in [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.95)]:
    b = (p >= lo) & (p < hi)
    print(f"  [{lo},{hi}): n={int(b.sum())} wetfreq={float(np.mean(wet[b])):.3f}")
print("P<0.05 frac:", float(np.mean(p < 0.05)))
print("P>0.95 frac:", float(np.mean(p > 0.95)))
# legend-label check for fig08b: non-fringe wet cells with P<0.5 (misses) exist?
base_wet = ~fr & wet
print("HF-wet cells outside fringe:", int(base_wet.sum()))
print("  of those with P<0.5 (misses):", int(np.sum((p < 0.5) & base_wet)))
print("  of those with P>=0.95:", int(np.sum((p >= 0.95) & base_wet)))
base_dry = ~fr & ~wet
print("HF-dry cells outside fringe:", int(base_dry.sum()))
print("  of those with P<0.5:", int(np.sum((p < 0.5) & base_dry)))
print("  of those with P>=0.95:", int(np.sum((p >= 0.95) & base_dry)))

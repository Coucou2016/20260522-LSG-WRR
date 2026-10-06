"""Diagnostic for the non-monotonic dip in the Carlisle reliability diagram (Fig 8a)."""
import json
import numpy as np

TAU = 0.03
npz = np.load("outputs/evaluation/carlisle/pred_examples.npz")
hf = np.asarray(npz["hf_max"], dtype=np.float64).ravel()
p_raw = np.asarray(npz["inundation_prob_lsg_max"], dtype=np.float64).ravel()
pred = np.asarray(npz["pred_lsg_max"], dtype=np.float64).ravel()
terrain = np.asarray(npz["terrain_hf"], dtype=np.float64).ravel()

obs_wet = hf >= TAU
print(f"n_cells={hf.size}  n_wet={int(obs_wet.sum())}  wet_frac={obs_wet.mean():.4f}")

edges = np.linspace(0, 1, 11)
print("\n-- raw P(wet) reliability bins (all cells) --")
print(f"{'bin':>12} {'count':>9} {'obs_freq':>9} {'mean_pred_depth':>15} {'obs_dry_frac':>12}")
for i in range(10):
    m = (p_raw >= edges[i]) & (p_raw < edges[i + 1]) if i < 9 else (p_raw >= edges[i]) & (p_raw <= edges[i + 1])
    n = int(m.sum())
    if n == 0:
        print(f"{edges[i]:.1f}-{edges[i+1]:.1f} {0:>9} {'--':>9} {'--':>15} {'--':>12}")
        continue
    of = float(obs_wet[m].mean())
    pd = float(pred[m].mean())
    dry = float((~obs_wet[m]).mean())
    print(f"{edges[i]:.1f}-{edges[i+1]:.1f} {n:>9} {of:>9.4f} {pd:>15.4f} {dry:>12.4f}")

# Focus on the dip region: predicted prob in (0.5, 0.95)
mid = (p_raw > 0.5) & (p_raw < 0.95)
print(f"\nmid-prob cells (0.5<p<0.95): n={int(mid.sum())} ({100*mid.mean():.3f}% of domain)")
print(f"  observed wet frac among them: {obs_wet[mid].mean():.4f}")
print(f"  predicted depth stats: mean={pred[mid].mean():.4f}  median={np.median(pred[mid]):.4f}  "
      f"frac with pred_depth>=tau: {(pred[mid] >= TAU).mean():.4f}")
# Are dip cells model-says-wet but HF-dry? (false-alarm fringe)
fa = mid & (pred >= TAU) & (~obs_wet)
print(f"  false-alarm fringe (pred wet, HF dry): n={int(fa.sum())} = {100*fa.sum()/max(mid.sum(),1):.1f}% of mid cells")

# Compare predicted depth of FA fringe vs correctly-hit mid cells
hit = mid & (pred >= TAU) & obs_wet
print(f"  hit mid cells: n={int(hit.sum())} mean pred depth={pred[hit].mean():.4f}" if hit.sum() else "  hit mid cells: 0")
print(f"  FA  mid cells mean pred depth={pred[fa].mean():.4f}" if fa.sum() else "  FA mid cells: 0")

# Depth margin of FA fringe: how shallow are they in the surrogate?
if fa.sum():
    print(f"  FA fringe pred-depth quantiles 10/50/90: "
          f"{np.quantile(pred[fa], [0.1, 0.5, 0.9]).round(4)}")

# Latent-margin view: P(wet) in (0.5,0.95) means |mu-tau| ~ sigma. Split by sign of mu-tau.
# mu approx = pred depth + tau mapping is not stored; use pred depth as mapped-depth proxy.
shallow_fa = fa & (pred < 0.10)
print(f"  FA fringe with pred depth < 0.10 m: {100*shallow_fa.sum()/max(fa.sum(),1):.1f}%")

# Calibrated probs for the same cells (s=0.417): recompute via probit shift is not possible without
# mu/sigma; instead report where FA fringe cells land using saved calibrated reliability (JSON).
print("\n-- per-bin composition of the fringe --")
for i in range(6, 10):
    lo, hi = edges[i], edges[i + 1]
    m = (p_raw >= lo) & (p_raw < hi) if i < 9 else (p_raw >= lo) & (p_raw <= hi)
    n = int(m.sum())
    if n == 0:
        continue
    fa_n = int((m & (pred >= TAU) & (~obs_wet)).sum())
    print(f"  bin {lo:.1f}-{hi:.1f}: n={n}  obs_freq={obs_wet[m].mean():.3f}  "
          f"FA_share={100*fa_n/n:.1f}%  mean_pred_depth={pred[m].mean():.3f}")

print("\n-- where the mass sits overall --")
for lo, hi in [(0, 0.05), (0.05, 0.5), (0.5, 0.95), (0.95, 1.0)]:
    m = (p_raw >= lo) & (p_raw < hi) if hi < 1 else (p_raw >= lo) & (p_raw <= hi)
    print(f"  P in [{lo},{hi}): {100*m.mean():.3f}%  obs_wet={obs_wet[m].mean():.4f}" if m.sum() else f"  P in [{lo},{hi}): 0%")

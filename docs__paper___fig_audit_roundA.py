"""Round-figure self-audit: verify figure source values against JSONs."""
from __future__ import annotations

import json
from pathlib import Path

R = Path("outputs/evaluation")


def load(rel: str):
    p = R / rel
    return json.load(open(p, encoding="utf-8")) if p.is_file() else None


def wt(s, v):
    b = (s.get("score_protocol") or {}).get(v) or {}
    w = b.get("wet_train") or {}
    return w.get("csi"), w.get("rmse")


print("=== Fig 5/7: wet_train CSI/RMSE (LSG-Max) ===")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext.json", "Carlisle Global"),
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_residual_kmeans.json", "Carlisle H-LSG"),
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "Carlisle H-LSG+SGPR"),
    ("chowilla/workflow_summary_grp1_wse_ext_global_max.json", "Chowilla Global"),
    ("chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json", "Chowilla H-LSG"),
    ("burnett/workflow_summary_grp1_wse_ext_global_max.json", "Burnett Global"),
    ("burnett/workflow_summary_grp1_wse_ext_hlsg_max.json", "Burnett H-LSG"),
]:
    s = load(key)
    if s is None:
        print(f"{name}: MISSING {key}")
        continue
    c, r = wt(s, "lsg_max")
    if c is not None:
        print(f"{name:24s} CSI={c:.4f} RMSE={r:.4f}")
    else:
        print(f"{name:24s} NO wet_train block")

print()
print("=== Fig 5: LF-only wet_train ===")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "Carlisle"),
    ("chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json", "Chowilla"),
    ("burnett/workflow_summary_grp1_wse_ext_hlsg_max.json", "Burnett"),
]:
    s = load(key)
    c, r = wt(s, "lf_only")
    if c is not None:
        print(f"{name:10s} LF CSI={c:.4f} RMSE={r:.4f}")
    else:
        print(f"{name:10s} LF NO wet_train block")
    # also top-level lf_only block
    lf = s.get("lf_only") or {}
    if lf:
        print(f"{'':10s} top-level lf_only: csi={lf.get('csi')} rmse={lf.get('rmse')}")

print()
print("=== Carlisle LSG-TS score_protocol blocks ===")
s = load("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json")
sp = s.get("score_protocol") or {}
for v in ["lsg_ts", "lf_only"]:
    blk = sp.get(v)
    if not blk:
        print(f"score_protocol.{v}: MISSING")
        continue
    for dom in ["all_cells", "wet_train"]:
        d = blk.get(dom) or {}
        print(f"score_protocol.{v}.{dom}: csi={d.get('csi')} rmse={d.get('rmse')}")
ts = s.get("lsg_ts") or {}
print("lsg_ts.ts_csi =", ts.get("ts_csi"), " ts_rmse =", ts.get("ts_rmse"))
print("lsg_ts.max_csi =", ts.get("max_csi"), " max_rmse =", ts.get("max_rmse"))

print()
print("=== Fig 8: UQ pairs (before/after) ===")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix_uq_calibrated.json", "Carlisle"),
    ("chowilla/workflow_summary_grp1_wse_ext_hlsg_max_uq_calibrated.json", "Chowilla"),
    ("burnett/workflow_summary_grp1_wse_ext_hlsg_max_uq_calibrated.json", "Burnett"),
]:
    s = load(key)
    if s is None:
        print(f"{name}: MISSING {key} -> fallback workflow summary (before = NaN!)")
        continue
    blk = s.get("lsg_max") or {}
    cal = blk.get("uq") or {}
    raw = blk.get("uq_uncalibrated")
    print(
        f"{name:10s} crps before={raw.get('crps') if raw else None} "
        f"after={cal.get('crps')} cov90 before={raw.get('coverage_90') if raw else None} "
        f"after={cal.get('coverage_90')} cov90_active before={raw.get('coverage_90_active') if raw else None} after={cal.get('coverage_90_active')}"
    )
    rel_cal = cal.get("reliability") or {}
    rel_raw = (raw or {}).get("reliability") or {}
    print(
        f"{'':10s} reliability bins: before n={len(rel_raw.get('predicted') or [])} after n={len(rel_cal.get('predicted') or [])}"
    )

print()
print("=== Fig 9: Chowilla zoning CSI/RMSE ===")
for key, name in [
    ("chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json", "Residual k-means"),
    ("chowilla/workflow_summary_grp1_wse_ext_wet_correlation_max.json", "Wet-correlation"),
    ("chowilla/workflow_summary_grp1_wse_ext_global_max.json", "Global (none)"),
]:
    s = load(key)
    c, r = wt(s, "lsg_max")
    print(f"{name:18s} CSI={c:.4f} RMSE={r:.4f}")

print()
print("=== Fig 6: error budget test rows ===")
for key, name, variant in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "Carlisle LSG-Max", "lsg_max"),
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "Carlisle LSG-TS", "lsg_ts"),
    ("chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json", "Chowilla LSG-Max", "lsg_max"),
    ("burnett/workflow_summary_grp1_wse_ext_hlsg_max.json", "Burnett LSG-Max", "lsg_max"),
]:
    s = load(key)
    eb = (s.get(variant) or {}).get("error_budget")
    if not eb:
        print(f"{name}: NO error_budget")
        continue
    for e in eb:
        if e.get("split") == "test":
            print(
                f"{name:18s} test: O1={e['o1_rmse']:.4f} O2={e['o2_rmse']:.4f} "
                f"O3={e['o3_rmse']:.4f} O4={e['o4_rmse']:.4f}"
            )
        elif e.get("split") == "train":
            print(
                f"{name:18s} train: O1={e['o1_rmse']:.4f} O2={e['o2_rmse']:.4f} "
                f"O3={e['o3_rmse']:.4f} O4={e['o4_rmse']:.4f}"
            )

print()
print("=== Fig 2/3/4 spatial bundles: test event ids & field shapes ===")
import numpy as np

for case in ["carlisle", "chowilla", "burnett"]:
    p = R / case / "pred_examples.npz"
    if not p.is_file():
        print(f"{case}: pred_examples.npz MISSING")
        continue
    raw = np.load(p, allow_pickle=True)
    test_ids = [str(x) for x in np.asarray(raw["test_ids"]).tolist()]
    hf = np.asarray(raw["hf_max"][0], dtype=float)
    print(
        f"{case:10s} test_ids={test_ids[:6]} n={hf.size} "
        f"hf_max finite={np.isfinite(hf).sum()} "
        f"has_lf={'lf_upsampled_max' in raw.files} "
        f"has_prob={'inundation_prob_lsg_max' in raw.files} "
        f"files={raw.files}"
    )

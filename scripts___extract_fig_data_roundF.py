"""Extract the numeric values backing each figure for the figure-review audit pack."""
from __future__ import annotations

import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "outputs" / "evaluation"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def wet(s, v):
    b = (s.get("score_protocol") or {}).get(v) or {}
    return (b.get("wet_train") if isinstance(b, dict) else None) or {}


files = {
    "carlisle_sgpr": R / "carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json",
    "carlisle_global_capacity": R / "carlisle/workflow_summary_grp1_wse_ext_global_max_capacity.json",
    "chowilla_hlsg": R / "chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json",
    "chowilla_global": R / "chowilla/workflow_summary_grp1_wse_ext_global_max.json",
    "chowilla_wet_corr": R / "chowilla/workflow_summary_grp1_wse_ext_wet_correlation_max.json",
    "burnett_hlsg": R / "burnett/workflow_summary_grp1_wse_ext_hlsg_max.json",
    "burnett_global": R / "burnett/workflow_summary_grp1_wse_ext_global_max.json",
}

print("=== FIG05 cross-case wet_train CSI/RMSE ===")
for k, p in files.items():
    s = load(p)
    if not s:
        continue
    for v in ["lf_only", "lsg_max", "lsg_ts"]:
        w = wet(s, v)
        if "csi" in w:
            print(f"{k:24s} {v:9s} CSI={w['csi']:.4f} RMSE={w['rmse']:.4f}")

print()
print("=== FIG06 O1-O4 (train/test) ===")
for k in ["carlisle_sgpr", "chowilla_hlsg", "burnett_hlsg"]:
    s = load(files[k])
    if not s:
        continue
    for v in ["lsg_max", "lsg_ts"]:
        rows = (s.get(v) or {}).get("error_budget")
        if rows:
            print(f"-- {k}/{v} --")
            for r in rows:
                if isinstance(r, dict):
                    print(f"  {r.get('split'):5s} O1={r.get('o1_rmse'):.4f} "
                          f"O2={r.get('o2_rmse'):.4f} O3={r.get('o3_rmse'):.4f} "
                          f"O4={r.get('o4_rmse'):.4f}")

print()
print("=== FIG07 Global vs H-LSG wet_train ===")
for k in ["carlisle_global_capacity", "carlisle_sgpr", "chowilla_global",
          "chowilla_hlsg", "burnett_global", "burnett_hlsg"]:
    s = load(files[k])
    if not s:
        continue
    w = wet(s, "lsg_max")
    if "csi" in w:
        print(f"{k:24s} CSI={w['csi']:.4f} RMSE={w['rmse']:.4f}")

print()
print("=== FIG09 Chowilla zoning ===")
for k in ["chowilla_hlsg", "chowilla_wet_corr", "chowilla_global"]:
    s = load(files[k])
    if not s:
        continue
    w = wet(s, "lsg_max")
    if "csi" in w:
        print(f"{k:24s} CSI={w['csi']:.4f} RMSE={w['rmse']:.4f}")

print()
print("=== FIG08 UQ CRPS/coverage ===")
for c in ["carlisle", "chowilla", "burnett"]:
    hits = list(R.rglob("*_uq_calibrated.json"))
    p = None
    for x in hits:
        if x.name.startswith(c):
            p = x
            break
    if not p:
        print(f"{c}: MISSING")
        continue
    s = load(p)
    b = (s.get("lsg_max") or {})
    raw = b.get("uq_uncalibrated") or {}
    cal = b.get("uq") or {}
    print(f"{c}: before CRPS={raw.get('crps')} after CRPS={cal.get('crps')} "
          f"cov90={cal.get('coverage_90')} cov90_active={cal.get('coverage_90_active')}")

"""Extract the numeric values backing each figure for the figure-review round."""
from __future__ import annotations

import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "outputs" / "evaluation"


def wet(summary, variant):
    b = (summary.get("score_protocol") or {}).get(variant) or {}
    wt = (b.get("wet_train") if isinstance(b, dict) else None) or {}
    return wt


files = {
    "carlisle_sgpr": R / "carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json",
    "carlisle_global_cap": R / "carlisle/workflow_summary_grp1_wse_ext_global_max_capacity.json",
    "chowilla_hlsg": R / "chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json",
    "chowilla_global": R / "chowilla/workflow_summary_grp1_wse_ext_global_max.json",
    "chowilla_wet": R / "chowilla/workflow_summary_grp1_wse_ext_wet_correlation_max.json",
    "burnett_hlsg": R / "burnett/workflow_summary_grp1_wse_ext_hlsg_max.json",
    "burnett_global": R / "burnett/workflow_summary_grp1_wse_ext_global_max.json",
}

print("=== CSI/RMSE (wet_train) for fig05/07/09 ===")
for k, p in files.items():
    if not p.is_file():
        print(f"{k}: MISSING {p}")
        continue
    s = json.loads(p.read_text(encoding="utf-8"))
    for v in ["lf_only", "lsg_max", "lsg_ts"]:
        w = wet(s, v)
        if w and "csi" in w:
            print(f"{k:20s} {v:9s} CSI={w['csi']:.4f} RMSE={w['rmse']:.4f}")

print()
print("=== CRPS before/after (fig08d) + coverage ===")
for k in ["carlisle", "chowilla", "burnett"]:
    hits = list(R.rglob("*_uq_calibrated.json"))
    p = None
    for cand in hits:
        if cand.name.startswith(k):
            p = cand
            break
    if p is None:
        print(f"{k}: no uq_calibrated json")
        continue
    s = json.loads(p.read_text(encoding="utf-8"))
    b = s.get("lsg_max") or {}
    raw = b.get("uq_uncalibrated") or {}
    cal = b.get("uq") or {}
    cov90 = cal.get("coverage_90")
    cov90a = cal.get("coverage_90_active")
    print(f"{k}: before CRPS={raw.get('crps')} | after CRPS={cal.get('crps')} "
          f"| cov90={cov90} cov90_active={cov90a}")

print()
print("=== O1-O4 error budget (fig06) ===")
for k in ["carlisle_sgpr", "chowilla_hlsg", "burnett_hlsg"]:
    p = files[k]
    if not p.is_file():
        print(f"{k}: MISSING")
        continue
    s = json.loads(p.read_text(encoding="utf-8"))
    for v in ["lsg_max", "lsg_ts"]:
        rows = (s.get(v) or {}).get("error_budget")
        if rows:
            print(f"--- {k} / {v} ---")
            for r in rows:
                if isinstance(r, dict):
                    print(f"  split={r.get('split'):5s} O1={r.get('o1_rmse'):.4f} "
                          f"O2={r.get('o2_rmse'):.4f} O3={r.get('o3_rmse'):.4f} "
                          f"O4={r.get('o4_rmse'):.4f}")

from __future__ import annotations

import json
from pathlib import Path

R = Path("outputs/evaluation")

print("=== Carlisle all-cell RMSE fingerprints ===")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext.json", "global"),
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_residual_kmeans.json", "hlsg"),
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "hlsg+sgpr"),
]:
    s = json.load(open(R / key, encoding="utf-8"))
    sp = ((s.get("score_protocol") or {}).get("lsg_max") or {})
    ac = sp.get("all_cells") or {}
    print(f"{name}: all_cells csi={ac.get('csi')} rmse={ac.get('rmse')}")

print()
print("saved Carlisle field all-cell clipped RMSE ~ 0.0607 (computed earlier)")

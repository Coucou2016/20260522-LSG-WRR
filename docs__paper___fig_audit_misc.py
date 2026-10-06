from __future__ import annotations

import json
from pathlib import Path

R = Path("outputs/evaluation")

print("=== lsg_ts score_protocol presence ===")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "Carlisle"),
    ("chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json", "Chowilla"),
    ("burnett/workflow_summary_grp1_wse_ext_hlsg_max.json", "Burnett"),
]:
    s = json.load(open(R / key, encoding="utf-8"))
    sp = s.get("score_protocol") or {}
    has_ts = "lsg_ts" in sp
    ts_block = sp.get("lsg_ts") or {}
    wt = ts_block.get("wet_train") if isinstance(ts_block, dict) else None
    print(f"{name}: score_protocol has lsg_ts={has_ts}, wet_train={bool(wt)}")

print()
print("=== Carlisle H-LSG (non-SGPR) summary detail: why RMSE 0.267? ===")
s = json.load(
    open(R / "carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_residual_kmeans.json", encoding="utf-8")
)
lsg = s.get("lsg_max") or {}
for k in ["rmse_wet_train", "csi_wet_train", "n_modes_global", "n_zones", "config_notes"]:
    if k in lsg:
        print(f"  lsg_max.{k}: {lsg[k]}")
print("  lsg_max keys:", list(lsg.keys())[:20])
sp = s.get("score_protocol") or {}
print("  score_protocol.lsg_max:", sp.get("lsg_max"))
print("  top-level keys:", [k for k in s.keys()][:30])

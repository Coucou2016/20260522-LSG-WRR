from __future__ import annotations

import json
from pathlib import Path

R = Path("outputs/evaluation/chowilla")

a = json.load(open(R / "workflow_summary_grp1_wse_ext_hlsg_max.json", encoding="utf-8"))
b = json.load(open(R / "workflow_summary_grp1_wse_ext_hlsg_max_capacity_rerun.json", encoding="utf-8"))

for name, s in [("9:40 hlsg_max", a), ("17:57 capacity_rerun", b)]:
    sp = ((s.get("score_protocol") or {}).get("lsg_max") or {})
    wt = sp.get("wet_train") or {}
    ac = sp.get("all_cells") or {}
    eb = ((s.get("lsg_max") or {}).get("error_budget")) or []
    test = next((e for e in eb if e.get("split") == "test"), {})
    print(
        f"{name}: wet CSI={wt.get('csi'):.4f} RMSE={wt.get('rmse'):.4f} "
        f"all CSI={ac.get('csi'):.4f} RMSE={ac.get('rmse'):.4f}"
    )
    print(
        f"   error_budget test: O1={test.get('o1_rmse')} O2={test.get('o2_rmse')} "
        f"O3={test.get('o3_rmse')} O4={test.get('o4_rmse')}"
    )

from __future__ import annotations

import json
from pathlib import Path

R = Path("outputs/evaluation")

print("=== Carlisle global-model artifact comparison ===")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext.json", "full_Grp1 (Fig 7 source)"),
    ("carlisle/workflow_summary_grp1_wse_ext_global_max_capacity.json", "capacity rerun (Table 6 source)"),
]:
    p = R / key
    if not p.is_file():
        print(f"{name}: MISSING")
        continue
    s = json.load(open(p, encoding="utf-8"))
    sp = ((s.get("score_protocol") or {}).get("lsg_max") or {})
    wt = sp.get("wet_train") or {}
    ac = sp.get("all_cells") or {}
    lsg = s.get("lsg_max") or {}
    eb = lsg.get("error_budget") or []
    test = next((e for e in eb if e.get("split") == "test"), {})
    print(f"--- {name} ({p.name}) ---")
    print(f"  wet_train: csi={wt.get('csi')} rmse={wt.get('rmse')}")
    print(f"  all_cells: csi={ac.get('csi')} rmse={ac.get('rmse')}")
    print(f"  lsg_zoning={s.get('lsg_zoning')} gp_backend={s.get('gp_backend')}")
    print(f"  n_modes keys: {[k for k in lsg.keys() if 'mode' in k.lower() or 'dim' in k.lower() or 'rank' in k.lower()]}")
    for k, v in lsg.items():
        if any(t in k.lower() for t in ["mode", "dim", "rank", "zone", "wse"]):
            print(f"  lsg_max.{k} = {v}")
    print(f"  error_budget test: O1={test.get('o1_rmse')} O2={test.get('o2_rmse')} O4={test.get('o4_rmse')}")
    print(f"  model_path={lsg.get('model_path')}")

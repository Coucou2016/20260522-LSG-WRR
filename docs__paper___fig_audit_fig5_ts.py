from __future__ import annotations

import json
from pathlib import Path

R = Path("outputs/evaluation")

print("=== lsg_ts wet_train values (Figure 5 LSG-TS bars) ===")
for key, name in [
    ("carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json", "Carlisle"),
    ("chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json", "Chowilla"),
    ("burnett/workflow_summary_grp1_wse_ext_hlsg_max.json", "Burnett"),
]:
    s = json.load(open(R / key, encoding="utf-8"))
    sp = s.get("score_protocol") or {}
    ts = sp.get("lsg_ts") or {}
    wt = ts.get("wet_train") or {}
    ac = ts.get("all_cells") or {}
    print(
        f"{name}: wet_train csi={wt.get('csi')} rmse={wt.get('rmse')} | "
        f"all_cells csi={ac.get('csi')} rmse={ac.get('rmse')}"
    )

print()
print("=== Carlisle H-LSG vs H-LSG+SGPR config difference ===")
import yaml

for cfg_path in [
    "config/carlisle_hlsg_residual_kmeans.yaml",
    "config/carlisle_hlsg_sgpr_fix.yaml",
]:
    p = Path(cfg_path)
    if not p.is_file():
        # try globbing
        cands = sorted(Path("config").glob("carlisle*hlsg*"))
        print(f"missing {cfg_path}; candidates: {[c.name for c in cands]}")
        continue
    c = yaml.safe_load(p.read_text(encoding="utf-8"))
    gp = c.get("gp") or {}
    zo = c.get("zoning") or {}
    print(
        f"{cfg_path}: zoning={c.get('zoning')} gp_keys={gp} "
    )

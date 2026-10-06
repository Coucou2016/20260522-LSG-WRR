"""Generate Global15 inducing-sweep configs (m2/m8/m28) from the matched15 template.

These fill the missing 2x2 cross in Major 1: Global15 at the same inducing
budgets already swept for H-LSG (m=2/8/16/28; m=16 is the existing matched15).
"""
from pathlib import Path

BASE = Path("config/chowilla_global_matched15.yaml").read_text(encoding="utf-8")

for m in (2, 8, 28):
    cfg = BASE.replace(
        "id: chowilla_global_matched15\n", f"id: chowilla_global_matched15_inducing_m{m}\n"
    )
    cfg = cfg.replace(
        "models: outputs/models/chowilla_global_matched15\n",
        f"models: outputs/models/chowilla_global_matched15_inducing_m{m}\n",
    )
    cfg = cfg.replace("min_inducing_points: 16\n", f"min_inducing_points: {m}\n")
    out = Path(f"config/chowilla_global_matched15_inducing_m{m}.yaml")
    out.write_text(cfg, encoding="utf-8")
    print("wrote", out)

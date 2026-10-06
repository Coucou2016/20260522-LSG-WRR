"""Generate Burnett m=56 (full-inducing) configs from the m=16 templates."""
from pathlib import Path

BASE_DIR = Path("config")

for src, dst, tag in [
    ("burnett_global.yaml", "burnett_global_inducing_m56.yaml", "global"),
    ("burnett.yaml", "burnett_inducing_m56.yaml", "hlsg"),
    ("burnett_global_matched18.yaml", "burnett_global_matched18_inducing_m56.yaml", "matched18"),
]:
    text = Path(BASE_DIR / src).read_text(encoding="utf-8")
    old_id = None
    for line in text.splitlines():
        if line.strip().startswith("id:"):
            old_id = line.split(":", 1)[1].strip()
            break
    new_id = f"{old_id}_inducing_m56"
    text = text.replace(f"id: {old_id}\n", f"id: {new_id}\n", 1)
    # models dir
    for line in text.splitlines():
        if line.strip().startswith("models:"):
            old_models = line.split(":", 1)[1].strip()
            text = text.replace(f"models: {old_models}\n", f"models: {old_models}_inducing_m56\n", 1)
            break
    text = text.replace("min_inducing_points: 16\n", "min_inducing_points: 56\n", 1)
    out = BASE_DIR / dst
    out.write_text(text, encoding="utf-8")
    print("wrote", out, "id=", new_id)

"""Create downscaled JPEG versions of manuscript figures for ChatGPT visual review."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

FIG_DIR = Path("outputs/figures")
OUT_DIR = Path("docs/paper/chatgpt_review_rounds/imgs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

NAMES = [
    "fig01_study_domains",
    "fig02_extent_hit_miss_carlisle_E1",
    "fig02_extent_hit_miss_chowilla_E1",
    "fig02_extent_hit_miss_burnett_E1",
    "fig03_peak_depth_error_carlisle_E1",
    "fig03_peak_depth_error_chowilla_E1",
    "fig03_peak_depth_error_burnett_E1",
    "fig04_pwet_carlisle_E1",
    "fig04_pwet_chowilla_E1",
    "fig04_pwet_burnett_E1",
    "fig05_cross_case_csi_rmse_wet_train",
    "fig06_error_budget_o1o4",
    "fig07_global_vs_hlsg_ab",
    "fig08_uq_calibration_crps_scale",
    "fig09_zoning_wet_correlation_ab",
]

MAX_W = 1400
for name in NAMES:
    src = FIG_DIR / f"{name}.png"
    dst = OUT_DIR / f"{name}.jpg"
    img = Image.open(src).convert("RGB")
    w, h = img.size
    if w > MAX_W:
        img = img.resize((MAX_W, int(h * MAX_W / w)), Image.LANCZOS)
    img.save(dst, "JPEG", quality=82, optimize=True)
    print(f"{dst.name}: {img.size} {dst.stat().st_size / 1024:.0f} KB")

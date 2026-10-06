"""Combine Round-A figures (1–3) into one contact sheet for ChatGPT upload."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path("docs/paper/chatgpt_review_rounds/imgs/roundA_contact_sheet.png")
FIG_DIR = Path("outputs/figures")

rows = [
    ("Figure 1 - study domains", "fig01_study_domains.png"),
    ("Figure 2a - Carlisle extent classification", "fig02_extent_hit_miss_carlisle_E1.png"),
    ("Figure 2b - Chowilla extent classification", "fig02_extent_hit_miss_chowilla_E1.png"),
    ("Figure 2c - Burnett extent classification", "fig02_extent_hit_miss_burnett_E1.png"),
    ("Figure 3a - Carlisle peak-depth error", "fig03_peak_depth_error_carlisle_E1.png"),
    ("Figure 3b - Chowilla peak-depth error", "fig03_peak_depth_error_chowilla_E1.png"),
    ("Figure 3c - Burnett peak-depth error", "fig03_peak_depth_error_burnett_E1.png"),
]

TARGET_W = 1500
BANNER_H = 46
imgs = []
for label, name in rows:
    im = Image.open(FIG_DIR / name).convert("RGB")
    w, h = im.size
    if w > TARGET_W:
        im = im.resize((TARGET_W, int(h * TARGET_W / w)), Image.LANCZOS)
    imgs.append((label, im))

total_h = sum(im.size[1] + BANNER_H + 12 for _, im in imgs) + 20
sheet = Image.new("RGB", (TARGET_W, total_h), "white")
draw = ImageDraw.Draw(sheet)
y = 10
for label, im in imgs:
    draw.rectangle([0, y, TARGET_W, y + BANNER_H], fill="#1a1a1a")
    draw.text((16, y + 12), label, fill="white")
    y += BANNER_H
    sheet.paste(im, (0, y))
    y += im.size[1] + 12

sheet.save(OUT, optimize=True)
print(f"wrote {OUT} {sheet.size} {OUT.stat().st_size/1024:.0f} KB")

"""Write per-chunk text files for localStorage staging of Round A images."""
from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path("docs/paper/chatgpt_review_rounds")
STAGE = ROOT / "_stage"
STAGE.mkdir(exist_ok=True)
IMGS = ROOT / "imgs"
CHUNK = 40_000

names = [
    "fig01_study_domains",
    "fig02_extent_hit_miss_carlisle_E1",
    "fig02_extent_hit_miss_chowilla_E1",
    "fig02_extent_hit_miss_burnett_E1",
    "fig03_peak_depth_error_carlisle_E1",
    "fig03_peak_depth_error_chowilla_E1",
    "fig03_peak_depth_error_burnett_E1",
]

manifest: dict[str, int] = {}
for name in names:
    raw = (IMGS / f"{name}.jpg").read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    n = 0
    for i in range(0, len(b64), CHUNK):
        (STAGE / f"{name}_{n:02d}.txt").write_text(b64[i : i + CHUNK], encoding="ascii")
        n += 1
    manifest[name] = n
    print(f"{name}: {len(raw)/1024:.0f} KB -> {n} chunks")

total = sum(manifest.values())
print("total chunks:", total)

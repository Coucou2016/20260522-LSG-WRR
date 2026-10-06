"""Build a localStorage injection plan for Round A images.

Outputs a JSON manifest mapping each image to its localStorage chunk keys,
chunk count, and a sha256 checksum of the full base64 string so the browser
side can verify integrity before constructing File objects.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

ROOT = Path("docs/paper/chatgpt_review_rounds")
STAGE = ROOT / "_stage"
STAGE.mkdir(exist_ok=True)
IMGS = ROOT / "imgs"
CHUNK = 40_000
PREFIX = "__imgA_"

names = [
    "fig01_study_domains",
    "fig02_extent_hit_miss_carlisle_E1",
    "fig02_extent_hit_miss_chowilla_E1",
    "fig02_extent_hit_miss_burnett_E1",
    "fig03_peak_depth_error_carlisle_E1",
    "fig03_peak_depth_error_chowilla_E1",
    "fig03_peak_depth_error_burnett_E1",
]

manifest = []
total_chunks = 0
for name in names:
    raw = (IMGS / f"{name}.jpg").read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    sha = hashlib.sha256(b64.encode("ascii")).hexdigest()
    n = 0
    for i in range(0, len(b64), CHUNK):
        key = f"{PREFIX}{name}_{n:02d}"
        (STAGE / f"{key}.txt").write_text(b64[i : i + CHUNK], encoding="ascii")
        n += 1
    manifest.append(
        {
            "name": name,
            "filename": f"{name}.jpg",
            "keys": [f"{PREFIX}{name}_{i:02d}" for i in range(n)],
            "chunks": n,
            "sha256_b64": sha,
            "bytes": len(raw),
        }
    )
    total_chunks += n
    print(f"{name}: {len(raw)/1024:.0f} KB -> {n} chunks sha={sha[:12]}")

(ROOT / "_imgA_manifest.json").write_text(json.dumps(manifest, indent=2))
print("total chunks:", total_chunks)

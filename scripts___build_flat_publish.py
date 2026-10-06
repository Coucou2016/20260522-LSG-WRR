#!/usr/bin/env python
"""Build a deliberately FLAT cross-review mirror of this project into a staging clone.

Why flat: ChatGPT (web) and other review agents fetch artifacts through the GitHub
contents API / raw URLs, which are far easier to enumerate when every file sits in the
repository root. Nested paths require recursive listing, and many simple fetchers only
read one directory level. So the mirror flattens the tree.

Naming convention (reversible):  <relative/path/with/slashes>  ->  <relative__path__with__slashes>
Root-level files keep their names. Every original path is recorded in FILE_MANIFEST.csv.

This script never modifies the working repository layout; it only writes the staging clone.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"I:\Projects\20260522-LSG-WRR")
STAGE = Path(r"I:\Projects\_publish_20260522-LSG-WRR")

# GitHub hard-rejects any single file >= 100 MB. Stay comfortably below.
MAX_BYTES = 95 * 1024 * 1024

SKIP_DIR_PARTS = {"__pycache__", ".pytest_cache", ".venv", ".git"}

# docs/paper working scratch that should not reach the review mirror
SKIP_PAPER_RE = re.compile(r"(_archive|imgs/|_stage/|roundA_contact_sheet|_roundA_chunks)")
# Raw ChatGPT conversation dumps: working scratch, not evidence of record
SKIP_RAW_CONV_RE = re.compile(r"_chatgpt_conv\d+.*_raw\.txt$")

# Local review plumbing: a CORS file server, a clipboard helper, a base64 payload blob,
# and image-staging scripts. These exist only to move screenshots into a browser session
# on the author's machine; they carry no scientific or reproduction content.
SKIP_PLUMBING_NAMES = {
    "docs/paper/chatgpt_review_rounds/_fileserver.py",
    "docs/paper/chatgpt_review_rounds/_set_clip_image.ps1",
    "docs/paper/chatgpt_review_rounds/_rA_p.b64",
    "docs/paper/chatgpt_review_rounds/_imgA_manifest.json",
    "docs/paper/chatgpt_review_rounds/roundA_fig1to3_prompt.txt",
    "docs/paper/_stage_roundA_imgs.py",
    "docs/paper/_make_roundA_sheet.py",
    "docs/paper/_plan_imgA.py",
    "docs/paper/_make_review_jpgs.py",
}

# Elsevier VoR full text / assets are copyright-restricted (see .gitignore)
SKIP_REF_RE = re.compile(r"(^1-s2\.0-|Fraehr_2024_WaterResearch_|Fraehr_2024_JEnvironManage_|_assets/)")

BINARY_SUFFIXES = {".png", ".svg", ".pdf", ".npz", ".h5", ".jpg", ".jpeg", ".zip", ".xlsx"}


def flat_name(rel: str) -> str:
    return rel.replace("/", "__")


def keep(p: Path) -> bool:
    parts = set(p.parts)
    if parts & SKIP_DIR_PARTS:
        return False
    if any(part.startswith("_archive") for part in p.parts):
        return False
    try:
        if p.stat().st_size >= MAX_BYTES:
            return False
    except OSError:
        return False
    return True


def collect() -> list[Path]:
    picked: list[Path] = []

    def add(p: Path) -> None:
        if p.is_file() and keep(p):
            picked.append(p)

    # ---- code -----------------------------------------------------------------
    for d in ("lsg", "scripts", "tests", "config"):
        for p in (ROOT / d).rglob("*"):
            add(p)

    # ---- root metadata --------------------------------------------------------
    for name in ("README.md", "requirements.txt", "pytest.ini", ".gitignore"):
        add(ROOT / name)
    for p in ROOT.glob("_patch_dual_budget_mem*.py"):
        add(p)

    # ---- docs/paper -----------------------------------------------------------
    for p in (ROOT / "docs" / "paper").rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if SKIP_PAPER_RE.search(rel) or SKIP_RAW_CONV_RE.search(rel):
            continue
        if rel in SKIP_PLUMBING_NAMES:
            continue
        add(p)

    # ---- docs/report ----------------------------------------------------------
    for p in (ROOT / "docs" / "report").rglob("*"):
        add(p)

    # ---- docs/references (public / OA only) -----------------------------------
    for p in (ROOT / "docs" / "references").rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT / "docs" / "references").as_posix()
        if SKIP_REF_RE.search(rel):
            continue
        if "token" in p.name.lower():
            continue
        add(p)

    # ---- data provenance (tiny: README / inventory / metadata) ----------------
    add(ROOT / "data" / "README.md")
    add(ROOT / "data" / "DATA_INVENTORY.md")
    for p in (ROOT / "data" / "metadata").glob("*"):
        add(p)
    for p in (ROOT / "data" / "external").glob("*/README.md"):
        add(p)

    # ---- results: evaluation summaries (source of truth for paper numbers) ----
    for p in (ROOT / "outputs" / "evaluation").rglob("*.json"):
        add(p)
    # Small prediction cubes only; Burnett's 205 MB cube exceeds the GitHub limit.
    for p in (ROOT / "outputs" / "evaluation").rglob("pred_examples.npz"):
        add(p)

    # ---- results: figures -----------------------------------------------------
    for p in (ROOT / "outputs" / "figures").iterdir():
        if not p.is_file():
            continue
        if p.name == "figure_manifest.json":
            add(p)
        elif p.suffix.lower() in {".png", ".svg", ".pdf"} and p.name.startswith("fig"):
            add(p)

    return sorted(set(picked))


def wipe_stage_tree() -> None:
    for child in STAGE.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"), "PEM private key"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub PAT"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub classic token"),
    (re.compile(r"gho_[A-Za-z0-9]{20,}"), "GitHub OAuth token"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI-like key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile("eyJ" + "0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ" + r"\."), "MinerU JWT"),
]


def secret_scan(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for p in paths:
        if p.suffix.lower() in BINARY_SUFFIXES:
            continue
        if p.suffix.lower() == ".html" and p.stat().st_size > 500_000:
            text = p.read_bytes()[:200_000].decode("utf-8", "replace")
        else:
            text = p.read_text(encoding="utf-8", errors="replace")
        for rx, label in SECRET_PATTERNS:
            m = rx.search(text)
            if m:
                hits.append(f"{p.name}: {label} @ {m.start()}")
    return hits


def rewrite_links(path: Path, mapping: dict[str, str]) -> None:
    """Point in-document relative links at the flattened names."""
    if path.suffix.lower() not in {".md", ".txt"}:
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    for rel, flat in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        if rel == flat:
            continue
        text = text.replace("(../)+" + rel, flat)
        text = re.sub(r"(?:\.\./)+" + re.escape(rel), flat, text)
        text = text.replace("`" + rel + "`", "`" + flat + "`")
    if text != original:
        path.write_text(text, encoding="utf-8")


GUIDE = """# 00 - START HERE: this repository is deliberately FLAT

**Repository:** https://github.com/{owner}/{repo}
**Mirror of working project:** `{root}`
**Built:** {built}, assembled from the working tree (base revision `{commit}`), so files also
include working-tree corrections made after that revision
**Purpose:** one-directory, machine-readable cross-review mirror of the LSG multi-fidelity
flood-surrogate study (manuscript, Chinese research report, code, configs, tests, result
summaries, figures).

---

## 1. Why there are no folders here (on purpose)

This repository intentionally places **every file in the repository root**. That is a
review-ergonomics decision, not an accident or an unfinished cleanup:

- AI reviewers (ChatGPT web, code assistants) and simple HTTP fetchers enumerate
  `https://api.github.com/repos/{owner}/{repo}/contents/` and get **one directory level**.
  With a flat root, a single call returns the *entire* artifact inventory.
- `https://raw.githubusercontent.com/{owner}/{repo}/main/<file>` addresses every artifact
  directly, with no recursive tree walking.
- Nested `docs/paper/...`, `outputs/evaluation/<case>/...` paths require recursive listing
  and per-directory calls; several tools simply stop at depth 1 and silently miss content.
- A flat tree makes it impossible for a reviewer to be "unaware" of a result file.

The cost is that filenames carry their original location. That is intentional and fully
reversible.

## 2. Naming convention (reversible)

The original POSIX path is preserved, with every `/` replaced by a **double underscore** `__`:

| Original path (working repo) | Name in this repository |
|---|---|
| `lsg/base.py` | `lsg__base.py` |
| `scripts/run_lsg_workflow.py` | `scripts__run_lsg_workflow.py` |
| `tests/test_eof.py` | `tests__test_eof.py` |
| `config/chowilla_global_matched15.yaml` | `config__chowilla_global_matched15.yaml` |
| `docs/paper/manuscript.md` | `docs__paper__manuscript.md` |
| `docs/report/report.html` | `docs__report__report.html` |
| `outputs/figures/fig03_peak_depth_error_chowilla_E1.png` | `outputs__figures__fig03_peak_depth_error_chowilla_E1.png` |
| `outputs/evaluation/chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json` | `outputs__evaluation__chowilla__workflow_summary_grp1_wse_ext_hlsg_max.json` |
| `data/metadata/splits.yaml` | `data__metadata__splits.yaml` |

Files that were already at the repository root (`README.md`, `requirements.txt`, `pytest.ini`,
`.gitignore`) keep their names unchanged.

`FILE_MANIFEST.csv` lists **every** file here with its original path and byte size, so the
mapping can be inverted exactly.

## 3. Read this in order (fast cross-review path)

1. `docs__paper__manuscript.md` - the English manuscript (main scientific claim).
2. `docs__report__report.md` - the Chinese research report (background, process, per-figure walkthrough).
3. `docs__paper__audit_trail.md` - audit trail: which number or figure came from which run/JSON.
4. `docs__paper__03_new_results.md`, `docs__paper__04_capacity_controls.md`, `docs__paper__05_carlisle_capacity.md` - result detail.
5. `README.md` - implementation-level reproduction notes (working-repo paths).
6. `docs__paper__manuscript.pdf` / `docs__report__report.pdf` - rendered, self-contained PDFs.

## 4. Where the numbers live (independent verification)

Every quantitative claim in the manuscript traces to a JSON summary in the repository root:

- `outputs__evaluation__carlisle__workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json` (Carlisle H-LSG, primary)
- `outputs__evaluation__chowilla__workflow_summary_grp1_wse_ext_hlsg_max.json` (Chowilla native H-LSG)
- `outputs__evaluation__chowilla__workflow_summary_grp1_wse_ext_global_matched15_max.json` (Chowilla matched-capacity global)
- `outputs__evaluation__burnett__workflow_summary_grp1_wse_ext_hlsg_max.json` (Burnett H-LSG)
- `outputs__evaluation__burnett__workflow_summary_grp1_wse_ext_global_matched18_max.json` (Burnett matched-capacity global)
- `outputs__evaluation__*__nested_crps_scale_cv.json` (CRPS scale cross-validation)

Each contains `lsg_max` / `lsg_ts` blocks with `csi`, `rmse`, `pod`, `rfa`, and the
`error_budget` (O1-O4) sub-block. Figures are regenerated from these summaries plus two
small prediction cubes: `outputs__evaluation__carlisle__pred_examples.npz` and
`outputs__evaluation__chowilla__pred_examples.npz`.

## 5. What is deliberately NOT in this repository

The working project directory is ~37 GB. GitHub rejects any file >= 100 MB and the platform
soft-limits repositories to ~1 GB, so the following are excluded **by size, not by secrecy**:

| Excluded | Size | Why | How to obtain / regenerate |
|---|---|---|---|
| `data/external/**` HF/LF cubes | ~30 GB | GitHub file/size limits | Public, CC BY 4.0: Fraehr (2024) https://doi.org/10.26188/24312658 |
| `outputs/models/**` trained states | ~4.4 GB | regenerable | retrain with the shipped `config__*.yaml` |
| `outputs/evaluation/burnett/pred_examples.npz` | 206 MB | exceeds 100 MB/file | regenerate or request |
| `docs/paper/_archive_*` snapshots | - | superseded working history | not needed for review |
| Elsevier VoR article PDFs / full-text extracts | - | copyright (`1-s2.0-*`, `Fraehr_2024_*`) | publisher / library |
| `.venv/`, `__pycache__/`, `.pytest_cache/` | - | build artifacts | - |
| `.secrets/`, `*token*` | - | credentials, never published | - |

Consequently the manuscript's `data/...` and `outputs/...` path references describe the
**working** layout; translate them with the table in section 2.

Because of that split, some `*.json` summaries record the absolute run path of the machine
that produced them (for example `I:\\Projects\\20260522-LSG-WRR\\...`) inside their provenance
fields. Those strings are left exactly as written: the JSON files are the primary numerical
evidence for the reported metrics, and editing them to tidy paths would make the archived
evidence differ from what the code actually emitted. Treat any absolute path as a local
machine detail, not as a reproducible location.

## 5b. How to verify a reported number yourself

1. Open the relevant `outputs__evaluation__*.json` and locate the `lsg_max` or `lsg_ts` block.
2. Read `score_protocol.<variant>.<mask>.{{csi,rmse,pod,rfa}}`; mask keys are `all` and `wet_train`.
3. Compare against the corresponding table row in `docs__paper__manuscript.md`.
4. To regenerate end to end: obtain the cubes, then run `scripts__run_lsg_workflow.py`
   with the matching `config__*.yaml`, then `scripts__make_figures.py`.

## 6. Reproduction (working layout)

Obtain the cubes from the DOI above, unzip under `data/external/<case>/`, then:

```powershell
python scripts/run_lsg_workflow.py --config config/carlisle.yaml
python scripts/make_figures.py
pytest tests -q
```

GPflow/TensorFlow are required for the reported SGPR results; the NumPy GP fallback is for
CI/synthetic smoke tests only.

## 7. Provenance and attribution

- **This implementation** is an independent Python 3.12 reimplementation of the LSG
  framework; it does not call the upstream reference code.
- **Upstream reference:** Fraehr et al. Hybrid LSG - https://github.com/nfraehr/Hybrid_LSG_model
- **Benchmark data:** Fraehr (2024), DOI 10.26188/24312658, CC BY 4.0.
- **Framing papers:** Fraehr et al. (2022, 2023) WRR; Wang et al. (2026) WRR
  (Brisbane TUFLOW/URBS data are licence-restricted and are not redistributed here).
- All accuracy metrics compare surrogate output against the corresponding HF hydrodynamic
  simulation, never against independent observations.
- The independent evaluation unit is the held-out **event**, not the raster cell.

## 8. 中文说明（同义摘要）

本仓库**故意不设任何文件夹**，全部文件平铺在根目录，目的是让 ChatGPT 等 AI 审稿工具
和简单 HTTP 抓取器一次目录调用就能拿到全部内容，便于交叉审查。原路径中的 `/` 一律替换为
双下划线 `__`（例如 `docs/paper/manuscript.md` → `docs__paper__manuscript.md`），
完整映射见 `FILE_MANIFEST.csv`。

被排除的只有**体积超限或受版权限制**的内容（约 30 GB 的 HF/LF 水动力数据立方体、
训练态模型、单文件超 100 MB 的 Burnett 预测立方体、受限的 Elsevier 正式版 PDF），
不涉及保密；数据可从 DOI 10.26188/24312658（CC BY 4.0）公开获取。
"""


def main() -> int:
    if not STAGE.is_dir():
        print(f"FATAL: staging clone missing: {STAGE}")
        return 2

    picked = collect()
    mapping: dict[str, str] = {}
    collisions: dict[str, list[str]] = {}
    oversize: list[tuple[str, float]] = []

    for p in picked:
        rel = p.relative_to(ROOT).as_posix()
        flat = flat_name(rel)
        mapping[rel] = flat
        collisions.setdefault(flat, []).append(rel)
        if p.stat().st_size >= MAX_BYTES:
            oversize.append((rel, p.stat().st_size / 1024 / 1024))

    dups = {k: v for k, v in collisions.items() if len(v) > 1}
    if dups:
        print("FATAL: flat-name collisions:")
        for k, v in dups.items():
            print(f"  {k} <- {v}")
        return 3
    if oversize:
        print("FATAL: oversize files:")
        for rel, mb in oversize:
            print(f"  {mb:.1f} MB  {rel}")
        return 4

    total = sum(p.stat().st_size for p in picked)
    print(f"selected {len(picked)} files, {total / 1024 / 1024:.2f} MB")
    if total >= 1000 * 1024 * 1024:
        print("FATAL: staging tree exceeds the 1 GB repository soft limit")
        return 5

    wipe_stage_tree()
    for p in picked:
        rel = p.relative_to(ROOT).as_posix()
        dst = STAGE / flat_name(rel)
        shutil.copy2(p, dst)

    # ---- provenance manifest --------------------------------------------------
    with (STAGE / "FILE_MANIFEST.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["flat_name", "original_path", "bytes", "area"])
        for p in picked:
            rel = p.relative_to(ROOT).as_posix()
            w.writerow([flat_name(rel), rel, p.stat().st_size, rel.split("/")[0] if "/" in rel else "(root)"])

    # ---- fix in-document links to the flat names ------------------------------
    for name in ("README.md",):
        rewrite_links(STAGE / name, mapping)
    for p in STAGE.glob("docs__*.md"):
        rewrite_links(p, mapping)

    # ---- guide document -------------------------------------------------------
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        commit = "unknown"
    import datetime

    guide = GUIDE.format(
        owner="Coucou2016",
        repo="20260522-LSG-WRR",
        root=str(ROOT),
        built=datetime.date.today().isoformat(),
        commit=commit,
    )
    (STAGE / "00_START_HERE_FLAT_LAYOUT.md").write_text(guide, encoding="utf-8")

    # ---- flat .gitignore ------------------------------------------------------
    (STAGE / ".gitignore").write_text(
        ".venv/\n__pycache__/\n*.pyc\n.pytest_cache/\n.DS_Store\n"
        "# Secrets - never commit\n.secrets/\n**/*token*\n",
        encoding="utf-8",
    )

    # ---- line-ending policy ---------------------------------------------------
    # The staging tree is assembled by byte copy from a Windows working copy, so files
    # arrive with mixed CRLF/LF. Normalise to LF in the repository so that diffs reflect
    # content changes only, and so every file reads identically regardless of platform.
    (STAGE / ".gitattributes").write_text(
        "# Normalise line endings for reviewability: store LF in the repository.\n"
        "* text=auto eol=lf\n"
        "# Keep screenshots and other binaries untouched.\n"
        "*.png binary\n*.jpg binary\n*.pdf binary\n*.npz binary\n*.svg text eol=lf\n",
        encoding="utf-8",
    )

    # ---- secret scan ----------------------------------------------------------
    hits = secret_scan([p for p in STAGE.iterdir() if p.is_file()])
    print("SECRET_SCAN_PASS" if not hits else "SECRET_SCAN_FAIL")
    for h in hits:
        print("  -", h)

    counts: dict[str, int] = {}
    for p in picked:
        rel = p.relative_to(ROOT).as_posix()
        area = rel.split("/")[0] if "/" in rel else "(root)"
        counts[area] = counts.get(area, 0) + 1
    print("by area:", json.dumps(counts, sort_keys=True))
    print(f"staged into {STAGE}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())

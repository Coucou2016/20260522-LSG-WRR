# 00 - START HERE: this repository is deliberately FLAT

**Repository:** https://github.com/Coucou2016/20260522-LSG-WRR
**Mirror of working project:** `I:\Projects\20260522-LSG-WRR`
**Built:** 2026-10-06, assembled from the working tree (base revision `970318b735444cb4f1b1ea4b691daae9405d6f91`), so files also
include working-tree corrections made after that revision
**Purpose:** one-directory, machine-readable cross-review mirror of the LSG multi-fidelity
flood-surrogate study (manuscript, Chinese research report, code, configs, tests, result
summaries, figures).

---

## 1. Why there are no folders here (on purpose)

This repository intentionally places **every file in the repository root**. That is a
review-ergonomics decision, not an accident or an unfinished cleanup:

- AI reviewers (ChatGPT web, code assistants) and simple HTTP fetchers enumerate
  `https://api.github.com/repos/Coucou2016/20260522-LSG-WRR/contents/` and get **one directory level**.
  With a flat root, a single call returns the *entire* artifact inventory.
- `https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/<file>` addresses every artifact
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
that produced them (for example `I:\Projects\20260522-LSG-WRR\...`) inside their provenance
fields. Those strings are left exactly as written: the JSON files are the primary numerical
evidence for the reported metrics, and editing them to tidy paths would make the archived
evidence differ from what the code actually emitted. Treat any absolute path as a local
machine detail, not as a reproducible location.

## 5b. Some in-document links point to files that are not here (by design)

A few cross-references in `docs__references__README.md` and the data READMEs name artifacts
that section 5 excludes — for example the Elsevier VoR full-text Markdown files
(`Fraehr_2024_WaterResearch_*`, `Fraehr_2024_JEnvironManage_*`) and local verification
scripts that operate on the working tree. Those links will 404 here. That is expected: it
marks exactly which inputs are local-only or copyrighted rather than missing by accident.
Relative filenames mentioned inside `data__external__*/README.md` are relative to their
original folder in the working layout, not to this root.

## 5c. How to verify a reported number yourself

1. Open the relevant `outputs__evaluation__*.json` and locate the `lsg_max` or `lsg_ts` block.
2. Read `score_protocol.<variant>.<mask>.{csi,rmse,pod,rfa}`; mask keys are `all` and `wet_train`.
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

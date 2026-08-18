# Figure ↔ Code Correspondence Audit Pack (WRR manuscript)

**Repo:** https://github.com/Coucou2016/20260522-LSG-WRR
**Manuscript:** https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/docs/paper/manuscript.md
**Generating code:** `scripts/make_figures.py` (all figures)
**Captions:** `docs/paper/_build_html.py` (`FIGURES` list)

This pack pairs every manuscript figure with (a) the figure image, (b) the exact
generating code, and (c) the underlying data values, so you can do a **visual
review** and a **code review** simultaneously.

Please check each figure for:

1. **Internal consistency** — does the figure match the caption and the numbers
   quoted in the manuscript text?
2. **Visual quality** — axis labels, legends, font sizes, color maps, panel
   layout, overlapping text, misleading axes, truncated labels, invisible bars.
3. **Correctness of the code** — does the code actually plot what the caption
   claims? Any indexing, unit, or sign errors?
4. **Statistical presentation** — shared vs independent color scales, log vs
   linear axes, whether one panel's outliers suppress another panel's structure.

Figures are embedded below as raw GitHub image URLs (renderable inline). The
spatial maps (Figs 1–4) are plotted as cell-center scatter because a DEM raster
is not available in the public geometry package.

---

## Figure 1 — Study domains

**Caption:** High-fidelity (HF) computational domains for Carlisle, Chowilla, and
Burnett, plotted from HF cell-center coordinates on equal-aspect easting and
northing axes. Cell counts *n* are given in the panel titles, and points are
subsampled for display on the largest meshes.

![Figure 1](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig01_study_domains.png)

**Generating code** (`fig_study_domains`):

```python
def fig_study_domains(out_dir, skips):
    specs = [("Carlisle", pred_carlisle, geom_carlisle),
             ("Chowilla", pred_chowilla, geom_chowilla),
             ("Burnett", pred_burnett, geom_burnett)]
    ...
    for ax, b, tag in zip(axes, bundles, [...]):
        xy = b["xy"]
        step = max(1, b["n"] // 80_000)   # subsample for readability
        ax.scatter(xy[::step, 0], xy[::step, 1], s=0.15, c=PALETTE["lsg_max"],
                   marker="s", linewidths=0, rasterized=True, alpha=0.7)
        ax.set_title(f"{b['case']} · n={b['n']:,}")
```

**Data:** cell counts — Carlisle / Chowilla / Burnett (n printed in panel titles).

---

## Figure 2 — Inundation-extent hit/miss/false-alarm maps

**Caption:** Event E1 inundation-extent classification at τ = 0.03 m, comparing
(a) the LF simulation with the HF reference and (b) the LSG-Max H-LSG prediction
with HF. Blue = hits, red = misses, gold = false alarms, grey = dry in both.

![Figure 2a (Carlisle)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig02_extent_hit_miss_carlisle_E1.png)

![Figure 2b (Chowilla)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig02_extent_hit_miss_chowilla_E1.png)

![Figure 2c (Burnett)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig02_extent_hit_miss_burnett_E1.png)

**Generating code** (`fig_extent_hit_miss` + `_extent_category`):

```python
def _extent_category(hf, pred, tau):
    hf_w = hf >= tau; pr_w = pred >= tau
    cat = np.zeros(hf.shape, dtype=np.int8)
    cat[hf_w & pr_w] = 1    # hit
    cat[hf_w & ~pr_w] = 2   # miss
    cat[~hf_w & pr_w] = 3   # false alarm
    return cat              # 0 = dry

# panels: (a) LF vs HF, (b) LSG-Max vs HF; tau = 0.03 m
```

**Note for review:** Chowilla is the Group 1 held-out event E1. The manuscript
(Section 4.5, "Sensitivity to the Scoring Domain") reports that E1's inundation
extent (84,667 wet cells) substantially exceeds the 36,124-cell training wet
domain. Check whether panel (b) of Figure 2b visually reflects this and whether
the caption communicates it.

---

## Figure 3 — Peak-depth error maps

**Caption:** Event E1 peak-depth errors (m) for (a) LF − HF and (b) LSG-Max − HF;
each panel uses an **independent** color scale spanning its own
99th-percentile absolute error. Positive = overprediction, negative =
underprediction.

![Figure 3a (Carlisle)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig03_peak_depth_error_carlisle_E1.png)

![Figure 3b (Chowilla)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig03_peak_depth_error_chowilla_E1.png)

![Figure 3c (Burnett)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig03_peak_depth_error_burnett_E1.png)

**Generating code** (`fig_peak_depth_error`):

```python
for ax, title, err, tag in ((axes[0], "LF − HF", err_lf, "(a)"),
                            (axes[1], "LSG-Max − HF", err_lsg, "(b)")):
    fin = np.abs(err[np.isfinite(err)])
    lim = float(np.nanpercentile(fin, 99)) or 1.0   # per-panel color scale
    sc = _scatter_field(ax, b["xy"], err, cmap=PALETTE["error"], vmin=-lim, vmax=lim, s=s)
    cbar.set_label("depth error (m)")
```

---

## Figure 4 — P(wet) probabilistic maps

**Caption:** Event E1 LSG-Max H-LSG inundation probability *P*(*h* ≥ 0.03 m),
reconstructed from the probabilistic WSE pathway conditional on the EXT gate.

![Figure 4a (Carlisle)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig04_pwet_carlisle_E1.png)

![Figure 4b (Chowilla)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig04_pwet_chowilla_E1.png)

![Figure 4c (Burnett)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig04_pwet_burnett_E1.png)

**Generating code** (`fig_pwet_maps`):

```python
sc = _scatter_field(ax, b["xy"], b["pwet"], cmap=PALETTE["inundation"],
                    vmin=0.0, vmax=1.0, s=s)
cbar.set_label(f"P(h ≥ {DEPTH_TAU_M:g} m)")   # single panel, no (a) label
```

---

## Figure 5 — Cross-case CSI / RMSE (wet-domain)

**Caption:** CSI and depth RMSE (m) on the Group 1 training wet-domain scoring
mask for LF-only, LSG-Max H-LSG, and (Carlisle only) LSG-TS across the three cases.

![Figure 5](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig05_cross_case_csi_rmse_wet_train.png)

**Generating code** (`fig_cross_case`):

```python
variants = ("lf_only", "lsg_max", "lsg_ts")
# LSG-TS is only evaluated for Carlisle; Chowilla/Burnett use max-only time
# reduction, so LSG-TS duplicates LSG-Max and is skipped.
for ax, metric, ylab, ylim in ((axes[0], csi, "CSI (−)", (0.7, 1.02)),
                               (axes[1], rmse, "RMSE (m)", None)):
    ...
```

**Data** (`wet_train` protocol):

| Case | LF-only CSI / RMSE | LSG-Max CSI / RMSE | LSG-TS CSI / RMSE |
|---|---|---|---|
| Carlisle | 0.9660 / 0.1010 | 0.9757 / 0.0945 | 0.9702 / 0.1543 |
| Chowilla | 0.9247 / 0.6902 | 0.9756 / 0.0932 | — (duplicates LSG-Max) |
| Burnett | 0.8533 / 0.9895 | 0.9752 / 0.3868 | — (duplicates LSG-Max) |

---

## Figure 6 — O1–O4 oracle error budget

**Caption:** O1–O4 depth RMSE (m) for the Group 1 train and test splits, scored on
the training wet domain. Panels: (a) Carlisle LSG-Max, (b) Carlisle LSG-TS,
(c) Chowilla LSG-Max, (d) Burnett LSG-Max.

![Figure 6](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig06_error_budget_o1o4.png)

**Generating code** (`fig_error_budget`):

```python
oracle_keys = ["o1_rmse", "o2_rmse", "o3_rmse", "o4_rmse"]
for ax, (case, variant, rows), tag in zip(...):
    ...
    maxv = max(float(by_split[s][ok]) for s in splits for ok in oracle_keys)
    ax.set_ylim(0, maxv * 1.12)   # independent per-panel y limit
    ax.set_title(f"{case} · {variant}")
```

**Data** (test split):

| Case / variant | O1 | O2 | O3 | O4 |
|---|---|---|---|---|
| Carlisle LSG-Max | 0.048 | 0.052 | 0.068 | 0.094 |
| Carlisle LSG-TS | 0.018 | 0.033 | 0.240 | 0.102 |
| Chowilla LSG-Max | 0.021 | 0.034 | 0.701 | 0.093 |
| Burnett LSG-Max | 0.074 | 0.083 | 0.668 | 0.387 |

---

## Figure 7 — Global vs H-LSG A/B

**Caption:** Native-capacity wet-domain CSI and depth RMSE (m) comparing the
native global model with residual H-LSG for the three cases; the Carlisle H-LSG
bar is the SGPR-enabled run (0.094 m).

![Figure 7](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig07_global_vs_hlsg_ab.png)

**Generating code** (`fig_global_vs_hlsg`):

```python
for ax, metric_idx, ylab, ylim in ((axes[0], 2, "CSI (−)", (0.9, 1.01)),
                                   (axes[1], 3, "RMSE (m)", None)):
    labels_order = ["Global", "H-LSG"]
    ...
```

**Data** (`wet_train`, LSG-Max):

| Case | Global CSI / RMSE | H-LSG CSI / RMSE |
|---|---|---|
| Carlisle | 0.9757 / 0.1122 | 0.9757 / 0.0945 |
| Chowilla | 0.9744 / 0.0877 | 0.9756 / 0.0932 |
| Burnett | 0.9751 / 0.1788 | 0.9752 / 0.3868 |

---

## Figure 8 — UQ calibration

**Caption:** CRPS-based variance calibration and spatial diagnostics. (a)
Carlisle reliability diagram before/after. (b) spatial distribution of the
0.5 ≤ P < 0.95 fringe vs the HF wet–dry pattern. (c) all-cell and active-cell 90%
coverage before/after. (d) CRPS (m) before/after for all three cases on a
logarithmic axis.

![Figure 8](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig08_uq_calibration_crps_scale.png)

**Generating code** (`fig_uq_calibration`):

```python
# (a) reliability: pred vs obs frequency, 1:1 ideal line
# (b) fringe map: fringe = (p >= 0.5) & (p < 0.95)
# (c) coverage: before/after bars for coverage_90 and coverage_90_active
# (d) CRPS: log scale, bottom = 1e-2
ax.set_yscale("log")
ax.set_ylim(1e-2, 5.0)
ax.set_ylabel("CRPS (m, log scale)")
```

**Data**:

| Case | CRPS before | CRPS after | cov90 | cov90 (active) |
|---|---|---|---|---|
| Carlisle | 0.0389 | 0.0285 | 0.987 | 0.966 |
| Chowilla | 2.1547 | 2.1550 | 0.446 | 0.287 |
| Burnett | 0.1332 | 0.1270 | 0.939 | 0.890 |

---

## Figure 9 — Chowilla zoning-method sensitivity

**Caption:** Chowilla Group 1 maximum-surface zoning sensitivity comparing the
global model, residual-response *k*-means zoning, and wet-correlation zoning:
(a) wet-domain CSI and (b) wet-domain depth RMSE (m).

![Figure 9](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig09_zoning_wet_correlation_ab.png)

**Generating code** (`fig_zoning_sensitivity`):

```python
rows = [("Residual k-means", chowilla_hlsg, PALETTE["hlsg"]),
        ("Wet-correlation", chowilla_wet_corr, PALETTE["sgpr"]),
        ("Global (none)", chowilla_global, PALETTE["global"])]
for xi, c, v in zip(x, colors, csi_vals):
    axes[0].bar(xi, v, width=0.55, color=c)
axes[0].set_ylim(0.9, 1.01)
```

**Data** (`wet_train`, LSG-Max):

| Zoning method | CSI | RMSE (m) |
|---|---|---|
| Residual k-means (H-LSG) | 0.9756 | 0.0932 |
| Wet-correlation | 0.9778 | 0.0944 |
| Global (none) | 0.9744 | 0.0877 |

---

## Review request

Please do a **dual-line review** (visual + code) of these 15 figure panels and
report, for each finding:

1. **Which figure/panel** is affected.
2. **The problem** — visual, numerical, caption-code mismatch, or logic.
3. **Severity** — P0 (wrong/misleading result), P1 (visual imbalance hiding
   structure), P2/P3 (cosmetic/consistency).
4. **Suggested fix** — prefer small edits (caption clarification, independent
   color scale, log axis, y-limit) rather than restructuring.

Cross-check each figure's plotted numbers against the data tables above and the
manuscript text (Tables 2–9 and Sections 4.1–4.5). Pay special attention to:
(a) whether the Chowilla spatial panels (2b/3b/4b) are self-consistent with the
training-wet-domain caveat in Section 4.5, and (b) whether any bar chart uses a
shared axis that suppresses smaller bars (Figs 5, 6, 7, 8d).

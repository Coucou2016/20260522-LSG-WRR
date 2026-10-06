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
spatial maps (Figs 1–3) are plotted as cell-center scatter because a DEM raster
is not available in the public geometry package.

---

## Figure 1 — Inundation-extent hit/miss/false-alarm maps

**Caption:** Event E1 inundation-extent classification at τ = 0.03 m, comparing
(a) the LF simulation with the HF reference and (b) the LSG-Max H-LSG prediction
with HF. Blue = hits, red = misses, gold = false alarms, grey = dry in both.

![Figure 1a (Carlisle)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig02_extent_hit_miss_carlisle_E1.png)

![Figure 1b (Chowilla)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig02_extent_hit_miss_chowilla_E1.png)

![Figure 1c (Burnett)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig02_extent_hit_miss_burnett_E1.png)

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
domain. Check whether panel (b) of Figure 1b visually reflects this and whether
the caption communicates it.

---

## Figure 2 — Peak-depth error maps

**Caption:** Event E1 peak-depth errors (m) for (a) LF − HF and (b) LSG-Max − HF;
each panel uses an **independent** color scale spanning its own
99th-percentile absolute error. Positive = overprediction, negative =
underprediction.

![Figure 2a (Carlisle)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig03_peak_depth_error_carlisle_E1.png)

![Figure 2b (Chowilla)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig03_peak_depth_error_chowilla_E1.png)

![Figure 2c (Burnett)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig03_peak_depth_error_burnett_E1.png)

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

## Figure 3 — P(wet) probabilistic maps

**Caption:** Event E1 LSG-Max H-LSG inundation probability *P*(*h* ≥ 0.03 m),
reconstructed from the probabilistic WSE pathway conditional on the EXT gate.

![Figure 3a (Carlisle)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig04_pwet_carlisle_E1.png)

![Figure 3b (Chowilla)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig04_pwet_chowilla_E1.png)

![Figure 3c (Burnett)](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig04_pwet_burnett_E1.png)

**Generating code** (`fig_pwet_maps`):

```python
sc = _scatter_field(ax, b["xy"], b["pwet"], cmap=PALETTE["inundation"],
                    vmin=0.0, vmax=1.0, s=s)
cbar.set_label(f"P(h ≥ {DEPTH_TAU_M:g} m)")   # single panel, no (a) label
ax.set_title(f"{case} · {b['eid']} · LSG-Max P(wet)", fontsize=9)   # shortened title
```

---

## Figure 4 — Cross-case CSI / RMSE (wet-domain)

**Caption:** CSI and depth RMSE (m) on the Group 1 training wet-domain scoring
mask for LF-only, LSG-Max H-LSG, and (Carlisle only) LSG-TS across the three cases.

![Figure 4](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig05_cross_case_csi_rmse_wet_train.png)

**Generating code** (`fig_cross_case`):

```python
variants = ("lf_only", "lsg_max", "lsg_ts")
colors = {"lf_only": PALETTE["lf"], "lsg_max": PALETTE["hlsg"],
          "lsg_ts": PALETTE["lsg_ts"]}
# LSG-TS is only evaluated for Carlisle; Chowilla/Burnett use max-only time
# reduction, so LSG-TS duplicates LSG-Max and is skipped.
for ax, metric, ylab, ylim in ((axes[0], csi, "CSI (−)", (0, 1.02)),
                               (axes[1], rmse, "RMSE (m)", None)):
    ...
    for xi, val in zip(x + (i - 1) * width, vals):
        if not np.isfinite(val):
            ax.text(xi, 0.01, "N/A", ha="center", va="bottom", fontsize=7)
        else:
            ax.text(xi, val + 0.015, f"{val:.3f}", ha="center", va="bottom", fontsize=7)
    # CSI axis spans 0–1 (no truncated baseline); numeric labels added on bars
    # LSG-Max H-LSG uses the shared H-LSG blue for cross-figure consistency
```

**Data** (`wet_train` protocol):

| Case | LF-only CSI / RMSE | LSG-Max CSI / RMSE | LSG-TS CSI / RMSE |
|---|---|---|---|
| Carlisle | 0.9660 / 0.1010 | 0.9757 / 0.0945 | 0.9702 / 0.1543 |
| Chowilla | 0.9247 / 0.6902 | 0.9756 / 0.0932 | — (duplicates LSG-Max) |
| Burnett | 0.8533 / 0.9895 | 0.9752 / 0.3868 | — (duplicates LSG-Max) |

---

## Figure 5 — O1–O4 oracle error budget

**Caption:** O1–O4 depth RMSE (m) for the Group 1 train and test splits, scored on
the training wet domain. Panels: (a) Carlisle LSG-Max, (b) Carlisle LSG-TS,
(c) Chowilla LSG-Max, (d) Burnett LSG-Max. Each panel uses an independent y-axis
limit so that the small O1/O2 bars remain visible alongside the larger O3 values;
bars should not be compared across panels by height.

![Figure 5](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig06_error_budget_o1o4.png)

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
| Chowilla LSG-Max | 0.020 | 0.034 | 0.701 | 0.093 |
| Burnett LSG-Max | 0.074 | 0.083 | 0.668 | 0.387 |

---

## Figure 6 — Global vs H-LSG (depth RMSE)

**Caption:** Native-capacity wet-domain depth RMSE (m) comparing the native
global model with residual H-LSG for the three cases; the Carlisle H-LSG bar is
the SGPR-enabled run (0.094 m). Wet-domain CSI is essentially unchanged across
the two models (0.974–0.976, shared global extent gate) and is reported in the
text (Section 4.3) rather than plotted.

![Figure 6](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig07_global_vs_hlsg_ab.png)

**Generating code** (`fig_global_vs_hlsg`):

```python
# Single RMSE panel (the CSI panel was removed: it is flat because the
# extent gate is shared and global, so only RMSE carries the contrast).
fig, ax = plt.subplots(1, 1, figsize=figsize_double(2.4))
labels_order = ["Global", "H-LSG"]
width = 0.32
for i, lab in enumerate(labels_order):
    # records are (case, label, csi, rmse); index 3 = depth RMSE
    vals = [r[3] for r in records if r[1] == lab]
    _bar_values(ax, x + (i - 0.5) * width, vals, width=width,
                color=color_map[lab], label=lab)
    for xi, val in zip(x + (i - 0.5) * width, vals):
        ax.text(xi, val + 0.008, f"{val:.3f}", ha="center", va="bottom", fontsize=7)
ax.set_ylabel("Depth RMSE (m)")
ax.set_xlabel("Case")
```

**Data** (`wet_train`, LSG-Max):

| Case | Global RMSE | H-LSG RMSE |
|---|---|---|
| Carlisle | 0.1122 | 0.0945 |
| Chowilla | 0.0877 | 0.0932 |
| Burnett | 0.1788 | 0.3868 |

---

## Figure 7 — Chowilla zoning-method sensitivity

**Caption:** Chowilla Group 1 maximum-surface zoning sensitivity comparing the
global model, residual-response *k*-means zoning, and wet-correlation zoning.
Bars show wet-domain CSI (left axis) and depth RMSE (right axis, m).

![Figure 7](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig09_zoning_wet_correlation_ab.png)

**Generating code** (`fig_zoning_sensitivity`):

```python
# Single grouped panel with twin y-axes (CSI left, RMSE right).
fig, ax = plt.subplots(1, 1, figsize=figsize_double(2.4))
width = 0.32
bars_csi = ax.bar(x - width / 2, csi_vals, width=width,
                  color=PALETTE["hlsg"], label="CSI")
ax.set_ylabel("CSI (−)")        # left axis, 0–1.01
ax.set_ylim(0, 1.01)
ax2 = ax.twinx()
bars_rmse = ax2.bar(x + width / 2, rmse_vals, width=width,
                    color=PALETTE["sgpr"], label="RMSE")
ax2.set_ylabel("Depth RMSE (m)")  # right axis, 0–0.12
ax2.set_ylim(0, 0.12)
```

**Data** (`wet_train`, LSG-Max):

| Zoning method | CSI | RMSE (m) |
|---|---|---|
| Residual k-means (H-LSG) | 0.9756 | 0.0932 |
| Wet-correlation | 0.9778 | 0.0944 |
| Global | 0.9744 | 0.0877 |

---

## Figure 8 — UQ calibration

**Caption:** CRPS-based variance calibration and spatial diagnostics. (a)
Carlisle reliability diagram before/after. (b) spatial distribution of the
0.5 ≤ P < 0.95 fringe vs the HF wet–dry pattern. (c) Carlisle all-cell and
active-cell 90% coverage before/after. (d) CRPS (m) before/after for all three
cases on a logarithmic axis.

![Figure 8](https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/outputs/figures/fig08_uq_calibration_crps_scale.png)

**Generating code** (`fig_uq_calibration`):

```python
# (a) reliability: pred vs obs frequency, 1:1 ideal line
# (b) fringe map: fringe = (p >= 0.5) & (p < 0.95)
# (c) coverage: before/after bars for coverage_90 and coverage_90_active
ax.set_title("Carlisle LSG-Max coverage")   # panel (c) now names Carlisle
ax.set_ylim(0, 1.02)                        # full 0–1 scale (no truncated baseline)
ax.axhline(0.9, color="0.4", ls=":", lw=0.8)  # nominal 90% coverage line
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

## Review request

Please do a **dual-line review** (visual + code) of these 14 figure panels and
report, for each finding:

1. **Which figure/panel** is affected.
2. **The problem** — visual, numerical, caption-code mismatch, or logic.
3. **Severity** — P0 (wrong/misleading result), P1 (visual imbalance hiding
   structure), P2/P3 (cosmetic/consistency).
4. **Suggested fix** — prefer small edits (caption clarification, independent
   color scale, log axis, y-limit) rather than restructuring.

Cross-check each figure's plotted numbers against the data tables above and the
manuscript text (Tables 2–9 and Sections 4.1–4.5). Pay special attention to:
(a) whether the Chowilla spatial panels (1b/2b/3b) are self-consistent with the
training-wet-domain caveat in Section 4.5, and (b) whether any bar chart uses a
shared axis that suppresses smaller bars (Figs 4, 5, 6, 8d).

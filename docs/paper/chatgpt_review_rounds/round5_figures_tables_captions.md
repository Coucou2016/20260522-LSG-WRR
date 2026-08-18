# Round 5 — Figures, tables, and captions formatting

- **Date:** 2026-08-18 ~03:10–03:45 (UTC+8)
- **Backup before edits:** `docs/paper/_archive_manuscript_pre_round5_20260818_031347.md`
- **ChatGPT chat:** "Manuscript Review Feedback" (https://chatgpt.com/c/6a8347ff-93b8-83ea-a14e-ac1894e0f5cf)
- **Scope:** All figure captions (`_build_html.py` FIGURES list), all table captions (manuscript.md), cross-references, in-figure labels, number formatting.
- **Prior rounds already fixed (do not re-flag):** innovation framing; EXT threshold 0.5, EXT-gating of uncertainty, O1–O4 common EXT gate, SGPR inducing rule, variance propagation formula, metric definitions, fringe stats (63%/35%/1.5%, 8,936/581,061, 70% FA in 0.6–0.9 bins); hedging for Burnett localization, Chowilla null result, LF-to-LSG gains, Section 5.3 causal wording; WRR/AGU house style, en-dash/minus typography, "primary" terminology, Table 1 notation.

## ChatGPT findings (30 items: 13 must-fix, 12 should-fix, 5 polish)

### Accepted and applied

**Figure captions (`docs/paper/_build_html.py`):**
1. Figure 1: removed build-script shorthand ("cell-centre scatters (DEM raster unavailable)"); now describes domains, equal-aspect axes, and DEM unavailability in prose; notes cell counts in panel titles (verified present: n=581,061 / 109,914 / 780,785).
2. Figures 2a–2c: removed nested "(a) LF vs HF, (b) LSG-Max vs HF" ambiguity by keeping panel letters but spelling out full comparison per case; removed interpretation from 2b ("Supports...") and 2c ("Clearest visual..."); unified three captions to identical structure; replaced H/M/FA shorthand with hits/misses/false alarms/grey dry-in-both (verified legend has "Both dry" patch).
3. Figures 3a–3c: replaced "LF−HF and LSG-Max−HF (red +, blue −)" shorthand; stated signed error interpretation; added "(m)" units; unified all three captions (removed interpretation from 3c).
4. Figures 4a–4c: unified parallel structure; replaced "after deterministic maps" with "reconstructed from the probabilistic WSE pathway conditional on the EXT gate"; stated model (LSG-Max H-LSG) and event in each.
5. Figure 5: removed `wet_train`/`Grp1` code identifiers; stated maximum-surface context, all three variants (LF-only, LSG-Max H-LSG, and LSG-TS — verified present in fig05), RMSE unit.
6. Figure 6: named cases/variants/splits/scoring domain/RMSE unit. **Adapted, not verbatim:** figure has four panels (Carlisle LSG-Max, Carlisle LSG-TS, Chowilla H-LSG, Burnett H-LSG) — verified in `fig_error_budget` sources list and rendered SVG; ChatGPT's suggestion naming Chowilla/Burnett "global LSG" panels does not match the figure, so panels were listed as actually plotted.
7. Figure 7: replaced "Max Grp1 (native capacity)" shorthand; stated CSI and RMSE panels. **Adapted:** ChatGPT proposed also "O2 − O1 truncation contrast (m)" but verified fig07 plots only CSI and RMSE (2 panels) — omitted non-plotted metric per its own escape clause. Also corrected scope: figure includes Carlisle (Global, H-LSG, H-LSG+SGPR), not just Chowilla/Burnett.
8. Figure 8: neutralized panel (b) ("dominated by false-alarm boundary cells" removed from caption; that interpretation stays in Sections 4.6/5.3); specified Carlisle coverage scope for panel (c) (verified: coverage panel uses only Carlisle raw/cal pair) and Carlisle/Chowilla/Burnett for panel (d) (verified x-axis names); removed "90 pct" style text.
9. Figure 9: removed `residual_kmeans`/`wet_correlation`/`Max Grp1` code identifiers; stated wet-domain CSI and RMSE panels. **Adapted:** O2 − O1 not plotted (verified 2 panels), so only plotted metrics listed per its escape clause.

**Table captions (manuscript.md):**
10. Table 1: expanded to describe solver pairs, domain sizes, temporal products, and Group 1 splits.
11. Table 2: stated both scoring domains and RMSE unit; renamed column headers from `CSI all_cells`/`CSI wet_train`/`RMSE all`/`RMSE wet_train` to "CSI (full mesh)"/"CSI (training wet domain)"/"RMSE full mesh (m)"/"RMSE wet domain (m)".
12. Table 3: replaced "Test-split"/"protocol wet index" with "Group 1 test evaluations on the training wet-domain scoring mask".
13. Table 4: added scoring domain and meter units for RMSE and O2 − O1.
14. Table 5: added scoring domain and units (meters; EXT agreement dimensionless); retained the EXT-agreement explanatory paragraph verbatim.
15. Table 6: added scoring domain and units.
16. Table 7: added Group 1 maximum-surface setting, scoring domain, and units.
17. Table 8: added scoring domain and units; renamed `CSI wet_train`/`RMSE wet_train` headers to CSI/RMSE (m).
18. Table 9: stated CRPS in meters, coverage as fraction, active-cell scoring domain, unchanged point scores; kept provenance sentence (rescored saved states; workflow-fit scales 0.309/0.606) after clearer lead; header "CRPS (m; uncalibrated → calibrated)" aligned with coverage header style.

**Cells/formatting:**
19. Table 9 Carlisle TS CRPS cell: "≈0.0165 (near calibrated)" → "≈0.017" (removed mixed interpretation; no separate before/after available, so single approximate value kept).
20. "wet_train" in Table 9 point-score column cells → "wet domain"; "all cells" → "full mesh" for consistency with Table 2 headers.

**Cross-reference:**
21. Figure 9 citation added at its natural location in Section 4.4 wet-correlation paragraph (the only uncited figure; verified Figures 1–8 and Tables 1–9 were already cited).

**In-figure labels (`scripts/make_figures.py`) — code-style identifiers also cleaned inside the rendered SVGs/PDFs/PNGs, figures regenerated:**
22. `MASK_LABEL` "Fraehr wet_train (Categories wet_idx)" → "training wet domain" (used in fig05, fig07, fig09 suptitles).
23. fig01 suptitle: "Study domains (HF cell centres; DEM raster unavailable — cell-scatter)" → "Study domains (HF cell centers; DEM raster unavailable)" (also centre→center spelling alignment with manuscript body).
24. fig02 suptitle: "extent H/M/FA (τ=0.03 m)" → "inundation-extent classification (τ=0.03 m)".
25. fig03 suptitle: "peak-depth error (red +, blue −)" → "peak-depth error relative to HF".
26. fig04 title: "LSG-Max P(wet)" → "LSG-Max inundation probability".
27. fig06 suptitle: "O1–O4 error budget (clipped-depth RMSE on wet_idx)" → "O1–O4 oracle depth RMSE on the training wet domain".
28. fig07 suptitle: "Global vs H-LSG (residual_kmeans) LSG-Max" → "Global vs residual H-LSG (LSG-Max)".
29. fig08 reliability legend: "After crps_scale" → "After calibration".
30. fig09 bar labels: "residual_kmeans"/"wet_correlation"/"global (none)" → "Residual k-means"/"Wet-correlation"/"Global (none)".

### Rejected (with reasons)

- Figure 5 caption suggestion "for LF-only and LSG-Max H-LSG maximum-surface predictions": rejected the variant list because the rendered fig05 also includes an LSG-TS bar for Carlisle (verified in `fig_cross_case` and SVG). Caption instead lists all three variants with "(Carlisle only)" qualifier for LSG-TS.
- Figure 6 caption naming Chowilla/Burnett panels as "global LSG": rejected — no global panels exist in the figure (verified in `fig_error_budget` sources list). Caption lists the four actual panels.
- Figure 7/9 captions mentioning "O2 − O1 truncation contrast (m)": rejected — not plotted (verified 2-panel figures). ChatGPT's own escape clause ("If Figure … does not display all three quantities, remove the quantities not actually plotted") was applied.
- Figure 8(c)/(d) proposal "evaluated cases" expanded to "Carlisle Max, Chowilla Max, and Burnett Max": partially accepted — verified coverage panel (c) plots only the Carlisle raw/cal pair, so caption states Carlisle for (c); CRPS panel (d) verified to include Carlisle, Chowilla, Burnett.
- Panel-letter convention change (Finding: use one convention "Figure 8a" throughout): already consistent in the manuscript (only "Figure 8a"/"Figure 8b" used); no action needed.
- Figure 1 "equal-aspect easting and northing axes" phrasing kept in caption since verified in code (`ax.set_aspect("equal")`).

## Verification performed

- All figure panel contents verified against `scripts/make_figures.py` source and the rendered SVG text (regex-extracted labels) before adopting any caption wording.
- `_build_html.py` pre-existing Python-3.9-incompatible f-string (`src=\"data:` backslash) fixed; build re-run: 14 img tags / 14 data URIs (9 numbered figures with fig2a-c, fig3a-c, fig4a-c subpanels = 14 images).
- Figures regenerated with Agg backend (45 files); matplotlib version 3.9.2 in this shell.

## Post-round state

- `manuscript.md`: all 9 table captions self-contained (split, scoring domain, units); Figure 9 cited; Table 9 formatting aligned.
- `_build_html.py`: all figure captions prose-style, no code identifiers, no interpretation beyond description.
- `make_figures.py`: in-figure labels free of code identifiers; figures regenerated.
- HTML rebuilt successfully.
- Next: Round 6 — numeric consistency + simulated reviewer pass.

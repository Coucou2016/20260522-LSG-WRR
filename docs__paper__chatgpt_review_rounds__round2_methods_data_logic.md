# ChatGPT Review Round 2 — Content Logic & Internal Consistency (Methods + Data)

**Date:** 2026-08-18 (UTC+8)
**Scope:** Sections 2.1–2.7 (Methods) and 3.1–3.2 (Data/Design) of `docs/paper/manuscript.md`
**Backup before edits:** `docs/paper/_archive_manuscript_pre_round2_20260818_022230.md`

## Issues raised by ChatGPT reviewer (external) and disposition

1. **O1/O2 stage interpretation.** O1 was labeled "numerical SVD floor" and O2 "EOF truncation / held-out out-of-subspace error", which implied O1 used all cells' theoretical basis and overstated O2. **Fix applied:** O1 = "Full-training-basis projection floor"; O2 = "Additional loss from truncating the available training basis to *k* modes"; added explicit note that O4−O3 is the GP-mapping contrast and that all dual-path stages share the production EXT gate.
2. **CRPS calibration wording.** "estimated from training events" was imprecise (it is training *predictions*, and only on active cells; censoring vs. closed form distinction was missing). **Fix applied:** rewritten with active-cell restriction, Gneiting–Raftery closed form, deterministic-mean invariance.
3. **Notation clash.** Inundation probability used Φ while CRPS also used Φ for standard-normal CDF. **Fix:** probability notation unified to Φ_N.
4. **Variance propagation left implicit.** Manuscript jumped from coefficient variance to cell variance without the formula. **Fix applied:** σ_i² = Σ_j φ_ij² v_j + σ_res,i² with the independence assumption stated.
5. **EXT gating of uncertainty unstated.** Added: cells gated dry carry zero probability; coefficient variance propagates through WSE branch only.
6. **Metric definitions absent.** POD/RFA/CSI now defined explicitly (RFA = FP/(TP+FP), verified against `lsg/evaluation.py`); PIT summarized over wet cells.
7. **"123/40/40 events" phrasing.** Checked — current manuscript already states Group 1 splits (Carlisle E1–E9; Chowilla 29; Burnett 74/56/18), consistent with `config/*.yaml` and audit trail. No change needed.
8. **Benchmark alignment paragraph.** Softened from "we report the published Group 1 split" to "headline comparisons retain the published Group 1 train/test split rather than pooling statistics across groups" (more accurate; Fraehr's protocol pools leave-one-group-out).
9. **EXT agreement 0.986 (Table 5) undefined.** Verified against `outputs/evaluation/burnett/diagnose_hlsg_o2_vs_rmse.json` (`ext_cell_agree`): wet-domain cell fraction where predicted binary EXT (threshold 0.5, AF cells forced wet) matches HF binary extent at τ = 0.03 m, averaged over the 18 held-out Burnett events. H-LSG and native global share the identical EXT branch, hence identical values — now stated as a construction check in Section 4.3 text under Table 5.

## Code verifications performed before edits
- `lsg/eof.py`: mean-centering before SVD; rank cap by numerical rank.
- `lsg/gp.py`: GPflow SGPR, Exponential kernel, two L-BFGS-B passes (100 it), inducing floor m = min{n, max[2, round(f·n), m_min]}, MIN_INDUCING_POINTS=16.
- `lsg/wse_ext.py`: EXT threshold 0.5, AF forcing, dry cells = terrain, zoning WSE-only.
- `lsg/uq.py`: CRPS latent-Gaussian closed form vs observed depth (dry=0); variance scaling Var_cal = s·Var_raw; EXT-gated UQ.
- `lsg/zoning.py`: residual EOFs fit to global residual; k-means features (RMS, mean, p90|res|) + standardized xy.
- `lsg/diagnostics.py`: common EXT gate across O1–O4 in dual path.
- `scripts/diagnose_burnett_hlsg_gap.py` + JSON: ext_cell_agree = 0.9861 (identical hlsg/global), n_test = 18.

**Decision:** all accepted items applied; no structural changes; claims remain bounded by computed evidence.

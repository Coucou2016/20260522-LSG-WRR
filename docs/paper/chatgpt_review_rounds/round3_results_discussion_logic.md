# ChatGPT Review Round 3 — Results/Discussion Logic

**Date:** 2026-08-18 (UTC+8)
**Scope:** Sections 4 (Results), 5 (Discussion), 6 (Conclusions) of `docs/paper/manuscript.md`
**Backup before edits:** `docs/paper/_archive_manuscript_pre_round3_20260818_*.md`
**Review chat:** ChatGPT Pro, chat `6a8347ff-...` ("Manuscript Review Feedback")

## Findings (18 total) and disposition

All 18 items accepted and applied as sentence-level edits; no structural changes.

### Must-fix (7)
1. **§4.6 fringe statistics inconsistency.** "observed wet frequency 0.62 overall" was incompatible with "roughly 70% of fringe cells are HF-dry false alarms" for the whole 0.5–0.95 fringe. Verified against `docs/paper/_dip_analysis.py` output recorded in `audit_trail.md`: the ~70% false-alarm share applies to the 0.6–0.9 bins (observed wet frequency 0.29–0.33), not the whole fringe. Wording now scopes the 70% to the 0.6–0.9 bins.
2. **§5.1 residual-modes-off control scope.** Original text implied the modes-off control was shown for Burnett; Tables 4/6 show it only for Chowilla and Carlisle. Now explicit.
3. **§5.1 capacity-allocation claim scope.** "O2–O1 primarily controlled by capacity" now scoped to Chowilla and Burnett (the cases with exact matched-capacity tests); Carlisle excluded.
4. **§5.1 matched-18 attribution.** Table 5 reports no O4–O2 for matched-18 global; text no longer attributes its degradation to the LF-to-HF mapping specifically.
5. **§5.1 final hedging.** "apparent localization advantage" replaced with "apparent truncation advantage of H-LSG" (Burnett H-LSG is predictively worse, not better).
6. **§5.3 nested-stability claim.** Chowilla nested check validates s=0.309 (workflow-fit), not the saved-state rescore optimum s=0.419 used in Table 9. Now stated; Burnett noted as not nested-checked.
7. **§5.3 "under-dispersed" + Tobit remedy contradiction.** Fringe is a mean-side false-alarm bias, not under-dispersion (s=0.417<1 indicates over-dispersion overall); Tobit censoring is already in the uncertainty treatment so cannot be proposed as an untried remedy; "extent-posterior sharpening" unsupported. Paragraph rewritten accordingly.
8. **§6 Burnett oracle attribution.** O4–O2 attribution is explicit only for H-LSG; sentence now reads "For Burnett H-LSG, the oracle analysis locates the additional degradation...".

### Should-fix (9)
9. §5.2 first paragraph: gains scoped to Chowilla/Burnett (Carlisle LF baseline already strong).
10. §5.3 scoring-domain cause: now reflects both restrictive trained extent domain and model errors outside it (matches §4.5).
11. §5.3 causal mechanism: false-alarm cells with latent mean above τ — variance shrinkage pushes P(h≥τ) toward one; cannot correct mean-side boundary error.
12. §5.3 "sampling noise" softened to "should not be interpreted as stable structure".
13. §5.4 "orthogonal" replaced with "distinct resource-allocation questions".
14. §5.5 "native H-LSG advantage" → "native reduction in H-LSG truncation error".
15. §5.5 added missing limitation: nested calibration check performed for Carlisle and Chowilla only, not Burnett.
16. §6 third paragraph: gains scoped to Chowilla/Burnett; Carlisle noted separately.
17. §6 calibration sentence: "Carlisle Max and Burnett H-LSG Max" with Chowilla "neutral in CRPS and adverse in active coverage".

### Polish (1)
18. §6 final sentence: "Under the controls tested here, ..." added explicit study scope.

## Verified correct (no change needed)
- All numbers cited in Sections 5–6 match Tables 2–9.
- Chowilla matched-capacity numbers (0.085 vs 0.093 m; 0.002 vs 0.013 m).
- Burnett capacity numbers (0.179/0.387/0.416 m; EXT agreement 0.986 by construction).
- Carlisle correctly treated as unresolved (13 requested modes realize only 8).
- Figure 8 mechanism coherent once false-alarm denominator corrected.
- Limitations disclose 1-vs-18 held-out events, HF-as-reference, unretrained ML baselines.

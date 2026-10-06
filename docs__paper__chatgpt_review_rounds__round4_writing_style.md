# ChatGPT Review Round 4 — Writing Style / AGU-WRR House Style

**Date:** 2026-08-18 (UTC+8)
**Scope:** Full-manuscript style review (Key Points, Abstract, Sections 1–6)
**Backup before edits:** `docs/paper/_archive_manuscript_pre_round4_20260818_*.md`
**Review chat:** ChatGPT Pro, chat `6a8347ff-...` ("Manuscript Review Feedback")
**Note:** First send attempt landed in an unrelated EMS chat (tab focus drift); response there was discarded. The prompt was re-sent to the correct review chat with URL guards; response used is from that chat only.

## Applied (34 of 36 findings)

### Key Points & Abstract (must-fix ×4, should-fix ×2)
- KP2/KP3: expanded LF/HF/GP/CRPS so Key Points stand alone.
- Abstract: sentence-case "spatial analysis"; defined CSI and RMSE at first use; title-cased "Continuous Ranked Probability Score" → "continuous ranked probability score"; reworded dual-reconstruction clause.

### Introduction (must-fix ×2, should-fix ×2, polish ×2)
- CSI/RMSE/CRPS/REOF redefined in body; sentence-case LSG expansion; direct attribution wording in closing.

### Methods (should-fix ×7, polish ×3)
- Section 2 opening: removed defensive reviewer-response tone; fixed "here-none" typo.
- 2.2: dropped redundant originality claim.
- 2.4: "RBF-GP" → spelled out; "exact GP" → "equivalent to the corresponding full Gaussian-process fit"; inducing-point "settings" → "counts".
- 2.5: table-free prose definitions of O1–O4 kept as table but contrast paragraph tightened; O4−O3 redundancy removed.
- 2.6: provenance phrasing → method phrasing.
- 2.7: metric names sentence-case; dropped "correct negatives"; evaluation-module sentence in active voice; scoring-domain definitions consolidated; `ts_*` → "LSG-TS metrics".

### Data (should-fix ×2, polish ×2)
- 3.1: "license restricted" → "license-restricted"; Table 1 publication-style notation (×10⁵, en-dash splits, nine/56/18 wording); memory phrasing.
- 3.2/2.7: "headline" → "primary" throughout.

### Results/Discussion/Conclusions (must-fix ×2, should-fix ×4, polish ×6)
- 4.1: DEM defined at first use; "foreshadowing" → analytical wording.
- 4.3: "behaves more strongly" → "shows a stronger divergence"; "downstream of" → "in the WSE pathway after".
- 4.6: bimodal sentence rewritten; percentages unified to %; ± and en-dash typography.
- 5.1: hedge stack trimmed ("could reasonably be interpreted" → "could be interpreted").
- 5.2: indirect phrasing → direct.
- 5.4: FIER acronym removed (undefined); tense unified; scope hedge preserved (added back the "do not establish ... ineffective in general" sentence the reviewer's replacement omitted).
- 5.5: "LESS-style event reselection" → "training-event reselection"; opening simplified.
- 6: final paragraph de-conversationalized.

### Typography pass (whole manuscript)
- O1-O4 → O1–O4 (en dash, 6 occurrences); O2-O1/O4-O2 contrasts → minus sign (24 occurrences); +/- → ±; ASCII ranges → en dashes; backticks removed from scoring-domain labels in prose (kept only where table column headers use wet_train/all_cells).

## Rejected (2)
- 2.5 reviewer proposal to replace the O1–O4 table with running prose: rejected — the table is clearer and was already verified; only the contrast paragraph was tightened.
- 5.4 reviewer replacement dropped the "controls do not establish localization/rotated decompositions are ineffective in general" hedge: the hedge was restored, since it is a claim-scoping sentence from Rounds 1–3.

## Checked and found correct (per reviewer)
- Figure/Table cross-references ("Figure 1", "Table 2", "Figure 8a") already consistent.
- Abbreviation discipline otherwise consistent after first definitions.

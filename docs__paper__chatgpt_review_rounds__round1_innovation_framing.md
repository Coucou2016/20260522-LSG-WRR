# Round 1 — innovation framing & claim calibration (ChatGPT external advisor)

**Chat URL:** https://chatgpt.com/c/6a8347ff-93b8-83ea-a14e-ac1894e0f5cf
**Date:** 2026-08-18
**Local verdict:** all 13 findings accepted (two with minimal local adaptation: "baseline LSG" -> "LSG" in the Burnett sentence; O1-O4 hyphenation kept as manuscript style "O1–O4").

## Findings (verbatim, condensed)

1. (major) KP1 undersells with "two public cases" -> name Chowilla and Burnett.
   PROPOSED: "Capacity-matched controls show no held-out depth benefit from residual hierarchical zoning in Chowilla or Burnett."
2. (minor) KP2 sharpen -> "Oracle error budgets trace Burnett depth degradation to LF-to-HF GP mapping, not extent reconstruction."
3. (major) KP3 weakest; report concrete 2-positive/1-neutral -> "Scalar variance calibration improves CRPS in Carlisle and Burnett but is neutral in Chowilla."
4. (minor) Abstract s1 categorical -> "High-fidelity flood inundation models can be computationally expensive for ensemble and rapid-prediction applications."
5. (major) Abstract "LSG provides most of the improvement..." vague/overstated -> "For Burnett, LSG substantially improves wet-domain extent skill over LF, increasing CSI from 0.853 to 0.975." (advisor said "baseline LSG"; adapted to "LSG")
6. (major) Abstract headline sentence -> "Capacity matching gives no depth-RMSE advantage to zoning on Chowilla (0.093 m versus 0.085 m for matched global LSG), while Burnett RMSE increases from 0.179 to 0.387 m; the O1–O4 ladder locates this degradation in LF-to-HF mapping."
7. (major) Carlisle as rank-limited, not positive exception -> "Carlisle does not provide the same capacity comparison because the global maximum-surface model is rank-limited by eight training events."
8. (minor) calibration sentence -> "Scalar variance rescaling improves CRPS for Carlisle and Burnett but is neutral on Chowilla."
9. (minor) final sentence tighten -> "...can reflect added representation capacity rather than localization itself and should be tested against capacity-matched global baselines."
10. (major) Introduction: add explicit novelty sentence before "The central question...": "Relative to the LSG and zonal-EOF formulations of Fraehr et al. (2022–2024), Tan et al. (2025), and Wang et al. (2025, 2026), the contribution here is not localization itself, but its capacity-controlled evaluation using matched global and residual-modes-off controls together with an O1–O4 oracle error ladder."
11. (major) Replace "The answer is heterogeneous..." with "The capacity-controlled result is consistent across the two cases in which it can be tested: the apparent truncation advantage does not survive matching on Chowilla or Burnett, whereas Carlisle is constrained by the rank available from eight maximum-surface training events."
12. (major) Replace final sentence with "This distinction provides a direct attribution test: localized EOF extensions should be credited with improved skill only when their gains persist against capacity-matched global controls."
13. (minor) Avoid summarizing results as "mixed"/"heterogeneous" elsewhere.

## 3-bullet summary (advisor)
- Key Points: KP1/KP2 lead with capacity-controlled null result and Burnett attribution; KP3 reports concrete 2-positive/1-neutral.
- Abstract: clean architecture; remove generic LSG-success dilution; Carlisle = rank-limited.
- Intro novelty: "we test whether zoning deserves causal credit after controlling representation capacity, and diagnose failures with ordered oracles."

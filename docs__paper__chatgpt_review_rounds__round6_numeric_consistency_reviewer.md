# Round 6 — Numeric consistency audit + simulated critical reviewer (ChatGPT)

Date: 2026-08-18 (UTC+8)
Chat: LSG WRR paper / 论文写作修改建议 (`6a82fa1e-ec94-83ea-9be2-31429a2f926d`)
Prompt: `docs__paper___round6_prompt_compact.txt` (compact extract: Key Points + Abstract, all tables verbatim,
every sentence containing a number from Results/Discussion, full Conclusions).
Injected via base64 chunks into `localStorage.__r6text`, verified byte-identical
(26,110 chars, checksum 33827) before sending.

## Verdict

"Substantively numerically coherent and very close to submission-ready." Remaining hard defects:
three Table-3 subtraction/rounding failures and the Burnett Key Point claim. Verbatim reply saved below.

## Findings

### TASK A — numeric consistency

| Status | Location | Finding | Required correction |
|---|---|---|---|
| FAIL | Table 3 Carlisle H-LSG; Results 4.2; Table 6 | displayed 0.052 − 0.048 = 0.004, not 0.005 m | contrast 0.004 or show extra decimals |
| FAIL | Table 3 Chowilla H-LSG; Results 4.3; Tables 4/7/8; Conclusions | displayed 0.034 − 0.020 = 0.014, not 0.013 m | contrast 0.014 or show extra precision |
| FAIL | Table 3 Chowilla global; Results 4.3; Tables 4/8 | displayed 0.078 − 0.020 = 0.058, not 0.057 m | contrast 0.058 or show extra precision |
| FAIL (claim) | Key Point 1 | H-LSG 0.387 m is actually LOWER than matched-18 global 0.416 m at equal capacity; "no benefit" misstates this | rewrite as truncation/accuracy decoupling vs native global baseline |
| CLARIFY | Abstract Burnett 0.179→0.387 | 0.179 is native 6-D global, not capacity-matched; reads as matched comparison | "relative to the native 6-dimensional global model" |
| CLARIFY | Table 3 Carlisle LSG-TS O4 = 0.102 vs 0.065 (ts RMSE) vs 0.099/0.154 (max-surface) | evaluation object/mask unstated | one sentence defining LSG-TS O4 object + mask |
| + suggestion | Table 9 caption | CRPS scoring domain not stated; 2.155 m vs 0.093 m wet RMSE easily misread | name the CRPS domain |

### Checks that PASS (summary)

- Burnett Table 3 arithmetic closes (0.083−0.074=0.009; 0.123−0.074=0.049); Carlisle LSG-TS 0.033−0.018=0.015.
- Table 5 O4−O2 exact: 0.179−0.123=0.056; 0.387−0.083=0.304.
- Chowilla capacity controls consistent everywhere (0.088/0.093/0.085/0.088 m; CSI 0.974/0.976/0.975/0.974; dims 3/15/15/3).
- Burnett capacity controls consistent except Key Point interpretation (0.179/0.387/0.416 m; EXT agreement 0.986).
- Carlisle capacity controls agree with Table 6 (0.112/0.094/0.202/0.112 m; rank-8 limitation).
- Inducing sweep exact (m=2,8,16,28 → 0.244/0.096/0.093/0.073 m; O2−O1 = 0.013 m).
- Zone sweep matches (9→21 dims; O2−O1 0.019→0.012; RMSE 0.087→0.103 m).
- Wet-correlation sensitivity consistent (CSI 0.978/0.976/0.974; RMSE 0.094; O2−O1 0.010).
- Deterministic scores match (Burnett 0.853→0.975 CSI, 0.989→0.387 m; Chowilla 0.925→0.976, 0.690→0.093 m; Carlisle 0.966→0.976, 0.101→0.094 m).
- Scoring-domain numbers consistent; probabilistic numbers match Table 9/Results 4.6; nested calibration reconciled;
  reliability count 8,936/581,061 = 1.538% ≈ 1.5%; units clean.

### TASK B — simulated reviewer

| Severity | Point | Fix |
|---|---|---|
| major | Key Point 1 overstates Burnett matched-capacity result (0.387 < 0.416 at equal capacity) | "Capacity controls show that lower truncation error from residual zoning does not imply lower RMSE than the native global baseline." |
| major | three Table-3 O2−O1 contrasts don't match displayed O2−O1 | recompute or show extra precision |
| major | Carlisle LSG-TS O4 = 0.102 m not reconciled with 0.065 / 0.099 / 0.154 m | define LSG-TS evaluation object + scoring mask |
| minor | Abstract Burnett comparison reads capacity-matched | name native 6-D global baseline explicitly |
| minor | "Gaussian-process mapping" narrower than O4−O2 diagnostic | "learned LF-to-HF WSE mapping, not the shared extent reconstruction" |
| minor | "same gate miss/false-alarm behavior" unsupported | replace with shared-EXT-prediction statement |
| minor | Table 9 CRPS population implicit | state CRPS scoring domain in caption |
| minor | front matter says calibration improves CRPS for "Carlisle" | "Carlisle Max and Burnett H-LSG Max" |

## Verbatim ChatGPT reply

> I treated the supplied compact extract as the numerical SSOT and used current AGU review
> criteria—significance, methods, data/evidence, presentation, and key points—as the frame for
> the simulated reviewer pass. I did not reopen issues from Rounds 1–5.
>
> TASK A — Numeric consistency audit
>
> Overall: almost clean, but not yet a full PASS. I find three displayed-arithmetic failures, one
> substantive Burnett claim mismatch, and two metric/comparator ambiguities that should be explicitly
> reconciled. Everything else checked below is internally consistent.
>
> FAIL — Table 3, Carlisle, LSG-Max H-LSG; repeated in Results 4.2 ("0.048…0.052…giving…0.005 m")
> and propagated as 0.005 in Table 6. At displayed precision, 0.052 − 0.048 = 0.004 m, not 0.005 m.
> Either change the displayed contrast to 0.004 m, or report O1/O2 with sufficient additional decimals
> to demonstrate that the separately rounded raw difference is 0.005 m.
>
> FAIL — Table 3, Chowilla, LSG-Max H-LSG; repeated as 0.013 in Results 4.3, Tables 4, 7, 8, Conclusions.
> At displayed precision, 0.034 − 0.020 = 0.014 m, not 0.013 m. Same remedy.
>
> FAIL — Table 3, Chowilla, LSG-Max global; repeated as 0.057 in Results 4.3, Tables 4 and 8.
> At displayed precision, 0.078 − 0.020 = 0.058 m, not 0.057 m. Same remedy.
>
> FAIL (claim) — Key Point 1. "Capacity-matched controls show no held-out depth benefit from residual
> hierarchical zoning in … Burnett" does not match Table 5: at equal WSE dimension 18, H-LSG has RMSE
> 0.387 m whereas matched-18 global has 0.416 m; H-LSG is therefore 0.029 m lower at matched capacity.
> What is true is that both are worse than the native 6-D global model at 0.179 m. Replace with a claim
> about truncation/accuracy decoupling or failure to beat the native global baseline.
>
> CLARIFY — Abstract "while Burnett RMSE increases from 0.179 to 0.387 m": 0.179 is native 6-D global,
> not capacity-matched global; write "relative to the native 6-dimensional global model".
>
> CLARIFY — Table 3 Carlisle LSG-TS O4 = 0.102 m vs Results 4.1 time-series RMSE 0.065 m and Table 2
> maximum-surface RMSE 0.099 m full mesh / 0.154 m wet domain: state the LSG-TS O4 evaluation object and
> scoring mask.
>
> [Checks that PASS: Burnett Table 3 arithmetic; Table 5 O4−O2 arithmetic (0.056/0.304 m); Chowilla
> capacity controls 0.088/0.093/0.085/0.088 m and CSI 0.974/0.976/0.975/0.974; Burnett capacity controls
> 0.179/0.387/0.416 m with EXT agreement 0.986; Carlisle capacity controls 0.112/0.094/0.202/0.112 m;
> inducing sweep m=2,8,16,28 → 0.244/0.096/0.093/0.073 m with O2−O1 = 0.013 m; zone sweep dims 9→21,
> O2−O1 0.019→0.012, RMSE 0.087→0.103 m; wet-correlation CSI 0.978/0.976/0.974, RMSE 0.094, O2−O1 0.010;
> deterministic scores Burnett 0.853→0.975 CSI, 0.989→0.387 m; Chowilla 0.925→0.976, 0.690→0.093 m;
> Carlisle 0.966→0.976, 0.101→0.094 m; scoring-domain numbers; Table 9 probabilistic numbers;
> nested calibration 0.310±0.007 tied to workflow s=0.309; reliability 8,936/581,061 = 1.538%; units.]
>
> One additional definition clarification would help Table 9: the caption does not state the CRPS
> scoring domain; naming it would prevent readers from assuming CRPS 2.155 m and wet-domain point RMSE
> 0.093 m share the same population.
>
> TASK B — Simulated critical WRR reviewer
>
> [major] Key Point 1 overstates the Burnett matched-capacity result because H-LSG has lower RMSE than
> matched-18 global LSG (0.387 versus 0.416 m). Fix: "Capacity controls show that lower truncation error
> from residual zoning does not imply lower RMSE than the native global baseline."
>
> [major] Three Table-3 O2−O1 values do not equal the displayed O2 minus O1 values, which undermines
> confidence in the central oracle diagnostic. Fix: recompute contrasts from displayed numbers or report
> sufficient O1/O2 precision.
>
> [major] The Carlisle LSG-TS O4 value of 0.102 m is not explicitly reconciled with the reported 0.065 m
> time-series RMSE and 0.099/0.154 m maximum-surface RMSEs. Fix: add one sentence defining the exact
> LSG-TS evaluation object and scoring mask represented by O4 = 0.102 m.
>
> [minor] The Abstract makes the Burnett 0.179→0.387 m comparison sound capacity matched even though
> 0.179 m is the native 6-mode global result. Fix: name the native 6-dimensional global model.
>
> [minor] "Gaussian-process mapping" is slightly narrower than the displayed O4−O2 diagnostic. Fix:
> "Oracle diagnostics trace Burnett degradation to the learned LF-to-HF WSE mapping, not the shared
> extent reconstruction."
>
> [minor] The claim of "the same gate miss/false-alarm behavior" is not quantitatively shown. Fix:
> "Because the WSE variants share the same EXT prediction, differences in their depth RMSE cannot
> originate from the EXT branch."
>
> [minor] Table 9 leaves the CRPS scoring population implicit. Fix: add "CRPS is evaluated on
> [the actual scoring domain]" to the caption.
>
> [minor] The front-matter statement that calibration improves CRPS for "Carlisle" is broader than the
> evidence, which is specifically Carlisle Max. Fix: "Carlisle Max and Burnett H-LSG Max".
>
> Overall verdict: The manuscript is substantively numerically coherent and very close to
> submission-ready, but I would not submit the present text unchanged. The capacity-control tables,
> deterministic scores, UQ numbers, repeated values, units, and most cross-references are consistent;
> the remaining hard defects are the three Table-3 subtraction/rounding failures and the Burnett Key
> Point, which currently misstates what the matched-18 comparison shows. Once those are corrected and
> the Carlisle LSG-TS O4 evaluation object plus CRPS scoring domain are explicitly identified, I would
> regard the manuscript as numerically sound and ready for submission from the standpoint of this final
> consistency/reviewer pass.

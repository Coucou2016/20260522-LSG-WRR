# Capacity-Controlled Evaluation of Residual Hierarchical Zoning in Multi-Fidelity Flood Inundation Surrogates

**Authors:** [Author names and affiliations to be finalized by the author team before submission]  
**Affiliations:** [To be finalized]  
**Corresponding author:** [To be finalized]

## Key Points

- Capacity controls show that lower truncation error from residual zoning does not imply lower RMSE than the native global baseline.
- Oracle diagnostics trace Burnett degradation to the learned low- to high-fidelity water-surface-elevation mapping, not the shared extent reconstruction.
- Scalar variance calibration lowers continuous ranked probability score in Carlisle Max and Burnett H-LSG Max but not Chowilla.

## Abstract

High-fidelity flood inundation models can be computationally expensive for ensemble and rapid-prediction applications. Low-fidelity, spatial analysis, and Gaussian process learning (LSG) addresses this cost by mapping low-fidelity (LF) hydrodynamic fields to high-fidelity (HF) empirical orthogonal function representations. We examine whether residual hierarchical zoning, which augments global LSG with zone-specific residual modes, improves prediction once the additional representation capacity is controlled. Tests use three public benchmark cases (Carlisle, Chowilla, and Burnett), dual reconstruction of inundation extent and water-surface elevation, an O1–O4 oracle error ladder, and continuous ranked probability score (CRPS) variance calibration. For Burnett, LSG substantially improves wet-domain extent skill over LF, increasing the critical success index (CSI) from 0.853 to 0.975. Capacity matching gives no root-mean-square error (RMSE) advantage to zoning on Chowilla (0.093 m versus 0.085 m for matched global LSG), while relative to the native 6-dimensional global model, Burnett H-LSG wet-domain RMSE increases from 0.179 to 0.387 m; the O1–O4 ladder locates this degradation in LF-to-HF mapping. Carlisle does not provide the same capacity comparison because the global maximum-surface model is rank-limited by eight training events. Scalar variance rescaling improves CRPS for Carlisle Max and Burnett H-LSG Max but is neutral on Chowilla. These results show that apparent gains from localized residual modes can reflect added representation capacity rather than localization itself and should be tested against capacity-matched global baselines.

**Keywords:** flood inundation; multi-fidelity surrogate; empirical orthogonal functions; Gaussian process; spatial zoning; uncertainty quantification

## 1. Introduction

Flood inundation models are used to resolve the spatial distribution of water depth and extent for forecasting, emergency response, and scenario assessment. Two-dimensional hydrodynamic models can represent channels, floodplains, and temporary wetting at high spatial resolution, but the computational cost of repeated high-fidelity (HF) simulations limits their use in ensemble prediction and other time-sensitive applications. Surrogate models reduce this cost by learning from a limited set of HF simulations together with information that can be generated more cheaply.

Low-fidelity, spatial analysis, and Gaussian process learning (LSG) is a multi-fidelity surrogate in which low-fidelity (LF) hydrodynamic fields are projected onto an HF empirical orthogonal function (EOF) basis and mapped to HF expansion coefficients (ECs) with Gaussian process regression (Fraehr et al., 2022, 2023a, 2023b). The approach retains physically meaningful LF information while using spatial reduction to make the HF prediction problem tractable. Subsequent studies have compared LSG with machine-learning surrogates on public flood-inundation benchmarks (Fraehr et al., 2024a), examined event selection for HF training (Fraehr et al., 2024b), and investigated Gaussian-process kernel choice (Lu et al., 2025). Wang et al. (2026) further evaluated LSG for a large and hydrodynamically complex floodplain and compared time-series (LSG-TS) and maximum-surface (LSG-Max) training. That study identified zonal EOF analysis as a possible direction for improving spatial representation in heterogeneous domains.

Spatial localization is plausible because a single global EOF basis must represent flood behavior across regions with different hydraulic responses. Related approaches have therefore introduced regional or rotated spatial decompositions. Tan et al. (2025) regionalized LSG over focus subdomains, Wang et al. (2025) combined rotated EOF analysis with sparse Gaussian-process mapping, and rotated-EOF (REOF)-based flood-extent methods have partitioned large satellite-observed domains (Chang et al., 2020, 2023; Markert et al., 2026; Wan et al., 2025). Compound-flood applications using SFINCS-LSG have also extended EOF-based surrogate modeling to coastal settings, with accompanying scripts and data made publicly available (Eilander et al., 2025, 2026a, 2026b). These studies show that spatial decomposition can be useful, but they do not answer a separate question that arises for hierarchical LSG: does a localized residual representation improve prediction because it is localized, or because it simply introduces more retained coefficients?

That distinction matters for a fair comparison. In the residual hierarchical formulation considered here, a global EOF basis represents basin-scale structure and each zone contributes additional residual EOF modes. The zoned model therefore has a larger coefficient vector and a higher-dimensional LF-to-HF regression problem than the native global model. A reduction in truncation error is expected when more modes are retained, even if the spatial partition itself provides no additional predictive information. A capacity-matched global baseline is needed before a reduction in truncation error can be attributed to localization.

Two further issues affect interpretation of LSG performance. First, end-to-end critical success index (CSI) or root-mean-square error (RMSE) does not identify where error enters the surrogate. Tan et al. (2025) separated downscaling and LSG mapping error, but the dual extent-plus-water-surface formulation used in hybrid LSG contains several additional stages: EOF truncation, LF projection into the HF subspace, Gaussian-process mapping, and extent gating. We therefore use an ordered O1–O4 oracle ladder to diagnose these stages on the same reconstruction path. Second, Gaussian-process prediction provides a natural basis for probabilistic inundation, yet the posterior variance may be poorly calibrated after spatial reconstruction. Probabilistic flood surrogates have been developed with Gaussian processes and related emulators (Donnelly et al., 2022; Kohanpur et al., 2023; López-Lopera et al., 2022; Siripatana et al., 2025; Zanchetta & Coulibaly, 2022), but calibration of reconstructed LSG uncertainty has received less attention.

This study addresses these questions using the public Carlisle, Chowilla, and Burnett cases released by Fraehr (2024). We first reproduce the dual extent and water-surface-elevation LSG workflow and evaluate residual hierarchical zoning at its native capacity. We then match the global model to the zoned model in total water-surface coefficient dimension and perform complementary controls in which residual modes are removed. Inducing-point and zone-count sensitivities test whether sparse-GP approximation or coefficient count can explain the observed behavior. The O1–O4 ladder is used to locate the Burnett degradation, and a scalar continuous ranked probability score (CRPS)-based variance adjustment is evaluated for probabilistic depth and inundation output. Because the published Group 1 splits differ in the number of held-out events and because full time-series evaluation is not computationally feasible for all three cases, conclusions are restricted to the evaluated splits and maximum-surface setting where applicable.

Relative to the LSG and zonal-EOF formulations of Fraehr et al. (2022, 2023a, 2024a), Tan et al. (2025), and Wang et al. (2025, 2026), the contribution here is not localization itself, but its capacity-controlled evaluation using matched global and residual-modes-off controls together with an O1–O4 oracle error ladder. The central question is therefore not whether zonal EOF methods can ever be useful, but whether the residual hierarchical implementation tested here provides predictive benefit beyond the extra capacity it introduces. The capacity-controlled result is consistent across the two cases in which it can be tested: the apparent truncation advantage does not survive matching on Chowilla or Burnett, whereas Carlisle is constrained by the rank available from eight maximum-surface training events. This distinction provides a direct attribution test: we therefore attribute improved skill to localized EOF extensions only when their gains persist against capacity-matched global controls.

## 2. Methods

The LSG framework follows Fraehr et al. (2022, 2023a), but we independently implemented all components used in the present experiments in Python 3.12 rather than reusing the upstream Hybrid LSG reference code. The complete source is archived in the public repository cited in Section 7, and the reported results are generated by this implementation.

### 2.1. Multi-Fidelity LSG Formulation

For one event or time step, let **h**<sup>HF</sup> ∈ ℝ<sup>*n*</sup> denote the HF water-depth field and **h**<sup>LF→HF</sup> ∈ ℝ<sup>*n*</sup> the LF field interpolated to the HF mesh. Cells with depth ≥ τ are treated as wet, with τ = 0.03 m throughout. Always-flooded (AF) and temporary-flooded (TF) masks follow the Fraehr-style cell categories used by the public benchmark data.

Global LSG compresses the HF training fields with EOF analysis. Fields are mean-centered with the training-event mean before fitting and projection, and the same preprocessing convention is used at reconstruction, so the attainable mode count is capped by the numerical rank of the centered HF training matrix. Optional cell-area weighting multiplies centered fields by the square root of cell area before the singular-value decomposition and is divided out at reconstruction. If Φ contains the retained HF EOF modes and **c**<sup>HF</sup> the corresponding HF ECs, an HF field is reconstructed from a reduced coefficient vector rather than predicted cell by cell. The LF fields are projected onto the same HF basis to obtain LF pseudo-ECs. Sparse Gaussian process regression (SGPR) then learns the mapping from LF pseudo-ECs to HF ECs. At prediction time, a new LF simulation is projected onto the HF basis, the GP predicts the corresponding HF coefficients, and the field is reconstructed from the predicted coefficients.

### 2.2. Dual Extent and Water-Surface-Elevation Reconstruction

The operational formulation follows the hybrid extent-plus-water-surface approach of Fraehr et al. (2023a). Two independent LSG emulators are trained simultaneously. The first predicts inundation extent (EXT) on TF cells, with AF cells forced wet. The second predicts water-surface elevation (WSE) over the retained wet domain. Both emulators use the same EOF+SGPR pipeline, with separate EOF bases and GP hyperparameters. After prediction, the two fields are combined with terrain elevation *Z*:

> **WSE′** = WSE if EXT = 1; **WSE′** = *Z* if EXT = 0;  
> *h* = max(WSE′ − *Z*, 0),

after which depths below τ are set to dry. The EXT emulator is trained on binary TF-cell wet/dry targets; its continuous reconstruction is converted to EXT ∈ {0, 1} with a fixed decision threshold of 0.5 in all experiments. In the WSE branch, dry training samples retain terrain elevation as their water-surface value, and WSE values below terrain elevation plus τ are clipped to terrain before the terrain subtraction. Thus, EXT is a learned component of the surrogate rather than an LF post-processing gate applied to a depth-only prediction.

### 2.3. Residual Hierarchical Zoning

We introduce residual hierarchical LSG (H-LSG), a formulation that keeps a global EOF basis for basin-scale structure and represents the remaining WSE residual with zone-specific EOFs. Writing η for WSE, the reconstruction is

> **η** = Φ<sub>global</sub> **c**<sub>global</sub> + Σ<sub>*z*</sub> **1**<sub>*z*</sub> Φ<sub>*z*</sub><sup>res</sup> **c**<sub>*z*</sub>,

and water depth *h* is obtained only afterward through the EXT-plus-terrain combination in Section 2.2. Zone residual EOFs are fitted per zone to the HF training WSE after subtraction of the *k*<sub>global</sub>-mode global reconstruction. Zones are obtained from *k*-means clustering of per-cell residual-response features (root-mean-square residual, mean residual, and 90th percentile of the absolute residual) augmented with standardized cell coordinates; the resulting labels are not constrained to be hydrologically connected subcatchments. Under the dual EXT+WSE formulation, zoning is applied only to the WSE branch; the EXT emulator remains global. LF residual pseudo-ECs are obtained by applying the same global residualization and zone-specific projection to the LF field after interpolation to the HF mesh. All zone labels, residual-response features, and residual EOF bases are constructed from training events only and are held fixed when predicting the test event(s).

This construction changes both the WSE spatial representation and the dimension of the WSE LF-to-HF regression problem. If the global model retains *k*<sub>global</sub> coefficients and each of *n*<sub>zones</sub> zones contributes *k*<sub>res</sub> residual modes, then the WSE coefficient dimension becomes *k*<sub>global</sub> + *n*<sub>zones</sub> × *k*<sub>res</sub>.

For the default maximum-surface experiments, the dimension increases from 3 to 15 on Chowilla and from 6 to 18 on Burnett. Carlisle uses 1 global mode plus four sets of three residual modes, for a total dimension of 13. These dimension changes motivate the matched-capacity controls described in Section 3.

### 2.4. Sparse Gaussian Process Regression

Each retained HF coefficient is modeled by a separate SGPR with the retained LF pseudo-EC vector as the regression input and that HF coefficient as the scalar target; LF pseudo-ECs and HF ECs are standardized separately before training and prediction. We use GPflow SGPR with an exponential covariance kernel; kernel variance, length scales, and likelihood variance are initialized, then optimized in two L-BFGS-B passes (100 iterations each), with inducing-point locations drawn from standardized training rows and held fixed during optimization. A custom NumPy radial-basis-function Gaussian process is retained only as a software fallback and is not part of the reported comparison protocol; every reported run uses the GPflow backend. Maximum-surface training can involve relatively few events. Carlisle Group 1, for example, contains eight training events. When the H-LSG coefficient vector is expanded, a small default inducing-point fraction may leave too few inducing points to represent the LF-to-HF mapping. We therefore set the inducing budget to *m* = min{*n*<sub>train</sub>, max[2, round(*f*·*n*<sub>train</sub>), *m*<sub>min</sub>]}, where *f* is the default inducing-point fraction (0.02) and *m*<sub>min</sub> the configured floor, capped at the number of training events (*n*<sub>train</sub>). At the cap, SGPR with inducing points equal to the training rows is equivalent to the corresponding full Gaussian-process fit. This inducing-point floor is a numerical robustness addition that is not present in the reference LSG implementation.

The inducing-point floor is treated as a numerical robustness condition rather than a methodological contribution. Its influence is evaluated explicitly on Chowilla with minimum inducing-point counts of 2, 8, 16, and 28.

### 2.5. O1–O4 Oracle Error Ladder

To distinguish representation error from LF projection and GP mapping, we introduce a four-stage counterfactual oracle ladder evaluated on the same dual EXT+WSE reconstruction path. This diagnostic is not part of the LSG reference literature; Tan et al. (2025) proposed a two-component split (downscaling vs. LSG mapping), whereas our ladder separates truncation (O2 − O1), LF expressibility (O3 − O2), and GP mapping (O4 − O3) under the same extent gate, WSE reconstruction, and clipping rules.

| Stage | Inputs | Interpretation |
|---|---|---|
| O1 | HF true ECs, full training-rank modes | Full-training-basis projection floor |
| O2 | HF true ECs, truncated to *k* modes | Additional loss from truncating the available training basis to *k* modes |
| O3 | LF pseudo-ECs, no GP | LF expressibility in the retained HF subspace |
| O4 | Full LSG prediction | End-to-end surrogate error on the production path |

The dual-path variant applies the same hierarchy synchronously to the EXT and WSE branches and combines them with the production gating before scoring, so all four stages use the same production-path EXT reconstruction; O1–O4 therefore diagnose the WSE pathway conditional on a common extent gate. The difference O2 − O1 is the truncation contrast, O3 − O2 reflects replacement of HF coefficients by direct LF projections, and O4 − O3 reflects replacement of direct LF pseudo-ECs by GP-predicted HF ECs. These differences are not additive error shares. Extent gating, WSE reconstruction, clipping, and GP prediction make the sequence nonlinear, so the contrasts are interpreted only in the stated order.

### 2.6. Posterior Variance and CRPS Calibration

We implement a probabilistic extension of LSG that propagates GP predictive variance to flood-depth maps and inundation probability. While probabilistic flood surrogates exist in other frameworks (Donnelly et al., 2022; López-Lopera et al., 2022; Kohanpur et al., 2023; Siripatana et al., 2025), here we combine GP coefficient-variance propagation through linear EOF reconstruction, left-censored (Tobit) observation modeling, and scalar CRPS-based variance calibration within the LSG framework.

Predictive variance in coefficient space is propagated through the linear EOF reconstruction and combined with a cell-wise residual/truncation term to obtain a latent depth distribution *H*\* ∼ 𝒩(μ, σ²). Observation is represented as a left-censored (Tobit) process:

> *h* = 0 if *H*\* < τ; *h* = *H*\* if *H*\* ≥ τ.

The corresponding inundation probability is

> *P*(*h* ≥ τ) = 1 − Φ<sub>N</sub>((τ − μ) / σ),

where Φ<sub>N</sub> is the standard-normal cumulative distribution function. The latent variance is assembled as σ<sub>*i*</sub><sup>2</sup> = Σ<sub>*j*</sub> φ<sub>*ij*</sub><sup>2</sup> *v*<sub>*j*</sub> + σ<sub>res,*i*</sub><sup>2</sup>, where *v*<sub>*j*</sub> is the predictive variance of coefficient *j*, cross-coefficient covariance terms are taken as zero because the coefficient GPs are fitted independently, and σ<sub>res,*i*</sub><sup>2</sup> is a cell-wise residual variance estimated from training-event reconstruction residuals and held fixed at prediction. Uncertainty propagation conditions on the deterministic EXT gate: cells gated dry have zero predicted depth and zero inundation probability, and coefficient uncertainty is propagated through the WSE branch only.

The raw posterior can be over-dispersed. Carlisle Max, for example, has uncalibrated 90% coverage of approximately 0.996 when all cells are included. A single variance multiplier *s* ≥ 0 is therefore estimated from training predictions by minimizing mean Gaussian Continuous Ranked Probability Score (CRPS):

> Var<sub>cal</sub> = *s* · Var<sub>raw</sub>.

CRPS is evaluated for the latent Gaussian *H*\* using the Gaussian closed form of Gneiting and Raftery (2007) against the observed clipped depth, with dry cells scored at zero; censoring is used separately for zero-depth expectations and inundation-probability diagnostics. The fit is restricted to active cells (observed or predicted latent depth at least τ) so that EXT-gated dry zeros do not dominate the objective. Variance scaling leaves the deterministic point prediction used for RMSE and CSI unchanged; it changes only the predictive distribution used for probabilistic scores. The calibration assessment therefore focuses on CRPS and interval coverage. Because dry cells generated by the extent gate can dominate all-cell coverage, we also report active-cell coverage for cells where the observation or predictive mean is at least τ.

For *z* = (*y* − μ) / σ, Gaussian CRPS is

> CRPS(𝒩(μ, σ²), *y*) = σ [ *z* (2Φ<sub>N</sub>(*z*) − 1) + 2φ(*z*) − 1/√π ]

(Gneiting & Raftery, 2007), with φ the standard-normal density. The stability of *s* is checked by leave-one-training-event-out nested validation for Chowilla and Carlisle Max: in each nested check, *s* is fitted without the omitted event and evaluated on that event; outer test events are never used to estimate *s*.

### 2.7. Evaluation Metrics and Scoring Domains

Binary inundation performance is evaluated at τ = 0.03 m. With hits (TP), false alarms (FP), and misses (FN) defined against the HF binary extent at this threshold, probability of detection is POD = TP/(TP+FN), rate of false alarms is RFA = FP/(TP+FP), and critical success index is CSI = TP/(TP+FP+FN). Depth performance is summarized by RMSE. POD and RFA are computed in every evaluation summary alongside CSI and RMSE, but the tables here emphasize CSI and RMSE because they are the primary comparisons. We compute all metrics with the study's Python evaluation module rather than the reference Fraehr MATLAB evaluation script. The protocol defines two spatial scoring domains: the training wet domain (wet_train), corresponding to the Fraehr category-based wet index, and the full HF mesh (all_cells). The distinction is particularly important for Chowilla.

Time-series scores from LSG-TS are kept separate from maximum-surface scores and are never pooled across the two data products. For Carlisle, LSG-TS metrics refer to the held-out time series, whereas the maximum surface derived from that time series is evaluated independently. Probabilistic evaluation uses CRPS, Brier score, probability integral transform summaries over wet cells, and 50% and 90% interval coverage. The combination of spatial diagnostics, quantitative scores, and purpose-specific tests follows broader recommendations for evaluating environmental models (Bennett et al., 2013).

The benchmark protocol is aligned with Fraehr et al. (2024a) in its use of the public Carlisle, Chowilla, and Burnett data, the group-structured event splits, the wet-domain mask, and CSI. It differs in three respects. Primary comparisons retain the published Group 1 train/test split rather than pooling performance statistics across benchmark groups; depth performance is summarized by RMSE on the evaluated surfaces; and the machine-learning baselines and 50% extrapolation experiments of Fraehr et al. (2024a) are not re-trained here.

## 3. Public Data and Experimental Design

### 3.1. Benchmark Cases

The paired HF and LF inundation cubes are from Fraehr (2024), DOI 10.26188/24312658, and are distributed under CC BY 4.0. We use the three fully public benchmark cases: Carlisle, Chowilla, and Burnett. The Brisbane TUFLOW/URBS data used by Wang et al. (2026) are license-restricted and are not part of the redistributable evidence base considered here.

**Table 1. Public benchmark cases, HF/LF solver pairs, domain sizes, temporal reduction products, and Group 1 training/test splits used in this study.**

| Case | HF / LF solvers | HF scale (order) | Events / Group 1 split | Temporal reduction |
|---|---|---:|---|---|
| Carlisle | LISFLOOD-FP / HEC-RAS | ~5.8×10⁵ cells | Nine events; E2–E9 training, E1 testing | Full time series and maximum surface |
| Chowilla | fine / coarse HEC-RAS | ~1.1×10⁵ cells | 29 events; 28 training, E1 testing | Maximum surfaces |
| Burnett | TUFLOW / HEC-RAS | ~7.8×10⁵ cells | 74 events; 56 training, 18 testing | Maximum surfaces |

Full time-series Group 1 experiments are retained for Carlisle. Chowilla and Burnett are evaluated primarily on maximum-inundation surfaces because their full time-series stacks exceed the available memory. The Burnett in-memory HF stack is approximately 199 GB, compared with approximately 128 GB of available RAM; Chowilla becomes similarly restrictive when the dual EXT+WSE and uncertainty workflows are included. These constraints define the scope of the present comparison rather than a claim about time-series behavior at those sites.

### 3.2. Capacity Controls and Sensitivity Experiments

All primary experiments use the dual EXT+WSE reconstruction. The native global model is compared with residual H-LSG using residual-response *k*-means zoning. To separate localization from coefficient capacity, we use two complementary controls. First, the global EOF mode count is increased to match the total H-LSG WSE coefficient dimension where this is feasible: 15 modes on Chowilla and 18 on Burnett. Carlisle requests 13 modes, but only eight can be realized because the maximum-surface training matrix contains eight events. Second, residual modes are set to zero while the H-LSG partitioning machinery is retained. This control reduces H-LSG to the native global coefficient dimension.

Two additional Chowilla experiments probe approximation effects. The minimum SGPR inducing-point budget is varied over {2, 8, 16, 28}, and the number of residual zones is varied over {2, 4, 6}. A wet-correlation partition is also evaluated as a zoning sensitivity. For Burnett, the O1–O4 ladder is combined with an extent-agreement comparison to determine whether the H-LSG degradation is associated with the shared EXT gate or with the WSE mapping.

The independent evaluation unit is the held-out event or event set, not the raster cell. Carlisle and Chowilla maximum-surface Group 1 evaluations each contain one held-out event; Burnett contains 18. Raster cells contribute to spatial performance metrics but are not treated as independent replicates for inferential testing. We therefore report controlled effect-size comparisons rather than cell-based *p*-values.

The primary maximum-surface workflows were run with Python 3.12 using NumPy, SciPy, scikit-learn, h5py, TensorFlow, and GPflow. Package versions are recorded in the public repository environment file. All reported accuracy metrics compare surrogate output with the corresponding HF hydrodynamic simulation, not with independent observations.

## 4. Results

### 4.1. Baseline Spatial Performance

The extent maps in Figure 1 compare LF and LSG-Max predictions with HF at the 0.03 m threshold. Burnett shows the largest reduction in misses and false alarms after the LSG correction. Carlisle has relatively strong LF extent agreement before upscaling, so the visual change is smaller. Chowilla shows a different pattern: extent disagreement is concentrated outside the training wet-domain mask, consistent with the large difference between wet-domain and all-cell scores reported in Section 4.5.

Peak-depth errors in Figure 2 show the same broad pattern. LF-HF errors are large over parts of Chowilla and Burnett and are reduced by LSG-Max over much of the trained wet domain. Carlisle errors are smaller in magnitude. Figure 3 adds the probabilistic view by showing reconstructed *P*(*h* ≥ 0.03 m) for the three maximum-surface examples.

Table 2 summarizes point performance. On Burnett, H-LSG increases wet-domain CSI from 0.853 for LF to 0.975 and reduces wet-domain RMSE from 0.989 to 0.387 m. The native global LSG reaches the same CSI with a substantially lower RMSE of 0.179 m. Chowilla shows a similar LF-to-LSG improvement on the wet domain: CSI increases from 0.925 to 0.976 for H-LSG and RMSE decreases from 0.690 to 0.093 m. The native global model gives a slightly lower wet-domain RMSE of 0.088 m. Carlisle begins from a stronger LF baseline; H-LSG changes wet-domain CSI from 0.966 to 0.976 and RMSE from 0.101 to 0.094 m.

**Table 2. Critical success index (CSI) and depth root-mean-square error (RMSE; m) for the Group 1 evaluations at the 0.03 m inundation threshold, reported on the training wet-domain mask and the full HF mesh.**

| Case | Model | CSI (full mesh) | CSI (training wet domain) | RMSE full mesh (m) | RMSE wet domain (m) |
|---|---|---:|---:|---:|---:|
| Carlisle | LF only | 0.960 | 0.966 | 0.074 | 0.101 |
| Carlisle | LSG-TS (maximum surface) | 0.970 | 0.970 | 0.099 | 0.154 |
| Carlisle | LSG-Max H-LSG | 0.976 | 0.976 | 0.061 | 0.094 |
| Chowilla | LF only | 0.930 | 0.925 | 0.690 | 0.690 |
| Chowilla | LSG-Max H-LSG | 0.390 | 0.976 | 3.789 | 0.093 |
| Chowilla | LSG-Max global | 0.390 | 0.974 | 3.789 | 0.088 |
| Burnett | LF only | 0.853 | 0.853 | 0.983 | 0.989 |
| Burnett | LSG-Max H-LSG | 0.975 | 0.975 | 0.384 | 0.387 |
| Burnett | LSG-Max global | 0.975 | 0.975 | 0.179 | 0.179 |

Figure 4 compares the corresponding wet-domain CSI and RMSE values across cases. The dominant contrast is the LF-to-LSG improvement in Chowilla and Burnett rather than the smaller differences among LSG variants. For Carlisle LSG-TS, the held-out time-series score is CSI 0.959 with RMSE 0.065 m. The maximum surface reconstructed from that time-series model is a different evaluation object and gives CSI 0.970 with all-cell RMSE 0.099 m (Table 2).

### 4.2. Oracle Error Budgets

Figure 5 and Table 3 show the O1–O4 ladder. On Carlisle Max, the test RMSE changes from 0.048 m at the full-rank HF reconstruction (O1) to 0.052 m after truncation (O2), giving an O2 − O1 contrast of 0.005 m. Direct LF projection increases the RMSE to 0.068 m (O3), and the full model reaches 0.094 m (O4). The relatively small O2 − O1 gap indicates that truncation is not the principal source of Carlisle Max error at the retained H-LSG capacity. Reported O2 − O1 and O4 − O2 contrasts throughout this study are computed from the unrounded stage RMSEs; at the displayed three-decimal precision, the rounded contrast can therefore differ from the difference of the displayed O1 and O2 values by up to 0.001 m.

Chowilla and Burnett show larger discrepancies between direct LF projection and the HF-oracle stages. For Chowilla H-LSG, O2 is 0.034 m and O3 is 0.701 m; the learned full mapping then reduces the final error to 0.093 m. Burnett H-LSG similarly increases from 0.083 m at O2 to 0.668 m at O3, but the full model reaches only 0.387 m. The native Burnett global model has a larger truncation contrast (O2 − O1 = 0.049 m) yet a much lower O4 error of 0.179 m. Thus, smaller truncation error does not imply better operational prediction.

**Table 3. O1–O4 depth RMSE (m) for the Group 1 test evaluations on the training wet-domain scoring mask.** The O2 − O1 column is computed from unrounded O1 and O2 values before display rounding; for example, Carlisle LSG-Max H-LSG gives 0.0525 − 0.0478 = 0.0047 ≈ 0.005 m. The Carlisle LSG-TS row evaluates the 266 held-out test time steps of the time-series model with clipped-depth RMSE on the training wet-domain mask; it is a different evaluation object from the held-out time-series RMSE of 0.065 m (all cells) and the maximum-surface values in Table 2 (0.099 m full mesh, 0.154 m wet domain).

| Case | Variant | O1 | O2 | O3 | O4 | O2 − O1 |
|---|---|---:|---:|---:|---:|---:|
| Carlisle | LSG-TS H-LSG | 0.018 | 0.033 | 0.240 | 0.102 | 0.015 |
| Carlisle | LSG-Max H-LSG | 0.048 | 0.052 | 0.068 | 0.094 | 0.005 |
| Chowilla | LSG-Max H-LSG | 0.020 | 0.034 | 0.701 | 0.093 | 0.013 |
| Chowilla | LSG-Max global | 0.020 | 0.078 | 0.666 | 0.088 | 0.057 |
| Burnett | LSG-Max H-LSG | 0.074 | 0.083 | 0.668 | 0.387 | 0.009 |
| Burnett | LSG-Max global | 0.074 | 0.123 | 0.708 | 0.179 | 0.049 |

### 4.3. Native and Capacity-Matched Zoning Comparisons

At native capacity, H-LSG appears to improve the truncation contrast on both Chowilla and Burnett. Figure 6 compares wet-domain depth RMSE for the native global model and residual H-LSG across the three cases; the corresponding truncation contrasts (Table 4 and Table 5) show that Chowilla O2 − O1 decreases from 0.057 m for the 3-mode global model to 0.013 m for the 15-dimensional H-LSG model, while CSI changes only from 0.974 to 0.976 and RMSE increases from 0.088 to 0.093 m. Wet-domain CSI is nearly identical between the two models because the extent gate is shared and global, so it is reported in the text rather than as a separate panel. Burnett shows a stronger divergence between truncation error and operational RMSE: O2 − O1 decreases from 0.049 to 0.009 m, but wet-domain RMSE increases from 0.179 to 0.387 m. Because the zoned models use more coefficients, these native comparisons do not isolate the effect of localization.

The Chowilla matched-capacity control removes that difference in coefficient dimension. A 15-mode global EOF model attains RMSE 0.085 m, lower than both the native global model (0.088 m) and H-LSG (0.093 m). Its O2 − O1 contrast is 0.002 m, also lower than the 0.013 m obtained with H-LSG. When residual modes are disabled, H-LSG returns to the native global result. The reduction in truncation error that appears under native zoning can therefore be reproduced, and in this case exceeded, by allocating the same capacity to the global basis.

**Table 4. Chowilla capacity control for the Group 1 maximum-surface test event, scored on the training wet-domain mask. RMSE and O2 − O1 are reported in meters.**

| Model | WSE dimension | CSI | RMSE (m) | Test O2 − O1 (m) |
|---|---:|---:|---:|---:|
| Global (native) | 3 | 0.974 | 0.088 | 0.057 |
| H-LSG residual *k*-means | 15 | 0.976 | 0.093 | 0.013 |
| Global matched-15 | 15 | 0.975 | 0.085 | 0.002 |
| H-LSG residual modes = 0 | 3 | 0.974 | 0.088 | 0.057 |

Burnett provides a complementary result. Increasing the global model from 6 to 18 coefficients reduces O2 − O1 from 0.049 to 0.004 m, similar to the reduction obtained with 18-dimensional H-LSG (0.009 m). Neither expanded model improves prediction. H-LSG RMSE rises to 0.387 m and the matched-18 global model reaches 0.416 m, compared with 0.179 m for the native global model.

The Burnett oracle comparison locates this degradation in the WSE pathway after the shared extent prediction. EXT agreement is 0.986 for the native global, H-LSG, and matched-18 global models. Because the WSE variants share the same EXT prediction, differences in their depth RMSE cannot originate from the EXT branch. In contrast, the O4 − O2 path difference increases from 0.056 m for the native global model to 0.304 m for H-LSG. Training O4 is also larger for H-LSG (0.360 m versus 0.115 m). Additional coefficient capacity improves HF reconstruction but makes the LF-to-HF regression problem harder to exploit in Burnett.

**Table 5. Burnett capacity control and oracle attribution for the 18 Group 1 maximum-surface test events, scored on the training wet-domain mask. RMSE, O2 − O1, and O4 − O2 are reported in meters; EXT agreement is dimensionless.**

| Model | WSE dimension | CSI | RMSE (m) | Test O2 − O1 (m) | Test O4 − O2 (m) | EXT agreement |
|---|---:|---:|---:|---:|---:|---:|
| Global (native) | 6 | 0.975 | 0.179 | 0.049 | 0.056 | 0.986 |
| H-LSG residual *k*-means | 18 | 0.975 | 0.387 | 0.009 | 0.304 | 0.986 |
| Global matched-18 | 18 | 0.972 | 0.416 | 0.004 | — | 0.986 |

EXT agreement is the fraction of wet-domain cells whose predicted binary extent (EXT emulation ≥ 0.5, with always-flowing cells forced wet) matches the HF binary extent at the 0.03 m threshold, averaged over the 18 held-out Burnett events. Because the EXT branch is trained separately from the WSE branch, changing the number of WSE modes does not alter it; the native global, H-LSG, and matched-18 models therefore share the same EXT prediction, and the identical agreement values are a construction check rather than three independent estimates.

Carlisle does not provide an exact matched-capacity test because the global maximum-surface EOF rank is limited by eight training events. H-LSG uses 13 WSE coefficients, whereas a request for 13 global modes realizes only eight. The max-rank global model removes the truncation contrast (O2 − O1 = 0.000 m) but increases wet-domain RMSE to 0.202 m. H-LSG reaches 0.094 m, compared with 0.112 m for the native 1-mode global model. Removing residual modes again returns H-LSG to the native global result. Carlisle therefore remains a rank-limited case in which residual coefficient stacking improves RMSE, but it cannot be used as an exact equal-dimension test of localization.

**Table 6. Carlisle capacity control for the Group 1 maximum-surface test event, scored on the training wet-domain mask. RMSE and O2 − O1 are reported in meters.**

| Model | Requested / realized WSE dimension | CSI | RMSE (m) | Test O2 − O1 (m) |
|---|---|---:|---:|---:|
| Global (native) | auto / 1 | 0.976 | 0.112 | 0.064 |
| H-LSG residual *k*-means | — / 13 | 0.976 | 0.094 | 0.005 |
| Global forced to 13 modes | 13 / 8 | 0.975 | 0.202 | 0.000 |
| H-LSG residual modes = 0 | — / 1 | 0.976 | 0.112 | 0.064 |

### 4.4. Approximation and Partition Sensitivities

The Chowilla inducing-point sweep shows that sparse-GP approximation can alter operational RMSE without changing the truncation contrast. With the 15-dimensional H-LSG representation, reducing the inducing-point floor to 2 increases RMSE to 0.244 m, whereas floors of 8 and 16 give 0.096 and 0.093 m, respectively. Using all 28 training events as inducing points reduces RMSE further to 0.073 m. O2 − O1 remains 0.013 m throughout because the EOF representation is unchanged.

Changing the number of zones produces a different but related pattern. Increasing from 2 to 6 zones raises the WSE dimension from 9 to 21 and progressively reduces O2 − O1 from 0.019 to 0.012 m. Operational RMSE moves in the opposite direction, from 0.087 to 0.103 m. The zone-count experiment therefore reinforces the distinction between HF representational capacity and predictability of the resulting coefficients from LF inputs.

**Table 7. Chowilla H-LSG inducing-point and zone-count sensitivities for the Group 1 maximum-surface test event, scored on the training wet-domain mask. RMSE and O2 − O1 are reported in meters.**

| Factor | Setting | WSE dimension | CSI | RMSE (m) | Test O2 − O1 (m) |
|---|---|---:|---:|---:|---:|
| Inducing-point floor | 2 | 15 | 0.947 | 0.244 | 0.013 |
|  | 8 | 15 | 0.990 | 0.096 | 0.013 |
|  | 16 (default) | 15 | 0.976 | 0.093 | 0.013 |
|  | 28 (= *n*<sub>train</sub>) | 15 | 0.983 | 0.073 | 0.013 |
| Zone count | 2 | 9 | 0.975 | 0.087 | 0.019 |
|  | 4 (default) | 15 | 0.976 | 0.093 | 0.013 |
|  | 6 | 21 | 0.975 | 0.103 | 0.012 |

A second Chowilla partition based on wet-cell correlation changes wet-domain CSI only slightly (Figure 7). CSI is 0.978 for wet-correlation zoning, compared with 0.976 for residual *k*-means and 0.974 for the native global model. RMSE is 0.094 m and O2 − O1 is 0.010 m. Because this is a single-fold sensitivity and the capacity differs across representations, it does not alter the matched-capacity conclusion.

**Table 8. Chowilla zoning sensitivity for the Group 1 maximum-surface test event, scored on the training wet-domain mask. RMSE and O2 − O1 are reported in meters.**

| Zoning | CSI | RMSE (m) | Test O2 − O1 (m) |
|---|---:|---:|---:|
| Global (none) | 0.974 | 0.088 | 0.057 |
| Residual *k*-means | 0.976 | 0.093 | 0.013 |
| Wet-correlation | 0.978 | 0.094 | 0.010 |

For Carlisle Max, residual-response clustering augmented with spatial coordinates produces a mean same-zone fraction of approximately 0.95 among each cell's eight nearest neighbors. The zones are therefore spatially coherent in that configuration, but the clustering algorithm itself remains response based and does not enforce geographic connectivity.

### 4.5. Sensitivity to the Scoring Domain

Chowilla is strongly affected by whether evaluation is restricted to the training wet domain. Under wet_train, H-LSG has CSI 0.976 and RMSE 0.093 m. Under all_cells, CSI falls to 0.390 and RMSE increases to 3.789 m for both H-LSG and the native global model. The LF model, by contrast, retains all-cell CSI 0.930 because its coarse simulation already covers a large inundation footprint.

The extent maps in Figure 1 show that many of the additional errors occur in HF-wet cells outside the category-based wet index used to construct the LSG training domain. The all-cell result therefore reflects a mismatch between the training/scoring domains as well as model behavior. Reporting both domains makes this dependence explicit and prevents wet-domain performance from being interpreted as full-domain skill.

### 4.6. CRPS-Based Uncertainty Calibration

Table 9 and Figure 8 compare probabilistic scores before and after variance rescaling. Carlisle Max has a fitted scale *s* = 0.417. CRPS decreases from 0.039 to 0.028 m and active 90% coverage moves from 0.990 to 0.966, closer to the nominal 0.90 level. Burnett shows a smaller but consistent improvement: CRPS decreases from 0.133 to 0.127 m and active coverage from 0.943 to 0.890.

Chowilla does not benefit from the same scalar adjustment. In the saved-state rescore, *s* = 0.419, CRPS remains 2.155 m, and active 90% coverage decreases from 0.334 to 0.287. The calibration is therefore neutral in CRPS and adverse in coverage for this fold. Because variance scaling leaves the predictive mean unchanged, all reported CSI and RMSE values are unchanged by construction.

**Table 9. CRPS variance scaling and selected probabilistic scores.** CRPS is evaluated on the full non-padded cell domain including dry cells; coverage is reported as a fraction on the active-cell scoring domain (cells wet in the HF reference or in the predicted latent mean); point scores are unchanged by construction because variance scaling leaves the predictive mean unchanged. Because CRPS includes dry cells, it should not be compared directly with the wet-domain point RMSE in Tables 2–8. The Chowilla and Burnett before/after pairs are independent rescores of saved H-LSG model states; the original workflow-fit variance scales were 0.309 for Chowilla and 0.606 for Burnett.

| Case / surface | *s* | CRPS (m; uncalibrated → calibrated) | Active 90% coverage (uncalibrated → calibrated) | Point CSI / RMSE (m) |
|---|---:|---|---|---|
| Carlisle Max | 0.417 | 0.039 → 0.028 | 0.990 → 0.966 | Unchanged (CSI 0.976; RMSE 0.061 m, full mesh) |
| Carlisle TS | 0.900 | ≈0.017 | — | Unchanged |
| Chowilla H-LSG Max (rescore) | 0.419 | 2.155 → 2.155 | 0.334 → 0.287 | Unchanged (CSI 0.976; RMSE 0.093 m, wet domain) |
| Burnett H-LSG Max (rescore) | 0.604 | 0.133 → 0.127 | 0.943 → 0.890 | Unchanged (CSI 0.975; RMSE 0.387 m, wet domain) |

The Carlisle reliability diagram in Figure 8 is strongly bimodal. About 63% of cells have P(h ≥ τ) < 0.05 with an observed wet frequency of 0.004, whereas about 35% have P > 0.95 with an observed frequency of 0.99, and only 1.5% of cells (8,936 of 581,061) fall in the intermediate range 0.5 < P < 0.95. This thin fringe is systematically overconfident about wetness: its observed wet frequency is 0.62 overall and 0.29–0.33 in the 0.6–0.9 probability bins. In those 0.6–0.9 bins, roughly 70% of cells are false-alarm boundary cells for which the surrogate predicts shallow inundation (mean depth 0.07–0.21 m) while the HF reference is dry. Because these cells have latent means above τ, variance rescaling moves their probabilities toward one rather than toward the observed frequency, which is why the calibrated curve in Figure 8a retains the intermediate-probability dip. Figure 8b shows where the responsible cells sit: the fringe forms a narrow band along the wet-dry boundary and is dominated by false-alarm cells (surrogate wet, HF dry), i.e., the probabilistic counterpart of the extent over-prediction in Figure 1. The largest fringe bin (0.8–0.9) contains 2,971 cells, whereas the 0.6–0.7 bin contains only 15; the local nonmonotonicity should therefore not be interpreted as a fully resolved reliability curve.

The fitted scale itself is stable under the nested checks that were performed. Chowilla leave-one-training-event-out validation gives *s* = 0.310 ± 0.007 (range 0.298–0.324) around the full-training workflow value of 0.309. Carlisle gives *s* = 0.418 ± 0.031 around the full-training value of 0.417. These results indicate that the Chowilla null result is not explained by a highly unstable scalar estimate, although they do not establish transferability across sites. Burnett nested validation was not performed.

## 5. Discussion

### 5.1. What the Capacity Controls Change

At native capacity, residual H-LSG produces a substantially smaller O2 − O1 truncation contrast than the global model on Chowilla and Burnett. Without an equal-capacity comparison, that result could be interpreted as evidence that localization captures spatial structure missed by the global EOF basis. The matched controls change that interpretation. On Chowilla, increasing the global basis from 3 to 15 modes reduces O2 − O1 below the H-LSG value and yields the lowest wet-domain RMSE. On Burnett, increasing the global basis from 6 to 18 modes reproduces the truncation reduction but also reproduces the deterioration in end-to-end RMSE. For Chowilla, disabling the residual modes returns H-LSG to the native global result; the same behavior is observed for Carlisle in Table 6.

For Chowilla and Burnett, these results indicate that O2 − O1 is more strongly controlled by retained HF representation capacity than by whether that capacity is allocated globally or through residual zones. This is expected because O2 uses true HF coefficients: adding either global or residual modes expands the subspace available to reconstruct the held-out HF field. The operational prediction problem is different. Every additional coefficient must be inferred from LF information, and that mapping can become more difficult as the representation is expanded.

Burnett makes this distinction particularly clear. The shared EXT prediction is unchanged across the relevant models, whereas the O4 − O2 contrast increases from 0.056 m for the native global model to 0.304 m for H-LSG. The additional residual modes improve HF expressibility but are not predicted with comparable skill from the LF state. The matched-18 global model shows that the deterioration in end-to-end prediction is not unique to the residual partition: increasing representation capacity can also reduce operational skill in the global model.

Carlisle provides an important qualification. H-LSG improves wet-domain RMSE relative to the native global model, while the global basis cannot be expanded to the same 13-dimensional representation because only eight maximum-surface training events are available. The max-rank global control performs worse, not better. The present evidence therefore does not support a general statement that residual localization is ineffective. It supports the narrower conclusion that the apparent truncation advantage of H-LSG on Chowilla and Burnett cannot be attributed to localization without capacity matching, while Carlisle remains unresolved under an exact equal-dimension test.

### 5.2. Where Multi-Fidelity LSG Provides Skill

The largest LF-to-LSG improvements occur on Chowilla and Burnett: Burnett increases from wet-domain CSI 0.853 for LF to 0.975 for the native global LSG while RMSE decreases from 0.989 to 0.179 m, and Chowilla shows a similarly large reduction in wet-domain depth error. Carlisle begins from a stronger LF baseline, so the incremental gains are smaller.

The O1–O4 results help explain why a low truncation error should not be used as a surrogate for operational performance. On Chowilla and Burnett, O3 is much larger than O2, indicating that direct LF projection does not reproduce the HF coefficients well even when the HF basis itself is expressive. Gaussian-process learning then recovers a large fraction of that discrepancy. Model quality therefore depends on the joint behavior of the spatial basis and the LF-to-HF coefficient mapping. A spatial decomposition that improves one stage can still reduce end-to-end performance if it makes the regression problem harder.

The inducing-point sweep reinforces this point. Chowilla H-LSG RMSE changes from 0.244 to 0.073 m across the tested inducing budgets while O2 − O1 is fixed at 0.013 m. Comparisons of different coefficient dimensions should therefore control the SGPR approximation budget. Otherwise a low inducing budget can be mistaken for a failure of the spatial decomposition itself.

### 5.3. Evaluation Domain and Probabilistic Calibration

Chowilla shows that the scoring domain is not a minor reporting choice. The same LSG-Max prediction has wet-domain CSI near 0.98 and all-cell CSI of 0.39. This contrast reflects the restrictive trained extent domain together with model errors outside that domain, where many HF-wet cells are absent from the category-based wet index. Neither score is sufficient on its own: wet_train describes performance on the intended trained domain, whereas all_cells tests whether that domain restriction hides errors elsewhere. Both should be reported when the LF extent already covers a large area or when the trained extent mask is restrictive.

The uncertainty results are similarly case dependent. A scalar variance reduction is effective when the reconstructed posterior is broadly over-dispersed, as in Carlisle Max, and it also modestly improves Burnett. Chowilla remains poorly calibrated under the same class of adjustment. A single global scale can correct overall spread but cannot repair structural errors in the predictive mean, spatially varying variance bias, or extent-domain mismatch. For Carlisle, the leave-one-training-event-out estimates are stable around the fitted scale of 0.417. For Chowilla, the nested estimates are stable around the original workflow value of 0.309, but this check does not directly establish the stability of the saved-state rescore optimum of 0.419. Burnett was not evaluated with the same nested check. More flexible calibration may be useful, but the present results do not support assuming that a scalar CRPS adjustment transfers across sites.

The Carlisle reliability diagram adds a diagnostic dimension to this point. In the 0.6–0.9 probability bins, the intermediate-probability fringe is strongly biased toward false-alarm boundary cells: the surrogate mean lies above τ while the HF reference is dry. For these false-alarm cells, the latent mean already exceeds τ; reducing the variance therefore pushes *P*(*h* ≥ τ) toward one rather than correcting the dry HF outcome. Variance rescaling can adjust spread but cannot remove this mean-side boundary error. Scalar CRPS-based calibration is therefore a spread correction, whereas the residual dip in Figure 8a and the false-alarm fringe in Figure 8b indicate a mean-side wet-dry boundary error. Correcting that feature would require changes to the predicted mean or to the coupling between extent and reconstructed depth, for example through localized bias correction near the wet-dry boundary. The same analysis indicates how such diagrams should be read in data-poor settings: with only 15 cells in the 0.6–0.7 bin, local variation in that part of the reliability curve should not be interpreted as stable structure; the more defensible signal is the observed-frequency deficit across the populated intermediate-probability bins. This is a practical caveat for flood-mapping products that attach confidence intervals to surrogate predictions.

### 5.4. Relation to Previous LSG and Regionalization Studies

The results complement rather than replace earlier LSG developments. Fraehr et al. (2024a) compared LSG with several machine-learning surrogates and evaluated extrapolation across the same public benchmark family; the present study keeps the published split fixed and focuses on how LSG representation capacity is allocated. Fraehr et al. (2024b) addressed a different resource constraint by selecting HF training events. These studies address distinct resource-allocation questions: one concerns which events should be simulated at high fidelity, whereas the present study concerns how the spatial information from those events is represented.

These controls apply specifically to the formulation tested here. Tan et al. (2025) retrained LSG over focus subdomains, whereas H-LSG uses a simultaneous global-plus-residual representation over the whole domain. Wang et al. (2025) used rotated EOFs rather than residual hierarchical modes, and satellite-derived flood-extent methods address a different prediction setting (Chang et al., 2020, 2023; Markert et al., 2026; Wan et al., 2025). They therefore do not establish that geographic localization or rotated decompositions are ineffective in general.

Wang et al. (2026) identified zonal EOF analysis as a potential extension for large complex floodplains. The results here refine that suggestion by showing what must be controlled in such a test. If a zonal model retains more coefficients than its global comparator, a reduction in truncation error is not sufficient evidence of a localization benefit. A matched-capacity global model, together with a regression-capacity check such as the inducing-point sensitivity used here, provides a more informative baseline. The contribution of the present study lies in this controlled comparison, the ordered dual-path oracle diagnosis, and calibrated LSG uncertainty, rather than in introducing spatial localization, LSG error decomposition, or probabilistic flood surrogates per se.

### 5.5. Limitations and Future Work

Several limitations constrain these conclusions. First, the capacity-controlled analysis is based mainly on Group 1 maximum-inundation evaluations. Full time-series capacity controls were not performed for Chowilla or Burnett because of memory requirements. The results should therefore not be extrapolated quantitatively to time-series training at those sites. Second, capacity matching equalizes the WSE representation and GP input dimension, but it does not make every kernel, noise, regularization, and optimization degree of freedom identical. The conclusion is that the native reduction in H-LSG truncation error cannot be attributed uniquely to localization under the tested controls, not that every possible capacity confound has been removed.

Third, the residual-response zones are not hydrologically constrained. Spatial coordinates produce strong local coherence in the Carlisle diagnostic, but the method remains a response-feature clusterer rather than a watershed or adjacency-based partition. Connectivity-constrained zoning could behave differently. Fourth, O1–O4 is an ordered counterfactual ladder, not an additive variance decomposition, so individual contrasts should not be interpreted as unique causal shares of total error.

The number of independent held-out events is also uneven. Carlisle and Chowilla each provide one maximum-surface test event in Group 1, whereas Burnett provides 18. The reported differences are therefore controlled comparisons on published splits rather than population-level significance estimates. In addition, all accuracy measures use HF simulations as the reference; neither LF nor HF fields are independently validated here against observed flood depth or extent. The stability of the scalar variance factor was examined by leave-one-training-event-out checks for Carlisle and Chowilla only; the corresponding nested calibration check was not performed for Burnett.

Finally, the evidence is restricted to the public Carlisle, Chowilla, and Burnett cubes. Licensed Brisbane data and other benchmark families are outside the present replication set, the machine-learning baselines of Fraehr et al. (2024a) are cited rather than re-trained, and training-event reselection is not included because the published splits are held fixed. Future work should test connectivity-aware localization and full time-series capacity controls on additional public sites and should examine whether variance calibration can be made spatially adaptive without compromising the interpretability of the GP uncertainty.

## 6. Conclusions

This study tested residual hierarchical zoning in multi-fidelity LSG flood surrogates using capacity-matched controls, an O1–O4 oracle error ladder, and CRPS-based uncertainty calibration on three public benchmark cases. The controls change the interpretation of the native zoning results. On Chowilla, a global model with the same 15-dimensional WSE representation as H-LSG achieves lower wet-domain RMSE (0.085 versus 0.093 m) and a smaller truncation contrast (0.002 versus 0.013 m). On Burnett, both residual H-LSG and a matched 18-mode global model reduce truncation error but worsen end-to-end RMSE relative to the native 6-mode global model. For Burnett H-LSG, the oracle analysis locates the additional degradation in the LF-to-HF WSE mapping rather than in the shared extent prediction.

Carlisle is different because eight maximum-surface training events cap the realizable global EOF rank below the 13-dimensional H-LSG representation. Residual stacking improves RMSE in that setting, so the three cases do not support a universal statement for or against localization. They do show that an apparent truncation advantage should not be interpreted as a localization effect unless representation capacity is controlled.

On Chowilla and Burnett, the largest predictive gains arise from the multi-fidelity LSG mapping rather than from zoning, while Carlisle begins from a stronger LF baseline and shows smaller incremental gains. The results also show that sparse-GP approximation can materially affect higher-dimensional variants and that scoring-domain choice can dominate reported extent skill. Scalar variance calibration improves probabilistic performance for Carlisle Max and Burnett H-LSG Max, while the Chowilla rescore is neutral in CRPS and adverse in active coverage.

For localized EOF flood surrogates, the practical implication is to compare against a capacity-matched global basis, report the regression approximation budget, separate representation error from LF-to-HF mapping error, and evaluate uncertainty and scoring domains explicitly. Under the controls tested here, residual hierarchical zoning is better interpreted as one possible representation strategy than as an inherent source of accuracy improvement.

## 7. Open Research

Public multi-fidelity HF/LF cubes are available from Fraehr (2024), DOI 10.26188/24312658 (CC BY 4.0). Workflow configurations, evaluation summaries, figure exports, and code used for the analyses are archived at https://github.com/Coucou2016/lsg-flood-surrogate-benchmark. The upstream Hybrid LSG reference code is available at https://github.com/nfraehr/Hybrid_LSG_model. The Brisbane TUFLOW/URBS data used by Wang et al. (2026) are license restricted and are not redistributed with this study.

## 8. Author Contributions

[CRediT roles to be finalized and agreed by the author team before submission.]

## 9. Conflict of Interest

[Conflict-of-interest statement to be finalized by the author team before submission.]

## 10. Acknowledgments

[Acknowledgments and funding disclosures to be finalized by the author team before submission.]

## References

Bennett, N. D., Croke, B. F. W., Guariso, G., Guillaume, J. H. A., Hamilton, S. H., Jakeman, A. J., Marsili-Libelli, S., Newham, L. T. H., Norton, J. P., Perrin, C., Pierce, S. A., Robson, B., Seppelt, R., Voinov, A. A., Fath, B. D., & Andreassian, V. (2013). Characterising performance of environmental models. *Environmental Modelling & Software*, 40, 1–20. https://doi.org/10.1016/j.envsoft.2012.09.011

Chang, C.-H., Lee, H., Kim, D., Hwang, E., Hossain, F., Chishtie, F., Jayasinghe, S., & Basnayake, S. (2020). Hindcast and forecast of daily inundation extents using satellite SAR and altimetry data with rotated empirical orthogonal function analysis: Case study in Tonle Sap Lake Floodplain. *Remote Sensing of Environment*, 241, 111732. https://doi.org/10.1016/j.rse.2020.111732

Chang, C.-H., Lee, H., Do, S. K., Du, T. L. T., Markert, K., Hossain, F., Ahmad, S. K., Piman, T., Meechaiya, C., Bui, D. D., Bolten, J. D., Hwang, E., & Jung, H. C. (2023). Operational forecasting inundation extents using REOF analysis (FIER) over lower Mekong and its potential economic impact on agriculture. *Environmental Modelling & Software*, 162, 105643. https://doi.org/10.1016/j.envsoft.2023.105643

Donnelly, J., Abolfathi, S., Pearson, J., Chatrabgoun, O., & Daneshkhah, A. (2022). Gaussian process emulation of spatio-temporal outputs of a 2D inland flood model. *Water Research*, 225, 119100. https://doi.org/10.1016/j.watres.2022.119100

Eilander, D., Fraehr, N., Leijnse, T., & de Goede, R. (2025). Surrogate flood models for compound flood risk assessments and early warning. EGU General Assembly 2025, abstract EGU25-5209. https://doi.org/10.5194/egusphere-egu25-5209

Eilander, D., de Goede, R., Leijnse, T., & Fraehr, N. (2026a). Hybrid surrogate modeling of compound flood events using SFINCS-LSG. EGU General Assembly 2026, abstract EGU26-11062. https://doi.org/10.5194/egusphere-egu26-11062

Eilander, D., de Goede, R., Leijnse, T., & Fraehr, N. (2026b). SFINCS-LSG dataset, model files, python environment and scripts (Version v1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20352880

Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2022). Upskilling low-fidelity hydrodynamic models of flood inundation through spatial analysis and Gaussian process learning. *Water Resources Research*, 58(8), e2022WR032248. https://doi.org/10.1029/2022WR032248

Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2023a). Development of a fast and accurate hybrid model for floodplain inundation simulations. *Water Resources Research*, 59(6), e2022WR033836. https://doi.org/10.1029/2022WR033836

Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2023b). Supercharging hydrodynamic inundation models for instant flood insight. *Nature Water*, 1(10), 835–843. https://doi.org/10.1038/s44221-023-00132-2

Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2024a). Assessment of surrogate models for flood inundation: The physics-guided LSG model vs. state-of-the-art machine learning models. *Water Research*, 252, 121202. https://doi.org/10.1016/j.watres.2024.121202

Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2024b). Generation and selection of training events for surrogate flood inundation models. *Journal of Environmental Management*, 373, 123570. https://doi.org/10.1016/j.jenvman.2024.123570

Fraehr, N. (2024). Surrogate flood model comparison – Datasets and python code [Data set]. The University of Melbourne. https://doi.org/10.26188/24312658

Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378. https://doi.org/10.1198/016214506000001437

Kohanpur, A. H., Saksena, S., Dey, S., Johnson, J. M., Riasi, M. S., Yeghiazarian, L., & Tartakovsky, A. M. (2023). Urban flood modeling: Uncertainty quantification and physics-informed Gaussian processes regression forecasting. *Water Resources Research*, 59(3), e2022WR033939. https://doi.org/10.1029/2022WR033939

López-Lopera, A. F., Idier, D., Rohmer, J., & Bachoc, F. (2022). Multioutput Gaussian processes with functional data: A study on coastal flood hazard assessment. *Reliability Engineering & System Safety*, 218, 108139. https://doi.org/10.1016/j.ress.2021.108139

Lu, J., Wang, Q. J., Fraehr, N., Xiang, X., & Wu, X. (2025). Choice of Gaussian Process kernels used in LSG models for flood inundation predictions. *Journal of Hydrology*, 655, 132949. https://doi.org/10.1016/j.jhydrol.2025.132949

Markert, K. N., Lee, H., Williams, G. P., Nelson, E. J., Ames, D. P., Griffin, R. E., & Meyer, F. J. (2026). Evaluating the feasibility of scaling the FIER framework for large-scale flood inundation prediction. *Hydrology and Earth System Sciences*, 30(2), 459–484. https://doi.org/10.5194/hess-30-459-2026

Siripatana, A., Wilson, A. L., & Beevers, L. (2025). Uncertainty quantification for multi-input fluvial flood inundation using GPR- and PCE-based surrogates. *Water Resources Research*, 61(10), e2024WR039668. https://doi.org/10.1029/2024WR039668

Tan, Z., Xu, D., Taraphdar, S., Ma, J., Bisht, G., & Leung, L. R. (2025). An efficient hybrid downscaling framework to estimate high-resolution river hydrodynamics. *Hydrology and Earth System Sciences*, 29(16), 3833–3852. https://doi.org/10.5194/hess-29-3833-2025

Wan, H.-H., Lee, H., Thuy Du, T. L., Rostami, A., Chang, C.-H., Markert, K. N., Nelson, E. J., Williams, G. P., Li, S., Straka, W., Helfrich, S. R., & Meyer, F. J. (2025). An interpretable and scalable model for rapid flood extent forecasting using satellite imagery and machine learning with rotated EOF analysis. *Environmental Modelling & Software*, 192, 106562. https://doi.org/10.1016/j.envsoft.2025.106562

Wang, R., Lian, J., Yuan, X., Tian, F., Li, K., & Liu, Z. (2025). Rapid simulation of floods by considering the spatial and temporal characteristics of inundation. *International Journal of Disaster Risk Science*, 16(3), 481–495. https://doi.org/10.1007/s13753-025-00642-5

Wang, W., Wang, Q. J., & Nathan, R. (2026). Strategies for predicting flood inundation in a large and complex floodplain based on low-fidelity hydrodynamic models. *Water Resources Research*, 62(5), e2025WR042481. https://doi.org/10.1029/2025WR042481

Zanchetta, A. D. L., & Coulibaly, P. (2022). Probabilistic forecasts of flood inundation maps using surrogate models. *Geosciences*, 12(11), 426. https://doi.org/10.3390/geosciences12110426

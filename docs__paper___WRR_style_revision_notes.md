# WRR-style manuscript revision notes

## Scope

This revision is a writing- and organization-focused edit. It preserves the study's scientific direction, benchmark cases, numerical results, uncertainty findings, capacity-control interpretation, and stated limitations. No new experiment, metric, citation, or numerical result has been invented.

The editorial target was the organization and prose rhythm of Wang et al. (2026), *Water Resources Research*, while avoiding close imitation of its sentences. The revision also applies Academic Phrasebank principles for reporting results, cautious interpretation, and discussion, together with common "humanizer" checks for formulaic AI prose.

## Main editorial changes

1. **Shortened the title.** The original title attempted to carry the research question, result, diagnostic framework, uncertainty method, and data scope at once. The revised title foregrounds the main scientific contribution: a capacity-controlled evaluation of residual hierarchical zoning.

2. **Rebuilt the Introduction as one argument.** The former Introduction and separate "Related work and novelty boundary" section were merged. The new flow is:
   - computational motivation;
   - LSG lineage;
   - localization literature;
   - capacity confounding;
   - diagnostic and uncertainty gaps;
   - study design and bounded conclusion.

   This is closer to the Wang et al. article, which develops the problem, literature, gap, and objectives in a single Introduction rather than using a separate novelty-defense section.

3. **Removed report-like research-question scaffolding.** The four RQ labels were converted into prose objectives. The questions remain scientifically intact, but the manuscript now reads as a research article rather than a project brief.

4. **Reorganized Methods around the modeling logic.** The revised sequence is LSG formulation → EXT+WSE reconstruction → residual hierarchy → sparse GP → oracle ladder → uncertainty calibration → metrics. Internal implementation names are minimized in running prose.

5. **Merged data and experimental design.** The public benchmark description, split definitions, capacity controls, sensitivity experiments, statistical unit, and software stack now form one coherent section.

6. **Reduced Results from eleven small subsections to six substantive result units.** Spatial evidence is presented first, followed by oracle budgets, capacity controls, approximation/partition sensitivities, scoring-domain sensitivity, and uncertainty calibration. Each subsection follows a location/summary/highlight pattern rather than repeatedly announcing what a figure "shows."

7. **Renumbered tables in order of appearance.**
   - old Table 1 → new Table 1
   - old Table 2 → new Table 2
   - old Table 3 → new Table 3
   - old Table 6 → new Table 4
   - old Table 7 → new Table 5
   - old Table 9 → new Table 6
   - old Table 8 → new Table 7
   - old Table 5 → new Table 8
   - old Table 4 → new Table 9

8. **Rewrote the Discussion as evidence-led discussion cycles.** Each section now starts from a finding, explains the mechanism or interpretation, qualifies it, and relates it to prior work. This replaces headings such as "Central advance," "Rival explanations and risks," and "Open questions," which read more like review notes than journal prose.

9. **Converted the nine-item Limitations list into a journal-style limitations/future-work subsection.** Every substantive limitation is retained, but the presentation is less checklist-like.

10. **Reduced defensive/meta language.** Phrases such as "honest cell-scatter," "not a silent success," "not an extent-gate story," "anti-cases," "horse-race," "defensible novelty," and repeated "we do not claim" constructions were replaced by direct statements of scope and evidence.

11. **Reduced typographic AI markers.** In the manuscript body, bold-emphasis spans and em-dash use were reduced sharply. Bold is now largely limited to manuscript metadata and table captions rather than used to steer the reader sentence by sentence.

12. **Added WRR/AGU front matter.** Three Key Points were added and kept below AGU's 140-character limit. Keywords were reduced to six. The revised Abstract is about 207 words and remains a single paragraph.

13. **Removed internal appendices from the submission draft.** The terminology ledger, figure/table inventory, and scope-boundary project notes are useful for the research workspace but are not appropriate as submission appendices. Their substantive scientific content is already incorporated into Methods and Limitations.

## Quantitative style change

Approximate body-text diagnostics:

| Metric | Original | Revised |
|---|---:|---:|
| Body words before references | 7,635 | 6,979 |
| Level-3 subsections | 29 | 20 |
| Em dashes | 45 | 4 (all remaining are table missing-value marks) |
| Bold-emphasis spans | 119 | 13 |
| Longest prose sentence (rough) | 114 words | 45 words |
| Mean prose sentence length (rough) | 21.1 words | 18.5 words |

The goal was not simply to shorten the manuscript. Most of the reduction comes from repeated qualification, internal workflow language, and duplicated interpretation. Space was reallocated to a more continuous Introduction and a fuller evidence-based Discussion.

## Items intentionally preserved

- All headline CSI/RMSE values.
- Chowilla matched-15 result: RMSE 0.085 m and O2-O1 0.002 m.
- Burnett native/H-LSG contrast: RMSE 0.179/0.387 m and O4-O2 0.056/0.304 m.
- Carlisle rank-limited qualification.
- Inducing-point and zone-count sensitivity values.
- Chowilla wet-domain/all-cell contrast.
- CRPS calibration values and the Chowilla null/adverse outcome.
- Nested scale-factor stability for Carlisle and Chowilla.
- Public-data scope and Brisbane licensing boundary.
- The non-additive, path-ordered interpretation of O1-O4.
- The distinction between HF-simulation emulation and validation against observations.

## One non-prose issue to fix in the paper-generation pipeline

The supplied PDF repeats the study-domain Figure 1 under later Results subsections where the uncertainty and zoning figures should appear. This looks like a figure-insertion/build issue rather than a manuscript-text problem. The revised Markdown does not attempt to repair the figure pipeline.

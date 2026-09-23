# SPB Review Paper — Path to Submission-Ready

**Target changed 2026-09-17: IEEE Open Journal of Power Electronics (OJPEL)**,
not TTE. OJPEL page policy (per official Sept-2025 guidelines PDF): **10 pages
body content, excluding references and bios**, +4 more pages allowed with a
justification statement at submission (so realistically ~14 body pages), *no*
overlength charges. This is more generous than TTE's 12-pages-including-refs
cap (our refs run ~3 pages, so real body budget goes from ~9 pages under TTE to
~10-14 under OJPEL). Tradeoff: OJPEL is fully open-access, ~$2160 APC (~20%
off with a PELS-member author, discounts don't stack). Same double-column
IEEEtran/"Transactions" template, no reformatting needed. OJPEL explicitly
welcomes "tutorial and survey articles."

Current state (2026-09-17): 14 pages total (~11 body + ~3 refs) — already fits
OJPEL's base 10+4 body budget without further trimming. Given the relaxed
budget, the author asked to ADD content: a per-section waveform figure or two
(dc-link balancing waveform, carrier-interleaving ripple reduction) and a new
section on common-mode voltage (CMV) effects. In progress — see below.

Historical target (superseded, kept for context): IEEE Transactions on
Transportation Electrification (TTE), review paper, ≤ 12 pages including
references, double-column, IEEEtran. Source: IEEE Editorial Style Manual for
Authors + TTE Author Guidelines (10-2024), both supplied by the author.

Current state (as of 2026-09-15): 15 pages compiled. Editorial review pass #1 done;
mechanical LaTeX hygiene pass #1 done; content softening pass #1 done (dropped
case-study/EMC-section promises, deduped a paragraph, fixed acronym first-use,
fixed cross-refs). Not yet done: page-budget compliance, abstract/keyword
compliance, per-section visualization, final IEEE-style compliance pass, final
compile + page count check.

**Working method:** go section by section (per author's instruction). For each
section: ieee-editor review against IEEE style rules below -> ieee-writer fixes
content/prose (tightening for page budget, no repetition) -> figure-generator adds
one well-designed native (TikZ/pgfplots) figure where the section lacks
visualization and one would genuinely help -> latex-source-editor mechanical
cleanup -> move to next section. Full-paper pdf-builder compile + page-count check
after each 2-3 sections, and a final full pass at the end.

## A. Global IEEE/TTE compliance (do once, paper-wide)

- [x] **Abstract**: was 224 words, now 199 (TTE limit: "not more than 200 words").
      Single paragraph, no numbered citations/equations preserved.
- [x] **Index Terms / keywords**: was 9, trimmed to the TTE-allowed 5: "Electric
      vehicles, integrated motor drives, modular converters, multiphase machines,
      stacked polyphase bridge (SPB) converters." Dropped GaN/SiC/wide-bandgap
      semiconductors/traction inverter to fit the limit — flagged to the author,
      revisit if a different 5 are preferred.
- [ ] **Page budget**: the build was actually broken the whole time (missing
      `jabbrv` package files — now fixed, see below) so the "15 pages" baseline
      was from a corrupted bibliography, not a real number. With a clean build,
      the true baseline is **17 pages**, and the target is **≤12**. That's a 5-page
      cut needed, in direct tension with "add more figures." See chat for the
      author's call on how to balance this.
- [x] **Fixed the build**: `\bibliographystyle{jabbrv_IEEEtran}` needs
      `\usepackage{jabbrv}` plus `jabbrv.sty`/`jabbrv-ltwa-all.ldf`/
      `jabbrv-ltwa-en.ldf` sitting in the repo root (not available via MiKTeX's
      package manager — downloaded from the upstream compholio/jabbrv GitHub repo
      instead, per that project's own no-install-needed instructions). Also fixed
      a missing `}` and 6 unescaped `&` in `ref.bib`. Compiles clean now, 0 bibtex
      warnings, 0 undefined references.
- [x] **Corresponding author**: added "(Corresponding author: Enes Ayaz.)" plus
      e-mail (enesa@kth.se) in the `\thanks` block. Postal address/phone are
      submission-portal-only per IEEE guidance, not needed in the PDF.
- [ ] **Unused bibliography clusters**: ~12 EMC/insulation refs and ~9
      MMC/multilevel-balancing refs in `ref.bib` are cited nowhere (leftover from
      the dropped case-study/EMC sections). Harmless for the compiled PDF (BibTeX
      only prints cited entries) but dead weight in the source — low-priority
      cleanup, decide at the end whether to prune `ref.bib`.
- [ ] **Sanity-check section auto-numbering**: file names skip "IX"/"XI"
      (historical), but LaTeX auto-numbers `\section{}` by input order, so the
      *compiled* numbering should already be sequential (I–XI or so) — confirm
      once compiled and check no section improperly hardcodes a Roman numeral
      that no longer matches.
- [ ] Final full-paper `ieee-editor` re-review once all sections are done, then
      final `pdf-builder` compile and page-count/warning check.

## B. Section-by-section pass

| # | Section | File | Figures now | Visualization plan |
|---|---|---|---|---|
| 1 | Introduction | `Sections/Section_I_Intro.tex` | 3 (motivation, Ron_sp vs. V, block diagram) | Likely fine as-is — confirm no redundancy, check abstract/intro alignment |
| 2 | Evolution of SPB | `Sections/Section_II_Evolution_SPB.tex` | 1 (new, `fig:spb_timeline`) | Done — native TikZ timeline of the 6 milestones already in Table `spb_validation` |
| 3 | Operating Principle | `Sections/Section_III_Operating.tex` | 0 (relies on Section I's block diagram) | Evaluate whether a dedicated schematic (e.g. series dc-path + per-cell winding ports) earns its space |
| 4 | Machine Integration | `Sections/Section_IV_Machine_Integration.tex` | 2 (Integration.png full-size + `fig:winding_options`) | Done — Table II's content folded into Fig 6's caption (per-panel advantage/consideration), Table II removed; subfloat side-by-side layout was tried first and rejected as ugly, reverted to single full-width figure |
| 5 | Modulation | `Sections/Section_V_Modulation.tex` | 2 (scheme2 PNG + new `fig:spb_modulation_taxonomy`) | Done — TikZ taxonomy grouping the 5 DOF from Table `spb_modulation_dof` by ripple/loss vs. CMV/balancing effect |
| 6 | DC-Link Balancing | `Sections/Section_VI_DCLink.tex` | 1 (new, `fig:spb_balancing_taxonomy`), table `spb_balancing_comparison` removed (duplicate) | Done — native TikZ taxonomy tree of the 3 approaches, colored, citations preserved in figure |
| 7 | Semiconductor Scaling | `Sections/Section_VII_Semiconductor.tex` | 1 merged `figure*` (cell-count PNG + pgfplots chart as subfloats a/b, one label `fig:cell_count_scaling`) | Done — Fig 10+11 merged, placed directly after Table V with connecting sentence; Table VI (`device_screening_metrics`) removed, its content folded into prose, 0 citations lost (had none) |
| 8 | Thermal | Deleted entirely (author's final call — the folded-in subsection added too little value) | `fig:electrothermal_loop` removed with it | Done — abstract and Section I roadmap updated to stop claiming "thermal behavior" coverage; thermal management now listed as an open research direction (Section XII) instead, which is accurate |
| 9 | Fault Tolerance | `Sections/Section_X_FaultTolerance.tex` | 1 (new, `fig:spb_fault_locations`) | Done — schematic mapping the 5 fault markers 1:1 onto Table `spb_fault_compact` rows |
| 10 | Future Directions | `Sections/Section_XII_Future.tex` | 0 | Condensed twice (~28% cut on 2nd pass); remaining subsections merged to one ("Cell Count, Reliability, and Cost Co-Design"); all citations kept |
| 11 | Conclusion | `Sections/Section_XIII_Conclusion.tex` | 0 | Not expected to need a figure |

Old/unused PNGs under `Figures/` (Evolution, DC-Link, Thermal, and other
leftover files like `SPB_intro.png`, `Modulation_scheme1.png`,
`IMMD_Hilpert2014.png`, `IMMD_Brown2007.png`, `SPB_machine_winding_options.png`,
`SPB_CellCount_Loss_Comparison_example.png`,
`SPB_CellCount_Semiconductor_Tradeoff.png`,
`Traction_Power_Voltage_Map_expanded.png`) are considered **not usable** per the
author — new visuals are native TikZ/pgfplots, not these files. Decide at the end
whether to delete the dead PNGs from the repo.

## C. Citation pass

- [ ] Confirm every non-trivial technical claim in each section has a `\cite{}` —
      spot-checked already for Sections VII/X during the first pass; do the same
      for the remaining sections during their individual passes.
- [ ] Confirm no "in reference [X]" phrasing anywhere (checked paper-wide already
      — none found; recheck after new prose is added).

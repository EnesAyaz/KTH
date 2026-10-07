# Revision notes — 1 October 2026

Edited the manuscript in C:\Github\KTH\Review-Paper-SPB and rebuilt main.pdf (17 total pages). The conclusion ends on page 13; acknowledgment and references begin on page 14. Count 14 pages conservatively for the body including acknowledgment.

## Implemented
- Added an honest narrative-review scope and distinguished direct SPB evidence from related IMMD research.
- Added a representative evidence/EV-validation table and an application-based design framework: variables, objectives, healthy/fault constraints, mission-energy boundary, fair benchmarks, and unfavorable SPB cases.
- Corrected carrier harmonics, binary switching-current normalization, RMS ripple definition, and source-network assumptions; corrected three-cell carrier phases.
- Corrected common-mode voltage references and separated matched-capacitance cancellation, static insulation stress, frame current, and bearing current.
- Added post-fault blocking-voltage feasibility; replaced arbitrary transient/current-derating curves with a vector feasibility diagram.
- Qualified machine dq steady-state assumptions and broad device/topology claims. Corrected GaN attribution in the integration table.
- Restored the original introductory radar illustration as Fig. 1 at the author's request; its caption explicitly identifies the scores as conceptual rather than measured.
- Updated AI assistance acknowledgment for the substantive assistance used in this revision.
- New/replacement figures are native TikZ/PGFPlots vectors in the corresponding section source. Legacy external figure files are retained but superseded figures are no longer included.

## Validation and remaining author checks
- All 118 original active citation keys retained. BibTeX and repeated pdfLaTeX builds pass; no undefined citations/references or overfull boxes in the final log. Revised pages visually checked.
- Wang2025GaNIMMD and Wang2025MWIMMD have identical DOI 10.1109/JESTPE.2023.3283538. Both keys/entries remain to honor reference preservation; consolidate this bibliographic duplicate before submission (no distinct publication would be lost).
- This pass is not an independent full-text audit of all 118 references or validation of every inherited simulation. Inherited external illustrations and small lettering still merit a final publication-size artwork audit; OJPEL specifies at least 8 pt.
- Authors should verify the substantive technical revisions and actual AI-use disclosure before submission. No experimental or automotive validation is claimed.

## Length policy and proposed exception motivation
Official September 2025 OJPEL guidelines: https://www.ieee-pels.org/wp-content/uploads/2025/09/OJPEL-Guidelines.pdf
Ten double-column pages excluding references/bios; up to four extra pages require detailed motivation at submission and editorial approval. Fourteen pages is an exception ceiling, not an unconditional allowance.

Suggested motivation: The review integrates SPB converter topology, machine winding requirements, modulation, common-mode excitation, dc-link stability, device scaling, and post-fault operation. The additional length supports the coupled analytical constraints, evidence-to-validation synthesis, and EV design framework needed to assess complete-drive feasibility, while preserving traceable primary-source coverage. We request approval for the manuscript length under the systems/topic exception.

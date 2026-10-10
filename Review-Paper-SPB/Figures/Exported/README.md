# Embeddable figures

The manuscript includes fig01.pdf through fig16.pdf using graphicx.
PDF is the preferred vector format for pdfLaTeX/Overleaf. PNG previews
are 300 dpi. SVG copies preserve vector paths for external editing.
Captions remain editable in the section source files.

Original drawings are retained in the project. To refresh assets after
editing them, compile the manuscript first, then run from the repository root:

    python Figures/Exported/export_figures.py --aux PATH_TO_MAIN_AUX

Recompile the manuscript afterward. Figure 4 contains numerical citations;
refresh the assets whenever bibliography numbering changes. Its original
citation keys are retained with nocite in the manuscript for BibTeX.

Exported PDFs are cropped to visible content. Figure-caption spacing is
controlled in main.tex with abovecaptionskip=2pt; per-figure negative vspace
is unnecessary. The natural drawing widths preserve the existing typography.

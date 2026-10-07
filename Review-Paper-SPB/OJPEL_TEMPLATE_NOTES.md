# OJPEL template migration

The active entry point remains `main.tex`; compile it in this folder with pdfLaTeX, BibTeX when references change, and two pdfLaTeX passes.

- `ieeeojpel.cls` and `ojpel-logo.png` are the exact user-supplied files. The class is unmodified.
- Main front matter now follows `ojpel.tex`: author affiliation/correspondence commands and abstract/keywords before maketitle; journal color and logo match the template.
- No sample authors, biographies, figures, DOI, publication dates, or funding were imported.
- A documented preamble patch suppresses the empty publication-history row (the supplied class otherwise prints `; revised .`). Remove this draft patch when IEEE assigns editorial metadata.
- Body text and references are preserved. Two small width adjustments accommodate narrower columns without reducing font size.
- The pre-migration main.tex and PDF are in `template-migration-backup`.
- The supplied class identifies itself internally as IEEEphot and generates header/footer box warnings; these are template artifacts. No margins, text height, font sizes, or line spacing were reduced to change the page count.
- MATLAB figure sources remain unchanged by this migration.

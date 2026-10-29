---
name: ieee-paper
description: The author's taste and standing rules for IEEE-format papers and similar technical documents (theses, reports, slides that reuse paper figures). Use whenever creating, restyling or exporting a figure, plot or diagram, building a table, or writing or editing paper text and captions. Covers figure size and aspect ratio, lettering, colour choice, export and LaTeX inclusion, and the writing rules on tables versus text, small numerical differences, abbreviations, cross-references, scope and language.
---

# IEEE paper style

These files describe how the author wants a paper to look and read. They are generic: nothing in them belongs to one project.

- [figures.md](figures.md) covers size and aspect ratio, lettering, lines, colour, export and LaTeX inclusion. Read it before making or changing any figure.
- [writing.md](writing.md) covers tables and text, small numerical differences, abbreviations, cross-references, scope and language. Read it before writing or editing text, tables or captions.

An explicit instruction from the author always wins over these files, and it holds for the rest of that paper. A project's own conventions (an existing style file, the template of the venue) win where they exist. These files are the default for everything else.

## The short version

**Figures**

1. Draw the figure at its printed size: 3.5 in wide for one column, 7.16 in for two columns, nothing in between. One column is the default.
2. Lettering is 8 pt in a Times face at printed size, never below 7 pt, and identical in all figures.
3. No default colours of the plotting tool. Colour has a stated job, means the same thing in every figure, and still works in greyscale.
4. Export as vector PDF with embedded fonts, at the figure size, without cropping.
5. Include with `width=\columnwidth` and nothing else. The caption is the title.
6. Look at the rendered result at printed size before showing it.

**Text and tables**

1. A number that is in a table is not repeated in the text. The text says what the numbers mean.
2. A difference of one or two percent between numerical results is usually no difference. Check it analytically, then report the quantities as equal.
3. An abbreviation is defined at its first use and never appears before that, in the abstract and again in the body.
4. Every figure and table is referred to in the text, and each sits within two pages of its first reference.
5. Plain language, the established terms of the field, and one name for one thing.

**Working with the author**

1. Do what was asked. Do not add analyses, metrics, figures or sections that were not requested. Suggest them in the reply instead.
2. What the author removed stays removed in every later version.
3. When the author says "show me first", the result does not go into the paper until they approve it.
4. When a check contradicts something the author believes, say so in one or two sentences with the reason, then follow their decision.

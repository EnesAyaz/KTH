# Figures

A figure is read at the size at which it is printed, usually in a column 3.5 inches wide, often in greyscale. Every rule below follows from that.

## 1. Size and aspect ratio

IEEE prints a figure at one of two widths.

| | Width | In LaTeX (IEEEtran) |
|---|---|---|
| One column | 3.5 in (88.9 mm) | `\columnwidth`, 252 pt |
| Two columns | 7.16 in (182 mm) | `\textwidth`, 516 pt, in `figure*` |

The largest allowed figure is 7.16 in by 8.8 in. There is no width in between and none narrower than a column.

**Draw at printed size.** Create the figure at exactly this width in the plotting tool and include it at exactly this width. Then 8 pt in the tool is 8 pt on paper. A figure drawn large and scaled down ends up with small lettering and hairlines.

**One column is the default.** A two-column figure takes a strip across the whole page. Use it only when panels must be compared side by side, or when the content cannot be read at one-column width. Content that fits one column but is spread over two looks empty. Try stacking the panels in one column first.

Heights that work:

| Content | Size (in) | Height / width |
|---|---|---|
| One axes | 3.5 × 2.2 | 0.63 |
| One axes with a legend below or many curves | 3.5 × 2.6 | 0.74 |
| Equal axes: phasor or space-vector diagram, locus, map | 3.5 × 3.2 | 0.9 |
| Two stacked axes with a common x axis | 3.5 × 3.2 | |
| Three stacked axes with a common x axis | 3.5 × 4.3 | |
| Timing diagram or waveform strips | 3.5 × (0.4 + 0.35 to 0.6 per row) | |
| Row of two to four panels, two columns | 7.16 × 2.2 to 2.8 | |
| Grid of panels, two columns | 7.16 × (0.5 + 1.2 to 1.5 per row) | |

- A single axes is between 0.55 and 0.75 as high as it is wide.
- Each further stacked axes adds 1.0 to 1.2 in.
- Panels with a common axis show its tick labels once: on the bottom row and on the left column.
- Figures of the same kind have the same size throughout the paper.

## 2. Lettering

- **Typeface.** Times New Roman or a Times clone, to match the body text of an IEEE paper. One typeface for all figures of the paper.
- **Size.** 8 pt for axis labels, tick labels and legends. This is the caption size of IEEEtran and the lower end of what IEEE asks for (about 8 to 10 pt). Nothing below 7 pt at printed size, subscripts excepted.
- **When it does not fit.** If the lettering only fits below 7 pt, the figure holds too much. Split it or use two columns. Do not shrink the text.
- **Symbols.** Typeset as in the text: variables italic, units and descriptive subscripts upright, and the same symbol as in the paper's equations. Variable names from the code never appear in a figure.
- **Axis labels.** A word plus the symbol or unit: "Time (ms)", "Line voltage (V)". IEEE puts units in parentheses. If the paper already uses another convention, keep that one convention everywhere.
- **No title in the figure.** The caption is the title. Panels carry (a), (b), (c) or a short heading that names the case.
- **Labels sit beside what they name.** A component label goes next to the component, not next to a wire that leads to it. A curve label goes on or beside its curve. Text never crosses a line or other text.
- **Legend.** Use one only when direct labels do not fit. No box. Place it in an empty region, or put one shared legend below the panels. The entries use the words of the paper.
- **Ticks.** Few, at round values. Angles at multiples of 30°, 60° or 90°. The last tick label must not be cut off at the edge of the figure.

## 3. Lines and marks

| Element | Width |
|---|---|
| Data lines | 1.0 pt |
| Reference and secondary lines | 0.6 to 0.75 pt |
| Axes | 0.5 pt |
| Grid | 0.3 to 0.5 pt, light grey, behind the data |

- Lines thinner than 0.25 pt disappear in print.
- Markers are 3 to 4 pt. Use them on measured or sampled points, or to tell lines apart, not on every point of a dense curve.
- Axes are drawn on the left and bottom only, with ticks pointing outwards.
- Filled areas have no edge line, and the grid stays behind them.
- **Draw what is known analytically as a curve.** When the shape of a curve can be derived, plot the derived curve. A cloud of points picked out of a simulation looks random and raises questions. Simulated or measured points may go on top as markers to validate the curve.
- **Mark states with lines or bars, not scattered symbols.** An offset line or a bar above the data reads better than dots on the data.
- **Timing diagrams are drawn, not plotted.** Gate signals and switching states are shown as a clean diagram: one row per signal, filled blocks, labelled intervals, one time axis. Stacked raw traces are not a timing diagram.
- **A comparison shows everything that is compared.** All methods appear, on the same axes and scale, in the same order as in the tables and the text.

## 4. Colour

### Principles

1. **No defaults.** Never the default colours of the plotting tool, such as the MATLAB blue and orange or the matplotlib cycle. Never a rainbow colour map.
2. **Colour has a job, and the caption or legend states it.**
   - Identity, such as method or phase: different hues.
   - Two states of the same thing: one hue, dark for the stronger state and light for the weaker.
   - Polarity: two hues, one per sign.
   - Magnitude: one hue from light to dark.
3. **The encoding must be literally true.** If dark means "continuous", then only what really is continuous is dark. Check every panel against the definition in the legend before showing the figure.
4. **Same thing, same colour, in every figure of the paper.** One style file per paper holds the colours and every figure script reads it.
5. **It must survive greyscale print and colour-vision deficiency.** Series differ in lightness, and also in line style or marker. Label lines directly where possible.
6. **At most four colours plus black and grey in one axes.** More series go into separate panels.
7. **Black and grey are part of the palette.** The main or reference quantity is black. Envelopes, limits and context are grey.
8. **Avoid:** red against green as the only distinction, yellow or any light colour for lines on white, fully saturated primaries, coloured backgrounds, gradients, shadows and 3-D effects.
9. **No transparency.** Use the light tint of the colour instead. EPS cannot store transparency and print flattens it unpredictably.

### Default palette

Use the colours in this order.

| # | Name | Colour | Tint for fills and the weaker state |
|---|---|---|---|
| 1 | Ink | `#111111` | `#949494` |
| 2 | Teal | `#018789` | `#8DC9CA` |
| 3 | Wine | `#A41C59` | `#D699B4` |
| 4 | Ochre | `#C38714` | `#E4C995` |
| 5 | Indigo | `#392390` | `#A69CCD` |

| Grey | Colour | Use |
|---|---|---|
| Dark | `#52514E` | Axes, tick labels, secondary text |
| Mid | `#898781` | Reference lines, envelopes, limits |
| Light | `#E2E0DA` | Grid |

- Pair the colours with line styles in the same order: solid, dashed, dash-dotted, dotted.
- For two states of one quantity drawn as filled areas, use a dark and a light shade of one hue: `#0D5C6B` with `#96D0CE`, or `#922B3E` with `#EEB0B4`.
- Rename the colours in the project's style file by what they mean there, for example "forward" and "reverse".

Every pair of the five colours was checked by calculation, not by eye. Each pair is clearly different in normal vision, stays different under red-green colour-vision deficiency, and differs in lightness after greyscale conversion. Each colour has a contrast of at least 3:1 on white.

A different palette, for instance one imposed by a venue, must pass the same four tests for every pair that can meet in one axes:

| Test | Limit |
|---|---|
| Difference in normal vision, OKLab distance × 100 | at least 15 |
| Difference under simulated protanopia and deuteranopia | at least 8 |
| Difference in lightness after greyscale conversion, OKLab L × 100 | at least 8 |
| Contrast against white | at least 3:1 |

## 5. Export

- **Format.** Vector PDF for plots and diagrams. EPS only when the venue compiles with plain LaTeX. PNG at 600 dpi for images and for figures with thousands of filled patches, where a vector file becomes very slow. Never below 300 dpi. Never JPEG for a plot.
- **What IEEE accepts.** PS, EPS, PDF, PNG and TIFF. Line art needs more than 600 dpi and colour or greyscale images more than 300 dpi when they are not vector.
- **Fonts.** All fonts are embedded. Type 3 fonts are not allowed, because the IEEE PDF check rejects them. MATLAB's vector export embeds TrueType fonts. Matplotlib writes Type 3 by default, so set its PDF font type to 42.
- **No cropping.** Export at the size of the figure. A tight crop makes the file narrower than the column, and LaTeX then scales it back up. In a test, a 3.5 in figure cropped to 3.3 in and its lettering grew by 5 %, by a different amount in every figure.
  - In MATLAB, create the figure in inches at the printed size, use a compact layout, and export with the padding option that keeps the figure size.
  - In matplotlib, set the figure size in inches, use a constrained layout, and save without the tight bounding box.
- **Colour space and background.** RGB, on a white background that is not transparent.
- **Check a raster export.** Its pixel size must equal inches times dpi. A mismatch means the export was clipped, usually at the right or bottom edge.
- **One script regenerates every figure from the data.** No retouching by hand. File names are stable and descriptive. The file naming IEEE asks for at final upload is applied only then.
- **Drawings.** Circuits and block diagrams are vector as well, with the same typeface and sizes. Lettering in an imported drawing is redone when it is below 7 pt at printed size.

## 6. LaTeX

```latex
\begin{figure}[!t]
  \centering
  \includegraphics[width=\columnwidth]{figures/fig_name}
  \caption{What is plotted, at which operating point, and what each line style means.}
  \label{fig:name}
\end{figure}
```

- **Width.** `width=\columnwidth` for one column, `figure*` with `width=\textwidth` for two. No `scale`, no `height`, no fraction of the column width. If a figure is too tall, redraw it lower.
- **Placement.** `[!t]`. Not `[h]` and not `[H]`. A `figure*` appears at the top of a later page than its place in the source, so put it early.
- **Caption.** Below a figure, above a table. Sentence case, ending with a period. It must stand alone: it explains every colour and line style and uses only abbreviations that are already defined. It does not repeat the discussion in the text.
- **Label.** `\label` comes after `\caption`.
- **Reference.** `Fig.~\ref{fig:name}` and `Table~\ref{tab:name}`. IEEE writes "Fig." at the start of a sentence too.
- **Panels.** Prefer one image file that holds all panels, with (a), (b), (c) drawn in the figure and explained in the caption.
- **Figures drawn in LaTeX.** TikZ and pgfplots figures use the document font at `\footnotesize`, the palette defined once in the preamble with the same colour values, and the line widths of Section 3.
- **Tables.** `booktabs` rules, no vertical lines, the unit in the column header, and the same number of significant digits within a column.

## 7. Before showing a figure

1. Render the exported file at 100 % and look at it.
2. The width is 3.5 in or 7.16 in and the height is at most 8.8 in.
3. The smallest lettering is at least 7 pt. Nothing overlaps. Nothing is cut off at an edge.
4. Every colour and line style is explained, and every mark is true to that explanation.
5. It still reads in greyscale.
6. Colours, typeface, sizes and symbols match the other figures and the text.
7. Fonts are embedded and none is Type 3.
8. In the compiled paper the figure sits near its first reference. See [writing.md](writing.md).

# Design-loop log

One section per round (newest at the bottom). Format:

```
## <date> - <short title>
Comment (Enes): ...
Plan: ...
-> <agent>: task ...
<- <agent>: result ... (numbers)
Checks: ...
Commit: <hash>
```

## 2026-10-27 - Loop set up
Comment (Enes): one leader to talk to, specialists that work in parallel, visible communication.
Plan: six agent definitions in .claude/agents, leader protocol in CLAUDE.md, this log.
Checks: none yet (no agent run).

## 2026-10-28 - Project-meeting poster
Comment (Enes): update the ICPE poster with the SPB review paper and the design-flow presentation.
Plan: leader did it directly (single document, no parallel work): scripts/make_poster.py, template style kept.
Checks: Inkscape PDF/PNG export, A0, no overflow (preview + 150 dpi detail checked).
Commit: 2aca85c

## 2026-10-28 - Poster: Enes's layout, A0 print quality
Comment (Enes): poster edited by hand (modulation/balancing removed, flow emphasised); fix it in that style, check
figure quality for A0 print.
Plan: leader did it directly on the hand-edited SVG (make_poster.py superseded); new scripts/make_poster_figs.py
for print-resolution figures.
Fixes: review fig03/fig13/fig16 re-rendered from vector PDFs (113/137/156 -> 331/344/345 dpi; fig13 was stretched
5 %); Q3D model replaced (600 px paste, 84 dpi, stretched 17 % -> 1900 px, 279 dpi, legend as SVG text); loop-per-cell
chart redrawn at box size with A0 fonts; footer no longer covers the third bullets of cards 8/9; cards centred;
header centred; typos (Department, dc current, D-FoM, "GaN ,", "and -1.9", stray "t", "/", "." objects).
Checks: all rasters >= 227 dpi at print size; Inkscape PDF = A0 (2384 x 3370 pt); 150 dpi detail views checked.
Commit: 5ce33cc

## 2026-10-28 - Poster restyled in one style
Comment (Enes): the pasted slide parts do not match the poster style; restyle them.
Plan: leader rewrote scripts/make_poster.py to Enes's layout and content (Enes's hand-edited SVG kept in git history,
5ce33cc); make_poster_figs.py removed.
Result: one type scale (section 8.6, panel 6.8, body 6.4, chart 4.6 mm) and palette; review figs 3 and 16 as vector
(PDF import); line charts matplotlib SVG with text; bar charts, screens and V_DS bars drawn natively; all numbers from
revb_flow_numbers / final_numbers / q3d_spice_numbers / gate_summary_dpt. Sections renumbered 1-8 (7 was missing).
Changed from the hand version: power-loop +0.3 nH imbalance 2 % (deck table), not "~0 %".
Checks: PDF A0 (2384 x 3370 pt); rasters: logo 554 dpi, DPT render 216 dpi, Q3D model 287 dpi; 150 dpi detail views.
Commit: fa3f42f

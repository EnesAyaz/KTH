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

## 2026-10-28 - Poster: D-FoM check, review Fig. 13 restored
Comment (Enes): check the D-FoM values against our data; why was the voltage-class / cell-count graph changed?
Checks: D-FoM = R_DS(on) * C_oss,tr (DEV table, revb_flow_figures.py): lowest per class 1.35 ps EPC2361 (100 V),
4.14 ps EPC2215 (200 V), 6.88 ps EPC2050 (350 V), 4.90 ps IGT65R140D2 (650 V) - the pasted values were right.
Now computed from revb_flow_numbers.json devices, device names under the bars. Section 1 uses review Fig. 13 again
(vector), the redraw was a mistake.
Commit: 89e4e1f

## 2026-10-29 - Commit before push
Comment (Enes): commit everything that is not committed, then push.
Committed: Enes's Inkscape edits of the poster SVG (title "Propulsion", wording, Conclusions numbered 7) with PDF/PNG
re-exported from it (A0); deck PPTX as saved on 28 Oct; DPT .kicad_pro re-saved by KiCad (rules unchanged apart from
float rounding) and DPT plot PDFs (same size, re-plotted 26 Oct).
Not committed: spb-bb-fab.kicad_pro and hardware/To-do.txt (standing rule), load-board plots and busbar Q3D results
(frozen boards, changes predate these rounds), untracked notes/drafts of Enes's.
Note: scripts/make_poster.py would now overwrite Enes's SVG edits; port them before regenerating.
Commit: 80e2a07

## 2026-10-29 - Commit all, ignore generated files
Comment (Enes): commit all 556 changes; generated files (e.g. LTspice run outputs) go to .gitignore.
Done: root .gitignore extended (Office ~$ locks, LaTeX aux/bbl/blg/fls/fdb_latexmk/synctex, __pycache__/pyc,
LTspice .op.raw, Ansys .aedt.auto/.temp/.lock/.aedtresults, tmp/ and .build/ scratch folders, KiCad generator
caches, the 64 MB downloaded PCB-design thesis). 556 -> 419 changes, committed per project (Review-Paper-SPB,
Airgap Harmonics, PresentationOfMeetings, PCB-Design). Q3D .aedt models kept (convention, each < 20 MB).
CLAUDE.md commit rule updated: the old do-not-commit list is lifted.
Commits: e05324b, 2071d60, 25ec617, f4a8d26, a17e051

## 2026-10-29 - Poster: R_DS(on) vs C_oss,tr panel
Comment (Enes): show R_DS(on) versus output capacitance instead of the D-FoM bars.
Done: panel 2(a) = log-log scatter of the ten surveyed devices (revb_flow_numbers.json), coloured by class, dashed
lines of constant D-FoM 1/2/5/10 ps, best device per class circled, EPC2361 1.35 ps labelled. Enes's Inkscape edits
(title "Propulsion", KPI texts, 2nd n=4 bullet, 4(a) title, Conclusions 7 / status 8 / questions 9, open question 1,
footer) ported into make_poster.py so the script reproduces them.
Checks: A0 PDF; 150 dpi detail view of section 2.

## 2026-11-03 - Pre-fab layout review: SW vias
Comment (Enes): new review (reports/pcb-rules/spb-bb-revb-dpt-layout-review.pdf); fix the switch-node via issue
without breaking anything else; do what the review suggests.
Review: must-fix = one 0.6/0.3 mm via per cell from the F.Cu SW island to the inner/bottom SW planes (~1.2 mOhm, in the
v_DS path); minor = 4 DC+ vias missing from the via-in-pad list; rest are judgement calls (prepreg with JLC, silk
text, MLCC flex, shunt overhang).
Plan: pcb-layout adds >= 15 SW vias per island at the geometry source (no antipads in the In1 DC- loop return) ->
fab-release regenerates the package + via-in-pad list -> sim-analyst re-checks loop per cell in Q3D.
-> pcb-layout: SW via array per island, DRC 0, nothing else moved, report what each layer under the vias is.
<- pcb-layout: 15 SW vias per cell (14 new, 0.6/0.3 tented); none fit inside the original island (bottom U.FL J7/J8
   + sense routing under it), so the F.Cu SW island was extended outward over the V_DS spring pad (44 mm2, was 27.5).
   In1: cells 1/4 no copper under the vias; cells 2/3 a 1.9 x 5.4 mm antipad slot in DC-, 5.6 mm from the loop.
   Island-to-plane 2.86 -> 0.44 mOhm. DRC 0/0, silk 0, sch 0, 3D 0 collisions; vias 1094 -> 1150. Side effects:
   4 SW stubs gone (pad in pour), 5 bottom silk labels moved; TP3/24/37/41 0.2 mm (generator, not this change).
-> fab-release: regenerate DPT package, complete via-in-pad list (4 DCP vias), order checklist.
-> sim-analyst: Q3D re-export, loop per cell before/after (0.652/0.652/0.647/0.653 nH), k.
<- fab-release: package regenerated (27 files rewritten). Gerbers: +56 SW via flashes on F/In2/B, 4 F.Cu SW pours, In1 DC-
   -17.2 mm2 (inner-cell antipads), TP3/24/37/41 0.2 mm, 6 silk labels (incl. "VDS Q7"); PTH 1140 -> 1196, NPTH 4.
   via_in_pad.csv 184 -> 190 (rule now = drill overlaps a mask opening, scripts/via_in_pad_list.py; geometric check
   190/190, none extra); CPL/BOM 170 (38 bottom), C13 18.0/45.4. Findings (pre-existing): GH_L2 via 0.57 mm off TP33
   centre (cell-1 twin 0.41), GNDI1 via on the TP1 edge, 28 DC- drills tangent to pad openings (rely on JLC POFV).
<- sim-analyst: full Q3D (100 MHz, 2 %, same flow as loop_dpt) on HEAD board (swv0) and SW-via board (swv1). Loop per
   cell all switching: before 0.646/0.637/0.644/0.645, after 0.646/0.644/0.645/0.648 nH (mean +0.003 nH, max cell +0.007,
   mostly mesh noise: mirror cells 2/3 now agree); all below committed 0.652. k max 0.0330 -> 0.0333. Overshoot 30 A/ns
   94.3 -> 94.4 V. SW island -> AC column (cell 1, plated barrels) 3.76 -> 1.02 mOhm, L 9.7 -> 7.5 nH. dpt.lx (HS 4.91 /
   LS 2.68 nH) now stale-high, not re-run (2.3 h); final_numbers.json not overwritten.
Checks: DRC 0/0, silk 0, sch 0, 3D 0; via-in-pad 190/190; Q3D loop change < 0.01 nH per cell. Pass.
Open for Enes: prepreg/2 oz inner with JLC engineers; "DESIGNED BY CLAUDE" silk; MLCC flex near M4 bolts; RS1/RS4
2.4 mm overhang; GH_L2/TP33 offset, GNDI1 on TP1 edge, 28 tangent DC- drills (POFV); paper numbers (after row) or keep.
Commit: 1b464f3e

## 2026-11-03 - Answers + slides on the SW-via numbers
Comment (Enes): keep the "DESIGNED BY CLAUDE" silk; explain the MLCC cracking, RS1/RS4 and the item-5 findings;
update the slides to the new numbers.
Plan: sim-analyst puts the swv1 loop per cell into final_numbers.json (lx kept, flagged stale) -> slides-builder
rebuilds the deck (numbers + DPT board renders) and exports the changed slides for a visual check.
-> sim-analyst: final_numbers.json DPT loop from swv1 (0.646/0.644/0.645/0.648 nH), no Q3D re-run, load unchanged.
<- sim-analyst: final_post.py LOOP_TAG -> dpt_swv1; final_numbers.json dpt.loop 0.646/0.644/0.645/0.648 nH (mean
   0.6511 -> 0.6457), k max 0.0338 -> 0.0333, overshoot 94.5 -> 94.4 V; dpt.lx unchanged + note (upper bound); load
   and busbar keys identical. 10-22 matrix files kept.
-> slides-builder: rebuild deck from final_numbers.json, re-render DPT board images, one line on 15 SW vias per cell,
   L_x marked upper bound, export changed slides as PNG and check.
Comment (Enes, same day): agreed torque limit + one DC-link leakage measurement after mounting; remind at test time.
Done (leader): bring-up checklist added to reports/pcb-rules/DPT_measurement_setup.md (POFV check, shunt preheat and
overhang, torque, leakage test); POFV must-stay note in DPT_JLC_order.md.
Comment (Enes): likely ordering at Eurocircuits, not JLC; remind item 5 and what to select at ordering.
Done (leader): Eurocircuits section in DPT_JLC_order.md (Type VII filled+capped on all vias, 2 oz all layers +
0.10 mm prepreg build-up to confirm, ENIG, origin/CPL format); reminder memory extended to ordering.
<- slides-builder: deck rebuilt (55 slides). Changed: 28 (15 SW vias line, DPT copper re-rendered), 30/31/33 (3D
   re-render, slide 30 text 13 pt), 34 + 52 (L_x "upper bounds, pre SW vias", image boxes fixed), 46 (DPT 0.646/0.644/
   0.644/0.648 nH, chart), 47 (k 0.034 -> 0.033, 21 -> 20 pH), 48 (overshoot line now data-driven, same text), 53.
   Load-board images restored, unchanged. 12 slide PNGs checked.
Checks (leader): slides 28 and 46 viewed; numbers match final_numbers.json.
Commit: 7a7ba452

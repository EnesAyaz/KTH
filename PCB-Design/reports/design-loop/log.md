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

## 2026-11-03 - Near-pad vias into the fill list
Comment (Enes): yes, add the 28 DC- vias (drill tangent to a mask opening) to the via-in-pad list.
Plan: fab-release adds a 0.1 mm near-pad margin to scripts/via_in_pad_list.py, regenerates only list-dependent files
(Gerber/drill content unchanged), updates DPT_JLC_order.md counts.
-> fab-release: margin rule + in_pad/near_pad column, report any extra vias beyond the 28, Gerber diff = none.
<- fab-release: margin NEAR 0.02 mm (0.1 mm would add 12 more); list 190 -> 218 (190 in_pad + 28 near_pad, reason
   column). Gerber copper/mask/paste/silk/drill byte-identical; only via_in_pad.csv, fab notes, zip changed. Independent
   Gerber check 218/218. Open: 4 Kelvin vias KH1/KH2/KL1/KL2 at 0.047 mm gap (NEAR 0.05 -> 222).
Commit: d3053164
Comment (Enes): add the 4 Kelvin vias too.
-> fab-release (same agent): NEAR 0.05 mm, 218 -> 222 (190 in_pad + 32 near_pad), Gerber diff = none.
Comment (Enes): also fix the RON subscript on slide 48.
-> slides-builder (same agent): bold + subscript markup on slide 48 (renderer fix if general), rebuild, PNG check.
<- fab-release: NEAR 0.05 mm; list 222 (190 in_pad + 32 near_pad), exactly KH1/KL1/KH2/KL2 added; Gerber/drill
   byte-identical; independent Gerber check 222/222; DPT_JLC_order.md counts updated.
<- slides-builder: build_pptx.ps1 Parse-Markup keeps sub/superscripts inside bold/alert spans; rebuilt (55 slides).
   Changed render: slide 48 (bold R_ON) and slide 4 (bold A_rms). Checks (leader): slide 48 PNG viewed, subscript OK.
Commits: 0485f0af (Kelvin vias), e3177f25 (deck)

## 2026-11-03 - Paper on the SW-via loop numbers
Comment (Enes): update the paper with the new loop numbers too.
Plan: paper-writer updates the IEEE LaTeX paper and the current ICPE manuscript from final_numbers.json (DPT 0.646/
0.644/0.645/0.648 nH, k 0.033, L_x upper bound); new dated docx, never WrittenByHand; page counts 6 / 5.
-> paper-writer: identify current versions, update via generators, report old -> new and page counts.
<- paper-writer: loop_breakdown.py -> LOOP_TAG dpt_swv1 (DPT copper 0.469 -> 0.464, total 0.6457). IEEE paper: Table II
   cells 0.646/0.644/0.644/0.648 (%.3f), copper 0.47 -> 0.46, M/k 21 pH/0.034 -> 20 pH/0.033, abstract spread 0.8 -> 0.7 %,
   Fig. 8 + Fig. 6(a) regenerated, one sentence on 15 SW vias per cell. Tracked ICPE digest: k text, boards.png, rebuilt.
   Submission digest: new Submission-Files/Digest-ParasiticAwareSPB_revised_2026-11-03.docx (Enes's 11-02 copy, only
   Fig. 7 swapped); Enes's copy is 6 pages (his edits). Full 13-page paper figure still has 0.47 hard-coded (not rebuilt).
Checks (leader): IEEE paper 6 pages, tracked digest 5 pages (pdfinfo).
-> slides-builder: rebuild loop_breakdown slide image from the new loop_breakdown.json.
<- slides-builder: slide 9 copper 0.47 -> 0.46 nH, loop_breakdown.png regenerated, "black stars" label moved
   (revb_flow_figures.py, also used for the paper figure). Checks (leader): slide 9 PNG viewed, OK.
Commits: 9b5fa895 (paper), b50036c7 (deck)

## 2026-11-04 - Independent board check before ordering
Comment (Enes): is the PCB ready; create new agents to check the PCB. Paper full-version figure: do not update now.
Plan: three fresh design-reviewer agents in parallel, read-only, one report each in reports/pcb-rules/:
manufacturability at Eurocircuits, electrical, assembly + fab package. Findings go back to pcb-layout / fab-release.
-> reviewers: measure from release files, severity + evidence per finding, list coverage and what was not checked.
<- reviewer (assembly): 0 blockers, 14 should fix, 14 notes. Gerbers/drills match board (86 nets, 0 shorts/opens, 56 SW
   vias, 222 list OK, EPC2361 land pattern OK). Top: Eurocircuits limits unconfirmed, no IN/SHLD mark at RS1-RS4, REDCUBE
   paste 150 um, M4 x 8 vs 4.0 mm thread + 1.2 N.m, Wurth 61201021621 is a male header, no fiducials, U1/U2 pin-1 silk.
<- reviewer (manufacturability): Eurocircuits cannot build the release as designed: 4 blockers, 8 should fix, 7 notes.
   B1 44 vias 0.25/0.45 ring 0.05 on tool size; B2 0.30/0.60 ring 0.10 (70 um row ~ class 4, OAR 0.150); B3 KL1/KL2 drill
   pairs 0.16 mm vs 0.25; B4 0.10 mm prepreg not listed, Special build-up. S1: fill ALL vias (928 would lose tenting).
   Class 8/9 with 70 um unconfirmed; 8 questions in the report. Fetch tool cached one image + a 2010 PDF outside the repo.
<- reviewer (electrical): 0 blockers, 3 should fix, 10 notes; no wrong pin, polarity, net, short, split. SW via change
   confirmed. Should fix: DC link sags to ~61 V at 322 A without the 1 mF bulk the SPICE assumes (not in BOM/setup note);
   M4 x 8 too long; V_DS ports not Kelvin to the die (transients only). Notes incl. shunt gain 0.957 mV/A.
   Leftover scratch KiCad python PID 32932 hung; Stop-Process denied; surfaced to Enes.
Done (leader): DPT_JLC_order.md order ALL vias filled + Eurocircuits status; setup checklist item 3 corrected (1.2 N m,
no flat support, C67/C68). No board change until Enes decides.

## 2026-11-05 - V_DS with a differential probe
Comment (Enes): hands-free V_DS without fancy probes; no board change; add the differential probe connection to the
setup note and the parts to the BOM.
Done (leader): DPT_measurement_setup.md new section + port table + rule 3; make_fab_outputs_revb.py MECH rows (4 MMCX-BNC
cables, 1 BNC-4 mm adapter, 1 probe), same 3 rows in fab BOM (5 columns, so skipped by make_jlc_files.py). No board change.

## 2026-11-05 - DPT sequence on the board's own DC link
Comment (Enes): no PCB change; discussed the 134 uF bank with lower L and precise timing (hand calc: 1 uH, 80 V, 4.1 us);
run the simulation with 1 uH and 80 V pre-charge.
Plan: sim-analyst runs a new deck copy, no Cbulk: reference, 1 uH / 80 V, sensitivities, 2.48 uH sag check.
-> sim-analyst: bus, current, V_DS peaks, E_on/E_off, off-time decay, settle time, limits; new files only.

## 2026-11-05 - Readiness check and test procedure
Comment (Enes): several agents to check everything is OK to fabricate and test; report step by step to start the test.
Plan: design-reviewer (fab readiness, go/no-go per manufacturer incl. JLC recheck) + design-reviewer (test readiness) +
general-purpose (DPT_test_procedure.md) in parallel, read-only apart from own report; SPICE results relayed into the
procedure when sim-analyst finishes.
<- procedure author: DPT_test_procedure.md, 83 steps, 20 stop criteria, checklist. Holds H1 HS gate unmeasurable without
   isolated probe, H2 probe not chosen, H3 pulse values, H4 MMCX sees LS peak 86.7 V not HS 92.9 V, H5 end-of-burst energy.
   21 values T1-T21 to be set by Enes. Source contradictions listed, incl. my note allowing V_GS via differential probe.
-> sim-analyst: extend run with end-of-burst energy (H5).
<- test-readiness: 6 blockers for test, 16 should prepare, 13 notes; no board change needed. B5 HS not observable, B1 bus
   source undefined (proposal >= 90 V, 100 mA, OVP 85 V, 1 kOhm 25 W series), B2 HS gate supply at bus potential, B3 pulse
   source, B4 load inductor (3 turns 16 mm2 proposal), B6 scope/probe unidentified. Proposals for T1-T21 in section 5.
-> sim-analyst: add first turn-on + second turn-off windows, 0-13 ns skew sweep, port-node and filtered V_DS outputs.
<- fab readiness: no-go at both today. JLC: Gerbers pass, but JLC04161H-3313 is 1 oz/0.5 oz; 2/2 oz build JLC041622-3313 has
   0.1835 mm L1-L2, so 0.10 mm + 70 um inner not on listed builds (hand est. loop 0.71-0.75 nH per cell, needs Q3D). Eurocircuits:
   4 blockers stand. 37 open items F01-F37; 10-step list. Also XUMA2 order code, Amphenol lab cable is a female bulkhead BNC.
Done (leader): Amphenol removed from the lab cable line (generator + BOM).
<- sim-analyst: 33 cases, Q3D dpt_swv1. 1 uH / 80 V / 4.146 us: 74.9 V, 322.0 A; HS peak 95.9 V (first turn-on) / 90.9 V, LS 87.7 /
   89.3 V; E_on 121, E_off 20.6 uJ; I end 339.5 A; V_GS min -3.43 V. D confirms 60.7 V sag. New: U1-U2 skew limit about 1 ns
   (V_GS past -4 V at 2 ns, 18 nH estimate); pre-charge max 84 V; read limits 98/93/87 V at 500/200/100 MHz; 1.36 MHz row ring
   sets off-time 0.75 us; tail 12.85 mJ per HS FET, 79 us, shots >= 1 s. Committed 92.9 V was at 79.4 V rows and 316 A.
-> procedure author: fill section 8, stop rules, T proposals, B1-B6; two setup-note corrections.
<- procedure author: DPT_test_procedure.md final, 84 steps, 23 stop criteria; setup note intro corrected. Note: M0_skew1 at 80 V
   gives HS first turn-on 99.98 V, V_GS -3.72 V, so 1 ns skew has no V_DS margin even at 80 V; 84 V only near zero skew.
Open: HS peak and gate unmeasured (optical probe), equipment choice, T1/T2/T3/T20, 15 proposals for Enes; stack-up decision.
Commit: 4c4328f0

## 2026-11-05 - R_ON staging against skew
Comment (Enes): start with more gate resistance and lower bus to see current sharing, then lower R_ON and raise the bus.
Plan: sim-analyst sweeps R_ON 1.5/2/3/5 Ohm x skew 0-3 ns at 40/60/80 V on the 1 uH deck; results go into the procedure.
-> sim-analyst: allowed skew per R_ON and stage, turn-off peak vs R_ON, new files only.
<- sim-analyst: 86 runs. Higher R_ON does not relax skew; lower bus does: 40 V >= 3 ns, 60 V about 1.5 ns, 80 V 0.5 ns (crossing 0.9-1.0).
   R_ON 5 Ohm unstable at 0.5 ns at 80 V. Turn-off peak independent of R_ON (87.3-87.5 V). Zero skew HS on1 95.8/89.3/83.0/80.4 V,
   E_on 121/145/187/262 uJ at R_ON 1.5/2/3/5. Option R_G 1.5 / R_ON 1: crossing about 1.5 ns, E_off +27 %.
Done (leader): procedure T7, gates and section 8 updated to staged skew limits.

## 2026-11-06 - Q3D for the skew limit
Comment (Enes): run the Q3D extraction for the skew limit.
-> sim-analyst: L_x on the SW-via board (new tag), replace the 18 nH Lac estimate, rerun skew limits and the R_G 1.5 / R_ON 1 option.
<- sim-analyst: Q3D BB_PL_LX_dpt_swv1, 1 h 37 min, converged; 52 SPICE cases, 0 failed. Pair to pair 17.49 nH (18 estimated), L_x HS/LS
   4.58/2.70 nH (4.91/2.68), node to bolt outer/inner 29.6/14.75 nH. Network is not a star: 92/68 A inner/outer at first turn-off.
   Skew limits unchanged (80 V crossing 1.1-1.3 ns; R_G 1.5 / R_ON 1 >= 2 ns, E_off +30 %). NEW: inner HS V_GS -6.0 V pin, -5.6 V die at
   zero skew, about 20 ns; -4.25 V at 20 V, -3.14 V at 10 V; not set by skew or R_ON. Earlier "inside EPC limits" withdrawn.
Check (leader): limits.csv, die_vgs.json and results.csv match the report; bolt on the centreline, load J21 to J1 as in the deck.
   Found: stage table 80/161/241 A never simulated (runs 50/100/200 A); T17 +/-10 % would trip on the predicted split; LS peak rose.
-> sim-analyst: per-cell probe-filtered readings, last stage inside V_GS, T15 check.
<- sim-analyst: inner J9/J15 93 V, outer J6/J18 87 V raw; 10 V last stage inside (20 V outside, -3.7 V about 15 V by 2-point
   interpolation, not a limit). T15 proposal 97.5/93 V at 500/200 MHz on J9/J15, no 100 MHz line. Two solver spikes removed, counted in JSON.
Done (leader): procedure: hold H6, S0 10 V stage, stages at simulated currents, H1 gate moved to before S1, T7 basis, T14, T15, T17, 7.4-7.7,
   section 8 values, stops 10, 12, 13, checklist. Setup note warning. Own slip fixed before commit: an unsupported "2.8 ns" sentence.
Open: H6 (measure, then decide), T17 proposal, paper sharing text 77-81 A (symmetric model), L_x in final_numbers.json, stack-up.

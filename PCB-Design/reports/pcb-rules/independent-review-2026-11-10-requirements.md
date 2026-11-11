# Independent review 2026-11-10: Rev B DPT board against the electrical requirements

Reviewer: design-reviewer (read-only). Board: `hardware/spb-bb-revb-dpt/spb-bb-revb-dpt.kicad_pcb` as committed on
main (6cfa2633), generator `scripts/make_kicad_bb_revb.py` with BOARD=dpt. Trial tie: uncommitted worktree
`C:/Github/KTH/.claude/worktrees/agent-a226540339b516abb` (that board was dumped as well).

Method: geometry read from the board file with the KiCad 7 Python API (zones, tracks, vias, pads), the generator,
the Q3D terminal/summary files and the gate-dip SPICE decks. No Q3D or SPICE run was made. All inductance and
capacitance numbers marked "estimate" are hand formulas on measured geometry, shown below. Coordinates: board x = 0
is the centreline; "x_r" is block-local (block centres at x = -23.75 and +23.75); y as in the generator.

Classes: blocker (wrong copper, connectivity or fab data) / fix before order / acceptable for a prototype.
**No blocker was found.** Manufacturability is not repeated here (see `independent-review-2026-11-04-*.md` and
`fab-readiness-2026-11-05.md`).

Formulas used:
- flat strip, partial inductance: L = 0.2 l (ln(2l/(w+t)) + 0.5 + 0.2235 (w+t)/l) nH, lengths in mm
- strip over a plane: L = 1.257 h l / w nH (h = 0.10 mm prepreg); fringing lowers it by 10-20 %
- plate capacitance: C = 8.854e-3 x 4.4 x A / h pF (A in mm2, h in mm)

---------------------------------------------------------------------------------------------------------------

## Summary

1. The outer/inner difference (29.6 vs 14.75 nH) is almost only the sideways run in the AC bus: outer necks land
   42 mm from the bolt, inner necks 5.5 mm. The cells themselves are mirror images. Moving the take-off to the
   centre of each driver pair makes all four cells equal by construction. This is the largest single gain and it
   does not touch the cell loop (0.646 nH per cell stays).
2. The same asymmetry is very likely the source of the 9 V SW difference inside a pair that drives the gate dip
   (hold H6): cells 1 and 2 share one driver, so with a symmetric take-off their SW nodes move together. This
   should be confirmed in SPICE (equal L_x) before any tie is drawn.
3. The trial tie (L3 band 2.5 mm x 11.2 mm) cannot plausibly reach 1 nH. Estimate 6-8 nH: 4-6 nH for the band
   (no plane above or below it) plus about 1 nH per side, because each L1 SW island reaches L3 at the corridor
   edge through one single via. By the numbers of the model itself (5 nH fails) it does not fix the dip.
4. The HS gate/Kelvin legs are modelled without mutual coupling (the LS legs have k = 0.58 for nearly the same
   copper). The HS dip may be overstated. Check the model before redrawing.
5. The gate error is set by the coupling between each gate leg and its Kelvin leg, not by the Kelvin inductance
   or the star position. Copper fix: run the HS Kelvin under the gate row, as the LS nearly does already.
6. The DC terminals (J1 at x = -6, J2 at x = +6) are in neither the Q3D L_x terminals nor the SPICE deck. They add
   a left/right asymmetry of several nH that the +-15-18 % figure does not contain.

---------------------------------------------------------------------------------------------------------------

## Q1. Where the outer/inner asymmetry comes from

Verified geometry (board file):

| item | cell 1 (outer) | cell 2 (inner) | cell 3 (inner) | cell 4 (outer) |
|---|---|---|---|---|
| FET centre x | -33.25 | -14.25 | +14.25 | +33.25 |
| L1 SW island | 9.0 x 3.7 mm + extension, 2 x 7 vias at x_r 18.4/19.4 | same, mirrored | same | same |
| L3/L4 upper column (y 5.2..15.9 / 4.6..17.9) | 14.5 mm wide | same | same | same |
| L3/L4 lower column (y 14.9..33.4) | 8.95 mm wide | same | same | same |
| neck, 4 layers (y 20.8/33..44.5) | 3.3 mm wide, x -43.65..-40.35 | 3.3 mm, x -7.15..-3.85 | 3.3 mm, x 3.85..7.15 | 3.3 mm, x 40.35..43.65 |
| neck centre to bolt J21 (0, 52.4) | 42.0 mm | 5.5 mm | 5.5 mm | 42.0 mm |

The two cells of a block are mirror images about the block centre (the driver). Every SW column runs away from
the driver, so the neck of the outer cell ends at the board edge and the neck of the inner cell ends next to the
bolt. From the FET to the end of the neck the four paths are identical in length and width on every layer. The
whole difference is in the AC bus (4 layers, x -43.95..43.95, y 44.5..60, 15.5 mm tall).

Estimate check: 36.5 mm of extra bus, 15.5 mm wide, 4 layers treated as one 1.6 mm bar:
0.2 x 36.5 x (ln(73/17.1) + 0.5 + 0.105) = 15.0 nH. Q3D difference: 29.6 - 14.75 = 14.85 nH. The common part
(neck 3.3 x 11.5 mm about 5 nH, lower column about 7 nH, upper column and vias 2-3 nH) agrees with 14.75 nH.
So the picture is consistent with the extraction (confidence high).

Options, without touching the cell loop:

- **A (recommended): one AC take-off per driver pair.** Bolts at (-23.75, 52.4) and (+23.75, 52.4); AC bus copper
  removed for |x| < 3.55 on all four layers. Each half bus is then exactly mirror-symmetric about its bolt: necks
  18.25 mm on either side. Estimate per cell: 14.75 + 0.2 x 18.25 x (ln(36.5/17.1) + 0.5 + 0.21) = 14.75 + 5.4
  = about 20 nH, equal for all four. The dynamic split falls to the static level (+-2 %) plus the DC-side term of
  Q2. Confidence in "equal": high (symmetry). Confidence in the 20 nH value: medium (+-3 nH).
  Without the centre gap the inner cells keep a second path to the other bolt (29 mm) and stay about 20-25 %
  lower than the outer cells; the gap is part of the revision.
- **B (fallback, one bolt): H-tree slots.** Collector strip 3 mm tall joining the two necks of a pair, a 5 mm
  bridge at the block centre, then the rest of the bus to the centre bolt. Estimate: +10.6 nH (collector half,
  18.25 x 3 mm) + 9.5 nH (23.75 x 11.7 mm, common to the pair), about 35 nH per cell, equal. Problem: the slot
  that separates the inner neck from the bolt runs through the 14 mm bolt pad (the pad reaches y 45.4 at x = 0);
  the bolt must move down about 3.5 mm and the board grows by about 2.5 mm in y. More copper lost, higher DC drop.
- Moving only the single bolt cannot help: it stays on the mirror line of the two blocks, and the asymmetry is
  inside each block.

## Q2. DC side

Verified: each cell has the same local capacitors (6 x 0805 top, 4 x 0805 bottom). The 2220 bank has 20 parts:
row A at |x| = 15, 21, 27, 33 (8 parts), row B at |x| = 3..33 in steps of 6 (12 parts); none beyond |x| = 33, so
the outer cells (33.25) have bank capacitors on one side only. L3 DCP and L2 DCN are continuous across each
block. The per-cell loop is the same for all four cells.

Not symmetric: J1 (DC+) at x = -6 and J2 (DC-) at x = +6, y = -18.8. The Q3D terminal list
(`BB_PL_LX_dpt_swv1_terminals.txt`) has no J1/J2 terminal, and the SPICE deck uses one 127 uF bank behind an equal
4 nH per cell with the load on a common node. So the terminal position is not in the +-15-18 % number.

Estimate (inference, low to medium confidence): the load current of each cell must cross the DC planes sideways
to J1. Distance 27 / 8 / 20 / 39 mm for cells 1 / 2 / 3 / 4. Plane strip about 18 mm wide: 9 / 1.5 / 6 / 16 nH,
minus about 2 x 2-3 nH mutual with the AC bus current (it runs the other way, 50 mm away): about +5 / +1.5 / +6 /
+10 nH on top of the AC-side values. The distributed bank hides this for the first microsecond (bank
redistribution period about 2 us), then the terminal position shows. Expected effect on the present board:
cell 4 lowest, cell 2 highest, cells 2 and 3 no longer equal.

V_DS at the probe (inner 93 V, outer 87 V): the overshoot ratio 13 V / 7 V = 1.86 is larger than the current
ratio 92/68 = 1.35, so current alone does not explain it; part is the different SW-node path seen by the probe.
With equal currents both should come to about 90 V (inference). The DC side itself gives no V_DS difference
between cells, because the local capacitors and planes are the same.

Class: acceptable for a prototype, but it must be extracted (J1/J2 as terminals) before shunt data are used as
proof of sharing. Failure scenario: a left/right difference on the bench is read as a fault of the cell layout.

## Q3. Gate drive

Verified routing, block-local, same in both blocks:

| leg | L1 | L2 | via |
|---|---|---|---|
| HS gate | pad (-/+7.15) to R_G at -/+5.6 (1.55 mm), R_G, star row y 4.9 to x_r 0 (5.09 mm) | - | - |
| HS Kelvin left | row y 3.6, x_r -7.15..-1.8 (5.35 mm) | diagonal (-1.8, 3.6) to (0, 4.9), 2.2 mm | (-1.8, 3.6) |
| HS Kelvin right | row y 6.2, x_r 7.15..1.8 (5.35 mm) | diagonal (1.8, 6.2) to (0, 4.9), 2.2 mm | (1.8, 6.2) |
| LS gate | same pattern, star row y 9.2 | - | - |
| LS Kelvin left / right | row y 7.9 / 10.5, 3.15 mm | diagonal (-4, 7.9) to (4, 10.5), 4.2 mm per side | (-/+4.0, ...) |
| HS star to driver | stub (0, 4.9) to (0, 6.6), via | KH: (0, 4.9) to (0.75, 7.0), via | L3 GH_STAR over L4 KH, 0.1 mm apart, to y 10 |

Shared segment: none between the two FETs up to the star point (0, 4.9) / (0, 9.2); from the star to the driver
gate and Kelvin run broadside on L3/L4 (good). All tracks 0.3 mm. L2 has a keepout under the corridor
(|x_r| <= 3.3, y 3.3..12.9), so inside |x_r| < 3.3 the gate and Kelvin rows have no plane under them and lie
1.3 mm apart on the same layer. Left and right legs are point-symmetric and of equal length.

What matters (inference from the circuit): the two Kelvin legs form a bridge between the two SW nodes. The SW
difference dV divides over the two legs, half each. Each FET sees dV/2 x (1 - k) as gate error, where k = M/L_k
is the coupling between its Kelvin leg and its own gate leg. Consequences:
- A lower Kelvin inductance does not help by itself (the bridge still takes dV; only the current changes).
- Another star position does not help (the two legs still carry dV).
- Only three things help: a smaller dV (symmetry, tie), a larger k (gate over Kelvin, or a common-mode choke per
  gate/Kelvin pair), or one driver channel per FET.

Model finding (fix before order, model side): in the gate-dip decks the HS legs are `LgbH1 0.7644n` and
`LkbH1 3.723n` with no K statement; the LS legs are 3.505 nH each with `KgkL1 -0.58`. 0.76 nH matches only the
1.55 mm pad-to-R_G stub; the 5.09 mm HS star row seems to be inside `LconHA` (8.84 nH against 5.47 nH for LS).
So the HS gate row is treated as common to both FETs and as uncoupled to the Kelvin legs. On the board the HS
row runs 1.3 mm from the Kelvin row and the L2 diagonal passes under it; a real k of 0.2-0.4 is likely. The
-6.0 V figure may be 20-40 % too pessimistic. Failure scenario if not checked: copper is added (tie,
capacitance) for an error that is partly a modelling artefact, or the wrong fix is ranked first.

Copper fix (revision G1 below): give the HS Kelvin the LS pattern and go one step further, with the L2 Kelvin
track directly under the L1 star row for the last 2.7 mm on each side. Estimate: HS k from about 0.2-0.4 to
0.6-0.7, so the HS gate error for a given dV falls to roughly half. Coupling to SW/AC copper: the HS gate network
sits in the corridor with SW columns starting at |x_r| 5.4 on L3/L4; the reference of the HS gate is SW, so this
is harmless. The LS star row (y 9.2) has the L1 SW islands 5 mm away and no SW copper under it; no change needed.

## Q4. SW tie

Trial as drawn (verified in the worktree board): one L3 zone, x_r -5.6..5.6, y 4.8..7.3 (11.2 x 2.5 mm). The L4
keepout was opened but no L4 SW zone crosses the corridor, so the tie is one layer. In the band sit the GH_STAR
via (0, 6.6), the KH via (0.75, 7.0), the KH through via (1.8, 6.2) and the start of the L3 GH_STAR track; the
clear copper next to them is about 1.0 mm (y 4.8..5.8). There is no plane on L2 above it (keepout) and none on L4
below it; the L3 DCP edge is 0.2 mm away on one side only. The L1 SW island of each cell reaches L3 at the
corridor edge through one via, at (-/+5.45, 7.05); its other 14 vias are 13 mm away at x_r 18.4/19.4.

Estimate: band 0.2 x 11.2 x (ln(22.4/2.57) + 0.55) = 6.1 nH as a free strip, about 4-5 nH with the DCP edge as
partial return, +0.5-1 nH for the 1 mm neck, + about 1 nH per single via (1.3 mm long, 0.3 mm drill). Total
6-8 nH. With the rule of thumb dV_tied = dV x L_tie / (L_tie + 1.3 nH) (two cell loops as source impedance;
it reproduces the model result 1 nH pass / 2 nH marginal / 5 nH fail) this leaves 80-85 % of the SW difference.
Class: fix before order if a tie is wanted. Failure scenario: the board is ordered with a tie that is believed to
clear hold H6, and the inner HS V_GS still goes below -4 V at 80 V.

Note on the 1 nH target itself: by the same rule 1 nH still leaves about 43 % of dV; the model passes only
together with the -1.5 V off level. A tie is a weak cure compared with removing dV at the source (revision S1).

Best geometry if a tie is kept (revision T1): on L1, island to island, over a closed L2 DCN plane. No via in
the path, and the 0.10 mm prepreg puts the return directly under it. Free L1 band between the gate parts today:
y 6.55..7.50 (0.95 mm), limited by the HS Kelvin row at y 6.2 and the gate stub at y 6.13 above, and by the LS
Kelvin row at y 7.9 and R5 below. Estimate 1.257 x 0.10 x 10 / 0.95 = 1.3 nH, about 1.1 nH with fringing, plus
0.2-0.3 nH per side inside the islands: 1.5-1.8 nH. To reach 1 nH the strap must be at least 2 mm wide, which
needs Kelvin rows moved out of y 5.3..7.6. Added SW capacitance: strap 10 x 0.95 mm over DCN:
8.854e-3 x 4.4 x 9.5 / 0.1 = 3.7 pF per pair (2 mm strap: 7.8 pF). Whole-board SW to DCN today is 23 pF (Q3D)
and C_oss is of the order of 1 nF per FET (datasheet value not rechecked), so this is negligible.

Alternative considered and not recommended: an L4 tie 4.7 mm wide under a new L3 DCP tongue (corridor part about
0.3 nH, 20 pF per pair). It still ends on the single via per island; there is room for two through vias at most
at the inner island edge (about 0.7 nH per side), and it covers the bottom V_GS test pads TP15/TP16.

What a tie must not cross or touch: the L2 Kelvin tracks (they must stay separate from SW copper although they
are at the same DC potential), the GH_STAR and KH vias, the bottom V_GS test pads, and the LS Kelvin row.
Barrier: any tie at y < 10 is inside the HS/power domain; the control barrier moats start at y 16.8, so the
1200 V rules (4.0 mm outer layers) are not affected. Loop per cell: an L1 strap in the corridor (|x_r| < 5)
lies outside the cell loops (|x_r| 5..14) and closing the L2 keepout only adds DCN copper, so 0.646 nH per cell
should not change; to be confirmed by the standard per-cell Q3D run. Current: about 12-15 A for microseconds
through a 1 mm x 70 um strap (about 2.5 mOhm): no thermal issue.

Extraction note: the tie must be extracted as a loop (SW island 1 to SW island 2 with the DCN/DCP planes as
return, capacitors shorted). A partial node-to-node value like the 40.3 nH figure is not the number the model
needs.

## Q5. What the measurements show after a tie

- RS1-RS4 stay in series with one LS FET source each (LSRC1-4 remain separate nets). They still read the current
  of each LS FET. With a tie they no longer read the current of the branch from that cell to the bolt: the tie
  carries the difference (about 12 A in the model). Equal shunt readings then prove equal FET currents, not a
  symmetric AC path.
- J6/J9/J15/J18 read SW (L4 column) against the LSRC of the same cell, 6-8 mm from the LS FET. With the tie the
  two SW nodes of a pair are close to common below about 100 MHz, so the inner/outer V_DS difference inside a
  pair largely disappears; a difference between the pairs can remain.
- HS currents are not measured at all, with or without a tie (V_DS spring points exist for Q1, Q2, Q5, Q6).
- Consequence: make the tie a plain L1 strap with a solder-mask opening over a 3 mm long section, so it can be
  cut on the bench. Then one board gives both cases: tied (gate dip) and untied (sharing as built). With S1 in
  place the untied case should already share within a few percent, and the tie becomes a tolerance measure.

## Q6. Other points against fast switching and sharing

- **AC bar symmetry (comes with S1).** Two bolts need an external link. A 47.5 mm bar has 20-30 nH; the load lead
  must leave from its centre, otherwise the asymmetry returns one level up (block against block). The bolt note
  on the board says "M6 bolt + nut, 12 x 5 mm Cu bar". Whether that bar belongs to the frozen busbar set was not
  checked. Class: fix before order, together with S1.
- **V_DS margin.** With the modelled tie the HS V_DS peak is 95.6-98.0 V (97.7-98.0 V at 0.5 ns skew), 2 V under
  the 100 V requirement, and this rests on the 0.10 mm prepreg. Failure scenario: a thicker L1-L2 dielectric from
  the fab, or the DC-side terms of Q2, take the peak over 100 V at 80 V / 322 A. Class: acceptable for a
  prototype because the bench plan steps the voltage.
- **One via at the inner edge of each L1 SW island.** All cell current leaves L1 through the 14 vias of the
  outer extension. This is the same for all cells (no sharing effect) and is inside the extracted L_x, but it is
  the reason why no inner-layer tie can be good. Acceptable for a prototype.
- No further point was found that the earlier reviews do not already list.

---------------------------------------------------------------------------------------------------------------

## Ranked revisions

### S1. AC take-off per driver pair (fix before order; needs a decision on the AC bar)
- Requirement: dynamic current sharing; also removes the source of the gate dip.
- Draw: replace J21 at (0, YAC) by two AC_BOLT_M6 footprints at (-BX, YAC) and (+BX, YAC), that is (-23.75, 52.4)
  and (+23.75, 52.4). Remove the AC bus copper and its via grid for |x| < 3.55 on L1-L4 (two bus rectangles
  x -43.95..-3.55 and 3.55..43.95, y 44.5..60). Keep the necks as they are. TP47 (SW, bottom, at (-1.2, 44.2))
  must move onto one half bus.
- Effect: about 20 nH node-to-bolt for every cell (estimate); split from +-15-18 % to about the static +-2 % plus
  the DC-side term; SW difference inside a pair close to zero in the model.
- Risk: no change to the cell loop. Bolt pad top edge y 45.4 against the control connector pads J5/J14 at
  y 38.92: 6.5 mm on the board (rule 4.0 mm), but bar and washer must also keep 4 mm from the connector bodies.
  New AC bar with centre take-off. The DPT board then differs from the frozen load board at the AC terminal.
  DRC: the bus via grid must be regenerated around the new pads; mounting holes H1/H2 unchanged.
- Verify: Q3D L_x with two J_AC terminals joined by an ideal centre-fed bar: node-to-bolt equal within 5 % for
  the four cells; SPICE split within +-5 % at 322 A; gate-dip deck without tie: inner HS V_GS minimum above
  -4 V at 80 V.
- Fallback S1b: H-tree slots with one bolt (Q1, option B); board grows about 2.5 mm; about 35 nH per cell.

### M1. Three model checks before anything is redrawn (fix before order; no copper)
- (a) SPICE what-if: set the node-to-bolt inductances equal (present deck, no tie). Pass: SW difference inside a
  pair below 1 V and HS V_GS minimum above -4 V. This tests the claim that S1 removes hold H6.
- (b) Re-extract or re-map the HS gate legs like the LS legs (star row inside the leg, K between gate and
  Kelvin). Report k for HS. If k >= 0.4 the present -6.0 V figure must be restated.
- (c) Add J1 and J2 as terminals to the L_x extraction and put the result in the deck (Q2).

### G1. HS Kelvin under the gate row (fix before order)
- Requirement: the gate loop must allow R_ON 1.5 ohm inside +6/-4 V.
- Draw (block-local, both blocks): set XKV["H"] = 4.0 like the LS, so the HS Kelvin vias sit at (-4.0, 3.6) and
  (+4.0, 6.2). On L2 route each Kelvin as (-/+4.0, y_k) to (-/+2.7, 4.9) at 45 degrees, then straight along
  y = 4.9 to (0, 4.9), directly under the L1 star row, width 0.3-0.5 mm. Same pattern for the LS: from
  (-/+4.0, 7.9 / 10.5) to (-/+2.7, 9.2), then along y = 9.2. Leave the star-to-driver routing as it is.
- Effect: k of each HS leg to about 0.6-0.7 (estimate, medium to low confidence); HS gate error for a given SW
  difference about halved; LS slightly better than today.
- Risk: only tracks inside the existing L2 keepout and 0.7 mm of DCN plane edge at |x_r| 3.3..4.0 (as the LS has
  today); no effect on the cell loop. The via at (-4.0, 3.6) is about 1.0 mm from the pad edge of R1: check DRC.
- Verify: Q3D gate-leg extraction, K(gate, Kelvin) >= 0.6 for all eight FETs and equal within 10 % left/right.

### T1. Cuttable L1 tie strap, replaces the trial L3 band (before order only if M1(a) fails or S1 is rejected; otherwise optional)
- Requirement: gate dip under tolerance (V_th spread, residual asymmetry).
- Draw: L1 SW strap from the left island edge (x_r -5.0) to the right island edge (x_r +5.0), y 6.55..7.50 with
  the present gate routing; 2.0 mm wide (y 5.5..7.5) only if the right HS Kelvin row (L1, y 6.2) is taken off L1,
  for example on L4 from the existing sense via at (6.33, 6.395). Move the GH_STAR via from (0, 6.6) and the KH
  via from (0.75, 7.0) to y >= 8.0. Close the L2 keepout under the strap (DCN fill for y 5.9..8.1, |x_r| <= 3.3)
  after the L2 Kelvin tracks have moved to y = 4.9 (G1). Solder-mask opening over x_r -1.5..1.5 as the cut point.
  Remove the SW_TIE L3 zone and restore the L4 keepout.
- Effect: 1.5-1.8 nH at 0.95 mm, about 0.9-1.0 nH at 2 mm (estimate). SW to DCN +3.7 pF (7.8 pF at 2 mm) per pair.
- Risk: densest part of the board; 0.2 mm clearance to gate and Kelvin tracks; moving the star vias changes the
  star-to-driver length by about 1.5 mm. No barrier effect. Cell loop unchanged (to be confirmed).
- Verify: Q3D loop extraction island to island with plane return: <= 1.0 nH for the 2 mm strap, or state the
  value and rerun the gate-dip deck with it; per-cell loop still 0.646 nH +-3 %.

### Leave for after the bench test
- G2: common-mode choke per gate/Kelvin pair (forces k near 1), or one driver channel per FET. Needs space and
  adds leakage inductance to the gate loop; only if S1 + G1 are not enough on the bench.
- D1: any DC-terminal change (centre-fed DC+ for the load return). The busbar is frozen; measure first.
- S1b slots, if S1 is rejected and the measured split is not acceptable.

Why this order: S1 and G1 remove the cause (unequal paths, weak coupling) and cost no loop inductance. M1 costs
hours, not a board. T1 treats the symptom, sits in the densest area and still leaves about 40 % of the difference
at 1 nH, so it should not be the first choice. The DC-side and choke items need bench data to be sized.

---------------------------------------------------------------------------------------------------------------

## Verified, inferred, not checked

Verified from files: all coordinates and dimensions in the tables; cell mirror symmetry; neck positions; capacitor
counts per cell and bank positions; the single SW via at each inner island edge; the gate/Kelvin track lists; the
trial tie zone and what sits in it; no J1/J2 terminal in the Q3D terminal list; HS legs without K and LS legs
with K = -0.58 in the decks; the tie as an ideal 1 nH between QH_S nodes; HS V_DS 95.6-98.0 V in `pass_fail.csv`;
DRC report of the trial board with 0 violations (report file read, DRC not rerun).

Inferred (hand estimates or reasoning): every inductance and capacitance value marked estimate; that the SW
difference inside a pair comes from the take-off asymmetry; the dV/2 x (1 - k) rule; that the HS dip is
overstated; the DC-side terms; the expected results of S1, G1 and T1.

Not checked: any Q3D or SPICE run; whether J21 or the 12 x 5 mm AC bar are mechanically tied to the frozen load
board or busbar; connector body heights near the new bolt positions; a DRC-clean routing of G1 and T1 (clearances
by hand only); EPC2361 C_oss and transient V_DS rating (datasheet not reopened); the L4 DCP island fill areas
differ between cells (17.55 against 10.58 mm2) although every cell has 4 bottom capacitors - seen, not explained,
worth one look.
---------------------------------------------------------------------------------------------------------------

## Addendum: position on findings of the blind review (`independent-review-2026-11-10-blind.md`)

Coordinates here are KiCad board mm as in the blind review (this report elsewhere: x - 150, y - 100).

**Blind F2, slot in the L2 DC- plane at y = 102.5: real, and already inside the 0.646 nH.**
Checked with a hit test on the filled L2 DCN zone of cell 1: at y 102.36..102.64 there is no copper from
x 114.1 to 121.2; webs exist only at y <= 102.2 and y >= 102.8, outside the via row. So the antipads of the 8 DC+
vias (0.9 mm pitch) merge into one slot 7.15 mm long under each 9 mm wide cell, between the capacitor DC- vias and
the FETs. The loop value 0.646 nH per cell comes from the `dpt_swv1` model, and `simulation/bb_q3d/revb_export.py`
exports the filled zone polygons with their holes (`GetFilledPolysList`, holes above 0.05 mm2 kept), so the slot
is in the extraction. The older parametric model (`bb_q3d_cs.py`, r_anti 0.35 mm, webs 0.2 mm) did not have it.
The blind estimate of 0.3-1 nH extra is therefore too high: the whole loop is 0.646 nH. Gain from closing it
(inference): 0.05-0.15 nH per cell at most. Revision L1 (optional, cheap): `via_pitch` of the cell DC+ row from
0.9 to 1.2 mm (6 vias instead of 8, 0.2 mm webs), or stagger the row by 0.5 mm in y. Risk: it changes the
per-cell loop number, so paper and slides numbers go stale; fewer DC+ vias to the bottom capacitors. Verify: one
per-cell Q3D A/B run; adopt only if the loop falls by 0.05 nH or more. Class: acceptable for a prototype.

**Blind F3, cells of a pair rotated 180 degrees instead of mirrored: true for the gate pads only; small effect.**
Verified: power copper (islands, columns, necks, capacitors, vias) is mirrored about the block centre; the FET
gate and Kelvin pads are point-symmetric (left HS gate at y 106.13, right at 103.67), so the Kelvin row runs
above the star row on one side and below it on the other. Leg lengths are equal on both sides (gate 1.55 +
5.09 mm, Kelvin 5.35 + 2.2 mm). The "extra" L2 track 126.25,105.6 to 127.0,107.0 is the common KH lead from the
star point to the driver, not part of the right leg. Contribution to the SW difference inside a pair: none in
the copper (power path mirrored). Contribution to the gate dip: second order; the deck shows it as LgbH1/LgbH2
0.764/0.800 nH and mutual terms of about 0.05 nH with opposite sign. G1 (both Kelvin tracks under the star row)
removes most of what is left. Class: acceptable for a prototype; no separate revision.

**Blind F4, bank mirrored about x = 150, via counts 13/20/19/14: agreed, same point as Q2.**
Verified: the bank via rows of block 1 run from x_r -15.4 to +22.6, that is they lean towards the board centre,
and the 2220 rows end at |x| = 33. The outer cells see fewer bank vias and capacitors. This acts in the range of
the bank (hundreds of kHz to about 1 MHz), behind the 10 local capacitors that are equal for every cell, so it
does not change the per-cell loop but adds to the DC-side imbalance during the pulse, in the same direction as
the AC-side asymmetry (outer cells get less). It is not in the SPICE deck (one bank, equal 4 nH per cell).
Position: no copper change now (bank and terminals go with the frozen busbar); covered by M1(c), which should
include the bank as terminals. Class: acceptable for a prototype.

**Blind F1, Kelvin resistors and local SW bridge.**
- Kelvin resistors: the SPICE result is right, the blind proposal is not a fix. The two Kelvin legs take the
  whole SW difference dV, half each, whatever their impedance. With an inductive leg, coupling to the gate leg
  cancels part of it (error dV/2 x (1 - k)). A resistor in the leg limits the bridge current (9 V over 2 x 2.2
  ohm is about 2 A instead of 15 A), but its voltage drop sits fully inside the gate loop and no coupling
  cancels it, so the gate error goes towards the full dV/2. It also adds to R_ON and R_OFF. Do not fit them.
- Local SW bridge at y about 107, x 121-131: same place as T1. It only works on L1 over a closed L2 plane and
  at 2 mm width (see Q4); on an inner layer it ends on single vias.
- KL1 bypasses the shunts: confirmed, and the number is right. KL1 joins the source of Q3 and the source of Q4
  through the two Kelvin legs: 2 x 7.35 mm of 0.3 mm x 70 um track = 1.72e-5 x 14.7 / 0.021 = 12 mOhm. The
  shunt path between the same two points is RS1 + RS2 = 2 mOhm. A current difference between the two cells
  divides 12 : 2, so 2/14 = 1/7 of it flows through the Kelvin net and is not seen by the shunts. The time
  constant is about 7 nH / 12 mOhm = 0.6 us, so within the 4 us pulse the DC ratio applies; in the first
  hundreds of ns the bypass is smaller. Consequence: the shunts under-read a difference inside a pair by about
  14 % (a true +-15 % reads as about +-13 %); differences between the pairs are read correctly. Position: no
  copper change; multiply the measured in-pair difference by 1.17 and write this in the test procedure.
  Class: acceptable for a prototype, but must be documented before the bench test.

**Blind F5, narrow SW strip between HS and LS FET, SW leaving at one end:** not examined in detail. The lateral
SW path of each cell (island to the 14 vias of the extension) is the same for all cells and is inside the
extracted L_x (4.58 / 2.70 nH); the commutation current crosses the strip directly from HS to LS and does not
run along it. No position beyond that.
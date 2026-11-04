# Independent pre-order review: Rev B DPT board, assembly, mechanics, fab package

Date: 2026-11-04. Board `hardware/spb-bb-revb-dpt` at HEAD 15415976 (`.kicad_pcb` byte-identical to commit 1b464f3e).
Method: measured from the release files with my own Gerber/Excellon parser and 20 µm rasters, plus KiCad 7.0.10 on a scratch
copy. No generator was run, nothing was written to `hardware/`, and earlier reports were not used as evidence.
Coordinates are mm, board origin bottom-left, x right, y up, unless stated.

## Result

| Severity | Count |
|---|---|
| Blocker | 0 |
| Should fix | 14 |
| Note | 14 |

**The copper, drill, mask and paste data are correct and match the board. I found no wrong connectivity or manufacturing
data.** The open risk is elsewhere: the package was verified against JLC only, while the board will probably go to
Eurocircuits (S1-S3), and the hand-assembly and mechanical steps are under-specified (S4-S9). S1 and S2 are not defects in
the data, but they should be answered by Eurocircuits before a purchase order is placed.

## Should fix

### S1. Via annular rings were checked against JLC's rule, not Eurocircuits'
- Evidence: Eurocircuits uses TOOLSIZE = ENDSIZE + 0.10 mm for PTH and calculates the ring from the tool size. Applied to the
  sizes in `PTH.drl` and the board pads:

| Finished hole | Pad | Tool | Ring | Holes |
|---|---|---|---|---|
| 0.25 | 0.45 | 0.35 | **0.05** | 44 vias (gate, Kelvin, sense) |
| 0.30 | 0.60 | 0.40 | **0.10** | 1106 vias |
| 0.40 | 0.92 | 0.50 | 0.21 | 16 (J21 stitching) |
| 1.00 / 1.02 | 1.7 / 1.8 | 1.10 / 1.15 | 0.30 / 0.325 | 8 / 13 |
| 1.85 | 3.2 | 1.95 | 0.625 | 8 |

- Failure scenario: Eurocircuits may reduce vias by up to 0.30 mm to solve ring problems, so CAM can silently shrink all 1150
  via barrels (for example 0.30 to 0.20 mm), or the job is priced in a higher class or held. A narrower barrel changes the
  current path that the SW-via work relied on. I could not read the numeric OAR table (image only), so whether 0.10 mm passes
  at 70 µm is unconfirmed; 0.05 mm is the clear outlier.
- Action: send the Gerbers to Eurocircuits' Visualizer before ordering and get the resulting pattern and drill class and any
  via reduction in writing. Do not accept a reduction without looking at the SW and DC vias.

### S2. The 2 oz / 2 oz stack-up with 0.10 mm prepreg is unconfirmed at Eurocircuits, and "2 oz" is ambiguous
- Evidence: fab notes specify "70 um (2 oz) finished" on all four layers with 0.10 mm prepreg. Eurocircuits' published multilayer
  data points to 35 µm inner copper as standard, and I found no predefined 70 µm inner build-up. Their classification lists
  0.200-0.250 mm for 70 µm copper (the extracted table does not show which value applies where). This board has 0.20 mm gaps
  on all layers, including the EPC2361 recommended copper (p. 12: 0.20 mm).
- Failure scenario: the fab starts from 70 µm foil on the outer layers and then plates; the 0.20 mm EPC gaps fall under its
  etch limit. Or a thicker prepreg is substituted, and the quoted 0.646 nH per cell no longer describes the built board.
- Action: `DPT_JLC_order.md` already asks for the build-up. Extend the request: outer start copper for about 70 µm finished,
  70 µm inner, pressed dielectric L1-L2 and L3-L4, and whether 0.20 mm gaps are accepted. If either changes, rerun Q3D first.

### S3. The package is still a JLC package; the via-fill list is not in Eurocircuits' preferred form
- Evidence: `spb-bb-revb-dpt-fab-notes.txt` names JLC 8 times and Eurocircuits never; the release has no Eurocircuits
  section outside `DPT_JLC_order.md`. Eurocircuits wants selected fills as a separate file or layer (or marked in its drill
  editor), not a CSV. By default it treats finished holes up to 0.45 mm as vias, so the 16 J21 0.40 mm holes count as vias.
- Failure scenario: 222 vias are entered by hand or the CSV is overlooked. An unfilled via under a 0805 pad (raster: up to 70 % of
  a top drill's area and up to 99 % of a bottom drill's area lie under paste) wicks solder away from a bypass capacitor.
- Action: order "all vias filled" (no selection data needed; tool 0.40 is inside their 0.20-0.60 mm limit). Otherwise export
  the 222 hits as a separate drill file. Add a short Eurocircuits note to the zip.

### S4. No IN / SHLD marking for the hand-soldered shunts RS1-RS4
- Evidence: PMK datasheet Rev 02A p. 3 warns to observe the soldering direction: UFCS IN to the input, SHLD (internally tied to the
  SMA shield) to the reference. `F_Silkscreen.gto` has only the labels RS1-RS4 near the lands. No `IN` or `SHLD` text exists
  on any layer. The correct direction is IN to pad 1 (LSRCx, y 49.0) and SHLD to pad 2 (DCN, y 46.4).
- Failure scenario: a shunt soldered the wrong way round puts the SMA shield, and so the earthed scope, on LSRCx instead of DC-.
  This bypasses the shunt through earth and inverts the signal, and the 15 mm blade is very hard to rework on these planes.
- Action: add `IN` and `SHLD` silk at the land ends (silk-only change; the land ends are outside the 15 mm blade). State the
  direction in `DPT_measurement_setup.md`.

### S5. RS1-RS4 can be soldered, but there is no workable procedure
- Evidence: body 22 x 7.5 mm starts 4.1 mm above the board (PMK p. 3) and overhangs the full 15 mm lands. The IN land edge (y 49.6)
  is 0.20 mm from the Q3/Q4/Q7/Q8 copper (y 49.8) and 0.30 mm from their mask opening (y 49.9). Each shunt has 38 via drills
  in its lands into 2 oz planes; the SHLD land is a 15 x 3 mm pad. Bring-up item 2 says only "preheat the board". The
  bottom side carries REDCUBE (6.0 mm) and MMCX (5 mm), so a flat hot plate does not contact the board.
- Failure scenario: a large tip at a shallow angle melts into the LS FET area, and a solder bridge from the IN land to a drain pad
  shorts SW to LSRC across the FET. Or the iron cannot lift the plane to temperature and leaves a cold joint carrying 80 A pulses.
- Action: use the sequence in the "Hand assembly" section. Prove it on a spare or bare board first. I found no PMK soldering
  temperature limit, so ask PMK.

### S6. TP45 and TP46 sit in solid planes
- Evidence: copper around the 1.02 mm holes, sampled just outside the pad: TP45 (DCP) 100 % on F.Cu and In2; TP46 (DCN) 100 % on
  In1 and B.Cu. No relief. TP47 (SW) has spokes (40 %) on all layers. The other ten loop test points tie in through tracks or
  small copper only, and are easy.
- Failure scenario: the loop looks seated (it press-fits on its own) but the joint is cold, giving an intermittent bus reading
  at bring-up, the point where the DC-link leakage check depends on it.
- Action: solder TP45/TP46 during the same preheat as the shunts, or change these two pads to thermal relief if a revision is
  made anyway.

### S7. REDCUBE process conflicts with the stencil note
- Evidence: Wurth 74650174R p. 1: THR, paste thickness **150 µm**, stencil Ø3.1, MSL 1. The order notes specify only EPC's 100 µm
  (p. 11) and also say J1/J2 may be placed "as THT (hand or selective soldering)". All 8 pins are unrelieved into DC planes (J1 on
  F.Cu and In2, J2 on In1 and, for two of four pins, B.Cu). Alloy from the Ø3.1 print is about 0.57 mm³ at 150 µm and 0.38 mm³ at 100 µm,
  against a 4.3 mm³ hole before subtracting the pin. Barrel fill is therefore low even as specified (roughly a fifth, assuming
  a pin about 1 mm square).
- Failure scenario: one stencil thickness is used on both sides, or a hand joint is attempted without preheat. The terminals
  that carry all bus current and take 1.2 N·m then have weak joints, invisible from the bottom. A torque test tears them out.
- Action: 100 µm top stencil and 150 µm bottom stencil (the EPCs are all on top). Reflow top first and bottom last, so the REDCUBEs
  and MMCX are not hanging in the second pass. Ask for a topside fill check (pin tips stand about 1.4 mm proud on top).

### S8. M4 x 8 screw can bottom out in the 4 mm blind thread
- Evidence: 74650174R p. 1 sectional drawing: blind M4 thread, 4.0 mm. Mechanical BOM: "M4 x 8 screw + washer".
- Failure scenario: 8 mm minus a 0.8 mm washer and a 2 mm lug leaves 5.2 mm of screw for a 4.0 mm thread. The screw bottoms at
  full torque while the lug stays loose, giving a hot or arcing contact, or it damages the terminal or pulls on its pins.
- Action: choose the length from the actual stack: clamped thickness + at most 3.5 mm. Keep M4 x 8 only if the stack is at least
  4.5 mm. Put the stack in the BOM.

### S9. Torque procedure cannot be followed as written, and its MLCC statement is wrong
- Evidence: `DPT_measurement_setup.md` bring-up item 3 says "board resting flat on a support" and "Twenty 2220 MLCCs (C67-C86) are within
  10 mm of the bolts". The torque is not stated: it is 1.2 N·m (74650174R p. 1). J1/J2 are on the bottom, so tightening puts the top
  (2.8 mm MLCCs, pin tips, later 27.4 mm shunts) against the support. Measured from bolt axis to MLCC body: only **C67 and C68** are
  inside 10 mm (7.63 mm); C75-C78 are 11.46 mm, C69, C70, C79, C80 about 13.1 mm, the rest further.
- Failure scenario: the board rests on the MLCC tops and flexes while tightening, cracking the capacitors the note wants to protect.
- Action: tighten before fitting the shunts, using a block under J1/J2 in the part-free top area (x 33-56, y 74-85) relieved for the
  pin tips, and hold the terminal against the reaction torque. Correct the count and state 1.2 N·m.

### S10. BOM names a male header as the control-cable socket
- Evidence: BOM mechanical line for J5/J14: "2 x 5 IDC socket ... e.g. Wurth 61201021621". Distributors list that number as a
  male WR-BHD box header, THT.
- Failure scenario: the part arrives and cannot mate with the male TSM header, delaying bring-up.
- Action: replace it with a female 2 x 5 IDC socket, and confirm its body clears L3-L5 and L8/L9.

### S11. Driver order code and package name disagree; land pattern not verifiable here
- Evidence: BOM `2EDF7275KXUMA1`, footprint `PG-TFLGA-13-4` citing datasheet Rev 3.0 Fig. 22. Digi-Key lists XUMA1 as PG-TFLGA-13-1.
  Octopart marks XUMA1 obsolete while Digi-Key shows it active, and an XUMA2 code exists. The Rev 2.0 copy I could read confirms
  the pin map but lacks the package chapter.
- Failure scenario: the delivered variant differs from the land, or XUMA1 cannot be sourced and the substitution has not been
  checked against the footprint, on the one part whose joints cannot be seen.
- Action: get the current datasheet, check pads 0.35 x 0.75 mm, pitch 0.65 mm and row distance 4.10 mm against its package
  drawing, and fix the orderable code.

### S12. No fiducials on the board
- Evidence: no fiducial footprint among the 225; the order notes rely on JLC rails.
- Failure scenario: placement of the 0.65 mm LGA and the mask-defined EPC2361 is referenced only to panel rails after routing tolerance,
  on both sides. Offset parts are then soldered with no local reference for AOI.
- Action: ask Eurocircuits to add panel fiducials and confirm its alignment method, or if silk is being revised anyway, add three
  1 mm fiducials per side. The bare round test pads could serve as alternatives if the assembler agrees.

### S13. U1/U2 have no pin-1 mark or outline on silk
- Evidence: Gerber crop at U1 (x 15-28, y 36-47): only the bare pads and the text `U1`. The footprint has only F.Fab and courtyard
  lines, with no pin-1 feature. The package is a nominally 5 x 5 mm square, so 90 and 180 degree errors fit the outline.
- Failure scenario: an operator or CPL rotation error rotates a driver and nothing on the board shows it. The first power-up
  then applies the supplies to the wrong pins.
- Action: add a silk dot at pin 1, U1 (19.05, 39.65) and U2 (66.55, 39.65). Pin 1 lies on the row with the seven pads, so the
  180 degree case can be recognised from the pad gap on the other row, but only with the drawing at hand.

### S14. DNP parts and J21 are in the pick-and-place file without a marker
- Evidence: `spb-bb-revb-dpt-pos.csv` has 179 rows including R16-R19, R35-R38 and J21. The KiCad DNP attribute is not set on any
  footprint. The JLC CPL correctly has 170.
- Failure scenario: Eurocircuits works from the generic pos file and the 0 R links are fitted, adding U.FL stubs to all eight gates
  and changing the measured gate loop.
- Action: send a pos file with these nine rows removed, and set the DNP attribute.

## Notes

- **N1 Control connector is reversible.** TSM headers are unshrouded. Turned 180 degrees, cable 12 V (pin 8) lands on header pin 3
  (GNDI). Mark the cable. Also confirm `-P` pick-and-place pad and packaging for machine placement: `TSM-105-01-T-DV` as listed
  has no such suffix; distributors list -P variants.
- **N2 `testpoints.csv` uses another origin.** All 38 rows match the board only with origin (150, 100) mm and y down. Gerber, drill,
  CPL and the via list are all on the board origin. Convert it or state the origin in its header.
- **N3 Mechanical stack.** Standoff height is unspecified. Bottom-side height is about 12 mm at J1/J2 with lug and screw head, plus
  7.6 mm test loops and MMCX probes: plan about 20 mm. The holes are 2.4 mm from the edges, so an M2.5 washer overhangs slightly.
  H1/H2 are 0.22 mm from SW copper with SW vias inside the head radius, so keep the nylon hardware from the BOM.
- **N4 TP45/TP46 near the lugs.** Bushing edge is 5.48 / 5.33 mm from the J1 / J2 axis and the loop (7.6 mm) stands above the REDCUBE
  (6.0 mm). An Ø9 washer clears; a wide ring lug pointing that way does not.
- **N5 Dense 0805 rows.** C1-C12, C26-C45, C59-C66: 1.6 mm pitch, 0.15 mm pad gap, 0.35 mm nominal body gap, shared mask openings,
  0.06 mm courtyard gap. Acceptable for this prototype, but ask for the assembler's DFA view.
- **N6 Paste on unfitted pads.** RS1-RS4 and the eight DNP links have paste apertures. On the shunts this gives useful pre-tinning, but
  make it a decision: tell the assembler paste is intended with no part placed, or drop the apertures.
- **N7 Shunt mechanics.** IN land is 1.2 mm against PMK's 3 mm footprint (gap 0.5, SHLD 3 mm and 15 mm width match). PMK says performance
  may differ off-footprint. A 6.2 g, 27.4 mm part on a butt joint needs cable strain relief. RS2-RS3 bodies are 0.7 mm apart.
- **N8 MLCC voltage margin.** 100 V parts against the simulated 92.9 V peak at the FET; R_ON 1.0 Ω would reach about 105 V. I could
  not get the TDK bias curves, so effective capacitance at 75 V is unverified.
- **N9 Sourcing.** Eight BOM lines have no MPN (10k, 47R, 3.0k, 150R, 0R, 68k, 100k, 1x2 header). Long-lead or special items: EPC2361,
  2EDF7275K, 74650174R, 66012102111404, 744232601, TSM header, UFCS-R001. Buy these before committing to a date.
- **N10 V_DS Q4/Q8 have no spring pad.** They are reachable through MMCX J9/J18 only. The `testpoints.csv` fallback (ground at RS2/RS4 pad 1)
  is covered once a shunt is fitted. The other six V_DS and all eight V_GS have an adjacent return.
- **N11 Silk.** Text 0.8 mm / 0.16 mm stroke is legible in the render, but confirm against the fab's legend limit. Label `GNDI2`
  (71.3-75.3, 38.8-40.2) sits closer to TP21 (VDDI2) than to TP19. 17 references exist only on F.Fab (for example R8, R26, C18, FB1), so
  the assembly PDF is needed there. No label is covered by a fitted part in the lands checked. Warnings on both sides read "75 V DC -
  CHECK POLARITY"; none mentions discharge. Bleeder time constant is about 44 s at nominal 440 µF, so D9 off is the practical sign.
- **N12 Job file and leftovers.** `.gbrjob`: Finish "None", revision "rev?", size 89.6 x 85.3 (outline plus line width; true 89.5 x 85.2).
  `drc_tp_tmp.txt` is an older report showing 18 warnings; the current DRC is 0.
- **N13 Saved plot settings.** The board file has `useauxorigin false` and `subtractmaskfromsilk false`; the release used both options from
  the script. Plotting from the GUI with saved settings gives different output.
- **N14 Schematic.** 25 test points (spring and pad types) are board-only, so the schematic PDF does not show them. Pin groupings of the
  200 shared parts match exactly.

## Hand assembly: proposed order

Inspect first: filled and capped vias flat (TP33, TP1 edge, y 61.3 rows), bare-board continuity between nets at J1, J2, J21.

1. Fit the eleven low-mass loops (TP7, TP8, TP11-TP13, TP25-TP27, TP29, TP30, TP47) with a normal iron while both sides are still reachable.
   Solder sides are clear: nearest foreign pad 1.56 mm (TP29 to C58).
2. Fit and torque J1/J2 hardware as in S9, before the shunts make the top side unusable.
3. Support the board on standoffs over a convection or IR preheater, target well below the 217 °C SAC305 solidus. Solder TP45/TP46.
4. In the same setup, solder RS1-RS4, IN towards the FET, SHLD side first, one at a time, with a narrow tip entering at the land end.
   Inspect the IN fillet against Q3/Q4/Q7/Q8 and measure SW to LSRCx for each cell.
5. Cool, then add strain relief to the SMA cables, then do the leakage check from bring-up item 4.

## Verified correct

- **Zip vs folder:** all 15 files byte-identical. Board unchanged since 1b464f3e; only notes, CSV and zip changed later.
- **Regeneration:** 11 Gerbers and both drill files regenerated in scratch with `--subtract-soldermask --use-drill-file-origin` differ only
  in date lines. The job file is identical.
- **DRC:** fresh run with saved rules: 0 violations, 0 unconnected, 0 footprint errors, 0 exclusions. Courtyard-vs-hole checks
  (`pth_inside_courtyard`, `npth_inside_courtyard`) are set to ignore.
- **Layers and polarity:** L1 Top, L2/L3 Inr, L4 Bot positive; mask negative; outline 89.5 x 85.2 at (0, 0).
- **Holes:** PTH 1196 = 1150 vias (1106 x 0.30, 44 x 0.25) + 46 component holes; NPTH 4 x 2.7. Every hole matches the board within 0.0015 mm.
- **Pads:** all 423 top and 168 bottom pad flashes with reference, position and net match the board.
- **Connectivity from Gerbers alone:** 86 nets, 0 shorts, 0 opens. Schematic pin groups: 0 differences.
- **Commit 1b464f3e:** 56 new SW vias, 14 per cell, in the drill file with SW pads on F.Cu, In2, B.Cu. No In1 pad, as intended
  (DC- plane). The four F.Cu islands are present as SW regions.
- **Origin:** Gerber, drill, pos, CPL and via list agree; C13 at 18.0 / 45.4 bottom.
- **Via list:** 222 entries are real vias with correct drill and net, identical in CSV and fab notes; no exposed via is missing.
- **Mask:** no web under 0.2 mm. Copper to edge at least 0.56 mm; silk to edge at least 0.68 mm.
- **BOM/CPL:** 182 BOM references all on the board, values and footprints agree, quantities correct. 170 CPL = 170 JLC BOM, 132 top and 38
  bottom, positions and rotations equal the board. Generic pos matches the board.
- **EPC2361 (datasheet p. 10-12):** every copper pad, the 15 mask features and all 21 stencil openings match in size and position.
  Paste beyond the mask is EPC's design. Pin 1 and silk dot correct; pads 2/4/6 source, 3/5/7 drain; nets correct on all 8.
- **2EDF7275K:** pin map matches Table 2 (1 GNDI, 2 INA, 3 INB, 4 SLDON to GNDI, 5 DISABLE, 6 NC, 7 VDDI, 8-10 B, 11-13 A), counter-clockwise from the top.
- **REDCUBE 74650174R:** pitch 5.87, hole Ø1.85, pad Ø3.2, stencil Ø3.1, 1.6 mm board in range.
- **WR-MMCX:** centre Ø1.47, clearance Ø2.59, 4.21 x 4.22, slot 1.07; 170 V rms suits 100 V.
- **WE-CNSW:** pads 1.1 x 0.6, 1.6 gap, 0.4 row gap. Windings 1-2 and 4-3 run along the long sides, so nets are right; footprint numbering
  is mirrored from the drawing but electrically equivalent. 260 mA, 0.8 Ω, 50 V suit this use.
- **UFCS:** body overhang 2.4 mm at RS1/RS4 confirmed; no part under the 4.1 mm body exceeds it; 80 A pulses are within rating.
- **Polarity:** diodes (cathode on pad 1 and silk bar), Zeners, D9 and J3/J4/J12/J13 pin 1 positive with matching silk.
- **Test loops:** Adafruit 3825 is through-hole, for a 0.04 in hole with Ø0.1 in bushing; 13 on board and in BOM. M6 x 16 fits the bar stack. "DESIGNED BY CLAUDE" present.

## Not checked

- Eurocircuits' numeric class table, its legend limits, and its assembly DFA; JLC limits were not rechecked as Eurocircuits is the likely fab.
- 2EDF7275K land pattern (S11), U.FL, TSM header, SOD and passive lands against manufacturer drawings: these use KiCad or project footprints that I
  did not compare. PMEG3020EJ, ERJ-3BQFR50V and LED polarity marks were not checked on datasheets, and stock was not checked.
- MLCC DC-bias curves (TDK page refused or timed out).
- Assembler rotation conventions: the CPL equals KiCad, but each house's library zero must be checked in its preview. Expected pin 1 for that check:
  Q1 (13.85, 54.67), Q2 (28.15, 57.13), U1 (19.05, 39.65), D1 cathode (18.0, 45.1), D3 cathode (9.7, 30.0).
- The physical parts, and any test fit. STEP: confirmed date and part list only, no collision analysis; heights come from datasheets.
- Isolation, EMC, thermal and loop-inductance results, and the paper, digest and slides (outside this request). Load board and busbar (frozen).

## Sources

Local: `Datasheet/EPC2361_datasheet.pdf`.
Web: [Wurth 74650174R](https://www.we-online.com/components/products/datasheet/74650174R.pdf),
[Wurth 66012102111404](https://www.we-online.com/components/products/datasheet/66012102111404.pdf),
[Wurth 744232601](https://www.we-online.com/components/products/datasheet/744232601.pdf),
[PMK UFCS Rev 02A](https://www.iwatsu.co.jp/wp-content/uploads/2026/01/UFCS_current-shunt-series_datasheet-Rev02A_J.pdf),
[2EDi family Rev 2.0](https://datasheet.chipsmall.com/2EDF7275FXUMA1/282538.pdf),
[Eurocircuits drilled holes](https://www.eurocircuits.com/pcb-design-guidelines-drilled-holes/),
[Eurocircuits via filling](https://www.eurocircuits.com/pcb-design-guidelines/via-filling/),
[Eurocircuits classification](https://www.eurocircuits.com/pcb-design-guidelines/classification/),
[Adafruit 3825 listing](https://www.pishop.ca/product/small-pcb-test-points-100-pack-red),
[61201021621 listing](https://au.element14.com/wurth-elektronik/61201021621/header-tht-vertical-2-54mm-10way/dp/1642019),
[2EDF7275KXUMA1 at Digi-Key](https://www.digikey.ch/en/products/detail/infineon-technologies/2EDF7275KXUMA1/8627157),
[2EDF7275KXUMA1 at Octopart](https://octopart.com/part/infineon/2EDF7275KXUMA1).
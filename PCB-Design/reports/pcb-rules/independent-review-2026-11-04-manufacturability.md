# Independent review: can Eurocircuits build the Rev B DPT board as released?

Date 2026-11-04. Reviewer: design-reviewer (independent, no earlier checks reused).
Board: `hardware/spb-bb-revb-dpt` (release Gerbers 2026-11-03 12:42, fab notes and zip 16:07). Load board and busbar out of scope.
Intended build: 4 layers, 1.6 mm, 70 um on all layers, 0.10 mm prepreg L1-L2 and L3-L4, ENIG, resin filled and capped vias.

## Verdict

**No, not as released.** The copper sits at Eurocircuits' 70 um limit with zero margin, and the vias are outside every published
class. Eurocircuits measures annular ring from the production tool (finished hole + 0.10 mm), JLC from the hole. On that basis the
0.25 / 0.45 mm vias have a 0.05 mm ring, below class 9, the highest class on offer. The 0.10 mm prepreg is not in their published
prepreg list, and 70 um inner copper at 1.6 mm is not confirmed anywhere public.

The release is internally sound: Gerbers and drills regenerate identically, DRC is clean, one origin. The problem is the rule set
it was checked against, not the data integrity.

Findings: **4 blockers, 8 should fix, 7 notes.**

| ID | Severity | Finding |
|---|---|---|
| B1 | blocker | 44 vias 0.25 / 0.45: ring 0.05 mm on tool size, outside all classes |
| B2 | blocker | 0.30 / 0.60 vias: ring 0.10 mm; needs class 9, while the 70 um row matches class 4 |
| B3 | blocker | 2 via pairs 0.16 mm drill-to-drill on tool size (limit 0.25) |
| B4 | blocker | 0.10 mm prepreg + 70 um inner + 1.6 mm: not a published build |
| S1 | should fix | Order notes allow filling only the 222 listed vias: the other 928 would lose their tenting |
| S2 | should fix | "70 um finished" outer copper is not a Eurocircuits outcome: about 60 or about 95 um |
| S3 | should fix | Different-net gaps exactly 0.200 mm on all 4 layers: zero margin |
| S4 | should fix | Inner clearance IPI 0.200 mm on 448 hole/layer cases; class 4 needs 0.225 |
| S5 | should fix | Same-net copper gaps 0.045 to 0.15 mm (peelable risk, will show in their analysis) |
| S6 | should fix | EPC2361 mask-defined pads vs their mask correction; 58 openings below 0.40 mm |
| S7 | should fix | Fab notes and job file carry JLC rules and wrong metadata |
| S8 | should fix | Copper imbalance L1 / L4: 0.66 / 0.31 in the DC-link half |
| N1-N7 | note | see section 4 |

B1, B2 and S4 depend partly on question 1 to Eurocircuits (section 7). B4 is a blocker for placing the order, not proof the build is impossible.

## Method

- All numbers measured from the release files in `fab/gerber/`, with my own RS-274X and Excellon reader (scratch folder, not the
  project scripts). Copper and mask rastered at 5 um. Different-net gaps below 0.225 mm and inner clearances were then recomputed
  exactly on the Gerber vectors. Raster-only numbers (same-net gaps, mask) are good to about +-0.005 mm.
- Coordinates are board mm: origin bottom-left, outline 0..89.5 x 0..85.2.
- Regeneration and DRC ran on a scratch copy with KiCad 7.0.10. No generator run, nothing written to `hardware/`.
- `kicad-cli` regeneration vs release: 4 copper, 2 mask, 2 paste, 2 silk (with `--subtract-soldermask`, as the release script does),
  Edge_Cuts, PTH, NPTH and job file identical apart from dates and comments. All 15 files in the zip are byte-identical to `fab/gerber/`.
- Fresh DRC with the saved rules: 0 violations, 0 unconnected. This confirms the JLC rule set only.
- Eurocircuits' classification table is an image on their page. The fetch tool cached that image and their 2010 build-up PDF in the
  session folder, outside the repo, so they could be read. No other files were downloaded.

## Eurocircuits limits used

From the [classification table, dated 07/05/2024](https://www.eurocircuits.com/content/uploads/2025/04/EC-classification-ENGLISH-5-2024-V3.png), shown on the [Classification page](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/classification/):

| Pattern class | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|
| Service | all | all | all | all | S, DZ, RF, SF | S, DZ, RF | S, DZ, RF | none |
| OTW / ITW, OTT / ITT (mm) | 0.250 | 0.200 | 0.175 | 0.150 | 0.125 | 0.100 | 0.090 | <0.090 |
| OAR (mm) | 0.200 | 0.150 | 0.150 | 0.125 | 0.125 | 0.100 | 0.100 | <0.100 |
| IAR (mm) | 0.200 | 0.150 | 0.150 | 0.125 | 0.125 | 0.125 | 0.100 | <0.100 |
| IPI (mm) | 0.275 | 0.225 | 0.225 | 0.200 | 0.200 | 0.200 | 0.200 | <0.200 |

| Drill class | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| PTH finished (mm) | 0.50 | 0.35 | 0.25 | 0.15 | 0.10 | <0.10 |
| Min tool (mm) | 0.60 | 0.45 | 0.35 | 0.25 | 0.20 | <0.20 |
| Max board thickness (mm) | 3.20 | 3.20 | 2.40 | 2.00 | 1.60 | - |

- Same table, min pattern by base copper: **70 um outer and inner: track and gap 0.200 mm**; 35 um: 0.125 mm; 105 um: 0.250 mm.
- Aspect ratio 1:8 on tool size. Note B: the table applies only with Plating Index >= 0.40.
- Ring is half of (pad - tool). PTH tool = finished + 0.10 mm, NPTH tool = finished ([Drilled Holes](https://www.eurocircuits.com/pcb-design-guidelines/drilled-holes/)).
- "The highest pattern class possible depends on the copper thicknesses" and "Do not design your board up to the limits of any given classification" (Classification page).
## 1. Measured values vs limits

Holes (PTH.drl, NPTH.drl): 1200 in total.

| Finished (mm) | Tool (mm) | Count | X2 function | Pad (mm) |
|---|---|---|---|---|
| 0.25 | 0.35 | 44 | ViaDrill | 0.45 |
| 0.30 | 0.40 | 1106 | ViaDrill | 0.60 |
| 0.40 | 0.50 | 16 | ComponentDrill | 0.92 inside M6 pad |
| 1.00 | 1.10 | 8 | ComponentDrill | 1.70 |
| 1.02 | 1.12 | 13 | ComponentDrill | 1.80 |
| 1.85 | 1.95 | 8 | ComponentDrill | 3.20 |
| 6.40 | 6.50 | 1 | ComponentDrill | 14.0 |
| 2.70 NPTH | 2.70 | 4 | ComponentDrill | none |

| Parameter | L1 | L2 | L3 | L4 | Limit at 70 um | Result |
|---|---|---|---|---|---|---|
| Min track (mm) | 0.200 (30 segments) | no copper below 0.19; tracks 0.30 | same as L2 | no copper below 0.19; tracks 0.25 | 0.200 | at limit |
| Min gap, different nets, exact (mm) | 0.200 | 0.200 | 0.200 | 0.200 | 0.200 | at limit (S3) |
| Smallest same-net gap (mm) | 0.045 | about 0.10 to 0.13 | about 0.13 | 0.062, 0.10, 0.15 | 0.200 | S5 |
| Ring 0.25 vias, tool based (mm) | 0.05 (44) | 0.05 (20) | 0.05 (12) | 0.05 (44) | 0.100 at class 9 | **fail** (B1) |
| Ring 0.30 vias, tool based (mm) | 0.10 (34) | >= 0.15 | 0.10 (20) | 0.10 (438) | 0.150 class 4; 0.100 class 9 | B2 |
| Ring, component holes (mm) | >= 0.30 | >= 0.30 | >= 0.30 | >= 0.30 | 0.150 | pass |
| IPI unconnected hole, exact (mm) | - | 0.200 (218 holes) | 0.200 (230); 0.110 same net (2) | - | 0.225 class 4; 0.200 class 6-9 | S4 |
| Copper to edge (mm) | 0.545 | 0.695 | 0.795 | 0.795 | 0.25 outer, 0.40 inner | pass |

The 0.25 mm via counts on L2 and L3 are the vias with a pad on that layer; on other layers the unused pad is removed.

| Parameter | Measured | Limit | Result |
|---|---|---|---|
| Smallest tool | 0.35 mm | Drill class C | class C |
| Aspect ratio | 1.6 / 0.35 = 4.6 | 1:8 on tool | pass |
| Drill to drill, tool edge | 0.16 mm (2 pairs); next 0.30 mm | 0.25 mm | B3 |
| Hole to edge | 1.05 mm (NPTH) | none found | pass |
| NPTH to copper | 0.245 mm (raster) | IPI 0.225 | pass |
| Mask web | top 0.295 mm at (19.37, 44.05) and (68.82, 39.95); bottom >= 0.30 mm | MSM 0.075 mm ([Soldermask](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/soldermask/)) | pass |
| Mask clearance (MAR) | 0 in data, openings 1:1 on pads (`pad_to_mask_clearance 0`) | MAR 0.030 mm, but ["You can deliver the solder-mask windows at the same size as the pads and we will make the necessary adjustments"](https://www.eurocircuits.com/blog/eurocircuits-data-preparation-single-image-part/) | pass, except EPC2361 (S6) |
| Mask overlap (MOC) | not measured directly; derived >= 0.15 mm (1:1 openings, gap >= 0.20, less 0.05 growth) | 0.060 mm | pass |
| Smallest mask opening | 0.30 mm (58 openings below 0.40, all top) | 0.40 mm | S6 |
| Openings across two nets | none, top or bottom | - | pass |

**Class this board needs.** As drawn: track and gap class 4, drill class C, but the ring is outside the table, so there is no valid
class (class 10 has no service). The smallest value decides the class, so the ring sets it. Whether a fixed board exists at 70 um
inner copper depends on how Eurocircuits reads the base copper table:

- **Strict reading** (70 um allows class 4 at most): OAR and IAR 0.150, IPI 0.225. Class 4 exists in all services, but this board does
  not meet it: every isolated via pad fails.
- **Loose reading** (the base copper table limits only track and gap, as printed): the ring can go down to class 9, which needs
  S, DZ or RF service. Whether a class 9 ring is accepted with 70 um foil is not stated publicly. This is question 1.

Via options if Eurocircuits reduces the hole or the design changes it (pad unchanged):

| Pad (mm) | Finished (mm) | Tool (mm) | OAR = IAR (mm) | Pattern class by ring | Drill class |
|---|---|---|---|---|---|
| 0.60 | 0.30 (drawn) | 0.40 | 0.100 | 9 | C |
| 0.60 | 0.25 | 0.35 | 0.125 | 6 | C |
| 0.60 | 0.20 | 0.30 | 0.150 | 4 | D |
| 0.45 | 0.25 (drawn) | 0.35 | 0.050 | none | C |
| 0.45 | 0.20 | 0.30 | 0.075 | none | D |
| 0.45 | 0.15 | 0.25 | 0.100 | 9 | D |
| 0.45 | 0.10 | 0.20 | 0.125 | 6 | E (max 1.60 mm: no margin on this board) |

## 2. Blockers

### B1. 44 vias 0.25 / 0.45 mm have a 0.05 mm ring

- **Evidence:** PTH.drl tool T1 0.250, production tool 0.35 mm. F_Cu and B_Cu: 44 pads 0.45 mm, ring (0.45 - 0.35) / 2 = 0.05 mm, measured 0.05 at all 44. Same on In1_Cu (20) and In2_Cu (12). Examples (14.67, 54.67), (17.0, 52.9), (20.5, 44.65). Gate, Kelvin and driver supply nets.
- **Limit:** OAR and IAR 0.100 mm minimum at class 9; below that is class 10, no service.
- **Failure:** the job stops with an exception at [data analysis](https://www.eurocircuits.com/tips-tricks/eurocircuits-data-preparation-analysis/). If built with the drill as given, ordinary drill offset breaks the barrel out of the pad: an open or high-resistance gate or Kelvin path that passes visual inspection.
- **Rescue:** they may reduce vias by up to 0.30 mm to solve ring issues ([Drilled Holes](https://www.eurocircuits.com/pcb-design-guidelines/drilled-holes/)). 0.25 becomes 0.15 mm (tool 0.25): ring 0.10, class 9, drill class D. That is the only route without layout change, and it depends on question 1.
- **Action:** ask question 1. If class 9 is refused, move to pad 0.60 / finished 0.20 mm. Only 14 of the 44 have room for that (+0.075 mm radius at 0.20 mm clearance); 26 others have less than 0.05 mm of room and 4 are the B3 pairs. So about 30 vias need re-routing.

### B2. 0.30 / 0.60 mm vias have a 0.10 mm ring

- **Evidence:** T2 0.300, tool 0.40 mm, ring 0.10 mm where the pad is isolated: 34 on L1, 20 on L3, 438 on L4. L4 includes the via rows at y 61.3, 66.3, 71.55, 73.45 and the shunt arrays at y 45.3 to 47.4. Examples (5.6, 73.45), (7.55, 24.2), (8.6, 46.7). The other vias on L1 sit in copper.
- **Limit:** OAR 0.100 fits class 8 or 9. IAR 0.100 on L3 fits class 9 only (class 8 IAR is 0.125). Class 4 needs 0.150.
- **Failure:** if class 9 is refused at 70 um: exception and hold, or a via reduction outside our control, so the built holes differ from the release data and the model.
- **Action:** set the finished hole to 0.25 mm (ring 0.125, class 6, drill class C) or 0.20 mm (ring 0.15, class 4, drill class D). No copper change: drill size only, plus the via list. This also clears S4. Ask sim-analyst to confirm the loop value is insensitive to barrel diameter.
### B3. Two via pairs 0.16 mm apart on tool size

- **Evidence:** PTH.drl (24.900, 49.800) and (25.000, 50.300), net KL1; (72.400, 49.800) and (72.500, 50.300), net KL2. Centre distance 0.510, tool 0.35, edge to edge 0.160 mm. KiCad passes it at 0.26 mm because its rule uses the finished hole.
- **Limit:** 0.25 mm edge to edge on tool size ([Drilled Holes](https://www.eurocircuits.com/pcb-design-guidelines/drilled-holes/)). [Below 0.15 mm is not allowed in any service](https://www.eurocircuits.com/tips-tricks/eurocircuits-data-preparation-analysis/), so this sits between the two.
- **Failure:** a 0.16 mm wall between two holes risks cracking and drill deflection, on the Kelvin return. Pads are only 0.062 mm apart on L1 and L4 (S5). Same net, so no short, but an exception at analysis and a reliability weak point.
- **Action:** replace each pair by one via, or move them to at least 0.60 mm centres. Each pair is a same-net hop, so check why both are needed. Reducing to 0.15 mm finished would also give 0.26 mm.

### B4. Build-up not available as specified from public data

- **Evidence:** fab notes lines 6-12: prepreg 0.10 mm, core "for 1.60 mm total", 70 um on all layers.
- **Limit:** [Eurocircuits' pool materials](https://www.eurocircuits.com/blog/review-standard-and-predefined-build-ups-2/): prepreg PR1080 70 um, PR2116 120 um, PR7628 180 um. Cores 100, 200, 360, 710 um with foil up to 70/70. Cores 510, 1000, 1200 um for special build-ups only, stock not guaranteed. [STANDARD pool](https://www.eurocircuits.com/services/standard-pool/): 4 layers pooled only at 1.00 mm, inner copper pooled 18 and 35 um, others in the online calculator. [Special build-up](https://www.eurocircuits.com/ec-smart-tools-user-guides/pcb-configurator/material-section/): no online price, their technical team makes a proposal.
- **My estimate, not their data** (nominal values, resin loss = (1 - copper density) x 70 um, L2 density 0.68, L3 0.63):

| Dielectric option | L1-L2 over copper | L3-L4 over copper |
|---|---|---|
| 1 x 1080 | about 48 um, too little resin for 70 um copper | about 44 um |
| 1 x 2116 | about 98 um | about 94 um |
| 2 x 1080 | about 118 um | about 114 um |

- Total with 1 x 2116 per side: foil 0.14 + prepreg 0.24 + core 1.00 + inner copper 0.14 = 1.52 mm, about 1.59 mm with plating and mask. A 710 um core gives about 1.3 mm, so the build needs the 1000 um special core.
- 1 x 2116 lands closest to 0.10 mm, but as a single ply. Their [lay-up description](https://www.eurocircuits.com/pcb-multilayer-fabrication-layup-and-bond/) uses two sheets per side, and their [2010 standard 4-layer build](https://be.eurocircuits.com/basic/Documents/EC-STD-buildups-0-8-layers-GERMAN-1-2010-V3.pdf) had 2 x 7628 (0.40 mm), four times the design spacing.
- **Failure:** a predefined build gives a much thicker L1-L2 dielectric, and 0.646 nH per cell no longer describes the board. Too little resin gives voids around 70 um inner copper, including at the 3 mm barrier gaps.
- **Action:** send question 2 before any layout work. Then run Q3D at the dielectric they confirm. Do not order from the calculator without a written stack-up.

## 3. Should fix

### S1. Filling only the listed vias reopens the other 928

- **Evidence:** `DPT_JLC_order.md` lines 82-87: "If Eurocircuits fills a selected set, give them `fab/via_in_pad.csv`" and "Confirm in the order whether they fill all vias or the listed set". Fab notes lines 3 and 21: all vias covered, the barrier relies on it. 1150 vias, 222 listed.
- **Limit:** ["Fully Tented Via Holes with spray coating is only possible in conjunction with Via Filling"](https://www.eurocircuits.com/technical-guidelines/pcb-manufacturing-technology/soldermask-for-via-holes-and-pads/). All other holes are opened; ["In case a hole has no defined Soldermask opening we will define one to be equal to the TOOSIZE"](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/soldermask/).
- **Failure:** 928 vias are delivered with open barrels, 0.35 to 0.40 mm mask openings. The "all vias tented" assumption of the barrier is silently lost.
- **Action:** order **all vias filled** ([normal data + option in Advanced options](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/via-filling/)). Remove the "or the listed set" wording. A selected set would also need a Via Filling layer or manual marking; a CSV is not one of their listed methods.

### S2. Outer copper: "70 um finished" is not one of their outcomes

- **Evidence:** fab notes lines 6 and 12: "70 um (2 oz) finished".
- **Limit:** [Copper tolerances](https://www.eurocircuits.com/technical-guidelines/understanding-manufacturing-tolerances-on-a-pcb/tolerances-on-copper-thickness/): start 35 um gives nominal about 60 um, minimum 47.9 um. Start 70 um gives nominal about 95 um, minimum 78.7 um. Inner 70 um: minimum 55.7 um.
- **Failure:** "70 um" is read as start copper and the board comes with about 95 um and a 0.200 mm minimum gap, or 35 um is chosen and it comes with about 60 um, below the thermal and resistance assumption. Either way the copper differs from the model without anyone deciding.
- **Trade-off:** start 35 um lowers the outer gap limit to 0.125 mm, which gives S3 real margin on L1 and L4. Start 70 um is their recommendation when a 70 um minimum must be guaranteed.
- **Action:** Enes decides, then state start foil and expected final thickness in the notes.

### S3. Different-net gaps are exactly at the 70 um limit

- **Evidence:** exact vector minimum 0.2000 mm on all layers. Copper object pairs at or below 0.2014 mm: L1 66, L2 33, L3 17, L4 132. Examples: L1 EPC2361 land gaps (x 29.555 to 29.750, y 55.9), L2 (34.345, 75.805) DCN-DCP, L3 (5.775, 35.33) SW-VEEA1, L4 (2.305, 47.135) SW-DCN.
- **Limit:** 0.200 mm at 70 um, and "Always allow for a small margin above the classification limits".
- **Failure:** on 95 um finished outer copper a 0.20 mm gap has a height-to-width near 1:2. Under-etch leaves narrowed gaps or shorts found at electrical test, and yield drops. EPC2361 land gaps come from the datasheet and cannot move.
- **Action:** ask question 3. Widen to 0.225 mm where routing allows, inner layers first (inner copper has no thinner foil option if 70 um stays). Outer layers: S2 with start 35 um.

### S4. IPI 0.200 mm vs 0.225 mm at class 4

- **Evidence:** exact: 218 holes on L2, 230 on L3 at 0.200 mm (plane clearance 0.25 mm from the finished hole), e.g. (10.338, 66.3) on L2, (10.338, 61.3) on L3. The two 0.110 mm cases at (25.0, 50.3) and (72.5, 50.3) on L3 are same net and vanish with B3.
- **Limit:** IPI 0.225 at class 4 and 5; 0.200 at class 6 to 9. Minimum IPI = IAR + 0.075 mm, at least 0.200 mm.
- **Failure:** under the strict reading this is a class violation and a hold. Physically, drill offset eats into a 0.20 mm wall between barrel and plane.
- **Action:** fixed by the B2 drill reduction: tool 0.35 gives IPI 0.225, tool 0.30 gives 0.250. No separate work.

### S5. Same-net copper gaps far below 0.200 mm

- **Evidence (raster):**
  - L1 0.045 mm at (17.64, 36.03) GNDI1 and (65.14, 36.03) GNDI2, a pinch in the zone fill.
  - L1 and L4 0.062 mm at (24.93, 50.06), (72.43, 50.06), the B3 via pads.
  - L4 0.10 mm between 0.60 mm via pads at 0.70 mm pitch in the shunt arrays, 96 pairs, e.g. (8.6, 47.05). L4 0.15 mm, 4 pairs.
  - L3 about 0.13 mm where anti-pads almost merge, 16 places, e.g. (3.095, 47.405); similar notches on L2, e.g. (24.945, 50.055).
- **Limit:** [Copper Layers](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/copper-layers/): avoid peelables by meeting the class rules even within one net; webs must meet the class.
- **Failure:** a thin strip of resist in a 0.045 to 0.10 mm slot lifts during processing and lands elsewhere as a short or nick. Their analysis may also report these as the minimum gap, so the job gets queried.
- **Action:** on L4 replace each shunt array by a solid DCN patch: removes the 96 gaps and about 148 of the B2 rings at once, and each array already sits in its own cut-out. Refill the L1 GNDI zones with a larger min width or add a short track over the pinch. Have sim-analyst check the L4 patch against the loop model.
### S6. EPC2361 mask-defined pads and their mask correction

- **Evidence:** F_Cu and F_Mask at y 55.9: copper fingers 0.655 mm, mask openings 0.305 x 3.405 mm centred on them, so mask overlaps copper by 0.175 mm each side (32 openings, nets SW, DCP, LSRC). 26 more openings about 0.355 x 0.755 mm (2EDF7275K pads). These 58 are below 0.40 mm; every other opening is above. Fab notes do not mention mask-defined pads.
- **Limit:** ["The minimum SM opening is 0.40mm"](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/soldermask/); data preparation ["Check and correct the clearance between the copper pad and the edge of the soldermask"](https://www.eurocircuits.com/blog/eurocircuits-data-preparation-single-image-part/). I found no public statement on mask-defined pads.
- **Failure:** CAM treats the openings as an error and opens them to pad + MAR, about 0.71 mm wide. Solder then wets the full finger, the land no longer matches the EPC drawing, and only the 0.20 mm copper gap separates DCP and SW solder: bridging or tilt on all 8 FETs.
- **Action:** add a note: "F_Mask openings on Q1-Q8 are solder-mask-defined per EPC2361 datasheet; do not modify". Ask question 4. Order Pre-Production Approval and compare the mask before release.

### S7. Fab notes and job file are JLC-worded or wrong

Evidence in `fab/gerber/spb-bb-revb-dpt-fab-notes.txt`:

| Line | Text | Problem at Eurocircuits |
|---|---|---|
| 7, 11 | "JLC 3313: 0.0994" | prepreg style not in their list |
| 9 | "JLCPCB stack-up JLC04161H-3313" | names another fab's product as the build |
| 16 | "pad >= drill + 0.15 mm (JLCPCB via rule...)" | ring from the hole, not the tool |
| 17 | "annular ring >= 0.254 mm (JLCPCB 2 oz)" | hole based, they measure from the tool |
| 18 | "Hole-to-hole 0.25 mm" | finished size; 0.16 on tool size (B3) |
| 18 | "copper to board edge 0.30 mm" | looser than their inner 0.40 rule; actual board is 0.695 mm |
| 21 | "JLCPCB: order 'Epoxy Filled & Capped'" | not their option name |
| 6, 12 | "70 um (2 oz) finished" | see S2 |

`spb-bb-revb-dpt-job.gbrjob`: `Finish: None` (should be ENIG), `Revision: rev?`, Size 89.6 x 85.3 (outline is 89.5 x 85.2; line width included), no dielectric or copper thickness in `MaterialStackup`. The `.kicad_pcb` has no stack-up section either, so a native KiCad upload carries no build data.

- **Failure:** the configurator reads the job data and starts from the wrong finish, or an operator tries to follow "JLC04161H-3313" and the job stops. Anyone trusting the via rules in the notes misses B1 to B3. [Instructions must be "evidently clear in the actual layout data"](https://www.eurocircuits.com/pcb-design-guidelines-input-data-requirements/).
- **Action:** write a fab-neutral stack-up table with Eurocircuits' confirmed build. Set finish and revision so the job file is right. Keep JLC values only in `DPT_JLC_order.md`, and split the Eurocircuits section into its own file.

### S8. Copper imbalance between L1 and L4

- **Evidence:** copper density over the board: L1 0.606, L2 0.677, L3 0.635, L4 0.439. Upper half (y > 42.6): L1 0.659, L4 0.312. Lower half: L1 0.552, L4 0.566. L2 / L3 are close (0.762 / 0.713 upper).
- **Limit:** [bow and twist 0.75 % for SMD](https://www.eurocircuits.com/technical-guidelines/understanding-manufacturing-tolerances-on-a-pcb/bow-and-twist-on-a-pcb/), about 0.67 mm over 89.5 mm, twist about 1.85 mm. Their advice: spread copper evenly. Plating Index >= 0.40 is a condition of the class table; [below it they expect plating problems](https://www.eurocircuits.com/plating-index/). The formula is not public, so I could not compute it.
- **Failure:** with 70 um copper, the 35-point L1-L4 difference in the DC-link half can bow that half. Paste then prints unevenly at the EPC2361 and LGA parts. Low L4 density with isolated pads also raises plating non-uniformity. Likelihood not quantified.
- **Action:** upload to PCB Visualizer and read the Plating Index and copper-per-layer report. If low, add same-net copper on L4 in the upper half, away from the barrier.

## 4. Notes

- **N1. Resin fill limits are met.** [Via Filling](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/via-filling/): tool 0.20 to 0.60 mm, end size 0.10 to 0.50 mm, board 1.00 to 2.40 mm, outer start copper min 12 um, no max. Both 0.25 and 0.30 mm fit (tool 0.35 / 0.40, aspect 4.6 / 4.0). No numeric aspect limit is published. All vias or a selected set are both offered. Always Type VII, via-in-pad allowed, not UL certified. Class 2 acceptance is 60 % of hole volume, and ["A complete filling can't be guaranteed"](https://www.eurocircuits.com/technical-guidelines/pcb-manufacturing-technology/via-filling-eurocircuits-have-invested-in-the-itc-thp-30-machine/), so do not count on the resin as insulation. Every via has pads on both outer layers, as they require.
- **N2. Hole rounding.** Sizes round to the nearest 0.05 mm, so the 13 test-loop holes 1.02 become 1.00 mm, tolerance +-0.10 mm. Check the Adafruit 3825 lead fit at 0.90 mm, and REDCUBE 1.85 mm with the same +-0.10.
- **N3. Hole density.** 1200 holes on 0.763 dm2 = 1574 per dm2, above the configurator default "< 1000/dm2" ([Technology section](https://www.eurocircuits.com/user-guides/visualizer-user-guides/pcb-configurator-user-guide/technology/)). Affects price.
- **N4. The sixteen 0.40 mm bolt stitching holes.** X2 says ComponentDrill, but holes <= 0.45 mm count as vias by default. They are open in the mask on both sides. Filled or not, both work electrically; state which, and set "Holes <= may be reduced" deliberately because it also controls B1 and B2.
- **N5. Outline.** Only in `Edge_Cuts.gm1`, 0.10 mm line. [Rule 10](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/10-rules-for-better-data/) asks for it on all layers as well. Not a stopper: offsets are consistent and X2 `SameCoordinates` is set.
- **N6. Legend.** Thinnest line 0.10 mm, at their [minimum](https://www.eurocircuits.com/pcb-design-guidelines/legend-print/). KiCad text rule 0.8 mm is below their 1.00 mm readable height. They clip legend near mask openings, so text next to pads shortens.
- **N7. Assembly (only touched).** No fiducials on the board. `fab/jlc` CPL is in JLC format; `fab/spb-bb-revb-dpt-pos.csv` shares the origin (C13 at 18.0 / 45.4 mm, bottom). The assembly side was not reviewed here.

## 5. Direct answers

**Task 1, class:** see section 1. Target after fixes: class 4 track and gap, ring class 6 or 4, drill class C or D. Pattern class 4 is on the table for all services; 70 um inner at 4 layers 1.6 mm is unconfirmed.

**Task 2, build-up:** 70 um inner is not pooled and needs the calculator or a Special build-up. 0.10 mm prepreg is not in the published list; 1 x 2116 comes closest by my estimate. On request at best. Resin fill: both drill sizes fit, all or a selected set possible, but this board needs all vias (S1). Copper balance: S8.

**Task 3, files:**

| Item | Status |
|---|---|
| File set | Complete: 4 copper, 2 mask, 2 legend, 2 paste, outline, PTH, NPTH, job file, flat zip |
| Format | Gerber X2 mm 4.6 and Excellon mm decimal, both accepted |
| Origin | One origin: outline 0,0 to 89.5,85.2; drills, pos file and via list agree |
| PTH / NPTH split | Correct: 1196 PTH, 4 NPTH, X2 ViaDrill on the 1150 vias |
| Via list | 222 entries, all found in PTH.drl with matching drill; 218 vias reach or touch a mask opening, all listed. CSV not in the zip; the same table is in the fab notes |
| Fab notes | Mislead (S7) |

## 6. Not confirmed from public sources

- The [online calculator](https://be.eurocircuits.com/shop/assembly/configurator.aspx) does not render without a browser session, so I could not see whether 70 um inner / 70 um outer at 1.6 mm appears as a predefined build. The 940 predefined builds are not listed publicly.
- Whether a class 9 ring is permitted with 70 um copper.
- Pressed prepreg thickness over 70 um copper, single-ply policy, core stock with 70/70 foil. The material list comes from a blog post, not a specification, and the 4-layer build sheet is from 2010.
- Plating Index for this board, and via cap and pad plating thickness.
- How CAM treats mask-defined pads.
- Prices and lead times.

## 7. Questions for Eurocircuits (ready to send)

> Subject: Pre-order technical inquiry: 4-layer 1.6 mm board, 70 um copper, all vias resin filled
>
> We plan an 89.5 x 85.2 mm power board, 4 layers, 1.6 mm, ENIG, IPC class 2, green mask, 1150 vias (1106 at 0.30 mm, 44 at 0.25 mm finished). Please advise:
>
> 1. **Annular ring at 70 um.** Your classification table limits 70 um copper to 0.200 mm track and gap. Does it also limit the board to pattern class 4 values (OAR and IAR 0.150, IPI 0.225), or may rings go to class 8 / 9 values with 70 um outer and 70 um inner copper? What is the smallest OAR and IAR you accept here, on tool size?
> 2. **Build-up.** Can you offer 4 layers, about 1.6 mm, 70 um inner copper, with a dielectric of 0.10 mm (+-0.02 mm) between L1-L2 and L3-L4 after pressing? Please give the exact build: prepreg styles and number of plies, core thickness and foil, calculated total, and the pressed thickness over copper at 65 % copper density. Is a single 2116 ply acceptable over 70 um copper? Is the 1000 um core with 70/70 foil available? Would a reverse build-up with 100 um 70/70 cores on L1-L2 and L3-L4 be possible, and if so, what fills the centre?
> 3. **Outer copper and gaps.** Which outer start foil do you recommend for about 70 um finished (35 um gives about 60 um, 70 um gives about 95 um)? Do you accept 0.200 mm gaps with no margin at 70 um start on outer and inner layers, including 3.4 mm long parallel runs between pads?
> 4. **Solder-mask-defined pads.** The GaN FET lands have mask openings of 0.30 x 3.4 mm on 0.65 mm wide copper, following the device datasheet, so the mask overlaps the copper by 0.175 mm. Other openings are 0.35 x 0.75 mm. Will you keep these openings unchanged despite your 0.40 mm minimum opening? If you need a marking, how should we supply it?
> 5. **Via filling.** All 1150 vias filled and capped, mask covering those without openings in the data. Any limit on number or density (1574 holes per dm2)? What is the cap and pad copper thickness on 70 um (or 35 um) start foil, and the planarity of the cap for via-in-pad? Does the fill step change the minimum gap of 0.20 mm next to via pads?
> 6. **Via reduction.** If we keep pads 0.45 mm and finish 0.15 mm (tool 0.25), or pads 0.60 mm and finish 0.20 or 0.25 mm, which technology class results, and is it compatible with questions 1 and 5?
> 7. **Copper balance.** Outer density is 0.61 top and 0.44 bottom, with 0.66 / 0.31 in one half of the board. Is this acceptable for bow and twist 0.75 %, or do you want copper added?
> 8. **Service.** Which service applies (STANDARD non-pooled, Special build-up)? Is Pre-Production Approval available on it, and what are the price and lead time for 5 boards?

## 8. Suggested order of work

1. Send the questions; hold the order until 1 and 2 are answered.
2. Make the no-regret changes now: all-vias wording (S1), fab notes and job file (S7), mask note (S6).
3. pcb-layout, after answers: via drills (B2, S4), the 44 small vias and two pairs (B1, B3), L4 patches and zone fills (S5), inner gap widening (S3).
4. fab-release: regenerate, re-check against Eurocircuits' limits, and add tool-based ring and drill-to-drill rules to the DRC. Today's clean DRC says nothing about them.
5. sim-analyst: Q3D at the confirmed dielectric and copper. Paper and slide numbers follow only after that.
6. Upload to PCB Visualizer and order with Pre-Production Approval.
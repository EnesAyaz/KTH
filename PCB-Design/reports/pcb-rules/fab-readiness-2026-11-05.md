# Fab readiness of the Rev B DPT board: go / no-go per manufacturer

Date: 2026-11-05. Reviewer: design-reviewer (fresh audit, no history with the board). Read-only on the repo apart from this file.
Board `hardware/spb-bb-revb-dpt`, SHA-256 `bdcca1a3...ca3965a`, last board commit 1b464f3e, the same file the 2026-11-04 reviews saw.
Load board and busbar are out of scope. Nothing was committed. Coordinates are fab mm (origin bottom-left, outline 0..89.5 x 0..85.2).

## Verdict

| Manufacturer | Today | Reason | Ready after |
|---|---|---|---|
| **JLCPCB** | **NO-GO** as written | The Gerbers and drills pass every published JLC geometry rule, with wording questions open on the via ring and the fill range. The order specification does not exist as a product: JLC04161H-3313 is a 1 oz / 0.5 oz build. The 2 oz / 2 oz build in JLC's stack-up data is JLC041622-3313 with **0.1835 mm** L1-L2, not 0.10 mm. | No Gerber change needed. Enes chooses the stack-up, JLC confirms it, Q3D runs on it, notes are corrected (section 5, path J) |
| **Eurocircuits** | **NO-GO** | 4 blockers stand (B1 to B4). I found no reason to doubt the measurements. | Written answers to the inquiry, then via drill change or CAM reduction, a fix at the KL pairs, a written build-up, Q3D, regenerated package (section 5, path E) |

Neither manufacturer is ready. JLC is closer on data: it needs no copper or drill change. Eurocircuits may be closer on the loop value: its estimated 2 oz builds land near 0.10 to 0.12 mm, where JLC's lands at 0.18 mm.

**The same stack-up problem exists at both houses.** A single thin prepreg ply does not fill 70 um inner copper. JLC's data shows this directly: 3313 x 1 at 0.092 to 0.0994 mm is offered only with 0.5 oz or 1 oz inner copper, and 2 oz inner copper gets two plies. So **0.10 mm dielectric and 70 um inner copper cannot both be had at JLC** on its listed builds, and at Eurocircuits this is unconfirmed (B4). That choice is Enes's and comes first.

**The release data itself is sound.** I found no wrong copper or connectivity. Regeneration is identical, zip equals folder, one origin. The problems are the rule set it was checked against and the stack-up statement.

## Ordered list for Enes

Steps 1 to 3 cost nothing and can start today.

1. **Decide what is fixed: 0.10 mm L1-L2, or 70 um inner copper.** Section 2.3 gives the numbers. This sets the manufacturer more than any other item.
2. **Open JLC's live order page** (4 layers, 1.6 mm, outer 2 oz, inner 2 oz) and record which stack-ups it offers and their prepreg thickness. Do the same with inner 1 oz. I could not read that page (it needs a browser session), so this checks the one piece of evidence that is second-hand.
3. **Send both inquiries.** Eurocircuits: the 8 questions in the manufacturability review, section 7, plus question 9 in section 3.3 here. JLC: the 5 questions in section 2.4.
4. **Choose the manufacturer** from the replies. Do not order from either calculator without a written stack-up.
5. **Path J (JLC):** correct the stack-up name, thickness and via rule wording in `DPT_JLC_order.md` and the fab notes (F01, F10). No Gerber change.
   **Path E (Eurocircuits):** apply the via changes of section 3.2 by board change or written CAM reduction, fix the two KL pairs, regenerate, and add tool-based ring and drill-to-drill checks to the DRC (F03 to F06).
6. **Decide the silk fixes** (F16, F17). They are not gates. If path E regenerates the Gerbers anyway, add them in the same pass, because they then cost almost nothing.
7. **Correct the files on both paths:** fab-neutral notes and job file with finish ENIG and revision set (F10), BOM order code XUMA2, screw, IDC socket and lab cable (F19 to F22), and a pos file without the 9 unfitted rows if Eurocircuits assembles (F18).
8. **Run Q3D at the confirmed dielectric and copper** (`h_diel`, `h_34`, `t_L2`, `t_L3` in the `STACK` of `bb_q3d_revb.py`). Accept the build only if the HS peak stays under 100 V. Paper, digest and slide numbers follow after that, not before.
9. **Buy long-lead parts before committing to a date:** EPC2361, 2EDF7275KXUMA2, 74650174R, 66012102111404, 744232601, TSM header, UFCS-R001 (F23).
10. **Last check, then order.** Eurocircuits: PCB Visualizer upload, read Plating Index and class, order with Pre-Production Approval, compare the EPC mask openings (F09, F11). JLC: tick "confirm production file", put the fill remark in the order (F13), compare the mask in the production file. Fill all vias at either house.

## 1. All findings, merged

Sources: **M** manufacturability, **E** electrical, **A** assembly (reviews of 2026-11-04), **L** layout review PDF of 2026-10-30, **new** = this audit.
Severity: **blocker** (wrong manufacturing data, or not buildable as specified), **fix** (fix before order), **proto** (acceptable for a prototype).
Who: **board** / **file** (fab or doc file, no copper) / **fab Q** (question to the manufacturer) / **Enes** / **bench**.
"Before order" gives JLC / Eurocircuits. Status was checked against the release files as stated in each row.

### Open: manufacturing

| ID | Source | What | Severity | Status and evidence | Who | Before order (JLC / EC) |
|---|---|---|---|---|---|---|
| F01 | M-B4, A-S2, L stack-up item, **new** | 0.10 mm prepreg with 70 um inner copper is not a published build. Stack-up code in order notes and fab notes is wrong for JLC | blocker | Open. Fab notes line 9 and order notes line 13 still say JLC04161H-3313 with 2 oz / 2 oz; section 2.2 | fab Q, Enes | yes / yes |
| F02 | M-S2, A-S2 | "70 um finished" outer copper: Eurocircuits gives about 60 or about 95 um | fix at EC | Open, fab notes lines 6, 12. At JLC, 2 oz finished is what is sold, 0.07 mm in its data | Enes, file | no / yes |
| F03 | M-B1, A-S1 | 44 vias 0.25 / 0.45: ring 0.05 mm on tool size | blocker at EC | Open. Re-measured: 44 pads 0.45 on L1 and L4, 20 on L2, 12 on L3. JLC's via rule is met (+0.20 mm), see F12 | fab Q, then board or CAM | no / yes |
| F04 | M-B2, A-S1 | 1106 vias 0.30 / 0.60: ring 0.10 mm on tool size | blocker at EC | Open. Re-measured: 1106 pads 0.60 on L1 and L4 | fab Q, then board or CAM | no / yes |
| F05 | M-B3 | KL1, KL2 via pairs, 0.51 mm centres: 0.16 mm on tool size, limit 0.25 | blocker at EC | Open. Drill file (24.9, 49.8)-(25.0, 50.3), (72.4, 49.8)-(72.5, 50.3). Finished edge 0.26 mm passes JLC's 0.20 | board | no / yes |
| F06 | M-S4 | Inner hole to plane 0.200 mm against IPI 0.225 at class 4 | fix at EC | Open. Closes with F04, no separate work | board | no / yes |
| F07 | M-S3, A-S2, L DC-link spacing | Different-net gaps exactly 0.200 mm on all 4 layers | fix at EC; proto at JLC | Open. JLC limit 0.15 mm, so 0.05 mm margin there. At EC it is the limit, zero margin | fab Q; board if refused | no / yes (answer needed) |
| F08 | M-S5 | Same-net gaps 0.045 to 0.15 mm, peelable risk | fix at EC; proto at JLC | Open. JLC publishes no same-net rule | board at EC | no / after EC reply |
| F09 | M-S6 | EPC2361 and 2EDF mask-defined openings: CAM may open them to pad size. 58 openings below EC's 0.40 mm | fix | Open. No note in fab notes. JLC publishes no minimum opening and lists mask 1:1, but the same CAM risk applies | file, fab Q | yes / yes |
| F10 | M-S7, A-S3, A-N12 | Fab notes and job file are JLC-worded and carry wrong metadata | fix | Open. Fab notes: 7 lines name JLC, 0 name Eurocircuits. `.gbrjob`: `Finish: None`, `Revision: rev?`, size 89.6 x 85.3. No stack-up in `.kicad_pcb` | file | yes / yes |
| F11 | M-S8, M-N3 | Copper imbalance L1 / L4 0.66 / 0.31 in the upper half; hole density 1574 per dm2 | proto at JLC; fix at EC | Open. Density re-measured: L1 0.607, L2 0.678, L3 0.635, L4 0.440. Read the Plating Index in Visualizer | fab Q | no / yes |
| F12 | **new** | "Annular rings (resolved 2026-10-23)" is overstated. JLC's "PTH annular ring" row, 2 oz multilayer: 0.254 mm or above. The page does not say whether vias are excluded; board vias are 0.15 and 0.10 mm hole-based | fix | Open; section 2.1. Failure: JLC's CAM applies 0.254 and holds the job, or enlarges pads, which cannot fit at 0.20 mm gaps | fab Q | yes / no |
| F13 | M-S1, A-S3, **new** | Fill all vias. EC: a selected set opens the other 928. JLC: its via-covering page wants the plugging diameter in the order remarks, and the order notes do not say so | fix | Partly closed. Order notes line 85 now says ALL, but lines 88-89 still say "Confirm in the order whether they fill all vias or the listed set". JLC remark missing | file | yes / yes |
| F14 | **new** | JLC fill range "via diameters from 0.15 to 0.55 mm" against 0.60 mm pads. The order notes quote this range without comment | fix | Open; section 2.1. Probably means hole size, but "via diameter" is the pad elsewhere on the same page. Failure: fill refused or job held after payment | fab Q | yes / no |
| F15 | A-S12, A-N6, M-N7 | No fiducials on the board; paste on RS1-RS4 and DNP pads | fix at EC; JLC rails cover it | Open. 225 footprints, none a fiducial. JLC: rails with fiducials. EC: confirm the alignment method. Tell the assembler paste with no part is intended, or drop it | fab Q, Enes | no / yes if EC assembles |
| F37 | **new** | M6 hole 6.40 mm is above JLC's multilayer drill row of 0.15 to 6.3 mm | proto | Open; PTH.drl T7. Failure: engineering query that delays the job; a routed plated hole has looser tolerance, which is fine for an M6 bolt | fab Q | ask with F12 / no |

### Open: board silk, BOM and assembly data

| ID | Source | What | Severity | Status and evidence | Who | Before order (JLC / EC) |
|---|---|---|---|---|---|---|
| F16 | A-S4 | No IN / SHLD mark at RS1-RS4. A reversed shunt ties the earthed scope to LSRCx | proto | Open. A written direction in the setup note would also do; `SHLD` does not appear there today | board (silk) or file, Enes | no / no; do it if Gerbers regenerate |
| F17 | A-S13 | U1, U2 have no pin-1 mark. A rotated driver gets supplies on the wrong pins | proto | Open. Check in the placement preview: pin 1 at (19.05, 39.65) and (66.55, 39.65) | board (silk), Enes | no / no; do it if Gerbers regenerate |
| F18 | A-S14 | Generic pos file has 9 unfitted rows (R16-R19, R35-R38, J21); DNP attribute not set | fix at EC | Open. Re-counted: pos 179, CPL 170, difference exactly those 9; 0 footprints with DNP attribute. Failure: 0 R links fitted, U.FL stubs on 8 gates | file | no / yes if EC assembles |
| F19 | E-S2, A-S8 | M4 x 8 screw bottoms in the 4.0 mm blind thread | fix | Partly closed. Setup note item 3 warns, BOM still says M4 x 8. Does not touch the PCB order | file (BOM), bench | no / no, before bring-up |
| F20 | A-S10 | BOM names a male header (Wurth 61201021621) as control-cable socket | fix | Open, BOM mechanical line. Lab part | file (BOM) | no / no, before bring-up |
| F21 | A-S11, **new** | Driver order code. BOM and JLC BOM say 2EDF7275KXUMA1; the local datasheet Rev 3.0 Table 30 lists **2EDF7275KXUMA2**, package PG-TFLGA-13-4 | fix | Half closed. E verified the land pattern against Rev 3.0 Fig. 21-22. The code is still wrong. Failure: sourcing buys XUMA1, which Digi-Key lists as PG-TFLGA-13-1 (A-S11) | file (BOM, JLC BOM) | yes if assembled / yes if assembled |
| F22 | **new** | Lab BOM example Amphenol 095-850-207-006 is a **BNC jack (female), bulkhead**, with right-angle MMCX plug, not "BNC male". It will not mate with the BNC-female CT3889 adapter on the next line | fix | Open; [Digi-Key](https://www.digikey.ch/en/products/detail/amphenol-rf/095-850-207-006/9655882), 12 weeks standard lead time. PE3C1904 is listed as MMCX plug to BNC male, so use that one | file (BOM) | no / no, before bring-up |
| F23 | A-N9 | 8 BOM lines without MPN; long-lead items | proto | Open. JLC BOM: 0 of 29 lines have an LCSC number, so every line needs manual matching | Enes | matching is part of the JLC order / no |
| F24 | A-S7 | REDCUBE: 150 um stencil and THR against EPC 100 um and "hand or selective soldering". Order notes and JLC BOM disagree. Two codes, 74650174 and 74650174R | fix | Open. Failure: weak joints on the terminals carrying all bus current | file, fab Q | yes if assembled / yes if assembled |
| F25 | A-N1 | TSM header: no -P suffix for machine placement; connector reversible | proto | Open | file, bench | with F23 |
| F26 | A-N2 | `testpoints.csv` uses origin (150, 100), y down; everything else uses the board origin | proto | Open, rows confirm it (TP1 -25.55, 27.50). Lab document, not sent to the fab | file | no / no |
| F27 | M-N2, M-N4, M-N5, M-N6, A-N11, A-N12, A-N13, A-N14 | Hole rounding 1.02 to 1.00 at EC; 16 x 0.40 holes count as vias; outline in one layer only; legend 0.8 mm text; leftover `drc_tp_tmp.txt`; saved plot settings differ from the script; schematic has no test points | proto | Open. `useauxorigin false`, `subtractmaskfromsilk false` confirmed in the board file. State the 0.40 holes in the order | file, Enes | no / no |
| F28 | L KiCad 10 housekeeping, E stale comment | Zone overlaps flagged in KiCad 9/10; schematic sync would rename nets; generator comment says 12 bypass caps | proto | Open, process only: keep using the generator, never sync | none | no / no |

### Open: bench only (no effect on the order)

| ID | Source | What | Severity | Status | Who |
|---|---|---|---|---|---|
| F29 | E-S1 | DC link sags to about 61 V at 322 A without the 1 mF bulk in the SPICE deck | fix before test | Open in the setup note; a 1 uH / 80 V simulation is running per the log | bench |
| F30 | E-S3 | V_DS ports not Kelvin; MMCX reads about +99 mV | fix before test | Mostly closed: setup note lines 111-112 cover the MMCX. Spring pads (+70 mV) are not stated | bench |
| F31 | A-S5, A-S6, L soldering | No shunt soldering procedure; TP45 / TP46 unrelieved in planes | fix before test | Open. Setup item 2 still only says "preheat". Procedure is in A, "Hand assembly" | bench |
| F32 | E-N1, E-N3, E-N4, E-N5 | Zener current, shunt gain 0.957 mV/A, short IN land, shield choke | proto | Open: `0.957` and UFCS-Choke do not appear in the setup note | bench |
| F33 | E-N2, A-N10 | Q4, Q8 have no V_DS spring pad; use MMCX | proto | Open, accepted in both reviews | bench |
| F34 | E-N6 to E-N10 | Kelvin bypass of shunt, outer / inner cell spread, unkeyed headers and INA/INB without interlock, In1 shield, pad 2 use | proto | Open, no action or bench care | bench |
| F35 | A-N3, A-N4, A-N5, A-N7, A-N8, L shunt bodies, L driver placement | Mechanical stack, lugs near TP45/46, dense 0805 rows, shunt strain relief, MLCC margin | proto | Open, bench care | bench |
| F36 | L silk | "DESIGNED BY CLAUDE" on the top silk | proto | Open, present in the board file | Enes |

### Closed, verified

| ID | Source | What | Verified how |
|---|---|---|---|
| C1 | L must-fix | One SW via per cell | Closed. L1 Gerber: 15 SW vias per cell. 14 at x 1.6/2.6, 39.4/40.4, 49.1/50.1, 86.9/87.9 (y 50.5 to 55.0), plus the old one at x 15.55, 26.45, 63.05, 73.95, y 53.75. L1 SW regions join them to the FET islands. PTH count 1196 |
| C2 | L via list | 4 DC+ vias missing from the list | Closed. (14.65, 27.35, 62.15, 74.85; 58.3) are in `via_in_pad.csv` as in_pad |
| C3 | A-S9, L MLCC flex | Torque procedure and wrong MLCC count | Closed in text: setup note lines 138-140 give 1.2 N m, block support, C67 / C68 at 7.63 mm |
| C4 | M-N1 | Resin fill limits at EC | No action: tool 0.35 / 0.40 inside limits; also true after E2 and E3 |

## 2. JLC recheck against the current pages (2026-11-05)

### 2.1 Measured geometry against published rules

Measured from `fab/gerber/` and the drill files with my own Gerber and Excellon reader in the scratch folder. Copper clearances come from a 10 um raster, which reads about 0.01 mm low. Exact values from review M are given where they exist.

Limits from [JLC capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) (page carries no date) unless noted.

| Item | JLC limit | Measured | Result |
|---|---|---|---|
| Copper offered | Multilayer outer 1 / 2 oz; inner 0.5 / 1 / 2 oz, 0.5 oz default | 2 / 2 oz wanted | Offered; conditions in 2.2 |
| Min track, 2 oz multilayer | 0.15 mm ([copper weight page](https://jlcpcb.com/help/article/jlcpcb-copper-weight), updated 2026-09-09: 0.16 mm any layer) | 0.200 L1 (30 segments), 0.30 L2 / L3, 0.25 L4 (apertures) | Pass |
| Min space, 2 oz multilayer | same | 0.200 exact (M); raster 0.188 to 0.194 | Pass, 0.04 to 0.05 mm margin |
| SMD pad to pad, different nets | 0.15 mm | 0.200 (EPC land) | Pass |
| Via hole / diameter | Min 0.15 / 0.25 mm; diameter 0.1 larger, 0.15 preferred | 0.25 / 0.45 (+0.20, 44 vias), 0.30 / 0.60 (+0.30, 1106) | Pass |
| Via surcharge | 0.2 or 0.25 hole with diameter under 0.45 costs more | 0.45 exactly | No surcharge |
| "PTH annular ring", multilayer 2 oz | 0.254 mm or above; scope not stated | Vias 0.10 and 0.15, hole-based. Component holes 0.26 (0.40 / 0.92), 0.35, 0.39, 0.675, 3.8 | Component holes pass. **Vias: question (F12)** |
| Via hole to hole | 0.2 mm | 0.26 (KL pairs), next 0.40 | Pass |
| Pad hole to hole | 0.45 mm | 0.907 mm; M6 to stitching 1.0 mm | Pass |
| Via hole to track | 0.2 mm | 0.287 outer | Pass |
| PTH to track | Min 0.28, 0.35 recommended | 0.587 outer | Pass |
| Inner via hole to copper | 0.2 mm | 0.237 raster (0.25 by design) | Pass |
| Inner PTH hole to copper | 0.3 mm | 0.537 | Pass |
| NPTH to track | 0.2 mm | 0.239 | Pass |
| Copper to routed edge | 0.2 mm | 0.55 (L1), 0.70, 0.80, 0.80 | Pass |
| Mask dam, 2 oz | Min pad spacing 0.20 mm, any colour | Web between openings: 0.30 top at (9.14, 49.75) (M: 0.295), 0.385 bottom, 10 um raster | Pass |
| Drill range, multilayer | 0.15 to 6.3 mm | 0.25 to 6.40 mm | M6 hole 0.10 above the row (F37) |
| Fill: hole size | [Via covering page](https://jlcpcb.com/help/article/pcb-via-covering), 2026-09-09: holes not over 0.5 mm. [POFV blog](https://jlcpcb.com/blog/Free-Via-in-Pad-on-6-20-Layer-PCBs-with-POFV), 2022: 0.2 to 0.5 mm | 0.25, 0.30 | Pass |
| Fill: "via diameters from 0.15 to 0.55 mm" | Capabilities page | Pads 0.45, **0.60** | Question (F14) |
| Fill: ring | POFV blog: 0.05 min, 0.075 preferred | 0.10, 0.15 | Pass |
| Fill: distance to regular PTH / NPTH | POFV blog: more than 0.45 mm | 0.619 mm hole edge, (86.4, 4.4) to the NPTH at (87.1, 2.4) | Pass |
| Fill: order | Via covering page: give the plugging diameter in the remarks | Not in order notes | Fix (F13) |

- **F12 ring.** The published via rule is "Via diameter should be 0.1mm (0.15mm preferred) larger than Via hole size". The other row is "PTH annular ring ... 2 oz: 0.254 mm or above". The page never says the second excludes vias. The 2026-10-23 reading (vias follow the first rule) is the natural one, and a [question on JLC's help site about this](https://jlcpcb.com/help/answers/detail/110-minimum-via-size-vs.-minimum-annular-ring-size) has no answer. "Resolved" is not earned until JLC says so. If 0.254 did apply, 0.30 mm holes would need 0.81 mm pads, which this board cannot take.
- **F14 fill range.** The lower bound of 0.15 equals the minimum hole on the same page, and JLC's other two pages limit holes, not pads. So this very likely means hole size, and 0.25 / 0.30 pass. But the page uses "via diameter" for the pad, and read that way all 1106 pads of 0.60 mm fail. One line in the inquiry settles it.

**Result: the Gerbers and drills fit JLC with none of Eurocircuits' B1 to B3 problems**, because JLC states its via rule from the hole and needs only 0.20 mm hole to hole. F12, F14 and F37 are questions, not measured failures.

### 2.2 Stack-up: this is the problem

The order notes say "JLC04161H-3313, prepreg 3313, 0.0994 mm L1-L2 and L3-L4", "2 oz / 2 oz", and "JLC: 2 oz inner only with 1.6 mm, JLC3313 and 2 oz outer, i.e. exactly this combination".

Current sources say:

| Source | Content |
|---|---|
| [JLC stack-up page](https://jlcpcb.com/impedance) | Form shows outer 1 / 2 oz and inner 0.5 / 1 / 2 oz. The static rows are all 0.035 mm outer, 0.0152 mm inner. JLC04161H-3313 has 0.0994 mm prepreg. No 2 / 2 oz row appears |
| [JLC calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator), updated 2026-09-16 | Calculator "only supports 0.5 oz and 1 oz" inner and 1 oz outer; for 2 oz inner "please contact customer support" |
| [JLC copper weight page](https://jlcpcb.com/help/article/jlcpcb-copper-weight), updated 2026-09-09 | Inner 2 oz availability depends on total layers and overall thickness. Nothing ties it to 3313 |
| [Hive issue 468](https://github.com/Hive-RSI-Lab/hive-hwde/issues/468), 2026-10-31 | JLC04161H-3313 live in JLC's calculator: 1 oz outer, 0.5 oz inner, 1.56 mm |
| [gsuberland stack-up dump](https://github.com/gsuberland/jlcpcb_autogenerated_stackups), raw JSON from JLC's template API, about 2025-05 | Table below |

The code itself gives it away: layers, thickness, outer copper, inner copper, with H for half ounce. JLC04161H is 1 oz / 0.5 oz; 2 / 2 oz is JLC041622.

3313 builds, 4 layers, 1.6 mm, from the raw JSON (`enableFlag: true` on those read):

| Code | Outer / inner | L1-L2 dielectric (mm) | Plies | Inner Cu (mm) | Core (mm) | Total (mm) |
|---|---|---|---|---|---|---|
| JLC04161H-3313 | 1 / 0.5 oz | 0.0994 | 3313 x 1 | 0.0152 | 1.265 | 1.564 |
| JLC04162H-3313 | 2 / 0.5 oz | 0.0994 | 3313 x 1 | 0.0152 | 1.265 | 1.634 |
| JLC041611-3313 | 1 / 1 oz | 0.092 | 3313 x 1 | 0.030 | 1.23 | 1.544 |
| **JLC041621-3313** | **2 / 1 oz** | **0.092** | 3313 x 1 | 0.030 | 1.23 | 1.614 |
| JLC041612-3313 | 1 / 2 oz | 0.2005 | 3313 + 2116 | 0.061 | 0.96 | 1.553 |
| **[JLC041622-3313](https://raw.githubusercontent.com/gsuberland/jlcpcb_autogenerated_stackups/main/raw_json/jlcpcb_4L_1.6mm_outer2oz_inner2oz_JLC041622-3313.json)** | **2 / 2 oz** | **0.1835** (0.107 + 0.0765) | 3313 x 2 | 0.061 | 0.96 | 1.589 |

The only other 2 / 2 oz build listed, JLC041622-7628, has about 0.44 mm.

Evidence grade: the dump is a third-party copy of JLC's own API, about 18 months old. Its JLC04161H-3313 values agree with the 2026-10-31 live reading, which supports it, but step 2 of the list must confirm it. It fits the physics in M-B4 and JLC's guide sending 2 oz inner to support.

**Failure scenario.** Enes selects 2 oz / 2 oz and 3313 as the notes say. The board arrives with 0.18 mm L1-L2, not 0.10 mm, with no warning. The 0.646 nH per cell, the 92.9 V peak and the paper numbers no longer describe it.

**Effect on the loop (hand estimate, not Q3D; no `h_diel` sweep exists in the repo).** Plate formula, 1.257 nH per mm of spacing per square. Delta h = 0.0835 mm over an assumed 0.6 to 1.0 squares of L1-over-L2 path gives +0.06 to +0.11 nH per cell, so about 0.71 to 0.75 nH per cell against 0.646. At 30 V per nH for 30 A/ns (19.4 V at 0.646 nH, `final_numbers.json`) the 94.4 V figure moves to about 96 to 98 V. Upper bound if all 0.463 nH of copper scaled with h: about 1.03 nH and about 106 V, above the 100 V rating, below the 120 V transient rating. The bound is unrealistic, but it is why Q3D must run before accepting this build.

### 2.3 What JLC can actually deliver

| Option | Gerber change | L1-L2 | Cost |
|---|---|---|---|
| **J-A: JLC041621-3313, 2 oz outer, 1 oz inner** | None | 0.092 mm, closest to the model (spacing effect about -0.01 nH per cell, hand estimate) | Inner copper 30 um, not 70: inner sheet resistance x 2.3. Pulse heating stays small: 40 A/mm peak (E) on 30 um is about 0.1 K per 11 us pulse. "2 oz on all layers" must change in notes and documents. Run Q3D once with h 0.092, t_L2 = t_L3 = 0.03. Skin depth at 100 MHz is 6.6 um, so loop L should barely move with inner thickness |
| **J-B: JLC041622-3313, 2 oz / 2 oz** | None | 0.1835 mm | About +10 to +16 % loop per cell, hand estimate. Q3D, SPICE peak and all published DPT loop numbers change |
| J-C: custom build via support | None | Whatever they offer | Not published. A single ply over 61 um copper risks voids, as in M-B4 |

Technical view: J-A keeps the loop spacing and is the fastest route. J-B keeps the copper the documents state. For a pulsed DPT board inner copper thickness is not limiting, but the choice is Enes's.

### 2.4 Questions for JLC (live chat or email, ready to send)

> 4-layer FR-4, 1.6 mm, 89.5 x 85.2 mm, ENIG, epoxy filled and capped vias, 2 oz outer.
> 1. Please confirm the stack-ups you offer today for 2 oz outer with 2 oz inner, and with 1 oz inner: template name, prepreg styles and plies, pressed thickness L1-L2 and L3-L4, core, finished total. Is JLC041622-3313 still 0.107 + 0.0765 mm? Can any 2 oz inner build reach about 0.10 mm?
> 2. Does "PTH annular ring, multilayer 2 oz: 0.254 mm or above" apply to vias? Our vias are 0.30 / 0.60 mm (1106) and 0.25 / 0.45 mm (44). Component holes have at least 0.26 mm.
> 3. Epoxy Filled & Capped is "compatible with via diameters from 0.15 to 0.55 mm". Is that hole size or pad size? Our pads are 0.60 mm with 0.30 mm holes.
> 4. We want all 0.25 and 0.30 mm holes filled and capped. We also have sixteen 0.40 mm plated holes inside a bolt pad and one plated 6.40 mm bolt hole (above your 6.3 mm drill row): any problem? Is capping compatible with 2 oz outer copper and 0.20 mm gaps next to via pads?
> 5. The GaN FET lands are solder-mask-defined (0.30 x 3.4 mm openings on 0.65 mm copper, per datasheet). Will you keep the mask openings as supplied?

## 3. Eurocircuits

### 3.1 Go / no-go

**No-go, 4 blockers open (M).** I spot-checked B3 (0.51 mm centres, both pairs), hole counts and the 20 / 12 inner pad counts of the 0.45 mm vias against the Gerbers: all agree. I had no reason to redo the rest. B1, B2 and S4 hinge on question 1, B4 on question 2.

### 3.2 Smallest change set, and what each costs

Barrel model: 1.6 mm, 20 um wall, 20 C, non-conductive fill. Partial inductance by the Grover formula for the full barrel.

| Finished (mm) | Tool (mm) | R per barrel (mOhm) | Change vs 0.30 | Partial L, 1.6 mm (nH) | Pulse heating vs 0.30 |
|---|---|---|---|---|---|
| 0.30 (drawn) | 0.40 | 1.37 | - | 1.30 | x 1 (worst via 0.09 K per pulse, E) |
| 0.25 | 0.35 | 1.62 | +18 % | 1.36 | x 1.4 |
| 0.20 | 0.30 | 1.99 | +45 % | 1.43 | x 2.1 |
| 0.15 | 0.25 | 2.58 | +88 % (+59 % vs 0.25) | 1.52 | x 3.5 |

| Step | Closes | Change | Cost and re-verification |
|---|---|---|---|
| E1 | Gate | Inquiry, questions 1, 2, 4, 5, 6 at least | Days. No data change |
| E2 | B2, S4 | 1106 vias 0.30 to **0.25** finished (tool 0.35): ring 0.125, class 6, IPI 0.225, drill class C | Pad and copper unchanged. Via R +18 %; SW island path 1.02 mOhm rises by at most that fraction. Loop: the commutation loop stays on L1 and L2 (E, L), and vias enter only as short hops in parallel arrays: below 1 pH per cell by hand, inside Q3D mesh noise (0.007 nH). The bottom bypass branch is worth 0.019 nH in total, so a 5 % via change there is about 1 pH. **No separate Q3D run needed**; it rides along with E5 |
| E2 alt | B2, S4, strict reading | 0.20 finished: ring 0.15, class 4, drill class D | Needed if 70 um means class 4 at most. R +45 %, heating x 2.1 (0.19 K), still harmless |
| E3 | B1, B3 | 44 vias 0.25 to **0.15** finished (tool 0.25): ring 0.10, class 9, drill class D. KL pairs become 0.26 mm on tool size (limit 0.25, margin 0.01) | Works only if class 9 is allowed at 70 um (question 1); class 9 needs S, DZ or RF service. Aspect 6.4, fill limit met. Series R is mOhm against 3.5 Ohm gate resistance. L +0.16 nH per via against a gate loop of 12.5 to 21 nH: at most about 2 % with gate and Kelvin vias together. Re-run the gate SPICE only if the margin to -4 V is tight |
| E3 alt | B1 | If class 9 is refused: pad 0.60, finished 0.20 | **Layout work:** 14 vias fit, about 30 re-route (M). Full DRC, connectivity, gate-loop Q3D. Biggest cost in the list |
| E4 | B3 | If E3 is not taken: one via in place of each KL pair, or at least 0.60 mm centres | Two small edits per block. Keep the Kelvin route, check In1 and In2 pads |
| E5 | B4 | Written build-up. Estimate from M: 1 x 2116 about 98 / 94 um, 2 x 1080 about 118 / 114 um | Q3D at the confirmed dielectric. 2 x 1080 is about +0.014 to +0.023 nH per cell by the plate formula. Only then the paper numbers |
| E6 | S1, S2, S6, S7 | File edits only: all vias filled, start foil and final thickness stated, mask note, fab-neutral notes, job file | Regenerate notes and zip |

**Absolute minimum.** If Eurocircuits says yes to questions 1 and 6, no KiCad change is needed: E2 and E3 can be done with the "may be reduced" option in CAM, which allows up to 0.30 mm. Then only E1, E5, E6 remain. Get the reduction in writing, record the final holes in the fab notes, and check it at Pre-Production Approval. A silent reduction is what A-S1 warned against.

**Any data change needs this re-verification:** regenerate Gerbers and drills, DRC, a new tool-based check for ring and drill-to-drill (today's DRC cannot see them), re-run the via list since smaller drills change the near_pad set, update notes and zip, compare with this report.

### 3.3 One extra question for Eurocircuits

> 9. If 70 um inner copper is the obstacle: can you offer 35 um inner copper, 35 or 70 um outer start copper, with 0.10 mm (+-0.02 mm) L1-L2 and L3-L4, 1.6 mm total, and what are the pattern class limits then?

Why: the classification row for 35 um is 0.125 mm track and gap. That would give F07 real margin on the inner layers and could lift the strict reading of question 1 to class 7 (ring 0.125), which E2 meets. It mirrors option J-A at JLC.

## 4. Fab package consistency, as of today

### Consistent (checked in the scratch folder)

| Check | Result |
|---|---|
| Regeneration | kicad-cli 7.0 on a scratch copy, release flags. 11 Gerbers, job file, PTH, NPTH: 0 differing lines apart from dates |
| Zip vs folder | 15 of 15 byte-identical. The folder has 2 more files, the drill map PDFs |
| Holes | PTH 1196 = 1106 + 44 vias + 46 component; NPTH 4 x 2.70. Same as order notes |
| BOM vs board | 182 references, all on the board, quantities match, footprints match. The other 43 footprints: 38 TP, H1-H4, J21 |
| Three new lab lines | Mechanical section, 5 columns, so `make_jlc_files.py` skips them. JLC BOM stays exact (29 lines, 170 references = 170 "fit") |
| Loop test points | 13 in BOM = 13 in the line, footprint `TestPoint_Keystone5000_Adafruit3825` |
| CPL | 170 rows, 132 top, 38 bottom, same set as JLC BOM. Position against board within 1 nm; side and rotation equal to the pos file. Aux origin 105.25 / 160.8. C13 at 18.0 / 45.4 |
| Via list | CSV 222 rows (190 in_pad, 32 near_pad) = table in fab notes. All in `PTH.drl` with matching drill. Recomputed on the mask Gerbers at 10 um: exposed drills plus drills within 0.06 mm of an opening = exactly the 222 listed, none missing, none extra |
| Order notes counts | 1106 / 44, 222, 170, 38, 13 test loops, PTH 1196, NPTH 4: all right |
| Origin | Gerber, drill, CPL, pos, via list: one. `testpoints.csv` is the exception (F26) |

DRC was not re-run: the board hash is unchanged since the fresh 2026-11-04 runs (0 / 0 / 0) and `drc_report.txt` agrees.

### Stale or contradictory

| Where | Text | Problem | Finding |
|---|---|---|---|
| Order notes line 13, fab notes line 9 | JLC04161H-3313 with 2 oz / 2 oz | Code is 1 oz / 0.5 oz | F01 |
| Fab notes lines 7, 11; order notes line 13 | 0.0994 mm prepreg | Value belongs to 0.5 oz inner | F01 |
| Order notes line 14 | "2 oz inner only with 1.6 mm, JLC3313..." | Not on any current JLC page; 7628 also listed at 2 / 2 oz | F01 |
| Order notes line 5 | "limits checked on 2026-10-23" | Superseded by this report | - |
| Order notes line 18 | "JLC 2 oz: 0.16 mm" | Capabilities says 0.15 multilayer, copper page 0.16. Harmless | - |
| Order notes line 22 | "Annular rings (resolved 2026-10-23)" | Not resolved | F12 |
| Order notes lines 26-27 | Fill range 0.15-0.55 mm stated next to 0.60 mm pads | Wording conflict not noticed | F14 |
| Order notes lines 85 vs 88-89 | "Order ALL" against "all vias or the listed set" | Contradiction left over from the fix | F13 |
| Order notes line 3 vs 80 | "final release" against "fails Eurocircuits rules" | Status line does not reflect the likely fab | F10 |
| Order notes line 74 vs JLC BOM J1 note | "THT (hand or selective)" against "paste-in-hole or hand-soldered" | Process undecided; A-S7 wants 150 um paste | F24 |
| Fab notes, job file | 7 lines name JLC, 0 name Eurocircuits; Finish None, rev? | | F10 |
| BOM, JLC BOM | 2EDF7275KXUMA1 | Datasheet Rev 3.0 Table 30: XUMA2 | F21 |
| BOM against JLC BOM | J1, J2: 74650174 and 74650174R | Two codes for one part | F24 |
| BOM against setup note | M4 x 8 against "can bottom in the 4.0 mm thread" | | F19 |
| BOM mechanical | Wurth 61201021621 as socket | Male header | F20 |
| BOM lab line | Amphenol 095-850-207-006 under "BNC male" | Female bulkhead jack; will not mate with CT3889 | F22 |
| BOM lab line | PMK 4MM-BNC-F | I found no listing; verify before buying | F22 |
| BOM lab line | Probe "not chosen yet" | Blocks V_DS measurement, not the order | bench |
| Pos file | 179 rows | 9 unfitted | F18 |
| `testpoints.csv` | Origin (150, 100), y down | Differs from everything else | F26 |

None of these changes copper. All are text or data files, apart from what follows from F01 and F03 to F05.

## 5. Paths to "ready"

**Path J (JLC): ready after** live stack-up confirmed, Enes chooses J-A or J-B, JLC questions 2 to 5 answered, order notes and fab notes corrected (F01, F10, F12, F13, F14, F24), order code fixed (F21), Q3D run on the chosen build. No Gerber or drill change.

**Path E (Eurocircuits): ready after** questions 1, 2, 4, 5, 6, 9 answered, via drills changed or reduction agreed in writing (F03 to F06), gaps accepted or widened (F07, F08), written build-up (F01, F02), files made fab-neutral (F09, F10, F13, F18, F21), Q3D run on the confirmed build, Visualizer shows Plating Index at least 0.40 (F11), Pre-Production Approval ordered.

## 6. Not checked

- JLC's live order page and quote: needs a browser session. The stack-up table rests on a third-party copy of JLC API data plus one 2026-10-31 live reading of one entry.
- Eurocircuits' calculator, prices, lead times. Stock of any part.
- No Q3D or SPICE run: all inductance and overshoot deltas above are hand estimates, marked as such.
- DRC not re-run (board hash unchanged). Same-net gaps and class limits at EC are taken from M.
- JLC PCBA acceptance of this board: only via the order notes.
- Mask opening to neighbouring trace at JLC (0.09 mm rule): holds by construction with 1:1 openings and 0.20 mm gaps, not measured separately.
- `DPT_test_procedure.md` is being written in parallel and was not reviewed; F29 to F35 may change there.

## Sources

JLC: [capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [copper weight](https://jlcpcb.com/help/article/jlcpcb-copper-weight), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), [stack-up page](https://jlcpcb.com/impedance), [calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator), [POFV blog](https://jlcpcb.com/blog/Free-Via-in-Pad-on-6-20-Layer-PCBs-with-POFV), [via ring question](https://jlcpcb.com/help/answers/detail/110-minimum-via-size-vs.-minimum-annular-ring-size).
JLC data, third party: [gsuberland stack-ups](https://github.com/gsuberland/jlcpcb_autogenerated_stackups), [Hive issue 468](https://github.com/Hive-RSI-Lab/hive-hwde/issues/468).
Parts: [095-850-207-006 at Digi-Key](https://www.digikey.ch/en/products/detail/amphenol-rf/095-850-207-006/9655882), [PE3C1904 at findchips](https://findchips.com/detail/PE3C1904), [CT3889 listing](https://mcstaging.testequipmentdepot.com/caltest-ct3889-fully-insulated-bnc-female-to-sheathed-4mm-banana-plugs-coax-adapter-general-purpose-pack-of-5.html).
Local: `Datasheet/webfetch-1790845229554-qzkde0.pdf_datasheet.pdf` (2EDi Rev 3.0, Table 30); `simulation/bb_q3d/results/loop_breakdown.json`, `gate_summary_dpt.json`; `reports/slides/data/final_numbers.json`.
Eurocircuits limits: as cited in `independent-review-2026-11-04-manufacturability.md`.

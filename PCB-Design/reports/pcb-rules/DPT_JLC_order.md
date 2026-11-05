# DPT board (Rev B): ordering at JLCPCB with PCBA

Board: `hardware/spb-bb-revb-dpt`, final release (R_ON 1.5 Ω, JLC 2 oz rules; see the commit log). Files in `hardware/spb-bb-revb-dpt/fab/`:
Gerber zip `spb-bb-revb-dpt-gerber.zip` (with the fab notes), JLC BOM and CPL in `fab/jlc/`
(`scripts/make_jlc_files.py`). JLC limits checked on 2026-10-23 against their public capability pages; confirm on the
order page, which is binding.

**Status 2026-11-05: do not order yet.** The stack-up in this file is not confirmed at either manufacturer (JLC04161H-3313 is a 1 oz / 0.5 oz build); see `fab-readiness-2026-11-05.md`.

## PCB order settings

| Setting | Value | Note |
|---|---|---|
| Layers / thickness | 4 / 1.6 mm | |
| Stack-up | **JLC04161H-3313** | prepreg 3313, 0.0994 mm L1–L2 and L3–L4 (design: 0.10 mm, sets the commutation loop) |
| Outer / inner copper | **2 oz / 2 oz** | JLC: 2 oz inner only with 1.6 mm, JLC3313 and 2 oz outer, i.e. exactly this combination |
| Surface finish | ENIG | |
| Via covering | **Epoxy filled and capped (POFV)** | covers the via-in-pad list: **222 vias** = 190 in_pad (bypass, shunt SHLD and test pads) + 32 near_pad (drill edge within 0.05 mm of a mask opening); `fab/via_in_pad.csv`, also in the fab notes; all other vias are then filled too, which is fine (design asks for tented vias). **Must stay selected:** the list relies on filled + capped vias, e.g. the GH_L2 via in TP33 (0.57 mm off centre), the GNDI1 via on the TP1 pad edge and the 32 near-pad drills (2026-11-03) |
| Solder mask | green, both sides | 2 oz minimum web 0.20 mm: now the project rule; DRC clean. EPC2361 webs between different nets ≥ 0.28 mm |
| Min track / space | 0.20 / 0.20 mm in the design | JLC 2 oz: 0.16 mm |
| Remove order number | specify a location or "no" | keep it off the 1200 V barrier area |
| Confirm production file | **yes** | to get the engineering answer on the via ring below |

**Annular rings (resolved 2026-10-23).** JLC's capability page states separate rules:

- vias: "Via diameter should be 0.1mm (0.15mm preferred) larger than Via hole size", multilayer minimum
  0.15 / 0.25 mm. The board's 1106 power vias 0.60 / 0.30 mm (+0.30 mm) and 44 vias 0.45 / 0.25 mm (+0.20 mm), 1150 in all, meet
  it; 0.45 mm is not "less than 0.45 mm", so the via size carries no surcharge. Filled and capped via-in-pad is listed
  for via diameters 0.15–0.55 mm.
- plated component holes: "Multilayer: 2 oz: 0.254 mm or above". The AC bolt stitching holes were 0.40 / 0.80 mm
  (ring 0.20 mm) and are now 0.40 / 0.92 mm (0.26 mm); REDCUBE 0.675 mm, headers 0.35 mm. A custom DRC rule now
  enforces 0.254 mm on every plated pad.

**Via-in-pad list (2026-11-03).** The list now holds every via whose drill is exposed by a solder-mask opening on
either side, not only vias with their centre in a pad: 190 vias (was 184). The six added vias are the DC+ vias at
(14.650, 58.300), (27.350, 58.300), (62.150, 58.300), (74.850, 58.300) between the 0805 pads of the cell rows
(drill 0.06 mm into the top pad opening, 0.11 mm into the bottom ones), GNDI1 at (19.300, 33.800) at the edge of TP1
and GH_L2 at (62.170, 54.670) at the edge of TP33 (bottom). Checked against the plotted mask Gerbers: 190 drills
overlap an opening, all in the list, none extra. Rule and generator: `scripts/via_in_pad_list.py`.

**Near-pad vias added (Enes, 2026-11-03): 190 -> 218 -> 222.** Vias whose drill edge touches (is tangent to) or
comes within 0.05 mm of a solder-mask opening are now in the list too (column `reason` = `near_pad`, the others
`in_pad`), because mask registration at the fab (~±0.05 mm) can expose part of these holes. Margin 0.05 mm (drill
edge to merged opening) = 32 near-pad drills: the 28 tangent ones (gap 0.000 mm), 24 DC- vias at y 61.3 next to the
0805 pads C1.2-C12.2 / C34.2-C45.2 (top) and VEEA1/VDDB1 (20.5 / 21.5, 44.65), VEEA2/VDDB2 (68.0 / 69.0, 44.65) at
C14.2/C16.2/C47.2/C49.2 (bottom), plus the 4 Kelvin vias KH1 (7.550), KL1 (34.450), KH2 (55.050), KL2 (81.950) at
y 24.2, 0.047 mm from C22.2/C25.1/C55.2/C58.1 (top; added second, Enes approved). Not listed (clear of the margin):
DC- at 6.785/35.215/54.285/82.715, 61.3 (0.069 mm) and 16.262/25.738/63.762/73.238, 61.3 (0.093 mm). Checked on the
plotted mask Gerbers and the PTH drill file: 190 drills overlap an opening (all in_pad), 32 are within 0.05 mm (largest
gap 0.047 mm, all near_pad), list = Gerber set (222/222). Gerbers and drills unchanged; only `via_in_pad.csv`, the
fab notes and the Gerber zip changed.

**SW island stitching (2026-11-03).** Each top SW island now reaches the inner/bottom SW planes through 15 vias
instead of 1: +56 tented power vias 0.60 / 0.30 mm and 4 F.Cu SW zones (pre-fab layout review). PTH drill file
1140 -> 1196 holes, NPTH unchanged (4).

Still tick "confirm production file": the engineering question can then be answered on the actual CAM data.

## PCBA order settings

| Setting | Value |
|---|---|
| Assembly | Standard PCBA, **both sides** (38 of 170 placements on the bottom) |
| Tooling / fiducials | the board has no fiducials: let JLC add edge rails with fiducials |
| Not assembled | RS1–RS4 (UFCS shunts, hand-soldered in the lab), R16–R19 and R35–R38 (DNP 0 Ω U.FL links); spring pads and SMD test points are bare pads; the 13 loop test points (1.02 mm plated holes) get the Adafruit 3825 loops by hand in the lab |
| BOM / CPL | `fab/jlc/spb-bb-revb-dpt-BOM-JLC.csv`, `fab/jlc/spb-bb-revb-dpt-CPL-JLC.csv` |
| Coordinates | Gerbers, drills, CPL and the via-in-pad list share **one origin**: board bottom-left corner (x right, y up; outline 0..89.5 × 0..85.2 mm). In the preview, check that the parts sit on their pads (e.g. C13 at 18.0 / 45.4 mm, bottom) |
| Part matching | the "Comment" column holds the manufacturer part number; confirm each match in JLC's BOM tool |
| Parts JLC may not stock | EPC2361, 2EDF7275KXUMA1, Würth 74650174R (REDCUBE), 66012102111404 (WR-MMCX), 744232601 (WE-CNSW), Samtec TSM-105-01-T-DV: Global Sourcing, or consignment |
| Rotations | check every part in JLC's placement preview, especially EPC2361, 2EDF7275K (LGA-13), SOD-323F diodes, MMCX, U.FL and the REDCUBE |

Assembly checks before confirming:

- **EPC2361:** the footprint uses copper-only pads with graphical mask and paste openings (EPC land pattern). Confirm
  that JLC builds the stencil from `F_Paste` as supplied and use the stencil EPC recommends: 4 mil (100 µm), laser cut (EPC2361 datasheet p. 11).
- **REDCUBE J1 / J2:** through-hole-reflow parts on the bottom side; JLC places them as THT (hand or selective
  soldering). Confirm the M4 thread side and orientation in the preview.
- **MMCX and U.FL:** bottom side, check the polarity and orientation of the shield pads.

## If the board is ordered at Eurocircuits instead (Enes, 2026-11-03: likely)

**Status 2026-11-04: the release as designed fails Eurocircuits rules (4 blockers).** See `independent-review-2026-11-04-manufacturability.md`; send its eight questions before ordering.

The JLC-specific parts of this checklist (POFV naming, JLC PCBA, CPL format) do not carry over. Select / confirm:

1. **Via filling: resin filled, IPC-4761 Type VII "filled and capped"** (not VIb "filled and covered", which is not
   for via-in-pad). **Order ALL vias filled** (review 2026-11-04: Eurocircuits opens every unfilled hole, so a selected set would strip the tenting from the other 928 vias). `fab/via_in_pad.csv` is the must-have subset: **222 vias** = 190 in_pad +
   32 near_pad (drill edge within 0.05 mm of a mask opening: 24 DC- at y 61.3, VEEA/VDDB at 20.5/21.5 and 68/69,
   y 44.65, and the Kelvin vias KH1/KL1/KH2/KL2 at y 24.2; included because their mask registration of ~±0.05 mm can
   expose part of these holes).
2. **Stack-up:** 4 layers, 1.6 mm, 70 um (2 oz) copper on all four layers, 0.10 mm prepreg L1-L2 and L3-L4. The Q3D loop
   (0.646 nH per cell) assumes the 0.10 mm prepreg; a standard pool build-up with thicker prepreg raises it. Ask
   Eurocircuits for their exact build-up before ordering.
3. Finish ENIG, both sides solder mask, other vias tented (filled covers this).
4. Gerbers and drills are at the aux origin (board bottom-left); the pick-and-place file must be checked against
   Eurocircuits' assembly format if they assemble it.

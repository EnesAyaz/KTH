# DPT board (Rev B): ordering at JLCPCB with PCBA

Board: `hardware/spb-bb-revb-dpt`, final release (R_ON 1.5 Ω, JLC 2 oz rules; see the commit log). Files in `hardware/spb-bb-revb-dpt/fab/`:
Gerber zip `spb-bb-revb-dpt-gerber.zip` (with the fab notes), JLC BOM and CPL in `fab/jlc/`
(`scripts/make_jlc_files.py`). JLC limits checked on 2026-10-23 against their public capability pages; confirm on the
order page, which is binding.

## PCB order settings

| Setting | Value | Note |
|---|---|---|
| Layers / thickness | 4 / 1.6 mm | |
| Stack-up | **JLC04161H-3313** | prepreg 3313, 0.0994 mm L1–L2 and L3–L4 (design: 0.10 mm, sets the commutation loop) |
| Outer / inner copper | **2 oz / 2 oz** | JLC: 2 oz inner only with 1.6 mm, JLC3313 and 2 oz outer, i.e. exactly this combination |
| Surface finish | ENIG | |
| Via covering | **Epoxy filled and capped (POFV)** | covers the via-in-pad list (bypass and shunt SHLD pads); all other vias are then filled too, which is fine (design asks for tented vias) |
| Solder mask | green, both sides | 2 oz minimum web 0.20 mm: now the project rule; DRC clean. EPC2361 webs between different nets ≥ 0.28 mm |
| Min track / space | 0.20 / 0.20 mm in the design | JLC 2 oz: 0.16 mm |
| Remove order number | specify a location or "no" | keep it off the 1200 V barrier area |
| Confirm production file | **yes** | to get the engineering answer on the via ring below |

**Annular rings (resolved 2026-10-23).** JLC's capability page states separate rules:

- vias: "Via diameter should be 0.1mm (0.15mm preferred) larger than Via hole size", multilayer minimum
  0.15 / 0.25 mm. The board's 1050 power vias 0.60 / 0.30 mm (+0.30 mm) and 44 vias 0.45 / 0.25 mm (+0.20 mm) meet
  it; 0.45 mm is not "less than 0.45 mm", so the via size carries no surcharge. Filled and capped via-in-pad is listed
  for via diameters 0.15–0.55 mm.
- plated component holes: "Multilayer: 2 oz: 0.254 mm or above". The AC bolt stitching holes were 0.40 / 0.80 mm
  (ring 0.20 mm) and are now 0.40 / 0.92 mm (0.26 mm); REDCUBE 0.675 mm, headers 0.35 mm. A custom DRC rule now
  enforces 0.254 mm on every plated pad.

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

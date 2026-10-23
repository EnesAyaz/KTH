# DPT board (Rev B): ordering at JLCPCB with PCBA

Board: `hardware/spb-bb-revb-dpt` at commit 3c36e5c (R_ON 1.5 Ω). Files in `hardware/spb-bb-revb-dpt/fab/`:
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
| Solder mask | green, both sides | 2 oz mask web 0.20 mm: DRC at 0.20 mm shows no mask bridge |
| Min track / space | 0.20 / 0.20 mm in the design | JLC 2 oz: 0.16 mm |
| Remove order number | specify a location or "no" | keep it off the 1200 V barrier area |
| Confirm production file | **yes** | to get the engineering answer on the via ring below |

**Open point: annular ring at 2 oz.** JLC's capability table gives 0.20 mm minimum annular ring for 2 oz PTH
(0.13 mm for 1 oz). The board has 1050 power vias 0.6/0.3 mm (ring 0.15 mm) and 44 vias 0.45/0.25 mm (ring 0.10 mm,
gate / Kelvin / sense vias in the corridor). Ask JLC engineering (order comment or support) whether this is accepted.
If not: power vias 0.7/0.3 and signal vias 0.65/0.25 mm, which needs a layout pass (corridor clearances, plane
antipads) and a new Q3D loop and gate run.

## PCBA order settings

| Setting | Value |
|---|---|
| Assembly | Standard PCBA, **both sides** (38 of 174 placements on the bottom) |
| Tooling / fiducials | the board has no fiducials: let JLC add edge rails with fiducials |
| Not assembled | RS1–RS4 (UFCS shunts, hand-soldered in the lab), R16–R19 and R35–R38 (DNP 0 Ω U.FL links); test points and spring pads are bare pads |
| BOM / CPL | `fab/jlc/spb-bb-revb-dpt-BOM-JLC.csv`, `fab/jlc/spb-bb-revb-dpt-CPL-JLC.csv` |
| Part matching | the "Comment" column holds the manufacturer part number; confirm each match in JLC's BOM tool |
| Parts JLC may not stock | EPC2361, 2EDF7275KXUMA1, Würth 74650174R (REDCUBE), 66012102111404 (WR-MMCX), 744232601 (WE-CNSW), Samtec TSM-105-01-T-DV: Global Sourcing, or consignment |
| Rotations | check every part in JLC's placement preview, especially EPC2361, 2EDF7275K (LGA-13), SOD-323F diodes, MMCX, U.FL and the REDCUBE |

Assembly checks before confirming:

- **EPC2361:** the footprint uses copper-only pads with graphical mask and paste openings (EPC land pattern). Confirm
  that JLC builds the stencil from `F_Paste` as supplied and ask for the stencil thickness EPC recommends.
- **REDCUBE J1 / J2:** through-hole-reflow parts on the bottom side; JLC places them as THT (hand or selective
  soldering). Confirm the M4 thread side and orientation in the preview.
- **MMCX and U.FL:** bottom side, check the polarity and orientation of the shield pads.

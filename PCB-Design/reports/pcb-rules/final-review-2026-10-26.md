# Final PCB and manufacturing-package review

Date: 26 October 2026. Scope: `hardware/spb-bb-revb-dpt`, single-level 75 V DPT prototype.

**Decision: keep the PCB layout. No confirmed copper or circuit-connectivity defect was found that requires another layout revision. Resolve the manufacturing-coordinate inconsistency before approving automated assembly. The bare-board Gerbers and drills agree with each other and with the saved PCB.**

Reviewed PCB SHA-256:

```text
c632d0d9aad401f96218be079dd196fe5b3d1792e96d0ab27e7c68a007ee3685
```

All 82 original files under the board folder retained their initial hashes during this review. Checks and renders used temporary copies; only this report was added.

## 1. Independent checks

| Check | Result |
|---|---|
| Fresh KiCad DRC with saved project/custom rules | 0 violations, 0 unconnected pads, 0 footprint errors |
| DRC after independent copper refill | 0 violations, 0 unconnected pads, 0 footprint errors |
| Saved DRC exclusions | None |
| Circuit connectivity versus freshly exported schematic netlist | 86 connected circuit nets match after removing test points from both sides of the comparison |
| Schematic test points present on the board | Checked named-net assignments; no differences found |
| Independently regenerated Gerbers | All 11 match after ignoring generation timestamps |
| Independently regenerated PTH/NPTH drills | Both match after ignoring generation timestamps |
| Gerber ZIP | All 15 entries match the release-folder files |
| JLC BOM versus CPL | 170 references each, no missing references or duplicate references |
| CPL versus PCB | All 170 share the same coordinate transform; sides and KiCad rotations agree |
| Main BOM values versus saved footprints | No differences in checked fitted/DNP entries |
| Plated component-pad annular ring | Minimum measured nominal ring 0.26 mm, at J21 |
| Circular plated component-hole spacing | Minimum measured hole-edge gap approximately 0.908 mm |
| Copper review | Fresh renders of all four layers inspected |

Clean DRC applies to enabled checks; ignored library-footprint checks do not independently certify custom footprints. This review did not repeat field extraction, switching simulation, full schematic ERC or a dimensional audit against every manufacturer's footprint drawing.

## 2. One manufacturing issue to close

### Coordinate origins differ across the package

**Classification: assembly-release issue; no copper change required.**

The files are internally consistent in groups, but do not share one coordinate origin:

| File group | Coordinate convention |
|---|---|
| Gerbers and PTH/NPTH drills | Absolute PCB coordinates, with Y inverted in the exported coordinates |
| Main placement file and JLC CPL | Relative to PCB point (105.25, 160.8) mm, with Y inverted; this is the board's bottom-left corner |
| Via-in-pad list embedded in fabrication notes | Relative to the older point (150, 100) mm, with Y inverted |

Concrete example: C13 is at PCB position (123.25, 115.4) mm. The CPL lists (18.0000, 45.4000) mm. The Gerber coordinate system places that location at (123.25, −115.4) mm. The uniform translation is recoverable, but must not be assumed to happen correctly without checking the assembled-board preview.

The first via-in-pad list entry, (−13.8, −2.5) mm, corresponds to PCB position (136.2, 102.5) mm, or Gerber/drill position (136.2, −102.5) mm. The fabrication notes do not clearly explain this separate reference frame.

**Recommended resolution:** export Gerbers, drills, placement data and coordinate lists using a common documented origin. Alternatively, have the assembler explicitly align the CPL and confirm all placements in its preview; identify the via-list coordinate transform in the manufacturing instructions. Do not move footprints or alter the board to correct an export-origin issue.

Ordering all vias epoxy-filled and capped reduces the practical risk of selecting the wrong holes from the via-in-pad list. Nevertheless, clarify the coordinates instead of providing an ambiguous selective-treatment list. The Gerbers and drills themselves align, so this is not evidence that the bare board would be drilled in the wrong place.

JLC's assembly guidance specifically identifies mismatched Gerber/CPL origins as a placement error to resolve: [Files needed for PCB assembly](https://jlcpcb.com/blog/files-needed-for-pcb-assembly).

## 3. Previous concerns that do not justify another layout cycle

- **Via rings:** the 1,050 vias at 0.60/0.30 mm and 44 at 0.45/0.25 mm meet JLC's published via diameter-versus-hole guidance. The larger annular-ring guidance for plated component holes is a separate requirement; the checked minimum component-pad ring is now 0.26 mm. The earlier blanket objection to these via rings is closed.
- **Mask web:** the project now specifies 0.20 mm, matching the fabrication notes. The previous documentation mismatch is closed.
- **PWM chokes:** the PWM_H/PWM_L chokes have been removed in this revision. Direct signal/return routing and the 47 Ω / 100 pF input filters remain. The earlier PWM-choke concern does not apply unchanged to this board; chokes remain on other circuits.
- **Power and gate loops:** the compact cells, nearby bypassing, individual gate resistors, Kelvin routing and local output decoupling remain reasonable for an instrumented prototype. I found no new visual reason to reroute them. Residual inductance, SW coupling and current sharing are bring-up measurements, not reasons to keep redesigning without evidence.
- **Measurement ports:** retain the rated isolated-probe arrangement, local spring pads and DNP gate-sense links. No additional connector change is requested by this review.

Source for separate via and component-hole manufacturing guidance: [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/).

## 4. Minor items that can pass for this prototype

- The ordering document still says 174 assembly placements; the final BOM/CPL contain **170**, consistent with removal of four PWM chokes. Use the actual final files. This stale count is not an electrical fault.
- No onboard fiducials: use the documented assembler-added rails/fiducials. This is a panelization arrangement, not a reason to revise the circuit layout.
- Generic resistors and headers, blank LCSC fields and special-order components require part matching in the assembly order. The files provide a usable starting point but are not an already-approved supplier component selection.
- The broad SW copper and unused measurement stubs are accepted prototype tradeoffs. Route external control/probe cables away from SW and evaluate their effect experimentally.

## 5. Final order and bring-up conditions

For manufacturing, use the specified 4-layer, 1.6 mm, 2 oz/2 oz stack-up with approximately 0.10 mm outer dielectrics, ENIG and epoxy-filled/capped vias. Confirm the custom EPC2361 stencil and placement orientation in the supplier's normal CAM/assembly approval. Library rotations may differ even though the CPL matches KiCad. The four UFCS shunts remain laboratory-installed; eight gate-sense links remain DNP.

For operation, retain staged DPT and the documented per-channel gate-bias adjustment. The gate-voltage tolerance assessment already identifies narrow negative-voltage margin; nominal 7 V supply alone is not qualification. Check gate minima/maxima, effective dead time, U1/U2 skew, VDS overshoot and individual shunt currents before raising energy. These are hardware validation tasks, not additional fabrication blockers.

This disposition covers a **single-level 75 V research prototype**, not continuous full-current operation or a 1200 V stack. The functional-isolation driver and complete system insulation architecture remain separate from PCB fabrication readiness.

**Practical release recommendation:** resolve or obtain explicit CAM acceptance of the coordinate origins, complete the normal part/stencil/placement approval, and proceed with a small prototype order. Do not start another power/gate layout revision for the minor observations above.

Temporary evidence: `C:/Users/enesa/AppData/Local/Temp/spb-final-20261026`.

## Disposition (Claude, 26 October 2026)

PCB unchanged (same `.kicad_pcb`, DRC 0/0); only the exported manufacturing files were corrected.

| Item | Action |
|---|---|
| 2. Coordinate origins | **Fixed.** Gerbers (`--use-drill-file-origin`), PTH/NPTH drills (`--drill-origin plot`), CPL and the via-in-pad list now all use the drill/place origin = board bottom-left corner (KiCad aux origin 105.25 / 160.8 mm), x right, y up. Gerber outline 0..89.5 × 0..85.2 mm; C13 CPL (18.0, 45.4) lies between its two B_Cu pad flashes (18.0, 44.625 / 46.175). The fab notes state the common origin; the generator writes the via list in this frame from now on (`scripts/make_kicad_bb_revb.py`), the saved list was translated (x + 44.75, y + 60.8 mm; first entry C10.1 now 30.95 / 58.30). |
| 4. Stale count (174) | Fixed in `DPT_JLC_order.md`: 170 placements, 38 on the bottom. Also added: common-origin check in the JLC preview, EPC stencil 4 mil (100 µm) laser cut, the 13 loop test points are hand-fitted. |
| 4. Fiducials, part matching, SW copper | Accepted as written (JLC edge rails with fiducials; confirm every match in JLC's BOM tool). |
| 3, 5 | Agreed, no layout change. Bring-up checks stay in `DPT_measurement_setup.md`. |

`fab/testpoints.csv` (lab document) keeps the leg-centre frame used in the measurement notes; it is not sent to JLC.

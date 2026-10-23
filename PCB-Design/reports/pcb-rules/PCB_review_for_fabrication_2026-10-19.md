# PCB review for fabrication: SPB Rev B DPT

Date: 19 October 2026. Scope: the updated `hardware/spb-bb-revb-dpt` design and fabrication package. This review supersedes the earlier report's findings where the design has changed.

**Disposition: conditional GO for fabrication of a single-level, 75 V DPT research prototype, subject to the manufacturing confirmations and layout decisions below. Not an unconditional release for full-current operation or a 1200 V stack.**

The saved design passes fresh KiCad 7 DRC. The exported copper, mask, paste, outline and drill data reproduce from the current PCB. No confirmed short, unconnected pad or circuit-component connectivity mismatch was found. The main remaining concerns are the specified manufacturing process, one local power-return asymmetry, and gate-loop/measurement geometry that cannot be qualified by DRC alone.

No Q3D or other field extraction was used. All checks were read-only on the original project; exports and zone-refill experiments used temporary copies. Only this report was added to the repository.

## 1. Exact design reviewed and verification results

PCB SHA-256:

```text
f19e07fbd4a09b65fb61d93414538f3ffecec8444674118923d5babd369cd312
```

| Check | Result | Interpretation |
|---|---|---|
| Fresh DRC of saved PCB, with current project and custom rules | 0 violations, 0 unconnected pads, 0 footprint errors | Pass for the enabled checks |
| Actual PCB pads compared with a fresh schematic netlist | Circuit components match across 94 connected PCB nets | Pass after separately identifying PCB-only test pads |
| Added PCB-only test pads | 32 footprints | Not represented as schematic components; document explicitly |
| Independently exported Gerbers | All 11 copper/mask/paste/silkscreen/outline files match | Generation timestamps excluded from comparison |
| Independently exported Excellon drill | Matches | Timestamp/header date excluded |
| Fabrication ZIP versus files in `fab/gerber` | All 13 ZIP entries match byte-for-byte | ZIP contains the corresponding Gerbers, job file and drill |
| Copper-layer inspection | Top, bottom, In1 and In2 rendered and inspected | Geometric review, not an inductance/current-density calculation |
| Copper zones in saved board | 101 filled copper zones; 28 rule areas | Rule areas intentionally have no copper fill |
| Vias | 1,066 at 0.60/0.30 mm and 36 at 0.45/0.25 mm | All are through vias; no blind-via process is required for this DPT board |
| Placement output | 187 component rows; no test-pad placement rows | Bare test pads are correctly absent from placement data |

An independently refilled copy also passes DRC with matching project/custom-rule files present: **0 violations, 0 unconnected pads, 0 footprint errors**.

The schematic contains 98 nets including unconnected-pin nets. A strict component-set comparison initially differs because the PCB adds test-pad pins to existing nets. Removing only these `TP` entries from the comparison leaves no circuit connectivity differences. This does not constitute a complete schematic ERC.

## 2. Previous findings: what has been addressed

| Previous finding | Updated result |
|---|---|
| VDS connected directly through underrated U.FL | Replaced by four Wurth 66012102111404 MMCX jacks: J6, J9, J15, J18 |
| Small vias conflict with saved minimum rules | Fixed: loaded minimum via diameter 0.45 mm and drill 0.25 mm |
| No manufacturing track-width/neck-width floor | Fixed: loaded minimum track width and connection width are both 0.20 mm |
| No positive mask-web setting | Fixed: loaded solder-mask minimum width is 0.10 mm |
| Missing courtyards ignored | Severity now error; fresh DRC passes |
| AC mechanical BOM uses wrong reference | Mechanical entries now use J21, matching the PCB |
| Driver-courtyard insulation exception too broad | Narrowed to pads/tracks; vias and pours are no longer included in that exception |

The global clearance floor is now 0.20 mm. Copper-to-edge minimum is 0.30 mm. These are explicit settings, but their acceptability for the intended manufacturing process still requires fabricator agreement.

The MMCX manufacturer's datasheet specifies **170 V RMS maximum working voltage at sea level**, with a separate 500 V AC withstand test. The old 30 V U.FL objection therefore no longer applies to these VDS jacks. This does not qualify the mating cable, probe or instrument arrangement.

Source: [Wurth 66012102111404 manufacturer datasheet](https://www.we-online.com/katalog/datasheet/66012102111404.pdf).

## 3. Fabrication conditions to close before placing the order

### F1. Make the intended stack-up an explicit manufacturing requirement

The BOM header specifies 4 layers, 1.6 mm FR4, 70 um copper on all layers, 0.10 mm outer prepregs, ENIG, and filled/capped via-in-pad. However, the PCB has no explicit numerical stack-up block, and the Gerber job file does not specify copper/dielectric thicknesses or the required ENIG finish. The Gerber ZIP does not include the BOM header where these requirements are written.

**Required action:** provide a separate fabrication drawing or controlled order specification. Have the manufacturer confirm the finished copper thickness, L1-L2 and L3-L4 dielectric thicknesses, total thickness and tolerance, finish, minimum track/space, drill/annular ring, via treatment and IPC class. Do not order a default 4-layer stack-up and assume it reproduces the intended commutation-loop geometry.

This is a release-documentation condition, not evidence of a routed short. The low-inductance concept depends on the closely spaced opposing-current layers.

### F2. Confirm the combined small-via, copper-weight and via-in-pad process

The 0.45 mm diameter / 0.25 mm drill vias have a nominal radial annular ring of **0.10 mm**. The board also uses 2 oz copper and via-in-pad structures at the shunt return lands. A DRC pass only shows agreement with the project rules; it does not establish the supplier's production capability or finished-hole tolerances.

**Required action:** obtain DFM approval for this exact combination. Identify which via-in-pad holes require fill/cap and which ordinary vias require tenting. Confirm the distinction between tool diameter and finished plated-hole diameter with the supplier. The Excellon file combines PTH and NPTH with plating attributes; verify that the manufacturer's CAM process preserves those attributes, or supply separate PTH/NPTH outputs if requested.

### F3. Confirm assembly handling of the custom footprints

The EPC2361 footprint uses copper-only pads plus graphical solder-mask and paste apertures. The MMCX shield lands similarly use graphical paste apertures. This is intentional construction: absence of paste in a pad's layer list alone is not a missing-paste defect. The exported paste files contain those graphics and reproduce from the board.

**Required action:** inspect the stencil with the assembler against the current EPC2361 recommended land/stencil drawings, confirm stencil thickness and paste process, and review the custom driver, shunt and MMCX footprints. Library-footprint issue/mismatch checks remain ignored, so a clean DRC cannot independently validate these custom drawings. This review did not perform a complete dimension-by-dimension certification of every custom footprint.

Source: [EPC2361 manufacturer datasheet, land pattern and stencil drawings](https://www.epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf).

### F4. Remove assembly-document ambiguity

- The BOM groups J1 and J2 under value `DC+`, although J2 is DC−. Grouping identical MPNs is valid, but the displayed value is misleading. Split the values or explicitly list both functions.
- The grouped control-header row shows CTRL1's NTC pin assignment for both J5 and J14. Actual J14 pins 9/10 are NC. Provide individual connector pinouts in assembly/test documents.
- RS1-RS4 appear as fitted BOM/placement components and also as hand-soldered mechanical entries. Specify whether the assembler or laboratory installs them, once, using the agreed PMK procedure.
- The 32 bare test-pad footprints are correctly excluded from placement, but they are not schematic symbols. Retain the testpoint CSV in the build/test package and identify these as intentional PCB-only additions.

These items can be resolved in release documentation without necessarily changing copper.

## 4. Power-loop review without Q3D

### What looks sound

The intended fast loop is local bypass positive -> high-side FET -> SW -> low-side FET -> local source island -> UFCS shunt -> DC− return -> local bypass negative. The load-inductor lead should remain outside this local commutation loop.

- Four repeated half-bridge cells are retained, with two mirrored cells per driver.
- HS and LS device centres are 4.30 mm apart in each cell, rather than separated by a remote interconnect.
- Twenty-four top-side 1 uF bypass capacitors sit in the row at approximately y = 101.10 mm; sixteen bottom-side bypass capacitors sit around y = 101.20 mm. This gives the intended 6 top + 4 bottom bypass parts per cell.
- The 20 bulk 2220 capacitors are separate from the local edge bypassing.
- Broad power copper and stitched planes carry the commutation/load currents. The 0.30/0.40 mm individual segments seen on power net names are not, by themselves, evidence that the full phase current is routed through a single narrow track.
- Dedicated `LSRC1` to `LSRC4` islands and individual shunts remain distinct PCB nets; no direct copper short bypassing a shunt was found by the connectivity/DRC checks.
- DCP and SW via locations in the inspected local cell band mirror correctly about each driver centre.

### P1. DC− shunt-return via distribution is not fully mirrored

This is the clearest local power-layout discrepancy found in the geometric review.

Within the window `abs(x - shunt_x) < 7.1 mm`, `112 < y < 117 mm`, the DC− via counts are:

| Shunt | Centre x, mm | DC− vias in this defined window |
|---|---:|---:|
| RS1 | 113.85 | 37 |
| RS2 | 138.65 | 41 |
| RS3 | 161.35 | 37 |
| RS4 | 186.15 | 41 |

Specifically, DC− vias at **x = 131.65 mm**, y = **113.4, 114.1, 114.8, 115.5 mm** have no reflected counterparts at x = 120.85 mm about U1's centre x = 126.25 mm. The pattern repeats at **x = 179.15 mm**, with no counterparts at x = 168.35 mm about U2's centre x = 173.75 mm.

These are counts in a defined inspection window, not the total effective vias carrying each cell current. Nevertheless, they show that the shunt-return geometry is not perfectly mirrored. Equal gate-branch lengths alone therefore do not prove equal power-loop impedance.

**Suggested action before freezing copper:** inspect whether these four-via rows should be restored on the opposite side or removed symmetrically, while maintaining mask/pad clearance and sufficient current capacity. Alternatively, explicitly accept and document the asymmetry for the first instrumented prototype. Do not delete current-carrying vias merely to equalize a count. Without extraction or measurement, the inductance/current-sharing consequence cannot be quantified.

### P2. Do not reuse an older loop-inductance number as a current-layout guarantee

MMCX clearance removes power vias near the shunts, and the barrier/measurement geometry has changed relative to earlier layouts. The current broad return planes are favourable, but the effective fast return takes detours around clearance holes and keepouts.

**Suggested action:** preserve the return near each shunt and bypass transition, avoid additional cuts there, and treat old 0.5/0.65 nH figures as unverified for this exact hash. Qualify VDS overshoot and per-cell current sharing during staged DPT. This review makes no numerical loop-inductance claim.

## 5. Gate-loop review without Q3D

### What looks sound

- Separate gate branches and Kelvin-source nets are retained.
- R1-R4 and R20-R23 provide an individual 0.5 ohm branch resistor for every FET.
- Each of the eight post-resistor gate nets has **4.348 mm of explicitly drawn top-layer track**, at 0.30 mm width. This measurement excludes component interiors, pad traversal, the shared star feed, vias and sensing stubs. It is a useful geometric equality check, not a complete loop length.
- Driver-local C13-C16 and C46-C49 decoupling is on the bottom beneath the output-side region. The remote isolated-supply feed does not replace these local capacitors.
- The Kelvin nets remain separate from the high-current source copper on the PCB. Their intended connection to power source is through the device/package, rather than a deliberate long common PCB source trace.

### G1. Outgoing gate and Kelvin return are not a tightly paired route throughout

Most outgoing branches are on F.Cu. High-side Kelvin collectors are on B.Cu; low-side returns use B.Cu and an additional In1.Cu collector. The shared high-side gate feed also changes to In2.Cu. Driver output pins are around y = 117.05 mm, while gate stars are at y = 104.90 / 109.20 mm.

This retains separate Kelvin sensing but produces layer changes and stretches where the outgoing gate and return are separated laterally or through much of the 1.6 mm board thickness. The 0.10 mm outer prepreg does not automatically make these top-to-bottom gate routes a 0.10 mm loop. No numerical gate-loop inductance was calculated.

**Suggested improvement:** where practical, route each gate with its Kelvin return as a close pair on the same or adjacent layer, align the via transitions and minimize the shared driver/star loop. Preserve the power-return plane and insulation keepouts while doing so. Do not move Kelvin tracks into a critical power return merely to shorten a gate trace. For this prototype, this is a switching-performance concern requiring validation, not a demonstrated fabrication failure.

### G2. Individual gate resistors are several millimetres from the gate pads

For example, R1 is centred at (123.25, 104.90) mm and Q1's gate pad at (119.102, 106.13) mm: approximately **4.33 mm centre-to-centre**. The other branches follow the mirrored arrangement. The resistor is present in every branch, but it is not immediately at the device pad.

**Suggested improvement:** consider moving each individual resistor towards its FET gate, maintaining mirrored geometry, a clean Kelvin pickup and the power-cell clearances. This can isolate more of the shared routing from the sensitive gate, but its benefit must be weighed against the resulting route/power-plane disruption. Do not call the present placement a confirmed failure solely from its distance.

### G3. Gate-measurement branches add nontrivial stubs

Each gate has a through-via and approximately **2.975 mm** of bottom-side track to its 0 ohm sense resistor before the remaining connection to U.FL. The corresponding Kelvin shield pickup is longer: approximately **7.377 mm** of horizontal track for the HS U.FL returns and **10.577 mm** for the LS returns in block 1, plus the shield-pad link. The second block repeats the concept. Some new spring-tip pads add further branches.

Consequently, the U.FL measurement does not use a perfectly colocated gate/Kelvin pickup. Probe capacitance and the remote sense-return geometry can introduce apparent ringing or load the real gate.

**Suggested action:** prefer the new local paired spring-tip pads when compatible with the actual probe. Compare their gate waveforms with the U.FL measurements. If U.FL ports are retained, keep signal and Kelvin pickup together, shorten them where practical, and consider depopulating the dedicated 0 ohm sense jumpers for unused ports to disconnect the remote connector section. The short gate-side via/stub remains even with that jumper removed. Do not change the main gate resistor as a substitute for validating probe loading.

The low gate-to-source voltage means the old VDS connector-rating objection does not automatically apply to gate U.FL ports. High-side measurement still requires appropriate common-mode rejection/isolation, and low-side Kelvin grounding must not create a shunt-bypass path through instruments.

## 6. Measurement interface and access

The updated VDS connections are:

| Port | Centre | Shield |
|---|---|---|
| J6 | SW | LSRC1 |
| J9 | SW | LSRC2 |
| J15 | SW | LSRC3 |
| J18 | SW | LSRC4 |

The board label now calls for a rated probe. Keep these shields isolated from one another where their source nodes differ; an ordinary set of grounded scope inputs is not equivalent to isolated probes. A bare MMCX cable is not an attenuating probe.

**Before assembly release:** confirm that the selected probe-tip cable physically mates with the Wurth jack, its voltage/frequency rating covers VDS and overshoot, and the bottom-side cable/probe body clears the board supports. Manufacturer connector working-voltage approval does not itself establish waveform fidelity. The remote VDS return path also includes a source-side via/track; local spring contacts can provide a useful comparison.

## 7. Operating scope and insulation

The 2EDF7275K drivers have functional isolation, not a complete 1200 V reinforced barrier. The wider PCB rules and narrowed package exception do not upgrade the component rating. Restrict this disposition to a defined single-level bench DPT setup with agreed controller, supply and instrument references.

A full stack requires its own insulation architecture, dielectric/creepage assessment, supply and control isolation, hardware spacing and measurement provisions. This report does not authorize 1200 V common-mode operation, continuous full-current testing or operation without an appropriate pulse/fault-limiting test arrangement.

## 8. Recommended release checklist

- [ ] Fabricator accepts the explicit stack-up, 2 oz copper, 0.20 mm track/connection floor, 0.25 mm drill, 0.10 mm annular ring and mask-web requirements.
- [ ] Via-in-pad fill/cap and ordinary-via tenting are unambiguous in the order, not only in a BOM outside the Gerber ZIP.
- [ ] Assembler confirms EPC2361 stencil/mask geometry and assembly process, plus driver, shunt and MMCX custom footprints.
- [ ] Decide whether to correct or explicitly accept the four-via shunt-return asymmetry.
- [ ] Decide whether to shorten/pair gate sensing and gate-return paths before spending on this prototype; otherwise include them in the first DPT validation plan.
- [ ] Correct misleading grouped connector values and specify who installs the UFCS shunts.
- [ ] Confirm probe model, mating interface and bottom-side mechanical access.
- [ ] Freeze the approved revision and retain DRC, testpoint list, assembly drawings and order specification together.
- [ ] After any copper/rule change, refill, rerun DRC and regenerate the complete fabrication package.

**Release recommendation:** if these manufacturing requirements are accepted and the remaining loop/measurement concerns are explicitly accepted as prototype validation items, the current design is a reasonable candidate for a small 75 V DPT prototype order. I would not describe the gate/power loops as performance-qualified, or the board as ready for unrestricted system operation, from a geometric review alone.

## 9. Evidence and limitations

Reviewed: current PCB, project and custom rules; independently exported schematic netlist; fabrication BOM/placement/Gerbers/drill/ZIP; custom footprint construction; routing-generation rationale; and rendered current copper layers. Generation scripts were read for intent and were not run to alter the design.

Fresh reports and renders were created under the temporary folder `C:/Users/enesa/AppData/Local/Temp/spb-fabrication-review-20261019`. They are intermediate evidence and can be removed by the operating system.

Independent refill/custom-rule DRC: **PASS, 0 violations, 0 unconnected pads, 0 footprint errors**. Original-file integrity: all **69** files hashed in the target PCB folder remain unchanged at the end of this review.

Limits: no Q3D; no computed gate/power inductance or current-density/thermal result; no complete ERC, complete connector-mating mechanical study, full custom-footprint dimensional certification, dielectric qualification or EMC test. DRC's footprint/library mismatch checks remain ignored. The complete input-to-output insulation and the effects of device-internal Kelvin/source connections are not proven by PCB netlist matching.

## 10. Disposition of the findings (2026-10-22)

All findings were accepted and handled in the generators (`scripts/make_kicad_bb_revb.py`, `scripts/make_fab_outputs_revb.py`, `scripts/test_points.py`); the DPT board and its package were regenerated.

| Item | Action | Result |
|---|---|---|
| F1 | Fab notes inside the Gerber ZIP (`gerber/spb-bb-revb-dpt-fab-notes.txt`): stack-up table (L1/L2 and L3/L4 0.10 mm prepreg, 70 um all layers, 1.60 mm total, ENIG), IPC-6012 class 2, rules, barrier keep-out | in the ZIP the fab house receives |
| F2 | Via treatment stated: all vias tented except an explicit via-in-pad list (IPC-4761 type VII, generated from the board: 186 vias in 34 pads, shunt SHLD and bypass-capacitor pads); separate PTH / NPTH Excellon files | DFM confirmation by the fab house still to obtain at ordering |
| F3 | No copper change; stencil / custom-footprint confirmation stays an assembler action at ordering | open (ordering) |
| F4 | BOM grouped by value too (J1 DC+ / J2 DC- and J5 / J14 with their own pinouts on separate lines); RS1-RS4 stated once ("not by the assembler: hand-soldered in the lab") and removed from the pick-and-place file; test-point list `fab/testpoints.csv` kept in the package | done |
| P1 | Cause: the shunt-return via rows were counted from the left edge with a floating-point end test, so the left cell lost its via at x = -5.4 and kept one at -19.4 that the right cell lacked. Rows are now counted from the inner edge in both cells: every DC- via in the cell area has its mirror image (checked on the board) | done; power vias 1020 after pruning |
| G1 / G2 | Gate re-layout, all eight FETs: R_G (R1, R2, R4, R5) right at the gate pad (~1.5 mm of trace instead of ~6 mm); per branch the Kelvin return runs on L1 beside the gate / star trace (1.3 mm) to the corridor, the two Kelvin rows of a pair join under the star (HS on L4, LS on L2 inside the corridor cut-out), star -> driver as stacked pairs (HS: L1 stub + L3 over L4, LS: L1 over L2). The two cells of a row are rotated by 180 deg, so the routing is point-symmetric about each star and both branches are identical. Pull-downs now 10 k 0402 (R3, R6) between the Kelvin and star rows | done; plot: `figures/dpt_gate_layout_block1.png`; Q3D of gate loop and gate-power coupling pending |
| G3 | 0 R U.FL gate-sense links (R16-R19, R35-R38) DNP by default; the spring pads are the primary V_GS points | done |

Verification of the regenerated board: DRC 0 violations / 0 unconnected / 0 footprint errors, also after a fresh load of the saved project (rules: via 0.45 / drill 0.25 / track and clearance 0.20); schematic = PCB (94 nets, 187 parts, 0 problems); no 3D collisions (187 bodies); 36 labelled test points (all eight V_GS spring pads, V_DS spring pads on Q1-Q3 and Q5-Q7; Q4 / Q8 V_DS via the MMCX jacks), fallbacks listed in `fab/testpoints.csv`.

Still open before ordering: F2 / F3 supplier confirmations, and the Q3D re-extraction of the power loop, the cell-to-cell loop coupling, the gate loops and the gate-power coupling on this geometry (P2: no earlier loop value is quoted for this layout).

### 10.1 Gate loop after Q3D (2026-10-22 / 23)

The first complete gate extraction (`simulation/bb_q3d/gate_post.py`, AC 100 MHz, copper only) showed that the shared star -> driver part, not the per-FET branch, dominated. Two further layout rounds paired every gate path with its Kelvin return on the adjacent layer (L1/L2 at 0.1 mm, L3/L4 at 0.1 mm) all the way to the 1 uF output-side capacitors, and took the island supply vias out of the gate-current path.

| Gate loop (nH) | G1/G2 round 1 | round 2 | round 3 (released) |
|---|---|---|---|
| HS single FET on / pair-driven | 15.4 / 25.4 | 13.7 / 22.8 | 12.5 / 20.6 |
| LS single FET on / pair-driven | 9.7 / 16.6 | 9.0 / 15.0 | 7.6 / 12.3 |
| Gate-power coupling, both cells switching (pH) | 11 - 22 | 1.8 - 14 | 1.2 - 8.5 |
| v_GK at 30 A/ns (V) | 0.32 - 0.65 | 0.02 - 0.43 | 0.04 - 0.26 |

Double-pulse SPICE with the extracted copper (75 V, 322 A, `revb_q3d_spice.py`): HS V_DS peak at the LS turn-on 100.3 V at R_G,on = 2 Ohm, 94.0 V at 2.5 Ohm (E_on 105 uJ, equal to the design-flow value with the lumped 1.7 nH gate), 89.8 V at 3 Ohm. Recommendation: R_ON 1.0 Ohm (R_G,on 2.5 Ohm) for the first DPT, or keep the 75 V DPT peak below the rating by limiting the bus voltage.

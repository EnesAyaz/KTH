# P3 — left-side DC input and gate driver

This revision supersedes P2 for placement review. It is not released for manufacturing.

## Implemented arrangement

85 × 55 mm, four layers. DC+ and DC− M4 terminals are on the upper left, with auxiliary power and HI/LI inputs on the left edge. AC is on the right. LMG1210 is immediately left of the switch group. Both switch pairs face left toward the driver. There are two EPC2361s per switch, four total.

Twenty-four TDK C2012X7S2A105K125AB bus capacitors are fitted: six above and six below each local half bridge. All are on the top face. Upper banks C1–C6 and C19–C24 directly serve the short local commutation paths; lower banks C7–C12 and C25–C30 supplement DC-link decoupling through the collectors. The count was increased so the lower row does not require a long top-layer positive feeder to the high-side devices. Nominal total is 24 µF; effective capacitance at 75 V and permissible RMS ripple have not been established.

Every component has a silkscreen reference. Gate/source headers are marked G and S; the control header has individual 12V/GND/HI/GND/LI/GND labels. DC and AC terminals and all five test points are identified. The BOM contains all 51 purchased components; five additional footprints are copper test points.

## Four-layer allocation

| Layer | Actual baseline P3 use |
|---|---|
| L1 / F.Cu | Components, local DC+/AC/DC− power islands, local gate escapes and decoupling |
| L2 / In1.Cu | Continuous DC− plane underneath the power cells; no routed signals |
| L3 / In2.Cu | DC+ collector, with auxiliary/control and source-return routes |
| L4 / B.Cu | AC collector and gate-drive routes |

L1 is not a whole-board DC+ plane. The commutation current passes through separate positive, switch-node and negative regions. L2 provides a nearby opposing current path. L3/L4 are already used for power distribution as well as driver connections; they are not two unused signal layers.

The gate-routing candidate adds explicit star branches and source-return corridors on the lower layers. Consult its separate report for its actual result before adopting it. A gate route over an unrelated DC+ plane is not automatically a properly referenced gate loop.

## Proposed stackup for fabricator review

F.Cu 0.070 mm / dielectric 0.100 mm / In1.Cu 0.035 mm / core 1.190 mm / In2.Cu 0.035 mm / dielectric 0.100 mm / B.Cu 0.070 mm. Copper plus dielectric totals 1.600 mm, excluding masks. The 0.100 mm outer dielectric spacing is a requested finished value, not a confirmed catalogue stackup. Manufacturer tolerances and 0.15 mm routing at the chosen finished copper weight must be accepted before ordering. Finish and assembly stencil remain unspecified.

## Inductance interpretation

Both primary upper-bank local geometries now share the same 6 mm device spacing and 0.100 mm top-to-return dielectric. The P2 selected external finger estimate (~0.385 nH) and six-capacitor ideal component ESL (~0.080 nH) apply only to those selected local contributions. Their ~0.47 nH subtotal is not the complete loop or a measured value. Lower-bank vias, shared collectors, package contributions and coupling require extraction; do not divide component ESL by all 24 capacitors and call that the switching-loop ESL.

## Electrical and mechanical release items

Design targets remain 75 V maximum, 36.7 A RMS / 51.9 A peak total output, 50 kHz nominal and 100 kHz maximum. Current capability and thermal rise have not been validated. The gate-routing report must demonstrate acceptable branch symmetry and source-return topology; DRC alone cannot do this. Current distribution through collectors and vias, MLCC bias/ripple, bootstrap operating range and actual gate overshoot also remain engineering checks.

The controller supplies nonoverlapping HI/LI in independent-input mode; bootstrap startup/refresh is required. JCTRL1 is not isolated. Gate headers must not be driven by a second active driver while onboard outputs are connected. Individual 0 Ω gate-resistor footprints remain for tuning and isolation.

Cold plate, insulating TIM, clamping force, mechanical mounting and cable-lug support are not designed. Tall headers and capacitors constrain the plate underside. No fabrication-ready claim is made while these remain open. Exact EPC2361 and LMG1210 manufacturer models are still unavailable: their local 3D models are explicitly approximate envelopes. Generic header and capacitor models require manufacturer-dimension comparison.

## Project files

Open epc2361-prototype-p3.kicad_pro; open its PCB and press Alt+3 for 3D. BOM.md / BOM.json are the revised component lists. The schematic and PCB use local footprints and local visualization models. connectivity-check.txt checks exported net assignments and model presence; drc.rpt records baseline geometric checks. A separate gate candidate is not the baseline released design. P2 files copied into this folder during preparation are historical; use only the P3-named project for this revision.

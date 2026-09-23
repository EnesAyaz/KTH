# Four-EPC2361 prototype — revision P2

Engineering layout for review, not a fabrication or current-rating release.

## Implemented design

- Half bridge with two EPC2361 in parallel per switch, four total.
- 75 V maximum bus; target 36.7 A RMS / 51.9 A peak total output, 50 kHz nominal and 100 kHz maximum. These are design targets, not validated ratings.
- 76 × 53 mm, four-layer PCB. Proposed 0.100 mm F.Cu-to-In1.Cu dielectric for close power-loop return coupling. Stackup must be agreed with the fabricator.
- Two mirrored local half bridges with gates facing a central LMG1210. The left capacitor row is below its MOSFET pair in top view; the right row is above its pair. All twelve bus capacitors are on F.Cu; none are underneath the PCB.
- C1–C12: TDK C2012X7S2A105K125AB, 1 µF / 100 V / X7S / 0805. Twelve µF is nominal; effective capacitance at 75 V, ripple heating and resonances remain to be qualified. External bulk bus capacitance is not included.
- Three Würth 74650094 M4 terminals for DC+, DC− and AC; four fitted 1.27 mm gate/local-source headers; five copper test pads.
- One LMG1210RVRR drives both high-side gates and both low-side gates. Each FET retains an individual 0 Ω series tuning footprint. They provide branch damping adjustment and isolation for external-drive tests. Removing them without a replacement connection disconnects the gates.

## Control and first-power conditions

JCTRL1 pins: 1 = 12 V auxiliary input, 2 = DC−, 3 = HI, 4 = DC−, 5 = LI, 6 = DC−. This control interface is not galvanically isolated.

LMG1210 uses independent-input mode: the controller must supply nonoverlapping HI/LI signals. There is no internal shoot-through interlock in this mode. Bootstrap charging requires a startup sequence and periodic low-side intervals; sustained 100% high-side duty is unsupported. Check the TI datasheet and `docs/onboard-driver-review.md` for bias, bootstrap and gate-charge calculations.

Gate/source header pin 1 is gate after its resistor; pin 2 is the associated local source. Do not connect another active driver while the onboard output remains connected. Use short, suitable differential probing for switching measurements.

## Inductance calculation

See `../../docs/inductance-prototype-p2.md` for actual dimensions, formula and exclusions. The selected external copper fingers contribute approximately 0.385 nH per local branch under a parallel-strip approximation. Six ideal parallel capacitors contribute approximately 0.080 nH using 0.480 nH typical individual component ESL. Their selected-contribution subtotal is about 0.47 nH per branch.

**0.47 nH is not the full loop inductance or a rigorous lower bound.** Other copper regions, vias, packages, shared collectors and mutual coupling are excluded. The two parallel branches do not justify simply halving this subtotal. A full extraction and double-pulse measurement are still required.

## Files and viewing

Open `epc2361-prototype.kicad_pro`, then the PCB. In PCB Editor choose View → 3D Viewer or press Alt+3. `preview/top.png` shows the top layout; `preview/epc2361-prototype.svg` is the zoomable schematic. `BOM.md` is the grouped PCB component BOM; `BOM.json` contains individual placement data.

All purchased-component placements have local visualization models after the model audit passes. Standard passives and headers use generic KiCad package models. Four EPC2361s and the LMG1210 use explicitly approximate envelopes, not exact manufacturer CAD. An official terminal STEP is also saved in `models`. Exact EPC2361 and LMG1210 manufacturer models remain outstanding; generic models do not establish mechanical fit or capacitor height.

## Verification and remaining engineering

`drc.rpt` records the actual KiCad DRC result. `connectivity-check.txt` checks exported schematic net assignments against the PCB and checks local model files. Native schematic ERC has not been run; custom symbols use passive pins, so these checks are not a substitute for circuit review.

Before fabrication: qualify dynamic gate-current sharing and branch parasitics; review the control routes through the DC+ collector; verify copper/via current density and thermal rise; establish effective MLCC capacitance and RMS ripple; verify all manufacturer land patterns and connector drill dimensions; and reconcile EPC, TI and terminal stencil/reflow requirements. Grid-routed control connections establish connectivity, not matched gate-loop inductance or optimized switching behavior.

Cold-plate contact regions are indicated in the drawing layer. The cold plate, electrical insulation/TIM, contact pressure, mounting and fasteners remain unselected. Gate headers and nearby capacitors constrain the plate geometry. No thermal/current validation or cold-plate assembly design is claimed. The BOM covers PCB components; add the custom PCB, cable lugs/bolts and cooling assembly after those are specified.

Sources and reviews: `../../docs/literature-review.md`, `../../docs/onboard-driver-review.md`, `../../docs/prototype-connectors-models.md`.

Final automated check, 2026-09-21: zero DRC violations, zero unconnected pads, zero footprint errors; 44 components and 120 connected pin assignments verified. All 39 purchased-component placements reference existing local 3D files.

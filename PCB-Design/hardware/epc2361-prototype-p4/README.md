# P4 compact pin-array half bridge

2026-09-22. Engineering prototype for review; not a manufacturing release.

Open `epc2361-prototype-p4.kicad_pro`, then the PCB. In PCB Editor, Alt+3 opens the 3D Viewer. P2 and P3 remain in their original directories.

## Implemented layout

- Four EPC2361s: two high-side and two low-side devices; targets are 75 V maximum bus, 36.7 A RMS / 51.9 A peak total output, 50 kHz nominal and 100 kHz maximum.
- Driver left of both switch pairs; both pairs face the driver. The board outline is 78.5 × 51 mm.
- Twenty-four 1 µF / 100 V TDK C2012X7S2A105K125AB capacitors. Each local half bridge has six above and six below, all on the top face. The upper bank is the closest fast-decoupling bank; lower capacitors provide supplementary bus decoupling through collectors. Actual capacitance at 75 V and ripple limits remain unqualified.
- JDC1: all 24 pins DC+; JDC2: all 24 pins DC−. Both arrays are on the upper left. JAC1: all 24 pins AC, on the right.
- Each power header is a Samtec TSW-112-07-G-D candidate, 2 × 12 contacts at 2.54 mm pitch. It uses a local copy of the generic KiCad footprint and package model; verify the manufacturer's hole and body drawing before release.
- JGH1/JGH2/JGL1/JGL2 retain gate/local-source access. Individual 0 Ω gate-resistor footprints remain for damping adjustment and isolating the onboard output during external-drive tests.
- All component references, power arrays, control pins and test points have silkscreen labels. Capacitor references are vertically aligned to improve legibility.

## Power-header interpretation

The photograph was used as a packaging reference, not as evidence that an ordinary pin header is rated for this prototype current. At perfectly equal sharing, 36.7 A RMS / 24 = 1.529 A RMS per AC contact; 51.9 A peak / 24 = 2.163 A peak. Actual DC-pin RMS depends on modulation, load and bus-capacitor current. Do not apply this board to the earlier 220 A full-system target.

Use all contacts through a suitably designed mating board/socket and broad copper distribution. Single flying leads or a ribbon cable do not implement the intended connection. The mating assembly is outside this PCB BOM and must be selected and thermally qualified. Adjacent DC arrays also require correct insulation and mechanical retention.

The manufacturer describes the selected 24-pin geometry on its [product page](https://www.samtec.com/products/tsw-112-07-g-d). The [series specification](https://suddendocs.samtec.com/productspecs/tsw-sxx.pdf) gives current under limited-contact loading. A [related SSW/TSW power test](https://suddendocs.samtec.com/testreports/tc0838-1970_reportrev2_pwr.pdf) reports 2.1 A/contact with 100 contacts powered at 30 °C rise after derating. This is useful family-level evidence, not certification of this 24-contact assembly, plating configuration or ambient temperature.

## Actual four-layer allocation

| Layer | Use |
|---|---|
| L1 / F.Cu | Components, local DC+/AC/DC− power islands and short pin escapes |
| L2 / In1.Cu | Continuous DC− return under the switching cells; no signal routing |
| L3 / In2.Cu | DC+ collector, control/supply traces and source-return corridors |
| L4 / B.Cu | AC collector and explicit star gate routing |

L1 is not a whole-board DC+ plane. Local forward and return current geometry matters more than assigning a global net to a layer. L3 source corridors use local copper-pour exclusions while L2 remains intact. Source tracks retain their existing AC/DC− net names and power connections; they are not electrically isolated Kelvin nets. The source routing is bounded near the gates, but not a field-solved controlled-impedance pair.

Proposed stackup: 70 µm outer copper / 0.100 mm dielectric / 35 µm inner copper / 1.190 mm core / 35 µm inner copper / 0.100 mm dielectric / 70 µm outer copper. Total copper plus dielectric is 1.600 mm, excluding masks. PCBWay or the chosen European fabricator must confirm this stackup and copper-weight-specific trace limits. Present minimum route width is 0.15 mm and general clearance is 0.20 mm; generic capability tables are not order acceptance.

## Verification

The adopted gate routing and silkscreen pass KiCad DRC with zero violations, zero unconnected pads and zero footprint errors. All 56 components and 213 connected pin assignments agree between the exported schematic and PCB. All 51 purchased-component placements have existing local visualization models; four FET models and the driver model are approximate envelopes. Exact manufacturer CAD remains outstanding.

The graph audit splits track intersections to catch shortcuts. Actual B.Cu centreline paths from output via to gate-resistor input via are HO: 33.96 / 33.94 mm; LO: 33.76 / 33.74 mm. Each pair differs by 0.02 mm. This excludes F.Cu escapes, pad spreading and vias; equal geometric length does not establish equal impedance or switching delay. See `gate-path-audit.json`, `gate-candidate-review.json`, `connectivity-check.txt` and `drc.rpt`.

The source candidate filename remains as a review artifact; its checked electrical geometry was adopted into the main P4 board. `review-history/p4-before-star-routing.kicad_pcb` preserves the earlier routing. The main P4 board includes the final silkscreen.

## Before manufacturing

The remaining release items are current distribution and thermal rise of copper/vias/connectors, effective MLCC capacitance and RMS ripple, gate-loop impedance and switching behavior, cold-plate/TIM/clamping and supports, and fabricator/assembler acceptance of land patterns, stackup, finish and stencil. No cold plate or fixture has been dimensioned. Tall headers constrain heatsink clearance. No fabrication Gerbers have been released.

The LMG1210 operates in independent-input mode: external HI/LI must be nonoverlapping, and bootstrap startup/refresh is required. JCTRL1 is 12V, DC−, HI, DC−, LI, DC−; it is not galvanically isolated. Do not attach another active gate driver while onboard outputs are connected. The current targets have not been proven by thermal or switching tests.

`BOM.md` and `BOM.json` list PCB components. `preview/top.svg`, `preview/bottom.svg` and the schematic SVG are zoomable. Rebuild the baseline using `build_p4_schematic.py`, `build_p4_board.py`, `route_p4.py`; then run `route_p4_gates.py`, the graph audit and `label_p4.py`, and adopt only a candidate that passes the checks. Rebuilding the baseline alone does not include the final gate-routing pass.

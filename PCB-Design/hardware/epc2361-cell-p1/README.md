# P1: EPC-style one-pair power-loop layout

This is the revised native KiCad 7 project requested from EPC's optimal-loop illustration. The original P0 project is preserved in the sibling directory. Open `epc2361-cell.kicad_pro` here.

## What changed

- 27 x 30 mm study outline. One high-side EPC2361 at (15,16) mm and one low-side at (15,22) mm; 6 mm pitch.
- Six 0805 capacitors across the top above the high-side device, with positive terminals facing the devices. Broad top DC+ copper replaces the long side rail.
- Capacitor negative terminals connect through paired vias to the first inner DC- layer. Low-side source vias complete the return directly beneath the top power path.
- Six optional/DNP bottom capacitors sit underneath the top bank. Their rail transitions are outside the device lands. The DC+ via antipads perforate L2 locally but leave a continuous return; their effect needs extraction. Bottom parts are not assumed equally effective at high frequencies.
- No driver IC. Individual top G/Kelvin-source contact pairs, series gate-resistor sites and optional local gate-source resistors remain.
- All power ports and seven probe pads are routed. Pads are interface placeholders, not selected or rated power sockets. Probe mapping: TP1 GH, TP2 high-side source/AC, TP3 GL, TP4 low-side source/DC-, TP5 DC+, TP6 DC-, TP7 AC.
- Insulated top cold-plate contact corridor reserved over the FET pair. Full plate, TIM, mounting and clamping remain mechanical design work.

## Capacitors

C1-C6: TDK C2012X7S2A105K125AB, 1 uF / 100 V / X7S / 0805, six populated provisionally. C7-C12 use the same part but are DNP until impedance and heating justify population. Nominal capacitance is 6 uF top-only or 12 uF with both banks; neither number is the retained capacitance at 75 V.

TDK's simple equivalent-circuit model gives 0.480 nH for this component. The six-capacitor ideal uncoupled component-only result is 0.080 nH. This excludes mounting, shared copper, vias, FET interconnections and coupling, and is not the complete loop inductance. The 1210 alternative has 0.600 nH model inductance and more nominal capacitance. These are conventional MLCCs selected for a low-inductance assembled bank; no suitable 100 V reverse-geometry part was verified.

See `../../docs/capacitor-selection-p1.md` for manufacturer links, alternatives and qualification limits. C at 75 V and capacitor RMS heating remain unqualified. External bulk capacitance is still required.

## Proposed stackup

The board file records a provisional four-layer stack: 70 um top copper, 100 um prepreg to the 35 um L2 return, 1.19 mm core, 35 um L3, 100 um prepreg, and 70 um bottom copper. Copper plus dielectric totals 1.60 mm before solder mask. FR4 electrical properties are placeholders, not a selected laminate. Fabricator confirmation is required. L3 currently has no functional plane; layer count alone does not reduce the loop.

The key optimization parameter is the 0.10 mm top-to-L2 separation. A parallel-plate estimate must use the actual overlapping current corridor and include transitions separately. No extracted or measured inductance is claimed.

## Checks and release status

30 components and 60 pin assignments match the KiCad-exported schematic netlist and PCB. Native PCB DRC: zero violations, zero unconnected pads, zero footprint errors. Native schematic ERC has not been run. Views: `top.svg`, `return.svg`, `bottom.svg`; PNG previews alongside them. Bottom export is viewed through the board from above unless mirrored in KiCad.

This is a routed engineering study, not a manufacturing release or a demonstrated 36.7 A RMS cell rating. Wide power distribution, terminal ratings, assembly footprint sign-off, capacitor derating, coupled parasitic extraction, switching tests and electrothermal validation are outstanding. The six-parallel module and gate-driver PCB are deferred.

## Rebuild

Run `scripts/build_cell_p1.py` with KiCad Python. Set `CELL_REVISION=epc2361-cell-p1`, run `scripts/build_cell_schematic.py`, export the XML netlist to this folder, then run `scripts/check_cell.py` with the same environment variable. The audit fills zones and writes the DRC report. Preserve manual edits before regenerating.

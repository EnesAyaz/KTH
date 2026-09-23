# EPC2361 one-pair placement prototype

Open `epc2361-cell.kicad_pro` in KiCad 7. This is a native schematic and partially routed PCB placement study, not a fabrication release.

## Design basis

- One EPC2361 high-side device and one low-side device; eventual module has six of each.
- Bus: 75 V nominal and maximum. Switching: 50 kHz nominal, 100 kHz maximum.
- Eventual module: 220 A RMS AC. Ideal equal sharing gives 36.7 A RMS per cell and 51.9 A peak for a sinusoid. These are design targets, not demonstrated ratings.
- Study outline: 30 x 40 mm, four copper layers. Fabricator stackup and dielectric spacing are not selected.
- Four 1210 local ceramic sites. Candidate: TDK C3225X7R2A225K230AB, 2.2 uF / 100 V X7R each, 8.8 uF nominal total. Capacitance retained at 75 V, ripple heating and required count remain unqualified. External bulk DC link is needed.

## Placement and interfaces

QH1 and QL1 form a vertical pair, with local capacitors on the right and gate/source contacts on the left. Top copper combs connect the interleaved device pads; the filled first-inner DC-minus plane provides the proposed return path. Loop inductance has not been extracted or measured. The present narrow power traces illustrate topology and are not rated for the target current.

JGH1/JGL1: pin 1 gate input through RG1/RG2; pin 2 local source return. The source trace takes off at the source land nearest the gate. These are exposed contact pads, not a selected connector. The future driver board must preserve short gate/source paths. RG values are provisional; optional RGS1/RGS2 are DNP.

JDC1 = DC+, JDC2 = DC-, JAC1 = AC. Their 3 mm pads reserve interface positions; they are not rated sockets or final high-current terminals.

TP1 = high-side gate; TP2 = high-side source/AC; TP3 = low-side gate; TP4 = low-side source/DC-; TP5 = DC+; TP6 = DC-; TP7 = AC. Probe connections are still unrouted.

The drawing-layer rectangle reserves the MOSFET-top cold-plate contact corridor. An electrically insulating thermal interface is necessary between a common plate and the different source potentials. Cold plate, TIM, compression, mounting holes and thermal performance remain to be designed. Tall capacitors are outside the contact corridor, but the full cold-plate assembly has not been clearance checked.

## Verification and remaining work

KiCad successfully exported the schematic and both previews. The automated audit passes all 22 components and 44 pin-to-net assignments against the schematic manifest and PCB; footprint paths are linked to schematic UUIDs. Netlist labels carry KiCad's root-sheet slash prefix, normalized by the audit.

The latest native KiCad PCB DRC reports **0 geometric DRC violations, 13 unconnected items, and 0 footprint errors**. This is not a clean finished-board DRC: power ports, probes and optional gate resistors still need routing. Native schematic ERC has not been run. See `cell-drc.rpt` and `connectivity-check.txt`.

The project-local EPC2361 footprint transcribes the manufacturer's separate copper, mask and stencil geometries from datasheet revision 2.4, pages 11-12. Independent footprint/assembly sign-off is still required before fabrication; DRC does not validate the transcription against the datasheet.

Next engineering steps are footprint sign-off, selecting the stackup and real terminals, completing wide power distribution and probe routing, checking capacitance under bias, and electrothermal/commutation validation. Do not scale this cell by simply copying long shared gate traces. The six-cell board and gate-driver PCB are deferred.

## Reproducing the study

Run `scripts/build_cell_schematic.py`, then `scripts/build_cell_layout.py` with KiCad's bundled Python. Export a KiCad XML netlist to `cell-netlist.xml`, then run `scripts/check_cell.py` with KiCad Python. The latter fills zones, verifies connectivity and writes the DRC report. Generators overwrite their generated files; preserve manual edits first.

Reference review and system-level plan are in `../../docs/literature-review.md` and `../../docs/power-stage-plan.md`.

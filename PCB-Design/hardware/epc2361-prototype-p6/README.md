# EPC2361 P6 - instrumented half-bridge

Four EPC2361s, two per switch, with LMG1210. Design targets are 75 V maximum bus, 36.7 A RMS / 51.9 A peak prototype current and 50-100 kHz switching. These are not validated board ratings.

Open epc2361-prototype-p6.kicad_pcb in KiCad. Alt+3 opens the 3D viewer. Dwgs.User and Cmts.User show the mechanical envelope, contact bosses and access windows. The main board includes four mounting holes, the raised LK1 current link, and the split-spreader model.

LK1 is the sole intended connection between AC and QL1 drain net D_QL1. Place the PEM CWT Ultra Mini around the link, with winding plane perpendicular to its horizontal current direction. TP8/TP9 sense QL1 drain/source locally. H1/H2 retain provisional output-current access and are not individual-device sensing holes. No physical sensor fit or switching test has been performed.

Validation: 72 PCB footprints including five mechanical-only features; 223 connected schematic pin assignments agree; zero final DRC violations and unconnected pads. Each pair of gate centreline routes differs by 0.02 mm. The device-current audit lists the complete D_QL1 pad set. Equal gate length does not establish matched impedance.

Fabrication release is on hold. Gerbers and drill files are in fabrication-review and must not be ordered yet. Remaining items include supplier stackup/process approval, formed-link/coil closure fit, mounting and TIM tolerances, cooling design and connector mating qualification. The LaTeX report and detailed review documents explain the limits.

Rebuild sequence: prepare_p6.py, build_p6_schematic.py, build_p6_board.py, route_p6.py, route_p6_gates.py; after inspecting the candidate DRC, adopt the candidate, run label_p6.py, then finalize_p6.py once. Export the XML netlist, run verify_p6.py and audit_p6_gate_paths.py on the final board. Rebuilding intentionally replaces generated P6 files; preserve manual edits first. P5 is unchanged.

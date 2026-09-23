# Double-pulse measurement provisions

Reviewed 2026-09-22 for the P4-derived four-EPC2361 half bridge: two parallel devices per switch, 75 V maximum bus, 51.9 A peak total test-current target. This is a topology review, not evidence that a probe fixture or final PCB has been qualified.

## Implement now

Add a small paired drain/source probe landing at each FET. Low-side VDS is AC minus its local source/DC−; high-side VDS is DC+ minus its local source/AC. Label polarity and device reference, for example `QL1 VDS D+ S−`. Pick up source at the device pad region, before high-current spreading. Keep both tap branches short, adjacent where possible, and outside the main current path. A compact exposed two-pad landing is a probe-neutral starting point; a populated pin/socket footprint must match the selected probe accessory. Do not call an arbitrary two-pin header a controlled-bandwidth probe interface.

Retain existing gate/source access and use short spring or solder-in connections for switching waveforms. Keep probe metal and approach clearance away from the gate pad and cold-plate hardware. Do not route a long VDS test trace to the board edge simply to make it accessible. High-side source is the switching node, not measurement ground.

Separate the left driver region geometrically from DC input collectors. A local 12 V copper island and its quiet return are appropriate; LMG1210 also needs its local 5 V VDD bypass and floating HB/HS bootstrap loop. Splitting copper does not create galvanic isolation: the present input return and driver VSS remain referenced to DC−. True galvanic isolation requires an isolator and isolated supply design. Preserve L2 DC− directly under the fast commutation cells.

## What a current aperture measures

| Enclosed conductor | Observable | Limitation |
|---|---|---|
| AC conductor going to external load inductor | Inductor/output current | Does not resolve individual FET current during commutation |
| DC input conductor before local ceramics | Supply replenishment current | Local capacitors bypass fast switching current |
| Sole source connection from both low-side FETs to DC− | Total low-side-bank source current | Requires removal of all parallel source-return paths; adds common-source impedance |
| Sole source connection of one FET | That device's source terminal current | Breaks symmetry and can change the sharing being measured |

A coil must encircle the intended current once, with no opposite return inside its aperture and no unmeasured copper/via bypass. Two holes in a broad multilayer plane do not establish this condition. For a low-side-bank sensor, every source-connected layer must converge through the sensed bridge before meeting capacitor negative. Driver VSS/source pickup must be taken on the device side so the sensing bridge is outside the gate-return path. Even then, the bridge is inside the power commutation loop and its inductance must be included. Source current also differs from drain current by gate-terminal current during transitions.

For the first compact switching PCB, keep its uninterrupted low-inductance power return. Add AC-side access only if clearly identified as `I_OUT / I_L`. A dedicated instrumented source-bridge variant or qualified low-inductance current-viewing resistor is the appropriate next step for quantitative switching-loss measurement. Neither should be silently inserted into the base power cell.

## Coil choice and release dependency

PEM's CWTUMHF-F/06 is a possible research candidate: 120 A peak, 50 mV/A nominal into high impedance, 30 MHz bandwidth, 1.7 mm coil cross-section and 55 mm coil length. It has more peak-current margin than the 60 A /03 version for the 51.9 A target. Its published /06 peak di/dt limit is 8 kA/µs. The example 51.9 A in 10 ns is 5.19 kA/µs, but a 5 ns transition is 10.38 kA/µs and exceeds that /06 limit. Selection therefore depends on the actual fastest edge as well as current range. These are manufacturer specifications, not a recommendation to purchase before confirming the fixture. [PEM product and performance table](https://www.pemuk.com/products/cwt-range/cwtumhf-f)

The simple bandwidth estimate t_r ≈ 0.35/BW gives 11.7 ns for 30 MHz. A 5 ns edge measured by such a first-order-limited chain would appear about sqrt(5² + 11.7²) = 12.7 ns, before other errors. This illustrative approximation explains why a coil that shows the pulse envelope may not quantify GaN edge energy. The oscilloscope, voltage probe and current probe must be deskewed and their complete transfer functions considered. Tektronix discusses these bandwidth and insertion-inductance limitations and the use of shunts/current-viewing resistors for wide-bandgap DPT. [Tektronix DPT application note](https://www.tek.com/en/documents/application-note/double-pulse-test-tektronix-afg31000-arbitrary-function-generator)

Final hole/slot placement is blocked until the coil model, insertion/end geometry, minimum bending radius, probe approach and cold-plate clearance are known. A 1.7 mm coil does not justify a 1.7 mm finished hole. Clearance must include manufacturing tolerance and insulation protection, and the removable end may govern insertion size. For provisional drawings, show a reserved mechanical region with dimensions explicitly unapproved; do not include speculative sensor slots in fabrication drill output.

## DPT connection and analysis

For low-side DPT, connect the external inductor between DC+ and AC, hold the high-side gate off, and pulse the low-side bank. The first pulse establishes inductor current; the off interval transfers current through the high-side reverse-conduction path; the second pulse captures turn-on and subsequent turn-off at the selected current. EPC GaN reverse conduction must not be described as a conventional silicon body diode. Approximately t_on = L_load I_target / V_bus when losses are small; specify the actual inductor and saturation rating before calculating pulse width.

Keep the load connection outside the local capacitor–high-side–low-side commutation cell. A Rogowski coil on the external inductor lead can validate pulse amplitude, while local paired VDS and VGS taps show switching voltage and gate behavior. This combination alone does not establish accurate per-device Eon/Eoff. Quantitative energy needs a validated device-current measurement and timing alignment. Initial pulses should be staged from reduced voltage/current with externally enforced nonoverlap and the required bootstrap startup procedure.

## Layout overlay convention

Draw the power loop as capacitor DC+ → high-side drain/source → low-side drain/source → capacitor DC−, explicitly indicating its L2 return and vias. Draw separate HO/HS and LO/VSS gate loops, including the local source return, not just the outgoing gate tracks. Mark capacitor currents as local branch currents and the AC lead as load current. Label arrows as representative commutation directions; current reverses with operating state. Any sensor bridge must appear in the appropriate loop overlay and inductance model.

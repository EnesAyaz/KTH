# Smaller sensing investigation - active direction

23 September 2026: user selected minimum power-loop inductance over retaining PEM CWTUM. This supersedes requirements that fix the individual-device measurement to that coil. Preserve the requirement for two independent QL1/QL2 current channels. Do not add CWTUM slots or return-plane detours to the compact board.

## Shortlist and decision

Investigate small PCB magnetic pickup structures first, with one local sensing channel per device and the main power conductors left flat. These need a calibrated transfer function, integrator or numerical reconstruction, electric-field rejection and a two-channel cross-coupling assessment. They do not measure DC directly. The available four-layer stackup and nearby return planes may prevent adequate local signal; no bandwidth or added-inductance value is established for our board.

Retain a low-inductance current-viewing shunt as a comparison/validation option, not a default source-series insertion. Two source shunts can be bypassed by a shared driver-source reference or introduce common-source feedback. Drain-side sensing avoids that particular source problem but demands high common-mode rejection. Its resistance, mounted inductance, heating and effect on current sharing require explicit evaluation. Ordinary current-monitor IC bandwidth is not evidence of nanosecond switching-current fidelity.

CPES demonstrates a planar Rogowski structure between DC bus conductors. Its published geometry adds 5.6 mm of bus length and reports a simulated 399 pH increase, with 1.3 nH mutual inductance. This supports investigating small printed pickups, but these numbers belong to that prototype, not ours. Its bus measurement also does not automatically separate two paralleled device currents. The distinction must be retained during adaptation.

For preliminary reconstruction, model v1=M11*di1/dt+M12*di2/dt and v2=M21*di1/dt+M22*di2/dt, plus electric-field pickup and instrument response. Calibrate both columns independently; evaluate frequency-dependent conditioning before attempting matrix inversion. Nearby copper and the installed metal spreader must be present during calibration. Numerical integration requires initial-current and offset treatment, and energy measurement requires voltage/current deskew.

Next: establish the compact power routing and compare local pickup placements without cutting return planes; quantify sensitivity and cross-coupling before adding a sensing connector or declaring a sensor selected. If that cannot distinguish branch currents reliably, report that limitation rather than treating the total bus signal as two independent channels.

## Sources checked

- https://cpes.vt.edu/library/view_nugget/1141 - primary institutional summary of planar DC-bus Rogowski research, 2023.
- https://www.tek.com/en/documents/application-note/double-pulse-test-tektronix-afg31000-arbitrary-function-generator - DPT measurement and current-viewing resistor considerations.
- https://www.mdpi.com/1996-1073/13/19/5161 - relevant PCB pickup research identified; full text fetch unavailable in this session, so no numerical design claims adopted from it.
- Local EPC AN023 reviewed for probing context; it does not by itself establish an individual-device current sensor implementation.

Current P8 is a placement-only board. Its 221 connected pin assignments match the exported schematic netlist. It has no tracks or zones and is not fabrication-ready.

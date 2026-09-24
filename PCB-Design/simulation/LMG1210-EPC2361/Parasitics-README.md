# HalfBridge_Parasitics
Open Open-Parasitics.cmd, or HalfBridge_Parasitics.asc with LTspice Alternate solver. Original HalfBridge.asc is unchanged. Its 75 V bus, 100 uH / 2 ohm load, 50 kHz IIM inputs and 1 ms duration are retained.

Edit this directive in the schematic:
.param RGON=2 RGOFF=0.5 LGATE=2n LPOWER=4n LCAP=0.5n

| Parameter | Meaning |
|---|---|
| RGON | External turn-on branch resistor, ohms, on each device |
| RGOFF | External turn-off branch resistor, ohms, on each device |
| LGATE | Lumped loop inductance for each gate, henries |
| LPOWER | Total commutation interconnect inductance, split equally into DC+ feed and DC- return |
| LCAP | Additional local DC-link capacitor ESL |

Defaults are exploratory assumptions, not PCB extraction. Total modeled power commutation inductance is LPOWER + LCAP, 4.5 nH by default. Do not put the complete loop inductance in each of LPPLUS and LPMINUS: they each contain half. The inductor in the load path is not part of the fast local commutation loop.

Gate branches:
- Turn-on: HO/LO -> RGxON -> forward diode -> LGx -> gate.
- Turn-off: gate -> LGx -> RGxOFF -> forward diode -> HO/LO.
- 100 kohm gate-source resistors provide a DC discharge/reference path.
- The diode models are generic simulation placeholders. Their forward voltage and capacitance influence gate voltage and transitions; resistors are branch values, not exact total effective drive impedance.
- The EPC model already includes 0.4 ohm internal gate resistance. Driver output impedance and diode resistance also contribute.
- LGATE represents a lumped gate-loop inductance with ideal Kelvin return. No shared/common-source inductance or mutual coupling has been added. Those require a distinct model, not simply adding the same inductance again to the gate and power paths.

Plots:
V(GH,SW) = high-side VGS
V(GL) = low-side VGS
V(DH,SW) = high-side VDS (DH is after LPPLUS)
V(SW) = low-side VDS relative to source node 0
V(HB,SW) = bootstrap voltage
I(LGH), I(LGL) = gate-loop currents
I(LPPLUS), I(LPMINUS) = interconnect currents

PGND is the capacitor/supply return, separated from low-side source/driver node 0 by LPMINUS. This arrangement deliberately keeps the low-side driver Kelvin-referenced to the device source. Gate source references remain SW and 0.

Optional .step examples are comments near the bottom of the sheet. Change ONE into a SPICE directive to sweep it. Use a small positive inductance, e.g. 1p, for a near-ideal baseline, rather than 0. Multiple enabled steps multiply the number of simulations.

Existing limitations still apply: TI PSpice-to-LTspice model warnings are unresolved; negative gate transients and nanosecond timing are exploratory. This model is not a hardware qualification or a validated switching-loss model.
Validation uses Parasitics_Check.asc (400 us total, measured 330-400 us). The main 1 ms run was stopped after reaching approximately 461 us because of runtime; its partial RAW is not a completed simulation. Main schematic remains set to 1 ms. The short check covers startup and five commanded switching cycles, not steady-state load qualification.

## Completed short check
Parasitics_Check.asc completed 400 us in 114 seconds with Alternate solver / Gear. Extrema over 330-400 us:
- High-side VGS: 0.064 to 6.109 V.
- Low-side VGS: -1.130 to 4.871 V.
- High-side VDS: -2.611 to 82.869 V.
- Low-side VDS: -3.173 to 162.548 V.
- Bootstrap: 4.265 to 4.623 V.
No sampled simultaneous VGS above 2.5 V in that interval. Simulation completion is not an acceptable-stress pass: the strong ringing is a result to investigate, not a validated prediction. Default values are not recommended hardware values. Driver translation warnings remain. Time-step/solver convergence and realistic diode/interconnect damping must be established before relying on peak amplitudes.

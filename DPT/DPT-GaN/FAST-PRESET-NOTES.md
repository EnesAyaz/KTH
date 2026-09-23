# 75 V / 45 A fast-switching preset

The GUI defaults and fast preset use 75 V, a 45 A target, +5/-1 V gate command and external Rg(on)/Rg(off) = 1/0 ohm. First pulse duration is automatically estimated; actual measured current is reported by LTspice and need not equal the target exactly. Load DPT-75V-45A-fast-zero-off.json for +5/0 V operation.

## Published device conditions

EPC2361 datasheet, revised July 20, 2026, page 6: typical waveforms use EPC90156, uP1966E pull-up/pull-down resistance 0.7/0.4 ohm, external turn-on/off resistors 1/0 ohm, 48 V and 30 A. These are the smallest external values explicitly stated in this datasheet's switching example, not a specified universal minimum or proof of safe operation at 75 V/45 A. The device's intrinsic 0.4 ohm gate resistance (page 2) already exists in the vendor model and is not added again. The local library is unchanged and is not asserted to match the latest datasheet revision.

Page 1 recommends +5 V on and 0 V off. Page 3 explains that negative gate drive increases reverse conduction voltage. -1 V is the user's negative-bias study setting, chosen to leave nominal margin above the -4 V absolute rating; it is not EPC's recommended off voltage. Gate ringing must still be checked. The older gate-driver application note discusses 4.5 V drive; the device-specific current datasheet takes precedence here.

Datasheet: https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf

## Parasitic budget and provenance

Optimizing PCB Layout with eGaN FETs, page 2 compares 1.6 nH and 0.4 nH loops; page 5 describes approximately 1 nH for a conventional eGaN power loop. These are other devices/layouts, not an extraction of EPC2361 or your PCB. We select a representative 1 nH complete loop budget, rather than assume the best-case 0.4 nH layout.

| GUI quantity | Default | Basis |
|---|---:|---|
| External PCB Lloop | 0.6 nH | Allocated share of the selected 1 nH complete-loop budget |
| DC-link ESL | 0.2 nH | Assumed share of that budget |
| Shared-source CSI | 0.1 nH per device | Assumed share; total budget = 0.6 + 0.2 + 2 x 0.1 nH |
| Private gate-forward / return L | 0.5 / 0.5 nH per device | Compact-layout engineering assumption, not a published extracted value |
| PCB power-loop R | 5 milliohm | Retained estimate, not measured in the supplied papers |
| Private gate-forward / return R | 20 / 20 milliohm | Retained trace estimates |
| Shared-source R | 100 microohm per device | Retained estimate |
| DC-link C / ESR | 470 uF / 5 milliohm | Lumped bank assumption; requires an actual bank specification |
| Local Cdecap | Disabled | Avoid assuming an additional unidentified capacitor |

The current 50/50/0 percent positive/return/middle allocation is a user-selected symmetric modeling assumption. This means 0.3 nH and 2.5 milliohm in each outer path at the defaults. CSI stays equal and separate. The midpoint branch has zero requested L/R (a 1 fH solver floor). Published loop values cannot determine its individual branches. AN020 reports optimized loops below 0.4 nH and package inductance below 0.2 nH for the devices discussed there; those are not EPC2361 package extraction values. The gate-driver note's damping criterion relates allowable gate-loop inductance to gate capacitance and total source resistance; it does not establish a universal trace inductance. Impact of Parasitics on Performance emphasizes minimizing shared-source and commutation-loop inductance. No additional intrinsic input capacitance is added: nonlinear device capacitances are already in the vendor model.

The model therefore uses a literature-informed total inductance with explicit estimated allocations. Its resistances, capacitance-bank values and gate-loop values remain editable assumptions, not values falsely attributed to the papers. A real 470 uF bank will generally need local ceramics to achieve the assumed high-frequency impedance; specify its measured/equivalent impedance or enable explicit local decoupling when known.

## Validation

The exported negative-off simulation and measurements are under parasitic_refinement/fast_75V45A. This is a fast-switching study preset, not a voltage-qualified optimum. Keep the 100 V design ceiling and inspect both devices' Vds and Vgs results. A smaller external resistor does not remove intrinsic gate resistance or driver impedance. No broad resistance optimization was repeated.

Completed default-solver simulation (100 ps maximum step): second-turn-on current 44.2869 A; DUT Vds peak 88.771 V; HS Vds peak 109.588 V; DUT Vgs range -1.46314 to 5.32179 V; HS Vgs range -2.75466 to 0.902656 V. The upper device exceeds the 100 V design ceiling. These are nominal simulation results, not a convergence or hardware qualification.

The earlier recorded results above used the previous 40/40/20 allocation. New symmetric results are stored separately in parasitic_refinement/symmetric_75V45A. Equal outer-path parasitics do not force equal voltage stress because only the lower device receives DPT gate pulses. Local_bus_peak/min now measure V(rail,pgnd), separate from Rail_peak relative to supply ground.

# Refined DPT parasitics

Restart the GUI using Launch-DPT.cmd. The Power parasitics and Gate parasitics tabs contain the new controls. The 75 V / 50 A preset loads DPT-75V-50A-refined-parasitics.json. It retains the previous candidate operating point, +5/0 V gate commands and 10/10 ohm external gate resistances.

## Power paths

Refined mode distributes Lloop and Rloop between the positive DC feed, bridge return, and high-side-source-to-switch-node interconnect. Inductance and resistance have independent allocation fractions. The middle path receives the remaining fraction; positive plus return fractions cannot exceed one.

Lloop excludes capacitor ESL and each device's shared-source inductance (CSI). RCSI represents additional shared-source PCB resistance. The vendor device model, including its intrinsic gate resistance and device conduction losses, is unchanged: do not count those resistances again as PCB resistance.

The initial allocation is 40% positive feed, 40% return and 20% middle path. RCSI starts at 100 microohm per device. These are illustrative values, not PCB extraction results.

## Gate paths

Both devices now have separate forward and private return inductances and trace resistances. Each path initially uses 0.5 nH and 20 milliohm. Shared-source CSI is separate: it carries both power and gate-return current and therefore produces source feedback. The driver references connect through the private return path to the external source reference of each device.

External gate resistors and existing driver resistance remain in the circuit. The high-side off-state resistance control includes its external resistor and driver resistance. Results include both devices' minimum and maximum Vgs, as well as Vds peaks, to expose gate-loop effects.

## Decoupling

Cin remains the bulk capacitor. Optional Cdecap connects directly across the local bridge rail and return with independent ESR and ESL. It is disabled by default (Cdecap = 0). Use effective capacitance at operating DC bias and realistic connection ESL.

With local decoupling, the fast commutation loop can bypass the bulk positive feed and return. Therefore Lloop is the total allocated bulk-to-bridge PCB inductance, not necessarily the effective local commutation inductance. Local capacitor ESL, middle-path inductance and shared-source inductances still matter. Re-export after changing topology mode or enabling/disabling this capacitor.

## Existing settings

Older JSON settings load in legacy mode, preserving the original physical circuit. To enable the new model, use Apply illustrative parasitic starting values on the Power parasitics tab. This preserves the operating point, total Lloop/Rloop and CSI while filling the new controls. Refined = 0 keeps the original topology and ignores the new parasitic controls.

## Validation and limits

validate_parasitic_refinement.py checks legacy topology compatibility, settings validation, driver references, GUI controls and schematic completeness. It runs three bounded simulations using the existing 75 V / 50 A candidate preset: legacy, refined, and refined with a 4.7 uF local capacitor (test only). All three completed, and LTspice successfully netlisted the refined schematic. Results and exact settings are in parasitic_refinement/validation/results.json. These checks use Gear integration and tighter solver tolerances; they validate operation, not numerical convergence or hardware voltage qualification.

Run with Python: python -X utf8 validate_parasitic_refinement.py. Unchanged simulation inputs reuse existing waveforms.

This is a lumped model with constant resistances. It does not include extracted magnetic coupling, frequency-dependent copper loss, or a detailed nonlinear gate-driver model. Real PCB resistance can attenuate ringing, but damping and voltage margin must be established with realistic parameters and measurements. Earlier optimization reports remain unchanged and do not qualify this revised topology.

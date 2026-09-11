# Parallel EPC2361 layout estimate: four to six devices

The supplied EPC9186 quick-start guide (revision 1.0, 2 April 2026) gives
no numerical loop inductance. EPC9186 uses four EPC2302 devices per position.
EPC9186HC2 uses two EPC2361, and EPC9186HC3 uses three EPC2361. These distinctions
matter when comparing capacitance, resistance and gate-driver load.

The supplied guide specifies a maximum input of 60 V, even though the live
product page currently advertises a wider range. Its documented 48 V tests
do not validate operation of our 75 V module. The listed minimum input pulse
is 120 ns, unlike the 10 ns placeholder in our analytical input. Adopting
that board's driver would require updating the timing assumptions.

## What can be estimated before layout?

EPC AN020, Figure 10, compares another four-parallel design using EPC2001:
approximately 0.4 nH per paired local commutation loop with distributed
loops, versus approximately 1.7-2.6 nH in a larger shared-loop arrangement.
These are useful layout references, NOT extracted EPC9186 or EPC2361 values.

For preliminary four-to-six EPC2361 studies, sweep complete local-loop
inductance at 0.5, 1, 2 and 3 nH. Treat 0.5 nH as an aggressive compact-layout
case requiring extraction, not a default guaranteed value. Separate shared
capacitor/bus paths, drain/source branch paths, gate-loop inductance, and
common-source inductance. Keep mutual coupling and branch mismatch visible.

For equal current in N symmetric branches with identical self-inductance Lb
and equal mutual inductance M=k*Lb:

    Leffective = Lshared + [Lb + (N-1)*M]/N

Only the uncoupled independent portion divides by N. Shared paths do not.
If physical routing grows with N, even Lshared and Lb can increase. This
common-mode approximation does not describe branch imbalance or ringing
between devices; a real transient model needs individual branches.

The archived early scenario file contained these explicitly assumed scenarios (historical examples):

| Scenario | Shared nH | Full branch nH | Coupling k |
|---|---:|---:|---:|
| Compact assumption | 0.3 | 0.8 | 0.1 |
| Central assumption | 0.6 | 1.5 | 0.2 |
| Extended assumption | 1.5 | 3.0 | 0.3 |

These give illustrative effective values of about 0.5-3 nH across four to
six branches, not a confidence interval for the actual board. Do not insert
these totals into the old single-device bus-inductor parameter: that parameter
excluded its separately modeled common-source inductance.

## Current and thermal implications

At 75 V, 18.75 kW, modulation 1.15 and unity power factor, phase current is
about 205 A RMS / 290 A peak before ripple. Equal device peak currents are
about 72.5 A (N=4), 58.0 A (N=5), and 48.3 A (N=6).

Actual full-cycle RMS current per device is Iphase_rms/(sqrt(2)*N) under
the balanced sinusoidal ideal-sharing model. With 1.65 mOhm hot resistance,
module conduction losses alone are about 52.0, 41.6 and 34.7 W respectively.
These exclude switching, copper, capacitor, control and driver losses.

Six is a useful candidate within the user's current cap: it leaves more
current-sharing margin than five against the present 60 A/device design
screen. It does not by itself demonstrate 99.5% module efficiency or thermal
feasibility. Real local TIM, plate-to-water resistance, thermal coupling
and unequal switching losses still determine the hottest device.

## Requirements for a credible parallel SPICE model

- Model four/five/six actual FET instances in each position.
- Give every device its own gate resistor and branch parasitics.
- Include the shared driver's source/sink impedance once; it sees the sum
  of gate currents, not a fixed current independent of device count.
- Place local HF decoupling at each paired commutation cell where feasible.
- Use symmetric power and gate returns; retain a Kelvin source return.
- Sweep branch mismatch and mutual coupling, not only total loop inductance.
- Resolve the actual driver minimum pulse width before using near-limit SVM.

The previous single-device 3-ohm ON / 1-ohm OFF candidate does not transfer
directly to a six-device bank. Six devices have roughly six times the gate
charge and the common driver drop changes switching times.

A board-specific estimate needs Gerbers/ODB++ or PCB CAD, layer stackup,
copper geometry, capacitor placement and ESL, via geometry, and driver
placement. Use those for field extraction (e.g. Q3D) or validated impedance/
ringing measurements. Do not infer L from voltage dv/dt alone.

For the active geometry calculator use scripts/estimate_loop_from_geometry.py and data/inputs/paper_loop_geometry.json. The active half-bridge study is data/inputs/design.json and models/half_bridge.py, restricted to N=4/5/6.


Source: [EPC AN020](https://epc-co.com/epc/Portals/0/epc/documents/application-notes/AN020%20Effectively%20Paralleling%20Enhancement%20Mode%20Gallium%20Nitride%20Transistors.pdf).

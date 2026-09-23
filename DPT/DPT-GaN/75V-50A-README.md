# 75 V / 50 A DPT candidate

Open Launch-DPT.cmd and choose **75 V / 50 A preset**. The new Vds design ceiling field defaults to 100 V. Results report the worst of the two devices and remaining voltage margin; a below-ceiling result describes only that simulation.

## Saved candidate

| Parameter | Value |
|---|---:|
| DC supply | 75 V |
| Nominal target current | 50 A |
| Load inductor | 20 uH, 20 mOhm |
| First pulse | Manual 13.537 us |
| DC-link capacitor | 470 uF |
| Capacitor ESR / ESL | 5 mOhm / 0.2 nH |
| Additional layout inductance | 1 nH |
| Loop resistance | 5 mOhm |
| CSI per device | 0.1 nH |
| External Rg_on / Rg_off | 10 / 10 ohm |
| Driver pull-up / pull-down resistance | 0.7 / 0.4 ohm |
| Fixed temperature | 100 deg C |
| Maximum timestep | 250 ps |
| Frequency for estimated losses | 500 kHz placeholder, edit to intended frequency |

470 uF is a lumped local DC-link-bank assumption. Its 0.2 nH ESL and the 1 nH PCB loop must be supported by the actual layout and capacitor network; assigning these values in software does not create that performance in hardware. The first pulse is calibrated for this candidate. Re-estimate or retune it after changing voltage, inductance or gate resistance. The manual setting intentionally reaches approximately 50 A at the first turn-off / second turn-on; current rises further during the second pulse.

## Nominal simulation

At second turn-on: 50.1089 A.
Lower device maximum Vds: 86.5035 V.
Upper device maximum Vds: 78.789 V.
Nominal margin to 100 V: 13.4965 V.
DUT-only window-energy switching-loss estimate at the placeholder 500 kHz: 38.8599 W. This is not total half-bridge loss or a thermal qualification. Frequency changes scale this estimate; the simulated sequence remains a DPT with the upper device held off.

The original gate resistances and parasitics, at 75 V with the larger 470 uF capacitor, produced 153.782 V lower-side and 183.49 V upper-side. Slowing the gates alone while retaining 5 nH layout / 1 nH capacitor ESL (22 ohm external on and off) produced nominal peaks 96.1626 V and 91.7855 V, with limited voltage margin. These are comparisons, not hardware prescriptions.

## Corner / numerical limitations

The earlier candidate with Rg_off=5 ohm gave 88.64 V / 78.82 V at 1 ns and 88.66 V / 78.79 V at 250 ps. A combined 82.5 V supply, 1.5 nH layout, 0.3 nH ESL, 150 deg C corner gave 100.928 V on the lower device. This motivated increasing external Rg_off to 10 ohm.

For the saved 10-ohm-off candidate, illustrative corners were run using Gear integration and 1 ns maximum timestep:
- 82.5 V, 1.5 nH layout, 0.3 nH ESL, 25 deg C: approximately 55.13 A, lower peak 98.9151 V, upper peak 98.147 V.
- Same voltage/parasitics, 150 deg C: approximately 55.13 A, lower peak 96.5633 V, upper peak 89.4934 V.

These are intentionally more stressful examples, not specified component tolerances or an exhaustive worst-case analysis. Only about 1.1 V margin remains in the cold example. The finer-step default-solver hot case and a separate 100 ps run timed out before completing. Therefore neither full numerical convergence nor robust worst-case margin has been established. Do not treat this preset as certified safe for hardware or continuous 50 A operation.

## Rating and next design decision

Use 100 V as the ceiling and allow further margin for bus variation, component variation and measurement uncertainty. The current EPC2361 datasheet gives a 120 V repetitive-transient rating only with duty factor <=1%; it is not an unrestricted 120 V operating rating. Source: https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf (accessed 2026-09-16).

Qualifying a real 75 V / 50 A half-bridge requires its actual power-loop and capacitor parasitics, gate-driver behavior, switching frequency, current waveform and thermal conditions. If those cannot give adequate voltage margin, evaluate damping/snubbing or a higher-voltage device, rather than relying on the 120 V exception. Synchronous high-side gating belongs to a complementary-switching test with dead time; it cannot clamp the upper device while the lower device is on.

Files: DPT-75V-50A-candidate.asc/.cir/.json. Numerical studies are in study_75V_50A, including screening.json, verification.json, off10_verification.json and corner_gear_25/results.json / corner_gear_150/results.json. All existing source circuits and user presets were preserved.

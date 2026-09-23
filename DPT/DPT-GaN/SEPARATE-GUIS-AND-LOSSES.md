# Separate DPT and half-bridge applications

- Launch-DPT.cmd opens only the double-pulse-test interface. No PWM tab or conduction estimate is shown.
- Launch-HalfBridge.cmd opens only the synchronous RL half-bridge interface, initialized with HalfBridge-75V-RL.json. DPT-only pulse/current controls are hidden. Mode is fixed by the launcher. Settings from the other mode are rejected with an explanatory message.

Both applications retain save/export, Run simulation, schematic view and switching slopes. Their circuit code is shared to keep the vendor model and parasitic definitions consistent. Rerun a simulation from the new half-bridge GUI to obtain the internal signals required for losses; older RAW files without them show Unavailable.

## Half-bridge loss measurements

Measurements include per-device Eon/Eoff in uJ, Pon=Eon*f and Poff=Eoff*f in W, on-state conduction, reverse conduction during effective dead time, other/off-state loss, and total channel plus internal drain/source resistance dissipation. A Measurement definitions tab explains the calculation; a .losses.json file accompanies processed results.

The calculation uses the unchanged EPC2361 model's internal channel element Bswitch and internal Rd/Rs elements. Instantaneous dissipative power is Vds_internal*I(Bswitch) plus the voltage-current products for Rd and Rs. This avoids interpreting ideal capacitor charge storage as heat, and no extra Eoss loss term is added. The reported total excludes intrinsic gate-resistor/leakage loss, external gate-driver power, PCB loss, capacitor ESR heating and load loss. It is not total converter loss or a complete device electrothermal model.

Three complete interior cycles are averaged by default (fewer for very short runs); cycle boundaries occur within a high-side on interval to avoid cutting a switching event. The actual averaging interval is written to the JSON output. Initial warm-start current does not prove periodic steady state; increase Cycles and inspect settling when needed.

Exclusive allocation, in priority order:

1. Dead-time reverse conduction: both internal Vgs values are below LossVth, and the device has negative internal Vds and negative channel current. LossVth defaults to 1.5 V as an adjustable classification assumption, not an extracted physical turn-off boundary or universal datasheet threshold.
2. Eon/Eoff: remaining dissipation in Wpre/Wpost windows around that device's on/off command edges. Overlapping windows are rejected. Dividing energy by the number of cycles gives uJ/event; multiplication by frequency gives watts. These are window-attributed energies, including any on-state dissipation inside the window, not standardized isolated switching-energy measurements.
3. On-state conduction: remaining dissipation with internal Vgs >= LossVth, including gate-on reverse-channel conduction.
4. Other/off-state: remaining dissipation, retained visibly rather than dropped.

All categories sum exactly to the reported channel/Rd/Rs total. Moving the switching windows or threshold can change the split without changing that total. Dead-time-associated capacitive switching losses may appear under switching; the dead-time row specifically represents reverse conduction. Small lower-device Eon/Eoff is consistent with synchronous/soft-switching operation and is not assumed to equal upper-device loss.

## Validation

Run python -X utf8 validate_separate_guis.py to reuse the saved waveform for GUI mode/reset checks, energy partition closure, E*f conversions, result availability and matching schematic/netlist device names. Validation data: half_bridge_validation/losses/HalfBridge.raw and HalfBridge.losses.json. No broad parameter sweep is required.

The nominal 75 V case at approximately 43.8 A gives (100 ps maximum timestep):

| Quantity | Upper | Lower |
|---|---:|---:|
| Eon window (uJ) | 24.2404 | 0.208274 |
| Eoff window (uJ) | 0.119380 | 0.291850 |
| Pon (W) | 12.1202 | 0.104137 |
| Poff (W) | 0.059690 | 0.145925 |
| On-state conduction outside switching windows (W) | 0.626402 | 0.618197 |
| Dead-time reverse conduction (W) | 0 | 1.088602 |
| Total channel + Rd/Rs (W) | 12.8063 | 1.95688 |

These values depend on the stated partition and the supplied device model; they are not hardware-validated losses.

## Reference basis

The supplied AN030 Hard Switching Losses Calculation, page 6, distinguishes stored capacitive energy from dissipated energy. Dead-Time Optimization for Maximum Efficiency, page 1, distinguishes effective gate-threshold dead time from command dead time, and identifies reverse conduction as only one dead-time-related loss. Selecting eGaN FET Optimal On-Resistance discusses differing device loss components; Impact of Parasitics on Performance motivates retaining the explicit external parasitic network. Their analytical formulas guide interpretation, while this implementation integrates model dissipation instead of adding analytical Eoss or I^2R terms on top of it.

# Open directly in LTspice

Open half_bridge_N4.cir, half_bridge_N5.cir or half_bridge_N6.cir in LTspice and click Run. These are editable SPICE netlists, not graphical .asc schematics. Keep EPC2361.lib in the same folder; no global library installation is required.

The three files instantiate 8, 10 and 12 actual EPC2361 vendor subcircuits respectively. They are not a single transistor scaled by a multiplier.

## View waveforms

After Run, activate the waveform window and use Plot Settings > Add Trace (or right-click > Add Trace):

- V(sw): switch-node voltage relative to DC−.
- I(Lload): phase-inductor current, positive from SW toward the load.
- V(gH1,sH1), V(gL1,sL1): package gate-to-source voltages of one upper/lower device.
- I(LdH1), I(LdL1): corresponding branch drain currents.
- V(duty), V(carrier): PWM duty and triangular carrier.
- V(dc): local capacitor/DC-link node.

The .save line restricts waveform storage. Add other device nodes/currents there before rerunning if you want to compare every branch. View > SPICE Error Log shows peak voltage/current measurements and simulation diagnostics.

## Parameters at the top of each file

| Parameter | Default | Meaning |
|---|---:|---|
| Vbus | 75 | DC-link voltage, V |
| Fsw | 20k | Carrier frequency; change to 100k for a later study |
| Ffund | 1k | Illustrative fundamental frequency, not specified motor data |
| ModIndex | 0.8 | SPWM modulation, use less than 1 with timing margin |
| Tstop | 2m | Two fundamental cycles at 1 kHz |
| Lphase | 20u | Illustrative load inductance |
| Rphase | 0.1 | Illustrative winding/series resistance |
| BemfPeak | 20 | Sinusoidal back-EMF peak voltage |
| BemfPhase | 0 | Back-EMF phase in degrees |
| Ron / Roff | 3 / 1 | Individual external gate path resistance, ohm |
| RdrvOn / RdrvOff | 0.5 / 0.5 | Shared driver output resistance per bank |
| Deadtime | 20n | Nominal nonoverlap parameter; finite command slew affects actual gate timing |

Temperature is fixed at 125 C using .temp. The local 20 uF capacitor, ESR/ESL, feed inductance, per-device drain/source inductance and gate inductance are assumptions. They are not PCB-extracted or component-qualified values. The vendor model contains its own internal gate resistance in addition to the external resistances.

## Circuit interpretation and limits

The upper bank connects DC+ to SW; the lower bank connects SW to DC−. SW drives Lphase, Rphase and a sinusoidal back-EMF source returned to an ideal DC midpoint at Vbus/2. This is a single-leg SPWM test bench, not a complete three-phase motor or SVM implementation.

Gate commands are smoothly transitioned behavioral sources. Each bank has one shared driver output impedance; each transistor has separate on/off resistance and gate inductance. It is not a particular gate-driver IC: no current limit, UVLO, isolation, propagation mismatch, bootstrap dynamics or fault logic is modeled. Source-return parasitics are retained and can disturb actual package Vgs.

The DC capacitor is initialized charged and the phase inductor starts at zero current (.tran ... uic). Startup behavior is therefore an imposed initial condition, not a power-supply startup simulation. The two-cycle run includes initial current transients; extend the simulation until periodic steady state before averaging losses.

Current results from PWM voltage minus back EMF across R/L. It is not forced to 205 A RMS, and need not be perfectly sinusoidal. Use actual motor values or a controlled-current fixture for rated current characterization. The model is not an efficiency or thermal validation; do not interpret a successful simulation as a safe gate-resistor selection. Inspect both upper and lower Vds/Vgs and all branch currents before increasing stress.

The default maximum step is 20 ns. LTspice takes smaller adaptive steps at switching events, but energy/overshoot conclusions require deliberate timestep and tolerance convergence checks. No switching-energy measurement is supplied here because terminal energy includes reactive storage. Use the existing DPT characterization workflow for defined switching-energy extraction.

smoke_test.cir is a short 40 us N4 initialization/syntax check. Full default examples are also run during creation; see their .log files for results. Source EPC2361.lib is copied unchanged from data/spice/EPC2361.lib.

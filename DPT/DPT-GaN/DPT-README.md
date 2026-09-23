# EPC2361 double-pulse test

Double-click **Launch-DPT.cmd** or **Launch-GUI.cmd**. The original buck editor remains available through Launch-Buck-GUI.cmd. Python with Tkinter is required; no extra packages are needed by the GUI.

## Use

1. Set bus voltage, load inductance and target current.
2. With AutoT1=1, the first pulse plateau is estimated as Itest * Lload / Vin. With AutoT1=0, enter Tcharge. Target current does not force the simulated current: finite bus capacitance, losses, edge times and reverse conduction affect it. Use I_first_off and I_second_on from the results to tune the pulse.
3. Set Toff, Tsecond and driver edge times. This is a single two-pulse sequence, so PWM frequency/duty cycle are replaced by explicit durations. Toff is the inter-pulse gap; the upper device is held off, not driven complementarily.
4. Set Cin, ESR, ESL and Lloop in DC link & layout. Run DPT executes LTspice in the background and opens the result log. Open waveforms launches the saved raw file in LTspice.
5. Save setup exports an .asc schematic, matching .cir netlist and .json settings. Load settings restores the GUI from JSON. Save + open opens the schematic in LTspice.

Each run is isolated in dpt_runs with a timestamp and copies of the supplied symbol/library. The GUI runs the .cir file in batch mode. Schematic connectivity and its LTspice-generated netlist were separately tested against the same model. The schematic uses labeled terminals: matching names are connected. The local .\\EPCGaNLibrary.lib path avoids selecting an older library from LTspice's search path.

## Circuit definition

Vdc -> Rcharge -> bus -> Llayout (Rloop in series) -> rail.
The DC-link branch is bus -> ESR -> ESL -> Cin -> ground.
Lload connects rail to the switching node sw, with resistance Rload.
The upper EPC2361 connects rail to sw through its common-source inductance. Its gate is held at Voff relative to sw through Rg_HS, allowing reverse conduction during freewheel and off-state gate movement through its nonideal gate impedance.
The DUT connects sw through a zero-volt drain-current sensor to the lower EPC2361, then through CSI to ground. Driver return is ground, so CSI is common to gate and power paths.
The lower driver uses two voltage-controlled switches with separate pull-up and pull-down resistance (external resistor plus driver resistance). It is an idealized driver, not a manufacturer gate-driver IC model.

Cin means external DC-link input capacitance, not device Ciss. Intrinsic nonlinear device capacitances remain in the original EPC library. Lloop is additional lumped PCB/bus inductance. Capacitor ESL and device CSI are separate; avoid counting them again in Lloop. Zero external inductance is approximated by 1 fH to keep a valid inductor element.
Rcharge provides supply isolation so an ideal voltage source does not clamp away capacitor droop. The DC operating point charges Cin before the pulses; the load current starts near zero. The old buck output RC load, PWM drive, efficiency measurements and invalid C2 initial condition are not part of the DPT circuit.

Both devices use the supplied EPC2361 GaN model at fixed global temperature Tj. No Wolfspeed SiC model was substituted. Reverse conduction is represented by the GaN model; do not interpret it as a SiC body-diode reverse-recovery model. This model has no load-inductor saturation or dynamic self-heating.

## Measurements

- I_first_off / I_second_on: load current at the first falling command edge and second rising command edge, in A.
- Vds_peak: maximum DUT drain-to-source voltage over the entire run, in V.
- Vbus_min: minimum capacitor-bus terminal voltage, including high-frequency ESR/ESL transients, in V; it is not simply capacitor electrostatic voltage droop.
- Eoff1_window / Eon2_window / Eoff2_window: signed integrals of DUT terminal Vds * drain current from Wpre before the command edge to Wpost after it, in joules. They are adjustable-window terminal energies, not standardized datasheet switching losses. Ringing and displacement current can make them negative. Inspect the waveform and adjust integration bounds before using them for loss estimation.

Plot V(drain,sl), V(gl,sl), V(gh,sh), I(Vsense), I(Lload), and V(bus). DPT-waveforms.png shows the actual default simulation. Pulse plateau times exclude finite rise/fall edges. Defaults are illustrative GaN test values, not limits taken from the SiC reference articles.

## Validation

Run `python test_dpt.py`. Tests check invalid inputs, auto/manual timing, two rising and two falling command edges in actual binary waveforms, source-to-schematic connectivity, simulation agreement with LTspice's generated schematic netlist, parasitic sensitivity, and the GUI's asynchronous Run flow.

Default: 48 V, 16 A nominal target, 20 uH, 100 uF Cin, 5 nH Lloop, 100 deg C.
Actual first turn-off current: 15.8411 A. Second turn-on current: 15.7675 A. Peak Vds: 57.3029 V.
At 20 nH layout inductance: peak Vds 69.7361 V.
At 10 uF Cin: first turn-off current 15.3277 A.
Full results: dpt_validation/results.json. Validation is for simulation behavior; it is not hardware correlation.

## Supplied references

- Wolfspeed, PRD-07913 Rev. 2 (December 2023), pages 7-8, Figures 6-7: clamped inductive double-pulse setup, charge-pulse/load-inductance control of current, bus inductance and additional parasitics. Source: C:/Users/enesa/Downloads/Wolfspeed_PRD-07913_Power_Modules_SPICE_Models_User_Guide.pdf.
- Infineon, Double Pulse Testing: The How, What and Why (Bodo's Power Systems, April 2020), PDF page 1, Figures 1-2, and page 4: pulse sequence, half-bridge alternative, measurement of switching behavior and layout effects. Source: C:/Users/enesa/Downloads/Infineon-Double_pulse_testing-Bodos_power_systems-Article-v01_00-EN.pdf.

## Updated results: high-side stress, microjoules and switching power

Operating point now includes Fsw (default 500k Hz). It is only the frequency used to scale measured event energies, not the repetition rate of the two-pulse waveform. Existing JSON settings files load with the default Fsw when that field is absent.

The Measurements tab shows high-side maximum/minimum Vds = V(rail,sh), high-side maximum/minimum Vgs = V(gh,sh), low-side maximum Vds, and Eoff1/Eon2/Eoff2 in microjoules. Original signed joule integrals remain available in the raw log. The exported schematic also measures the microjoule conversions and powers directly.

Primary estimate:
Psw_DUT [W] = (Eon2 [uJ] + Eoff1 [uJ]) * Fsw [Hz] * 1e-6.

Eon2 and Eoff1 occur at approximately the same load current, making them a better matched pair than summing both events of pulse 2. An alternate Eon2+Eoff2 estimate is also displayed; Eoff2 occurs at higher current after the second ramp. Neither estimate includes high-side, conduction or driver power. These are event-energy extrapolations, not a periodic converter simulation. Negative event integrals remain visible, but the GUI withholds a dissipative power estimate for that pair instead of taking absolute values.

For the baseline 1 ns maximum-step run: Eoff1 = 1.62869 uJ, Eon2 = 0.763706 uJ, Eoff2 = 1.73332 uJ. At 500 kHz, the primary estimate is 1.1962 W and the alternate is 1.24851 W. These quantities depend on integration bounds and timestep; they are not yet a converged hardware loss prediction.

## Why the high-side rings

Diagnostic runs reproduced the high-side peak at 125.045 V. With a 250 ps maximum step the peak was 125.526 V; Gear integration at 250 ps gave 125.689 V. This supports a circuit resonance rather than only trapezoidal integration ringing. The modeled loop has very low damping, while the low-side rapidly commutates the nonlinear capacitances of both devices. Layout inductance, capacitor ESL and CSI store energy and participate in the resonant response. The off-state gate network can couple this response into Vgs; peak Vgs alone does not prove that unintended channel conduction is absent.

Sensitivity experiments (illustrative changes, not a fitted hardware model):
- Lloop reduced from 5 nH to 1 nH: high-side peak 101.701 V.
- Rloop increased from 5 mOhm to 50 mOhm: high-side peak 121.181 V.
- External Rg_on increased from 1.8 to 5 ohm: high-side peak 112.129 V.

The waveform rings when the lower device turns ON, when the upper device must block. Driving the upper device on at the same time would create shoot-through. Holding the upper device off is valid for a reverse-conduction DPT. Synchronous high-side drive during the freewheel interval is a different test mode; it requires dead time before and after its pulse and does not by itself eliminate the resonance at low-side turn-on. No high-side drive pulse was silently added.

EPC enhancement-mode GaN has reverse channel conduction but no silicon-like PN body diode / minority-carrier reverse-recovery charge. Output-capacitance charge/discharge current is still present. Therefore a current spike or Vds ringing should not automatically be labeled diode reverse recovery.

The EPC2361 datasheet specifies 100 V continuous Vds and 120 V repetitive transient Vds at duty factor <=1%. The simulated approximately 125 V exceeds even that transient figure; do not interpret the unconstrained model waveform as proof of device survival. The GUI flags this observed condition.

Sources:
- EPC AN002, Fundamentals of GaN Power Transistors: https://epc-co.com/epc/Portals/0/epc/documents/product-training/appnote_ganfundamentals.pdf
- EPC AN003, Using Enhancement Mode GaN-on-Silicon Power FETs: https://epc-co.com/epc/Portals/0/epc/documents/product-training/using_gan_r4.pdf
- EPC2361 datasheet, February 20, 2026: https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf

Diagnostic data are in ringing_diagnosis/results.json. Run diagnose_ringing.py to reproduce the principal comparison cases. Unit/integration tests now also check high-side peak against waveform samples, uJ conversion, linear frequency scaling, and older settings compatibility.

Additional convergence check: reducing Maxstep to 100 ps gave Eon2=0.493051 uJ and primary Psw=1.05536 W; at 50 ps it gave Eon2=2.22383 uJ and Psw=1.90466 W. High-side peaks remained approximately 125-126 V. The default energy/loss result is therefore NOT numerically converged. Voltage-peak stability does not establish switching-energy accuracy. Inspect time-resolved terminal power and integration bounds and establish solver/timestep convergence before treating displayed watts as design losses. These finer runs are saved under ringing_diagnosis/step_100p and step_50p.

## 75 V / 50 A candidate preset

Use the new **75 V / 50 A preset** button. See 75V-50A-README.md for tested values, nominal peaks, corner results and numerical limitations. The new Vlimit field controls a per-run Vds ceiling report, not a physical voltage clamp. Existing settings load with Vlimit=100 V if absent. This preset is not a hardware-safe or thermally qualified configuration.

## Conduction loss and live schematic

The **Conduction loss** tab calculates periodic half-bridge ON-state loss without requiring a simulation:

P_LS = I_rms,on^2 * DutyLS * RdsLS
P_HS = I_rms,on^2 * DutyHS * RdsHS
P_halfbridge,on = P_LS + P_HS

Icond is RMS current within each device's ON interval, not RMS averaged over the whole switching period. This simple model assumes the same ON-interval RMS current for both devices. The ON fractions weight the result once and must sum to at most one. If current is approximately constant at 50 A, both ON fractions are 0.5, and both resistances are 2 mOhm, the estimate is 2.5 W per device / 5 W combined. For current ripple, enter the appropriate RMS current rather than the peak target current.

RdsLS and RdsHS are editable effective on-resistances at the operating junction temperature and gate voltage. The 2 mOhm defaults are illustrative assumptions, not extracted from the EPC model or guaranteed datasheet values. Changing Tj does not automatically rescale them. Older settings/presets initialize Icond from Itest when no separate conduction current was saved. Subsequent Icond edits are independent of the DPT target current.

These estimates describe a separately assumed periodic, synchronously operated half-bridge; they are not averaged losses of this DPT sequence, in which the upper FET is held off. Dead-time reverse conduction, switching, gate-drive and passive losses are excluded. The estimate does not provide total converter loss or predict device temperature. Results also show the three conduction values in watts, with a scrollbar to reach all measurements. The existing switching estimate remains DUT-only; it is not silently added to conduction and called total half-bridge loss.

The **Setup schematic** tab displays a live simplified circuit: source/charging resistance, DC-link ESR/ESL/capacitance, layout inductance, load inductor, both FETs, common-source inductances, drain-current sensing and gate drive. Labels update with the GUI inputs. Its driver return references are explicitly labeled. The gate-command preview remains visible below the tabs. The exported .asc remains the executable LTspice schematic. Conduction assumptions are saved in JSON but intentionally excluded from the electrical netlist so they do not change the DPT simulation.

Implementation: dpt_visuals.py provides the diagram and analytic conduction calculation; keep it beside dpt_gui.py. Tests verified duty weighting, units, invalid inputs, old-settings migration, unchanged electrical netlists, live diagram labels and the simulation/results flow.

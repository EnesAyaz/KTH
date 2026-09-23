# Synchronous half-bridge with an RL load

Restart Launch-DPT.cmd, open Half-bridge PWM and click Load 75 V RL + film/ceramic preset. Mode 0 retains DPT; Mode 1 runs complementary PWM. Save setup exports a complete .asc, .cir and .json. The Setup schematic tab changes with the mode.

The load connects switch node -> Lload (with winding Rload) -> Rout -> local bridge return. This is a unipolar buck-style RL half-bridge, not an H-bridge or a motor back-EMF model. Both gates have their own source-referenced supplies and private gate-loop parasitics. The existing external Rg(on/off) and pull-up/down resistances apply to both devices in PWM; Rg_HS is used only in DPT. Deadtime is the interval from one command finishing its falling ramp to the other beginning its rising ramp. Actual device timing depends on the gate network.

## Preset

75 V, 500 kHz, 50% duty, 10 ns command dead time, +5/-1 V gate commands, 1/0 ohm external on/off resistances, 20 uH load, 20 milliohm winding resistance and 0.81333 ohm external load. Ignoring dead time and losses, Imean = D*Vin/(Rout+Rload) = 45 A and inductor ripple is approximately Vin*D*(1-D)/(L*f) = 1.875 A peak-to-peak. Actual current is measured, not imposed by Itest; Itest and DPT pulse/energy settings do not set PWM current. Wpost still sets the switching-rate observation window.

The 20-cycle run uses an explicit 45 A inductor initial condition to study switching near the requested operating point without a long startup run. Set Iinitial=0 and increase Cycles for cold-start evaluation. The load time constant is about 24 us; a 40 us run is not a general steady-state qualification. Compare final cycles and extend the run when assessing slow capacitor/source settling. No conduction-loss estimates have been reintroduced.

## Capacitor branches and starting assumptions

| Branch | Effective C | ESR | ESL including connection | Location |
|---|---:|---:|---:|---|
| Bulk Cin | 470 uF | 20 milliohm | 10 nH | Upstream bus to supply return |
| Film Cfilm | 22 uF | 5 milliohm | 3 nH | Upstream bus to supply return |
| Ceramic Cdecap | 4.7 uF | 3 milliohm | 0.3 nH | Directly across rail and local bridge return |

These are equivalent bank assumptions, not selected or qualified manufacturer parts. Source resistance is 20 milliohm in this PWM preset, replacing the DPT charging/isolation resistor of 10 ohm. The model uses the existing distributed layout inductance; capacitor ESL is additional. The local ceramic branch bypasses the upstream feed/return path for fast commutation. With the current 50/50 split and zero midpoint allocation, its local loop contains ceramic ESL and both shared-source inductances; add realistic midpoint inductance if the actual PCB requires it.

## How to choose capacitor values

1. Set allowable DC-link ripple and separate the slower switching-frequency ripple from nanosecond edge spikes. For approximately constant load current, a stiff source providing average current, and continuous conduction:

   C >= I*D*(1-D)/(f*DeltaV)

   At 45 A, D=0.5 and f=500 kHz, a 1 V capacitive ripple budget requires about 22.5 uF effective capacitance. A conservative bound assuming the capacitor alone supplies the full high-side pulse is C >= I*D/(f*DeltaV) = 45 uF. Which bound is appropriate depends on source impedance and current sharing. The 22 uF film plus 4.7 uF ceramic is a starting point; bulk contributes only according to its frequency-dependent branch impedance.

2. Check capacitor ripple current and heating, not just capacitance. The simplified combined input-capacitor RMS current is I*sqrt(D*(1-D)) = 22.5 A. This is not the rating required of each branch separately. Their ESR/ESL determines sharing; use the simulated RMS values and the manufacturer's frequency/temperature curves. Estimate branch heating as Irms^2*ESR only where ESR can be treated as constant; sum harmonic losses for a frequency-dependent model. RMS currents from parallel branches cannot simply be added because they have different waveforms/phases.

3. Size local ceramic charge support using C >= I*DeltaT/DeltaV. At 45 A for 10 ns with 1 V allowed droop, the charge-only minimum is 0.45 uF. This does not constrain inductive spikes: ESL*di/dt remains even with large C. Use short, wide paths and closely spaced power/return layers. Use EFFECTIVE capacitance at 75 V including bias, tolerance, temperature and aging; do not enter nominal MLCC capacitance without derating.

4. Choose voltage ratings above the maximum local voltage including transients, with the manufacturer's required derating. Check film pulse-current/dv/dt capability, ripple current, thermal rise and life at operating temperature. Select actual part numbers only after checking their impedance and current-rating curves. A 100 V nominal bus capacitor is not automatically adequate just because the supply is 75 V.

5. Inspect resonance/antiresonance between bulk, film and ceramic branches. More capacitance does not guarantee lower edge peaks. Update ESR/ESL with manufacturer models or extracted connection impedance and verify both device Vds, gate extrema, local bus ripple, and individual capacitor currents.

## Measurements and interpretation

Results report full-run Vds/Vgs extrema, local bus extrema, and capacitor RMS currents, load average/min/max and bus peak-to-peak ripple over the final two cycles. The bus peak-to-peak measurement includes high-frequency spikes; it is not the charge-ripple estimate in the sizing formula. PWM rates are signed 10-90% transitions in the penultimate cycle. Soft switching or reverse conduction before a gate command can produce no complete post-command transition; this is not a zero slope. DPT energy formulas are not used to estimate PWM switching losses.

Initial 200 ps-step results: average current 43.8203 A, lower/upper Vds peaks 92.0432/82.8739 V; bulk/film/ceramic RMS currents 3.36683/15.4249/10.1555 A. Local bus ripple including edge spikes is 20.9954 Vpp. This is much larger than the 1 V charge-ripple sizing example and must not be presented as a 1 V-ripple-qualified design. At the assumed resistances, film and ceramic ESR heating estimates are about 1.19 W and 0.31 W respectively. Simulation does not establish physical capacitor current capability or device survival.

Validation artifacts are in half_bridge_validation; a 100 ps repeat is in its fine subfolder. Original DPT presets remain available and the vendor model is unchanged.

## Sources

- TI, Selecting capacitors to minimize ripple: https://www.ti.com/document-viewer/lit/html/SSZTAL7/GUID-3EDE487C-5BCB-45E3-8940-52FAA90331EA
- TI, Multiphase Buck Design from Start to Finish, Part 1 (DC bias derating and capacitor ripple-current checks): https://www.ti.com/lit/an/slva882b/slva882b.pdf
- TDK, DC-link capacitor selection (electrical, thermal and ripple-current requirements): https://www.tdk-electronics.tdk.com/en/2804170/products/product-catalog/dc-link-capacitors

Numerical bank values and allocations above are engineering starting assumptions, not quoted component specifications from these sources.

100 ps repeat: mean current 43.8205 A, lower/upper Vds peaks 92.524/83.0886 V, local bus ripple 21.2379 Vpp. Peak shifts from 200 ps were 0.481/0.215 V; this is a limited timestep sensitivity check, not exhaustive convergence.

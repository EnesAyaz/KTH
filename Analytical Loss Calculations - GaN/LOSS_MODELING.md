# EPC2361 loss model: revised single-device half bridge

## Operating point and scope

75 V bus; 40 A **AC RMS**; 100 kHz PWM; one FET per position (two total); sinusoidal current; modulation index 1.0; power factor 1. These retain the existing topology and control assumptions. RMS/instantaneous current must not be interchanged. The model assumes one hard turn-on/off pair per PWM period across the half bridge, with the opposite device naturally commutating. It is not a DC buck model or a model of two independently hard-switched devices.

External gate resistors remain 1 ohm on/off, driver resistances 0.5 ohm, current limits 2 A, effective and commanded dead time 50 ns, loop inductance 2 nH, case temperature 50 C, ambient 25 C and iterative RDS temperature feedback. Manual mode retains a 1.7 multiplier. The two GUIs now share these defaults. Previously the plotter had different driver defaults and silently replaced entered values.

## Datasheet inputs and provenance

Source: supplied `Datasheet/EPC2361_datasheet.pdf`, revision July 20, 2026.

| Parameter | Implemented value | Basis |
|---|---:|---|
| RDS(on), typical / maximum | 0.75 / 1 mOhm | p1, 5 V gate / 50 A |
| Gate drive / threshold | 5 / 1.1 V | p1; threshold typical |
| Internal gate resistance | 0.4 ohm | p2 |
| Charge to threshold | 6 nC | p2 QG(th) |
| Current-transition charge QGS2 | 2.5 nC | QGS 8.5 minus QG(th) 6; AN030 Eq3 |
| Miller plateau | about 2.1 V | p3 Fig7 at 50 V / 50 A |
| QGD at 75 V | about 4.0 nC | 3.8 nC at 50 V plus integral of CRSS, 50 to 75 V, Fig5b |
| QG at 75 V | about 28.2 nC | 28 nC table value plus estimated 0.2 nC QGD increment |
| QOSS at 75 V | about 114 nC | p3 Fig6, approximate graphical reading |
| EOSS at 75 V | about 3.2 uJ | p3 Fig6, reference only |
| COSS at 75 V | about 0.9 nF | p3 Fig5a; optional ringing only |
| Reverse drop | about 2.2 V | p3 Fig8, representative 40-57 A value |
| RthetaJC / RthetaJA | 0.2 / 44 C/W | p1; JA is JEDEC board, EVB is 25 |

Curve-derived numbers are nominal estimates, not guaranteed limits or exact 75 V switching data. Plateau and QGS2 are held fixed around the 50 A characterization point. Iterative mode interpolates the normalized RDS curve from Figure 9 at the calculated junction temperature. Manual mode retains the optional fixed multiplier 1.7. VSD depends on current and temperature; the previous 1.6 V was specified at only 0.5 A. The old 12 nC QGS2 was not supported by this datasheet.

When changing bus voltage, enter QOSS and EOSS for that voltage and update `qoss_voltage` to match. QGD/QG, plateau and reverse drop should also be reviewed for the new operating point. A mismatched QOSS reference voltage is rejected rather than extrapolated as a constant capacitance. EOSS is not used to compute losses and no QOSS/V energy equivalence is assumed.

## Equations

Let Ipk = sqrt(2) * Irms * waveform_factor and Iavg_abs = 2 Ipk / pi. The waveform factor scales the sinusoidal amplitude; it does not model arbitrary harmonic content.

With d_dead = 2 * effective_dead_time * fsw:

- Channel conduction: `Irms^2 * waveform_factor^2 * RDS(T) * (1-d_dead)` across both devices. Subtracting the small dead-time fraction avoids also assigning normal channel loss to the reverse-conduction intervals.
- Optional external loop resistance: `Irms^2 * waveform_factor^2 * Rloop`.
- Total gate resistance in each direction: external resistor + driver resistance + internal 0.4 ohm.
- Current-rise gate current: `min((Vdrive-(Vth+Vpl)/2)/Ron, driver_source_limit)`.
- Voltage-fall gate current: `min((Vdrive-Vpl)/Ron, driver_source_limit)`.
- Current-fall gate current: `min(((Vth+Vpl)/2)/Roff, driver_sink_limit)`.
- Voltage-rise gate current: `min(Vpl/Roff, driver_sink_limit)`; off gate drive is 0 V.
- `tCR=QGS2/Igate_CR`, `tVF=QGD/Igate_VF`, `tVR=QGD/Igate_VR`, `tCF=QGS2/Igate_CF`.
- Instantaneous-event overlap: `Eon=Vbus*Ievent*(tCR+tVF)/2`; `Eoff=Vbus*Ievent*(tVR+tCF)/2`.
- Line-cycle average overlap: `Poverlap=Vbus*Iavg_abs*(tCR+tVF+tVR+tCF)*fsw/2`. Peak event energies are not applied at every switching cycle.
- Symmetric half-bridge output-capacitor loss: **`Pcoss=Vbus*Qoss(Vbus)*fsw`**, AN030 p6 Eqs17-18. This includes both capacitors; do not add `2*Eoss*fsw` again.
- Two-gate supply power: `Pgate=2*Qg*Vdrive*fsw`.
- Reverse conduction: `Pdead=VSD*Iavg_abs*d_dead`.
- Total: conduction + overlap + capacitor + gate + dead-time + external loop loss.
- Output power: `Pout=m*Vbus/(2*sqrt(2))*Irms*power_factor` (retained sinusoidal half-bridge convention; waveform_factor affects loss-current estimates only).
- Efficiency: `100*Pout/(Pout+Ptotal)`.

Threshold and post-plateau gate durations use segment-average gate voltage and the driver current limit; these are illustrative piecewise approximations to nonlinear charging. Charge segments must sum to no more than QG. `qgs1_nc` is retained as a legacy fallback for threshold charge when `qgsth_nc=0`; it is not total QGS.

GaN QRR is zero. No silicon reverse-recovery term is added. The shaded waveform is channel overlap; capacitor displacement current is not inserted into that waveform and counted a second time.

## Iterative junction temperature and on-resistance

Default `rds_temperature_mode="iterative"` solves the coupled steady-state conduction/thermal problem. Approximate Figure 9 readings are normalized factors 0.84, 1.00, 1.16, 1.33, 1.49, 1.65, 1.80 at 0, 25, 50, 75, 100, 125, 150 C. Piecewise-linear interpolation scales the selected 25 C typical/maximum resistance. These are approximate typical curve readings, not guaranteed hot-resistance specifications.

Starting at the selected case/ambient temperature, each iteration updates RDS(T), conduction loss and semiconductor loss, then evaluates `Tnext = Tref + Rtheta * Psemiconductor(T)/2`. It stops when the thermal residual is below 1e-6 C, with at most 200 iterations. The code raises an explicit error on nonconvergence or temperatures outside the curve's 0..150 C range; it does not clamp or extrapolate into an invalid steady-state result.

The outputs include `junction_temperature`, `rds_on_mohm`, `rds_on_ohm`, `rds_temperature_factor`, `thermal_iterations` and `thermal_residual_c`. With the default maintained case temperature of 50 C: Tj is 50.4922 C, RDS(on) is 1.16335 mOhm, conduction loss is 1.84274 W, and total loss is 4.95047 W. The solution estimates steady-state temperature under the supplied cooling assumptions, not measured real junction temperature. Other loss terms remain fixed during this iteration.

Set `rds_temperature_mode="manual"` to recover the fixed `rds_temp_scale` approach. That multiplier is ignored in iterative mode. The GUI displays the temperature and updated resistance prominently.

## Stress, thermal, and limitations

`Lloop*Ievent/tCR` and `Lloop*Ievent/tCF` are crude overshoot indicators. Stress uses bus voltage plus the larger estimate. With retained 2 nH and the corrected fast current transitions, this exceeds the 100 V rating; the result includes `voltage_rating_exceeded`. Actual commutation depends on parasitic feedback, nonlinear capacitance and gate/source inductances, which this gate-charge model does not solve.

Semiconductor loss excludes external loop-resistor and gate-supply power. It is split equally between the FETs for symmetric sinusoidal averaging, then multiplied by RthetaJC or RthetaJA and added to the selected reference temperature. This neglects the small internal-gate-resistance share of gate-drive power. The default fixed case temperature presumes cooling that maintains that temperature; this is not a cooling-system prediction.

Effective dead time means the actual interval of reverse conduction used for the estimate. Commanded dead time is retained separately; effective timing can exceed the commanded value. The model does not solve output-capacitor self-commutation or duty-dependent dead-time distortion; treating the whole selected interval as reverse conduction is conservative.

`hard_switching=False` suppresses both overlap and output-capacitor dissipation as an ideal fully soft-switched limit. It does not establish ZVS or model residual soft-switching loss. Optional damped LC ringing is illustrative only; it is not included in the loss integral used by the calculator.

## Validation

`python -m unittest -v test_loss_model.py` checks analytical conduction/capacitance accounting, efficiency, waveform power integrals, endpoints, sinusoidal averaging, external thermal-loss separation, optional event current, invalid inputs, zero-charge/zero-inductance edges, and GUI input preservation. The exported PNG is visually inspected. The TeX/PDF report includes the iterative solution, current waveform graphic, and revised default results, without a table of contents or paralleling section.

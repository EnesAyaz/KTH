# H10 confirmation (independent, nonlinear MEC + DC cells)

Date 2026-11-02. Simulator. Inputs: `data/machine_geometry.json` (agreed geometry, R01), IM at 2100 rpm, flat road (248 Nm) and 2 % grade (677 Nm). Overlapped, sequential and ideal cases use the T03 350 kW current limit (310 A rms per leg, as T04); the H11s runs are also given at 300 kW (266 A) to match the analyst's H11 file. Files: `run_h10_mec.py` (MEC replay, ideal crossfade, sequential, H11s), `run_h10_balance.py`, `run_h10_sched.py`, `run_h10.py` (first, linear version); results `results/confirm_H10_mec_Q48.json`, `confirm_H10_mec_Q80.json`, `confirm_H10_balance_Q48.json`, `confirm_H10_balance_Q80.json`, `h10_schedule_search_Q*.json`, `confirm_H10_handover_*.json`.

## Method (own equations)

* **Machine and handover**: the two-mode IM model of T04 (orders p = 4 and p = 2 of the same coils, rotor-flux-oriented control, shared voltage and current budget). A controller error found during this work (demagnetising d current blocked at zero flux reference) is fixed; the T04 transition numbers are corrected in `validation.md`.
* **Nonlinear MEC replay**: the magnetising current of each mode (i_s + referred rotor current) is rebuilt into per-coil currents at 0.4 ms steps and passed through the MEC with the B-H iron (`spb_core.mec_solve`, smooth rotor). Coil voltage = R i + L_sigma di/dt + d psi_k/dt with the MEC flux linkages, so cross saturation between the two orders and every combination order is included. The cage reaction to saturation-generated orders is not modelled, so combination-order pulsations are an upper bound.
* **Cell power**: P_j(t) = sum over the coils of module j of v_k i_k (m = 3 coils per module, Q = 48; m = 5 coils, Q = 80, y = 11, same per-unit machine, 16 modules in both). The pulsation is read from P_j minus the mean over the 16 cells (removes the common mean power), by sliding demodulation at multiples of 70 Hz (window 1/70 s).
* **DC cells**: 16 series cells on a stiff 1200 V link: C dv_j/dt = (P_mean - P_j)/V_0, V_0 = 75 V. A constant-power cell on a fixed stack current is open-loop unstable (C V^2/P about 1.6 ms at 1 mF), so the reported ripple is the linearised open-loop value and the drift is the uncontrolled integral of the imbalance; the real system needs the cell-voltage balancing loop of item 4 for the slow part. Ripple amplitude is also given as A/(V_0 w C).
* **Spatial condition** (derived here): the product of order a and order b over the m coils of a module gives m/2 Re[V I e^(-j(a +- b) alpha_j)] if (a +- b) is a multiple of m and 0 otherwise. For m = 3 any two orders that are not multiples of 3 satisfy a = +-b (mod 3), so the condition always holds; for prime m >= 5 it holds only if a = +-b (mod m). The pair (4, 2) gives a + b = 6 (multiple of 3, pulsation at f_4 + f_2 = 210 Hz at 2100 rpm) and 4 +- 2 = 6, 2 (not multiples of 5).

## Verdict

* **Confirmed (m = 3).** The overlapped IM handover pulsates at 210 Hz with 9.2 kW per cell on flat road and 7.9 kW on the 2 % grade (analyst: 8464 W), 2.7x the cell mean power. Capacitance for +-5 % ripple: 25 mF (analyst 22.8 mF), for +-10 %: 12 mF. The 1.0 and 2.88 mF cells would see 93 V and 32 V amplitude on a 75 V cell. The nonlinear MEC changes the pulsation by less than 3 % relative to the linear model (iron saturation is moderate at 2100 rpm).
* **Confirmed, with a correction (m = 5).** On the 80-coil stator the product terms vanish and what is left is the saturation residual: 7 W (flat) and 39 W (2 %), i.e. 0.1 % and 0.5 % of the m = 3 value, at 350 Hz. It needs about 0.1 mF. **But the torque is not kept at 90 %: the best of 64 overlapped schedules on the m = 5 stator keeps 0.84 of the request on flat road and -0.15 on the 2 % grade** (m = 3: 0.79 and -0.11). The dip comes from the shared voltage budget (the residual 8-pole EMF), not from the cells, so m = 5 removes the pulsation but not the torque dip.
* **Sequential m = 3 (addition 3).** Sequential m = 3 costs a torque gap but needs little capacitance: flat road 0.13-0.18 s, 2 % grade 0.30-0.32 s depending on the trigger level, with no torque reversal on flat road (min -2 Nm) and a small one on the grade (-26 Nm). The residual V8 x I4 term (EMF of the left-over 8-pole flux against the 4-pole current) is 345 W when the 4-pole flux is built after the 8-pole flux has fallen below 2 %, 866 W at 5 %, 2502 W at 15 % and 5030 W at 30 % (about proportional to the residual flux). At 1.0 mF the cell ripple is 3.4 V pk at 2 % and 25 V pk at 15 %, so the trigger must be 5 % or lower for 1-3 mF cells.
* **H11s in the nonlinear MEC with DC cells.** 350 kW (310 A), 1 ms loop: gap 0.156 s flat / 0.302 s on the 2 % grade, minimum torque -73 / -103 Nm, peak cell ripple 6.1 % / 6.8 % at 1.0 mF and 2.1 % / 2.4 % at 2.88 mF, peak current 313 A rms; 300 kW (266 A), 1 ms loop: gap 0.174 s flat / 0.362 s on the 2 % grade, minimum torque -81 / -104 Nm, peak cell ripple 5.2 % / 6.2 % at 1.0 mF and 1.8 % / 2.2 % at 2.88 mF, peak current 268 A rms; 300 kW (266 A), 0.25 ms loop: gap 0.178 s flat / 0.372 s on the 2 % grade, minimum torque -2 / -103 Nm, peak cell ripple 5.4 % / 5.6 % at 1.0 mF and 1.9 % / 1.9 % at 2.88 mF, peak current 266 A rms. Analyst's linear model: 0.143 s flat, 0.181 s on the grade, no reversal, ripple at most 5.8 %.

## 1. Overlapped handover, pulsation and cell voltage

| case | mean cell power (W) | peak per-cell pulsation, MEC (linear) (W) | at (Hz) | pulsation / mean | C for +-5 % / +-10 % ripple (mF) | ripple amplitude at 1.0 / 2.88 mF (V pk) | cell voltage range 1.0 / 2.88 mF (V) | min torque / request | time below 90 % (s) |
|---|---|---|---|---|---|---|---|---|---|
| m = 3 overlapped, flat road | 3439 | 9244 (9292) | 210 | 2.69 | 24.9 / 12.5 | 93 / 32 | -25..175 / 40..110 | 0.79 | 0.34 |
| m = 3 overlapped, 2 % grade | 5797 | 7885 (8063) | 210 | 1.36 | 21.2 / 10.6 | 80 / 28 | -67..217 / 26..124 | -0.10 | 0.60 |
| m = 5 overlapped, flat road | 3511 | 7 (0) | 350 | 0.00 | 0.0 / 0.0 | 0 / 0 | 75..75 / 75..75 | 0.84 | 0.18 |
| m = 5 overlapped, 2 % grade | 6279 | 39 (0) | 350 | 0.01 | 0.1 / 0.0 | 0 / 0 | 75..75 / 75..75 | -0.14 | 0.58 |
| m = 3 ideal crossfade, psi and i linear in x | 2761 | 2027 (1993) | 211 | 0.73 | 5.4 / 2.7 | 20 / 7 | 55..95 / 68..82 | - | - |
| m = 5 ideal crossfade, psi and i linear in x | 2760 | 3 (0) | 350 | 0.00 | 0.0 / 0.0 | 0 / 0 | 75..75 / 75..75 | - | - |
| m = 3 ideal crossfade, torque-conserving (sqrt) | 3429 | 3990 (3987) | 211 | 1.16 | 10.7 / 5.3 | 40 / 14 | 34..116 / 61..89 | - | - |
| m = 5 ideal crossfade, torque-conserving (sqrt) | 3430 | 15 (0) | 350 | 0.00 | 0.0 / 0.0 | 0 / 0 | 75..75 / 75..75 | - | - |

Ripple amplitude is A/(V_0 w C) with the main pulsation line; the cell-voltage range is the open-loop linearised cell voltage over the whole handover including the uncontrolled integral of the imbalance. Ranges outside about 20-80 V are not admissible for a 75 V cell.

## 2. True crossfade envelope (addition 1)

For the m = 3 sum-frequency term the exact kernel is A(t) = 1.5 |V_4 I_2 + V_2 I_4| (checked: measured / kernel = 0.96 flat, 0.76 2 %, ideal laws 1.01 / 1.02). The x(1-x) law holds only when both flux linkage and current of each mode scale linearly with the crossfade variable:

| case | x defined as | kappa/4 = peak of kappa x(1-x) (W) | R^2 | measured peak (W) | x at peak |
|---|---|---|---|---|---|
| m = 3 ideal_linear_amplitude | share | 2020 | 1.00 | 2027 | 0.50 |
| m = 3 ideal_constant_torque | share | 4388 | 0.59 | 3990 | 0.48 |
| m = 3 overlapped_0pct | torque | 9253 | 0.64 | 9244 | 0.43 |
| m = 3 overlapped_0pct | flux | 11381 | -0.89 | 9244 | 0.67 |
| m = 3 overlapped_0pct | current | 6805 | 0.77 | 9244 | 0.44 |
| m = 3 overlapped_2pct | torque | 6218 | -1.13 | 7885 | 0.56 |
| m = 3 overlapped_2pct | flux | 4224 | -1.78 | 7885 | 0.08 |
| m = 3 overlapped_2pct | current | 3503 | -0.16 | 7885 | 0.95 |

* Ideal linear crossfade (psi and i linear in x): R^2 = 1.00, peak 2027 W at x = 0.50, C 5.4 mF for +-5 %, 2.7 mF for +-10 %. This is the lower bound.
* If the torque is to stay constant during the crossfade (amplitudes scale as sqrt(x), sqrt(1-x)) the product is sqrt(x(1-x)) and the peak doubles: 3990 W, C 10.7 / 5.3 mF.
* The real handover is not a clean crossfade: both modes are driven near the voltage and current limit while the 8-pole EMF is still present, so the envelope peaks at 9244 W (flat) and 7885 W (2 %), 2-4x the ideal values, and x(1-x) is a poor predictor (R^2 0.64 with the torque share).

## 3. m = 5: saturation residual (addition 2)

| case | MEC pulsation (W) | at (Hz) | lines (W) at 70 / 140 / 210 / 280 / 350 / 420 Hz | peak flux-derivative amplitude per order (V per coil) |
|---|---|---|---|---|
| m = 5 overlapped_0pct | 7 | 350 | 1 / 1 / 1 / 2 / 7 / 5 | p=4: 30.09, p=2: 25.01, p=6: 0.32, p=12: 0.02, p=8: 0.00 |
| m = 5 overlapped_2pct | 39 | 350 | 3 / 4 / 6 / 9 / 39 / 14 | p=4: 35.51, p=2: 25.50, p=6: 0.41, p=12: 0.09, p=8: 0.09 |
| m = 5 ideal_linear_amplitude | 3 | 350 | 0 / 0 / 0 / 0 / 3 / 0 | p=4: 30.00, p=2: 24.97, p=6: 0.32, p=8: 0.02, p=12: 0.02 |
| m = 5 ideal_constant_torque | 15 | 350 | 1 / 1 / 1 / 2 / 15 / 3 | p=4: 30.00, p=2: 24.97, p=6: 0.32, p=8: 0.09, p=12: 0.08 |
| (m = 3 overlapped flat, for scale) | 9244 | 210 | 1624 / 2254 / 9244 / 4227 / 1792 / 1209 | p=4: 29.83, p=2: 26.33, p=10: 0.21, p=8: 0.01, p=11: 0.00 |

The residual that is left for m = 5 is generated by the shared iron (order 6 = 4 + 2 flux derivative peaks at 0.32 V per coil, 1.1 % of the order-4 term; order 6 against the order-4 current gives 6 + 4 = 10, a multiple of 5, at 210 + 140 = 350 Hz, which is the line seen): the MEC flux-derivative contains orders that are combinations of 4 and 2 (6, 8, ...), and some of their products with the 4 and 2 currents are multiples of 5 (for example order 6 against order 4 at the sum frequency). Size: 7-39 W at 350 Hz for the handovers, 15 W for the ideal torque-conserving crossfade, to be compared with 7-9 kW for m = 3. With cell voltage amplitude 0.2 V at 1.0 mF, this is negligible. It is an upper bound because the cage would damp the combination orders. The 8/4 pair is not a special case here: with the iron shared, combination orders appear for any pair, but their amplitude is the saturation level (B_tooth peak 0.77 T), so a stator driven deeper into saturation (for example at the 2p = 8 flux cap at low speed) should be checked separately.

## 4. Sequential handover, m = 3 (addition 3)

Mode 2 is started only when the residual 8-pole rotor flux has fallen below the trigger level, the 8-pole current is then set to zero. The only cross product left is v_p4 (EMF of the residual 8-pole flux) x i_p2:

| grade | trigger: psi_r8 below | trigger time (s) | time below 90 % (s) | min torque (Nm) | peak pulsation MEC (W) | v_p4 x i_p2 term (W) | C for +-5 % / +-10 % (mF) | ripple pp at 1.0 / 2.88 mF (V) | I_rms peak / I_max |
|---|---|---|---|---|---|---|---|---|---|
| 0 % | 2 % | 0.099 | 0.158 | -2 | 345 | 345 | 0.9 / 0.5 | 6.8 / 2.4 | 1.01 |
| 0 % | 5 % | 0.085 | 0.142 | -2 | 866 | 866 | 2.3 / 1.2 | 17.1 / 5.9 | 1.01 |
| 0 % | 15 % | 0.068 | 0.126 | -1 | 2502 | 2502 | 6.7 / 3.4 | 49.4 / 17.1 | 1.01 |
| 0 % | 30 % | 0.058 | 0.176 | -3 | 5030 | 5031 | 13.6 / 6.8 | 99.0 / 34.4 | 1.01 |
| 2 % | 2 % | 0.126 | 0.318 | -26 | 362 | 362 | 1.0 / 0.5 | 7.1 / 2.5 | 1.01 |
| 2 % | 5 % | 0.11 | 0.302 | -26 | 882 | 882 | 2.4 / 1.2 | 20.0 / 7.0 | 1.01 |
| 2 % | 15 % | 0.094 | 0.298 | -26 | 2618 | 2618 | 7.1 / 3.5 | 51.5 / 17.9 | 1.01 |
| 2 % | 30 % | 0.084 | 0.310 | -26 | 5319 | 5319 | 14.3 / 7.2 | 104.6 / 36.3 | 1.01 |

## 5. H11s in the nonlinear MEC with DC cells

Schedule (analyst's H11s, my controller): ramp the 8-pole torque current to 0 in 20 ms; demagnetise with i_d8 = -0.9 I_pk until psi_r8 < 2 %; build the 4-pole flux with the d current up to the budget, the 4-pole current limited online so that 1.5(|V_8||I_4| + |V_4||I_8|) <= P_allow = 0.10 V_0 w_sum C (2137 W at 2.88 mF, 742 W at 1.0 mF); torque current once psi_4 > 5 %.

| limits / current loop | case | C (mF) | time below 90 % (s) | below 95 % until (s) | min torque (Nm) | reversal | peak cell ripple at C (V pk, % of 75 V) | peak pulsation (W) | peak I_rms (A) | analyst linear model: gap / ripple |
|---|---|---|---|---|---|---|---|---|---|---|
| 350 kW (310 A), 1 ms loop | 0 % grade | 1.00 | 0.156 | 0.222 | -73 (-0.30) | yes | 4.5 (6.1 %) | 354 | 313 | 0.143 s / 5.7 % |
| 350 kW (310 A), 1 ms loop | 0 % grade | 2.88 | 0.156 | 0.222 | -73 (-0.30) | yes | 1.6 (2.1 %) | 354 | 313 | 0.143 s / 5.7 % |
| 350 kW (310 A), 1 ms loop | 2 % grade | 1.00 | 0.302 | 0.308 | -103 (-0.15) | yes | 5.1 (6.8 %) | 380 | 313 | 0.181 s / 5.7 % |
| 350 kW (310 A), 1 ms loop | 2 % grade | 2.88 | 0.302 | 0.308 | -103 (-0.15) | yes | 1.8 (2.4 %) | 380 | 313 | 0.181 s / 5.7 % |
| 300 kW (266 A), 1 ms loop | 0 % grade | 1.00 | 0.174 | 0.244 | -81 (-0.33) | yes | 3.9 (5.2 %) | 301 | 268 | 0.143 s / 5.7 % |
| 300 kW (266 A), 1 ms loop | 0 % grade | 2.88 | 0.174 | 0.244 | -81 (-0.33) | yes | 1.4 (1.8 %) | 301 | 268 | 0.143 s / 5.7 % |
| 300 kW (266 A), 1 ms loop | 2 % grade | 1.00 | 0.362 | 0.366 | -104 (-0.15) | yes | 4.7 (6.2 %) | 320 | 267 | 0.181 s / 5.7 % |
| 300 kW (266 A), 1 ms loop | 2 % grade | 2.88 | 0.362 | 0.366 | -104 (-0.15) | yes | 1.6 (2.2 %) | 320 | 267 | 0.181 s / 5.7 % |
| 300 kW (266 A), 0.25 ms loop | 0 % grade | 1.00 | 0.178 | 0.190 | -2 (-0.01) | no | 4.1 (5.4 %) | 285 | 266 | 0.143 s / 5.7 % |
| 300 kW (266 A), 0.25 ms loop | 0 % grade | 2.88 | 0.178 | 0.190 | -2 (-0.01) | no | 1.4 (1.9 %) | 285 | 266 | 0.143 s / 5.7 % |
| 300 kW (266 A), 0.25 ms loop | 2 % grade | 1.00 | 0.372 | 0.376 | -103 (-0.15) | yes | 4.2 (5.6 %) | 309 | 266 | 0.181 s / 5.7 % |
| 300 kW (266 A), 0.25 ms loop | 2 % grade | 2.88 | 0.372 | 0.376 | -103 (-0.15) | yes | 1.5 (1.9 %) | 309 | 266 | 0.181 s / 5.7 % |

## 6. Balancing knob (item 4 of the first request)

IM 2p = 4 at cruise (4250 rpm, 352 Nm, a = 2): V = 29.1 V, I = 124 A rms, mean cell power 9963 W. A current of order b at the same electrical frequency exchanges average power between cells only if (a - b) is a multiple of m; it sums to zero over the cells (power is moved, not created). m = 3, Q = 48 (current per coil):

| b | (a - b) mod m | W per A rms | % of cell power per A | I_b for 5 % (A rms) | share of I_a | rotor Cu (W) | stator Cu (W) | V_b (V rms) | torque (Nm) |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | 81.9 | 0.82 | 6.1 | 4.9 % | 1.9 | 3.8 | 0.37 | -0.007 |
| -1 | 0 | 84.6 | 0.85 | 5.9 | 4.8 % | 1.7 | 3.6 | 0.18 | -0.001 |
| 8 | 0 | 84.3 | 0.85 | 5.9 | 4.8 % | 0.6 | 3.6 | 0.18 | -0.002 |
| -4 | 0 | 81.7 | 0.82 | 6.1 | 4.9 % | 3.3 | 3.8 | 0.58 | -0.005 |
| 4 | 1 | 0 | 0 | - | - | - | - | - | - |
| 1 | 1 | 0 | 0 | - | - | - | - | - | - |

m = 5, Q = 80 (coil current scaled by 48/80, so W/A is higher but the relative effect is the same):

| b | (a - b) mod m | W per A rms | % of cell power per A | I_b for 5 % (A rms) | share of I_a | rotor Cu (W) | stator Cu (W) | V_b (V rms) | torque (Nm) |
|---|---|---|---|---|---|---|---|---|---|
| 7 | 0 | 145.3 | 1.46 | 3.4 | 4.7 % | 0.0 | 3.3 | 0.04 | -0.000 |
| -3 | 0 | 139.4 | 1.40 | 3.6 | 4.9 % | 3.5 | 3.6 | 0.49 | -0.005 |
| 4 | 3 | 0 | 0 | - | - | - | - | - | - |
| 1 | 1 | 0 | 0 | - | - | - | - | - | - |
| 3 | 4 | 0 | 0 | - | - | - | - | - | - |

**About 82-85 W per A rms per cell (0.82-0.85 % of cell power per A) for m = 3**, so 5 % costs 5.9-6.1 A rms (about 5 % of the fundamental current), 5-7 W of copper, under 0.6 V of extra voltage and under 0.01 Nm of torque, which matches the analyst's "about 1 A per 1 %". Orders with (a - b) not a multiple of m move no power.

## Caveats

* The MEC replay uses a smooth rotor and the B-H table of the agreed geometry; no rotor slotting, no cage reaction to the saturation-generated orders.
* Cell voltage is the open-loop linearised value; the real cell-balancing loop removes the slow drift but not the 70-350 Hz ripple.
* The m = 5 machine is the same per-unit machine on 80 slots (y = 11, 5.4 mm slots, coil current x 48/80, same V limit); a 5-leg bridge has a different linear voltage range, not modelled.
* Schedules are the best of a 64-point grid per case (t_d, t_f4, t_f2); a better controller may improve the torque dip but cannot beat the voltage budget.

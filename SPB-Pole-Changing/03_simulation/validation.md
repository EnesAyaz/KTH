# T04 validation: independent simulation vs analyst (T03, 350 kW file)

Date 2026-10-29. Simulator: `03_simulation/`. Analyst file checked: `02_analytics/results/torque_speed_envelope.json` (350 kW; the 300 kW rerun is not validated here).

## FLAGS (read first)

* **59 of 136 compared numbers differ by more than 5 %** (all rows in the appendix). The disagreement is not random. It has three identifiable causes:
  1. **Stator slot leakage.** The analyst assumes permeance coefficients lambda_self = 1.2 and lambda_mut = 0.4. I computed them from the field energy of the two stacked coil layers in the 9 x 45 mm slot, with 3 mm of wedge/insulation. I get 2.3x the analyst's slot leakage at 2p=8 (L_slot 29.1 uH vs 12.6 uH) and 2.0x at 2p=4 (21.7 vs 10.6 uH). Total stator leakage is 52 uH vs 37 uH (2p=8) and 38 uH vs 28 uH (2p=4). This alone explains the -12 to -20 % in the voltage-limited IM torque at 3000-6000 rpm (attribution table below: with the analyst's leakage in my model the difference drops to -1 to -6 %). **The IM and WRSM high-speed envelopes are therefore not confirmed within 5 %. A reconcile task is needed on the slot leakage; an FEA slot model or the real slot drawing would settle it.** I did not tune either side.
  2. **WRSM synchronous reactances.** The analyst uses typical saturated per-unit values (L_d = 1.10, L_q = 0.65 pu) for a WRSM. A WRSM built in this stator with the IM air gap (g_eff 1.3 mm) has L_d about 4x larger (unsaturated, 4.9 pu of magnetising reactance) and cannot even make the analyst's base-speed torque (config A below: 1062 Nm vs 2932 Nm at 500 rpm, voltage-limited). To compare at all, I used **config B: the WRSM air gap x4 (g_eff 5.2 mm, field MMF x4 so that the no-load B0 is unchanged)**. This reproduces the analyst L_d to about 30 %. It is a stated modelling choice made for the comparison, not a tuned fit. It has a consequence: the field time constant is also x4 (see item 3 below), which the analyst's 45 ms does not include.
  3. **Flux limits.** The analyst caps the fundamental gap flux density at 0.88 T (2p=8) and 0.44 T (2p=4). I imposed the same limits on the peak tooth and yoke flux density of my MEC (primary table, 0.95 stacking factor, peak of a non-sinusoidal field). That gives a rotor-flux cap of 0.046 Wb (2p=8) and 0.038 Wb (2p=4) against the analyst's 0.0535 and 0.0439 Wb, which is why the flux-limited low-speed IM torque is 14 % (2p=8, 1000 rpm) and 19 % (2p=4, 2100 rpm) lower. With soft MEC saturation only and no imposed caps (second IM table) the 2p=4 torque at 2100 rpm is +8.6 % above the analyst and the 2p=8 torque at 1000 rpm is still -14.6 % (voltage-limited there).
* **The WRSM "no gain" result survives, but the size of the 2p=4 deficit does not.** Analyst: the 2p=4 torque is 0.45 of the 2p=8 torque at low speed and 0.43 at 4500 rpm. Simulation (config B): 0.43 at 1000 rpm and 0.72-0.78 from 2100 rpm to 9000 rpm. Neither model gets a crossover with the stator as specified. The cruise point is reachable by the 2p=4 WRSM in the simulation (418 Nm available vs 352 Nm needed), not in the analyst model (329 Nm). It is less efficient than 2p=8 at cruise either way (95.5 % vs 96.7 %).
* Agreement that does hold within 5 %: PMSM envelope torque up to 4500 rpm (-0.2 / -2.0 / -4.6 %; -7.4 % at 6000 rpm) and PMSM current, voltage and stator copper loss at all six efficiency points (this is a check of the solver and the loss bookkeeping, since the PMSM per-unit parameters are shared inputs); WRSM 2p=8 stator current, voltage and stator copper loss at the suburban, highway and cruise points (-2 to 0 %); IM stator current at launch/accel (+3.6 %) and highway/cruise (+2 %); cage resistance R_r (identical to 4 digits, 0.0020 / 0.0017 ohm), rotor leakage (3.60 vs 3.51 uH, 2.75 vs 2.69 uH), L_m (same winding-function formula, exact), winding factors, low-speed torque ratio 2p=4/2p=8 (sim 0.43 at 1000 rpm, analyst 0.45).
* Iron loss differs by up to 40-90 % (PMSM -32 to -48 % at high speed; WRSM +40 to +77 %). My iron loss uses tooth/yoke flux density from the MEC solution with a different two-parameter fit (P = c f^1.29 B^2, same two catalogue points), the analyst uses fundamental B from cap formulas. Iron loss is 0.3-1 % of the shaft power, so the efficiency differences stay within 1.7 points. Field loss in the WRSM differs by up to 2x because the loss-optimal I_f differs (sim picks 0.65-0.9, analyst 0.47-0.68 at highway/cruise).

## What the simulation is

`spb_core.py` (coil-level model, 48 coil-phases, 16 modules) is independent of the analyst's equations:

* Each coil has sides in slots k and k+7 (double-layer lap, N_c = 3). A nonlinear magnetic equivalent circuit (48 tooth branches with gap + B-H tooth iron, 48 yoke segments with B-H, slot ampere-turns as sources, Newton solve) gives the 48 tooth fluxes. Coil flux linkage = N_c x flux of the 7 enclosed teeth. The same circuit takes a smooth rotor (IM) or 8 salient poles with the coil-group MMF patterns of `Field Excitation/FE_MMF.m` (WRSM).
* Slot leakage from slot field energy (two layers, mutual term with sign from the coil-side phase difference), differential leakage from the winding-function harmonic sum nu = p + 48 j, cage resistance and leakage from the 58-bar loop model (R_loop(mu) = 4 R_bar sin^2(pi mu/58) + 2 R_seg).
* torque from the dq flux (checked against the virtual-work torque from the MEC: 12.73 vs 12.77 Nm at 2p=8 and 8.31 vs 8.59 Nm at 2p=4, linear region).
* Shared inputs read from the analyst file (not equations): V and I limits, stator dimensions, R_coil, g_eff = 1.3 mm, friction law, vehicle; rotor slot permeance coefficients (lambda_bar 1.5, lambda_ring 0.3, rotor slot geometry is not defined); end-winding leakage; PMSM per-unit values (psi_pm 0.70, L_d 0.65, L_q 1.30 pu) because there is no PMSM geometry.
* Additions the analyst does not have: stacking factor 0.95, soft saturation, 3 mm wedge, interpolar permeance (0.08 of the pole-face value) on the rotor.

Files: `spb_core.py`, `sync_model.py`, `wrsm_model.py`, `build_maps.py`, `run_validation.py`, `run_wrsm_study.py`, `run_im_transition.py`, `run_im_transition_opt.py`, `run_wrsm_transition.py`, `make_quicklooks.py`, `make_validation_md.py`. Results: `results/validation_points.json`, `wrsm_pole_change_study.json`, `im_pole_transition.json`, `wrsm_pole_transition.json`, `wrsm_pole_transition_ksweep.json`. Quick-looks: `scratch/*.png`.

## 1. Validation table (selected operating points; the full list is in the appendix)

| machine | point | quantity | analyst | simulation | error % |
|---|---|---|---|---|---|
| IM 2p8 | 1000 rpm, envelope | torque_Nm | 2948 | 2525 | -14.3 **>5 %** |
| IM 2p8 | 1000 rpm, envelope | V_rms_V (limit) | 29.09 | 23.99 | -17.5 **>5 %** |
| IM 2p8 | 1000 rpm, envelope | I_rms_A (limit) | 310.4 | 308.4 | -0.7 |
| IM 2p4 | 4500 rpm, envelope | torque_Nm | 704.6 | 617.2 | -12.4 **>5 %** |
| IM 2p4 | 4500 rpm, envelope | V_rms_V (limit) | 29.09 | 28.82 | -0.9 |
| IM 2p4 | 4500 rpm, envelope | I_rms_A (limit) | 310.4 | 309.4 | -0.3 |
| IM 2p4 | 2100 rpm, envelope | torque_Nm | 1263 | 1016 | -19.5 **>5 %** |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | I_rms_A | 211.9 | 219.4 | +3.6 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | V_rms_V | 24.71 | 24.91 | +0.8 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_cu_stator_W | 4644 | 5104 | +9.9 **>5 %** |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_fe_W | 947.9 | 976.1 | +3.0 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | eta_pct | 95.7 | 95.32 | -0.4 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_cu_rotor_W | 3700 | 4069 | +10.0 **>5 %** |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | I_rms_A | 119.7 | 122.6 | +2.5 |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | V_rms_V | 29.06 | 28.98 | -0.3 |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_stator_W | 1481 | 1667 | +12.5 **>5 %** |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_fe_W | 777.9 | 904.2 | +16.2 **>5 %** |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | eta_pct | 97.05 | 96.78 | -0.3 |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_rotor_W | 1146 | 1287 | +12.3 **>5 %** |
| PMSM 2p8 | 1000 rpm, envelope | torque_Nm | 3060 | 3055 | -0.2 |
| PMSM 2p8 | 1000 rpm, envelope | I_rms_A at max T | 310.4 | 310.2 | -0.1 |
| PMSM 2p8 | 4500 rpm, envelope | torque_Nm | 897.3 | 855.8 | -4.6 |
| PMSM 2p8 | 4500 rpm, envelope | I_rms_A at max T | 310.4 | 306 | -1.4 |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | I_rms_A | 215.1 | 217.8 | +1.2 |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | V_rms_V | 28.93 | 28.39 | -1.9 |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_stator_W | 4789 | 4908 | +2.5 |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_fe_W | 1116 | 578.5 | -48.1 **>5 %** |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | eta_pct | 95.56 | 95.8 | +0.3 |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | I_rms_A | 251.9 | 254.7 | +1.1 |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | V_rms_V | 28.7 | 28.2 | -1.7 |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | P_cu_stator_W | 6566 | 6710 | +2.2 |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | P_fe_W | 1049 | 539.9 | -48.5 **>5 %** |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | eta_pct | 96.86 | 96.98 | +0.1 |
| WRSM 2p8 | 1000 rpm, envelope (free I_d, I_f) | torque_Nm | 2932 | 2627 | -10.4 **>5 %** |
| WRSM 2p8 | 4250 rpm, envelope (free I_d, I_f) | torque_Nm | 756.6 | 554.3 | -26.7 **>5 %** |
| WRSM 2p8 | 4500 rpm, envelope (free I_d, I_f) | torque_Nm | 712.9 | 520.7 | -26.9 **>5 %** |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | I_rms_A | 119.8 | 118.6 | -1.0 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | V_rms_V | 29.08 | 28.53 | -1.9 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_stator_W | 1485 | 1455 | -2.0 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_fe_W | 482.9 | 773.8 | +60.3 **>5 %** |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | eta_pct | 97.39 | 96.74 | -0.7 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_field_W | 876.2 | 1690 | +92.9 **>5 %** |
| WRSM 2p4 | 4250 rpm, envelope (free I_d, I_f) | torque_Nm | 329.5 | 418.5 | +27.0 **>5 %** |
| WRSM 2p4 | 2100 rpm, envelope (free I_d, I_f) | torque_Nm | 830.4 | 901.7 | +8.6 **>5 %** |

The "V_rms_V (limit)" and "I_rms_A (limit)" rows compare the voltage and current at the maximum-torque point. They equal the limits when the point is limit-bound. Where they do not (IM at 3000-4500 rpm, current about 130-165 A) the maximum torque is a breakdown/voltage limit and both models agree on that behaviour.

### IM envelope: where the difference comes from (analyst flux caps imposed on both)

| machine | speed rpm | analyst T (Nm) | sim T, own leakage (Nm) | err % | sim T with analyst L_sigma,s, L_sigma,r, R_r (Nm) | err % |
|---|---|---|---|---|---|---|
| IM 2p8 | 1000 | 2947.8 | 2525.0 | -14.3 | 2531.6 | -14.1 |
| IM 2p8 | 3000 | 625.7 | 500.1 | -20.1 | 619.2 | -1.0 |
| IM 2p8 | 4500 | 284.5 | 227.8 | -19.9 | 280.0 | -1.6 |
| IM 2p4 | 2100 | 1262.6 | 1016.1 | -19.5 | 1018.0 | -19.4 |
| IM 2p4 | 4500 | 704.6 | 617.2 | -12.4 | 662.8 | -5.9 |
| IM 2p4 | 6000 | 426.9 | 352.0 | -17.6 | 422.7 | -1.0 |

With the analyst's stator and rotor leakage and R_r put into my model, the voltage-limited points (2p=8 at 3000 and 4500 rpm, 2p=4 at 4500 and 6000 rpm) are reproduced within -1.0 / -1.6 / -5.9 / -1.0 %. The points that remain 14-19 % low (2p=8 at 1000 rpm, 2p=4 at 2100 rpm) are the flux-limited ones, where my tooth/yoke cap (0.046 / 0.038 Wb against 0.0535 / 0.0439 Wb) is the cause. So the **IM model structure agrees; the numbers differ because of slot leakage (high speed) and the flux cap definition (low speed)**.

IM with soft MEC saturation only (no imposed caps):

| machine | speed rpm | analyst T | sim (soft MEC saturation only) | err % |
|---|---|---|---|---|
| IM 2p8 | 1000 | 2947.8 | 2516.3 | -14.6 |
| IM 2p8 | 3000 | 625.7 | 489.2 | -21.8 |
| IM 2p8 | 4500 | 284.5 | 212.4 | -25.4 |
| IM 2p4 | 2100 | 1262.6 | 1371.3 | +8.6 |
| IM 2p4 | 4500 | 704.6 | 611.7 | -13.2 |
| IM 2p4 | 6000 | 426.9 | 349.2 | -18.2 |


### WRSM envelope (free I_d and I_f)

| mode | speed rpm | analyst T free I_d (Nm) | analyst T I_d=0 | sim config B (g x4) | err % vs free I_d | sim config A (g as IM) | I_f (B) | i_d / i_q (B, A peak) |
|---|---|---|---|---|---|---|---|---|
| 2p8 | 1000 | 2931.8 | 2931.8 | 2626.6 | -10.4 | 972.1 | 1.00 | 25 / 433 |
| 2p8 | 2100 | 1622.4 | 849.1 | 1185.3 | -26.9 | 357.9 | 1.00 | -193 / 252 |
| 2p8 | 4250 | 756.6 | 209.4 | 554.3 | -26.7 | 161.6 | 1.00 | -235 / 129 |
| 2p8 | 4500 | 712.9 | 186.9 | 520.7 | -26.9 | 150.8 | 1.00 | -242 / 123 |
| 2p4 | 1000 | 1309.1 | 1309.1 | 1121.4 | -14.3 | 462.0 | 1.00 | -67 / 433 |
| 2p4 | 2100 | 830.4 | 806.1 | 901.7 | +8.6 | 294.3 | 1.00 | -158 / 287 |
| 2p4 | 4250 | 329.5 | 199.7 | 418.5 | +27.0 | 103.2 | 1.00 | -179 / 94 |
| 2p4 | 4500 | 307.5 | 178.3 | 392.4 | +27.6 | 99.9 | 1.00 | -179 / 88 |

Config B (air gap x4) is used in the main table; config A (same air gap as the IM) is voltage-limited far below the analyst at every speed, because its L_d is about 4x the analyst's pu value. The WRSM 2p=4 torque at low speed is 1121 Nm (B) vs 1309 Nm (analyst).

### Efficiency points

Reachability: WRSM 2p=4 at cruise (4250 rpm, 352 Nm): analyst not reachable (329 Nm available), simulation reachable (419 Nm available; eta 95.5 %, I_f 0.85, i_d = -144 A, 121 A rms, 29.05 V, iron loss 1525 W, field loss 2890 W). WRSM 2p=8 at 4500 rpm / 600 Nm (grade point): analyst reachable, simulation not reachable (520 Nm available). Both are consequences of the different reactances, see flag 2.

## 2. WRSM pole change: independent check of "no gain"

**Verdict: the "no gain" conclusion holds for the stator as specified (3 turns per coil in both modes, 48 identical coils). It flips only if the 2p=4 mode works with about half the turns per coil (Dahlander-like series/parallel switching), and it does not flip from a thicker stator yoke alone.**

What I computed:

* **Magnetising inductance.** From the winding-function harmonic sum, L_m(2p=4)/L_m(2p=8) = 2.698, which equals the analyst's k_w^2/p^2 factor (kw 0.793 / 0.966; 2.698). The scaling law itself is correct for fixed turns. From the MEC (config B, small signal, I_f = 0), L_d(2p=4)/L_d(2p=8) = 1.77 and L_q ratio = 2.80 (leakage included). The L_d ratio is lower than 2.7 because with the ++-- pattern the rotor is almost round to the 4-pole stator wave: L_d and L_q are equal (0.48 mH both) in 2p=4 mode, so there is no reluctance torque, and L_d falls further to 0.14 mH at full field as the stator yoke saturates (yoke B_y = 1.95 T). The analyst keeps the 8-pole saliency in 2p=4 (L_d/L_q = 1.9; scale factors 2.34 on L_d and 2.10 on L_q), so it overstates the reluctance torque of the 2p=4 mode and overstates L_d, which is the opposite error for torque at high speed (L_q is what limits it).
* **Rotor MMF patterns.** I took [1 -1 1 -1 ...] (2p=8) and [1 1 -1 -1 ...] (2p=4) from `FE_MMF.m` on 8 poles of 0.7 pole arc, with group A = coils 0,3,4,7 fixed and group B = coils 1,2,5,6 reversed. Flux per unit field: psi_f(2p=4)/psi_f(2p=8) = 1.36 at I_f = 0.3 (analyst 1.36), falling to 1.29 at 0.655 and 0.99 at full field. The drop is the stator yoke saturating: the 2p=4 flux per pole is twice the 2p=8 flux in a 25 mm yoke. The absolute 2p=4 flux at the analyst's I_f cap of 0.655 is 0.041 Wb (analyst 0.044 Wb), so the yoke-limit conclusion agrees within 7 %.
* **Torque envelope with design variants** (config B, free I_d and I_f):

| variant | 2p4/2p8 torque ratio at 1000 / 2100 / 4500 / 9000 rpm | crossover (2p4 > 2p8) | hybrid/2p8 torque at 4500 rpm | at 9000 rpm |
|---|---|---|---|---|
| baseline: as specified (yoke 25 mm, 3 turns both modes) | 0.43 / 0.76 / 0.75 / 0.74 | none up to 9000 rpm | 1.00 | 1.00 |
| yoke_x2: stator yoke 50 mm (sized for 2p=4 flux) | 0.50 / 0.72 / 0.76 / 0.74 | none up to 9000 rpm | 1.00 | 1.00 |
| turns_half_2p4: 2p=4 runs with half the turns per coil (Dahlander-like series/parallel) | 0.29 / 0.63 / 1.42 / 1.58 | 4250 rpm | 1.42 | 1.58 |
| yoke_x2_turns_half: both | 0.33 / 0.72 / 1.43 / 1.59 | 3000 rpm | 1.43 | 1.59 |

  The thicker yoke raises the low-speed 2p=4 torque (ratio 0.43 -> 0.50 at 1000 rpm) but not the high-speed ratio, because at high speed the 2p=4 mode is limited by the voltage drop across its large L_q (0.48 mH), not by saturation. Halving the turns of the 2p=4 mode divides the reactance by 4 and the flux linkage by 2: the 2p=4 mode then delivers 1.35-1.58 times the 2p=8 torque from 4250 rpm to 9000 rpm (crossover 4250 rpm; 3000 rpm with the thick yoke as well), while below 1500 rpm its torque is only 0.28-0.43 of the 2p=8 torque (that region is served by 2p=8 anyway). In SPB terms this means the turn count of a coil group would have to differ between modes, which the fixed 48-coil, 16-module wiring cannot do electronically. **Open design item**: a coil-to-module regrouping per mode (two coils per module leg in series, series pairs that are in phase in one mode and cancel in the other) needs either contactors or a redesigned winding.
* **Compared with the P2 draft machine** (`draft_parameters.json`: 10 kW, 4-pole 3000 rpm / 2-pole 6000 rpm, both at 100 Hz, eta 92.4 / 93.1 %, DC bus 400 V). Equal power at equal electrical frequency in both modes needs equal flux linkage and equal reactance per unit in the two modes, i.e. psi_f2/psi_f4 about 1 and x2/x4 about 1. With fixed turns the winding-function scaling gives psi ratio 2 (kw2/kw4)(c2/c4) and reactance ratio 4 (kw2/kw4)^2, which is 1.7 even for an illustrative kw2/kw4 = 0.65 (36 slots, pitch 8 of 9, belts regrouped for 2 poles; the draft does not state kw2; the same formulas give psi ratio 1.06). With that estimate the flux linkage could match but the reactance in the 2-pole mode would be 1.7 times higher at equal turns, so equal power at equal frequency needs fewer series turns in the 2-pole mode or a lower relative reactance than the SPB stator has. That is a statement about the draft, which is unverified (open-questions.md lists the 0.093 ohm field resistance and the 15.5 W / 30 W rotor loss as unresolved).

### Comparison with Enes's per-unit model (P5: `OPT-Bipolar-Field-Excitation/analysis/4_design_studies/torque_speed_switching.m`)

I ported the script to Python (`run_wrsm_study.py::enes_model`) and ran it with its own constants (kw4 = 0.808, kw2 = 0.760, alpha = 2/3, x_q4 = 0.31, field limit 429/381). Results:

| relation | dq model with winding halves series (4p) / parallel (2p) = Dahlander (turns halved in 2-pole mode) | same turns in both modes (analyst assumption, built with the same formulas) |
|---|---|---|
| k2 = psi_f2 / psi_f4 per unit field | 0.768 | 1.536 (= 2 x k2) |
| x2 = 2-pole reactance (pu) | 0.368 = 1.19 x x_q4 | 1.471 = 4.75 x x_q4 (= 4 x x2) |
| low-speed torque ratio 2-pole/4-pole | 0.37 | 0.75 |
| torque ratio at 2x the 4-pole base speed | 0.69 | 0.98 |

**The two models agree on the physics and differ in one assumption: the number of turns in the low-pole mode.** The reactance of a mode scales as N^2 k_w^2 / p^2 in both. The analyst keeps N (x2/x4 = 4 (kw2/kw4)^2 = 2.70 for the SPB winding). Enes's Dahlander connection halves N in the 2-pole mode, so x2 = x_q4 (kw2/kw4)^2 (alpha/k_q) = 1.19 x_q4 (kw ratio 0.94 for her 24-slot winding, round-rotor factor alpha/k_q = 1.34). Applying the same halving to the SPB winding gives 4 x (1/4) x 0.82^2 = 0.67, so the numbers are consistent once the turns assumption is aligned. Rebuilt from the same formulas with equal turns, Enes's model gives k2 = 1.54 and x2 = 4.7 x_q4 instead of 0.77 and 1.19 x_q4 (table above): the same-turns column is the analyst's assumption. The low-speed torque ratio of the two modes is nearly the same in all models: 0.45 (analyst WRSM), 0.43 (this simulation), 0.40 (Enes's COMSOL map study, 3.73 / 9.31 Nm in `efficiency_map_switch_ref_Nc11_output.txt`, with Dahlander turns); it is flux-limited and independent of the turn count. Enes's results that the 2-pole mode wins only at 19-20 krpm (1.3 % of the continuous area) and needs a larger inverter (15.6 vs 11.1 kVA) agree with the analyst's "no gain" for the same-turns case and with the Dahlander column here at x_q4 = 0.31 (torque ratio 0.69 at 2x base speed, no crossover).

How the verdict depends on the reactance level (run `enes_port.py`, `results/enes_kx_sweep.json`): with Dahlander turns the 2-pole mode wins at 2.9x base speed for x_q4 = 0.9 pu and at 2.5x for x_q4 = 1.2 pu, never up to 3x for 0.31 and 0.6 pu. With equal turns it wins only for x_q4 = 0.31 (at 2.5x) and never for 0.6-1.2 pu. The SPB WRSM sits at x_q4 of 0.65 pu (analyst) to 0.9 pu (this simulation, L_q 0.17 mH on a 0.186 mH base), which is where the turns choice decides the answer. This matches my MEC variants (crossover 4250 rpm = 3.5x the 2p=8 base speed of 1200 rpm with halved turns, none with equal turns).

### Stator connection used here, in a form that can be reused for the OPT machine

Stator pole-changing winding (the item the OPT repo lists as undefined) as realised by SPB:

* Q = 48 slots, 48 coils, coil k has its sides in slots k and k+7 (double layer, N_c = 3). Coil k sits at electrical angle alpha_k(p) = p 2 pi k / 48 in a mode with p pole pairs.
* Coil-group (module) j contains coils j, j+16, j+32 (120 deg mechanical apart), star-connected to an isolated neutral, driven by one 3-leg module. Its three coil currents sum to zero for every p that is not divisible by 3, so this one fixed wiring is a balanced three-phase group in 2p = 8 (p=4), 2p = 4 (p=2), and any p not a multiple of 3.
* Pole change = changing the phase of each coil command only: i_k = I cos(omega t - p 2 pi k/48). No contactors; the only requirement is that each of the 48 coils has its own leg. The winding factor is k_w = sin(p y pi / Q) with y = 7: 0.966 (p=4) and 0.793 (p=2), because there is no distribution factor (one coil per phase). Spatial harmonics appear only at p +- 48 j.
* Harmonics that are zero-sequence inside a module and carry no current are those with 120 deg x nu = 0 (mod 360), i.e. nu a multiple of 3 (p = 6, 12 in the rotor fields).
* Python for reuse: `coil_phases(p) = p*2*pi*np.arange(48)/48`, module `j` = `[j, j+16, j+32]`; the 12-slot linearised version in `Field Excitation/6-phase Induction Machine/Phase-Pole.pptx` has the same rule with 12 coils.

## 3. Pole transitions in the time domain

### IM 8 -> 4 pole at 2100 rpm (42 km/h)

Model: two decoupled spatial modes (p=4 and p=2) of the same 48 coils, one stator current vector and one referred rotor-flux vector each (the cage mode of one p is orthogonal to the other), rotor-flux-oriented current control with a 1 ms current loop, shared inverter budget (peak voltage |v_4| + |v_2| <= 41.1 V, current |i_4|^2 + |i_2|^2 <= (439 A)^2), vehicle speed from the 40 t ODE (m_eq = 42 t, G = 9.80, eta 0.97). Initial and final steady states are the loss-optimal points from the algebraic IM model. The two flux build-ups cannot overlap freely: the residual 2p=8 rotor flux (rotor time constant about 0.5 s) induces a voltage in the stator coils that takes part of the voltage budget (about 18-35 V peak of 41 V at 2100 rpm), so the controller reduces the 2p=8 torque and flux and builds the 2p=4 flux in the voltage left over.

Best of 27 schedules per case (t_d = 2p=8 torque ramp-down, t_f4 = 2p=8 flux ramp-down, t_f2 = 2p=4 flux ramp-up):

| case | schedule (t_d, t_f4, t_f2) s | min torque Nm | torque below 90 % for (s) | below 95 % until (s) | torque deficit Nm s | speed drop km/h (rpm) | peak I_rms / I_max | peak sum of mode currents A (limit 439) | voltage-limited share of time |
|---|---|---|---|---|---|---|---|---|---|
| grade_0pct (T_req 248 Nm) | 0.25, 0.06, 0.15 | 199 | 0.056 | 0.064 | 1.5 | 0.002 (0.1) | 0.66 | 406 | 4 % |
| grade_2pct (T_req 677 Nm) | 0.02, 0.15, 0.15 | -62 | 0.508 | 0.528 | 256.1 | 0.414 (20.7) | 0.62 | 282 | 42 % |

The four fixed schedules tried first:

| case | schedule | min torque Nm | below 90 % for (s) | speed drop km/h | peak I_rms / I_max |
|---|---|---|---|---|---|
| grade 0 % | 0.01, 0.03, 0.03 | -116 | 0.134 | 0.040 | 0.95 |
| grade 0 % | 0.02, 0.05, 0.05 | -64 | 0.102 | 0.023 | 1.00 |
| grade 0 % | 0.05, 0.1, 0.08 | 19 | 0.098 | 0.026 | 0.98 |
| grade 0 % | 0.01, 0.01, 0.01 | -116 | 0.172 | 0.059 | 0.86 |
| grade 2 % | 0.01, 0.03, 0.03 | -106 | 0.496 | 0.495 | 0.46 |
| grade 2 % | 0.02, 0.05, 0.05 | -53 | 0.496 | 0.490 | 0.48 |
| grade 2 % | 0.05, 0.1, 0.08 | -60 | 0.496 | 0.468 | 0.53 |
| grade 2 % | 0.01, 0.01, 0.01 | -218 | 0.496 | 0.497 | 0.49 |

* Flat road (248 Nm, speed holding): the best schedule (slow torque hand-over, 0.25 s) dips to 80 % of the requested torque and is below 90 % for 56 ms; the speed drop is 0.002 km/h. Fast schedules are worse: 10 ms ramps give a 134 ms gap and a torque reversal to -116 Nm, because the new flux is built while the old flux still induces a voltage.
* 2 % grade (677 Nm): under the voltage limit the 2p=4 flux needs about 0.5 s to reach the 0.038 Wb that the load requires. The torque is below 90 % for about 0.5 s in every schedule tried, the speed drop is 0.4-0.5 km/h (21-25 rpm), which is small for a 40 t truck, but all four 2 % schedules show a negative torque spike (-53 to -218 Nm in the fixed schedules, -62 Nm in the best one) that the controller would have to avoid by a torque-hand-over rule better than the one used here.
* Current: in the best schedules the peak coil current is 0.62-0.66 of I_max = 310 A rms (rms of both modes combined). Three of the four fixed flat-road schedules also stay below 1.0 I_max; the 20 ms schedule reaches 1.004 I_max at the 439 A amplitude budget.
* Reading: the pole change is a 60 ms (light load) to 500 ms (2 % grade) torque gap, comparable with a gear shift. The cause is the voltage budget, not the current. The analyst's estimate for the 2p=4 flux build-up (85 ms with forced i_d) assumed the full voltage was available; it is not while the residual 2p=8 flux (time constant about 0.5 s) is still in the machine.

### WRSM field reversal

Field circuit: 8 pole coils, flux per pole from the permeance matrix (zero net flux) plus interpolar leakage (assumed 45 mm x 20 mm slot between poles), group copper 4 kW at full I_f (shared input). Stator side: the fundamental flux linkage of the p=4 and p=2 modes follows the instantaneous pole currents by superposition of single-pole MEC solutions, scaled to the saturated pure patterns. Stator torque capability is optimised at each instant over the two modes' d/q currents under the shared voltage and current budgets (quasi-static: stator electrical time constants of 1-5 ms are neglected).

Field time constants (stored energy x 2 / 4 kW):

| configuration | tau_f, 2p=8 pattern | tau_f, 2p=4 pattern | pole-leakage factor |
|---|---|---|---|
| air gap as IM (config A, g_eff 1.3 mm) | 39 ms | 36 ms | 1.13 / 1.06 |
| air gap x4 (config B, needed for the analyst's L_d) | 208 ms | 172 ms | 1.52 / 1.26 |

The analyst's tau_f = 45 ms uses the 1.3 mm gap energy (68.5 J, same as mine) and a 1.3 leakage factor; my interpolar-leakage estimate is 1.13 at that gap (39 ms). **But the analyst's L_d corresponds to a gap about 4x larger, and the field energy then grows 4x: tau_f is 0.17-0.21 s. The analyst's reactances and field time constant are not mutually consistent.**

Transition results (config B, 2100 rpm, 2p=8 -> 2p=4, requested torque = road load):

| field strategy | grade | field reversal: I_B crosses 0 at (s) / reaches 95 % at (s) | min torque Nm | time below 90 % (s) | speed drop km/h | peak I_rms / I_max |
|---|---|---|---|---|---|---|
| freewheel_blank_unforced | 0 % (248 Nm) | 0.60 / 1.16 | 248 | 0.00 | 0.000 | 0.84 |
| forced_3x | 0 % (248 Nm) | 0.06 / 0.13 | 248 | 0.00 | 0.000 | 0.84 |
| freewheel_blank_unforced | 2 % (677 Nm) | 0.60 / 1.16 | 624 | 0.00 | 0.003 | 0.84 |
| forced_3x | 2 % (677 Nm) | 0.06 / 0.13 | 628 | 0.00 | 0.001 | 0.84 |
| ksweep_forced | 0 % (248 Nm) | 0.21 / 0.40 | 248 | 0.00 | 0.000 | 0.84 |
| ksweep_forced | 2 % (677 Nm) | 0.21 / 0.40 | 620 | 0.00 | 0.002 | 0.84 |

* **Free-wheel + 20 ms blanking, unforced (P1 sequence):** with tau_f of 0.17-0.21 s the group-B current passes zero at 0.60 s and reaches 95 % of the new polarity at 1.16 s. With forced 3x field voltage the reversal takes 0.13 s (zero crossing 0.06 s). A gradual k-sweep over 0.4 s (P4 pattern [1 k -k -1], k from -1 to +1, forced voltage) reaches 95 % at 0.40 s. With the IM-sized air gap (config A, tau_f 36-39 ms) the same sequences take 0.25 s (free-wheel + unforced) and 0.03 s (forced), consistent with the analyst's 0.29 s and 0.05 s.
* **The torque does not drop out in any strategy** in my quasi-static model: while group B passes through zero the rotor pattern is [1 0 0 -1 ...], which carries both the p=4 and the p=2 harmonic, and the 48-coil stator is driven in both modes at once. The torque capability stays above 90 % of the requested torque (min 248 Nm of 248 flat, 620-624 Nm of 677 on the 2 % grade). The speed drop is 0.002-0.003 km/h. The price is that the stator must run two modes at once with a shared voltage budget (peak stator current 84 % of I_max), and a smooth hand-over of the d-axis reference as k moves. The simulation does not include the field-circuit induction from the stator currents (damping) nor the eddy currents in a solid rotor, which would slow the field; the margin is large for flat road, and thin (about 8 %) for the 2 % grade.
* With the air gap as in the IM (config A) the 2p=4 mode cannot carry the 677 Nm grade load at 2100 rpm at all (294 Nm available), so the grade case is not meaningful there.

## 4. 10th-order rotor harmonic in 2p=4 mode

Spatial harmonics of the rotor field for the two patterns (0.7 pole arc, B_nu / B0, FFT amplitude of the pole pattern) and the module test (phase shift of the three coils j, j+16, j+32 is 120 deg x nu):

| rotor mode | order | B_nu / B0 | winding factor | phase shift between the 3 coils of a module | zero-sequence? |
|---|---|---|---|---|---|
| 2p4 | 2 | 0.941 | 0.793 | 240 deg | no |
| 2p4 | 6 | 0.598 | 0.383 | 0 deg | yes |
| 2p4 | 10 | 0.137 | 0.991 | 120 deg | no |
| 2p4 | 14 | 0.168 | 0.131 | 240 deg | no |
| 2p8 | 4 | 1.135 | 0.966 | 120 deg | no |
| 2p8 | 12 | 0.067 | 0.707 | 0 deg | yes |
| 2p8 | 20 | 0.179 | 0.259 | 240 deg | no |

**The analyst's note is correct: nu = 10 is not zero-sequence in a module (phase shift 120 deg, a balanced set), while nu = 6 (and 12) is (phase shift 0).** The 10th harmonic of the 2p=4 rotor drives a balanced three-phase set of EMFs in every module, which the isolated neutral does not block.

Magnitude (per coil, field at full I_f, impedance from the 48-coil model at that order, no compensation by the inverter):

| rotor mode | order nu | speed rpm | f (Hz) | harmonic EMF (V rms per coil) | EMF / V_max | |Z| (ohm) | circulating current (A rms per coil) | share of I_max | copper loss, 48 coils (W) |
|---|---|---|---|---|---|---|---|---|---|
| 2p4 | 10 | 2100 | 350 | 5.36 | 0.18 | 0.465 | 11.5 | 3.7 % | 14 |
| 2p4 | 10 | 4500 | 750 | 11.50 | 0.40 | 0.996 | 11.5 | 3.7 % | 14 |
| 2p4 | 14 | 2100 | 490 | 0.86 | 0.03 | 0.032 | 27.3 | 8.8 % | 77 |
| 2p4 | 14 | 4500 | 1050 | 1.85 | 0.06 | 0.068 | 27.4 | 8.8 % | 77 |
| 2p8 | 20 | 2100 | 700 | 1.83 | 0.06 | 0.064 | 28.7 | 9.3 % | 85 |
| 2p8 | 20 | 4500 | 1500 | 3.92 | 0.13 | 0.137 | 28.7 | 9.3 % | 85 |

* nu = 10 in 2p=4 mode: 5.4 V rms per coil at 2100 rpm (18 % of the 29.1 V limit) and 11.5 V at 4500 rpm (40 %). The stator impedance at that order (0.46-1.0 ohm, L = 0.20 mH) limits the free-running current to **11.5 A rms per coil, 3.7 % of I_max, independent of speed**, with 13.8 W of copper loss over all 48 coils. The resulting drag torque is below 0.1 Nm, so the harm is mainly the voltage and the loss, not the torque.
* If the current controller fights it (holds the 10th-order current at zero), it must supply 5.4-11.5 V at 350-750 Hz on top of the fundamental, which is 18-40 % of the voltage budget. That is not available where the fundamental already uses the whole budget (field-weakening region), and there the 11.5 A flows.
* Higher orders have a smaller EMF but a much smaller impedance, because the two coil sides in each slot carry almost equal-phase currents at these orders (small net slot current, hence small slot leakage): nu = 14 (2p=4) gives 0.9-1.9 V and **27 A (8.8 % of I_max)**, nu = 20 (2p=8) gives 1.8-3.9 V and 29 A (9.2 %). Their copper loss (77-85 W) is larger than for nu = 10, so they need the same attention as the 10th order. These values depend strongly on the leakage of the real slot (see flag 1).
* The values assume the full-field B0 of 0.71 T with the harmonic content of the ideal pole-arc pattern. Stator-yoke saturation in 2p=4 mode reduces the fundamental but is not applied to the harmonics, so the harmonic EMFs are an upper bound relative to the fundamental.

## Method limits

* No FEA. The MEC has 48 teeth and a lumped rotor; no tooth tips, no slot opening effects (carried by g_eff = 1.3 mm), no rotor-position ripple.
* The IM transition and the WRSM stator side are rotor-flux/dq models with linear secant L_m; the WRSM transition is quasi-static on the stator side.
* WRSM config B is a comparison device, not a design. The 4x air gap implies 4x the field MMF per pole (about 2.95 kA-turns); I did not check whether the analyst's 4 kW field copper budget can carry that, it is kept as given.
* Slot leakage geometry (2 layers of 21 mm and 3 mm wedge) is my assumption; the real slot design shifts every number in flag 1.

## Appendix: all compared numbers

| machine | point | quantity | analyst | simulation | error % |
|---|---|---|---|---|---|
| IM 2p8 | 1000 rpm, envelope | torque_Nm | 2948 | 2525 | -14.3 **>5 %** |
| IM 2p8 | 1000 rpm, envelope | V_rms_V (limit) | 29.09 | 23.99 | -17.5 **>5 %** |
| IM 2p8 | 1000 rpm, envelope | I_rms_A (limit) | 310.4 | 308.4 | -0.7 |
| IM 2p8 | 3000 rpm, envelope | torque_Nm | 625.7 | 500.1 | -20.1 **>5 %** |
| IM 2p8 | 3000 rpm, envelope | V_rms_V (limit) | 29.09 | 28.97 | -0.4 |
| IM 2p8 | 3000 rpm, envelope | I_rms_A (limit) | 310.4 | 164.7 | -47.0 **>5 %** |
| IM 2p8 | 4500 rpm, envelope | torque_Nm | 284.5 | 227.8 | -19.9 **>5 %** |
| IM 2p8 | 4500 rpm, envelope | V_rms_V (limit) | 29.09 | 28.92 | -0.6 |
| IM 2p8 | 4500 rpm, envelope | I_rms_A (limit) | 310.4 | 127.2 | -59.0 **>5 %** |
| IM 2p4 | 2100 rpm, envelope | torque_Nm | 1263 | 1016 | -19.5 **>5 %** |
| IM 2p4 | 2100 rpm, envelope | V_rms_V (limit) | 29.09 | 19.71 | -32.3 **>5 %** |
| IM 2p4 | 2100 rpm, envelope | I_rms_A (limit) | 310.4 | 286.7 | -7.7 **>5 %** |
| IM 2p4 | 4500 rpm, envelope | torque_Nm | 704.6 | 617.2 | -12.4 **>5 %** |
| IM 2p4 | 4500 rpm, envelope | V_rms_V (limit) | 29.09 | 28.82 | -0.9 |
| IM 2p4 | 4500 rpm, envelope | I_rms_A (limit) | 310.4 | 309.4 | -0.3 |
| IM 2p4 | 6000 rpm, envelope | torque_Nm | 426.9 | 352 | -17.6 **>5 %** |
| IM 2p4 | 6000 rpm, envelope | V_rms_V (limit) | 29.09 | 28.71 | -1.3 |
| IM 2p4 | 6000 rpm, envelope | I_rms_A (limit) | 310.4 | 233.6 | -24.7 **>5 %** |
| PMSM 2p8 | 1000 rpm, envelope | torque_Nm | 3060 | 3055 | -0.2 |
| PMSM 2p8 | 1000 rpm, envelope | I_rms_A at max T | 310.4 | 310.2 | -0.1 |
| PMSM 2p8 | 2100 rpm, envelope | torque_Nm | 1873 | 1836 | -2.0 |
| PMSM 2p8 | 2100 rpm, envelope | I_rms_A at max T | 310.4 | 308.6 | -0.6 |
| PMSM 2p8 | 4500 rpm, envelope | torque_Nm | 897.3 | 855.8 | -4.6 |
| PMSM 2p8 | 4500 rpm, envelope | I_rms_A at max T | 310.4 | 306 | -1.4 |
| PMSM 2p8 | 6000 rpm, envelope | torque_Nm | 665.7 | 616.1 | -7.4 **>5 %** |
| PMSM 2p8 | 6000 rpm, envelope | I_rms_A at max T | 310.4 | 308.3 | -0.7 |
| WRSM 2p8 | 1000 rpm, envelope (free I_d, I_f) | torque_Nm | 2932 | 2627 | -10.4 **>5 %** |
| WRSM 2p8 | 2100 rpm, envelope (free I_d, I_f) | torque_Nm | 1622 | 1185 | -26.9 **>5 %** |
| WRSM 2p8 | 4250 rpm, envelope (free I_d, I_f) | torque_Nm | 756.6 | 554.3 | -26.7 **>5 %** |
| WRSM 2p8 | 4500 rpm, envelope (free I_d, I_f) | torque_Nm | 712.9 | 520.7 | -26.9 **>5 %** |
| WRSM 2p4 | 1000 rpm, envelope (free I_d, I_f) | torque_Nm | 1309 | 1121 | -14.3 **>5 %** |
| WRSM 2p4 | 2100 rpm, envelope (free I_d, I_f) | torque_Nm | 830.4 | 901.7 | +8.6 **>5 %** |
| WRSM 2p4 | 4250 rpm, envelope (free I_d, I_f) | torque_Nm | 329.5 | 418.5 | +27.0 **>5 %** |
| WRSM 2p4 | 4500 rpm, envelope (free I_d, I_f) | torque_Nm | 307.5 | 392.4 | +27.6 **>5 %** |
| IM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | I_rms_A | 211.9 | 219.4 | +3.6 |
| IM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | V_rms_V | 7.987 | 8.069 | +1.0 |
| IM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_cu_stator_W | 4644 | 5104 | +9.9 **>5 %** |
| IM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_fe_W | 264.7 | 218.4 | -17.5 **>5 %** |
| IM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | eta_pct | 87.9 | 86.95 | -1.1 |
| IM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_cu_rotor_W | 3700 | 4069 | +10.0 **>5 %** |
| PMSM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | I_rms_A | 221.7 | 221.7 | -0.0 |
| PMSM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | V_rms_V | 7.456 | 7.471 | +0.2 |
| PMSM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_cu_stator_W | 5084 | 5084 | -0.0 |
| PMSM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_fe_W | 236.3 | 234.8 | -0.6 |
| PMSM_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | eta_pct | 92.14 | 92.15 | +0.0 |
| WRSM_freeId_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | I_rms_A | 211.8 | 217.6 | +2.8 |
| WRSM_freeId_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | V_rms_V | 7.379 | 8.48 | +14.9 **>5 %** |
| WRSM_freeId_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_cu_stator_W | 4640 | 4901 | +5.6 **>5 %** |
| WRSM_freeId_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_fe_W | 238.4 | 269.5 | +13.0 **>5 %** |
| WRSM_freeId_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | eta_pct | 87.57 | 87.22 | -0.4 |
| WRSM_freeId_2p8 | launch_300rpm_2000Nm (300 rpm, 2000 Nm) | P_field_W | 4000 | 4000 | +0.0 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | I_rms_A | 211.9 | 219.4 | +3.6 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | V_rms_V | 24.71 | 24.91 | +0.8 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_cu_stator_W | 4644 | 5104 | +9.9 **>5 %** |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_fe_W | 947.9 | 976.1 | +3.0 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | eta_pct | 95.7 | 95.32 | -0.4 |
| IM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_cu_rotor_W | 3700 | 4069 | +10.0 **>5 %** |
| PMSM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | I_rms_A | 222.2 | 222.8 | +0.3 |
| PMSM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | V_rms_V | 23.37 | 23.01 | -1.5 |
| PMSM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_cu_stator_W | 5106 | 5135 | +0.6 |
| PMSM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_fe_W | 845.5 | 1025 | +21.2 **>5 %** |
| PMSM_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | eta_pct | 97.18 | 97.09 | -0.1 |
| WRSM_freeId_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | I_rms_A | 212.3 | 217.6 | +2.5 |
| WRSM_freeId_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | V_rms_V | 23.61 | 27.44 | +16.2 **>5 %** |
| WRSM_freeId_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_cu_stator_W | 4663 | 4901 | +5.1 **>5 %** |
| WRSM_freeId_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_fe_W | 885.2 | 1272 | +43.7 **>5 %** |
| WRSM_freeId_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | eta_pct | 95.59 | 95.31 | -0.3 |
| WRSM_freeId_2p8 | accel_1000rpm_2000Nm (1000 rpm, 2000 Nm) | P_field_W | 3980 | 4000 | +0.5 |
| IM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | I_rms_A | 182.3 | 199.3 | +9.3 **>5 %** |
| IM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | V_rms_V | 29.08 | 29.09 | +0.0 |
| IM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_cu_stator_W | 3438 | 4170 | +21.3 **>5 %** |
| IM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_fe_W | 719.2 | 719.1 | -0.0 |
| IM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | eta_pct | 96.61 | 96.01 | -0.6 |
| IM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_cu_rotor_W | 2863 | 3500 | +22.3 **>5 %** |
| IM_2p4 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | I_rms_A | 243 | 282.1 | +16.1 **>5 %** |
| IM_2p4 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | V_rms_V | 20.13 | 18.77 | -6.8 **>5 %** |
| IM_2p4 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_cu_stator_W | 6107 | 8314 | +36.1 **>5 %** |
| IM_2p4 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_fe_W | 626.8 | 547.1 | -12.7 **>5 %** |
| IM_2p4 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | eta_pct | 94.66 | 93.04 | -1.7 |
| IM_2p4 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_cu_rotor_W | 4754 | 6469 | +36.1 **>5 %** |
| PMSM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | I_rms_A | 154.5 | 157.3 | +1.8 |
| PMSM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | V_rms_V | 29.08 | 28.67 | -1.4 |
| PMSM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_cu_stator_W | 2471 | 2560 | +3.6 |
| PMSM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_fe_W | 960.8 | 1002 | +4.2 |
| PMSM_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | eta_pct | 98.24 | 98.18 | -0.1 |
| WRSM_freeId_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | I_rms_A | 170.7 | 169.8 | -0.5 |
| WRSM_freeId_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | V_rms_V | 29.08 | 28.84 | -0.8 |
| WRSM_freeId_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_cu_stator_W | 3014 | 2982 | -1.1 |
| WRSM_freeId_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_fe_W | 761.7 | 1067 | +40.0 **>5 %** |
| WRSM_freeId_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | eta_pct | 97.25 | 96.65 | -0.6 |
| WRSM_freeId_2p8 | suburban_2000rpm_1000Nm (2000 rpm, 1000 Nm) | P_field_W | 1824 | 2890 | +58.4 **>5 %** |
| IM_2p4 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | I_rms_A | 170.6 | 174.4 | +2.2 |
| IM_2p4 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | V_rms_V | 29.02 | 29.06 | +0.2 |
| IM_2p4 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_cu_stator_W | 3011 | 3206 | +6.5 **>5 %** |
| IM_2p4 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_fe_W | 876.1 | 1015 | +15.9 **>5 %** |
| IM_2p4 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | eta_pct | 96.87 | 96.66 | -0.2 |
| IM_2p4 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_cu_rotor_W | 2338 | 2482 | +6.1 **>5 %** |
| PMSM_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | I_rms_A | 210.6 | 211.6 | +0.5 |
| PMSM_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | V_rms_V | 28.91 | 28.74 | -0.6 |
| PMSM_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_cu_stator_W | 4587 | 4632 | +1.0 |
| PMSM_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_fe_W | 999.4 | 676.4 | -32.3 **>5 %** |
| PMSM_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | eta_pct | 97.14 | 97.26 | +0.1 |
| WRSM_freeId_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | I_rms_A | 167.7 | 167.1 | -0.3 |
| WRSM_freeId_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | V_rms_V | 29.08 | 28.64 | -1.5 |
| WRSM_freeId_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_cu_stator_W | 2909 | 2889 | -0.7 |
| WRSM_freeId_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_fe_W | 543.7 | 960.2 | +76.6 **>5 %** |
| WRSM_freeId_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | eta_pct | 97.33 | 96.5 | -0.9 |
| WRSM_freeId_2p8 | highway_3500rpm_600Nm (3500 rpm, 600 Nm) | P_field_W | 1692 | 3240 | +91.5 **>5 %** |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | I_rms_A | 119.7 | 122.6 | +2.5 |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | V_rms_V | 29.06 | 28.98 | -0.3 |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_stator_W | 1481 | 1667 | +12.5 **>5 %** |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_fe_W | 777.9 | 904.2 | +16.2 **>5 %** |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | eta_pct | 97.05 | 96.78 | -0.3 |
| IM_2p4 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_rotor_W | 1146 | 1287 | +12.3 **>5 %** |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | I_rms_A | 215.1 | 217.8 | +1.2 |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | V_rms_V | 28.93 | 28.39 | -1.9 |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_stator_W | 4789 | 4908 | +2.5 |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_fe_W | 1116 | 578.5 | -48.1 **>5 %** |
| PMSM_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | eta_pct | 95.56 | 95.8 | +0.3 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | I_rms_A | 119.8 | 118.6 | -1.0 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | V_rms_V | 29.08 | 28.53 | -1.9 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_cu_stator_W | 1485 | 1455 | -2.0 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_fe_W | 482.9 | 773.8 | +60.3 **>5 %** |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | eta_pct | 97.39 | 96.74 | -0.7 |
| WRSM_freeId_2p8 | cruise_85kmh_road_load (4250 rpm, 352 Nm) | P_field_W | 876.2 | 1690 | +92.9 **>5 %** |
| IM_2p4 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | I_rms_A | 236.7 | 265.2 | +12.0 **>5 %** |
| IM_2p4 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | V_rms_V | 29.08 | 29.05 | -0.1 |
| IM_2p4 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | P_cu_stator_W | 5794 | 7318 | +26.3 **>5 %** |
| IM_2p4 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | P_fe_W | 651.2 | 655 | +0.6 |
| IM_2p4 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | eta_pct | 95.75 | 94.88 | -0.9 |
| IM_2p4 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | P_cu_rotor_W | 4525 | 5705 | +26.1 **>5 %** |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | I_rms_A | 251.9 | 254.7 | +1.1 |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | V_rms_V | 28.7 | 28.2 | -1.7 |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | P_cu_stator_W | 6566 | 6710 | +2.2 |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | P_fe_W | 1049 | 539.9 | -48.5 **>5 %** |
| PMSM_2p8 | grade_at_vmax_4500rpm_600Nm (4500 rpm, 600 Nm) | eta_pct | 96.86 | 96.98 | +0.1 |

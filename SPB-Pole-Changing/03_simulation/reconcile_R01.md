# R01 reconcile: agreed geometry and what the analyst must change

Date 2026-11-02. Author: simulator. Shared source of truth: `data/machine_geometry.json` (inputs in the top-level groups, quantities derived from them in `derived`; load with `json.load`, units are in the key names). Scripts: `03_simulation/write_geometry_inputs.py` (inputs), `compute_R01.py` (derived), `run_validation_R01.py`, `headline_R01.py`; results `results/validation_points_R01.json`, `results/headline_R01.json`.

## Corrections to T04 (my side, read first)

Two numerical resolution errors in my own T04 model inflated the disagreement. Both are fixed in `spb_core.py` and the T04 points re-run (`results/validation_points_T04_rerun.json`, same legacy assumptions as T04):

1. The IM magnetising curve was sampled with 12 A steps, which floored the flux cap to 0.046 / 0.038 Wb. With a fine grid the caps on the same geometry model are within 4 % of the analyst's (0.0517 vs 0.0535 and 0.0422 vs 0.0439 Wb). **Flag 3 of T04 was an artifact.**
2. The slip grid (6 rad/s steps) quantised the current-limited torque. With a log-spaced grid the low-speed IM torque agrees within 1.5 % (T04 rerun: 2p=8 at 1000 rpm +1.0 %, 2p=4 at 2100 rpm +1.5 %; the T04 file said -14 % and -19 %).

After the correction, the T04 rerun has 49 of 136 numbers beyond 5 % (T04 said 59 of 136). The remaining IM disagreement (-11 to -19 % at 3000-6000 rpm) goes to -0.5 to -0.1 % when the analyst's leakage is put into my model, so **the IM models have the same structure and differ only in stator slot leakage**. The WRSM disagreement is a different input (reactance basis), see the table.

## 1. The agreed drawing (summary; full file in `data/machine_geometry.json`)

* Stator: 48 slots, R_bore 165 mm, stack 360 mm, R_out 235 mm, yoke 25 mm, slot 9 x 45 mm with a 3 mm opening and 1.5 mm tip, coil pitch 7, 3 turns, double layer, stacking factor 0.95, M270-35A-like B-H table, parallel slots (teeth 12.6 mm at the bore, 18.5 mm at the root).
* Slot layout from the bottom: liner 0.5, bottom layer 17.7 (3 conductors 7.5 x 5.4 mm bare), separator 1.0, top layer 17.7, air/wedge 6.6, tip 1.5 = 45 mm. Copper area per turn 40.5 mm2, so R_coil, copper mass 62.9 kg and the T03b constraint are unchanged; gross slot fill 0.60 (0.86 of the insulated window), J = 7.7 A/mm2 at 310 A and 6.6 A/mm2 at 266 A (oil cooling, as T03).
* IM air gap 1.0 mm; Carter coefficients from the stator (3 mm) and rotor (1.5 mm) openings give g_eff = 1.076 mm; **no saturation factor in g_eff**.
* IM cage: 58 bars 7.0 x 21.4 mm (150 mm2), 1 mm bridge, copper rings 600 mm2 at 270 mm.
* WRSM rotor: 8 salient poles, arc 0.7, pole body 50 mm, interpolar slots 55 mm deep, shaft radius 40 mm, rotor yoke 65 mm. Air gap and field winding chosen in `derived.wrsm` (below).

## 2. Per-parameter reconcile

| parameter | analyst | agreed (this file) | adopt | why | effect |
|---|---|---|---|---|---|
| stator slot leakage L_slot, 2p8 (uH) | 12.6 | 39.5 | **mine** | Energy method on the agreed layout: 6 hairpin conductors stacked 36.9 mm deep in a 9 mm slot, 6.6 mm of air above them, 1.5 mm tooth tip over a 3 mm opening. The analyst's lambda 1.2/0.4 equals roughly a single 20 mm layer; a full 45 mm slot already gives h/(3w) = 1.67 for one fully fed layer. | +213 % L_slot; this is the whole IM high-speed difference |
| stator slot leakage L_slot, 2p4 (uH) | 10.6 | 28.5 | **mine** | Energy method on the agreed layout: 6 hairpin conductors stacked 36.9 mm deep in a 9 mm slot, 6.6 mm of air above them, 1.5 mm tooth tip over a 3 mm opening. The analyst's lambda 1.2/0.4 equals roughly a single 20 mm layer; a full 45 mm slot already gives h/(3w) = 1.67 for one fully fed layer. | +169 % L_slot; this is the whole IM high-speed difference |
| stator differential leakage, 2p8 (uH) | 22.9 | 25.7 | mine | same winding-function sum; differs only through g_eff (1.076 vs 1.3 mm) | small |
| stator differential leakage, 2p4 (uH) | 15.3 | 17.2 | mine | same winding-function sum; differs only through g_eff (1.076 vs 1.3 mm) | small |
| end-winding leakage (uH) | 1.7 | 1.7 | keep (shared) | lambda_end 0.3 and l_end are not verified by either of us; needs a winding drawing | none |
| total stator leakage L_sigma,s, 2p8 (uH) | 37.2 | 66.8 | **mine** | sum of the above | +80 % |
| total stator leakage L_sigma,s, 2p4 (uH) | 27.6 | 47.3 | **mine** | sum of the above | +72 % |
| rotor leakage referred, 2p8 (uH) | 35.1 | 41.5 | mine | lambda_bar 1.69 from the 7.0 x 21.4 mm bar and 1 mm bridge (analyst 1.5); area unchanged | +18 % |
| rotor leakage referred, 2p4 (uH) | 26.9 | 31.2 | mine | lambda_bar 1.69 from the 7.0 x 21.4 mm bar and 1 mm bridge (analyst 1.5); area unchanged | +16 % |
| cage resistance R_r referred, 2p8 / 2p4 (mOhm) | 1.998 / 1.723 | 1.998 / 1.723 | same | derived independently from the bar/ring dimensions; identical | none |
| air gap for L_m (mm) | 1.30 (Carter x saturation) | 1.076 (Carter stator 1.055 x rotor 1.020) | **mine** | k_sat must not sit in g_eff when the flux caps already model saturation. Agreed: unsaturated L_m(2p8) = 1.113 mH (analyst 0.921), L_m(2p4) = 3.002 mH (analyst 2.485); iron saturation via the table `derived.flux_caps.<mode>.magnetising_curve` (secant k_sat at the cap: 1.035 at 2p=8, 1.158 at 2p=4) | +20 % L_m, lower I_mag by the same factor; < 1 % on torque |
| rotor-flux cap psi_cap, 2p8 (mWb rms) | 53.5 | 51.7 | mine | limited by the stator yoke (yoke) in both modes: B_y <= 1.45 T with stacking factor 0.95. Equivalent B_g1 caps 0.835 T (yoke), 0.914 T (tooth tip 1.65 T) against the analyst's 0.879 T | -3 % |
| rotor-flux cap psi_cap, 2p4 (mWb rms) | 43.9 | 42.2 | mine | limited by the stator yoke (yoke) in both modes: B_y <= 1.45 T with stacking factor 0.95. Equivalent B_g1 caps 0.417 T (yoke), 0.914 T (tooth tip 1.65 T) against the analyst's 0.439 T | -4 % |
| tooth geometry | 12.6 mm parallel | 12.6 mm at the bore, 18.5 mm at the root (parallel slots) | mine | B limit checked at the tip; iron MMF at one third height; teeth mass 87.8 kg (analyst 74.9), yoke 91.4 kg (96.3) with k_st | iron loss +- 5 % |
| stacking factor | none | 0.95 | mine | lamination | flux caps -5 % (already in the line above) |
| copper: R_coil, mass, current density | 2.155 mOhm, 62.9 kg, 7.7 / 6.6 A/mm2 | identical | same | 7.5 x 5.4 mm hairpin conductors (40.5 mm2), slot fill 0.60 of the gross slot, 0.86 of the insulated window | none |
| WRSM L_d, L_q at 2p=8 (pu) | 1.10 / 0.65 | 1.50 / 1.05 (g = 5 mm) | **mine** | the analyst's pair is a 'typical machine' input; with the IM gap this stator gives L_d = 5.8 pu. The pair is reached only by a larger gap, and L_q contains 0.36 pu of slot + end leakage so 0.65 needs a gap above 8 mm | the base of every WRSM result |
| WRSM L_d, L_q at 2p=4 (pu) | 2.58 / 1.36 | 0.84 / 2.62 | **mine** | MEC: in the ++-- pattern the rotor looks round to the 4-pole wave, so L_d <= L_q (inverse saliency, L_d falls with field because the stator yoke saturates). Scaling the 8-pole pair by k_w^2/p^2 keeps the saliency and is wrong in both axes | 2p=4 torque at high speed up to +20 % higher than the analyst |
| WRSM psi_f,max (mWb rms) | 49.2 (2p8), 43.9 (2p4 at I_f 0.655) | 48.3, 47.6 (full field) | agree | within 2-8 %; the 2p=4 flux is limited by the stator yoke gradually, not by an I_f cap of 0.655 | small |
| WRSM field MMF per pole | 737 A-turns | 2990 A-turns | **mine** | B0 = 0.712 T over g_eff = 5.27 mm. 737 At is B0 over the IM gap | field copper uses the next line |
| WRSM field copper at full field | 4.0 kW (J not stated) | 2.31 kW at J_f = 4.0 A/mm2 | **mine** | 743 mm2 per coil side (half an interpolar slot 54 x 55 mm, fill 0.5), mean turn 1.0 m, rho 2.4e-8 | field loss in the efficiency points x 0.58 |
| WRSM tau_f, 2p8 / 2p4 | 45 ms | 291 / 262 ms | **mine** | 2 W_f / P_f from the permeance matrix with interpolar leakage; the 45 ms belongs to the IM gap. Forced (3x) reversal to 95 % takes about 0.65 tau_f, free-wheel + unforced about 6 tau_f + 20 ms | P1 sequence 0.29 s -> about 1.8 s; forced 0.05 s -> about 0.2 s |
| rotor yoke margin 2.0 / I_f cap 0.655 | yes | not needed | mine | rotor yoke 65 mm gives 1.0 T in the ++-- pattern; only the stator yoke limits | I_f cap goes away |

### Which WRSM does a real 300 kW, 8-pole machine in this stator have?

An analyst WRSM with L_d = 1.10 pu is not physical at the IM gap (g_eff 1.08 mm gives L_d = 5.8 pu). A 300 kW, 8-pole WRSM in this stator needs a mechanical gap of about 5 mm (g_eff 5.3 mm), 2990 A-turns per pole at B0 = 0.71 T, J_f = 4.0 A/mm2 and 2.3 kW of field copper. The analyst's 4 kW and 45 ms correspond to 737 A-turns, i.e. the IM gap.

Sweep (350 kW per-unit base, L_base = 186 uH; full table in `derived.wrsm_gap_sweep`):

| g (mm) | F (A-turns/pole) | J_f (A/mm2) | P_field (kW) | L_d / L_q 2p8 (pu) | L_d / L_q 2p4 (pu) | tau_f 2p8 / 2p4 (s) |
|---|---|---|---|---|---|---|
| 1 | 598 | 0.8 | 0.09 | 5.83 / 3.30 | 4.42 / 10.49 | 1.32 / 1.30 |
| 2 | 1196 | 1.5 | 0.35 | 3.14 / 1.91 | 1.84 / 5.80 | 0.68 / 0.65 |
| 3 | 1794 | 2.3 | 0.81 | 2.23 / 1.43 | 1.26 / 4.05 | 0.46 / 0.43 |
| 4 | 2392 | 3.2 | 1.46 | 1.78 / 1.20 | 1.00 / 3.16 | 0.36 / 0.33 |
| 5 | 2990 | 4.0 | 2.31 | 1.50 / 1.05 | 0.84 / 2.62 | 0.29 / 0.26 |
| 6 | 3587 | 4.9 | 3.37 | 1.32 / 0.96 | 0.76 / 2.25 | 0.25 / 0.22 |
| 8 | 4783 | 6.7 | 6.18 | 1.08 / 0.84 | 0.68 / 1.80 | 0.19 / 0.17 |

Reading: a real design is a 4-6 mm gap with 2.4-3.6 kA-turns per pole, 3-5 A/mm2 and 1.5-3.4 kW of field copper. Choice rule: smallest gap with L_d(2p=8) <= 1.6 pu and J_f <= 6 A/mm2, which gives 5 mm. The analyst's pair (1.10 / 0.65 pu) is not reachable below about 8 mm (6.7 A/mm2, 6.2 kW). The gap is the one free parameter of the WRSM; if the analyst prefers another, `compute_R01.py::wrsm_design(g)` returns every number.

## 3. Expected effect on the headline numbers (300 kW)

| headline (300 kW, same V and I limits) | analyst (T03 300 kW file) | simulator on the agreed geometry | effect |
|---|---|---|---|
| IM with pole change: crossover 2p4 > 2p8 (rpm) | 2252 | 1920 | -15 % |
| IM peak torque (Nm) / max start grade at G = 9.80 | 2523 / 10.8 % | 2427 / 10.4 % | -4 % torque, -0.5 point grade (limit stays 12 %: G >= about 11.3 instead of 10.9) |
| IM power at 4500 rpm (kW) | 305 (at v_max) | 248 | -19 % |
| IM CPSR with pole change | 4.55 | 1.22 by the same 0.95 P_base rule (P_base 275 kW at 1080 rpm) | the metric is threshold-sensitive: the power after the crossover is 248 kW (91 % of P_base), below the 95 % band. Use P(n) next to CPSR. The analyst's 4.55 is not supported at the 0.95 threshold |
| IM cruise efficiency, 2p=4 (machine only) | 97.05 % | 96.88 % | -0.2 points (2p=8 still cannot reach cruise) |
| WRSM 2p=4 / 2p=8 torque at 4500 rpm | 0.42 | 0.77 | no crossover in either; the deficit is smaller (0.77 instead of 0.42) |
| WRSM peak torque (Nm) / start grade | 2513 / 10.8 % | 2444 / 10.5 % | -3 % torque |
| WRSM cruise efficiency 2p=8 / 2p=4 (machine only) | 97.23 % / not reachable | 97.04 % / 96.08 % | -0.2 points; 2p=4 becomes reachable but is 1 point worse |
| WRSM CPSR with free I_d | 8.1 (capped) | 9.9 (capped at 9000 rpm) | unchanged in kind |
| PMSM start grade / cruise efficiency | 11.3 % / 96.29 % | 11.3 % / 96.45 % | none: per-unit parameters, no geometry; iron-loss law differs (-0.4 points at cruise) |

T03b (fixed-pole IM baselines): replace the permeance scaling (h/3b + 0.33)/2.0 by the energy-method slot permeance of the actual layer stack for every candidate slot (`spb_core.slot_lambdas` is 20 lines; the layers scale with slot height). All IMs lose high-speed power in proportion to their leakage reactance, so I expect the ranking to hold but the gap between pole-changing IM and the best fixed-pole IM to move by a few points; this has to be re-run, I did not.
T03c (HESM) and T08: take L_d, L_q, field copper and tau_f from `derived.wrsm`; do not scale the 8-pole inductances by k_w^2/p^2.

## 4. Targets for the analyst's re-run (my numbers on the agreed geometry, 350 kW current, the T04 points)

| point (350 kW current, analyst flux caps imposed) | analyst T (Nm) | simulator T (Nm) | err % | simulator with the analyst's leakage and R_r |
|---|---|---|---|---|
| IM 2p8 1000 rpm | 2948 | 2848 | -3.4 | 2858 (-3.0 %) |
| IM 2p8 3000 rpm | 626 | 418 | -33.3 | 631 (+0.9 %) |
| IM 2p8 4500 rpm | 285 | 188 | -33.8 | 287 (+1.0 %) |
| IM 2p4 2100 rpm | 1263 | 1199 | -5.0 | 1215 (-3.8 %) |
| IM 2p4 4500 rpm | 705 | 526 | -25.3 | 708 (+0.5 %) |
| IM 2p4 6000 rpm | 427 | 302 | -29.2 | 430 (+0.7 %) |
| WRSM 2p8 1000 rpm (free I_d, I_f) | 2932 | 2526 | -13.8 | - |
| WRSM 2p8 2100 rpm (free I_d, I_f) | 1622 | 1098 | -32.3 | - |
| WRSM 2p8 4250 rpm (free I_d, I_f) | 757 | 522 | -31.1 | - |
| WRSM 2p8 4500 rpm (free I_d, I_f) | 713 | 494 | -30.7 | - |
| WRSM 2p4 1000 rpm (free I_d, I_f) | 1309 | 1131 | -13.6 | - |
| WRSM 2p4 2100 rpm (free I_d, I_f) | 830 | 863 | +3.9 | - |
| WRSM 2p4 4250 rpm (free I_d, I_f) | 329 | 393 | +19.1 | - |
| WRSM 2p4 4500 rpm (free I_d, I_f) | 307 | 366 | +19.2 | - |

After the analyst adopts the geometry, the IM rows should land within about 5 % of the simulator column (the remaining difference at 1000 and 2100 rpm is the flux-cap and slip-grid treatment). Validation count on the agreed geometry: 51 of 124 numbers beyond 5 % against the analyst's *old* parameters; this is expected to fall once the analyst re-runs.

## Caveats

* No FEA. The slot layout (6.6 mm air above the conductors, 0.5 mm liners, 7.5 x 5.4 conductors) is a stated drawing; if the real winding fills the slot to the top the stator slot leakage falls by about 15 %, not by the factor 2.3 needed to reach the analyst's value.
* End-winding leakage, rotor slot permeance coefficient of the ring (0.3) and friction/windage are shared assumptions from T03, not verified.
* WRSM interpolar permeance (0.176 of the pole face value at 5 mm gap, from a 30 mm path) and the 54 x 55 mm field slot are assumptions; they set L_q and J_f.
* The B-H table is generic. The flux caps use the T03 rules (tooth tip 1.65 T, yoke 1.45 T) applied to true flux density.

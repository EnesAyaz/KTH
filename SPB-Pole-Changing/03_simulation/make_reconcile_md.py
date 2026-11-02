import json, datetime
G = json.load(open("../data/machine_geometry.json"))
D = G["derived"]
V = json.load(open("results/validation_points_R01.json"))
V0 = json.load(open("results/validation_points_T04_rerun.json"))
H = json.load(open("results/headline_R01.json"))
A = H["analyst_300kW"]
im = D["im_leakage"]; fc = D["flux_caps"]; wr = D["wrsm"]
u = lambda x: f"{x*1e6:.1f}"


def pct(a, b):
    return f"{100*(b/a-1):+.0f} %"


rows = []
for key in ("2p8", "2p4"):
    d = im[key]
    rows.append(f"| stator slot leakage L_slot, {key} (uH) | {u(d['L_slot_H']['analyst'])} | {u(d['L_slot_H']['agreed'])} | **mine** | Energy method on the agreed layout: 6 hairpin conductors stacked 36.9 mm deep in a 9 mm slot, 6.6 mm of air above them, 1.5 mm tooth tip over a 3 mm opening. The analyst's lambda 1.2/0.4 equals roughly a single 20 mm layer; a full 45 mm slot already gives h/(3w) = 1.67 for one fully fed layer. | {pct(d['L_slot_H']['analyst'], d['L_slot_H']['agreed'])} L_slot; this is the whole IM high-speed difference |")
for key in ("2p8", "2p4"):
    d = im[key]
    rows.append(f"| stator differential leakage, {key} (uH) | {u(d['L_diff_stator_H']['analyst'])} | {u(d['L_diff_stator_H']['agreed'])} | mine | same winding-function sum; differs only through g_eff (1.076 vs 1.3 mm) | small |")
rows.append(f"| end-winding leakage (uH) | {u(im['2p8']['L_end_H']['analyst'])} | {u(im['2p8']['L_end_H']['agreed'])} | keep (shared) | lambda_end 0.3 and l_end are not verified by either of us; needs a winding drawing | none |")
for key in ("2p8", "2p4"):
    d = im[key]
    rows.append(f"| total stator leakage L_sigma,s, {key} (uH) | {u(d['L_sigma_s_H']['analyst'])} | {u(d['L_sigma_s_H']['agreed'])} | **mine** | sum of the above | {pct(d['L_sigma_s_H']['analyst'], d['L_sigma_s_H']['agreed'])} |")
for key in ("2p8", "2p4"):
    d = im[key]
    rows.append(f"| rotor leakage referred, {key} (uH) | {u(d['L_sigma_r_referred_H']['analyst'])} | {u(d['L_sigma_r_referred_H']['agreed'])} | mine | lambda_bar 1.69 from the 7.0 x 21.4 mm bar and 1 mm bridge (analyst 1.5); area unchanged | {pct(d['L_sigma_r_referred_H']['analyst'], d['L_sigma_r_referred_H']['agreed'])} |")
rows.append(f"| cage resistance R_r referred, 2p8 / 2p4 (mOhm) | {im['2p8']['R_r_referred_ohm']['analyst']*1e3:.3f} / {im['2p4']['R_r_referred_ohm']['analyst']*1e3:.3f} | {im['2p8']['R_r_referred_ohm']['agreed']*1e3:.3f} / {im['2p4']['R_r_referred_ohm']['agreed']*1e3:.3f} | same | derived independently from the bar/ring dimensions; identical | none |")
rows.append(f"| air gap for L_m (mm) | 1.30 (Carter x saturation) | {G['airgap']['g_eff_carter_IM_m']*1e3:.3f} (Carter stator {G['airgap']['carter_stator']:.3f} x rotor {G['airgap']['carter_rotor_IM']:.3f}) | **mine** | k_sat must not sit in g_eff when the flux caps already model saturation. Agreed: unsaturated L_m(2p8) = {im['2p8']['L_m_linear_H']['agreed']*1e3:.3f} mH (analyst {im['2p8']['L_m_linear_H']['analyst']*1e3:.3f}), L_m(2p4) = {im['2p4']['L_m_linear_H']['agreed']*1e3:.3f} mH (analyst {im['2p4']['L_m_linear_H']['analyst']*1e3:.3f}); iron saturation via the table `derived.flux_caps.<mode>.magnetising_curve` (secant k_sat at the cap: {fc['2p8']['k_sat_secant_at_cap']:.3f} at 2p=8, {fc['2p4']['k_sat_secant_at_cap']:.3f} at 2p=4) | +20 % L_m, lower I_mag by the same factor; < 1 % on torque |")
for key in ("2p8", "2p4"):
    d = fc[key]
    rows.append(f"| rotor-flux cap psi_cap, {key} (mWb rms) | {d['psi_cap_rms_Wb']['analyst']*1e3:.1f} | {d['psi_cap_rms_Wb']['agreed']*1e3:.1f} | mine | limited by the stator yoke ({d['limiting']}) in both modes: B_y <= 1.45 T with stacking factor 0.95. Equivalent B_g1 caps {d['Bg1_cap_T_analytic']['yoke']:.3f} T (yoke), {d['Bg1_cap_T_analytic']['tooth']:.3f} T (tooth tip 1.65 T) against the analyst's {d['Bg1_cap_T_analytic']['analyst']:.3f} T | {pct(d['psi_cap_rms_Wb']['analyst'], d['psi_cap_rms_Wb']['agreed'])} |")
rows.append(f"| tooth geometry | 12.6 mm parallel | 12.6 mm at the bore, 18.5 mm at the root (parallel slots) | mine | B limit checked at the tip; iron MMF at one third height; teeth mass 87.8 kg (analyst 74.9), yoke 91.4 kg (96.3) with k_st | iron loss +- 5 % |")
rows.append("| stacking factor | none | 0.95 | mine | lamination | flux caps -5 % (already in the line above) |")
rows.append("| copper: R_coil, mass, current density | 2.155 mOhm, 62.9 kg, 7.7 / 6.6 A/mm2 | identical | same | 7.5 x 5.4 mm hairpin conductors (40.5 mm2), slot fill 0.60 of the gross slot, 0.86 of the insulated window | none |")
rows.append(f"| WRSM L_d, L_q at 2p=8 (pu) | 1.10 / 0.65 | {wr['L_d_pu_2p8']:.2f} / {wr['L_q_pu_2p8']:.2f} (g = {wr['chosen_g_mech_mm']:.0f} mm) | **mine** | the analyst's pair is a 'typical machine' input; with the IM gap this stator gives L_d = 5.8 pu. The pair is reached only by a larger gap, and L_q contains 0.36 pu of slot + end leakage so 0.65 needs a gap above 8 mm | the base of every WRSM result |")
rows.append(f"| WRSM L_d, L_q at 2p=4 (pu) | {4.805e-4/wr['pu_base']['L_base_H']:.2f} / {2.542e-4/wr['pu_base']['L_base_H']:.2f} | {wr['L_d_pu_2p4']:.2f} / {wr['L_q_pu_2p4']:.2f} | **mine** | MEC: in the ++-- pattern the rotor looks round to the 4-pole wave, so L_d <= L_q (inverse saliency, L_d falls with field because the stator yoke saturates). Scaling the 8-pole pair by k_w^2/p^2 keeps the saliency and is wrong in both axes | 2p=4 torque at high speed up to +20 % higher than the analyst |")
rows.append(f"| WRSM psi_f,max (mWb rms) | 49.2 (2p8), 43.9 (2p4 at I_f 0.655) | {wr['psi_f_rms_Wb_2p8']*1e3:.1f}, {wr['psi_f_rms_Wb_2p4']*1e3:.1f} (full field) | agree | within 2-8 %; the 2p=4 flux is limited by the stator yoke gradually, not by an I_f cap of 0.655 | small |")
rows.append(f"| WRSM field MMF per pole | 737 A-turns | {wr['F_pole_At']:.0f} A-turns | **mine** | B0 = 0.712 T over g_eff = {wr['g_eff_mm']:.2f} mm. 737 At is B0 over the IM gap | field copper uses the next line |")
rows.append(f"| WRSM field copper at full field | 4.0 kW (J not stated) | {wr['P_field_full_W']/1e3:.2f} kW at J_f = {wr['J_f_A_mm2']:.1f} A/mm2 | **mine** | 743 mm2 per coil side (half an interpolar slot 54 x 55 mm, fill 0.5), mean turn 1.0 m, rho 2.4e-8 | field loss in the efficiency points x 0.58 |")
rows.append(f"| WRSM tau_f, 2p8 / 2p4 | 45 ms | {wr['tau_f_s_2p8']*1e3:.0f} / {wr['tau_f_s_2p4']*1e3:.0f} ms | **mine** | 2 W_f / P_f from the permeance matrix with interpolar leakage; the 45 ms belongs to the IM gap. Forced (3x) reversal to 95 % takes about 0.65 tau_f, free-wheel + unforced about 6 tau_f + 20 ms | P1 sequence 0.29 s -> about 1.8 s; forced 0.05 s -> about 0.2 s |")
rows.append("| rotor yoke margin 2.0 / I_f cap 0.655 | yes | not needed | mine | rotor yoke 65 mm gives 1.0 T in the ++-- pattern; only the stator yoke limits | I_f cap goes away |")

tab = "| parameter | analyst | agreed (this file) | adopt | why | effect |\n|---|---|---|---|---|---|\n" + "\n".join(rows)

hd = []
imc, imm = H["IM"], A["IM_combined"]
hd.append(f"| IM with pole change: crossover 2p4 > 2p8 (rpm) | {A['IM_crossover_rpm']:.0f} | {imc['crossover_rpm']:.0f} | -15 % |")
hd.append(f"| IM peak torque (Nm) / max start grade at G = 9.80 | {imm['T_peak_Nm']:.0f} / {imm['max_start_grade_pct']:.1f} % | {imc['metrics_combined']['T_peak_Nm']:.0f} / {imc['metrics_combined']['max_start_grade_pct']:.1f} % | -4 % torque, -0.5 point grade (limit stays 12 %: G >= about 11.3 instead of 10.9) |")
hd.append(f"| IM power at 4500 rpm (kW) | {imm['P_at_vmax_W']/1e3:.0f} (at v_max) | {imc['metrics_combined']['P_at_4500_kW']:.0f} | -19 % |")
hd.append(f"| IM CPSR with pole change | {imm['CPSR']:.2f} | {imc['metrics_combined']['CPSR']:.2f} by the same 0.95 P_base rule (P_base {imc['metrics_combined']['P_base_kW']:.0f} kW at {imc['metrics_combined']['n_base_rpm']:.0f} rpm) | the metric is threshold-sensitive: the power after the crossover is 248 kW (91 % of P_base), below the 95 % band. Use P(n) next to CPSR. The analyst's 4.55 is not supported at the 0.95 threshold |")
hd.append(f"| IM cruise efficiency, 2p=4 (machine only) | {A['cruise']['IM_2p4']['eta']*100:.2f} % | {imc['cruise_2p4']['eta']*100:.2f} % | -0.2 points (2p=8 still cannot reach cruise) |")
wc = H["WRSM"]
hd.append(f"| WRSM 2p=4 / 2p=8 torque at 4500 rpm | {H['analyst_300kW']['WRSM_2p4_over_2p8_at_4500']:.2f} | {H['sim_WRSM_2p4_over_2p8_at_4500']:.2f} | no crossover in either; the deficit is smaller (0.77 instead of 0.42) |")
hd.append(f"| WRSM peak torque (Nm) / start grade | {A['WRSM_combined']['T_peak_Nm']:.0f} / {A['WRSM_combined']['max_start_grade_pct']:.1f} % | {wc['metrics_combined']['T_peak_Nm']:.0f} / {wc['metrics_combined']['max_start_grade_pct']:.1f} % | -3 % torque |")
hd.append(f"| WRSM cruise efficiency 2p=8 / 2p=4 (machine only) | {A['cruise']['WRSM_freeId_2p8']['eta']*100:.2f} % / not reachable | {wc['cruise_2p8']['eta']*100:.2f} % / {wc['cruise_2p4']['eta']*100:.2f} % | -0.2 points; 2p=4 becomes reachable but is 1 point worse |")
hd.append(f"| WRSM CPSR with free I_d | {A['WRSM_combined']['CPSR']:.1f} (capped) | {wc['metrics_combined']['CPSR']:.1f} (capped at 9000 rpm) | unchanged in kind |")
hd.append(f"| PMSM start grade / cruise efficiency | 11.3 % / {A['cruise']['PMSM_2p8']['eta']*100:.2f} % | {H['PMSM']['metrics']['max_start_grade_pct']:.1f} % / {H['PMSM']['cruise']['eta']*100:.2f} % | none: per-unit parameters, no geometry; iron-loss law differs (-0.4 points at cruise) |")
htab = "| headline (300 kW, same V and I limits) | analyst (T03 300 kW file) | simulator on the agreed geometry | effect |\n|---|---|---|---|\n" + "\n".join(hd)

tg = ["| point (350 kW current, analyst flux caps imposed) | analyst T (Nm) | simulator T (Nm) | err % | simulator with the analyst's leakage and R_r |", "|---|---|---|---|---|"]
for e in V["extra"]["IM_envelope"]:
    if e["cap_mode"] == "an_caps":
        tg.append(f"| {e['machine']} {e['n_rpm']} rpm | {e['T_analyst']:.0f} | {e['T_sim']:.0f} | {100*(e['T_sim']/e['T_analyst']-1):+.1f} | {e['T_sim_with_analyst_leakage']:.0f} ({100*(e['T_sim_with_analyst_leakage']/e['T_analyst']-1):+.1f} %) |")
for e in V["extra"]["WRSM_envelope"]:
    if e["config"] == "B":
        tg.append(f"| WRSM {e['mode']} {e['n_rpm']} rpm (free I_d, I_f) | {e['T_analyst_freeId']:.0f} | {e['T_sim']:.0f} | {100*(e['T_sim']/e['T_analyst_freeId']-1):+.1f} | - |")
ttab = "\n".join(tg)

n1 = [r for r in V["rows"] if r["err_pct"] is not None]
b1 = [r for r in n1 if abs(r["err_pct"]) > 5]
n0 = [r for r in V0["rows"] if r["err_pct"] is not None]
b0 = [r for r in n0 if abs(r["err_pct"]) > 5]

md = f"""# R01 reconcile: agreed geometry and what the analyst must change

Date {datetime.date.today()}. Author: simulator. Shared source of truth: `data/machine_geometry.json` (inputs in the top-level groups, quantities derived from them in `derived`; load with `json.load`, units are in the key names). Scripts: `03_simulation/write_geometry_inputs.py` (inputs), `compute_R01.py` (derived), `run_validation_R01.py`, `headline_R01.py`; results `results/validation_points_R01.json`, `results/headline_R01.json`.

## Corrections to T04 (my side, read first)

Two numerical resolution errors in my own T04 model inflated the disagreement. Both are fixed in `spb_core.py` and the T04 points re-run (`results/validation_points_T04_rerun.json`, same legacy assumptions as T04):

1. The IM magnetising curve was sampled with 12 A steps, which floored the flux cap to 0.046 / 0.038 Wb. With a fine grid the caps on the same geometry model are within 4 % of the analyst's (0.0517 vs 0.0535 and 0.0422 vs 0.0439 Wb). **Flag 3 of T04 was an artifact.**
2. The slip grid (6 rad/s steps) quantised the current-limited torque. With a log-spaced grid the low-speed IM torque agrees within 1.5 % (T04 rerun: 2p=8 at 1000 rpm +1.0 %, 2p=4 at 2100 rpm +1.5 %; the T04 file said -14 % and -19 %).

After the correction, the T04 rerun has {len(b0)} of {len(n0)} numbers beyond 5 % (T04 said 59 of 136). The remaining IM disagreement (-11 to -19 % at 3000-6000 rpm) goes to -0.5 to -0.1 % when the analyst's leakage is put into my model, so **the IM models have the same structure and differ only in stator slot leakage**. The WRSM disagreement is a different input (reactance basis), see the table.

## 1. The agreed drawing (summary; full file in `data/machine_geometry.json`)

* Stator: 48 slots, R_bore 165 mm, stack 360 mm, R_out 235 mm, yoke 25 mm, slot 9 x 45 mm with a 3 mm opening and 1.5 mm tip, coil pitch 7, 3 turns, double layer, stacking factor 0.95, M270-35A-like B-H table, parallel slots (teeth 12.6 mm at the bore, 18.5 mm at the root).
* Slot layout from the bottom: liner 0.5, bottom layer 17.7 (3 conductors 7.5 x 5.4 mm bare), separator 1.0, top layer 17.7, air/wedge 6.6, tip 1.5 = 45 mm. Copper area per turn 40.5 mm2, so R_coil, copper mass 62.9 kg and the T03b constraint are unchanged; gross slot fill 0.60 (0.86 of the insulated window), J = 7.7 A/mm2 at 310 A and 6.6 A/mm2 at 266 A (oil cooling, as T03).
* IM air gap 1.0 mm; Carter coefficients from the stator (3 mm) and rotor (1.5 mm) openings give g_eff = 1.076 mm; **no saturation factor in g_eff**.
* IM cage: 58 bars 7.0 x 21.4 mm (150 mm2), 1 mm bridge, copper rings 600 mm2 at 270 mm.
* WRSM rotor: 8 salient poles, arc 0.7, pole body 50 mm, interpolar slots 55 mm deep, shaft radius 40 mm, rotor yoke 65 mm. Air gap and field winding chosen in `derived.wrsm` (below).

## 2. Per-parameter reconcile

{tab}

### Which WRSM does a real 300 kW, 8-pole machine in this stator have?

{wr['verdict']}

Sweep (350 kW per-unit base, L_base = {wr['pu_base']['L_base_H']*1e6:.0f} uH; full table in `derived.wrsm_gap_sweep`):

| g (mm) | F (A-turns/pole) | J_f (A/mm2) | P_field (kW) | L_d / L_q 2p8 (pu) | L_d / L_q 2p4 (pu) | tau_f 2p8 / 2p4 (s) |
|---|---|---|---|---|---|---|
""" + "\n".join(f"| {s['g_mech_mm']:.0f} | {s['F_pole_At']:.0f} | {s['rotor']['J_f_A_mm2']:.1f} | {s['rotor']['P_field_full_W']/1e3:.2f} | {s['2p8']['L_d_pu']:.2f} / {s['2p8']['L_q_pu']:.2f} | {s['2p4']['L_d_pu']:.2f} / {s['2p4']['L_q_pu']:.2f} | {s['2p8']['tau_f_s']:.2f} / {s['2p4']['tau_f_s']:.2f} |" for s in D["wrsm_gap_sweep"]) + f"""

Reading: a real design is a 4-6 mm gap with 2.4-3.6 kA-turns per pole, 3-5 A/mm2 and 1.5-3.4 kW of field copper. Choice rule: smallest gap with L_d(2p=8) <= 1.6 pu and J_f <= 6 A/mm2, which gives {wr['chosen_g_mech_mm']:.0f} mm. The analyst's pair (1.10 / 0.65 pu) is not reachable below about 8 mm (6.7 A/mm2, 6.2 kW). The gap is the one free parameter of the WRSM; if the analyst prefers another, `compute_R01.py::wrsm_design(g)` returns every number.

## 3. Expected effect on the headline numbers (300 kW)

{htab}

T03b (fixed-pole IM baselines): replace the permeance scaling (h/3b + 0.33)/2.0 by the energy-method slot permeance of the actual layer stack for every candidate slot (`spb_core.slot_lambdas` is 20 lines; the layers scale with slot height). All IMs lose high-speed power in proportion to their leakage reactance, so I expect the ranking to hold but the gap between pole-changing IM and the best fixed-pole IM to move by a few points; this has to be re-run, I did not.
T03c (HESM) and T08: take L_d, L_q, field copper and tau_f from `derived.wrsm`; do not scale the 8-pole inductances by k_w^2/p^2.

## 4. Targets for the analyst's re-run (my numbers on the agreed geometry, 350 kW current, the T04 points)

{ttab}

After the analyst adopts the geometry, the IM rows should land within about 5 % of the simulator column (the remaining difference at 1000 and 2100 rpm is the flux-cap and slip-grid treatment). Validation count on the agreed geometry: {len(b1)} of {len(n1)} numbers beyond 5 % against the analyst's *old* parameters; this is expected to fall once the analyst re-runs.

## Caveats

* No FEA. The slot layout (6.6 mm air above the conductors, 0.5 mm liners, 7.5 x 5.4 conductors) is a stated drawing; if the real winding fills the slot to the top the stator slot leakage falls by about 15 %, not by the factor 2.3 needed to reach the analyst's value.
* End-winding leakage, rotor slot permeance coefficient of the ring (0.3) and friction/windage are shared assumptions from T03, not verified.
* WRSM interpolar permeance (0.176 of the pole face value at 5 mm gap, from a 30 mm path) and the 54 x 55 mm field slot are assumptions; they set L_q and J_f.
* The B-H table is generic. The flux caps use the T03 rules (tooth tip 1.65 T, yoke 1.45 T) applied to true flux density.
"""
open("reconcile_R01.md", "w", encoding="utf-8").write(md)
print(len(md))

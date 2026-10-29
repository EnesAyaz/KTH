import json, datetime
import numpy as np

V = json.load(open("results/validation_points.json"))
S = json.load(open("results/wrsm_pole_change_study.json"))
IM = json.load(open("results/im_pole_transition.json"))
WT = json.load(open("results/wrsm_pole_transition.json"))
WK = json.load(open("results/wrsm_pole_transition_ksweep.json"))
rows = V["rows"]
ex = V["extra"]


def fmt(x):
    if x is None:
        return "-"
    return f"{x:.4g}"


def line(r):
    e = r["err_pct"]
    flag = "" if e is None or abs(e) <= 5 else " **>5 %**"
    return f"| {r['machine']} | {r['point']} | {r['quantity']} | {fmt(r['analyst'])} | {fmt(r['sim'])} | {'-' if e is None else f'{e:+.1f}'}{flag} |"


hdr = "| machine | point | quantity | analyst | simulation | error % |\n|---|---|---|---|---|---|\n"
n_all = len([r for r in rows if r["err_pct"] is not None])
n_bad = len([r for r in rows if r["err_pct"] is not None and abs(r["err_pct"]) > 5])


def pick(machine, ptsub, quants):
    out = []
    for r in rows:
        if r["machine"] == machine and ptsub in r["point"] and r["quantity"] in quants:
            out.append(r)
    return out


sel = []
Q_ENV = ("torque_Nm", "V_rms_V (limit)", "I_rms_A (limit)", "I_rms_A at max T")
Q_EFF = ("I_rms_A", "V_rms_V", "P_cu_stator_W", "P_cu_rotor_W", "P_fe_W", "P_field_W", "eta_pct")
sel += pick("IM 2p8", "1000 rpm, envelope", Q_ENV)
sel += pick("IM 2p4", "4500 rpm, envelope", Q_ENV)
sel += pick("IM 2p4", "2100 rpm, envelope", ("torque_Nm",))
sel += pick("IM_2p8", "accel_1000rpm", Q_EFF)
sel += pick("IM_2p4", "cruise_85kmh", Q_EFF)
sel += pick("PMSM 2p8", "1000 rpm, envelope", ("torque_Nm", "I_rms_A at max T"))
sel += pick("PMSM 2p8", "4500 rpm, envelope", ("torque_Nm", "I_rms_A at max T"))
sel += pick("PMSM_2p8", "cruise_85kmh", Q_EFF)
sel += pick("PMSM_2p8", "grade_at_vmax", Q_EFF)
sel += pick("WRSM 2p8", "1000 rpm", ("torque_Nm",)) + pick("WRSM 2p8", "4250 rpm", ("torque_Nm",)) + pick("WRSM 2p8", "4500 rpm", ("torque_Nm",))
sel += pick("WRSM_freeId_2p8", "cruise_85kmh", Q_EFF)
sel += pick("WRSM 2p4", "4250 rpm", ("torque_Nm",)) + pick("WRSM 2p4", "2100 rpm", ("torque_Nm",))

imenv = ex["IM_envelope"]
t_att = "| machine | speed rpm | analyst T (Nm) | sim T, own leakage (Nm) | err % | sim T with analyst L_sigma,s, L_sigma,r, R_r (Nm) | err % |\n|---|---|---|---|---|---|---|\n"
for e in imenv:
    if e["cap_mode"] != "an_caps":
        continue
    t_att += f"| {e['machine']} | {e['n_rpm']} | {e['T_analyst']:.1f} | {e['T_sim']:.1f} | {100*(e['T_sim']/e['T_analyst']-1):+.1f} | {e['T_sim_with_analyst_leakage']:.1f} | {100*(e['T_sim_with_analyst_leakage']/e['T_analyst']-1):+.1f} |\n"
t_mec = "| machine | speed rpm | analyst T | sim (soft MEC saturation only) | err % |\n|---|---|---|---|---|\n"
for e in imenv:
    if e["cap_mode"] == "mec":
        t_mec += f"| {e['machine']} | {e['n_rpm']} | {e['T_analyst']:.1f} | {e['T_sim']:.1f} | {100*(e['T_sim']/e['T_analyst']-1):+.1f} |\n"
t_wr = "| mode | speed rpm | analyst T free I_d (Nm) | analyst T I_d=0 | sim config B (g x4) | err % vs free I_d | sim config A (g as IM) | I_f (B) | i_d / i_q (B, A peak) |\n|---|---|---|---|---|---|---|---|---|\n"
wb = {(e["mode"], e["n_rpm"]): e for e in ex["WRSM_envelope"] if e["config"] == "B"}
wa = {(e["mode"], e["n_rpm"]): e for e in ex["WRSM_envelope"] if e["config"] == "A"}
for (m, n), e in wb.items():
    a = wa[(m, n)]
    t_wr += f"| {m} | {n} | {e['T_analyst_freeId']:.1f} | {e['T_analyst_Id0']:.1f} | {e['T_sim']:.1f} | {100*(e['T_sim']/e['T_analyst_freeId']-1):+.1f} | {a['T_sim']:.1f} | {e['I_f_pu']:.2f} | {e['id_A']:.0f} / {e['iq_A']:.0f} |\n"

sc = S["scaling"]
var = S["variants"]
t_var = "| variant | 2p4/2p8 torque ratio at 1000 / 2100 / 4500 / 9000 rpm | crossover (2p4 > 2p8) | hybrid/2p8 torque at 4500 rpm | at 9000 rpm |\n|---|---|---|---|---|\n"
for k, v in var.items():
    sp = v["speed_rpm"]; r = v["T_ratio"]
    g = lambda n: np.interp(n, sp, r)
    t_var += f"| {k}: {v['desc']} | {g(1000):.2f} / {g(2100):.2f} / {g(4500):.2f} / {g(9000):.2f} | {'none up to 9000 rpm' if v['crossover_rpm'] is None else str(int(v['crossover_rpm']))+' rpm'} | {v['P_hybrid_over_P_2p8_at_4500']:.2f} | {v['P_hybrid_over_P_2p8_at_9000']:.2f} |\n"

eb = IM["best_schedule"]
t_im = "| case | schedule (t_d, t_f4, t_f2) s | min torque Nm | torque below 90 % for (s) | below 95 % until (s) | torque deficit Nm s | speed drop km/h (rpm) | peak I_rms / I_max | peak sum of mode currents A (limit 439) | voltage-limited share of time |\n|---|---|---|---|---|---|---|---|---|---|\n"
for k, b in eb.items():
    p = b["params"]
    t_im += f"| {k} (T_req {b['T_req_Nm']:.0f} Nm) | {p['t_d']}, {p['t_f4']}, {p['t_f2']} | {b['torque_min_Nm']:.0f} | {b['torque_gap_below90pct_s']:.3f} | {b['t_recover95_s']:.3f} | {b['torque_deficit_Nms']:.1f} | {b['speed_drop_kmh']:.3f} ({b['speed_drop_rpm']:.1f}) | {b['I_rms_peak_over_Imax']:.2f} | {b['I_peak_sum_env_A']:.0f} | {100*b['v_limited_fraction_of_time']:.0f} % |\n"
t_im2 = "| case | schedule | min torque Nm | below 90 % for (s) | speed drop km/h | peak I_rms / I_max |\n|---|---|---|---|---|---|\n"
for b in IM["cases"]:
    p = b["params"]
    t_im2 += f"| grade {b['grade_pct']:.0f} % | {p['t_d']}, {p['t_f4']}, {p['t_f2']} | {b['torque_min_Nm']:.0f} | {b['torque_gap_below90pct_s']:.3f} | {b['speed_drop_kmh']:.3f} | {b['I_rms_peak_over_Imax']:.2f} |\n"

t_w = "| field strategy | grade | field reversal: I_B crosses 0 at (s) / reaches 95 % at (s) | min torque Nm | time below 90 % (s) | speed drop km/h | peak I_rms / I_max |\n|---|---|---|---|---|---|---|\n"
for T in (WT, WK):
    for r in T["transitions"]:
        if r["gs"] != 4.0:
            continue
        t_w += f"| {r['strategy']} | {r['grade_pct']:.0f} % ({r['T_req_Nm']:.0f} Nm) | {r['t_I_B_zero_cross_s']:.2f} / {r['t_I_B_95pct_s']:.2f} | {r['torque_min_Nm']:.0f} | {r['torque_gap_below90pct_s']:.2f} | {r['speed_drop_kmh']:.3f} | {r['I_rms_max_over_Imax']:.2f} |\n"
tau = WT["tau_f"]
circ = [r for r in WT["harmonic"]["circulating"]]
t_c = "| rotor mode | order nu | speed rpm | f (Hz) | harmonic EMF (V rms per coil) | EMF / V_max | |Z| (ohm) | circulating current (A rms per coil) | share of I_max | copper loss, 48 coils (W) |\n|---|---|---|---|---|---|---|---|---|---|\n"
for r in circ:
    if r["n_rpm"] in (2100, 4500):
        t_c += f"| {r['mode']} | {r['nu']} | {r['n_rpm']} | {r['f_Hz']:.0f} | {r['E_rms_V']:.2f} | {r['E_over_Vmax']:.2f} | {r['Z_ohm']:.3f} | {r['I_circ_rms_A']:.1f} | {100*r['I_circ_over_Imax']:.1f} % | {r['P_cu_W']:.0f} |\n"
hh = WT["harmonic"]["rotor_field_harmonics_rel_B0"]
hl = WT["harmonic"]["harmonics"]
t_h = "| rotor mode | order | B_nu / B0 | winding factor | phase shift between the 3 coils of a module | zero-sequence? |\n|---|---|---|---|---|---|\n"
for h in hl:
    t_h += f"| {h['mode']} | {h['nu']} | {h['B_rel']:.3f} | {h['kw']:.3f} | {h['phase_shift_in_module_deg']:.0f} deg | {'yes' if h['zero_sequence'] else 'no'} |\n"

eK = S["enes_kx"]
md = f"""# T04 validation: independent simulation vs analyst (T03, 350 kW file)

Date {datetime.date.today()}. Simulator: `03_simulation/`. Analyst file checked: `02_analytics/results/torque_speed_envelope.json` (350 kW; the 300 kW rerun is not validated here).

## FLAGS (read first)

* **{n_bad} of {n_all} compared numbers differ by more than 5 %** (all rows in the appendix). The disagreement is not random. It has three identifiable causes:
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

{hdr}{chr(10).join(line(r) for r in sel)}

The "V_rms_V (limit)" and "I_rms_A (limit)" rows compare the voltage and current at the maximum-torque point. They equal the limits when the point is limit-bound. Where they do not (IM at 3000-4500 rpm, current about 130-165 A) the maximum torque is a breakdown/voltage limit and both models agree on that behaviour.

### IM envelope: where the difference comes from (analyst flux caps imposed on both)

{t_att}
With the analyst's stator and rotor leakage and R_r put into my model, the voltage-limited points (2p=8 at 3000 and 4500 rpm, 2p=4 at 4500 and 6000 rpm) are reproduced within -1.0 / -1.6 / -5.9 / -1.0 %. The points that remain 14-19 % low (2p=8 at 1000 rpm, 2p=4 at 2100 rpm) are the flux-limited ones, where my tooth/yoke cap (0.046 / 0.038 Wb against 0.0535 / 0.0439 Wb) is the cause. So the **IM model structure agrees; the numbers differ because of slot leakage (high speed) and the flux cap definition (low speed)**.

IM with soft MEC saturation only (no imposed caps):

{t_mec}

### WRSM envelope (free I_d and I_f)

{t_wr}
Config B (air gap x4) is used in the main table; config A (same air gap as the IM) is voltage-limited far below the analyst at every speed, because its L_d is about 4x the analyst's pu value. The WRSM 2p=4 torque at low speed is 1121 Nm (B) vs 1309 Nm (analyst).

### Efficiency points

Reachability: WRSM 2p=4 at cruise (4250 rpm, 352 Nm): analyst not reachable (329 Nm available), simulation reachable (419 Nm available; eta 95.5 %, I_f 0.85, i_d = -144 A, 121 A rms, 29.05 V, iron loss 1525 W, field loss 2890 W). WRSM 2p=8 at 4500 rpm / 600 Nm (grade point): analyst reachable, simulation not reachable (520 Nm available). Both are consequences of the different reactances, see flag 2.

## 2. WRSM pole change: independent check of "no gain"

**Verdict: the "no gain" conclusion holds for the stator as specified (3 turns per coil in both modes, 48 identical coils). It flips only if the 2p=4 mode works with about half the turns per coil (Dahlander-like series/parallel switching), and it does not flip from a thicker stator yoke alone.**

What I computed:

* **Magnetising inductance.** From the winding-function harmonic sum, L_m(2p=4)/L_m(2p=8) = {sc['Lm_winding_function_p2_over_p4']:.3f}, which equals the analyst's k_w^2/p^2 factor (kw 0.793 / 0.966; {sc['analyst_scaling_kw2_over_kw4_sq_times_4']:.3f}). The scaling law itself is correct for fixed turns. From the MEC (config B, small signal, I_f = 0), L_d(2p=4)/L_d(2p=8) = {sc['Ld_ratio_2p4_over_2p8_at_If0']:.2f} and L_q ratio = {sc['Lq_ratio_2p4_over_2p8_at_If0']:.2f} (leakage included). The L_d ratio is lower than 2.7 because with the ++-- pattern the rotor is almost round to the 4-pole stator wave: L_d and L_q are equal (0.48 mH both) in 2p=4 mode, so there is no reluctance torque, and L_d falls further to 0.14 mH at full field as the stator yoke saturates (yoke B_y = 1.95 T). The analyst keeps the 8-pole saliency in 2p=4 (L_d/L_q = 1.9; scale factors 2.34 on L_d and 2.10 on L_q), so it overstates the reluctance torque of the 2p=4 mode and overstates L_d, which is the opposite error for torque at high speed (L_q is what limits it).
* **Rotor MMF patterns.** I took [1 -1 1 -1 ...] (2p=8) and [1 1 -1 -1 ...] (2p=4) from `FE_MMF.m` on 8 poles of 0.7 pole arc, with group A = coils 0,3,4,7 fixed and group B = coils 1,2,5,6 reversed. Flux per unit field: psi_f(2p=4)/psi_f(2p=8) = {sc['psi_f_ratio_2p4_over_2p8']['If=0.3']:.2f} at I_f = 0.3 (analyst {sc['analyst_psi_f_ratio_same_If']:.2f}), falling to {sc['psi_f_ratio_2p4_over_2p8']['If=0.655']:.2f} at 0.655 and {sc['psi_f_ratio_2p4_over_2p8']['If=1.0']:.2f} at full field. The drop is the stator yoke saturating: the 2p=4 flux per pole is twice the 2p=8 flux in a 25 mm yoke. The absolute 2p=4 flux at the analyst's I_f cap of 0.655 is 0.041 Wb (analyst 0.044 Wb), so the yoke-limit conclusion agrees within 7 %.
* **Torque envelope with design variants** (config B, free I_d and I_f):

{t_var}
  The thicker yoke raises the low-speed 2p=4 torque (ratio 0.43 -> 0.50 at 1000 rpm) but not the high-speed ratio, because at high speed the 2p=4 mode is limited by the voltage drop across its large L_q (0.48 mH), not by saturation. Halving the turns of the 2p=4 mode divides the reactance by 4 and the flux linkage by 2: the 2p=4 mode then delivers 1.35-1.58 times the 2p=8 torque from 4250 rpm to 9000 rpm (crossover 4250 rpm; 3000 rpm with the thick yoke as well), while below 1500 rpm its torque is only 0.28-0.43 of the 2p=8 torque (that region is served by 2p=8 anyway). In SPB terms this means the turn count of a coil group would have to differ between modes, which the fixed 48-coil, 16-module wiring cannot do electronically. **Open design item**: a coil-to-module regrouping per mode (two coils per module leg in series, series pairs that are in phase in one mode and cancel in the other) needs either contactors or a redesigned winding.
* **Compared with the P2 draft machine** (`draft_parameters.json`: 10 kW, 4-pole 3000 rpm / 2-pole 6000 rpm, both at 100 Hz, eta 92.4 / 93.1 %, DC bus 400 V). Equal power at equal electrical frequency in both modes needs equal flux linkage and equal reactance per unit in the two modes, i.e. psi_f2/psi_f4 about 1 and x2/x4 about 1. With fixed turns the winding-function scaling gives psi ratio 2 (kw2/kw4)(c2/c4) and reactance ratio 4 (kw2/kw4)^2, which is 1.7 even for an illustrative kw2/kw4 = 0.65 (36 slots, pitch 8 of 9, belts regrouped for 2 poles; the draft does not state kw2; the same formulas give psi ratio 1.06). With that estimate the flux linkage could match but the reactance in the 2-pole mode would be 1.7 times higher at equal turns, so equal power at equal frequency needs fewer series turns in the 2-pole mode or a lower relative reactance than the SPB stator has. That is a statement about the draft, which is unverified (open-questions.md lists the 0.093 ohm field resistance and the 15.5 W / 30 W rotor loss as unresolved).

### Comparison with Enes's per-unit model (P5: `OPT-Bipolar-Field-Excitation/analysis/4_design_studies/torque_speed_switching.m`)

I ported the script to Python (`run_wrsm_study.py::enes_model`) and ran it with its own constants (kw4 = 0.808, kw2 = 0.760, alpha = 2/3, x_q4 = 0.31, field limit 429/381). Results:

| relation | dq model with winding halves series (4p) / parallel (2p) = Dahlander (turns halved in 2-pole mode) | same turns in both modes (analyst assumption, built with the same formulas) |
|---|---|---|
| k2 = psi_f2 / psi_f4 per unit field | {eK['dahlander_turns_halved']['k2']:.3f} | {eK['same_turns_both_modes']['k2']:.3f} (= 2 x k2) |
| x2 = 2-pole reactance (pu) | {eK['dahlander_turns_halved']['x2']:.3f} = {eK['dahlander_turns_halved']['x2_over_xq4']:.2f} x x_q4 | {eK['same_turns_both_modes']['x2']:.3f} = {eK['same_turns_both_modes']['x2_over_xq4']:.2f} x x_q4 (= 4 x x2) |
| low-speed torque ratio 2-pole/4-pole | {eK['dahlander_turns_halved']['T2_over_T4_low']:.2f} | {eK['same_turns_both_modes']['T2_over_T4_low']:.2f} |
| torque ratio at 2x the 4-pole base speed | {eK['dahlander_turns_halved']['T2_over_T4_at_2x_base']:.2f} | {eK['same_turns_both_modes']['T2_over_T4_at_2x_base']:.2f} |

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

{t_im}
The four fixed schedules tried first:

{t_im2}
* Flat road (248 Nm, speed holding): the best schedule (slow torque hand-over, 0.25 s) dips to 80 % of the requested torque and is below 90 % for 56 ms; the speed drop is 0.002 km/h. Fast schedules are worse: 10 ms ramps give a 134 ms gap and a torque reversal to -116 Nm, because the new flux is built while the old flux still induces a voltage.
* 2 % grade (677 Nm): under the voltage limit the 2p=4 flux needs about 0.5 s to reach the 0.038 Wb that the load requires. The torque is below 90 % for about 0.5 s in every schedule tried, the speed drop is 0.4-0.5 km/h (21-25 rpm), which is small for a 40 t truck, but all four 2 % schedules show a negative torque spike (-53 to -218 Nm in the fixed schedules, -62 Nm in the best one) that the controller would have to avoid by a torque-hand-over rule better than the one used here.
* Current: in the best schedules the peak coil current is 0.62-0.66 of I_max = 310 A rms (rms of both modes combined). Three of the four fixed flat-road schedules also stay below 1.0 I_max; the 20 ms schedule reaches 1.004 I_max at the 439 A amplitude budget.
* Reading: the pole change is a 60 ms (light load) to 500 ms (2 % grade) torque gap, comparable with a gear shift. The cause is the voltage budget, not the current. The analyst's estimate for the 2p=4 flux build-up (85 ms with forced i_d) assumed the full voltage was available; it is not while the residual 2p=8 flux (time constant about 0.5 s) is still in the machine.

### WRSM field reversal

Field circuit: 8 pole coils, flux per pole from the permeance matrix (zero net flux) plus interpolar leakage (assumed 45 mm x 20 mm slot between poles), group copper 4 kW at full I_f (shared input). Stator side: the fundamental flux linkage of the p=4 and p=2 modes follows the instantaneous pole currents by superposition of single-pole MEC solutions, scaled to the saturated pure patterns. Stator torque capability is optimised at each instant over the two modes' d/q currents under the shared voltage and current budgets (quasi-static: stator electrical time constants of 1-5 ms are neglected).

Field time constants (stored energy x 2 / 4 kW):

| configuration | tau_f, 2p=8 pattern | tau_f, 2p=4 pattern | pole-leakage factor |
|---|---|---|---|
| air gap as IM (config A, g_eff 1.3 mm) | {tau['gs1']['2p8']['tau_f_s']*1000:.0f} ms | {tau['gs1']['2p4']['tau_f_s']*1000:.0f} ms | {tau['gs1']['2p8']['leak_factor']:.2f} / {tau['gs1']['2p4']['leak_factor']:.2f} |
| air gap x4 (config B, needed for the analyst's L_d) | {tau['gs4']['2p8']['tau_f_s']*1000:.0f} ms | {tau['gs4']['2p4']['tau_f_s']*1000:.0f} ms | {tau['gs4']['2p8']['leak_factor']:.2f} / {tau['gs4']['2p4']['leak_factor']:.2f} |

The analyst's tau_f = 45 ms uses the 1.3 mm gap energy (68.5 J, same as mine) and a 1.3 leakage factor; my interpolar-leakage estimate is 1.13 at that gap (39 ms). **But the analyst's L_d corresponds to a gap about 4x larger, and the field energy then grows 4x: tau_f is 0.17-0.21 s. The analyst's reactances and field time constant are not mutually consistent.**

Transition results (config B, 2100 rpm, 2p=8 -> 2p=4, requested torque = road load):

{t_w}
* **Free-wheel + 20 ms blanking, unforced (P1 sequence):** with tau_f of 0.17-0.21 s the group-B current passes zero at 0.60 s and reaches 95 % of the new polarity at 1.16 s. With forced 3x field voltage the reversal takes 0.13 s (zero crossing 0.06 s). A gradual k-sweep over 0.4 s (P4 pattern [1 k -k -1], k from -1 to +1, forced voltage) reaches 95 % at 0.40 s. With the IM-sized air gap (config A, tau_f 36-39 ms) the same sequences take 0.25 s (free-wheel + unforced) and 0.03 s (forced), consistent with the analyst's 0.29 s and 0.05 s.
* **The torque does not drop out in any strategy** in my quasi-static model: while group B passes through zero the rotor pattern is [1 0 0 -1 ...], which carries both the p=4 and the p=2 harmonic, and the 48-coil stator is driven in both modes at once. The torque capability stays above 90 % of the requested torque (min 248 Nm of 248 flat, 620-624 Nm of 677 on the 2 % grade). The speed drop is 0.002-0.003 km/h. The price is that the stator must run two modes at once with a shared voltage budget (peak stator current {max(r['I_rms_max_over_Imax'] for r in WT['transitions'] if r['gs']==4.0)*100:.0f} % of I_max), and a smooth hand-over of the d-axis reference as k moves. The simulation does not include the field-circuit induction from the stator currents (damping) nor the eddy currents in a solid rotor, which would slow the field; the margin is large for flat road, and thin (about 8 %) for the 2 % grade.
* With the air gap as in the IM (config A) the 2p=4 mode cannot carry the 677 Nm grade load at 2100 rpm at all (294 Nm available), so the grade case is not meaningful there.

## 4. 10th-order rotor harmonic in 2p=4 mode

Spatial harmonics of the rotor field for the two patterns (0.7 pole arc, B_nu / B0, FFT amplitude of the pole pattern) and the module test (phase shift of the three coils j, j+16, j+32 is 120 deg x nu):

{t_h}
**The analyst's note is correct: nu = 10 is not zero-sequence in a module (phase shift 120 deg, a balanced set), while nu = 6 (and 12) is (phase shift 0).** The 10th harmonic of the 2p=4 rotor drives a balanced three-phase set of EMFs in every module, which the isolated neutral does not block.

Magnitude (per coil, field at full I_f, impedance from the 48-coil model at that order, no compensation by the inverter):

{t_c}
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

{hdr}{chr(10).join(line(r) for r in rows)}
"""
open("validation.md", "w", encoding="utf-8").write(md)
print("written", len(md))

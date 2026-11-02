import json, math, datetime
A3 = json.load(open("results/confirm_H10_mec_Q48.json"))
A5 = json.load(open("results/confirm_H10_mec_Q80.json"))
BAL3 = json.load(open("results/confirm_H10_balance_Q48.json"))
BAL5 = json.load(open("results/confirm_H10_balance_Q80.json"))
SCH3 = json.load(open("results/h10_schedule_search_Q48.json"))
SCH5 = json.load(open("results/h10_schedule_search_Q80.json"))
H11 = json.load(open("../02_analytics/results/screen_H11.json"))["H11s"]["runs"]
H10 = json.load(open("../02_analytics/results/screen_H10.json"))
V0 = 75.0


def case(A, tag):
    for c in A["cases"]:
        if c["tag"] == tag:
            return c
    return None


def amp_v(Aw, f, C):
    return Aw / (V0 * 2 * math.pi * f * C)


# ---- table 1: overlapped m=3 and m=5
def row(c, label):
    m, l = c["mec"], c["lin"]
    r1, r2 = m["C_1.00mF"], m["C_2.88mF"]
    return (f"| {label} | {m['mean_cell_power_W']:.0f} | {m['pulsation_peak_W']:.0f} ({l['pulsation_peak_W']:.0f}) | {m['pulsation_main_Hz']:.0f} | {m['pulsation_over_mean']:.2f} | "
            f"{m['C_for_pm5pct_mF']:.1f} / {m['C_for_pm10pct_mF']:.1f} | {amp_v(m['pulsation_peak_W'], m['pulsation_main_Hz'], 1e-3):.0f} / {amp_v(m['pulsation_peak_W'], m['pulsation_main_Hz'], 2.88e-3):.0f} | "
            f"{r1['v_min_V']:.0f}..{r1['v_max_V']:.0f} / {r2['v_min_V']:.0f}..{r2['v_max_V']:.0f} | {c.get('torque_min_over_request', float('nan')):.2f} | {c.get('dq_result', {}).get('torque_gap_below90pct_s', float('nan')):.2f} |")


hdr1 = ("| case | mean cell power (W) | peak per-cell pulsation, MEC (linear) (W) | at (Hz) | pulsation / mean | C for +-5 % / +-10 % ripple (mF) | ripple amplitude at 1.0 / 2.88 mF (V pk) | cell voltage range 1.0 / 2.88 mF (V) | min torque / request | time below 90 % (s) |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n")
t1 = hdr1
for tag, lab in (("overlapped_0pct", "m = 3 overlapped, flat road"), ("overlapped_2pct", "m = 3 overlapped, 2 % grade")):
    t1 += row(case(A3, tag), lab) + "\n"
for tag, lab in (("overlapped_0pct", "m = 5 overlapped, flat road"), ("overlapped_2pct", "m = 5 overlapped, 2 % grade")):
    t1 += row(case(A5, tag), lab) + "\n"
for tag, lab in (("ideal_linear_amplitude", "ideal crossfade, psi and i linear in x"), ("ideal_constant_torque", "ideal crossfade, torque-conserving (sqrt)")):
    c3 = case(A3, tag); c5 = case(A5, tag)
    t1 += row(c3, "m = 3 " + lab).replace("nan", "-") + "\n"
    t1 += row(c5, "m = 5 " + lab).replace("nan", "-") + "\n"

# ---- crossfade fits
tf = "| case | x defined as | kappa/4 = peak of kappa x(1-x) (W) | R^2 | measured peak (W) | x at peak |\n|---|---|---|---|---|---|\n"
for A, nm in ((A3, "m = 3"),):
    for tag in ("ideal_linear_amplitude", "ideal_constant_torque", "overlapped_0pct", "overlapped_2pct"):
        c = case(A, tag)
        for xn, f in c["crossfade_fit"].items():
            tf += f"| {nm} {tag} | {xn} | {f['kappa_over_4']:.0f} | {f['R2']:.2f} | {f['peak_A_W']:.0f} | {f['x_at_peak']:.2f} |\n"

# ---- m=5 residual
def top_orders(c, n=5):
    d = c["dpsi_order_peaks_V"]
    items = sorted(d.items(), key=lambda kv: -kv[1])[:n]
    return ", ".join(f"p={k}: {v:.2f}" for k, v in items)


t5 = "| case | MEC pulsation (W) | at (Hz) | lines (W) at 70 / 140 / 210 / 280 / 350 / 420 Hz | peak flux-derivative amplitude per order (V per coil) |\n|---|---|---|---|---|\n"
for tag in ("overlapped_0pct", "overlapped_2pct", "ideal_linear_amplitude", "ideal_constant_torque"):
    c = case(A5, tag)
    l = c["mec"]["amp_by_freq_W"]
    t5 += f"| m = 5 {tag} | {c['mec']['pulsation_peak_W']:.0f} | {c['mec']['pulsation_main_Hz']:.0f} | " + " / ".join(f"{l[k]:.0f}" for k in ("70", "140", "210", "280", "350", "420")) + f" | {top_orders(c)} |\n"
c3 = case(A3, "overlapped_0pct")
t5 += f"| (m = 3 overlapped flat, for scale) | {c3['mec']['pulsation_peak_W']:.0f} | {c3['mec']['pulsation_main_Hz']:.0f} | " + " / ".join(f"{c3['mec']['amp_by_freq_W'][k]:.0f}" for k in ("70", "140", "210", "280", "350", "420")) + f" | {top_orders(c3)} |\n"

# ---- sequential
ts = "| grade | trigger: psi_r8 below | trigger time (s) | time below 90 % (s) | min torque (Nm) | peak pulsation MEC (W) | v_p4 x i_p2 term (W) | C for +-5 % / +-10 % (mF) | ripple pp at 1.0 / 2.88 mF (V) | I_rms peak / I_max |\n|---|---|---|---|---|---|---|---|---|---|\n"
for c in A3["cases"]:
    if c["tag"].startswith("sequential"):
        m = c["mec"]
        ts += (f"| {c['grade_pct']:.0f} % | {100*c['seq_eps']:.0f} % | {c['trigger_t'] if c['trigger_t'] is None else round(c['trigger_t'], 3)} | {c['dq_result']['torque_gap_below90pct_s']:.3f} | "
               f"{c['dq_result']['torque_min_Nm']:.0f} | {m['pulsation_peak_W']:.0f} | {c['product_terms_peak_W']['v_p4_x_i_p2']:.0f} | {m['C_for_pm5pct_mF']:.1f} / {m['C_for_pm10pct_mF']:.1f} | "
               f"{m['C_1.00mF']['ripple_pp_V']:.1f} / {m['C_2.88mF']['ripple_pp_V']:.1f} | {c['dq_result']['I_rms_peak_over_Imax']:.2f} |\n")

# ---- H11s
import os
sets = [("350 kW (310 A), 1 ms loop", A3)]
for fn, lab in (("results/confirm_H10_mec_Q48_h11s_300kW.json", "300 kW (266 A), 1 ms loop"), ("results/confirm_H10_mec_Q48_h11sfast_300kW.json", "300 kW (266 A), 0.25 ms loop")):
    if os.path.exists(fn):
        sets.append((lab, json.load(open(fn))))
th = ("| limits / current loop | case | C (mF) | time below 90 % (s) | below 95 % until (s) | min torque (Nm) | reversal | peak cell ripple at C (V pk, % of 75 V) | peak pulsation (W) | peak I_rms (A) | analyst linear model: gap / ripple |" + chr(10) +
      "|---|---|---|---|---|---|---|---|---|---|---|" + chr(10))
H11ROWS = []
for lab, A in sets:
    for c in A["cases"]:
        if c["tag"].startswith("H11s"):
            m = c["mec"]
            Cmf = float(c["tag"].split("_C")[1].replace("mF", ""))
            key = "C_1.00mF" if Cmf < 2 else "C_2.88mF"
            pk = m[key]["ripple_pp_V"] / 2
            an = H11["flat_2.9mF_10pct" if c["grade_pct"] == 0 else "grade_2pct_2.9mF_10pct"]
            rev = "yes" if c["dq_result"]["torque_min_Nm"] < -0.02 * c["dq_result"]["T_req_Nm"] else "no"
            imax = A["meta"].get("I_max_A", 310.44)
            H11ROWS.append((lab, c, pk))
            th += (f"| {lab} | {c['grade_pct']:.0f} % grade | {Cmf:.2f} | {c['dq_result']['torque_gap_below90pct_s']:.3f} | {c['dq_result']['t_recover95_s']:.3f} | {c['dq_result']['torque_min_Nm']:.0f} ({c['torque_min_over_request']:.2f}) | {rev} | "
                   f"{pk:.1f} ({100*pk/V0:.1f} %) | {m['pulsation_peak_W']:.0f} | {c['dq_result']['I_rms_peak_over_Imax']*imax:.0f} | {an['torque_gap_below90pct_s']:.3f} s / {an['ripple_max_pct']:.1f} % |" + chr(10))

# ---- balancing
def baltab(B):
    s = "| b | (a - b) mod m | W per A rms | % of cell power per A | I_b for 5 % (A rms) | share of I_a | rotor Cu (W) | stator Cu (W) | V_b (V rms) | torque (Nm) |\n|---|---|---|---|---|---|---|---|---|---|\n"
    for c in B["cases"]:
        if c["W_per_A_rms"] > 1e-3:
            k = c["cost_for_5pct"]
            s += f"| {c['b']} | {c['a_minus_b_mod_m'] if 'a_minus_b_mod_m' in c else c['a_minus_b_mod_3']} | {c['W_per_A_rms']:.1f} | {c['percent_of_cell_power_per_A']:.2f} | {c['I_b_for_5pct_A_rms']:.1f} | {100*c['I_b_over_I_a']:.1f} % | {k['rotor_cu_W']:.1f} | {k['stator_cu_W']:.1f} | {k['V_b_rms_V']:.2f} | {k['torque_Nm']:.3f} |\n"
        else:
            s += f"| {c['b']} | {c['a_minus_b_mod_m'] if 'a_minus_b_mod_m' in c else c['a_minus_b_mod_3']} | 0 | 0 | - | - | - | - | - | - |\n"
    return s



def sq(g, e):
    return case(A3, f"sequential_{g}pct_eps{e}")


seq_txt = (f"Sequential m = 3 costs a torque gap but needs little capacitance: flat road {min(sq(0,e)['dq_result']['torque_gap_below90pct_s'] for e in (0.02,0.05,0.15,0.3)):.2f}-{max(sq(0,e)['dq_result']['torque_gap_below90pct_s'] for e in (0.02,0.05,0.15,0.3)):.2f} s, 2 % grade "
           f"{min(sq(2,e)['dq_result']['torque_gap_below90pct_s'] for e in (0.02,0.05,0.15,0.3)):.2f}-{max(sq(2,e)['dq_result']['torque_gap_below90pct_s'] for e in (0.02,0.05,0.15,0.3)):.2f} s depending on the trigger level, with no torque reversal on flat road (min {sq(0,0.02)['dq_result']['torque_min_Nm']:.0f} Nm) and a small one on the grade ({sq(2,0.02)['dq_result']['torque_min_Nm']:.0f} Nm). "
           f"The residual V8 x I4 term (EMF of the left-over 8-pole flux against the 4-pole current) is {sq(0,0.02)['mec']['pulsation_peak_W']:.0f} W when the 4-pole flux is built after the 8-pole flux has fallen below 2 %, "
           f"{sq(0,0.05)['mec']['pulsation_peak_W']:.0f} W at 5 %, {sq(0,0.15)['mec']['pulsation_peak_W']:.0f} W at 15 % and {sq(0,0.3)['mec']['pulsation_peak_W']:.0f} W at 30 % (about proportional to the residual flux). "
           f"At 1.0 mF the cell ripple is {sq(0,0.02)['mec']['C_1.00mF']['ripple_pp_V']/2:.1f} V pk at 2 % and {sq(0,0.15)['mec']['C_1.00mF']['ripple_pp_V']/2:.0f} V pk at 15 %, so the trigger must be 5 % or lower for 1-3 mF cells.")
h_by = {}
for lab, c, pk in H11ROWS:
    h_by.setdefault(lab, {})[(c["grade_pct"], round(float(c["tag"].split("_C")[1].replace("mF", "")), 2))] = (c, pk)
h11_lines = []
for lab, d in h_by.items():
    f1, f3, g1, g3 = d.get((0.0, 1.0)), d.get((0.0, 2.88)), d.get((2.0, 1.0)), d.get((2.0, 2.88))
    if f1 and g1:
        h11_lines.append(f"{lab}: gap {f1[0]['dq_result']['torque_gap_below90pct_s']:.3f} s flat / {g1[0]['dq_result']['torque_gap_below90pct_s']:.3f} s on the 2 % grade, minimum torque {f1[0]['dq_result']['torque_min_Nm']:.0f} / {g1[0]['dq_result']['torque_min_Nm']:.0f} Nm, "
                         f"peak cell ripple {100*f1[1]/V0:.1f} % / {100*g1[1]/V0:.1f} % at 1.0 mF and {100*f3[1]/V0:.1f} % / {100*g3[1]/V0:.1f} % at 2.88 mF, peak current {f1[0]['dq_result']['I_rms_peak_over_Imax']*(c.get('meta',{}).get('I_max_A',0) if False else (310.44 if '350' in lab else 266.09)):.0f} A rms")
h11_txt = "; ".join(h11_lines)

md = f"""# H10 confirmation (independent, nonlinear MEC + DC cells)

Date {datetime.date.today()}. Simulator. Inputs: `data/machine_geometry.json` (agreed geometry, R01), IM at 2100 rpm, flat road (248 Nm) and 2 % grade (677 Nm). Overlapped, sequential and ideal cases use the T03 350 kW current limit (310 A rms per leg, as T04); the H11s runs are also given at 300 kW (266 A) to match the analyst's H11 file. Files: `run_h10_mec.py` (MEC replay, ideal crossfade, sequential, H11s), `run_h10_balance.py`, `run_h10_sched.py`, `run_h10.py` (first, linear version); results `results/confirm_H10_mec_Q48.json`, `confirm_H10_mec_Q80.json`, `confirm_H10_balance_Q48.json`, `confirm_H10_balance_Q80.json`, `h10_schedule_search_Q*.json`, `confirm_H10_handover_*.json`.

## Method (own equations)

* **Machine and handover**: the two-mode IM model of T04 (orders p = 4 and p = 2 of the same coils, rotor-flux-oriented control, shared voltage and current budget). A controller error found during this work (demagnetising d current blocked at zero flux reference) is fixed; the T04 transition numbers are corrected in `validation.md`.
* **Nonlinear MEC replay**: the magnetising current of each mode (i_s + referred rotor current) is rebuilt into per-coil currents at 0.4 ms steps and passed through the MEC with the B-H iron (`spb_core.mec_solve`, smooth rotor). Coil voltage = R i + L_sigma di/dt + d psi_k/dt with the MEC flux linkages, so cross saturation between the two orders and every combination order is included. The cage reaction to saturation-generated orders is not modelled, so combination-order pulsations are an upper bound.
* **Cell power**: P_j(t) = sum over the coils of module j of v_k i_k (m = 3 coils per module, Q = 48; m = 5 coils, Q = 80, y = 11, same per-unit machine, 16 modules in both). The pulsation is read from P_j minus the mean over the 16 cells (removes the common mean power), by sliding demodulation at multiples of 70 Hz (window 1/70 s).
* **DC cells**: 16 series cells on a stiff 1200 V link: C dv_j/dt = (P_mean - P_j)/V_0, V_0 = 75 V. A constant-power cell on a fixed stack current is open-loop unstable (C V^2/P about 1.6 ms at 1 mF), so the reported ripple is the linearised open-loop value and the drift is the uncontrolled integral of the imbalance; the real system needs the cell-voltage balancing loop of item 4 for the slow part. Ripple amplitude is also given as A/(V_0 w C).
* **Spatial condition** (derived here): the product of order a and order b over the m coils of a module gives m/2 Re[V I e^(-j(a +- b) alpha_j)] if (a +- b) is a multiple of m and 0 otherwise. For m = 3 any two orders that are not multiples of 3 satisfy a = +-b (mod 3), so the condition always holds; for prime m >= 5 it holds only if a = +-b (mod m). The pair (4, 2) gives a + b = 6 (multiple of 3, pulsation at f_4 + f_2 = 210 Hz at 2100 rpm) and 4 +- 2 = 6, 2 (not multiples of 5).

## Verdict

* **Confirmed (m = 3).** The overlapped IM handover pulsates at 210 Hz with {case(A3,'overlapped_0pct')['mec']['pulsation_peak_W']/1e3:.1f} kW per cell on flat road and {case(A3,'overlapped_2pct')['mec']['pulsation_peak_W']/1e3:.1f} kW on the 2 % grade (analyst: {H10['transition_IM_handover']['m3']['P_pulse_amplitude_W']:.0f} W), {case(A3,'overlapped_0pct')['mec']['pulsation_over_mean']:.1f}x the cell mean power. Capacitance for +-5 % ripple: {case(A3,'overlapped_0pct')['mec']['C_for_pm5pct_mF']:.0f} mF (analyst 22.8 mF), for +-10 %: {case(A3,'overlapped_0pct')['mec']['C_for_pm10pct_mF']:.0f} mF. The 1.0 and 2.88 mF cells would see {amp_v(case(A3,'overlapped_0pct')['mec']['pulsation_peak_W'],210,1e-3):.0f} V and {amp_v(case(A3,'overlapped_0pct')['mec']['pulsation_peak_W'],210,2.88e-3):.0f} V amplitude on a 75 V cell. The nonlinear MEC changes the pulsation by less than 3 % relative to the linear model (iron saturation is moderate at 2100 rpm).
* **Confirmed, with a correction (m = 5).** On the 80-coil stator the product terms vanish and what is left is the saturation residual: {case(A5,'overlapped_0pct')['mec']['pulsation_peak_W']:.0f} W (flat) and {case(A5,'overlapped_2pct')['mec']['pulsation_peak_W']:.0f} W (2 %), i.e. {100*case(A5,'overlapped_0pct')['mec']['pulsation_peak_W']/case(A3,'overlapped_0pct')['mec']['pulsation_peak_W']:.1f} % and {100*case(A5,'overlapped_2pct')['mec']['pulsation_peak_W']/case(A3,'overlapped_2pct')['mec']['pulsation_peak_W']:.1f} % of the m = 3 value, at 350 Hz. It needs about 0.1 mF. **But the torque is not kept at 90 %: the best of 64 overlapped schedules on the m = 5 stator keeps {SCH5['grade_0pct'][0]['min_over_request']:.2f} of the request on flat road and {SCH5['grade_2pct'][0]['min_over_request']:.2f} on the 2 % grade** (m = 3: {SCH3['grade_0pct'][0]['min_over_request']:.2f} and {SCH3['grade_2pct'][0]['min_over_request']:.2f}). The dip comes from the shared voltage budget (the residual 8-pole EMF), not from the cells, so m = 5 removes the pulsation but not the torque dip.
* **Sequential m = 3 (addition 3).** {seq_txt}
* **H11s in the nonlinear MEC with DC cells.** {h11_txt}. Analyst's linear model: 0.143 s flat, 0.181 s on the grade, no reversal, ripple at most 5.8 %.

## 1. Overlapped handover, pulsation and cell voltage

{t1}
Ripple amplitude is A/(V_0 w C) with the main pulsation line; the cell-voltage range is the open-loop linearised cell voltage over the whole handover including the uncontrolled integral of the imbalance. Ranges outside about 20-80 V are not admissible for a 75 V cell.

## 2. True crossfade envelope (addition 1)

For the m = 3 sum-frequency term the exact kernel is A(t) = 1.5 |V_4 I_2 + V_2 I_4| (checked: measured / kernel = {case(A3,'overlapped_0pct')['kernel_check']['ratio']:.2f} flat, {case(A3,'overlapped_2pct')['kernel_check']['ratio']:.2f} 2 %, ideal laws {case(A3,'ideal_linear_amplitude')['kernel_check']['ratio']:.2f} / {case(A3,'ideal_constant_torque')['kernel_check']['ratio']:.2f}). The x(1-x) law holds only when both flux linkage and current of each mode scale linearly with the crossfade variable:

{tf}
* Ideal linear crossfade (psi and i linear in x): R^2 = {case(A3,'ideal_linear_amplitude')['crossfade_fit']['share']['R2']:.2f}, peak {case(A3,'ideal_linear_amplitude')['crossfade_fit']['share']['peak_A_W']:.0f} W at x = {case(A3,'ideal_linear_amplitude')['crossfade_fit']['share']['x_at_peak']:.2f}, C {case(A3,'ideal_linear_amplitude')['mec']['C_for_pm5pct_mF']:.1f} mF for +-5 %, {case(A3,'ideal_linear_amplitude')['mec']['C_for_pm10pct_mF']:.1f} mF for +-10 %. This is the lower bound.
* If the torque is to stay constant during the crossfade (amplitudes scale as sqrt(x), sqrt(1-x)) the product is sqrt(x(1-x)) and the peak doubles: {case(A3,'ideal_constant_torque')['mec']['pulsation_peak_W']:.0f} W, C {case(A3,'ideal_constant_torque')['mec']['C_for_pm5pct_mF']:.1f} / {case(A3,'ideal_constant_torque')['mec']['C_for_pm10pct_mF']:.1f} mF.
* The real handover is not a clean crossfade: both modes are driven near the voltage and current limit while the 8-pole EMF is still present, so the envelope peaks at {case(A3,'overlapped_0pct')['mec']['pulsation_peak_W']:.0f} W (flat) and {case(A3,'overlapped_2pct')['mec']['pulsation_peak_W']:.0f} W (2 %), 2-4x the ideal values, and x(1-x) is a poor predictor (R^2 {case(A3,'overlapped_0pct')['crossfade_fit']['torque']['R2']:.2f} with the torque share).

## 3. m = 5: saturation residual (addition 2)

{t5}
The residual that is left for m = 5 is generated by the shared iron (order 6 = 4 + 2 flux derivative peaks at {case(A5,'overlapped_0pct')['dpsi_order_peaks_V']['6']:.2f} V per coil, {100*case(A5,'overlapped_0pct')['dpsi_order_peaks_V']['6']/case(A5,'overlapped_0pct')['dpsi_order_peaks_V']['4']:.1f} % of the order-4 term; order 6 against the order-4 current gives 6 + 4 = 10, a multiple of 5, at 210 + 140 = 350 Hz, which is the line seen): the MEC flux-derivative contains orders that are combinations of 4 and 2 (6, 8, ...), and some of their products with the 4 and 2 currents are multiples of 5 (for example order 6 against order 4 at the sum frequency). Size: {case(A5,'overlapped_0pct')['mec']['pulsation_peak_W']:.0f}-{case(A5,'overlapped_2pct')['mec']['pulsation_peak_W']:.0f} W at 350 Hz for the handovers, {case(A5,'ideal_constant_torque')['mec']['pulsation_peak_W']:.0f} W for the ideal torque-conserving crossfade, to be compared with 7-9 kW for m = 3. With cell voltage amplitude {amp_v(case(A5,'overlapped_2pct')['mec']['pulsation_peak_W'],350,1e-3):.1f} V at 1.0 mF, this is negligible. It is an upper bound because the cage would damp the combination orders. The 8/4 pair is not a special case here: with the iron shared, combination orders appear for any pair, but their amplitude is the saturation level (B_tooth peak {case(A5,'overlapped_0pct')['B_tooth_peak_max_T']:.2f} T), so a stator driven deeper into saturation (for example at the 2p = 8 flux cap at low speed) should be checked separately.

## 4. Sequential handover, m = 3 (addition 3)

Mode 2 is started only when the residual 8-pole rotor flux has fallen below the trigger level, the 8-pole current is then set to zero. The only cross product left is v_p4 (EMF of the residual 8-pole flux) x i_p2:

{ts}
## 5. H11s in the nonlinear MEC with DC cells

Schedule (analyst's H11s, my controller): ramp the 8-pole torque current to 0 in 20 ms; demagnetise with i_d8 = -0.9 I_pk until psi_r8 < 2 %; build the 4-pole flux with the d current up to the budget, the 4-pole current limited online so that 1.5(|V_8||I_4| + |V_4||I_8|) <= P_allow = 0.10 V_0 w_sum C (2137 W at 2.88 mF, 742 W at 1.0 mF); torque current once psi_4 > 5 %.

{th}
## 6. Balancing knob (item 4 of the first request)

IM 2p = 4 at cruise (4250 rpm, 352 Nm, a = 2): V = {BAL3['meta']['operating_point']['V_rms']:.1f} V, I = {BAL3['meta']['operating_point']['I_rms']:.0f} A rms, mean cell power {BAL3['meta']['operating_point']['mean_cell_power_W']:.0f} W. A current of order b at the same electrical frequency exchanges average power between cells only if (a - b) is a multiple of m; it sums to zero over the cells (power is moved, not created). m = 3, Q = 48 (current per coil):

{baltab(BAL3)}
m = 5, Q = 80 (coil current scaled by 48/80, so W/A is higher but the relative effect is the same):

{baltab(BAL5)}
**About 82-85 W per A rms per cell (0.82-0.85 % of cell power per A) for m = 3**, so 5 % costs 5.9-6.1 A rms (about 5 % of the fundamental current), 5-7 W of copper, under 0.6 V of extra voltage and under 0.01 Nm of torque, which matches the analyst's "about 1 A per 1 %". Orders with (a - b) not a multiple of m move no power.

## Caveats

* The MEC replay uses a smooth rotor and the B-H table of the agreed geometry; no rotor slotting, no cage reaction to the saturation-generated orders.
* Cell voltage is the open-loop linearised value; the real cell-balancing loop removes the slow drift but not the 70-350 Hz ripple.
* The m = 5 machine is the same per-unit machine on 80 slots (y = 11, 5.4 mm slots, coil current x 48/80, same V limit); a 5-leg bridge has a different linear voltage range, not modelled.
* Schedules are the best of a 64-point grid per case (t_d, t_f4, t_f2); a better controller may improve the torque dip but cannot beat the voltage budget.
"""
open("confirm_H10.md", "w", encoding="utf-8").write(md)
print(len(md))

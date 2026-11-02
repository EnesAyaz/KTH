"""Gap-loop step 3, H03: rotor excitation by SPB space-harmonic injection (no WPT / OPT / brushes).

Run from repo root:  python 02_analytics/screen_H03.py
Output: 02_analytics/results/screen_H03.json  (summary: 02_analytics/screen_H03.md)

Concept screened (generalises Enes's P3 decks: harvesting coil + superimposed voltage):
  * The 48 SPB coil-phases carry, on top of the torque current (space order p = 4 or 2), a small current
    wave of a different space order nu (not divisible by 3, so every isolated-neutral module stays balanced).
  * A polyphase rotor "harvesting" winding of order nu, series-tuned at a fixed rotor frequency f_r0, feeds
    a diode rectifier -> field winding (WRSM / HESM group coils).
  * Rotor sees f_r = f_i + nu f_m (backward stator wave, f_i >= 0) or f_i - nu f_m (forward).
    Choosing f_i = |f_r0 - nu f_m| keeps the rotor tank at f_r0 at every speed: at standstill it is a transformer
    (power from the inverter), at f_r0 = nu f_m it is a DC-excited brushless exciter (power from the shaft).
Machine: T03c WRSM (s = 0) and HESM (s = 0.25), T03 stator, N = 16, 300 kW, G = 10.8 (T03c gear rule).
Geometry: data/machine_geometry.json (R01 shared geometry; WRSM air gap still open in R01 -> T03 g_eff used,
larger-gap sensitivity reported).
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("SPB_P_RATED_KW", "300")
import torque_speed_envelope as T3  # noqa: E402  (read-only)
import fair_baselines as FB          # noqa: E402  (read-only)
import hesm_envelope as H            # noqa: E402  (read-only; VMAX patched temporarily for reduced-headroom points)

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "02_analytics", "results", "screen_H03.json")
GEO = json.load(open(os.path.join(ROOT, "data", "machine_geometry.json")))

MU0, RPM, M = T3.MU0, T3.RPM, T3.M_PH
VMAX, IMAX = T3.VMAX, T3.IMAX
S, W = GEO["stator"], GEO["winding"]
Q, Y, NC = S["Q_slots"], W["coil_pitch_slots"], W["turns_per_coil"]
R, L = S["R_bore_m"], S["L_stk_m"]
R_COIL = W["R_coil_120C_ohm"]
G_EFF_BASE = T3.ST["g_eff_m"]          # 1.3 mm (T03 k_c k_sat); R01 WRSM gap not yet set
G_EFF_SENS = [GEO["airgap"]["g_eff_carter_IM_m"], 2.0e-3, 3.0e-3]
K_PERM = GEO["rotor_wrsm"]["pole_arc_ratio"]   # nu-wave sees iron only under the pole arcs (assumption)
G_RATIO = 10.8                                 # T03c gear rule result (all feasible HESM/WRSM cases)
N_90 = FB.WHEEL_RPM_VMAX * G_RATIO

ETA_HARV = 0.97          # harvesting winding + tank copper (assumption)
FIELD_FORCING = 3.0      # T03 field forcing ratio
I_INJ_CAP = 0.15         # injected current budget, fraction of I_max (rms-add: 1.1 % thermal)


# ----------------------------------------------------------------------------------
# 1. Space orders: what the SPB can inject and what the rotor sees
# ----------------------------------------------------------------------------------
def rotor_field_orders(nmax=48):
    """Space orders present in the rotor field / field coil groups (8 salient poles, arc 0.7)."""
    a = GEO["rotor_wrsm"]["pole_arc_ratio"]
    h8 = T3.rotor_pole_pattern_harmonics([1, -1] * 4, a, nu_max=nmax)
    h4 = T3.rotor_pole_pattern_harmonics([1, 1, -1, -1] * 2, a, nu_max=nmax)
    hA = T3.rotor_pole_pattern_harmonics([1, 0, 0, -1, 1, 0, 0, -1], a, nu_max=nmax)
    hB = T3.rotor_pole_pattern_harmonics([0, -1, 1, 0, 0, -1, 1, 0], a, nu_max=nmax)
    pick = lambda h: [int(n) for n in range(1, nmax + 1) if h[n] > 0.02 * h.max()]
    return dict(field_2p8=pick(h8), field_2p4=pick(h4), group_A_coils=pick(hA), group_B_coils=pick(hB))


def conventional_3ph_orders(p=4, nmax=48):
    """Orders a conventional 3-phase 2p=8, q=2 winding can produce (all at the same time frequency)."""
    return [n for n in range(1, nmax + 1) if n % p == 0 and (n // p) % 6 in (1, 5)]


def order_params(nu, g_eff=G_EFF_BASE):
    kw = T3.winding_factor_analytic(nu)
    kw_num, _ = T3.winding_factor_numeric(nu)
    Lm = 2 * M * MU0 * R * L * (NC * kw) ** 2 / (math.pi * g_eff * nu ** 2) * K_PERM
    L_slot = 2 * MU0 * NC ** 2 * L * (T3.ST["lam_slot_self"] - T3.ST["lam_slot_mut"] * math.cos(2 * math.pi * nu * Y / Q))
    L_end = MU0 * NC ** 2 * 2 * W["end_half_length_m"] * W["lambda_end_winding"]
    sig = T3.differential_leakage_coeff(nu)
    Lm_unsat = Lm / K_PERM * g_eff / (g_eff / T3.ST["kc_ksat"] * 1.05)
    Ls = L_slot + L_end + sig * Lm_unsat
    psi_per_T = 2 * NC * kw * R * L / nu / math.sqrt(2)
    mod_sum = T3.module_current_sum(nu)
    return dict(nu=nu, k_w=kw, k_w_numeric=float(kw_num), Lm_H=Lm, L_sigma_H=Ls, sigma_diff=sig,
                coupling_k=Lm / (Lm + Ls), psi_rms_per_T=psi_per_T, module_current_sum_pu=mod_sum,
                injectable_by_SPB=bool(mod_sum < 1e-9))


def order_screen():
    f = rotor_field_orders()
    allf = set(f["field_2p8"]) | set(f["field_2p4"])
    conv = conventional_3ph_orders()
    rows = []
    for nu in range(1, 24):
        op = order_params(nu)
        sal = {abs(nu - 8), nu + 8}  # 8-pole saliency modulation
        rows.append(dict(op, in_rotor_field_spectrum=nu in allf,
                         couples_to_field_groups=bool(nu in f["group_A_coils"] or nu in f["group_B_coils"]),
                         couples_to_field_groups_via_saliency=bool(sal & (set(f["group_A_coils"]) | set(f["group_B_coils"]))),
                         radial_force_order_1_UMP=bool({nu - 1, nu + 1} & allf),
                         makes_avg_torque_with_field=False,
                         available_to_conventional_3ph_drive=nu in conv))
    return f, conv, rows


# ----------------------------------------------------------------------------------
# 2. Power transfer model (per coil-phase, m = 48)
# ----------------------------------------------------------------------------------
def rect_eta(P_out, P_rated):
    x = math.sqrt(max(P_out, 1e-9) / P_rated)
    E = H.EXC
    return P_out / (P_out + P_rated * (E["k0"] + E["k1"] * x)) if P_out > 0 else 1.0


def transfer(op, P_field_W, n_rpm, f_r0, P_rated_ch=4000.0, psi_grid=None, objective="V", V_budget=None, I_cap=None):
    """Stator-side injection needed to deliver P_field_W to the field (DC) at speed n.
    Rotor tank tuned at f_r0 (rotor leakage cancelled), rectifier = resistive load, referred to the stator.
    Returns the loss-/headroom-optimal operating point over the nu-wave flux linkage psi."""
    nu = op["nu"]
    f_m = n_rpm / 60.0
    f_i = abs(f_r0 - nu * f_m)          # stator frequency of the injected wave (>= 0)
    w_i, w_r = 2 * math.pi * f_i, 2 * math.pi * f_r0
    eta_r = rect_eta(P_field_W, P_rated_ch)
    P_rot = P_field_W / eta_r / ETA_HARV          # electrical power the rotor winding must receive
    if psi_grid is None:
        psi_grid = np.geomspace(1e-5, 2e-2, 600)
    psi = psi_grid
    E_r = w_r * psi                                # referred rotor EMF (rms per coil)
    I_L = P_rot / (M * E_r)                        # referred load current, in phase with E
    I_m = psi / op["Lm_H"]
    I_s = np.hypot(I_L, I_m)
    # stator voltage: j w_i psi + (R + j w_i Ls) I_s, with I_s = I_m (along psi) + I_L (along j psi)
    Is_c = I_m + 1j * I_L
    V = np.abs(1j * w_i * psi + (R_COIL + 1j * w_i * op["L_sigma_H"]) * Is_c)
    B = psi / op["psi_rms_per_T"] * math.sqrt(2)  # peak air-gap flux density of the nu-wave
    I_cap = I_INJ_CAP * IMAX if I_cap is None else I_cap
    ok = I_s <= I_cap
    if objective == "I" and V_budget is not None:
        ok = ok & (V <= V_budget)
    if not np.any(ok):
        return None
    cost = np.where(ok, V if objective == "V" else I_s, np.inf)
    j = int(np.argmin(cost))
    # losses
    P_cu_s = M * I_s[j] ** 2 * R_COIL
    fe = iron_nu(B[j], f_i, f_r0, nu)
    P_harv = P_rot * (1 - ETA_HARV) * ETA_HARV / ETA_HARV
    P_rect = P_field_W / eta_r - P_field_W
    P_air = P_rot * (f_i / f_r0) * (1 if f_r0 >= nu * f_m else -1)   # electrical airgap power from the inverter
    P_shaft = P_rot - P_air                                        # power taken from the shaft (exciter action)
    loss = P_cu_s + fe["P_fe_stator_W"] + fe["P_fe_rotor_W"] + P_harv + P_rect
    T_exc = P_shaft / (n_rpm * RPM) if n_rpm > 1 else 0.0
    return dict(nu=nu, speed_rpm=n_rpm, f_inj_stator_Hz=f_i, f_rotor_Hz=f_r0, P_field_W=P_field_W, P_rotor_winding_W=P_rot,
                psi_rms_Wb=float(psi[j]), B_nu_peak_T=float(B[j]), V_inj_rms_V=float(V[j]), V_inj_over_Vmax=float(V[j] / VMAX),
                I_inj_rms_A=float(I_s[j]), I_inj_over_Imax=float(I_s[j] / IMAX), I_load_ref_A=float(I_L[j]), I_mag_A=float(I_m[j]),
                P_from_inverter_W=float(P_air + loss - P_rect - P_harv - fe["P_fe_rotor_W"]), P_from_shaft_W=float(P_shaft),
                exciter_torque_Nm=float(T_exc), P_cu_stator_extra_W=float(P_cu_s), **fe, P_harvest_winding_W=float(P_harv),
                P_rectifier_W=float(P_rect), P_chain_loss_W=float(loss),
                chain_efficiency=float(P_field_W / (P_field_W + loss)))


def iron_nu(B_gap_pk, f_i, f_r, nu):
    """Stator teeth+yoke loss at f_i and rotor pole-shoe loss at f_r for the nu-wave (Bertotti two-term, T03 fit)."""
    FE = T3.FE
    st = T3.ST
    Bt = B_gap_pk * st["slot_pitch_m"] / st["tooth_w_m"]
    By = B_gap_pk * R / (nu * st["yoke_h_m"])
    spec = lambda f, b: FE["k_h"] * f * b ** 2 + FE["k_e"] * f ** 2 * b ** 2
    Ps = FE["build_factor"] * (st["m_teeth_kg"] * spec(f_i, Bt) + st["m_yoke_kg"] * spec(f_i, By))
    depth = min(R / nu, 0.03)  # nu-wave penetration ~ R/nu
    m_rot = K_PERM * 2 * math.pi * R * depth * L * st["rho_fe_kg_m3"]
    Pr = FE["build_factor"] * m_rot * spec(f_r, B_gap_pk)
    return dict(P_fe_stator_W=float(Ps), P_fe_rotor_W=float(Pr), B_yoke_nu_T=float(By), rotor_iron_mass_kg=float(m_rot))


def max_power(op, n_rpm, f_r0, V_avail, I_avail):
    """Largest field power deliverable within a voltage and current budget (bisection)."""
    lo, hi = 0.0, 2e5
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        r = transfer(op, mid, n_rpm, f_r0, psi_grid=np.geomspace(1e-5, 5e-2, 800))
        ok = r is not None and r["V_inj_rms_V"] <= V_avail and r["I_inj_rms_A"] <= I_avail
        if r is None:  # current cap of transfer() itself
            ok = False
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo


# ----------------------------------------------------------------------------------
# 3. Cost on the drive: headroom from the fundamental, efficiency at the T03c points
# ----------------------------------------------------------------------------------
def with_vmax(v, fn, *a, **k):
    old = H.VMAX
    H.VMAX = v
    try:
        return fn(*a, **k)
    finally:
        H.VMAX = old


def wheel_point(name):
    w = FB.wheel_points()[name]
    return w["wheel_rpm"] * G_RATIO, w["wheel_side_torque_Nm"] / G_RATIO


def cost_at_point(case, op, f_r0, n, T, label):
    par, rng, rot = case["_pars"][4], case["_rng"][4], case["rotor"]
    TN = case["T_N_Nm"]["2p8"]
    base = H.op_point(par, rot, rng, n, T, TN)
    if base is None:
        return None
    Vm = VMAX
    r = None
    for _ in range(6):   # fixed point: field power -> injection voltage -> fundamental headroom -> field power
        pt = with_vmax(Vm, H.op_point, par, rot, rng, n, T, TN)
        if pt is None:
            return dict(label=label, feasible=False)
        r = transfer(op, pt["P_field_cu_W"], n, f_r0)
        Vm = VMAX - r["V_inj_rms_V"]
    # replace the T03c exciter (rectifier only) by the injection chain; current: peak-sum check
    loss = pt["P_loss_total_W"] - pt["P_exciter_W"] + r["P_chain_loss_W"]
    P_out = T * n * RPM - pt["P_mech_W"]
    loss_wpt = base["P_loss_total_W"] - base["P_exciter_W"] + base["P_field_cu_W"] * (1 / (H_WPT_LINK) - 1) + base["P_exciter_W"] / H_WPT_LINK
    return dict(label=label, speed_rpm=n, torque_Nm=T, P_field_W=pt["P_field_cu_W"],
                eta_T03c_rectifier_only=base["eta"], eta_with_P1_WPT_link=P_out / (P_out + loss_wpt),
                eta_with_injection=P_out / (P_out + loss), delta_eta_vs_T03c_pts=100 * (P_out / (P_out + loss) - base["eta"]),
                V_fund_rms_V=pt["V_rms_V"], I_fund_rms_A=pt["I_rms_A"], peak_current_sum_over_Imax=(pt["I_rms_A"] + r["I_inj_rms_A"]) / IMAX,
                injection=r)


H_WPT_LINK = 0.94   # P1-type rotary WPT inverter+coils+compensation (excl. rectifier), assumed typical kW-class value


def envelope_cost(case, op, f_r0, P_field_W, speeds, current_rule="peak"):
    """Envelope torque when the injection (delivering P_field_W) shares the module V and I budgets, relative to T03c.
    current_rule 'peak': I_fund + I_inj <= I_max (device peak, conservative); 'rms': I_fund^2 + I_inj^2 <= I_max^2 (thermal).
    The nu-wave flux psi (V/I split of the injection) is chosen per speed to maximise the remaining torque."""
    par, rng = case["_pars"][4], case["_rng"][4]
    out = []
    for n in speeds:
        T0 = H.envelope(par, np.array([n]), *rng, n_g=241, n_f=41)[0]
        best = None
        for psi in np.geomspace(2e-4, 2e-2, 25):
            r = transfer(op, P_field_W, n, f_r0, psi_grid=np.array([psi]), I_cap=IMAX)
            if r is None or r["V_inj_rms_V"] >= VMAX:
                continue
            Ia = IMAX - r["I_inj_rms_A"] if current_rule == "peak" else math.sqrt(max(IMAX ** 2 - r["I_inj_rms_A"] ** 2, 0.0))
            T1 = H.envelope(par, np.array([n]), *rng, n_g=241, n_f=41, Vmax=VMAX - r["V_inj_rms_V"], Imax=Ia)[0]
            if best is None or T1 > best[0]:
                best = (T1, r)
        T1, r = best
        out.append(dict(speed_rpm=float(n), f_inj_Hz=r["f_inj_stator_Hz"], V_inj_over_Vmax=r["V_inj_over_Vmax"],
                        I_inj_over_Imax=r["I_inj_over_Imax"], B_nu_peak_T=r["B_nu_peak_T"], T_envelope_Nm=float(T0),
                        T_with_injection_Nm=float(T1), torque_ratio=float(T1 / T0) if T0 > 0 else None))
    return out


def tank_frequency_tradeoff(case, P_start_W, P_top_W, f_list):
    """f_r0 choice: start torque (standstill, transformer mode) vs power at 90 km/h."""
    rows = []
    for fr in f_list:
        o = order_params(8)
        st = envelope_cost(case, o, fr, P_start_W, [10.0], "peak")[0]
        st_rms = envelope_cost(case, o, fr, P_start_W, [10.0], "rms")[0]
        top = envelope_cost(case, o, fr, P_top_W, [N_90], "peak")[0]
        rows.append(dict(f_r0_Hz=fr, f_inj_at_90kmh_Hz=abs(fr - 8 * N_90 / 60),
                         start_torque_ratio_peak_rule=st["torque_ratio"], start_torque_ratio_rms_rule=st_rms["torque_ratio"],
                         start_grade_pct_peak_rule=T3.max_start_grade(st["T_with_injection_Nm"], G_RATIO),
                         start_grade_pct_rms_rule=T3.max_start_grade(st_rms["T_with_injection_Nm"], G_RATIO),
                         start_I_inj_over_Imax=st["I_inj_over_Imax"], start_B_nu_T=st["B_nu_peak_T"],
                         P90_ratio=top["torque_ratio"], P90_V_inj_over_Vmax=top["V_inj_over_Vmax"]))
    return rows


# ----------------------------------------------------------------------------------
# 4. Bipolar / per-group polarity channels for pole changing
# ----------------------------------------------------------------------------------
def channel_crosstalk(nu1, nu2):
    """Coupling between two harvest channels: direct (orthogonal orders -> 0) and via 8-pole saliency."""
    sal = {abs(nu1 - 8), nu1 + 8, (2 * 8 - nu1) if nu1 < 16 else None}
    return dict(direct=0.0, via_saliency=bool(nu2 in sal),
                remedy="tune the two tanks to different rotor frequencies f_r1 != f_r2; the inactive tank is off-resonance")


def main():
    fields, conv, orders = order_screen()
    NU, NU2 = 8, 16
    op = order_params(NU)
    op2 = order_params(NU2)
    f_r0 = NU * N_90 / 60.0            # tank frequency = nu f_m at 90 km/h -> f_i = 0 there (DC-excited exciter mode)
    cases = {"WRSM_s0": H.evaluate("T03_yoke25mm", H.mapping(16), 0.0, "If_weakening", ng=241, nf=61),
             "HESM_s0.25": H.evaluate("T03_yoke25mm", H.mapping(16), 0.25, "If_weakening", ng=241, nf=61)}
    need = {"WRSM_s0": dict(cruise_W=1147.0, start_peak_W=4000.0, forcing_transient_W=FIELD_FORCING * 4000.0),
            "HESM_s0.25": dict(cruise_W=500.0, start_peak_W=2000 * ((1 - 0.5) / 0.6191) ** 2 + 2000.0,
                               forcing_transient_W=FIELD_FORCING * 2000.0)}

    # capability at standstill / base / cruise / 90 km/h (voltage budget = what the fundamental leaves; I budget 15 %)
    speeds = {"standstill": 1.0, "n_base_1111rpm": 1111.0, "50kmh": 50 / 90 * N_90, "85kmh": 85 / 90 * N_90, "90kmh": N_90}
    cap = {}
    for k, n in speeds.items():
        r_full = max_power(op, n, f_r0, VMAX, I_INJ_CAP * IMAX)
        r_10 = max_power(op, n, f_r0, 0.10 * VMAX, I_INJ_CAP * IMAX)
        cap[k] = dict(speed_rpm=n, f_inj_Hz=abs(f_r0 - NU * n / 60), P_max_full_voltage_budget_W=r_full,
                      P_max_10pct_voltage_budget_W=r_10)

    # sensitivity: air gap (R01 WRSM gap open) - start torque with the 4 kW WRSM field
    gap_sens = {}
    for g in [G_EFF_BASE] + G_EFF_SENS:
        o = order_params(NU, g)
        stp = envelope_cost(cases["WRSM_s0"], o, f_r0, 4000.0, [10.0], "peak")[0]
        gap_sens[f"g_eff_{g * 1e3:.2f}mm"] = dict(Lm_H=o["Lm_H"], coupling_k=o["coupling_k"], start_torque_ratio_peak_rule=stp["torque_ratio"],
                                                  start_I_inj_over_Imax=stp["I_inj_over_Imax"], start_B_nu_T=stp["B_nu_peak_T"])
    # frequency sensitivity of the tank (standstill transformer mode)
    fr_sens = {}
    for fr in (300.0, f_r0, 1500.0, 3000.0):
        r = transfer(op, 4000.0, 1.0, fr)
        fr_sens[f"f_r0_{fr:.0f}Hz"] = None if r is None else {k: r[k] for k in ("V_inj_over_Vmax", "I_inj_over_Imax", "B_nu_peak_T", "P_chain_loss_W", "chain_efficiency")}

    # alternative order nu = 5 (strong coupling, but order-1 radial force = unbalanced magnetic pull with the 8-pole field)
    op5 = order_params(5)
    f5 = 5 * N_90 / 60.0
    alt5 = {}
    for name in ("WRSM_s0",):
        c = cases[name]
        stp = envelope_cost(c, op5, f5, 4000.0, [10.0], "peak")[0]
        n, T = wheel_point("cruise_85kmh_flat")
        cr = cost_at_point(c, op5, f5, n, T, "cruise_85kmh_flat")
        B4 = 0.8   # main 8-pole fundamental (peak), T
        sigma1 = B4 * stp["B_nu_peak_T"] / (2 * MU0)
        alt5[name] = dict(order_params=op5, f_r0_Hz=f5, start=stp, start_grade_pct=T3.max_start_grade(stp["T_with_injection_Nm"], G_RATIO),
                          cruise=dict(eta_with_injection=cr["eta_with_injection"], delta_eta_vs_T03c_pts=cr["delta_eta_vs_T03c_pts"],
                                      B_nu_peak_T=cr["injection"]["B_nu_peak_T"]),
                          UMP_force_at_start_N=math.pi * R * L * sigma1,
                          UMP_force_at_cruise_N=math.pi * R * L * B4 * cr["injection"]["B_nu_peak_T"] / (2 * MU0),
                          note="order-1 rotating radial force (orders 4 and 5 differ by 1) at the slip frequency of the injected wave; bearing/NVH load")

    res_cases = {}
    for name, c in cases.items():
        pts = {}
        for pn in ("cruise_85kmh_flat", "part_load_50kmh_3pct_grade", "cruise_85kmh_1pct_grade"):
            n, T = wheel_point(pn)
            pts[pn] = cost_at_point(c, op, f_r0, n, T, pn)
        # start (peak torque, standstill): field peak through transformer mode; current taken from the torque current
        par, rng = c["_pars"][4], c["_rng"][4]
        st_pk = envelope_cost(c, op, f_r0, need[name]["start_peak_W"], [10.0], "peak")[0]
        st_rms = envelope_cost(c, op, f_r0, need[name]["start_peak_W"], [10.0], "rms")[0]
        st_inj = transfer(op, need[name]["start_peak_W"], 1.0, f_r0, objective="I", V_budget=0.9 * VMAX)
        start = dict(peak_current_rule=st_pk, rms_current_rule=st_rms, min_current_injection=st_inj,
                     start_grade_pct=dict(T03c=T3.max_start_grade(st_pk["T_envelope_Nm"], G_RATIO),
                                          peak_rule=T3.max_start_grade(st_pk["T_with_injection_Nm"], G_RATIO),
                                          rms_rule=T3.max_start_grade(st_rms["T_with_injection_Nm"], G_RATIO)))
        tradeoff = tank_frequency_tradeoff(c, need[name]["start_peak_W"], need[name]["start_peak_W"], [661.1, 1500.0, 3000.0, 6000.0])
        # forcing transient (pole change / field build) at the T03c transition speed 2000 rpm, with 50 % of V and 15 % I
        forcing = max_power(op, 2000.0, f_r0, 0.5 * VMAX, I_INJ_CAP * IMAX)
        env = envelope_cost(c, op, f_r0, need[name]["start_peak_W"], [10.0, 1111.0, 1500.0, 2000.0, 3000.0, 4000.0, N_90 * 85 / 90, N_90])
        env_rms = envelope_cost(c, op, f_r0, need[name]["start_peak_W"], [10.0, 1111.0, 2000.0, 3000.0, N_90], "rms")
        Penv = H.envelope(par, np.array([N_90]), *rng, n_g=481, n_f=81)[0] * N_90 * RPM
        res_cases[name] = dict(field_need_W=need[name], points=pts, start=start,
                               forcing_transient_max_W_at_2000rpm_half_voltage=forcing,
                               forcing_transient_needed_W=need[name]["forcing_transient_W"],
                               envelope_with_peak_field_injection=env, envelope_with_peak_field_injection_rms_rule=env_rms,
                               tank_frequency_tradeoff=tradeoff, P_at_90kmh_kW=float(Penv / 1e3))

    # torque ripple / forces
    ripple = dict(
        average_torque_with_field="none: nu = 8 is not in the rotor-field spectrum and the wave is asynchronous (f_r0 != 0)",
        exciter_torque_Nm_at_4kW=4000.0 * NU / (2 * math.pi * f_r0) / ETA_HARV,
        rectifier_ripple_torque_Nm_estimate=0.25 * 4000.0 * NU / (2 * math.pi * f_r0),
        radial_force_orders=[NU - 4, NU + 4, NU - 2, NU + 2],
        radial_force_density_ratio_to_main=None)
    st_w = res_cases["WRSM_s0"]["start"]["peak_current_rule"]
    ripple["radial_force_density_ratio_to_main"] = float(2 * st_w["B_nu_peak_T"] / 0.8)   # B_nu B_main / (B_main^2/2)

    bip = dict(channels=[dict(order=NU, k_w=op["k_w"], coupling_k=op["coupling_k"], Lm_H=op["Lm_H"]),
                         dict(order=NU2, k_w=op2["k_w"], coupling_k=op2["coupling_k"], Lm_H=op2["Lm_H"])],
               crosstalk=channel_crosstalk(NU, NU2),
               clean_orders_on_48_coils=[r["nu"] for r in orders if r["injectable_by_SPB"] and not r["in_rotor_field_spectrum"]
                                         and not r["couples_to_field_groups"] and not r["couples_to_field_groups_via_saliency"]
                                         and not r["radial_force_order_1_UMP"]],
               P_max_standstill_order16_10pct_V_W=max_power(op2, 1.0, NU2 * N_90 / 60, 0.10 * VMAX, I_INJ_CAP * IMAX),
               topology="P1 dual-input/dual-output with the two WPT transmitters replaced by two injected space orders (or two tank "
                        "frequencies on one order): channel 1 rectifier -> group B (+), channel 2 rectifier -> group B (-) anti-parallel, "
                        "P1 self-driven blocking switches; group A from a third tank (frequency-selected). Polarity = which pattern the SPB injects.")

    compare = dict(
        injection=dict(extra_stationary_hardware="none (modulation only)", rotor_hardware="harvest winding (order 8, polyphase) + tank capacitors + diode rectifier (+ P1 blocking switches for bipolar)",
                       chain_eff_cruise_WRSM=res_cases["WRSM_s0"]["points"]["cruise_85kmh_flat"]["injection"]["chain_efficiency"]),
        P1_WPT=dict(extra_stationary_hardware="HF inverter + Tx coils + compensation", rotor_hardware="Rx coils + compensation + rectifier + switches",
                    chain_eff_assumed=H_WPT_LINK * 0.99, note="rectifier 99 % measured (P1); link 94 % assumed"),
        brushes=dict(extra_stationary_hardware="3 slip rings + brushes + stationary H-bridge (bipolar)", rotor_hardware="none",
                     chain_eff_estimate=0.97, note="2 V brush drop at an assumed 20 A / 200 V field + H-bridge 98 %; wear and maintenance"))

    res = dict(
        meta=dict(script="02_analytics/screen_H03.py", task="gap loop step 3, H03", date=_dt.date.today().isoformat(),
                  inputs=["data/machine_geometry.json (R01 shared geometry: stator, winding, R_coil, rotor_wrsm layout; WRSM gap not yet set)",
                          "02_analytics/hesm_envelope.py (T03c WRSM s=0 / HESM s=0.25 models, T03 stator, N=16)",
                          "board/prior_work.md P1 (rectifier 99/87 %), P3 decks (harvesting coil, superimposed voltage)"],
                  assumptions=dict(g_eff_m=G_EFF_BASE, g_eff_note="T03 k_c k_sat = 1.3 mm; R01 WRSM gap open -> sensitivity 1.08/2/3 mm",
                                   nu_wave_permeance_factor=K_PERM, harvest_winding_eff=ETA_HARV, I_inj_budget_over_Imax=I_INJ_CAP,
                                   rotor_tank="series-tuned at f_r0; rotor leakage cancelled; rectifier = resistive load",
                                   voltage_budget="peak sum: V_fund + V_inj <= V_max (rms of sinusoids, conservative)",
                                   current_budget="start: peak sum (conservative) and rms sum reported",
                                   gear_ratio=G_RATIO, WPT_link_eff=H_WPT_LINK,
                                   not_included=["saturation-dependent incremental permeability for the nu-wave", "PWM sidebands of the injected wave",
                                                 "rotor eddy loss in solid parts (laminated rotor assumed)", "harvest-winding space vs field copper"])),
        injection_choice=dict(order=NU, f_rotor_tank_Hz=f_r0, f_stator_rule="f_i = |f_r0 - nu f_m| (0 Hz at 90 km/h)", order_params=op,
                              rotor_field_orders=fields, conventional_3ph_2p8_orders=conv, order_table=orders,
                              zero_sequence="not possible: an isolated-neutral module carries no zero-sequence current (orders divisible by 3 put a module's coils in phase); "
                                            "the SPB-specific freedom is an independent space order per module pattern, not a zero-sequence path"),
        capability=cap, gap_sensitivity=gap_sens, tank_frequency_sensitivity_start_4kW=fr_sens,
        cases=res_cases, alternative_order_5=alt5, torque_ripple_and_forces=ripple, bipolar_for_pole_changing=bip, comparison=compare)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else (bool(o) if isinstance(o, np.bool_) else float(o)))
    print(json.dumps(dict(op=op, f_r0=f_r0, cap=cap, gap=gap_sens, fr=fr_sens, ripple=ripple, bip={k: v for k, v in bip.items() if k != "topology"}), indent=1, default=float))
    for nm, c in res_cases.items():
        print("==", nm, "P90", c["P_at_90kmh_kW"], "forcing max", c["forcing_transient_max_W_at_2000rpm_half_voltage"])
        print(" start", json.dumps({k: v for k, v in c["start"].items() if k != "min_current_injection"}, default=float))
        for t in c["tank_frequency_tradeoff"]:
            print("  tank", {k: round(v, 3) for k, v in t.items()})
        for pn, p in c["points"].items():
            if p:
                print(" ", pn, {k: (round(v, 5) if isinstance(v, float) else v) for k, v in p.items() if k != "injection"},
                      {k: round(p["injection"][k], 4) for k in ("f_inj_stator_Hz", "V_inj_over_Vmax", "I_inj_rms_A", "P_chain_loss_W", "chain_efficiency", "P_from_shaft_W", "B_nu_peak_T")})
        for e in c["envelope_with_peak_field_injection"] + c["envelope_with_peak_field_injection_rms_rule"]:
            print("  env", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in e.items()})


if __name__ == "__main__":
    main()

"""T03b - Fair fixed-pole IM baselines vs the SPB pole-changing IM (T03).

Run from repo root:  python 02_analytics/fair_baselines.py
Output: 02_analytics/results/fair_baselines.json   (does NOT touch torque_speed_envelope.json)

Three induction machines, same outer volume (R_out, L_stk), same copper mass, same SPB limits
(29.09 V rms, 310.4 A rms per module leg, 433 kVA):
  (1) fixed 2p=4, own yoke / slots / winding / turns, own gear ratio (optimised)
  (2) fixed 2p=6, same procedure (needs Q=144: see notes)
  (3) SPB pole-changing 2p=8/4 IM from T03, unchanged (G = 9.80)
Fixed-pole machines are fed by the same SPB with one coil-phase per leg (k_d = 1), i.e. at least
as good as a conventional 3-phase belt winding (k_d < 1) - the baseline is not handicapped.
Assumptions: 02_analytics/assumptions.md, section T03b.
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
os.environ.setdefault("SPB_P_RATED_KW", "300")   # D02 final: 300 kW (must be set before the import)
import torque_speed_envelope as T3  # noqa: E402  (constants and T03 design only; T03 outputs are not rewritten)

ROOT = os.path.dirname(HERE)
OUT_JSON = os.path.join(ROOT, "02_analytics", "results", "fair_baselines.json")
T03_JSON = T3.OUT_JSON   # T03 envelope at the same rating (torque_speed_envelope_300kW.json for 300 kW)

MU0, SQ2, RPM, M_PH = T3.MU0, T3.SQ2, T3.RPM, T3.M_PH
VMAX, IMAX0 = T3.VMAX, T3.IMAX
S_INV_kVA = M_PH * VMAX * IMAX0 / 1e3
ST = T3.ST
V_CU = ST["copper_mass_kg"] / 8900.0        # same copper volume as T03
R_OUT, L_STK = ST["R_out_m"], ST["L_stk_m"]  # same outer volume
B_Y_MAX, B_T_MAX, B_G_MAX = ST["B_yoke_max_T"], 1.65, ST["B_gap_max_T"]
TIP_SPEED_MAX = 125.0                        # m/s, copper-cage rotor surface speed limit
WHEEL_RPM_VMAX = T3.VEH["v_max_kmh"] / 3.6 / T3.VEH["wheel_radius_m"] / RPM
G_REF = T3.VEH["gear_ratio"]
T_START_WHEEL = T3.T_START * G_REF           # motor torque x gear (eta_gear already inside T_START)
CRUISE_WHEEL_T = T3.T_CRUISE * G_REF
CRUISE_WHEEL_RPM = T3.N_CRUISE / G_REF


# ----------------------------------------------------------------------------------
# Design -> per-leg equivalent-circuit parameters
# ----------------------------------------------------------------------------------
def mmf_sigma_d(p, Q, y):
    th = np.linspace(0, 2 * np.pi, 8192, endpoint=False)
    a = p * 2 * np.pi * np.arange(Q) / Q
    Islot = np.zeros(Q)
    for k in range(Q):
        Islot[k] += math.cos(a[k])
        Islot[(k + y) % Q] -= math.cos(a[k])
    pos = 2 * np.pi * (np.arange(Q) + 0.5) / Q
    F = np.zeros_like(th)
    for s in range(Q):
        F += Islot[s] * (th >= pos[s])
    F -= F.mean()
    c = np.abs(np.fft.rfft(F))[:400]
    Fp = c[p]
    c[p] = 0.0
    c[0] = 0.0
    return float(np.sum(c ** 2) / Fp ** 2), float(Fp)


def make_design(p, Q, y, cpl, R_gap, B_design, N_leg, name="", h_y=None):
    """cpl = coils in series per leg (Q = 48*cpl). Returns dict or None if geometrically infeasible."""
    if h_y is None:
        h_y = B_design * R_gap / (p * B_Y_MAX)
    h_s = R_OUT - R_gap - h_y
    if h_s < 0.012:
        return None
    D_mid = 2 * R_gap + h_s
    l_end = 1.2 * math.pi * D_mid * y / Q + 2 * ST["end_ext_m"]
    l_turn = 2 * (L_STK + l_end)
    A_side = V_CU / (Q * l_turn)                 # copper area per coil side
    A_slot = 2 * A_side / ST["fill"]
    b_s = A_slot / h_s
    tau_s = 2 * math.pi * R_gap / Q
    b_t = tau_s - b_s
    if b_t < 0.25 * tau_s:
        return None
    B_cap = min(B_G_MAX, B_Y_MAX * h_y * p / R_gap, B_T_MAX * b_t / tau_s)
    kw = abs(math.sin(p * y * math.pi / Q))
    Nk = N_leg * kw
    RL = R_gap * L_STK
    g_eff = ST["g_eff_m"]
    Lm = 2 * M_PH * MU0 * RL * Nk ** 2 / (math.pi * g_eff * p ** 2)
    N_c = N_leg / cpl
    lam_r = (h_s / (3 * b_s) + 0.33) / 2.0       # slot-permeance ratio to the T03 slot (=1 for T03)
    L_slot = cpl * 2 * MU0 * N_c ** 2 * L_STK * lam_r * (
        ST["lam_slot_self"] - ST["lam_slot_mut"] * math.cos(2 * math.pi * p * y / Q))
    L_end = cpl * MU0 * N_c ** 2 * 2 * l_end * ST["lam_end"]
    sig_d, _ = mmf_sigma_d(p, Q, y)
    L_diff = sig_d * Lm * ST["kc_ksat"] / 1.05
    R_s = ST["rho_cu_ohm_m"] * N_leg ** 2 * l_turn / (cpl * A_side)
    # cage scaled with bore (T03 cage at R = 165 mm)
    sc = R_gap / ST["R_gap_m"]
    I = T3.IMR
    Qr = I["Q_r"]
    sin_a = math.sin(math.pi * p / Qr)
    R_bar = I["rho_cage_ohm_m"] * I["bar_len_m"] / (I["bar_area_m2"] * sc ** 2)
    l_seg = math.pi * I["ring_diam_m"] * sc / Qr
    R_seg = I["rho_cage_ohm_m"] * l_seg / (I["ring_area_m2"] * sc ** 2)
    K = 4 * M_PH * Nk ** 2 / Qr
    R_r = K * (R_bar + R_seg / (2 * sin_a ** 2))
    sig_dr = ((math.pi * p / Qr) / sin_a) ** 2 - 1.0
    L_r = K * (MU0 * L_STK * I["lam_bar"] + MU0 * l_seg * I["lam_ring"] / (2 * sin_a ** 2)) + sig_dr * Lm
    m_teeth = Q * b_t * h_s * L_STK * ST["rho_fe_kg_m3"]
    m_yoke = math.pi * (R_OUT ** 2 - (R_OUT - h_y) ** 2) * L_STK * ST["rho_fe_kg_m3"]
    psi_per_T = 2 * Nk * RL / p / SQ2
    R_r_bar = K * R_bar
    R_r_ring = K * R_seg / (2 * sin_a ** 2)
    return dict(R_r_bar_ohm=R_r_bar, R_r_ring_ohm=R_r_ring, h_bar_m=0.025 * sc,
                name=name, p=p, Q=Q, y_slots=y, coils_per_leg=cpl, R_gap_m=R_gap, h_yoke_m=h_y, h_slot_m=h_s,
                b_slot_m=b_s, b_tooth_m=b_t, slot_pitch_m=tau_s, B_design_T=B_design, B_gap_cap_T=B_cap,
                N_leg_turns=N_leg, k_w=kw, l_end_half_m=l_end, J_at_Imax_A_mm2=IMAX0 / (A_side / N_c * 1e6),
                R_s_ohm=R_s, Lm_H=Lm, L_sigma_s_H=L_slot + L_end + L_diff, sigma_diff=sig_d,
                R_r_ohm=R_r, L_sigma_r_H=L_r, psi_rms_per_T=psi_per_T, psi_cap_rms_Wb=B_cap * psi_per_T,
                m_teeth_kg=m_teeth, m_yoke_kg=m_yoke, n_tip_limit_rpm=TIP_SPEED_MAX / R_gap / RPM)


def t03_pc_design(p):
    """T03 pole-changing IM, unchanged (2p=8 or 2p=4 operation)."""
    d = make_design(p, 48, ST["y_slots"], 1, ST["R_gap_m"], float("nan"), ST["N_c"],
                    name=f"T03_PC_2p{2 * p}", h_y=ST["yoke_h_m"])
    return d


# ----------------------------------------------------------------------------------
# Envelope / loss (same equations as T03, design-specific iron masses)
# ----------------------------------------------------------------------------------
def envelope(d, NG, I_max=IMAX0, n_psi=120, n_sl=180):
    w_bd = d["R_r_ohm"] / d["L_sigma_r_H"]
    wsl = np.geomspace(w_bd * 1e-4, w_bd, n_sl)[None, :]
    T = np.zeros_like(NG)
    for i, n in enumerate(NG):
        psi_hi = min(d["psi_cap_rms_Wb"], 1.1 * VMAX / (d["p"] * n * RPM))
        psi = np.linspace(psi_hi / n_psi, psi_hi, n_psi)[:, None]
        st = T3.im_state(d, n, psi, wsl)
        ok = (st["V"] <= VMAX) & (st["Is"] <= I_max)
        T[i] = np.max(np.where(ok, st["T"], 0.0))
    return T


def iron_loss(d, f, B):
    Bt = B * d["slot_pitch_m"] / d["b_tooth_m"]
    By = B * d["R_gap_m"] / (d["p"] * d["h_yoke_m"])
    f = np.abs(f)
    spec = lambda b: T3.FE["k_h"] * f * b ** 2 + T3.FE["k_e"] * f ** 2 * b ** 2
    return T3.FE["build_factor"] * (d["m_teeth_kg"] * spec(Bt) + d["m_yoke_kg"] * spec(By))


def min_loss(d, n, Treq, n_psi=500):
    p, Rr, Lr = d["p"], d["R_r_ohm"], d["L_sigma_r_H"]
    psi = np.linspace(d["psi_cap_rms_Wb"] / n_psi, d["psi_cap_rms_Wb"], n_psi)
    a, b, c = Treq * Lr ** 2, -M_PH * p * psi ** 2 * Rr, Treq * Rr ** 2
    disc = b ** 2 - 4 * a * c
    good = disc >= 0
    wsl = np.where(good, (-b - np.sqrt(np.where(good, disc, 0))) / (2 * a), np.nan)
    st = T3.im_state(d, n, psi, wsl)
    ok = good & (st["V"] <= VMAX) & (st["Is"] <= IMAX0)
    if not np.any(ok):
        return None
    B = psi / d["psi_rms_per_T"]
    Pcs = M_PH * st["Is"] ** 2 * d["R_s_ohm"]
    Pcr = M_PH * st["Ir"] ** 2 * Rr
    Pfe = iron_loss(d, st["we"] / (2 * np.pi), B)
    loss = np.where(ok, Pcs + Pcr + Pfe, np.inf)
    j = int(np.argmin(loss))
    Pm = float(T3.p_mech(n))
    Pout = Treq * n * RPM - Pm
    tot = float(loss[j]) + Pm
    Pem_loss = float(loss[j])
    return dict(eta=Pout / (Pout + tot), eta_excl_friction_windage=(Pout + Pm) / (Pout + Pm + Pem_loss), PF=(Pout + tot) / (M_PH * float(st["V"][j]) * float(st["Is"][j])),
                I_rms_A=float(st["Is"][j]), P_cu_stator_W=float(Pcs[j]), P_cu_rotor_W=float(Pcr[j]),
                P_fe_W=float(Pfe[j]), P_mech_W=Pm, f_e_Hz=float(st["we"][j] / (2 * np.pi)), B_gap_T=float(B[j]),
                speed_rpm=n, torque_Nm=Treq)


# ----------------------------------------------------------------------------------
# Realistic IM loss model (T03b, leader request): stray load, skin effect, magnetising copper, PWM ripple
# ----------------------------------------------------------------------------------
F_SW_HZ = 100e3          # SPB GaN PWM frequency (../Analytical Loss Calculations - GaN/LOSS_MODELING.md default)
RHO_FE = 5.2e-7          # ohm m, M270-35A
D_LAM = 0.35e-3          # m
MU_R_HF = 1000.0         # small-signal relative permeability for HF ripple flux
K_AC_STATOR_HF = 5.0     # stator AC-resistance factor at f_sw (stranded conductors, proximity) - assumed
L_HF_FACTOR = 0.5        # leakage inductance at f_sw relative to fundamental (eddy/saturated bridges) - assumed
K_RING_HF = 5.0          # end-ring AC factor at f_sw - assumed
STRAY_SCALE = 1.0        # x IEC 60034-2-1 assumed allowance (sensitivity reported at 2.0)


def iec_stray_allowance_W(P_rated_W, eta_rated=0.95):
    """IEC 60034-2-1 assumed allowance for additional load losses at rated load (1 kW < P2 <= 10 MW)."""
    P1 = P_rated_W / eta_rated
    return P1 * (0.025 - 0.005 * math.log10(P_rated_W / 1e3))


def bar_skin_factor(f, h_bar, rho=T3.IMR["rho_cage_ohm_m"]):
    """Rectangular deep-bar resistance factor k_R(xi), xi = h/delta."""
    f = np.maximum(np.abs(f), 1e-9)
    xi = h_bar * np.sqrt(np.pi * f * MU0 / rho)
    x2 = 2 * xi
    with np.errstate(over="ignore", invalid="ignore"):
        kR = xi * (np.sinh(x2) + np.sin(x2)) / (np.cosh(x2) - np.cos(x2))
    return np.where(xi > 20, xi, np.where(xi < 1e-3, 1.0, kR))


def pwm_ripple_losses(d):
    """Upper-bound estimate of switching-ripple losses per machine (all 48 legs)."""
    L_hf = L_HF_FACTOR * (d["L_sigma_s_H"] + d["L_sigma_r_H"])
    di_pp = T3.INV["V_module_V"] / (4 * L_hf * F_SW_HZ)            # worst case, duty 0.5
    I_h = di_pp / (2 * math.sqrt(3))                                 # triangular ripple rms
    kR_hf = float(bar_skin_factor(F_SW_HZ, d["h_bar_m"]))
    P_cs = M_PH * I_h ** 2 * d["R_s_ohm"] * K_AC_STATOR_HF
    P_cr = M_PH * I_h ** 2 * (d["R_r_bar_ohm"] * kR_hf + d["R_r_ring_ohm"] * K_RING_HF)  # cage carries ~ the ripple (L_m open)
    # tooth leakage ripple flux, eddy loss with lamination skin-effect correction
    psi_h = d["L_sigma_s_H"] * L_HF_FACTOR * I_h * SQ2
    B_h = psi_h / (d["N_leg_turns"] * d["b_tooth_m"] * L_STK)
    delta = math.sqrt(RHO_FE / (math.pi * F_SW_HZ * MU0 * MU_R_HF))
    x = D_LAM / delta
    Fx = 3.0 / x * (math.sinh(x) - math.sin(x)) / (math.cosh(x) - math.cos(x))
    p_e = T3.FE["k_e"] * F_SW_HZ ** 2 * B_h ** 2 * Fx / 2   # triangular ripple ~ half the sine-equivalent eddy loss
    P_fe = T3.FE["build_factor"] * d["m_teeth_kg"] * p_e
    return dict(f_sw_Hz=F_SW_HZ, ripple_pp_A=di_pp, ripple_rms_A=I_h, bar_kR_at_fsw=kR_hf, B_tooth_ripple_T=B_h,
                lamination_skin_factor=Fx, P_cu_stator_W=P_cs, P_cage_W=P_cr, P_fe_W=P_fe, P_total_W=P_cs + P_cr + P_fe)


def realistic_point(d, n, Treq, T_N, n_psi=500):
    """Loss-minimising flux and rated-flux operation with the extended loss set."""
    p, Rr, Lr = d["p"], d["R_r_ohm"], d["L_sigma_r_H"]
    psi = np.linspace(d["psi_cap_rms_Wb"] / n_psi, d["psi_cap_rms_Wb"], n_psi)
    a, b, c = Treq * Lr ** 2, -M_PH * p * psi ** 2 * Rr, Treq * Rr ** 2
    disc = b ** 2 - 4 * a * c
    good = disc >= 0
    wsl = np.where(good, (-b - np.sqrt(np.where(good, disc, 0))) / (2 * a), np.nan)
    st = T3.im_state(d, n, psi, wsl)
    ok = good & (st["V"] <= VMAX) & (st["Is"] <= IMAX0)
    if not np.any(ok):
        return None
    B = psi / d["psi_rms_per_T"]
    Im = psi / d["Lm_H"]
    f_sl = wsl / (2 * np.pi)
    kR = bar_skin_factor(f_sl, d["h_bar_m"])
    Pcs = M_PH * st["Is"] ** 2 * d["R_s_ohm"]
    Pcs_mag = M_PH * Im ** 2 * d["R_s_ohm"]
    Pcr = M_PH * st["Ir"] ** 2 * (d["R_r_bar_ohm"] * kR + d["R_r_ring_ohm"])
    Pfe = iron_loss(d, st["we"] / (2 * np.pi), B)
    P_LL = STRAY_SCALE * iec_stray_allowance_W(T3.INV["P_rated_W"]) * (Treq / T_N) ** 2
    pwm = pwm_ripple_losses(d)
    Pm = float(T3.p_mech(n))
    Pout = Treq * n * RPM - Pm
    loss = Pcs + Pcr + Pfe + P_LL + pwm["P_total_W"]
    res = {}
    j_opt = int(np.argmin(np.where(ok, loss, np.inf)))
    j_rat = int(np.max(np.where(ok)[0]))            # highest feasible flux = rated (cap) or voltage-limited flux
    for tag, j in (("flux_optimised", j_opt), ("rated_flux", j_rat)):
        tot = float(loss[j]) + Pm
        res[tag] = dict(eta=Pout / (Pout + tot), eta_excl_friction_windage=(Pout + Pm) / (Pout + tot), PF=(Pout + tot) / (M_PH * float(st["V"][j]) * float(st["Is"][j])),
                        I_rms_A=float(st["Is"][j]), I_mag_A=float(Im[j]), B_gap_T=float(B[j]), slip=float(wsl[j] / st["we"][j]),
                        f_slip_Hz=float(f_sl[j]), bar_kR_at_slip=float(kR[j]),
                        P_cu_stator_W=float(Pcs[j]), P_cu_stator_magnetising_share_W=float(Pcs_mag[j]),
                        P_cu_rotor_W=float(Pcr[j]), P_fe_W=float(Pfe[j]), P_stray_IEC_W=float(P_LL),
                        P_pwm_W=pwm["P_total_W"], P_mech_W=Pm, P_loss_total_W=tot)
    res["torque_over_T_N"] = Treq / T_N
    res["speed_rpm"], res["torque_Nm"] = n, Treq
    res["pwm_estimate"] = pwm
    # stray-load sensitivity (2x IEC allowance), flux-optimised
    j = j_opt
    tot2 = float(loss[j]) + P_LL + Pm
    res["eta_flux_optimised_stray_x2"] = Pout / (Pout + tot2)
    return res


def wheel_points():
    """Part-load points defined at the wheel (each machine sees them through its own gear)."""
    pts = {}
    for name, v, grade in (("cruise_85kmh_flat", 85.0, 0.0), ("cruise_60kmh_flat", 60.0, 0.0),
                           ("cruise_85kmh_1pct_grade", 85.0, 1.0), ("part_load_50kmh_3pct_grade", 50.0, 3.0)):
        F, n, T = T3.road_load(v, grade)
        pts[name] = dict(v_kmh=v, grade_pct=grade, wheel_rpm=n / G_REF, wheel_side_torque_Nm=T * G_REF,
                         wheel_power_kW=F * v / 3.6 / 1e3)
    return pts


def realistic_set(d_by_mode, G, T_N_by_mode):
    """Evaluate all wheel points; for a pole-changing machine pick the lower-loss feasible mode."""
    out = {}
    for name, w in wheel_points().items():
        n, T = w["wheel_rpm"] * G, w["wheel_side_torque_Nm"] / G
        best = None
        for mode, d in d_by_mode.items():
            r = realistic_point(d, n, T, T_N_by_mode[mode])
            simple = min_loss(d, n, T)
            if r is None:
                continue
            r["mode"] = mode
            r["eta_simple_T03_model"] = simple["eta"] if simple else None
            if best is None or r["flux_optimised"]["eta"] > best["flux_optimised"]["eta"]:
                best = r
        out[name] = dict(point=w, **(best if best else {"feasible": False}))
    return out


def metrics(T, NG, G):
    P = T * NG * RPM
    Tpk = float(T.max())
    ib = int(np.max(np.where(T >= 0.99 * Tpk)[0]))
    Pb = float(P[ib])
    icp = int(np.max(np.where(P >= 0.95 * Pb)[0]))
    n_vmax = WHEEL_RPM_VMAX * G
    P_v = float(np.interp(n_vmax, NG, P))
    T_start_req = T_START_WHEEL / G
    return dict(gear_ratio=G, n_at_vmax_rpm=n_vmax, T_peak_Nm=Tpk, T_start_required_Nm=T_start_req,
                meets_start_grade=bool(Tpk >= T_start_req * 0.999), max_start_grade_pct=T3.max_start_grade(Tpk, G),
                n_base_rpm=float(NG[ib]), P_base_W=Pb,
                CPSR=float(NG[icp] / NG[ib]), CPSR_capped_by_eval_range=bool(icp == len(NG) - 1),
                CPSR_needed_for_vehicle=float(n_vmax / NG[ib]),
                P_at_vmax_W=P_v, T_peak_per_leg_A_Nm_per_A=Tpk / IMAX0,
                wheel_force_per_leg_A_N_per_A=Tpk * G * T3.VEH["eta_gear"] / T3.VEH["wheel_radius_m"] / IMAX0,
                inverter_kVA_per_kW_base=S_INV_kVA / (Pb / 1e3))


def best_gear(T, NG, n_tip):
    """Highest P at v_max among gears that meet the start torque and the tip-speed limit."""
    Tpk = T.max()
    G_min = T_START_WHEEL / Tpk                              # start-torque bound (needs G >= G_min)
    G_max = min(n_tip, NG[-1]) / WHEEL_RPM_VMAX              # speed bound
    Gs = np.linspace(4.0, 22.0, 721)
    ok = (Gs >= G_min * 0.999) & (Gs <= G_max)
    Pv = np.interp(WHEEL_RPM_VMAX * Gs, NG, T * NG * RPM)
    if not np.any(ok):
        return None, float(G_min), float(G_max)
    j = int(np.argmax(np.where(ok, Pv, -1)))
    return float(Gs[j]), float(G_min), float(G_max)


# ----------------------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------------------
NG_FAST = np.linspace(10.0, 9000.0, 91)
NG_FULL = np.linspace(10.0, 9000.0, 450)
SEARCH = dict(R_gap_m=np.linspace(0.12, 0.19, 15).tolist(), B_design_T=[0.5, 0.6, 0.7, 0.8, 0.88],
              N_leg_turns=np.linspace(1.5, 9.0, 16).tolist())
LAYOUT = {2: dict(Q=48, y=10, cpl=1), 3: dict(Q=144, y=20, cpl=3)}   # y = 5/6 pole pitch


def search(p):
    lay = LAYOUT[p]
    rows = []
    for R in SEARCH["R_gap_m"]:
        for Bd in SEARCH["B_design_T"]:
            for N in SEARCH["N_leg_turns"]:
                d = make_design(p, lay["Q"], lay["y"], lay["cpl"], R, Bd, N)
                if d is None:
                    continue
                T = envelope(d, NG_FAST, n_psi=60, n_sl=90)
                G, Gmin, Gmax = best_gear(T, NG_FAST, d["n_tip_limit_rpm"])
                Pv = float(np.interp(WHEEL_RPM_VMAX * G, NG_FAST, T * NG_FAST * RPM)) if G else -1.0
                # at the T03 gear ratio
                Pv98 = float(np.interp(WHEEL_RPM_VMAX * G_REF, NG_FAST, T * NG_FAST * RPM))
                rows.append(dict(R=R, Bd=Bd, N=N, Tpk=float(T.max()), G=G, Gmin=Gmin, Gmax=Gmax, Pv=Pv,
                                 Pv98=Pv98, start98=bool(T.max() >= T3.T_START), wheelT=float(T.max()) * G_REF))
    return rows


def refine(p, R, Bd, N, label):
    lay = LAYOUT[p]
    best = None
    for dR in (-0.0025, 0.0, 0.0025):
        for dN in (-0.25, 0.0, 0.25):
            d = make_design(p, lay["Q"], lay["y"], lay["cpl"], R + dR, Bd, N + dN, name=label)
            if d is None:
                continue
            T = envelope(d, NG_FULL)
            G, _, _ = best_gear(T, NG_FULL, d["n_tip_limit_rpm"])
            if G is None:
                continue
            Pv = float(np.interp(WHEEL_RPM_VMAX * G, NG_FULL, T * NG_FULL * RPM))
            if best is None or Pv > best[0]:
                best = (Pv, d, T, G)
    return best


def current_for_start(d, G, target_T):
    """Inverter current factor needed for T_peak >= target (low-speed, flux-capped)."""
    lo, hi = 0.5, 4.0
    f = lambda k: envelope(d, np.array([50.0]), I_max=IMAX0 * k)[0] - target_T
    if f(hi) < 0:
        return None
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return hi


def report_machine(d, T, G, label, extra=None):
    m = metrics(T, NG_FULL, G)
    n_cr, T_cr = CRUISE_WHEEL_RPM * G, CRUISE_WHEEL_T / G
    cr = min_loss(d, n_cr, T_cr)
    out = dict(label=label, metrics=m,
               cruise_85kmh=cr if cr else dict(speed_rpm=n_cr, torque_Nm=T_cr, feasible=False),
               design={k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in d.items()},
               torque_Nm=T.round(2).tolist())
    m_full = metrics(T, NG_FULL, G)
    T_N = T3.INV["P_rated_W"] / (m_full["n_base_rpm"] * RPM)
    out["realistic_losses"] = dict(T_N_Nm=T_N, points=realistic_set({f"2p{2 * d['p']}": d}, G, {f"2p{2 * d['p']}": T_N}))
    if extra:
        out.update(extra)
    return out


def main():
    res = dict(meta=dict(script="02_analytics/fair_baselines.py", task="T03b", date=_dt.date.today().isoformat(),
                         P_rated_W=T3.INV["P_rated_W"],
                         inputs=["02_analytics/torque_speed_envelope.py (constants, T03 design; T03 JSON not modified)",
                                 T03_JSON.replace(ROOT + os.sep, "").replace(os.sep, "/"),
                                 "board/decisions.md D02 (provisional, 350 kW)"],
                         assumptions="02_analytics/assumptions.md#t03b",
                         constraints=dict(R_out_m=R_OUT, L_stk_m=L_STK, copper_mass_kg=ST["copper_mass_kg"],
                                          V_ph_rms_max_V=VMAX, I_module_rms_max_A=IMAX0, S_inverter_kVA=S_INV_kVA,
                                          rotor_tip_speed_max_m_s=TIP_SPEED_MAX, B_yoke_max_T=B_Y_MAX,
                                          B_tooth_max_T=B_T_MAX, B_gap_max_T=B_G_MAX),
                         vehicle_requirements=dict(start_12pct_wheel_side_torque_Nm=T_START_WHEEL,
                                                   wheel_rpm_at_90kmh=WHEEL_RPM_VMAX,
                                                   cruise_wheel_side_torque_Nm=CRUISE_WHEEL_T,
                                                   note="motor torque = value / G; motor speed = wheel rpm x G"),
                         search_grid=SEARCH, layouts=LAYOUT,
                         objective="max P at 90 km/h subject to 12 % start torque and rotor tip speed; gear ratio free",
                         notes=["Fixed-pole machines use SPB coil-phase feeding (k_d = 1): at least as good as a 3-phase belt winding.",
                                "N_leg is continuous (effective series turns per leg); integer rounding = small change of stack/turn choice.",
                                "2p=6 is not realisable on 48 slots with 16 three-phase modules (p divisible by 3 puts a module's 3 coils in phase). "
                                "It needs Q=144 with 3 coils in series per leg (coils 120 deg mech apart, same phase).",
                                "Efficiency is machine only (no inverter, no gearbox)."]))
    machines = {}
    search_summary = {}
    for p in (2, 3):
        rows = search(p)
        feas = [r for r in rows if r["G"] is not None]
        top = max(feas, key=lambda r: r["Pv"])
        feas98 = [r for r in rows if r["start98"]]
        top98 = max(feas98, key=lambda r: r["Pv98"]) if feas98 else None
        best_any98 = max(rows, key=lambda r: r["Pv98"])
        search_summary[f"2p{2 * p}"] = dict(n_designs=len(rows), n_feasible_free_gear=len(feas),
                                           best_free_gear=top, best_at_G98_meeting_start=top98,
                                           n_meeting_start_at_G98=len(feas98), best_P_at_G98_ignoring_start=best_any98)
        Pv, d, T, G = refine(p, top["R"], top["Bd"], top["N"], f"fixed_2p{2 * p}")
        extra = {}
        # same machine at the T03 gear ratio
        extra["at_G_9p80"] = metrics(T, NG_FULL, G_REF)
        if T.max() < T3.T_START:
            k = current_for_start(d, G_REF, T3.T_START)
            extra["at_G_9p80"]["current_factor_needed_for_start"] = k
            extra["at_G_9p80"]["inverter_kVA_needed_for_start"] = None if k is None else k * S_INV_kVA
        # two-speed gearbox: low gear for start, high gear for v_max
        G_low = T_START_WHEEL / T.max()
        Gs = np.linspace(4.0, min(d["n_tip_limit_rpm"], NG_FULL[-1]) / WHEEL_RPM_VMAX, 400)
        Pv_all = np.interp(WHEEL_RPM_VMAX * Gs, NG_FULL, T * NG_FULL * RPM)
        G_high = float(Gs[int(np.argmax(Pv_all))])
        extra["two_speed_gearbox"] = dict(G_low=float(G_low), G_high=G_high, ratio_spread=float(G_low / G_high) if G_high else None,
                                          P_at_vmax_high_gear_W=float(Pv_all.max()),
                                          note="G_low just meets the 12 % start; G_high maximises P at 90 km/h (tip-speed limited)")
        machines[f"fixed_2p{2 * p}"] = report_machine(d, T, G, f"fixed 2p={2 * p}, own design, gear optimised", extra)

    # (3) T03 pole-changing IM, unchanged, G = 9.80
    d8, d4 = t03_pc_design(4), t03_pc_design(2)
    T8, T4 = envelope(d8, NG_FULL, n_psi=260, n_sl=500), envelope(d4, NG_FULL, n_psi=260, n_sl=500)
    Tc = np.maximum(T8, T4)
    m = metrics(Tc, NG_FULL, G_REF)
    n_cr, T_cr = T3.N_CRUISE, T3.T_CRUISE
    cr = min_loss(d4, n_cr, T_cr)
    t03 = json.load(open(T03_JSON))
    ref = t03["machines"]["IM"]["combined"]["metrics"]
    machines["pole_changing_2p8_4_T03"] = dict(
        label="SPB pole-changing IM 2p=8/4 (T03 design, unchanged), G = 9.80", metrics=m,
        crossover_speed_rpm=T3.crossover(T8, T4),
        cruise_85kmh=dict(mode="2p=4", **cr),
        design={"2p8": {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in d8.items()},
                "2p4": {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in d4.items()}},
        reproduces_T03=dict(T_peak_Nm=[m["T_peak_Nm"], ref["T_peak_Nm"]], P_at_vmax_W=[m["P_at_vmax_W"], ref["P_at_vmax_W"]],
                            CPSR=[m["CPSR"], ref["CPSR"]],
                            cruise_eta=[cr["eta"], t03["efficiency_points"]["cruise_85kmh_road_load"]["IM_2p4"]["eta"]]),
        torque_Nm=Tc.round(2).tolist())
    TN8 = T3.INV["P_rated_W"] / (metrics(T8, NG_FULL, G_REF)["n_base_rpm"] * RPM)
    TN4 = T3.INV["P_rated_W"] / (metrics(T4, NG_FULL, G_REF)["n_base_rpm"] * RPM)
    machines["pole_changing_2p8_4_T03"]["realistic_losses"] = dict(
        T_N_Nm={"2p8": TN8, "2p4": TN4}, points=realistic_set({"2p8": d8, "2p4": d4}, G_REF, {"2p8": TN8, "2p4": TN4}))
    # PC IM with its gear also optimised (for symmetry with the baselines)
    Gpc, _, _ = best_gear(Tc, NG_FULL, d8["n_tip_limit_rpm"])
    machines["pole_changing_2p8_4_T03"]["with_gear_optimised"] = metrics(Tc, NG_FULL, Gpc) if Gpc else None

    # summary table
    def row(k):
        mm = machines[k]["metrics"]
        c = machines[k]["cruise_85kmh"]
        return dict(gear_ratio=mm["gear_ratio"], T_peak_Nm=mm["T_peak_Nm"], meets_start=mm["meets_start_grade"],
                    CPSR=mm["CPSR"], CPSR_capped=mm["CPSR_capped_by_eval_range"], P_at_90kmh_kW=mm["P_at_vmax_W"] / 1e3,
                    max_start_grade_pct=mm["max_start_grade_pct"],
                    cruise_eta=c.get("eta"), cruise_eta_excl_fw=c.get("eta_excl_friction_windage"), cruise_PF=c.get("PF"), cruise_I_rms_A=c.get("I_rms_A"),
                    T_per_leg_A_Nm_per_A=mm["T_peak_per_leg_A_Nm_per_A"],
                    wheel_force_per_leg_A_N_per_A=mm["wheel_force_per_leg_A_N_per_A"],
                    inverter_kVA_per_kW_base=mm["inverter_kVA_per_kW_base"])
    res["summary"] = {k: row(k) for k in machines}
    if Gpc:
        mg = machines["pole_changing_2p8_4_T03"]["with_gear_optimised"]
        crg = min_loss(d4, CRUISE_WHEEL_RPM * Gpc, CRUISE_WHEEL_T / Gpc)
        machines["pole_changing_2p8_4_T03"]["realistic_losses_gear_optimised"] = realistic_set(
            {"2p8": d8, "2p4": d4}, Gpc, {"2p8": TN8, "2p4": TN4})
        res["summary"]["pole_changing_2p8_4_gear_optimised"] = dict(
            gear_ratio=Gpc, T_peak_Nm=mg["T_peak_Nm"], meets_start=mg["meets_start_grade"], max_start_grade_pct=mg["max_start_grade_pct"],
            CPSR=mg["CPSR"], CPSR_capped=mg["CPSR_capped_by_eval_range"], P_at_90kmh_kW=mg["P_at_vmax_W"] / 1e3,
            cruise_eta=crg["eta"] if crg else None, cruise_eta_excl_fw=crg["eta_excl_friction_windage"] if crg else None,
            cruise_PF=crg["PF"] if crg else None, cruise_I_rms_A=crg["I_rms_A"] if crg else None,
            T_per_leg_A_Nm_per_A=mg["T_peak_per_leg_A_Nm_per_A"], wheel_force_per_leg_A_N_per_A=mg["wheel_force_per_leg_A_N_per_A"],
            inverter_kVA_per_kW_base=mg["inverter_kVA_per_kW_base"],
            note="Same T03 machine, gear ratio chosen by the same rule as the fixed-pole baselines")
    res["search_summary"] = search_summary
    rs = {}
    for k, v in machines.items():
        rs[k] = {}
        for pn, r in v["realistic_losses"]["points"].items():
            if r.get("feasible") is False:
                rs[k][pn] = None
                continue
            fo, rf = r["flux_optimised"], r["rated_flux"]
            rs[k][pn] = dict(mode=r["mode"], speed_rpm=r["speed_rpm"], torque_Nm=r["torque_Nm"], T_over_T_N=r["torque_over_T_N"],
                             eta_simple_T03_model=r["eta_simple_T03_model"], eta_realistic_flux_opt=fo["eta"],
                             eta_realistic_rated_flux=rf["eta"], eta_realistic_flux_opt_stray_x2=r["eta_flux_optimised_stray_x2"],
                             eta_realistic_excl_friction_windage=fo["eta_excl_friction_windage"],
                             PF_flux_opt=fo["PF"], PF_rated_flux=rf["PF"],
                             losses_flux_opt_W={kk: fo[kk] for kk in ("P_cu_stator_W", "P_cu_stator_magnetising_share_W", "P_cu_rotor_W",
                                                                       "P_fe_W", "P_stray_IEC_W", "P_pwm_W", "P_mech_W")},
                             slip=fo["slip"], bar_kR_at_slip=fo["bar_kR_at_slip"])
    if "realistic_losses_gear_optimised" in machines["pole_changing_2p8_4_T03"]:
        rs["pole_changing_2p8_4_gear_optimised"] = {
            pn: (None if r.get("feasible") is False else dict(mode=r["mode"], eta_realistic_flux_opt=r["flux_optimised"]["eta"],
                                                              eta_realistic_rated_flux=r["rated_flux"]["eta"],
                                                              PF_flux_opt=r["flux_optimised"]["PF"]))
            for pn, r in machines["pole_changing_2p8_4_T03"]["realistic_losses_gear_optimised"].items()}
    res["realistic_loss_summary"] = rs
    res["realistic_loss_model"] = dict(
        stray_load="IEC 60034-2-1 assumed allowance P_LL,N = P1,N (0.025 - 0.005 log10(P2,N/1 kW)), scaled (T/T_N)^2; T_N = P_rated / omega_base of the active mode; sensitivity x2",
        P_LL_rated_W=iec_stray_allowance_W(T3.INV["P_rated_W"]),
        rotor_skin="deep rectangular bar, h_bar = 25 mm x (R/165 mm), k_R(xi) on the bar part of R_r at slip frequency and at f_sw; ring x5 at f_sw",
        magnetising_copper="included in |I_s|; magnetising share 48 I_m^2 R_s reported",
        pwm=dict(f_sw_Hz=F_SW_HZ, ripple="dI_pp = V_mod/(4 L_hf f_sw), L_hf = 0.5 (L_s,sigma + L_r,sigma), triangular rms",
                 k_ac_stator=K_AC_STATOR_HF, k_ring=K_RING_HF, tooth_eddy="Bertotti eddy term at f_sw with lamination skin correction, mu_r = 1000"),
        flux_strategies="flux_optimised = loss-minimising flux; rated_flux = highest feasible flux (cap or voltage-limited)",
        excluded=["gearbox losses (eta_gear = 0.97 constant, independent of ratio)", "inverter losses", "rotor iron loss", "temperature feedback"])
    res["speed_rpm"] = NG_FULL.round(3).tolist()
    res["machines"] = machines
    # sanity: T03 design through the new generic code
    res["sanity_checks"] = dict(T03_design_reproduced_rel_err_T_peak=abs(m["T_peak_Nm"] / ref["T_peak_Nm"] - 1),
                                T03_design_reproduced_rel_err_P_vmax=abs(m["P_at_vmax_W"] / ref["P_at_vmax_W"] - 1),
                                T03_slot_width_recovered_m=d8["b_slot_m"], T03_lambda_ratio_is_1=True)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res["summary"], indent=1, default=float))
    print(json.dumps(res["sanity_checks"], indent=1, default=float))
    for k, v in machines.items():
        print(k, {kk: v.get(kk) for kk in ("at_G_9p80", "two_speed_gearbox") if kk in v})
        dd = v["design"] if "R_gap_m" in v["design"] else v["design"]["2p8"]
        print("  design:", {kk: round(dd[kk], 4) if isinstance(dd[kk], float) else dd[kk] for kk in
                            ("R_gap_m", "h_yoke_m", "h_slot_m", "b_slot_m", "N_leg_turns", "k_w", "B_gap_cap_T", "J_at_Imax_A_mm2", "n_tip_limit_rpm")})
    for k, v in search_summary.items():
        print(k, json.dumps(v, default=float))


if __name__ == "__main__":
    main()

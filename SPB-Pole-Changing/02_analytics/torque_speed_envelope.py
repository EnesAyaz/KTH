"""T03 - First-pass analytical torque-speed envelopes, SPB-driven IM / PMSM / WRSM,
with and without electronic pole changing, under identical SPB module limits.

Run from repo root:  python 02_analytics/torque_speed_envelope.py
Outputs:
  02_analytics/results/torque_speed_envelope.json
  02_analytics/scratch/torque_speed_envelope_quicklook.png
Assumptions: 02_analytics/assumptions.md (section T03).

Model frame
-----------
Stator: Q = 48 slots, 48 identical double-layer lap coils (N_c turns, pitch y slots).
SPB module j (j = 0..15) is a three-phase bridge that feeds coils j, j+16, j+32
(120 deg mechanical apart) in star with an isolated neutral. Coil k carries current
with electrical phase alpha_k = p * 2*pi*k/Q, so the pole-pair number p is set by the
modulation alone. Module currents sum to zero for every p not divisible by 3.
The machine is treated as an m = 48 "coil-phase" machine: every coil is one phase
with its own per-phase equivalent circuit (rms phasors), all coils identical.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "02_analytics", "results", "torque_speed_envelope.json")
OUT_PNG = os.path.join(ROOT, "02_analytics", "scratch", "torque_speed_envelope_quicklook.png")

MU0 = 4e-7 * math.pi
SQ2 = math.sqrt(2.0)
RPM = 2 * math.pi / 60.0

# ----------------------------------------------------------------------------------
# 1. Inverter (SPB) limits - identical for all machines
# ----------------------------------------------------------------------------------
INV = dict(
    V_dc_V=1200.0,
    N_modules=16,
    m_margin=0.95,          # usable fraction of SVPWM linear limit (dead time, min pulse, control margin)
    P_rated_W=350e3,        # D02 continuous drive power
    PF_ref=0.85,            # reference power factor used only to size the current limit
    eta_ref=0.95,           # reference machine efficiency used only to size the current limit
)
INV["V_module_V"] = INV["V_dc_V"] / INV["N_modules"]
INV["V_ph_peak_max_V"] = INV["m_margin"] * INV["V_module_V"] / math.sqrt(3.0)  # SVPWM: V_ph,pk <= V_dc/sqrt3
INV["V_ph_rms_max_V"] = INV["V_ph_peak_max_V"] / SQ2
M_PH = 3 * INV["N_modules"]  # 48 coil-phases
INV["I_module_rms_max_A"] = INV["P_rated_W"] / (M_PH * INV["V_ph_rms_max_V"] * INV["PF_ref"] * INV["eta_ref"])
INV["I_module_peak_max_A"] = INV["I_module_rms_max_A"] * SQ2
INV["S_total_max_VA"] = M_PH * INV["V_ph_rms_max_V"] * INV["I_module_rms_max_A"]
VMAX = INV["V_ph_rms_max_V"]
IMAX = INV["I_module_rms_max_A"]

# ----------------------------------------------------------------------------------
# 2. Vehicle (D02 provisional) - parameters from ../Drive Cycle/basic_vehicle_dynamics.m
# ----------------------------------------------------------------------------------
VEH = dict(mass_kg=40e3, wheel_radius_m=0.52, frontal_area_m2=10.5, Cd=0.7, Crr=0.01,
           rho_air_kg_m3=1.225, mass_factor=1.05, g_m_s2=9.81, eta_gear=0.97,
           v_max_kmh=90.0, n_motor_at_vmax_rpm=4500.0, v_cruise_kmh=85.0, grade_start_pct=12.0)
_wheel_rpm_vmax = VEH["v_max_kmh"] / 3.6 / VEH["wheel_radius_m"] / RPM
VEH["gear_ratio"] = VEH["n_motor_at_vmax_rpm"] / _wheel_rpm_vmax


def road_load(v_kmh, grade_pct=0.0):
    v = v_kmh / 3.6
    a = math.atan(grade_pct / 100.0)
    F = (VEH["Crr"] * VEH["mass_kg"] * VEH["g_m_s2"] * math.cos(a)
         + 0.5 * VEH["Cd"] * VEH["rho_air_kg_m3"] * VEH["frontal_area_m2"] * v ** 2
         + VEH["mass_kg"] * VEH["g_m_s2"] * math.sin(a))
    n_m = v / VEH["wheel_radius_m"] * VEH["gear_ratio"] / RPM
    T_m = F * VEH["wheel_radius_m"] / VEH["gear_ratio"] / VEH["eta_gear"]
    return F, n_m, T_m


F_cr, N_CRUISE, T_CRUISE = road_load(VEH["v_cruise_kmh"])
F_st, _, T_START = road_load(1e-6, VEH["grade_start_pct"])
VEH.update(cruise_force_N=F_cr, cruise_motor_speed_rpm=N_CRUISE, cruise_motor_torque_Nm=T_CRUISE,
           cruise_power_wheel_W=F_cr * VEH["v_cruise_kmh"] / 3.6,
           start_grade_motor_torque_Nm=T_START)

# ----------------------------------------------------------------------------------
# 3. Common stator (same outer size and copper volume for all three machines)
# ----------------------------------------------------------------------------------
ST = dict(Q=48, R_gap_m=0.165, L_stk_m=0.36, g_m=1.0e-3, kc_ksat=1.30, slot_w_m=9e-3, slot_h_m=45e-3,
          yoke_h_m=25e-3, fill=0.60, N_c=3, y_slots=7, rho_cu_ohm_m=2.40e-8,  # Cu at ~120 C
          end_ext_m=0.02, lam_slot_self=1.2, lam_slot_mut=0.4, lam_end=0.3,
          B_yoke_max_T=1.45, B_gap_max_T=0.90, rho_fe_kg_m3=7650.0)
ST["g_eff_m"] = ST["g_m"] * ST["kc_ksat"]
ST["slot_pitch_m"] = 2 * math.pi * ST["R_gap_m"] / ST["Q"]
ST["tooth_w_m"] = ST["slot_pitch_m"] - ST["slot_w_m"]
ST["R_out_m"] = ST["R_gap_m"] + ST["slot_h_m"] + ST["yoke_h_m"]
ST["A_turn_m2"] = ST["slot_w_m"] * ST["slot_h_m"] * ST["fill"] / 2 / ST["N_c"]
_Dmid = 2 * ST["R_gap_m"] + ST["slot_h_m"]
ST["l_end_half_m"] = 1.2 * math.pi * _Dmid * ST["y_slots"] / ST["Q"] + 2 * ST["end_ext_m"]
ST["l_turn_m"] = 2 * (ST["L_stk_m"] + ST["l_end_half_m"])
ST["R_coil_ohm"] = ST["rho_cu_ohm_m"] * ST["N_c"] * ST["l_turn_m"] / ST["A_turn_m2"]
ST["copper_mass_kg"] = ST["Q"] * ST["N_c"] * ST["A_turn_m2"] * ST["l_turn_m"] * 8900.0
ST["m_teeth_kg"] = ST["Q"] * ST["tooth_w_m"] * ST["slot_h_m"] * ST["L_stk_m"] * ST["rho_fe_kg_m3"]
ST["m_yoke_kg"] = math.pi * (ST["R_out_m"] ** 2 - (ST["R_out_m"] - ST["yoke_h_m"]) ** 2) * ST["L_stk_m"] * ST["rho_fe_kg_m3"]
ST["J_at_Imax_A_mm2"] = IMAX / (ST["A_turn_m2"] * 1e6)

# Iron loss: Bertotti-style two-term fit to M270-35A (2.7 W/kg @1.5T/50Hz, 17.5 W/kg @1.0T/400Hz)
FE = dict(k_h=None, k_e=None, build_factor=1.5)
_A = np.array([[50 * 1.5 ** 2, 50 ** 2 * 1.5 ** 2], [400 * 1.0, 400 ** 2 * 1.0]])
FE["k_h"], FE["k_e"] = [float(x) for x in np.linalg.solve(_A, np.array([2.7, 17.5]))]


def p_mech(n_rpm):
    """Friction + windage, same for all machines (W)."""
    x = np.asarray(n_rpm) / 4500.0
    return 500.0 * x + 1000.0 * x ** 3


# ----------------------------------------------------------------------------------
# 4. Winding: coil -> module mapping, MMF harmonics, winding factor per p
# ----------------------------------------------------------------------------------
def coil_phases(p, Q=ST["Q"]):
    return p * 2 * np.pi * np.arange(Q) / Q


def module_current_sum(p):
    a = coil_phases(p)
    n = INV["N_modules"]
    s = [abs(np.exp(1j * a[j]) + np.exp(1j * a[j + n]) + np.exp(1j * a[j + 2 * n])) for j in range(n)]
    return float(max(s))


def mmf_spectrum(coil_angle, coil_sign_slots, n_theta=4096, nu_max=200):
    """Instantaneous MMF (t=0) of coils. coil_sign_slots: list of (go_slot, return_slot, N, i)."""
    Q = ST["Q"]
    th = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    F = np.zeros(n_theta)
    slot_pos = 2 * np.pi * (np.arange(Q) + 0.5) / Q
    # conductor current in each slot
    Islot = np.zeros(Q)
    for go, ret, N, i in coil_sign_slots:
        Islot[go % Q] += N * i
        Islot[ret % Q] -= N * i
    # MMF = cumulative sum of slot currents (zero mean)
    for s in range(Q):
        F += Islot[s] * (th >= slot_pos[s])
    F -= F.mean()
    c = np.fft.rfft(F) / n_theta * 2
    return np.abs(c[: nu_max + 1])


def spb_mmf(p, Ipk=1.0):
    """Rotating MMF of the SPB stator set to pole-pair p, harmonics by order."""
    Q, y, N = ST["Q"], ST["y_slots"], ST["N_c"]
    a = coil_phases(p)
    coils = [(k, k + y, N, Ipk * math.cos(a[k])) for k in range(Q)]
    return mmf_spectrum(a, coils)


def winding_factor_numeric(p):
    """k_w from MMF: F_p = m N_c k_w I_pk / (pi p) for an m coil-phase set."""
    F = spb_mmf(p)
    return F[p] * math.pi * p / (M_PH * ST["N_c"]), F


def winding_factor_analytic(p):
    return abs(math.sin(p * ST["y_slots"] * math.pi / ST["Q"]))


def conventional_three_phase_kw(p=4, y=5):
    """Reference: conventional 3-phase, 48-slot, 2p=8 (q=2), double layer, pitch y; same MMF routine."""
    Q = ST["Q"]
    q = Q // (2 * p * 3)
    # 60-deg phase belts: A, -C, B, -A, C, -B
    belt = [(0, +1), (2, -1), (1, +1), (0, -1), (2, +1), (1, -1)]
    I = [math.cos(0), math.cos(-2 * math.pi / 3), math.cos(-4 * math.pi / 3)]
    coils = []
    for k in range(Q):
        ph, sg = belt[(k // q) % 6]
        coils.append((k, k + y, 1, sg * I[ph]))
    F = mmf_spectrum(None, coils)
    N_ph = Q // 3  # one turn per coil, all coils of a phase in series
    # 3-phase: F_p = (3/2)(4/pi) N_ph k_w I /(2p)
    kw = F[p] / (1.5 * 4 / math.pi * N_ph / (2 * p))
    kd = math.sin(math.pi / 6) / (q * math.sin(math.pi / (6 * q)))
    kp = math.sin(y / (Q / (2 * p)) * math.pi / 2)
    return float(kw), float(kd * kp)


def differential_leakage_coeff(p):
    _, F = winding_factor_numeric(p)
    F = F.copy()
    Fp = F[p]
    F[p] = 0.0
    F[0] = 0.0
    return float(np.sum(F ** 2) / Fp ** 2)


# ----------------------------------------------------------------------------------
# 5. Per-p stator electrical parameters (per coil-phase, rms)
# ----------------------------------------------------------------------------------
def stator_params(p):
    kw = winding_factor_analytic(p)
    Nk = ST["N_c"] * kw
    RL = ST["R_gap_m"] * ST["L_stk_m"]
    Lm = 2 * M_PH * MU0 * RL * Nk ** 2 / (math.pi * ST["g_eff_m"] * p ** 2)  # synchronous magnetising, per coil
    Lm_unsat = Lm * ST["kc_ksat"] / 1.05                                       # for harmonic leakage (k_c only)
    L_slot = 2 * MU0 * ST["N_c"] ** 2 * ST["L_stk_m"] * (
        ST["lam_slot_self"] - ST["lam_slot_mut"] * math.cos(2 * math.pi * p * ST["y_slots"] / ST["Q"]))
    L_end = MU0 * ST["N_c"] ** 2 * 2 * ST["l_end_half_m"] * ST["lam_end"]
    sig_d = differential_leakage_coeff(p)
    L_diff = sig_d * Lm_unsat
    B_cap = min(ST["B_gap_max_T"], ST["B_yoke_max_T"] * ST["yoke_h_m"] * p / ST["R_gap_m"])
    # flux linkage per coil (rms) per tesla of fundamental airgap peak:  psi_pk = 2 N_c k_w B R L / p
    psi_per_T = 2 * Nk * RL / p / SQ2
    return dict(p=p, k_w=kw, Lm_H=Lm, L_slot_H=L_slot, L_end_H=L_end, sigma_diff=sig_d, L_diff_H=L_diff,
                L_sigma_s_H=L_slot + L_end + L_diff, R_s_ohm=ST["R_coil_ohm"], B_gap_cap_T=B_cap,
                psi_rms_per_T=psi_per_T, psi_cap_rms_Wb=B_cap * psi_per_T)


def iron_loss(f_Hz, B_gap_T, p):
    """Stator teeth + yoke, fundamental only (W)."""
    Bt = B_gap_T * ST["slot_pitch_m"] / ST["tooth_w_m"]
    By = B_gap_T * ST["R_gap_m"] / (p * ST["yoke_h_m"])
    f = np.abs(f_Hz)
    spec = lambda B: FE["k_h"] * f * B ** 2 + FE["k_e"] * f ** 2 * B ** 2
    return FE["build_factor"] * (ST["m_teeth_kg"] * spec(Bt) + ST["m_yoke_kg"] * spec(By))


# ----------------------------------------------------------------------------------
# 6. Induction machine (copper cage, Q_r = 58)
# ----------------------------------------------------------------------------------
IMR = dict(Q_r=58, bar_area_m2=150e-6, bar_len_m=0.38, ring_area_m2=600e-6, ring_diam_m=0.27,
           rho_cage_ohm_m=2.57e-8, lam_bar=1.5, lam_ring=0.3)


def im_params(p):
    s = stator_params(p)
    Qr = IMR["Q_r"]
    sin_a = math.sin(math.pi * p / Qr)
    R_bar = IMR["rho_cage_ohm_m"] * IMR["bar_len_m"] / IMR["bar_area_m2"]
    l_seg = math.pi * IMR["ring_diam_m"] / Qr
    R_seg = IMR["rho_cage_ohm_m"] * l_seg / IMR["ring_area_m2"]
    K = 4 * M_PH * (ST["N_c"] * s["k_w"]) ** 2 / Qr
    R_r = K * (R_bar + R_seg / (2 * sin_a ** 2))
    L_bar = MU0 * ST["L_stk_m"] * IMR["lam_bar"]
    L_seg = MU0 * l_seg * IMR["lam_ring"]
    sig_dr = ((math.pi * p / Qr) / sin_a) ** 2 - 1.0
    L_r = K * (L_bar + L_seg / (2 * sin_a ** 2)) + sig_dr * s["Lm_H"]
    s.update(R_r_ohm=R_r, L_sigma_r_H=L_r, ring_share_of_Rr=(R_seg / (2 * sin_a ** 2)) / (R_bar + R_seg / (2 * sin_a ** 2)),
             sigma_diff_rotor=sig_dr, K_ref=K)
    return s


def im_state(par, n_rpm, psi, wsl, m=M_PH, Rs=None, Ls=None, Lm=None, Rr=None, Lr=None):
    """Vectorised IM per-phase solution; psi = rms airgap flux linkage per phase."""
    p = par["p"]
    Rs = par["R_s_ohm"] if Rs is None else Rs
    Ls = par["L_sigma_s_H"] if Ls is None else Ls
    Lm = par["Lm_H"] if Lm is None else Lm
    Rr = par["R_r_ohm"] if Rr is None else Rr
    Lr = par["L_sigma_r_H"] if Lr is None else Lr
    wm = n_rpm * RPM
    we = p * wm + wsl
    E = 1j * we * psi
    with np.errstate(invalid="ignore", divide="ignore"):
        Ir = psi * wsl / (Rr + 1j * wsl * Lr) * 1j          # in phase with E for small slip
    Im = psi / Lm + 0j
    Is = Im + Ir
    V = E + (Rs + 1j * we * Ls) * Is
    with np.errstate(invalid="ignore", divide="ignore"):
        T = m * p * np.abs(Ir) ** 2 * Rr / np.where(wsl > 0, wsl, np.inf)
    return dict(we=we, Is=np.abs(Is), Ir=np.abs(Ir), V=np.abs(V), T=T)


def im_envelope(par, n_grid, n_psi=260, n_sl=500):
    Rr, Lr = par["R_r_ohm"], par["L_sigma_r_H"]
    w_bd = Rr / Lr
    wsl = np.geomspace(w_bd * 1e-4, w_bd, n_sl)[None, :]
    T = np.zeros_like(n_grid)
    for i, n in enumerate(n_grid):
        # flux grid bounded by the cap and by the voltage-limited flux (E <= V, with 10 % margin)
        psi_hi = min(par["psi_cap_rms_Wb"], 1.1 * VMAX / (par["p"] * n * RPM))
        psi = np.linspace(psi_hi / n_psi, psi_hi, n_psi)[:, None]
        st = im_state(par, n, psi, wsl)
        ok = (st["V"] <= VMAX) & (st["Is"] <= IMAX)
        T[i] = np.max(np.where(ok, st["T"], 0.0))
    return T


def im_min_loss(par, n_rpm, T_req, n_psi=400):
    p = par["p"]
    Rr, Lr = par["R_r_ohm"], par["L_sigma_r_H"]
    psi = np.linspace(par["psi_cap_rms_Wb"] / n_psi, par["psi_cap_rms_Wb"], n_psi)
    a = T_req * Lr ** 2
    b = -M_PH * p * psi ** 2 * Rr
    c = T_req * Rr ** 2
    disc = b ** 2 - 4 * a * c
    good = disc >= 0
    wsl = np.where(good, (-b - np.sqrt(np.where(good, disc, 0))) / (2 * a), np.nan)
    st = im_state(par, n_rpm, psi, wsl)
    ok = good & (st["V"] <= VMAX) & (st["Is"] <= IMAX)
    if not np.any(ok):
        return None
    B = psi / par["psi_rms_per_T"]
    P_cus = M_PH * st["Is"] ** 2 * par["R_s_ohm"]
    P_cur = M_PH * st["Ir"] ** 2 * Rr
    P_fe = iron_loss(st["we"] / (2 * np.pi), B, p)
    P_m = float(p_mech(n_rpm))
    loss = np.where(ok, P_cus + P_cur + P_fe, np.inf)
    j = int(np.argmin(loss))
    P_out = T_req * n_rpm * RPM - P_m
    tot = float(loss[j]) + P_m
    P_in_st = P_out + tot
    return dict(eta=P_out / (P_out + tot), PF=P_in_st / (M_PH * float(st["V"][j]) * float(st["Is"][j])),
                S_inverter_used_kVA=M_PH * float(st["V"][j]) * float(st["Is"][j]) / 1e3, P_shaft_W=P_out, P_cu_stator_W=float(P_cus[j]),
                P_cu_rotor_W=float(P_cur[j]), P_fe_W=float(P_fe[j]), P_field_W=0.0, P_mech_W=P_m,
                I_rms_A=float(st["Is"][j]), V_rms_V=float(st["V"][j]), B_gap_T=float(B[j]),
                f_e_Hz=float(st["we"][j] / (2 * np.pi)), slip=float(wsl[j] / st["we"][j]))


# ----------------------------------------------------------------------------------
# 7. Synchronous machines (PMSM, WRSM) - per-unit parameters on SPB base
# ----------------------------------------------------------------------------------
N_REF_RPM = 1200.0
P_REF = 4
W_REF = P_REF * N_REF_RPM * RPM
L_BASE = VMAX / (IMAX * W_REF)
PSI_BASE = VMAX / W_REF

PMSM_PU = dict(psi_pm=0.70, L_d=0.65, L_q=1.30)       # saturated effective values, IPM, 2p = 8
WRSM_PU = dict(psi_f_max=0.85, L_d=1.10, L_q=0.65, P_field_max_W=4000.0,
               pole_arc_ratio=0.70, rotor_yoke_margin=2.0,   # rotor yoke sized for the 2p=4 (++--) pattern, as in a PC-WFSM (P2 seed)
               L_f_stored_energy_leakage_factor=1.3, field_forcing_ratio=3.0, blanking_s=0.02)

# P2 seed (Ayaz/Tosun PC-WFSM draft, Airgap Harmonics/OPT-Workspace/config/draft_parameters.json) - DRAFT, unverified
P2_SEED = dict(source="Airgap Harmonics/OPT-Workspace/config/draft_parameters.json (status: unverified draft)",
               rated_output_W=10000, poles="4/2", f_e_both_modes_Hz=100, efficiency_4pole_pct=92.4, efficiency_2pole_pct=93.1,
               loss_4pole_W=822, loss_2pole_W=798, field_resistance_ohm=0.093, field_turns=24,
               implied_T_lowpole_over_T_highpole=0.5,
               note="Equal rated power at equal f_e in both modes implies the low-pole mode runs at 2x speed with ~0.5x torque. "
                    "Used only as the scaling seed for the WRSM rotor-yoke choice (rotor yoke sized for the low-pole pattern).")


def rotor_pole_pattern_harmonics(signs, arc_ratio, n_theta=7200, nu_max=60):
    """Fundamental-order amplitudes of the rotor field for 8 salient poles with given polarities (B0 = 1)."""
    npol = len(signs)
    th = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    B = np.zeros(n_theta)
    pitch = 2 * np.pi / npol
    for k, s in enumerate(signs):
        c = (k + 0.5) * pitch
        d = np.angle(np.exp(1j * (th - c)))
        B += s * (np.abs(d) <= arc_ratio * pitch / 2)
    c = np.fft.rfft(B) / n_theta * 2
    return np.abs(c[: nu_max + 1])


def wrsm_pole_change_factors():
    a = WRSM_PU["pole_arc_ratio"]
    h8 = rotor_pole_pattern_harmonics([+1, -1] * 4, a)
    h4 = rotor_pole_pattern_harmonics([+1, +1, -1, -1] * 2, a)   # poles 1,2,5,6 reversed
    s4, s2 = stator_params(4), stator_params(2)
    # flux linkage per coil per unit B0: psi = psi_per_T(p) * B_p
    psi8 = s4["psi_rms_per_T"] * h8[4]
    psi4 = s2["psi_rms_per_T"] * h4[2]
    # rotor-yoke cap: yoke flux in ++-- pattern = 2x the alternating pattern at equal B0
    i_cap = WRSM_PU["rotor_yoke_margin"] / 2.0
    # stator-yoke cap on the p=2 fundamental
    B2_at_cap = h4[2] * (WRSM_PU["psi_f_max"] * PSI_BASE / psi8) * i_cap
    i_cap = min(i_cap, i_cap * s2["B_gap_cap_T"] / B2_at_cap) if B2_at_cap > 0 else i_cap
    return dict(B_harm_8pole_rel=[float(h8[k]) for k in (4, 12, 20)],
                B_harm_4pole_rel={"nu2": float(h4[2]), "nu6": float(h4[6]), "nu10": float(h4[10]), "nu4": float(h4[4])},
                psi_ratio_p2_over_p4_same_If=float(psi4 / psi8), I_f_cap_pu_p2=float(i_cap),
                B0_at_psi_f_max_T=float(WRSM_PU["psi_f_max"] * PSI_BASE / psi8))


WRSM_PC = wrsm_pole_change_factors()


def sync_params(kind, p):
    s = stator_params(p)
    s4 = stator_params(4)
    Ls_lin = s["L_sigma_s_H"]
    if kind == "PMSM":
        assert p == 4
        Ld, Lq = PMSM_PU["L_d"] * L_BASE, PMSM_PU["L_q"] * L_BASE
        psi_max, i_f_cap, Pf = PMSM_PU["psi_pm"] * PSI_BASE, 1.0, 0.0
        fixed_field = True
    else:
        Ld4, Lq4 = WRSM_PU["L_d"] * L_BASE, WRSM_PU["L_q"] * L_BASE
        scale = s["Lm_H"] / s4["Lm_H"]  # geometric k_w^2/p^2 scaling of the magnetising part
        Ld = (Ld4 - s4["L_sigma_s_H"]) * scale + Ls_lin
        Lq = (Lq4 - s4["L_sigma_s_H"]) * scale + Ls_lin
        if p == 4:
            psi_max, i_f_cap = WRSM_PU["psi_f_max"] * PSI_BASE, 1.0
        else:
            psi_max = WRSM_PU["psi_f_max"] * PSI_BASE * WRSM_PC["psi_ratio_p2_over_p4_same_If"]  # per unit I_f
            i_f_cap = WRSM_PC["I_f_cap_pu_p2"]
        Pf = WRSM_PU["P_field_max_W"]
        fixed_field = False
    s.update(kind=kind, L_d_H=Ld, L_q_H=Lq, psi_per_If_pu_Wb=psi_max, I_f_cap_pu=i_f_cap,
             P_field_at_If1_W=Pf, fixed_field=fixed_field)
    return s


def sync_eval(par, n_rpm, I, gam, i_f, R=None):
    p = par["p"]
    R = par["R_s_ohm"] if R is None else R
    we = p * n_rpm * RPM
    Id, Iq = I * np.cos(gam), I * np.sin(gam)
    psi_f = par["psi_per_If_pu_Wb"] * i_f
    psd = psi_f + par["L_d_H"] * Id
    psq = par["L_q_H"] * Iq
    vd = R * Id - we * psq
    vq = R * Iq + we * psd
    T = M_PH * p * (psd * Iq - psq * Id)
    return T, np.hypot(vd, vq), psd, psq, we


def sync_envelope(par, n_grid, policy="free_Id", n_I=1, n_g=241, n_f=161, R=None):
    """Max torque per speed. For each (gamma, i_f) the admissible current interval from |V|<=Vmax
    is found in closed form (quadratic in |I|) and T(I) = aI + bI^2 maximised on it."""
    p = par["p"]
    R = par["R_s_ohm"] if R is None else R
    if policy == "Id0":
        gam = np.array([np.pi / 2])
    else:
        gam = np.linspace(np.pi / 2 - 0.0, np.pi, n_g)  # I_d <= 0 (field weakening / MTPA side)
    if par["fixed_field"]:
        i_f = np.array([1.0])
    else:
        i_f = np.linspace(0.0, par["I_f_cap_pu"], n_f)
    G, F = np.meshgrid(gam, i_f, indexing="ij")
    c, s = np.cos(G), np.sin(G)
    psi_f = par["psi_per_If_pu_Wb"] * F
    Ld, Lq = par["L_d_H"], par["L_q_H"]
    aT = M_PH * p * psi_f * s
    bT = M_PH * p * (Ld - Lq) * s * c
    out = np.zeros_like(n_grid)
    for i, n in enumerate(n_grid):
        we = p * n * RPM
        A1 = R * c - we * Lq * s
        A2 = R * s + we * Ld * c
        B2 = we * psi_f
        qa = A1 ** 2 + A2 ** 2
        qb = 2 * A2 * B2
        qc = B2 ** 2 - VMAX ** 2
        disc = qb ** 2 - 4 * qa * qc
        okd = disc >= 0
        sq = np.sqrt(np.where(okd, disc, 0.0))
        r1 = (-qb - sq) / (2 * qa)
        r2 = (-qb + sq) / (2 * qa)
        lo = np.maximum(r1, 0.0)
        hi = np.minimum(r2, IMAX)
        feas = okd & (hi >= lo)
        best = np.full(G.shape, -np.inf)
        for Ic in (lo, hi):
            best = np.maximum(best, aT * Ic + bT * Ic ** 2)
        with np.errstate(divide="ignore", invalid="ignore"):
            Iv = np.where(bT < 0, -aT / (2 * bT), np.nan)
        inside = (Iv > lo) & (Iv < hi)
        best = np.where(inside, np.maximum(best, aT * Iv + bT * Iv ** 2), best)
        best = np.where(feas, best, -np.inf)
        out[i] = max(0.0, float(np.max(best)))
    return out


def sync_min_loss(par, n_rpm, T_req, policy="free_Id", n_g=721, n_f=401):
    p = par["p"]
    gam = np.array([np.pi / 2]) if policy == "Id0" else np.linspace(np.pi / 2, np.pi, n_g)
    i_f = np.array([1.0]) if par["fixed_field"] else np.linspace(1e-3, par["I_f_cap_pu"], n_f)
    G, F = np.meshgrid(gam, i_f, indexing="ij")
    c, s = np.cos(G), np.sin(G)
    psi_f = par["psi_per_If_pu_Wb"] * F
    aT = M_PH * p * psi_f * s
    bT = M_PH * p * (par["L_d_H"] - par["L_q_H"]) * s * c
    with np.errstate(divide="ignore", invalid="ignore"):
        lin = np.abs(bT) < 1e-12 * np.maximum(aT, 1e-30)
        disc = aT ** 2 + 4 * bT * T_req
        Iq_ = np.where(lin, T_req / aT,
                       np.where(disc >= 0, (-aT + np.sqrt(np.where(disc >= 0, disc, 0))) / (2 * np.where(lin, 1, bT)), np.nan))
    I = np.where(Iq_ > 0, Iq_, np.nan)
    T, V, psd, psq, we = sync_eval(par, n_rpm, I, G, F)
    ok = np.isfinite(I) & (I <= IMAX) & (V <= VMAX * (1 + 1e-9))
    if not np.any(ok):
        return None
    Ls = par["L_sigma_s_H"]
    Id, Iq = I * c, I * s
    psi_ag = np.hypot(psd - Ls * Id, psq - Ls * Iq)
    B = psi_ag / par["psi_rms_per_T"]
    P_cu = M_PH * I ** 2 * par["R_s_ohm"]
    P_fe = iron_loss(we / (2 * np.pi), B, p)
    P_f = par["P_field_at_If1_W"] * F ** 2
    loss = np.where(ok, P_cu + P_fe + P_f, np.inf)
    j = np.unravel_index(int(np.argmin(loss)), loss.shape)
    P_m = float(p_mech(n_rpm))
    P_out = T_req * n_rpm * RPM - P_m
    tot = float(loss[j]) + P_m
    P_in_st = P_out + tot - float(P_f[j])
    return dict(eta=P_out / (P_out + tot), PF=P_in_st / (M_PH * float(V[j]) * float(I[j])),
                S_inverter_used_kVA=M_PH * float(V[j]) * float(I[j]) / 1e3, P_shaft_W=P_out, P_cu_stator_W=float(P_cu[j]), P_cu_rotor_W=0.0,
                P_fe_W=float(P_fe[j]), P_field_W=float(P_f[j]), P_mech_W=P_m, I_rms_A=float(I[j]),
                V_rms_V=float(V[j]), B_gap_T=float(B[j]), f_e_Hz=float(we / (2 * np.pi)),
                I_d_A=float(Id[j]), I_q_A=float(Iq[j]), I_f_pu=float(F[j]))


# ----------------------------------------------------------------------------------
# 8. Envelope metrics
# ----------------------------------------------------------------------------------
N_GRID = np.linspace(10.0, 9000.0, 450)
N_EVAL_MAX = float(N_GRID[-1])
CP_BAND = 0.95  # constant-power band: P >= 0.95 P(n_base)


def metrics(T, NG=None):
    NG = N_GRID if NG is None else NG
    P = T * NG * RPM
    Tpk = float(T.max())
    ib = int(np.max(np.where(T >= 0.99 * Tpk)[0]))
    Pb = float(P[ib])
    above = np.where(P >= Pb * CP_BAND)[0]
    icp = int(above.max())
    def at(n):
        return float(np.interp(n, NG, T)), float(np.interp(n, NG, P))
    P350 = np.where(P >= INV["P_rated_W"])[0]
    T45, P45 = at(VEH["n_motor_at_vmax_rpm"])
    return dict(T_peak_Nm=Tpk, T_peak_per_leg_A_Nm_per_A=Tpk / IMAX, T_peak_per_inverter_kVA_Nm_per_kVA=Tpk / (M_PH * VMAX * IMAX / 1e3),
                n_base_rpm=float(NG[ib]), P_base_W=Pb, P_max_W=float(P.max()),
                n_const_power_end_rpm=float(NG[icp]), CPSR=float(NG[icp] / NG[ib]),
                CPSR_capped_by_eval_range=bool(icp == len(NG) - 1),
                inverter_kVA_per_kW_base=(M_PH * VMAX * IMAX / 1e3) / (Pb / 1e3),
                speed_range_P_ge_350kW_rpm=[float(NG[P350.min()]), float(NG[P350.max()])] if P350.size else None,
                T_at_vmax_Nm=T45, P_at_vmax_W=P45,
                T_at_start_Nm=float(T[0]), meets_start_grade=bool(T[0] >= T_START))


def crossover(T_hi_p, T_lo_p, NG=None):
    """Lowest speed above which the low-pole-count envelope exceeds the high-pole-count one (continuously)."""
    NG = N_GRID if NG is None else NG
    better = T_lo_p > T_hi_p * 1.001
    if not better[-1]:
        idx = np.where(better)[0]
        return None if idx.size == 0 else float(NG[idx[0]])
    k = len(better) - 1
    while k > 0 and better[k - 1]:
        k -= 1
    return float(NG[k])


# ----------------------------------------------------------------------------------
# 9. Sanity checks
# ----------------------------------------------------------------------------------
def sanity_checks(im4):
    chk = {}
    # (a) winding factor numeric == analytic, module currents balanced
    for p in (2, 4):
        kn, _ = winding_factor_numeric(p)
        chk[f"kw_p{p}_numeric"] = float(kn)
        chk[f"kw_p{p}_analytic"] = winding_factor_analytic(p)
        chk[f"module_current_sum_max_p{p}_pu"] = module_current_sum(p)
    chk["module_current_sum_max_p3_pu (not allowed, expected 3)"] = module_current_sum(3)
    kw_num, kw_ana = conventional_three_phase_kw(4, 5)
    chk["conventional_3ph_48s_8p_y5_kw_numeric"] = kw_num
    chk["conventional_3ph_48s_8p_y5_kw_textbook"] = kw_ana
    # (b) IM: 48 coil-phase model == equivalent 3-phase machine (16 coils in series per phase)
    ns = np.array([500.0, 1500.0, 3000.0])
    psi = 0.03
    wsl = 3.0
    a = im_state(im4, ns, psi, wsl)
    k = INV["N_modules"]
    b = im_state(im4, ns, psi * k, wsl, m=3, Rs=im4["R_s_ohm"] * k, Ls=im4["L_sigma_s_H"] * k,
                 Lm=im4["Lm_H"] * k, Rr=im4["R_r_ohm"] * k, Lr=im4["L_sigma_r_H"] * k)
    chk["IM_48phase_vs_3phase_equiv_torque_maxrel"] = float(np.max(np.abs(a["T"] - b["T"]) / a["T"]))
    chk["IM_48phase_vs_3phase_equiv_voltage_ratio"] = float(np.mean(b["V"] / a["V"]))
    # (c) IM breakdown: numeric envelope at high speed (voltage limited) vs textbook breakdown torque
    n = 6000.0
    we = im4["p"] * n * RPM
    Rs, Xs, Xr, Xm = im4["R_s_ohm"], we * im4["L_sigma_s_H"], we * im4["L_sigma_r_H"], we * im4["Lm_H"]
    Zth = (Rs + 1j * Xs) * 1j * Xm / (Rs + 1j * (Xs + Xm))
    Vth = VMAX * Xm / abs(Rs + 1j * (Xs + Xm))
    Tbd = M_PH * im4["p"] * Vth ** 2 / (2 * we * (Zth.real + math.hypot(Zth.real, Zth.imag + Xr)))
    Tn = im_envelope(im4, np.array([n]))[0]
    chk["IM_p4_6000rpm_breakdown_textbook_Nm"] = float(Tbd)
    chk["IM_p4_6000rpm_envelope_numeric_Nm"] = float(Tn)
    # (d) PMSM, R=0: low-speed MTPA torque and base speed vs closed form
    pm = sync_params("PMSM", 4)
    psi, Ld, Lq = pm["psi_per_If_pu_Wb"], pm["L_d_H"], pm["L_q_H"]
    Id = (psi - math.sqrt(psi ** 2 + 8 * (Lq - Ld) ** 2 * IMAX ** 2)) / (4 * (Lq - Ld))
    Iq = math.sqrt(IMAX ** 2 - Id ** 2)
    T_mtpa = M_PH * 4 * (psi * Iq + (Ld - Lq) * Id * Iq)
    n_b = VMAX / math.hypot(psi + Ld * Id, Lq * Iq) / 4 / RPM
    Tn = sync_envelope(pm, np.array([50.0, 0.98 * n_b, 1.02 * n_b]), R=0.0)
    chk["PMSM_R0_MTPA_torque_closed_form_Nm"] = T_mtpa
    chk["PMSM_R0_envelope_at_50rpm_Nm"] = float(Tn[0])
    chk["PMSM_R0_base_speed_closed_form_rpm"] = n_b
    chk["PMSM_R0_T_at_0.98nb_over_Tmtpa"] = float(Tn[1] / T_mtpa)
    chk["PMSM_R0_T_at_1.02nb_over_Tmtpa"] = float(Tn[2] / T_mtpa)
    # (e) WRSM, I_d = 0, R = 0, high speed: P_max = m V^2 / (2 we Lq)
    wr = sync_params("WRSM", 4)
    n = 6000.0
    we = 4 * n * RPM
    Pcf = M_PH * VMAX ** 2 / (2 * we * wr["L_q_H"])
    Tn = sync_envelope(wr, np.array([n]), policy="Id0", n_f=4001, R=0.0)[0]
    chk["WRSM_Id0_R0_6000rpm_Pmax_closed_form_W"] = Pcf
    chk["WRSM_Id0_R0_6000rpm_Pmax_numeric_W"] = float(Tn * n * RPM)
    return chk


# ----------------------------------------------------------------------------------
# 10. Inverter current-limit sweep (kVA vs CPSR) and WRSM rotor-yoke sensitivity
# ----------------------------------------------------------------------------------
K_SWEEP = [0.3, 0.4, 0.5, 0.6, 0.75, 1.0, 1.25, 1.5, 2.0]
NG_SWEEP = np.linspace(10.0, 9000.0, 181)


def current_sweep(pars):
    """Scale the module current limit (machines unchanged, V fixed by the DC link)."""
    global IMAX
    I0 = IMAX
    rows = []
    try:
        for k in K_SWEEP:
            IMAX = I0 * k
            e = {"IM_2p8": im_envelope(pars["IM"][4], NG_SWEEP, n_psi=160, n_sl=300),
                 "IM_2p4": im_envelope(pars["IM"][2], NG_SWEEP, n_psi=160, n_sl=300),
                 "PMSM_2p8": sync_envelope(pars["PMSM"][4], NG_SWEEP, n_g=121),
                 "WRSM_freeId_2p8": sync_envelope(pars["WRSM"][4], NG_SWEEP, n_g=121, n_f=81),
                 "WRSM_freeId_2p4": sync_envelope(pars["WRSM"][2], NG_SWEEP, n_g=121, n_f=81)}
            e["IM_combined"] = np.maximum(e["IM_2p8"], e["IM_2p4"])
            e["WRSM_freeId_combined"] = np.maximum(e["WRSM_freeId_2p8"], e["WRSM_freeId_2p4"])
            row = {"current_factor": k, "I_module_rms_max_A": IMAX, "S_inverter_kVA": M_PH * VMAX * IMAX / 1e3,
                   "IM_crossover_speed_rpm": crossover(e["IM_2p8"], e["IM_2p4"], NG_SWEEP)}
            for name, T in e.items():
                m = metrics(T, NG_SWEEP)
                row[name] = {key: m[key] for key in ("T_peak_Nm", "n_base_rpm", "P_base_W", "CPSR", "CPSR_capped_by_eval_range",
                                                     "P_at_vmax_W", "inverter_kVA_per_kW_base")}
            rows.append(row)
    finally:
        IMAX = I0
    return rows


def wrsm_variant(margin):
    """Rebuild WRSM 2p=4 with a different rotor-yoke margin (2.0 = rotor yoke sized for the 2p=4 pattern)."""
    global WRSM_PC
    old_m, old_pc = WRSM_PU["rotor_yoke_margin"], WRSM_PC
    try:
        WRSM_PU["rotor_yoke_margin"] = margin
        WRSM_PC = wrsm_pole_change_factors()
        return WRSM_PC, sync_params("WRSM", 2)
    finally:
        WRSM_PU["rotor_yoke_margin"] = old_m
        WRSM_PC = old_pc


def pole_transition(pars):
    """Order-of-magnitude pole-transition times (no-torque or reduced-torque interval)."""
    out = {}
    # WRSM: tau_f = L_f/R_f = 2 W_f / P_f (independent of turn count); W_f from airgap + leakage energy at rated field
    B0 = WRSM_PC["B0_at_psi_f_max_T"]
    a = WRSM_PU["pole_arc_ratio"]
    W_gap = B0 ** 2 / (2 * MU0) * a * ST["g_eff_m"] * 2 * math.pi * ST["R_gap_m"] * ST["L_stk_m"]
    W_f = W_gap * WRSM_PU["L_f_stored_energy_leakage_factor"]
    P_f_groupB = WRSM_PU["P_field_max_W"] / 2.0  # group B carries half of the field coils
    tau_f = 2 * W_f / WRSM_PU["P_field_max_W"]    # same for each group (same coils)
    k = WRSM_PU["field_forcing_ratio"]
    t_freewheel_to_5pct = 3.0 * tau_f
    t_build_unforced_95pct = 3.0 * tau_f
    t_reverse_forced = tau_f * math.log((k + 1) / (k - 1))   # +I -> -I with -k R I applied
    out["WRSM"] = dict(field_stored_energy_J=W_f, airgap_energy_J=W_gap, tau_f_s=tau_f, field_power_groupB_W=P_f_groupB,
                       transition_freewheel_plus_unforced_build_s=t_freewheel_to_5pct + t_build_unforced_95pct + WRSM_PU["blanking_s"],
                       transition_forced_reversal_s=t_reverse_forced + WRSM_PU["blanking_s"],
                       forcing_ratio=k, blanking_s=WRSM_PU["blanking_s"],
                       note="P1 sequence = free-wheel to zero + blanking + build-up (no torque from group B meanwhile; group A keeps partial field). "
                            "Forced reversal needs a bipolar exciter with k x rated field voltage. tau_f from stored energy, saturation ignored (overestimates L_f).")
    # IM: new-p rotor flux build under current control, rotor time constant tau_r = (Lm + Lsr)/Rr per p
    for p in (4, 2):
        im = pars["IM"][p]
        tau_r = (im["Lm_H"] + im["L_sigma_r_H"]) / im["R_r_ohm"]
        Im_cap = im["psi_cap_rms_Wb"] / im["Lm_H"]
        # build to the flux needed at the crossover speed (voltage-limited flux there, capped)
        out[f"IM_2p{2 * p}"] = dict(tau_r_s=tau_r, I_mag_at_flux_cap_A=Im_cap)
    im2 = pars["IM"][2]
    n_x = 2100.0
    psi_need = min(im2["psi_cap_rms_Wb"], VMAX / (2 * n_x * RPM))
    I_need = psi_need / im2["Lm_H"]
    tau_r2 = out["IM_2p4"]["tau_r_s"]
    I_force = IMAX
    t_build = -tau_r2 * math.log(1 - I_need / I_force)
    out["IM_8_to_4_at_2100rpm"] = dict(psi_needed_rms_Wb=psi_need, I_mag_needed_A=I_need, I_d_forcing_A=I_force,
                                       flux_build_time_s=t_build, flux_build_time_unforced_3tau_s=3 * tau_r2,
                                       note="Under rotor-flux-oriented control with i_d forced to I_max. The decaying 2p=8 cage currents are spatially orthogonal "
                                            "to the 2p=4 field (no mean torque interaction); torque can ramp during the build. Simulator to confirm.")
    return out


# ----------------------------------------------------------------------------------
# 11. Main
# ----------------------------------------------------------------------------------
def main():
    pars = {"IM": {p: im_params(p) for p in (4, 2)},
            "PMSM": {4: sync_params("PMSM", 4)},
            "WRSM": {p: sync_params("WRSM", p) for p in (4, 2)}}
    env = {}
    env["IM"] = {p: im_envelope(pars["IM"][p], N_GRID) for p in (4, 2)}
    env["PMSM"] = {4: sync_envelope(pars["PMSM"][4], N_GRID, n_g=5761)}
    env["WRSM_Id0"] = {p: sync_envelope(pars["WRSM"][p], N_GRID, policy="Id0", n_f=801) for p in (4, 2)}
    env["WRSM_freeId"] = {p: sync_envelope(pars["WRSM"][p], N_GRID, n_g=961) for p in (4, 2)}

    machines = {}
    for key, mname in (("IM", "IM"), ("PMSM", "PMSM"), ("WRSM_Id0", "WRSM"), ("WRSM_freeId", "WRSM")):
        e = env[key]
        d = {"pole_counts_2p": [2 * p for p in e]}
        for p, T in e.items():
            d[f"2p{2 * p}"] = dict(metrics=metrics(T), torque_Nm=T.round(2).tolist(),
                                   power_kW=(T * N_GRID * RPM / 1e3).round(3).tolist())
        if 2 in e:
            Tc = np.maximum(e[4], e[2])
            d["combined"] = dict(metrics=metrics(Tc), torque_Nm=Tc.round(2).tolist(),
                                 power_kW=(Tc * N_GRID * RPM / 1e3).round(3).tolist(),
                                 pole_count_2p_used=np.where(e[2] > e[4] * 1.001, 4, 8).tolist(),
                                 crossover_speed_rpm=crossover(e[4], e[2]))
        machines[key] = d

    # efficiency points (n, T); cruise from road load
    pts = [("launch_300rpm_2000Nm", 300.0, 2000.0), ("accel_1000rpm_2000Nm", 1000.0, 2000.0),
           ("suburban_2000rpm_1000Nm", 2000.0, 1000.0), ("highway_3500rpm_600Nm", 3500.0, 600.0),
           ("cruise_85kmh_road_load", N_CRUISE, T_CRUISE), ("grade_at_vmax_4500rpm_600Nm", 4500.0, 600.0)]
    eff = {}
    for name, n, T in pts:
        row = {"speed_rpm": n, "torque_Nm": T}
        for p in (4, 2):
            row[f"IM_2p{2 * p}"] = im_min_loss(pars["IM"][p], n, T)
            row[f"WRSM_Id0_2p{2 * p}"] = sync_min_loss(pars["WRSM"][p], n, T, policy="Id0")
            row[f"WRSM_freeId_2p{2 * p}"] = sync_min_loss(pars["WRSM"][p], n, T)
        row["PMSM_2p8"] = sync_min_loss(pars["PMSM"][4], n, T)
        eff[name] = row

    chk = sanity_checks(pars["IM"][4])

    # WRSM sensitivity: rotor yoke sized for the 2p=4 pattern
    pc2, wr2 = wrsm_variant(1.0)
    T_wr2 = sync_envelope(wr2, N_GRID)
    T_wr2c = np.maximum(env["WRSM_freeId"][4], T_wr2)
    wrsm_sens = dict(description="SENSITIVITY: rotor_yoke_margin = 1.0 (rotor yoke sized for 2p=8 only; ++-- pattern limited to half field current). Baseline uses 2.0 (P2 seed).",
                     pole_change=pc2, metrics_2p4=metrics(T_wr2), metrics_combined=metrics(T_wr2c),
                     crossover_speed_rpm=crossover(env["WRSM_freeId"][4], T_wr2),
                     cruise_2p4=sync_min_loss(wr2, N_CRUISE, T_CRUISE),
                     torque_2p4_Nm=T_wr2.round(2).tolist())

    sweep = current_sweep(pars)
    ext = [r for r in sweep if r["IM_combined"]["P_at_vmax_W"] > 1.05 * r["IM_2p8"]["P_at_vmax_W"]
           and r["IM_combined"]["CPSR"] > 1.05 * r["IM_2p8"]["CPSR"]]
    im4 = pars["IM"][4]
    I_mag_rated = im4["psi_cap_rms_Wb"] / im4["Lm_H"]
    bitsi = dict(I_module_rms_max_A=IMAX, IM_2p8_magnetising_current_at_flux_cap_A=I_mag_rated,
                 I_max_over_I_mag=IMAX / I_mag_rated,
                 min_current_factor_with_envelope_extension=min(r["current_factor"] for r in ext) if ext else None,
                 note="Extension = IM combined envelope gives >5 % more CPSR and >5 % more power at 4500 rpm than 2p=8 alone. "
                      "Bitsi2022design: no extension for current limit <= 18 A of 22 A (WICSC IM).")

    def g(row, key):
        v = row.get(key)
        return None if v is None else {k: v[k] for k in ("eta", "PF", "I_rms_A", "S_inverter_used_kVA", "P_fe_W", "P_cu_stator_W", "P_cu_rotor_W", "P_field_W", "f_e_Hz")}
    cr = eff["cruise_85kmh_road_load"]
    M = machines
    leader = dict(
        a_low_speed_peak_torque_per_inverter_ampere=dict(
            unit_note="Nm per A rms of one module leg (all 48 legs carry the same current); same inverter for all",
            IM_with_pole_change=M["IM"]["combined"]["metrics"]["T_peak_per_leg_A_Nm_per_A"],
            IM_fixed_2p8=M["IM"]["2p8"]["metrics"]["T_peak_per_leg_A_Nm_per_A"],
            IM_fixed_2p4=M["IM"]["2p4"]["metrics"]["T_peak_per_leg_A_Nm_per_A"],
            PMSM_fixed_2p8=M["PMSM"]["2p8"]["metrics"]["T_peak_per_leg_A_Nm_per_A"],
            WRSM_with_pole_change=M["WRSM_freeId"]["combined"]["metrics"]["T_peak_per_leg_A_Nm_per_A"],
            WRSM_fixed_2p8=M["WRSM_freeId"]["2p8"]["metrics"]["T_peak_per_leg_A_Nm_per_A"],
            WRSM_fixed_2p4=M["WRSM_freeId"]["2p4"]["metrics"]["T_peak_per_leg_A_Nm_per_A"],
            WRSM_fixed_2p4_rotor_yoke_8pole_only=wrsm_sens["metrics_2p4"]["T_peak_per_leg_A_Nm_per_A"]),
        b_inverter_kVA_vs_CPSR="see current_limit_sweep (S_inverter_kVA, CPSR, inverter_kVA_per_kW_base per machine)",
        c_cruise_efficiency=dict(IM_with_pole_change_2p4=g(cr, "IM_2p4"), IM_without_2p8=g(cr, "IM_2p8"),
                                 PMSM_2p8=g(cr, "PMSM_2p8"), WRSM_freeId_2p8=g(cr, "WRSM_freeId_2p8"),
                                 WRSM_freeId_2p4=g(cr, "WRSM_freeId_2p4"),
                                 WRSM_freeId_2p4_rotor_yoke_8pole_only=None if wrsm_sens["cruise_2p4"] is None else {k: wrsm_sens["cruise_2p4"][k] for k in ("eta", "PF", "I_rms_A", "P_fe_W", "P_cu_stator_W", "P_field_W")}),
        bitsi2022_current_limit_regime=bitsi,
        P2_seed_check=dict(P2_implied_T_lowpole_over_T_highpole=P2_SEED["implied_T_lowpole_over_T_highpole"],
                           model_T_peak_ratio_2p4_over_2p8=M["WRSM_freeId"]["2p4"]["metrics"]["T_peak_Nm"] / M["WRSM_freeId"]["2p8"]["metrics"]["T_peak_Nm"],
                           model_T_peak_ratio_rotor_yoke_8pole_only=wrsm_sens["metrics_2p4"]["T_peak_Nm"] / M["WRSM_freeId"]["2p8"]["metrics"]["T_peak_Nm"]))
    transition = pole_transition(pars)

    def clean(par):
        return {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in par.items()}

    res = dict(
        meta=dict(script="02_analytics/torque_speed_envelope.py", task="T03",
                  date=_dt.date.today().isoformat(), python=sys.version.split()[0],
                  inputs=["board/decisions.md D01, D02 (provisional)",
                          "../Drive Cycle/basic_vehicle_dynamics.m (vehicle constants)",
                          "M270-35A loss datapoints (2.7 W/kg @1.5T/50Hz, 17.5 W/kg @1T/400Hz)"],
                  assumptions="02_analytics/assumptions.md#t03",
                  notes=["Torque = electromagnetic torque; friction/windage only in efficiency points.",
                         "Efficiency = machine only (no inverter, no gearbox). Inverter conduction loss scales with I_rms reported per point; f_sw is unchanged by pole changing.",
                         "Synchronous-machine inductances are saturated effective per-unit values (not FEA); WRSM 2p=4 values scaled from 2p=8 by k_w^2/p^2 on the magnetising part.",
                         "CPSR = n_const_power_end / n_base; n_base = highest speed with T >= 0.99 T_peak; constant power = P >= 0.95 P(n_base). Evaluated up to %.0f rpm." % N_EVAL_MAX]),
        inverter=INV, vehicle=VEH, stator=ST, iron_loss_model=FE,
        per_unit_base=dict(n_ref_rpm=N_REF_RPM, p_ref=P_REF, L_base_H=L_BASE, psi_base_rms_Wb=PSI_BASE,
                           T_base_Nm=M_PH * P_REF * PSI_BASE * IMAX),
        machine_parameters=dict(
            IM={f"2p{2 * p}": clean(v) for p, v in pars["IM"].items()} | {"rotor": IMR},
            PMSM={"pu": PMSM_PU, "2p8": clean(pars["PMSM"][4])},
            WRSM={"pu": WRSM_PU, "pole_change": WRSM_PC, **{f"2p{2 * p}": clean(v) for p, v in pars["WRSM"].items()},
                  "rotor_switching": "8 field coil groups, patterns as in Field Excitation/FE_MMF.m (P4): 2p=8 [1 -1 1 -1 1 -1 1 -1], 2p=4 [1 1 -1 -1 1 1 -1 -1]. Group A = coils 0,3,4,7 (fixed polarity), group B = coils 1,2,5,6 (reversed). REQUIREMENT: bipolar excitation of group B plus a unipolar channel for group A. Generic rotating-rectifier brushless exciters are unipolar (Krupp2015rotary, Stella2024excitation); Enes's own bipolar exciters exist at small scale: WPT dual-channel, +/-2.88 A, 118 W, 99 % rectifier efficiency (P1, Field Excitation/manuscript.pdf) and bipolar optical power transfer on a 10 kW 4/2-pole PC-WFSM (P2, draft). Treated as available; scaling to a ~4 kW truck field is an open item. Alternative without contactless hardware: 3 slip rings + stationary H-bridge.", "P2_seed": P2_SEED, "pole_transition": transition, "gradual_transition_option": "P4 pattern [1 k -k -1 1 k -k -1], k: 1 -> -1, sweeps the rotor field from 2p=8 to 2p=4 without a zero-field interval (Field Excitation/FE_MMF.m) - simulator target"}),
        winding=dict(Q=ST["Q"], coil_pitch_slots=ST["y_slots"], module_to_coils="module j -> coils j, j+16, j+32 (star, isolated neutral)",
                     coil_phase_rule="alpha_k = p*2*pi*k/Q", allowed_p="p not divisible by 3",
                     prior_work_link="Same coil-group logic as Enes's 12-slot linearised 2-pole/4-pole patterns (Field Excitation/6-phase Induction Machine/Phase-Pole.pptx, slides 1-4): each coil group keeps its slot position and gets electrical angle p x (its mechanical position), so doubling p doubles every group's phase shift. Here generalised to 48 coils / 16 three-phase SPB modules.",
                     mmf_harmonics_rel={f"2p{2 * p}": {str(nu): float(a / spb_mmf(p)[p]) for nu, a in enumerate(spb_mmf(p)) if a > 1e-3 * spb_mmf(p)[p]} for p in (4, 2)}),
        speed_rpm=N_GRID.round(3).tolist(),
        machines=machines,
        efficiency_points=eff,
        leader_requests_T03=leader,
        pole_transition=transition,
        current_limit_sweep=sweep,
        wrsm_rotor_yoke_sensitivity=wrsm_sens,
        sanity_checks=chk,
    )
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(res, f, indent=1, default=float)

    # quick-look
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
        fig, ax = plt.subplots(2, 4, figsize=(16, 7), sharex=True)
        for j, key in enumerate(("IM", "PMSM", "WRSM_Id0", "WRSM_freeId")):
            for p, T in env[key].items():
                ax[0, j].plot(N_GRID, T, label=f"2p={2 * p}")
                ax[1, j].plot(N_GRID, T * N_GRID * RPM / 1e3, label=f"2p={2 * p}")
            ax[1, j].axhline(350, color="k", lw=0.5, ls="--")
            ax[1, j].axvline(VEH["n_motor_at_vmax_rpm"], color="k", lw=0.5, ls=":")
            ax[0, j].set_title(key)
            ax[0, j].legend()
            ax[1, j].set_xlabel("speed (rpm)")
        ax[0, 0].set_ylabel("T (Nm)")
        ax[1, 0].set_ylabel("P (kW)")
        fig.tight_layout()
        fig.savefig(OUT_PNG, dpi=110)
    except Exception as exc:  # quick-look only
        print("plot skipped:", exc)

    # console summary
    print(f"V_ph,rms,max = {VMAX:.2f} V, I_max = {IMAX:.1f} A rms per module leg, gear = {VEH['gear_ratio']:.2f}")
    print(f"cruise: {N_CRUISE:.0f} rpm, {T_CRUISE:.0f} Nm; start {VEH['grade_start_pct']}% grade: {T_START:.0f} Nm")
    for key, d in machines.items():
        for sub in [k for k in d if k.startswith("2p") or k == "combined"]:
            m = d[sub]["metrics"]
            extra = f" xover={d[sub].get('crossover_speed_rpm')}" if sub == "combined" else ""
            print(f"{key:12s} {sub:9s} Tpk={m['T_peak_Nm']:7.0f} nb={m['n_base_rpm']:6.0f} Pb={m['P_base_W']/1e3:6.1f}kW "
                  f"CPSR={m['CPSR']:5.2f}{'+' if m['CPSR_capped_by_eval_range'] else ' '} P@4500={m['P_at_vmax_W']/1e3:6.1f}kW{extra}")
    for k, v in chk.items():
        print(f"  check {k}: {v:.5g}" if isinstance(v, float) else f"  check {k}: {v}")
    print(json.dumps(leader, indent=1, default=float))
    for r in sweep:
        print(f"k={r['current_factor']:.2f} S={r['S_inverter_kVA']:.0f}kVA xover={r['IM_crossover_speed_rpm']} " + " ".join(
            f"{n}:CPSR={r[n]['CPSR']:.2f},Pb={r[n]['P_base_W']/1e3:.0f},P45={r[n]['P_at_vmax_W']/1e3:.0f}" for n in r if isinstance(r[n], dict)))
    print("transition:", json.dumps(transition, indent=1, default=float))
    print("WRSM rotor-yoke 8-pole-only (sensitivity):", wrsm_sens["metrics_2p4"]["T_peak_Nm"], wrsm_sens["metrics_combined"]["CPSR"], wrsm_sens["crossover_speed_rpm"],
          wrsm_sens["metrics_2p4"]["P_at_vmax_W"])
    for name, row in eff.items():
        s = " ".join(f"{k}={v['eta']*100:.2f}" if isinstance(v, dict) else f"{k}=n/a"
                     for k, v in row.items() if k not in ("speed_rpm", "torque_Nm"))
        print(name, f"({row['speed_rpm']:.0f} rpm, {row['torque_Nm']:.0f} Nm):", s)


if __name__ == "__main__":
    main()

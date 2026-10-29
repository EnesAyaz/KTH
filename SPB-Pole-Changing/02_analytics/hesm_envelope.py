"""T03c - SPB-driven hybrid-excited synchronous machine (HESM, PM + field winding) with
8 <-> 4 pole changing, on the same basis as T03b (300 kW, same SPB limits, same outer
volume and copper, same vehicle, same gear-choice rule).

Run from repo root:  python 02_analytics/hesm_envelope.py  [--quick]
Output: 02_analytics/results/hesm_envelope.json, 02_analytics/scratch/hesm_envelope_quicklook.png
Assumptions: 02_analytics/assumptions_hesm.md

Imports T03 (torque_speed_envelope.py, 300 kW) and T03b (fair_baselines.py) read-only.

Rotor (Conto2022hybrid generalised): 8 salient poles. Group A = poles 0,3,4,7 keep their
polarity; group B = poles 1,2,5,6 reverse. Pole amplitudes A (group A) and B (group B,
positive = 8-pole polarity) give the rotor field
    A*u_A + B*u_B = (A+B)/2 * P8 + (A-B)/2 * P4      (u_A = (P8+P4)/2, u_B = (P8-P4)/2)
8-pole mode: A = B (pure P8); 4-pole mode: B = -A (pure P4).
PM share s = PM fraction of the rated 8-pole no-load rotor flux:
    s <= 0.5: PM only on group A (m_A = 2s), field coils on both groups (s = 0: WRSM of T03;
              s = 0.5: Conto rule, group A pure PM, group B pure field)
    s >  0.5: group A pure PM (m_A = 1) and PM m_B = 2s-1 on group B (8-pole polarity)
              that the group-B coil must override in 4-pole mode.

D05: module count N and slot count Q are parameters. With constant copper and N_c, the
coil-frame per-unit model does not depend on N (V_leg = 1200/N and c = Q/(3N) coils per leg
cancel); N enters through the series grouping of coils on a leg: distribution factor k_d(p)
and the module current balance for each pole mode.
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

assert T3.P_RATED_KW == 300.0, "T03c is defined at 300 kW (D02)"
ROOT = os.path.dirname(HERE)
OUT_JSON = os.path.join(ROOT, "02_analytics", "results", "hesm_envelope.json")
OUT_PNG = os.path.join(ROOT, "02_analytics", "scratch", "hesm_envelope_quicklook.png")
QUICK = "--quick" in sys.argv

MU0, SQ2, RPM = T3.MU0, T3.SQ2, T3.RPM
VMAX, IMAX = T3.VMAX, T3.IMAX                # per coil-phase (N = 16 reference): 29.09 V, 266.1 A
ST = T3.ST
G_REF = T3.VEH["gear_ratio"]
NG = FB.NG_FULL                              # 10..9000 rpm, 450 points (same as T03/T03b)
N_TIP = FB.TIP_SPEED_MAX / ST["R_gap_m"] / RPM   # 125 m/s at R = 165 mm (same rule as T03b)

# ----------------------------------------------------------------------------------
# Rotor / PM / exciter data
# ----------------------------------------------------------------------------------
B0 = T3.WRSM_PC["B0_at_psi_f_max_T"]         # pole-face amplitude at rated WRSM field (0.712 T)
H8, H4 = T3.WRSM_PC["B_harm_8pole_rel"][0], T3.WRSM_PC["B_harm_4pole_rel"]["nu2"]  # fundamentals of P8 / P4 per unit amplitude
PM = dict(Br_T=1.10, mu_r=1.05, k_leak=0.85, rho_kg_m3=7500.0, grade="NdFeB UH-class (Conto2022: UH35) at ~120 C",
          pole_face_area_m2=T3.WRSM_PU["pole_arc_ratio"] * 2 * math.pi * ST["R_gap_m"] / 8 * ST["L_stk_m"])
P_FIELD_GROUP_MAX_W = T3.WRSM_PU["P_field_max_W"] / 2   # 2 kW per group (4 poles) = WRSM rotor copper limit
# P1 rectifier: 99 % at rated (2.88 A), 87 % at 0.61 A -> loss = P_rated (k0 + k1 x), x = I/I_rated
_x1 = 0.61 / 2.88
_l1, _l0 = 1 / 0.99 - 1, (1 / 0.87 - 1) * _x1 ** 2
EXC = dict(eta_rated=0.99, eta_light=0.87, x_light=_x1, k1=(_l1 - _l0) / (1 - _x1))
EXC["k0"] = _l1 - EXC["k1"]
POLICIES = ("If_weakening", "fixed_field", "If_weakening_bipolarA")


def pm_thickness(B_pole):
    """PM thickness (m) giving pole-face amplitude B_pole alone (series magnetic circuit with leakage)."""
    if B_pole <= 0:
        return 0.0
    kb = PM["k_leak"] * PM["Br_T"]
    if B_pole >= kb:
        return float("inf")
    return B_pole * PM["mu_r"] * ST["g_eff_m"] / (kb - B_pole)


def rotor(s):
    mA, mB = (2 * s, 0.0) if s <= 0.5 + 1e-12 else (1.0, 2 * s - 1)
    hA, hB = pm_thickness(mA * B0), pm_thickness(mB * B0)
    g = ST["g_eff_m"]
    kA, kB = g / (g + hA / PM["mu_r"]), g / (g + hB / PM["mu_r"])
    coilA = s < 0.5 - 1e-9
    m_pm = 4 * PM["pole_face_area_m2"] * (hA + hB) * PM["rho_kg_m3"]
    return dict(s=s, m_A=mA, m_B=mB, h_pm_A_mm=hA * 1e3, h_pm_B_mm=hB * 1e3, kappa_A=kA, kappa_B=kB,
                group_A_has_coil=coilA, L_dm_factor=0.5 * (kA + kB), PM_mass_kg=m_pm)


def exciter_loss(i):
    """Rectifier loss of one channel (W); i = coil current / thermal-limit current."""
    x = np.abs(i)
    return np.where(x > 1e-6, P_FIELD_GROUP_MAX_W * (EXC["k0"] + EXC["k1"] * x), 0.0)


# ----------------------------------------------------------------------------------
# Winding: coil -> leg/module mapping for any N, Q (D05)
# ----------------------------------------------------------------------------------
def mapping(N, Q=48, scheme="spb", p_hi=4):
    """Coil -> leg (= 3*module + phase) and wiring sign per coil.
    spb:   the first third of the coil positions (Q/3) is split into N contiguous blocks; module j feeds,
           on its phase leg ph, the coils of block j shifted by ph*Q/3 (120 deg mechanical), c = Q/(3N) coils in
           series per leg with polarity fixed for the high-pole mode p_hi. N = 16, Q = 48 is T03 (coils j, j+16, j+32).
    conto: Conto2022hybrid two-inverter supply (N = 2): conventional 3-phase 2p_hi-pole belt winding,
           coils under odd pole pairs on inverter 0, even pole pairs on inverter 1."""
    th = 2 * np.pi * np.arange(Q) / Q
    leg, sign = np.zeros(Q, int), np.ones(Q)
    if scheme == "spb":
        assert Q % (3 * N) == 0
        third, c = Q // 3, Q // (3 * N)
        for k in range(Q):
            leg[k] = 3 * ((k % third) // c) + k // third
        for l in range(3 * N):
            ks = np.where(leg == l)[0]
            sg = np.sign(np.cos(p_hi * (th[ks] - th[ks[0]])))
            sign[ks] = np.where(sg == 0, 1, sg)
    elif scheme == "conto":
        assert N == 2
        q = Q // (2 * p_hi * 3)
        belt = [(0, +1), (2, -1), (1, +1), (0, -1), (2, +1), (1, -1)]
        for k in range(Q):
            ph, sg = belt[(k // q) % 6]
            leg[k], sign[k] = ((k // (Q // p_hi)) % 2) * 3 + ph, sg
    else:
        raise ValueError(scheme)
    return dict(N=N, Q=Q, scheme=scheme, leg=leg, sign=sign, coils_per_leg=Q // (3 * N))


def winding(mp, p, y=ST["y_slots"]):
    """k_w, sigma_diff for pole-pair p under mapping mp. Every module stays a balanced 3-phase set
    (equal leg currents, phases phi_j + seq*120 deg*ph); offset phi_j and sequence seq = +/-1 are chosen per
    module to maximise the p-th harmonic (this is Conto's 'reverse inverter 2 and swap B/C' generalised)."""
    Q, leg, sg = mp["Q"], mp["leg"], mp["sign"]
    th = 2 * np.pi * np.arange(Q) / Q
    phi = np.zeros(3 * mp["N"])
    tot = 0.0
    for j in range(mp["N"]):
        S = np.array([np.sum(sg[leg == 3 * j + ph] * np.exp(1j * p * th[leg == 3 * j + ph])) for ph in range(3)])
        best = None
        for seq in (+1, -1):
            rot = np.exp(1j * seq * 2 * np.pi / 3 * np.arange(3))
            z = np.sum(S / rot)
            if best is None or abs(z) > best[0]:
                best = (abs(z), np.angle(z) + np.angle(rot))
        tot += best[0]
        phi[3 * j: 3 * j + 3] = best[1]
    kd = float(tot / Q)
    kp = abs(math.sin(p * y * math.pi / Q))
    # numerical MMF, split into forward/backward rotating waves (currents i_k = Re(a_k e^{jwt}))
    a = sg * np.exp(1j * phi[leg])
    Cr, Ci = mmf_complex(Q, y, a.real), mmf_complex(Q, y, a.imag)
    Fw, Bw = np.abs(Cr + 1j * Ci) / 2, np.abs(Cr - 1j * Ci) / 2   # forward / backward rotating-wave amplitudes
    Fp = max(Fw[p], Bw[p])
    kw_num = Fp * math.pi * p / (Q * ST["N_c"])
    harm = Fw ** 2 + Bw ** 2
    harm[0] = 0.0
    harm[p] -= Fp ** 2
    sig = float(np.sum(harm) / Fp ** 2) if Fp > 1e-9 else float("inf")
    return dict(p=p, k_w=kp * kd, k_pitch=kp, k_d=kd, k_w_numeric_MMF=float(kw_num), sigma_diff=sig,
                coils_per_leg=mp["coils_per_leg"], feasible=bool(kd > 0.3))


def mmf_complex(Q, y, i, n_theta=4096, nu_max=200):
    """Complex spatial harmonics (peak, same normalisation as T3.mmf_spectrum) of Q coils (k -> k+y) with currents i."""
    th = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    Islot = np.zeros(Q)
    for k in range(Q):
        Islot[k % Q] += ST["N_c"] * i[k]
        Islot[(k + y) % Q] -= ST["N_c"] * i[k]
    pos = 2 * np.pi * (np.arange(Q) + 0.5) / Q
    F = np.zeros(n_theta)
    for q in range(Q):
        F += Islot[q] * (th >= pos[q])
    F -= F.mean()
    return (np.fft.rfft(F) / n_theta * 2)[: nu_max + 1]


def conto_three_phase_kw():
    """Conto two-inverter supply on the T03 48-slot stator (y = 7): k_w per mode."""
    mp = mapping(2, 48, "conto")
    return {f"2p{2 * p}": winding(mp, p) for p in (4, 2)}


# ----------------------------------------------------------------------------------
# Stator (two yoke variants, same R_out, L_stk, copper mass) and per-mode machine parameters
# ----------------------------------------------------------------------------------
STATORS = {"T03_yoke25mm": 0.025, "yoke38mm_4pole_capable": 0.038}


def stator(name, mp, p):
    d = FB.make_design(p, mp["Q"], ST["y_slots"], 1, ST["R_gap_m"], float("nan"), ST["N_c"], h_y=STATORS[name])
    w = winding(mp, p)
    Nk = ST["N_c"] * w["k_w"]
    RL = ST["R_gap_m"] * ST["L_stk_m"]
    Lm = 2 * mp["Q"] * MU0 * RL * Nk ** 2 / (math.pi * ST["g_eff_m"] * p ** 2)
    lam_r = (d["h_slot_m"] / (3 * d["b_slot_m"]) + 0.33) / 2.0
    L_slot = 2 * MU0 * ST["N_c"] ** 2 * ST["L_stk_m"] * lam_r * (ST["lam_slot_self"] - ST["lam_slot_mut"] * math.cos(2 * math.pi * p * ST["y_slots"] / mp["Q"]))
    L_end = MU0 * ST["N_c"] ** 2 * 2 * d["l_end_half_m"] * ST["lam_end"]
    L_diff = w["sigma_diff"] * Lm * ST["kc_ksat"] / 1.05
    psi_per_T = 2 * Nk * RL / p / SQ2
    h = H8 if p == 4 else H4
    return dict(design=d, winding=w, p=p, k_w=w["k_w"], Lm_H=Lm, L_sigma_s_H=L_slot + L_end + L_diff, R_s_ohm=d["R_s_ohm"],
                psi_rms_per_T=psi_per_T, psi_per_amp_Wb=psi_per_T * h * B0, B_gap_cap_T=d["B_gap_cap_T"],
                amp_cap=min(d["B_gap_cap_T"] / (h * B0), T3.WRSM_PU["rotor_yoke_margin"] / 2.0 if p == 2 else 9.9))


_T3W4 = T3.sync_params("WRSM", 4)
LDM4 = T3.WRSM_PU["L_d"] * T3.L_BASE - _T3W4["L_sigma_s_H"]
LQM4 = T3.WRSM_PU["L_q"] * T3.L_BASE - _T3W4["L_sigma_s_H"]


def machine(st_name, mp, rot, p):
    s = stator(st_name, mp, p)
    sc = s["Lm_H"] / _T3W4["Lm_H"]
    s.update(L_d_H=LDM4 * sc * rot["L_dm_factor"] + s["L_sigma_s_H"], L_q_H=LQM4 * sc + s["L_sigma_s_H"])
    return s


def field_range(rot, par, policy):
    """Admissible pole amplitude c of the active mode (A = B in 8-pole, A = -B in 4-pole)."""
    mA, mB, kA, kB = rot["m_A"], rot["m_B"], rot["kappa_A"], rot["kappa_B"]
    if rot["group_A_has_coil"]:
        A_lo, A_hi = mA + kA * (-1.0 if policy == "If_weakening_bipolarA" else 0.0), mA + kA
    else:
        A_lo = A_hi = mA
    B_lo, B_hi = mB - kB, mB + kB
    if par["p"] == 4:
        lo, hi = max(A_lo, B_lo, 0.0), min(A_hi, B_hi, par["amp_cap"])
    else:
        lo, hi = max(A_lo, -B_hi, 0.0), min(A_hi, -B_lo, par["amp_cap"])
    if lo > hi + 1e-9:
        return None
    if policy == "fixed_field":
        lo = hi
    return lo, hi


def field_currents(rot, p, c):
    iA = (c - rot["m_A"]) / rot["kappa_A"] if rot["group_A_has_coil"] else np.zeros_like(c)
    B = c if p == 4 else -c
    iB = (B - rot["m_B"]) / rot["kappa_B"]
    return iA, iB


# ----------------------------------------------------------------------------------
# Envelope (closed-form current interval per (gamma, c), as T03 sync_envelope)
# ----------------------------------------------------------------------------------
def envelope(par, NGr, c_lo, c_hi, n_g=481, n_f=81, Vmax=VMAX, Imax=IMAX, Id0=False):
    p, R = par["p"], par["R_s_ohm"]
    gam = np.array([np.pi / 2]) if Id0 else np.linspace(np.pi / 2, np.pi, n_g)
    cf = np.array([c_hi]) if c_hi - c_lo < 1e-9 else np.linspace(c_lo, c_hi, n_f)
    G, F = np.meshgrid(gam, cf, indexing="ij")
    c, s = np.cos(G), np.sin(G)
    psi_f = par["psi_per_amp_Wb"] * F
    Ld, Lq = par["L_d_H"], par["L_q_H"]
    m = T3.M_PH
    aT = m * p * psi_f * s
    bT = m * p * (Ld - Lq) * s * c
    out = np.zeros(len(NGr))
    for i, n in enumerate(NGr):
        we = p * n * RPM
        A1 = R * c - we * Lq * s
        A2 = R * s + we * Ld * c
        B2 = we * psi_f
        qa, qb, qc = A1 ** 2 + A2 ** 2, 2 * A2 * B2, B2 ** 2 - Vmax ** 2
        disc = qb ** 2 - 4 * qa * qc
        okd = disc >= 0
        sq = np.sqrt(np.where(okd, disc, 0.0))
        lo, hi = np.maximum((-qb - sq) / (2 * qa), 0.0), np.minimum((-qb + sq) / (2 * qa), Imax)
        feas = okd & (hi >= lo)
        best = np.maximum(aT * lo + bT * lo ** 2, aT * hi + bT * hi ** 2)
        with np.errstate(divide="ignore", invalid="ignore"):
            Iv = np.where(bT < 0, -aT / (2 * bT), np.nan)
        inside = (Iv > lo) & (Iv < hi)
        best = np.where(inside, np.maximum(best, aT * Iv + bT * Iv ** 2), best)
        out[i] = max(0.0, float(np.max(np.where(feas, best, -np.inf))))
    return out


# ----------------------------------------------------------------------------------
# Loss-minimising operating point (simple T03 set, and realistic T03b set + field + exciter)
# ----------------------------------------------------------------------------------
P_LL_N = FB.iec_stray_allowance_W(T3.INV["P_rated_W"])


def pwm_loss(par):
    """SPB PWM ripple, same method as T03b (stator copper k_ac + tooth eddy); L_hf = 0.5 x 2 L_sigma_s (no cage)."""
    d = par["design"]
    L_hf = FB.L_HF_FACTOR * 2 * par["L_sigma_s_H"]
    di = T3.INV["V_module_V"] / (4 * L_hf * FB.F_SW_HZ)
    Ih = di / (2 * math.sqrt(3))
    P_cs = T3.M_PH * Ih ** 2 * par["R_s_ohm"] * FB.K_AC_STATOR_HF
    psi_h = par["L_sigma_s_H"] * FB.L_HF_FACTOR * Ih * SQ2
    B_h = psi_h / (ST["N_c"] * d["b_tooth_m"] * ST["L_stk_m"])
    delta = math.sqrt(FB.RHO_FE / (math.pi * FB.F_SW_HZ * MU0 * FB.MU_R_HF))
    x = FB.D_LAM / delta
    Fx = 3.0 / x * (math.sinh(x) - math.sin(x)) / (math.cosh(x) - math.cos(x))
    P_fe = T3.FE["build_factor"] * d["m_teeth_kg"] * T3.FE["k_e"] * FB.F_SW_HZ ** 2 * B_h ** 2 * Fx / 2
    return dict(ripple_pp_A=di, P_cu_stator_W=P_cs, P_fe_W=P_fe, P_total_W=P_cs + P_fe)


def op_point(par, rot, rng, n, T, T_N=None, realistic=True, n_g=721, n_f=201):
    if rng is None:
        return None
    p = par["p"]
    gam = np.linspace(np.pi / 2, np.pi, n_g)
    cf = np.array([rng[1]]) if rng[1] - rng[0] < 1e-9 else np.linspace(max(rng[0], 1e-3), rng[1], n_f)
    G, F = np.meshgrid(gam, cf, indexing="ij")
    c, s = np.cos(G), np.sin(G)
    psi_f = par["psi_per_amp_Wb"] * F
    m = T3.M_PH
    aT = m * p * psi_f * s
    bT = m * p * (par["L_d_H"] - par["L_q_H"]) * s * c
    with np.errstate(divide="ignore", invalid="ignore"):
        lin = np.abs(bT) < 1e-12 * np.maximum(aT, 1e-30)
        disc = aT ** 2 + 4 * bT * T
        I = np.where(lin, T / aT, np.where(disc >= 0, (-aT + np.sqrt(np.where(disc >= 0, disc, 0))) / (2 * np.where(lin, 1, bT)), np.nan))
    I = np.where(I > 0, I, np.nan)
    we = p * n * RPM
    Id, Iq = I * c, I * s
    psd, psq = psi_f + par["L_d_H"] * Id, par["L_q_H"] * Iq
    V = np.hypot(par["R_s_ohm"] * Id - we * psq, par["R_s_ohm"] * Iq + we * psd)
    ok = np.isfinite(I) & (I <= IMAX) & (V <= VMAX * (1 + 1e-9))
    if not np.any(ok):
        return None
    Ls = par["L_sigma_s_H"]
    B = np.hypot(psd - Ls * Id, psq - Ls * Iq) / par["psi_rms_per_T"]
    P_cu = m * I ** 2 * par["R_s_ohm"]
    P_fe = FB.iron_loss(par["design"], we / (2 * np.pi), B)
    iA, iB = field_currents(rot, p, F)
    P_f = P_FIELD_GROUP_MAX_W * (iA ** 2 + iB ** 2)
    P_exc = exciter_loss(iA) + exciter_loss(iB) if realistic else 0 * F
    P_ll = P_LL_N * (T / T_N) ** 2 if (realistic and T_N) else 0.0
    pw = pwm_loss(par)["P_total_W"] if realistic else 0.0
    loss = np.where(ok, P_cu + P_fe + P_f + P_exc, np.inf)
    j = np.unravel_index(int(np.argmin(loss)), loss.shape)
    Pm = float(T3.p_mech(n))
    Pout = T * n * RPM - Pm
    em = float(loss[j]) + P_ll + pw
    tot = em + Pm
    S = m * float(V[j]) * float(I[j])
    # realistic: circuit-consistent PF (air-gap power + stator copper); simple: T03 definition (for the sanity check)
    PF = (T * n * RPM + float(P_cu[j])) / S if realistic else (Pout + tot - float(P_f[j])) / S
    return dict(eta=Pout / (Pout + tot), eta_excl_friction_windage=(Pout + Pm) / (Pout + tot),
                PF=PF, S_inverter_used_kVA=S / 1e3, I_rms_A=float(I[j]), V_rms_V=float(V[j]),
                I_d_A=float(Id[j]), I_q_A=float(Iq[j]), pole_amplitude_pu=float(F[j]),
                i_field_A_pu=float(iA[j]), i_field_B_pu=float(iB[j]), B_gap_T=float(B[j]), f_e_Hz=we / (2 * np.pi),
                P_cu_stator_W=float(P_cu[j]), P_fe_W=float(P_fe[j]), P_field_cu_W=float(P_f[j]), P_exciter_W=float(P_exc[j]),
                P_stray_IEC_W=float(P_ll), P_pwm_W=float(pw), P_mech_W=Pm, P_loss_total_W=tot, speed_rpm=n, torque_Nm=T)


# ----------------------------------------------------------------------------------
# One HESM case: (stator, mapping, s, policy)
# ----------------------------------------------------------------------------------
def best_gear(T, tol=0.005):
    """T03b rule (max P at 90 km/h s.t. 12 % start and tip speed) with a tie-break: the smallest G whose
    P at 90 km/h is within 0.5 % of the maximum (the synchronous machines have flat P(G))."""
    Gb, Gmin, Gmax = FB.best_gear(T, NG, N_TIP)
    if Gb is None:
        return Gb, Gmin, Gmax
    Gs = np.linspace(4.0, 22.0, 721)
    ok = (Gs >= Gmin * 0.999) & (Gs <= Gmax)
    Pv = np.interp(FB.WHEEL_RPM_VMAX * Gs, NG, T * NG * RPM)
    Pbest = np.interp(FB.WHEEL_RPM_VMAX * Gb, NG, T * NG * RPM)
    return float(Gs[np.where(ok & (Pv >= (1 - tol) * Pbest))[0][0]]), Gmin, Gmax


def metrics_basic(T):
    return T3.metrics(T, NG)


def evaluate(st_name, mp, s, policy, maps=False, ng=481, nf=81):
    rot = rotor(s)
    pars = {p: machine(st_name, mp, rot, p) for p in (4, 2)}
    rng = {p: (field_range(rot, pars[p], policy) if pars[p]["winding"]["feasible"] else None) for p in (4, 2)}
    env = {p: (envelope(pars[p], NG, *rng[p], n_g=ng, n_f=nf) if rng[p] else np.zeros(len(NG))) for p in (4, 2)}
    Tc = np.maximum(env[4], env[2])
    out = dict(s=s, policy=policy, rotor=rot, field_range_pu={f"2p{2 * p}": rng[p] for p in (4, 2)},
               mode_feasible={f"2p{2 * p}": bool(rng[p] is not None and env[p].max() > 0) for p in (4, 2)})
    T_N = {}
    for p in (4, 2):
        if env[p].max() > 0:
            T_N[p] = T3.INV["P_rated_W"] / (metrics_basic(env[p])["n_base_rpm"] * RPM)
    res = {}
    for label, T, modes in (("fixed_2p8", env[4], (4,)), ("pole_changing", Tc, (4, 2))):
        modes = tuple(p for p in modes if p in T_N)
        if not modes:
            res[label] = None
            continue
        Gb, Gmin, Gmax = best_gear(T)
        G = Gb if Gb else Gmin
        mg = FB.metrics(T, NG, G)
        m98 = FB.metrics(T, NG, G_REF)
        pts = {}
        for name, w in FB.wheel_points().items():
            n_m, T_m = w["wheel_rpm"] * G, w["wheel_side_torque_Nm"] / G
            best = None
            for p in modes:
                r = op_point(pars[p], rot, rng[p], n_m, T_m, T_N[p])
                if r and (best is None or r["eta"] > best["eta"]):
                    best = dict(mode=f"2p{2 * p}", **r)
            pts[name] = best if best else dict(feasible=False, speed_rpm=n_m, torque_Nm=T_m)
        # UCG: field off, PM only, at the motor speed for 90 km/h
        n_v = FB.WHEEL_RPM_VMAX * G
        c8, c4 = (rot["m_A"] + rot["m_B"]) / 2, (rot["m_A"] - rot["m_B"]) / 2
        E = 4 * n_v * RPM * pars[4]["psi_per_amp_Wb"] * c8 + 2 * n_v * RPM * pars[2]["psi_per_amp_Wb"] * c4
        res[label] = dict(gear_ratio=G, gear_rule_feasible=Gb is not None, metrics=mg, metrics_at_G_9p80=m98,
                          crossover_speed_rpm=T3.crossover(env[4], env[2], NG) if label == "pole_changing" and 2 in T_N else None,
                          points=pts, torque_Nm=T.round(2).tolist(),
                          pole_count_2p_used=(np.where(env[2] > env[4] * 1.001, 4, 8).tolist() if label == "pole_changing" else None),
                          UCG_field_off_EMF_at_90kmh_over_V_ph_max=float(E / (VMAX / 0.95)))
    out.update(res)
    out["T_N_Nm"] = {f"2p{2 * p}": v for p, v in T_N.items()}
    mech = {}
    for p in (4, 2):
        q = pars[p]
        d = dict(k_w=q["k_w"], L_d_pu=q["L_d_H"] / T3.L_BASE, L_q_pu=q["L_q_H"] / T3.L_BASE,
                 X_d_at_same_rpm_pu=q["L_d_H"] / T3.L_BASE * p / 4, pole_amplitude_cap=q["amp_cap"], field_range=rng[p])
        if rng[p]:
            for tag, cc in (("max", rng[p][1]), ("min", rng[p][0])):
                psi = q["psi_per_amp_Wb"] * cc
                d[f"psi_rms_at_{tag}_field_pu"] = psi / T3.PSI_BASE
                d[f"EMF_per_1000rpm_at_{tag}_field_over_Vmax"] = p * 1000 * RPM * psi / VMAX
                d[f"I_ch_at_{tag}_field_over_Imax"] = psi / q["L_d_H"] / IMAX
        mech[f"2p{2 * p}"] = d
    out["mechanism"] = mech
    out["_env"], out["_pars"], out["_rng"] = env, pars, rng
    return out


def efficiency_map(case, n_pts=36, t_pts=26):
    pc = case["pole_changing"]
    if pc is None:
        return None
    pars, rng, rot = case["_pars"], case["_rng"], case["rotor"]
    modes = [p for p in (4, 2) if f"2p{2 * p}" in case["T_N_Nm"]]
    Tmax = max(case["_env"][p].max() for p in modes)
    n_grid = np.linspace(100.0, min(N_TIP, NG[-1]), n_pts)
    T_grid = np.linspace(0.02, 1.0, t_pts) * Tmax
    eta = np.full((n_pts, t_pts), np.nan)
    loss, mi = np.full_like(eta, np.nan), np.full_like(eta, np.nan)
    for i, n in enumerate(n_grid):
        for j, T in enumerate(T_grid):
            best = None
            for k, p in enumerate(modes):
                r = op_point(pars[p], rot, rng[p], n, T, case["T_N_Nm"][f"2p{2 * p}"], n_g=121, n_f=41)
                if r and (best is None or r["P_loss_total_W"] < best[1]):
                    best = (r["eta"], r["P_loss_total_W"], {4: 0, 2: 1}[p])
            if best:
                eta[i, j], loss[i, j], mi[i, j] = best
    return dict(gear_ratio=pc["gear_ratio"], speed_rpm=n_grid.round(3).tolist(), torque_Nm=T_grid.round(3).tolist(),
                modes=["2p8", "2p4"], eta=np.round(eta, 5).tolist(), loss_total_W=np.round(loss, 1).tolist(),
                mode_index=mi.tolist(),
                note="rows = speed, columns = torque (motor side); realistic loss set incl. field copper + exciter + friction/windage; "
                     "lower-loss feasible mode per point; NaN = outside envelope. Same format as fair_baselines.json.")


# ----------------------------------------------------------------------------------
# Pole transition: tau_f of group B, torque floor while B sweeps (group A / PM keeps polarity)
# ----------------------------------------------------------------------------------
def transition(case, n_rpm):
    rot, pars, rng = case["rotor"], case["_pars"], case["_rng"]
    if rng[4] is None or rng[2] is None:
        return None
    T8 = float(np.interp(n_rpm, NG, case["_env"][4]))
    T4 = float(np.interp(n_rpm, NG, case["_env"][2]))
    # start: 8-pole at the c giving the envelope (take max field); end: 4-pole max field
    c8, c4e = rng[4][1], rng[2][1]
    A0 = c8                                     # group A amplitude in 8-pole (A = B)
    # group A moves from c8 to c4e as well (coil); PM part fixed. Sweep B from +c8 to -c4e, A linear in the same parameter.
    lam = np.linspace(0, 1, 41)
    A = A0 + (c4e - A0) * lam
    B = c8 + (-c4e - c8) * lam
    k8, k4 = (A + B) / 2, (A - B) / 2
    we8, we2 = 4 * n_rpm * RPM, 2 * n_rpm * RPM
    E8, E4 = we8 * pars[4]["psi_per_amp_Wb"] * k8, we2 * pars[2]["psi_per_amp_Wb"] * k4
    Tfl = []
    for a8, a4, e8, e4 in zip(k8, k4, E8, E4):
        t8 = envelope(pars[4], np.array([n_rpm]), a8, a8, n_g=241, Vmax=max(VMAX - e4, 1e-6))[0] if VMAX > e4 else 0.0
        t4 = envelope(pars[2], np.array([n_rpm]), a4, a4, n_g=241, Vmax=max(VMAX - e8, 1e-6))[0] if VMAX > e8 else 0.0
        Tfl.append(max(t8, t4))
    Tfl = np.array(Tfl)
    Tref = max(T8, T4)
    tau0 = T3.pole_transition({"IM": {4: T3.im_params(4), 2: T3.im_params(2)}})["WRSM"]["tau_f_s"]
    tauB = tau0 * rot["kappa_B"]
    iB0, iB1 = field_currents(rot, 4, np.array(c8))[1], field_currents(rot, 2, np.array(c4e))[1]
    k = T3.WRSM_PU["field_forcing_ratio"]
    t_forced = tauB * math.log((abs(iB0) + k) / (k - abs(iB1))) if k > abs(iB1) else float("inf")
    return dict(speed_rpm=n_rpm, T_envelope_8pole_Nm=T8, T_envelope_4pole_Nm=T4, pole_amplitude_8pole=c8, pole_amplitude_4pole=c4e,
                group_B_current_pu=[float(iB0), float(iB1)], tau_f_groupB_s=tauB,
                t_forced_reversal_s=t_forced + T3.WRSM_PU["blanking_s"], forcing_ratio=k,
                t_unforced_P1_sequence_s=6 * tauB + T3.WRSM_PU["blanking_s"],
                torque_floor_min_over_Tref=float(Tfl.min() / Tref) if Tref > 0 else None,
                torque_floor_mean_over_Tref=float(Tfl.mean() / Tref) if Tref > 0 else None,
                torque_floor_at_B0_Nm=float(Tfl[np.argmin(np.abs(B))]),
                note="Lower bound: all current and voltage in the better rotor-field harmonic (p=4 component (A+B)/2 or p=2 component (A-B)/2); "
                     "the EMF of the unused harmonic is subtracted from the voltage budget. The SPB can carry both harmonics at once "
                     "(any p not divisible by 3), which can only raise the floor.")


# ----------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------
S_GRID = [0.0, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]


def strip(case):
    return {k: v for k, v in case.items() if not k.startswith("_")}


def summary_row(c):
    def one(r):
        if r is None:
            return None
        m, pts = r["metrics"], r["points"]
        def pt(name):
            q = pts[name]
            return None if q.get("feasible") is False else dict(mode=q["mode"], eta=q["eta"], eta_excl_fw=q["eta_excl_friction_windage"], PF=q["PF"],
                                                               I_rms_A=q["I_rms_A"], P_field_plus_exciter_W=q["P_field_cu_W"] + q["P_exciter_W"])
        return dict(gear_ratio=r["gear_ratio"], gear_rule_feasible=r["gear_rule_feasible"], T_peak_Nm=m["T_peak_Nm"],
                    max_start_grade_pct=m["max_start_grade_pct"], CPSR=m["CPSR"], CPSR_capped=m["CPSR_capped_by_eval_range"],
                    P_at_90kmh_kW=m["P_at_vmax_W"] / 1e3, T_per_leg_A_Nm_per_A=m["T_peak_per_leg_A_Nm_per_A"],
                    inverter_kVA_per_kW_base=m["inverter_kVA_per_kW_base"], crossover_speed_rpm=r["crossover_speed_rpm"],
                    cruise_85kmh_flat=pt("cruise_85kmh_flat"), part_load_50kmh_3pct=pt("part_load_50kmh_3pct_grade"),
                    UCG_EMF_over_Vmax=r["UCG_field_off_EMF_at_90kmh_over_V_ph_max"])
    return dict(s=c["s"], policy=c["policy"], PM_mass_kg=c["rotor"]["PM_mass_kg"], mode_feasible=c["mode_feasible"],
                mechanism=c["mechanism"], rotor=c["rotor"],
                pole_changing=one(c["pole_changing"]), fixed_2p8=one(c["fixed_2p8"]))


def main():
    ng, nf = (121, 31) if QUICK else (481, 81)
    mp16 = mapping(16, 48, "spb")
    mp2c = mapping(2, 48, "conto")
    mp2s = mapping(2, 48, "spb")
    wind = {f"N16_spb": {f"2p{2 * p}": winding(mp16, p) for p in (4, 2)},
            f"N2_conto_two_inverter": {f"2p{2 * p}": winding(mp2c, p) for p in (4, 2)},
            f"N2_spb_interleaved": {f"2p{2 * p}": winding(mp2s, p) for p in (4, 2)}}

    # ---- sanity: s = 0 must reproduce the T03 300 kW WRSM
    t03 = json.load(open(T3.OUT_JSON))
    c0 = evaluate("T03_yoke25mm", mp16, 0.0, "If_weakening", ng=961, nf=161)
    ref = t03["machines"]["WRSM_freeId"]
    m8, m4 = metrics_basic(c0["_env"][4]), metrics_basic(c0["_env"][2])
    cr = op_point(c0["_pars"][4], c0["rotor"], c0["_rng"][4], T3.N_CRUISE, T3.T_CRUISE, realistic=False)
    Tid0 = envelope(c0["_pars"][4], NG, 0, 1, n_f=801, Id0=True)
    sanity = dict(
        s0_vs_T03_WRSM_freeId_2p8=dict(T_peak_Nm=[m8["T_peak_Nm"], ref["2p8"]["metrics"]["T_peak_Nm"]],
                                       CPSR=[m8["CPSR"], ref["2p8"]["metrics"]["CPSR"]],
                                       P_at_4500rpm_W=[m8["P_at_vmax_W"], ref["2p8"]["metrics"]["P_at_vmax_W"]]),
        s0_vs_T03_WRSM_freeId_2p4=dict(T_peak_Nm=[m4["T_peak_Nm"], ref["2p4"]["metrics"]["T_peak_Nm"]],
                                       P_at_4500rpm_W=[m4["P_at_vmax_W"], ref["2p4"]["metrics"]["P_at_vmax_W"]]),
        s0_vs_T03_WRSM_Id0_2p8_P_at_4500rpm_W=[metrics_basic(Tid0)["P_at_vmax_W"], t03["machines"]["WRSM_Id0"]["2p8"]["metrics"]["P_at_vmax_W"]],
        s0_cruise_eta_simple_model_G9p80=[cr["eta"], t03["efficiency_points"]["cruise_85kmh_road_load"]["WRSM_freeId_2p8"]["eta"]],
        s0_cruise_PF_simple_model_G9p80=[cr["PF"], t03["efficiency_points"]["cruise_85kmh_road_load"]["WRSM_freeId_2p8"]["PF"]],
        N16_kw_numeric_vs_analytic={k: [v["k_w_numeric_MMF"], v["k_w"]] for k, v in wind["N16_spb"].items()},
        exciter_fit_check=dict(eta_rated=1 / (1 + EXC["k0"] + EXC["k1"]),
                               eta_light=EXC["x_light"] ** 2 / (EXC["x_light"] ** 2 + EXC["k0"] + EXC["k1"] * EXC["x_light"])))
    rel = lambda a: abs(a[0] / a[1] - 1)
    sanity["max_rel_err_s0_vs_T03"] = max(rel(sanity["s0_vs_T03_WRSM_freeId_2p8"]["T_peak_Nm"]), rel(sanity["s0_vs_T03_WRSM_freeId_2p8"]["CPSR"]),
                                         rel(sanity["s0_vs_T03_WRSM_freeId_2p8"]["P_at_4500rpm_W"]), rel(sanity["s0_vs_T03_WRSM_freeId_2p4"]["T_peak_Nm"]),
                                         rel(sanity["s0_vs_T03_WRSM_freeId_2p4"]["P_at_4500rpm_W"]), rel(sanity["s0_vs_T03_WRSM_Id0_2p8_P_at_4500rpm_W"]),
                                         rel(sanity["s0_cruise_eta_simple_model_G9p80"]))
    print("sanity:", json.dumps(sanity, indent=1, default=float))

    # ---- sweep
    sweep, maps, trans = {}, {}, {}
    for st_name in STATORS:
        for pol in POLICIES:
            key = f"{st_name}|N16_spb|{pol}"
            rows = []
            for s in S_GRID:
                c = evaluate(st_name, mp16, s, pol, ng=ng, nf=nf)
                rows.append(summary_row(c))
                if pol != "If_weakening_bipolarA" and not QUICK:
                    mk = f"HESM_s{s:.2f}_{st_name}_N16_{pol}"
                    if pol == "If_weakening" or st_name == "T03_yoke25mm":
                        maps[mk] = efficiency_map(c)
                if pol == "If_weakening":
                    pc = c["pole_changing"]
                    xs = pc["crossover_speed_rpm"] if pc else None
                    tr = {}
                    for n_x in ([xs] if xs else []) + [2000.0]:
                        tr[f"{n_x:.0f}rpm"] = transition(c, n_x)
                    trans[f"s{s:.2f}_{st_name}"] = tr
                print(f"{key} s={s:.2f}", json.dumps({k: (None if v is None else {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()
                                                                                    if kk in ("gear_ratio", "T_peak_Nm", "CPSR", "P_at_90kmh_kW", "crossover_speed_rpm")})
                                                      for k, v in rows[-1].items() if k in ("pole_changing",)}, default=float),
                      "cruise", (rows[-1]["pole_changing"] or {}).get("cruise_85kmh_flat"))
            sweep[key] = rows
    # ---- N = 2 (Conto two-inverter) next to N = 16, yoke variant, If weakening, s = 0 / 0.25 / 0.5
    for s in (0.0, 0.25, 0.5):
        for st_name in STATORS:
            c = evaluate(st_name, mp2c, s, "If_weakening", ng=ng, nf=nf)
            sweep.setdefault(f"{st_name}|N2_conto_two_inverter|If_weakening", []).append(summary_row(c))

    res = dict(
        meta=dict(script="02_analytics/hesm_envelope.py", task="T03c", date=_dt.date.today().isoformat(), python=sys.version.split()[0],
                  P_rated_W=T3.INV["P_rated_W"], quick_mode=QUICK,
                  inputs=["02_analytics/torque_speed_envelope.py (300 kW constants, WRSM per-unit model; read-only)",
                          "02_analytics/fair_baselines.py (stator design code, gear rule, realistic loss set; read-only)",
                          "02_analytics/results/torque_speed_envelope_300kW.json (sanity reference)",
                          "01_literature/inputs_for_analyst.md s7, 01_literature/papers/Conto2022hybrid.md",
                          "board/prior_work.md P1 (rectifier 99 % / 87 %), board/decisions.md D02, D03, D05"],
                  assumptions="02_analytics/assumptions_hesm.md",
                  inverter=dict(N_modules_reference=16, V_dc_V=1200.0, V_ph_rms_max_per_coil_V=VMAX, I_leg_rms_max_A=IMAX,
                                S_inverter_kVA=T3.M_PH * VMAX * IMAX / 1e3,
                                N_dependence="coil-frame model independent of N (V_leg = 1200/N, c = 48/(3N) coils in series per leg, N_c = 3); "
                                             "N enters through k_d(p) and module balance of each pole mode (see winding)"),
                  policies=dict(If_weakening="WRSM-style: field currents free within the rotor-copper limit (group A unipolar, group B bipolar) + free I_d <= 0",
                                fixed_field="field at the maximum of each mode, flux weakening by I_d only (PMSM-style)",
                                If_weakening_bipolarA="sensitivity: group-A coil may also buck its PM (demagnetisation risk not checked)"),
                  notes=["Efficiency is machine only (no inverter, no gearbox); includes field copper and exciter (rectifier) loss.",
                         "Rotor iron, pole-face and PM eddy losses are not included (as for the T03b IMs, whose rotor iron loss is also excluded).",
                         "Friction/windage = T03 law (T03d replaces it in T07)."]),
        winding=dict(mappings=wind,
                     spb_generalises_conto="Conto2022hybrid feeds each phase from two half-power inverters, coils under odd/even pole pairs; "
                                           "reversing inverter 2 (and swapping B/C) gives 4 poles. In SPB terms that is N = 2 with a fixed 0/180 deg "
                                           "group shift. SPB with N modules sets each leg phase freely (alpha_k = p 2 pi k/Q), so any p not "
                                           "divisible by 3 is available, every module stays a balanced 3-phase set, the winding factors rise (T03 48-slot stator, y = 7: "
                                           "SPB N = 16 k_w 0.966 / 0.793 for 2p = 8 / 4; Conto feed N = 2 k_w 0.933 / 0.507 with sigma_diff 0.18 in 4-pole), "
                                           "and both rotor-field harmonics can be carried at once during the rotor transition."),
        rotor_model=dict(B0_T=B0, P8_fundamental=H8, P4_fundamental=H4, PM=PM, exciter=EXC, P_field_per_group_max_W=P_FIELD_GROUP_MAX_W,
                         rotors={f"s{s:.2f}": rotor(s) for s in S_GRID}),
        stators={k: {f"2p{2 * p}": {kk: (float(vv) if isinstance(vv, (float, np.floating)) else vv) for kk, vv in machine(k, mp16, rotor(0.0), p).items()
                                     if kk not in ("design", "winding")} | {"design": machine(k, mp16, rotor(0.0), p)["design"]}
                     for p in (4, 2)} for k in STATORS},
        speed_rpm=NG.round(3).tolist(),
        sweep=sweep, pole_transition=trans, sanity_checks=sanity, efficiency_maps=maps,
        s0_case_detail=strip(c0) | {"pole_changing": {k: v for k, v in c0["pole_changing"].items()}})
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(res, f, indent=1, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else (bool(o) if isinstance(o, np.bool_) else float(o)))

    # ---- quick-look
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 3, figsize=(16, 8))
        for j, st_name in enumerate(STATORS):
            for s in (0.0, 0.25, 0.5):
                c = evaluate(st_name, mp16, s, "If_weakening", ng=161, nf=41)
                for p, ls in ((4, "-"), (2, "--")):
                    ax[0, j].plot(NG, c["_env"][p] * NG * RPM / 1e3, ls, label=f"s={s} 2p={2 * p}")
            ax[0, j].set_title(f"{st_name}, If weakening (P kW)")
            ax[0, j].axhline(300, color="k", lw=0.5)
            ax[0, j].legend(fontsize=7)
        for j, st_name in enumerate(STATORS):
            for pol in ("If_weakening", "fixed_field"):
                rows = sweep[f"{st_name}|N16_spb|{pol}"]
                ss = [r["s"] for r in rows]
                ax[1, 0].plot(ss, [r["pole_changing"]["P_at_90kmh_kW"] if r["pole_changing"] else np.nan for r in rows], "o-", label=f"PC {st_name} {pol}")
                ax[1, 0].plot(ss, [r["fixed_2p8"]["P_at_90kmh_kW"] if r["fixed_2p8"] else np.nan for r in rows], "x:", label=f"8p {st_name} {pol}")
                ax[1, 1].plot(ss, [(r["pole_changing"]["cruise_85kmh_flat"] or {}).get("eta", np.nan) * 100 if r["pole_changing"] else np.nan for r in rows], "o-", label=f"PC {st_name} {pol}")
                ax[1, 1].plot(ss, [(r["fixed_2p8"]["cruise_85kmh_flat"] or {}).get("eta", np.nan) * 100 if r["fixed_2p8"] else np.nan for r in rows], "x:", label=f"8p {st_name} {pol}")
                ax[1, 2].plot(ss, [r["pole_changing"]["CPSR"] if r["pole_changing"] else np.nan for r in rows], "o-", label=f"PC {st_name} {pol}")
        ax[1, 0].set_title("P at 90 km/h (kW), own gear")
        ax[1, 1].set_title("cruise 85 km/h eta (%)")
        ax[1, 2].set_title("CPSR")
        for a in ax[1]:
            a.set_xlabel("PM share s")
            a.legend(fontsize=6)
        fig.tight_layout()
        os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
        fig.savefig(OUT_PNG, dpi=100)
    except Exception as exc:
        print("plot skipped:", exc)


if __name__ == "__main__":
    main()

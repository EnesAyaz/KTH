"""Gap-loop iteration 2, H11 / H11s (analyst part).

Run from repo root:  python 02_analytics/screen_H11.py
Outputs: 02_analytics/results/screen_H11.json ; adds an 'iteration2_correction' block to results/screen_H10.json
Assumptions: 02_analytics/assumptions.md, section H11.

1. H10 correction: crossfade envelope x(1-x), C for +-5 / +-10 % ripple, the V8*I4 term of a 'sequential' handover,
   balancing-knob strength per ampere (m V_p, not winding-factor limited).
2. Cost table m = 3 + bulk C vs m = 5 (N = 16): (a) IM transient, (b) continuous H03s order-8 excitation incl. ripple
   heating and lifetime, (c) post-bypass N-1 operation + post-bypass mode table.
3. H11s: pulsation-constrained m = 3 IM 8->4 handover (demagnetise -> rebuild), +-10 % at 2.9 mF, gap <= 0.2 s,
   no torque reversal, flat and 2 % grade. Two-mode rotor-flux-oriented model (same structure as the simulator's).
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault("SPB_P_RATED_KW", "300")
import torque_speed_envelope as T3  # noqa: E402
import fair_baselines as FB         # noqa: E402
import module_count_sweep as MS     # noqa: E402
import screen_H10 as H10            # noqa: E402

RES = os.path.join(ROOT, "02_analytics", "results")
OUT = os.path.join(RES, "screen_H11.json")
H10_JSON = os.path.join(RES, "screen_H10.json")
M_PH, RPM = T3.M_PH, T3.RPM
V_MOD = 75.0
C_NOM, C_WORST = H10.C_MOD["nominal"], H10.C_MOD["worst_retained"]


def p_allow(f, C, frac, V=V_MOD):
    return 2 * math.pi * f * V * frac * V * C


def c_req(P, f, frac, V=V_MOD):
    return P / (2 * math.pi * f * V * frac * V)


# ----------------------------------------------------------------------------------
# Two-mode IM transition model (rotor-flux oriented, per coil-phase rms, m = 48 coil-phases)
# ----------------------------------------------------------------------------------
class Mode:
    def __init__(self, d):
        self.p = d["p"]
        self.Rs, self.Ls, self.Lm = d["R_s_ohm"], d["L_sigma_s_H"], d["Lm_H"]
        self.Rr, self.Lsr = d["R_r_ohm"], d["L_sigma_r_H"]
        self.Lr = self.Lm + self.Lsr
        self.tau_r = self.Lr / self.Rr
        self.sL = self.Ls + self.Lm * self.Lsr / self.Lr
        self.kT = M_PH * self.p * self.Lm / self.Lr
        self.psi_cap = d["psi_cap_rms_Wb"] * self.Lr / self.Lm   # rotor-flux cap (airgap cap referred)

    def volt(self, wm, psi, i_d, i_q):
        wsl = (self.Rr / self.Lr) * self.Lm * i_q / psi if abs(psi) > 1e-5 else 0.0
        we = self.p * wm + wsl
        vd = self.Rs * i_d - we * self.sL * i_q
        vq = self.Rs * i_q + we * (self.sL * i_d + self.Lm / self.Lr * psi)
        return math.hypot(vd, vq), we


def steady(mode, wm, T):
    """Steady-state flux (voltage-limited, capped) and currents for torque T."""
    psi = min(mode.psi_cap, 0.85 * T3.VMAX / (mode.p * wm) * mode.Lr / mode.Lm)
    iq = T / (mode.kT * psi)
    idd = psi / mode.Lm
    return psi, idd, iq


def simulate(d8, d4, n_rpm, T_req, strategy, C=C_NOM, ripple_frac=0.10, I_max=None, dt=1e-4, t_end=1.2,
             t_rd=0.02, I_dem_frac=1.0, eps=0.02, crossfade_s=0.25, tau_i=1e-3):
    m8, m4 = Mode(d8), Mode(d4)
    I_max = I_max or T3.IMAX
    wm = n_rpm * RPM
    psi8, id8_0, iq8_0 = steady(m8, wm, T_req)
    psi4_t, id4_t, iq4_t = steady(m4, wm, T_req)
    psi4 = 0.0
    id8, iq8, id4, iq4 = id8_0, iq8_0, 0.0, 0.0
    f_sum = (m8.p + m4.p) * n_rpm / 60
    Pal = p_allow(f_sum, C, ripple_frac)
    t = 0.0
    log = dict(t=[], T=[], Px=[], dV=[], v_sum=[], i_sum=[], psi8=[], psi4=[])
    phase = "A"
    t_phase = 0.0
    P8_0 = None
    while t < t_end:
        v8, we8 = m8.volt(wm, psi8, id8, iq8)
        v4, we4 = m4.volt(wm, psi4, id4, iq4)
        i8, i4 = math.hypot(id8, iq8), math.hypot(id4, iq4)
        # ---- commands
        if strategy == "crossfade":
            x = min(max(t / crossfade_s, 0.0), 1.0)
            c_id8, c_iq8 = (1 - x) * id8_0, (1 - x) * iq8_0
            c_id4 = x * id4_t + (1 - x) * 0.0
            c_iq4 = x * iq4_t * (psi4_t / max(psi4, 1e-3 * psi4_t)) if psi4 > 0.05 * psi4_t else 0.0
            c_iq4 = min(c_iq4, iq4_t * 3)
        else:
            # A: ramp torque down (and in 'h11s' start demagnetising); B: demag; C: build; D: run
            if phase == "A":
                r = min(t / t_rd, 1.0) if t_rd > 0 else 1.0
                c_iq8 = (1 - r) * iq8_0
                c_id8 = id8_0
                if r >= 1.0:
                    phase, t_phase = "B", t
            if phase == "B":
                c_iq8 = 0.0
                if strategy == "h11s":
                    c_id8 = -I_dem_frac * I_max if psi8 > eps * steady(m8, wm, T_req)[0] else 0.0
                    if c_id8 == 0.0:
                        phase, t_phase = "C", t
                else:                      # passive sequential: drop all 8-pole current, let the rotor flux decay
                    c_id8 = 0.0
                    phase, t_phase = "C", t
            if phase in ("C", "D"):
                c_id8, c_iq8 = 0.0, 0.0
            # 4-pole commands, limited by the current budget and (for h11s / passive) by the pulsation allowance
            I_av = max(I_max - max(math.hypot(id8, iq8), math.hypot(c_id8, c_iq8)) - 0.02 * I_max, 0.0)
            if phase in ("B", "C", "D") and (strategy == "h11s" or phase in ("C", "D")):
                if psi4 < 0.98 * psi4_t:
                    c_id4 = min(I_av, max(id4_t, 0.95 * I_av))
                else:
                    c_id4 = id4_t
                    phase = "D"
                iq_need = T_req / (m4.kT * max(psi4, 1e-4))
                c_iq4 = min(iq_need, math.sqrt(max(I_av ** 2 - c_id4 ** 2, 0.0))) if psi4 > 0.05 * psi4_t else 0.0
                if strategy in ("h11s", "passive"):
                    # pulsation constraint: 3 (v8 i4 + v4 i8) <= P_allow
                    lim = (Pal - 3 * v4 * i8) / (3 * max(v8, 1e-6))
                    lim = max(lim, 0.0)
                    mag = math.hypot(c_id4, c_iq4)
                    if mag > lim:
                        s = lim / mag
                        c_id4, c_iq4 = c_id4 * s, c_iq4 * s
            else:
                c_id4, c_iq4 = 0.0, 0.0
        # ---- current loops
        a = dt / tau_i
        id8 += a * (c_id8 - id8)
        iq8 += a * (c_iq8 - iq8)
        id4 += a * (c_id4 - id4)
        iq4 += a * (c_iq4 - iq4)
        # ---- rotor flux
        psi8 += dt / m8.tau_r * (m8.Lm * id8 - psi8)
        psi4 += dt / m4.tau_r * (m4.Lm * id4 - psi4)
        T = m8.kT * psi8 * iq8 + m4.kT * psi4 * iq4
        Px = 3 * (v8 * math.hypot(id4, iq4) + v4 * math.hypot(id8, iq8))
        log["t"].append(t)
        log["T"].append(T)
        log["Px"].append(Px)
        log["dV"].append(Px / (2 * math.pi * f_sum * V_MOD * C))
        log["v_sum"].append(v8 + v4)
        log["i_sum"].append(math.hypot(id8, iq8) + math.hypot(id4, iq4))
        log["psi8"].append(psi8)
        log["psi4"].append(psi4)
        t += dt
        if strategy != "crossfade" and phase == "D" and T >= 0.98 * T_req and t > 0.05:
            # run a little longer to catch residuals, then stop
            if t - t_phase > 0.05:
                break
    Ta = np.array(log["T"])
    ta = np.array(log["t"])
    below = Ta < 0.9 * T_req
    gap = float(below.sum() * dt)
    rec95 = float(ta[np.where(Ta >= 0.95 * T_req)[0][-1]] if False else 0.0)
    deficit = float(np.sum(np.clip(T_req - Ta, 0, None)) * dt)
    G, r_w = FB.G_REF, T3.VEH["wheel_radius_m"]
    dv = deficit * G * T3.VEH["eta_gear"] / r_w / (T3.VEH["mass_kg"] * T3.VEH["mass_factor"])
    Px = np.array(log["Px"])
    P8_0 = 3 * (m8.volt(wm, steady(m8, wm, T_req)[0], id8_0, iq8_0)[0] * math.hypot(id4_t, iq4_t)
                + m4.volt(wm, psi4_t, id4_t, iq4_t)[0] * math.hypot(id8_0, iq8_0))
    return dict(strategy=strategy, n_rpm=n_rpm, T_req_Nm=T_req, C_mF=C * 1e3, ripple_allowed_frac=ripple_frac,
                f_sum_Hz=f_sum, P_allow_W=Pal,
                torque_min_Nm=float(Ta.min()), torque_reversal=bool(Ta.min() < -0.01 * T_req),
                torque_gap_below90pct_s=gap, torque_deficit_Nms=deficit, speed_drop_kmh=dv * 3.6,
                Px_max_W=float(Px.max()), ripple_max_pk_V=float(max(log["dV"])), ripple_max_pct=float(max(log["dV"]) / V_MOD * 100),
                within_ripple=bool(max(log["dV"]) <= ripple_frac * V_MOD * 1.001),
                envelope_factor=float(Px.max() / P8_0) if P8_0 else None, P_cross_steady_products_W=P8_0,
                i_sum_max_A=float(max(log["i_sum"])), v_sum_max_V=float(max(log["v_sum"])), V_max_V=T3.VMAX,
                psi8_0_Wb=float(steady(m8, wm, T_req)[0]), psi4_target_Wb=float(psi4_t),
                duration_s=float(ta[-1]),
                trace_decimated=dict(t=ta[::50].round(4).tolist(), T=Ta[::50].round(1).tolist(), Px=Px[::50].round(0).tolist()))


# ----------------------------------------------------------------------------------
# Post-bypass mode table
# ----------------------------------------------------------------------------------
def post_bypass(N, m, Q, pairs, bypass_sets, V_class):
    """pairs: list of (p_hi, p_lo); each pair gets its own coil pitch (as in T08)."""
    out = {}
    for hi, lo in pairs:
        out[f"pair_{2 * hi}/{2 * lo}"] = _post_bypass_pair(N, m, Q, (hi, lo), bypass_sets, V_class)
    return out


def _post_bypass_pair(N, m, Q, modes, bypass_sets, V_class):
    cb = MS.screen_combo(N, m, Q)
    w = next(w for w in cb["wirings"] if w["family"] == "spaced" and w["partition"] == "interleaved" and all(s == 1 for s in w["signs"]))
    out = {}
    for p in modes:
        if p not in w["modes"]:
            continue
        y = MS.best_pitch(Q, max(modes), min(modes))
        P = MS.leg_phasor(w["legs"], w["signs"], Q, p)
        ang = np.angle(P)

        def spectrum(dead_modules):
            dead = {l for j in dead_modules for l in w["modules"][j]}
            Islot = np.zeros(Q)
            for li, coils in enumerate(w["legs"]):
                if li in dead:
                    continue
                for k in coils:
                    i = math.cos(ang[li])
                    Islot[k % Q] += i
                    Islot[(k + y) % Q] -= i
            nth = 4096
            pos = ((np.arange(Q) + 0.5) / Q * nth).astype(int)
            dF = np.zeros(nth)
            dF[pos] = Islot
            F = np.cumsum(dF)
            F -= F.mean()
            return np.abs(np.fft.rfft(F))[:200] / nth * 2
        F0 = spectrum([])
        res = {}
        for name, dead in bypass_sets.items():
            k = len(dead)
            Fb = spectrum(dead)
            ratio = Fb[p] / F0[p]
            harm = {int(nu): float(Fb[nu] / Fb[p]) for nu in range(1, 60) if nu != p and Fb[nu] / Fb[p] > 0.01 and Fb[nu] > F0[nu] * 1.5 + 1e-9}
            ump = sorted(nu for nu in harm if abs(nu - p) == 1)
            V_cell = MS.V_DC / (N - k)
            res[name] = dict(bypassed_modules=list(dead), V_cell_V=V_cell, V_cell_over_class=V_cell / V_class,
                             voltage_admissible=bool(V_cell <= MS.DERATING_PARK_MAX * V_class),
                             fundamental_ratio=float(ratio), torque_derating_same_current=float(1 - ratio),
                             new_harmonics_rel=harm, UMP_orders_p_pm_1=ump,
                             cell_power="remaining modules unchanged and balanced -> zero average imbalance and no pulsation (hole fields are "
                                        "same-frequency and reactive w.r.t. the main current, first order)")
        out[f"2p{2 * p}"] = dict(k_w_full=float(MS.pitch_factor(p, y, Q) * w["modes"][p]["kd"]), y_slots=y, **res)
    return out


# ----------------------------------------------------------------------------------
# Cost data (assumptions; unverified catalogue-typical values, see assumptions.md#h11)
# ----------------------------------------------------------------------------------
COST = dict(
    note="Unit prices are assumed order-of-magnitude distributor list prices at ~1k pcs, NOT verified (no web access in this run). "
         "Request lit-scout/Enes to replace with quotes. Ratios matter more than absolutes.",
    EPC2361_EUR=6.0, gate_driver_channel_EUR=3.0, isolated_supply_channel_EUR=6.0, current_sensor_per_leg_EUR=4.0,
    pcb_assembly_per_leg_EUR=15.0, mass_per_leg_g=60.0, volume_per_leg_cm3=40.0,
    winding_extra_m5_EUR=300.0, winding_extra_m5_note="80 vs 48 coils, more coil ends/insulation/connections (assumed)",
    caps=dict(
        Al_electrolytic_100V_1mF=dict(C_uF=1000, EUR=2.0, vol_cm3=10.2, mass_g=14.0, I_ripple_A_120Hz_105C=2.5, f_mult_400Hz=1.3,
                                      ESR_mOhm_400Hz=45.0, Rth_K_per_W=15.0, life_h_at_105C=5000, T_rated_C=105,
                                      size="18 x 40 mm (typical)"),
        hybrid_polymer_100V_330uF=dict(C_uF=330, EUR=1.6, vol_cm3=2.5, mass_g=4.0, I_ripple_A_120Hz_105C=1.2, f_mult_400Hz=1.0,
                                       ESR_mOhm_400Hz=60.0, Rth_K_per_W=30.0, life_h_at_105C=10000, T_rated_C=125,
                                       size="12.5 x 20 mm (typical); ripple rating at low frequency is much lower than at 100 kHz"),
        MLCC_100V_22uF_X7S_2220=dict(C_uF=22 * 0.35, EUR=0.8, vol_cm3=0.08, mass_g=0.3, I_ripple_A_120Hz_105C=3.0, f_mult_400Hz=1.0,
                                     ESR_mOhm_400Hz=5.0, Rth_K_per_W=60.0, life_h_at_105C=1e6, T_rated_C=125,
                                     size="TDK C5750X7S2A226M280KB as on Rev B; 0.35 DC-bias retention assumed")),
    T_ambient_C=85.0, life_target_h=25000.0,
    life_target_note="truck: ~1.2 Mkm at ~50 km/h average -> ~25 kh operating (assumption)")


def cap_bank(C_need_F, I_rms_A, kind):
    c = COST["caps"][kind]
    n_C = math.ceil(C_need_F / (c["C_uF"] * 1e-6) - 1e-9) if C_need_F > 0 else 0
    I_rate = c["I_ripple_A_120Hz_105C"] * c["f_mult_400Hz"]
    n_I = math.ceil(I_rms_A / I_rate - 1e-9) if I_rms_A > 0 else 0
    n = max(n_C, n_I, 0)
    if n == 0:
        return dict(kind=kind, n=0, EUR=0.0, vol_cm3=0.0, mass_g=0.0, ESR_loss_W=0.0, life_h=None)
    I_each = I_rms_A / n
    P = n * I_each ** 2 * c["ESR_mOhm_400Hz"] * 1e-3
    Tcore = COST["T_ambient_C"] + I_each ** 2 * c["ESR_mOhm_400Hz"] * 1e-3 * c["Rth_K_per_W"]
    life = c["life_h_at_105C"] * 2 ** ((c["T_rated_C"] - Tcore) / 10.0)
    return dict(kind=kind, n=n, n_by_C=n_C, n_by_ripple=n_I, C_total_mF=n * c["C_uF"] * 1e-3, EUR=n * c["EUR"],
                vol_cm3=n * c["vol_cm3"], mass_g=n * c["mass_g"], I_each_A=I_each, ESR_loss_W=P, T_core_C=Tcore, life_h=life,
                meets_life_target=bool(life >= COST["life_target_h"]))


def m5_extra_cost():
    inv3 = MS.inverter_design(16, 3)
    inv5 = MS.inverter_design(16, 5)
    dlegs = inv5["legs"] - inv3["legs"]
    ddev = inv5["devices_total"] - inv3["devices_total"]
    eur = (ddev * COST["EPC2361_EUR"] + 2 * dlegs * (COST["gate_driver_channel_EUR"] + COST["isolated_supply_channel_EUR"])
           + dlegs * (COST["current_sensor_per_leg_EUR"] + COST["pcb_assembly_per_leg_EUR"]) + COST["winding_extra_m5_EUR"])
    return dict(legs_m3=inv3["legs"], legs_m5=inv5["legs"], extra_legs=dlegs, devices_m3=inv3["devices_total"], devices_m5=inv5["devices_total"],
                extra_devices=ddev, extra_gate_drivers=2 * dlegs, extra_isolated_supplies=2 * dlegs, extra_current_sensors=dlegs,
                I_leg_max_m3_A=inv3["I_leg_rms_max_A"], I_leg_max_m5_A=inv5["I_leg_rms_max_A"],
                EUR=eur, mass_g=dlegs * COST["mass_per_leg_g"], vol_cm3=dlegs * COST["volume_per_leg_cm3"])


# ----------------------------------------------------------------------------------
def main():
    fb = json.load(open(FB.OUT_JSON))
    pc = fb["machines"]["pole_changing_2p8_4_T03"]["design"]
    d8, d4 = pc["2p8"], pc["2p4"]
    h10 = json.load(open(H10_JSON))
    res = dict(meta=dict(script="02_analytics/screen_H11.py", date=_dt.date.today().isoformat(), P_rated_W=T3.INV["P_rated_W"],
                         I_max_A=T3.IMAX, inputs=["02_analytics/results/fair_baselines.json (pole-changing IM, 300 kW)",
                                                  "02_analytics/results/screen_H10.json", "03_simulation/results/im_pole_transition.json",
                                                  "02_analytics/results/screen_H03.json (other analyst)"],
                         assumptions="02_analytics/assumptions.md#h11",
                         C_cell_mF=dict(nominal=C_NOM * 1e3, worst_retained=C_WORST * 1e3)))

    # ---- 1. H10 correction
    im = h10["transition_IM_handover"]
    P_ss = im["m3"]["P_pulse_amplitude_W"]
    f = im["m3"]["f_Hz"]
    flat = simulate(d8, d4, 2100.0, 248.12612268183904, "crossfade")
    grade = simulate(d8, d4, 2100.0, 677.2244, "crossfade")
    passive = simulate(d8, d4, 2100.0, 248.12612268183904, "passive", t_end=3.0)
    corr = dict(
        crossfade_analytic=dict(factor=0.25, P_pulse_W=0.25 * P_ss,
                                C_required_mF={"5pct": c_req(0.25 * P_ss, f, 0.05) * 1e3, "10pct": c_req(0.25 * P_ss, f, 0.10) * 1e3}),
        crossfade_model=dict(flat_envelope_factor=flat["envelope_factor"], flat_Px_max_W=flat["Px_max_W"],
                             flat_C_required_mF={"5pct": c_req(flat["Px_max_W"], f, 0.05) * 1e3, "10pct": c_req(flat["Px_max_W"], f, 0.10) * 1e3},
                             grade2_Px_max_W=grade["Px_max_W"],
                             grade2_C_required_mF={"5pct": c_req(grade["Px_max_W"], f, 0.05) * 1e3, "10pct": c_req(grade["Px_max_W"], f, 0.10) * 1e3},
                             note="naive linear 0.25 s CURRENT crossfade (no flux forcing) in the two-mode RFOC model: the terminal voltage follows "
                                  "the rotor flux, which lags the current by tau_r (0.48 s for 2p8, 1.46 s for 2p4), so V8 stays high while I4 rises "
                                  "and the envelope factor exceeds 1. The ideal x(1-x) = 0.25 assumes the fluxes track the currents instantly. "
                                  "The true factor of a flux-forced overlapped schedule lies between; the simulator's MEC run (confirm_H10) decides."),
        sequential_V8_I4_term=dict(
            note="'sequential' = drop all 2p8 current, then build 2p4 under the pulsation limit; the decaying 2p8 rotor flux still induces V8, "
                 "so 3 V8 I4 limits the 2p4 build current until the flux has decayed",
            tau_r_2p8_s=Mode(d8).tau_r, torque_gap_below90pct_s=passive["torque_gap_below90pct_s"],
            Px_max_W=passive["Px_max_W"], within_10pct_at_2p9mF=passive["within_ripple"]),
        balancing_knob_correction=dict(
            statement="The power shift per ampere of a same-frequency balancing order b is m V_p (main-mode leg voltage x m), independent of the "
                      "winding factor of b. Signed orders count: for p = 4, m = 5 the order b = -1 (counter-rotating 2-pole) satisfies 5 | (p - b). "
                      "So m = 5 is NOT a weaker knob (H10 said so - corrected).",
            m3_W_per_A=3 * T3.VMAX, m5_W_per_A=5 * MS.T3.INV["m_margin"] * MS.k_m(5) * V_MOD / math.sqrt(2),
            I_for_1pct_of_18p75kW_A={"m3": 187.5 / (3 * T3.VMAX), "m5": 187.5 / (5 * MS.T3.INV["m_margin"] * MS.k_m(5) * V_MOD / math.sqrt(2))}))
    h10["iteration2_correction"] = dict(corr, date=_dt.date.today().isoformat(), by="02_analytics/screen_H11.py",
                                        note="screen_H10.py rerun would drop this block; the numbers are reproduced by screen_H11.py")
    h10["admissible_mode_set"]["IM_handover_m3_corrected"] = (
        f"crossfade (factor {flat['envelope_factor']:.2f} in the model): C_req {c_req(flat['Px_max_W'], f, 0.10) * 1e3:.1f} mF at +-10 %, "
        f"{c_req(flat['Px_max_W'], f, 0.05) * 1e3:.1f} mF at +-5 % (flat). See screen_H11.json for the pulsation-constrained schedule.")
    json.dump(h10, open(H10_JSON, "w"), indent=1, default=MS.fmt)
    res["H10_correction"] = corr

    # ---- 3. H11s schedules
    h11s = {}
    for gname, T_req in (("flat", 248.12612268183904), ("grade_2pct", 677.2244)):
        for Cn, C in (("2.9mF", C_NOM), ("1.0mF", C_WORST)):
            for frac in (0.10, 0.05):
                r = simulate(d8, d4, 2100.0, T_req, "h11s", C=C, ripple_frac=frac)
                h11s[f"{gname}_{Cn}_{int(frac * 100)}pct"] = r
                print(f"H11s {gname:10s} C={Cn} +-{int(frac * 100)}%: gap={r['torque_gap_below90pct_s']:.3f}s Tmin={r['torque_min_Nm']:.0f} "
                      f"rev={r['torque_reversal']} ripple={r['ripple_max_pct']:.1f}% ok={r['within_ripple']} dv={r['speed_drop_kmh']:.3f}km/h "
                      f"isum={r['i_sum_max_A']:.0f} vsum={r['v_sum_max_V']:.1f}")
    for k, v in (("crossfade_flat", flat), ("crossfade_grade_2pct", grade), ("passive_sequential_flat", passive)):
        h11s[k] = v
        print(f"{k}: gap={v['torque_gap_below90pct_s']:.3f} Tmin={v['torque_min_Nm']:.0f} Px={v['Px_max_W']:.0f} ripple={v['ripple_max_pct']:.1f}% env={v['envelope_factor']}")
    main_ok = {k: (v["within_ripple"] and v["torque_gap_below90pct_s"] <= 0.2 and not v["torque_reversal"])
               for k, v in h11s.items() if k.endswith("2.9mF_10pct")}
    res["H11s"] = dict(target="+-10 % ripple at 2.9 mF, torque gap <= 0.2 s, no torque reversal, flat and 2 % grade, 2100 rpm",
                       schedule="A: ramp 2p8 torque current to 0 in 20 ms; B: demagnetise 2p8 with i_d8 = -I_max until psi8 < 2 % "
                                "(single order -> no cell pulsation); C: build 2p4 flux with i_d4 up to the current budget, 2p4 current "
                                "limited online by 3 (V8 I4 + V4 I8) <= P_allow(f8+f4, C, ripple); torque current as soon as psi4 > 5 %; D: run",
                       meets_target=main_ok, runs=h11s,
                       model_note="Two-mode RFOC model with T03 IM parameters at 300 kW (I_max 266 A); linear magnetics (no saturation "
                                  "intermodulation); simulator confirm_H10 (MEC) should repeat it.")

    # ---- 2c. post-bypass table
    pb = dict(
        N16_m3_Q48=post_bypass(16, 3, 48, [(4, 2)], {"one_cell": [0], "two_adjacent": [0, 1], "two_opposite": [0, 8]}, 100.0),
        N16_m5_Q80=post_bypass(16, 5, 80, [(4, 2), (6, 2)], {"one_cell": [0], "two_adjacent": [0, 1], "two_opposite": [0, 8]}, 100.0),
        note="Bypass = module DC port shorted, its coil group unpowered (fixed wiring; at N = 15 c = Q/(mN) is not an integer, so the remaining "
             "coils cannot be regrouped - the machine runs with a hole). Cell voltage limit 0.80 V_class (H05).")
    res["post_bypass_mode_table"] = pb

    # ---- 2. cost table
    ex = m5_extra_cost()
    inj = h10["harmonic_injection_H03"]["points"] if h10.get("harmonic_injection_H03") else {}
    cases = {}
    # (a) IM transient: crossfade (model factor) at +-5 % / +-10 %, and H11s (zero extra C if it meets the target)
    Px_a = flat["Px_max_W"]
    for frac in (0.05, 0.10):
        Cn = c_req(Px_a, f, frac)
        for Cav_n, Cav in (("nominal", C_NOM), ("worst_retained", C_WORST)):
            extra = max(Cn - Cav, 0.0)
            bank = cap_bank(extra, 0.0, "Al_electrolytic_100V_1mF")
            cases.setdefault("a_IM_transient_crossfade", {})[f"{int(frac * 100)}pct_{Cav_n}"] = dict(
                C_required_mF=Cn * 1e3, extra_mF_per_cell=extra * 1e3, per_cell=bank,
                stack=dict(EUR=16 * bank["EUR"], vol_L=16 * bank["vol_cm3"] / 1e3, mass_kg=16 * bank["mass_g"] / 1e3))
    cases["a_IM_transient_H11s"] = dict(extra_mF_per_cell=0.0 if main_ok.get("flat_2.9mF_10pct") else None,
                                        note="pulsation-constrained schedule needs no extra capacitance if H11s meets the target (see H11s)")
    # (b) continuous H03s order-8 excitation
    for pt, v in inj.items():
        P = v["P_pulse_amplitude_W"]
        fp = v["f_Hz"]
        I_rms = P / V_MOD / math.sqrt(2)
        row = {}
        for frac in (0.05, 0.10):
            Cn = c_req(P, fp, frac)
            extra = max(Cn - C_NOM, 0.0)
            row[f"{int(frac * 100)}pct"] = dict(C_required_mF=Cn * 1e3, extra_mF_per_cell_vs_nominal=extra * 1e3,
                                                ripple_current_rms_A=I_rms,
                                                banks={k: cap_bank(extra, I_rms, k) for k in COST["caps"]})
            for k, b in row[f"{int(frac * 100)}pct"]["banks"].items():
                b["stack_EUR"] = 16 * b["EUR"]
                b["stack_vol_L"] = 16 * b["vol_cm3"] / 1e3
                b["stack_mass_kg"] = 16 * b["mass_g"] / 1e3
                b["stack_ESR_loss_W"] = 16 * b["ESR_loss_W"]
        cases.setdefault("b_H03s_continuous_excitation", {})[pt] = dict(P_pulse_W=P, f_Hz=fp, **row)
    # (c) post-bypass
    cases["c_post_bypass_N_minus_1"] = dict(
        m3=dict(extra_C=0.0, torque_derating=pb["N16_m3_Q48"]["pair_8/4"]["2p8"]["one_cell"]["torque_derating_same_current"],
                cell_voltage_V=pb["N16_m3_Q48"]["pair_8/4"]["2p8"]["one_cell"]["V_cell_V"]),
        m5=dict(extra_C=0.0, torque_derating=pb["N16_m5_Q80"]["pair_8/4"]["2p8"]["one_cell"]["torque_derating_same_current"],
                cell_voltage_V=pb["N16_m5_Q80"]["pair_8/4"]["2p8"]["one_cell"]["V_cell_V"]),
        note="No cell pulsation or average imbalance from the hole in either m (first order); both lose 1/16 of the fundamental. "
             "Two bypassed cells exceed 0.80 V_class (85.7 V on 100 V) for both. m = 5 gives no post-bypass advantage.")
    # m = 5 cost, and the comparison
    best_b = None
    for pt, v in cases.get("b_H03s_continuous_excitation", {}).items():
        for frac in ("5pct",):
            banks = v[frac]["banks"]
            ok = {k: b for k, b in banks.items() if b.get("meets_life_target", True) or b["n"] == 0}
            cand = min(ok.values() or banks.values(), key=lambda b: b["stack_EUR"])
            if best_b is None or cand["stack_EUR"] > best_b[1]["stack_EUR"]:
                best_b = (pt, cand)
    m5 = ex
    verdict_b = None
    if best_b:
        verdict_b = dict(worst_point=best_b[0], m3_bulk_option=best_b[1]["kind"], m3_bulk_stack_EUR=best_b[1]["stack_EUR"],
                         m3_bulk_stack_L=best_b[1]["stack_vol_L"], m3_bulk_stack_kg=best_b[1]["stack_mass_kg"],
                         m3_bulk_ESR_loss_W=best_b[1]["stack_ESR_loss_W"], m5_extra_EUR=m5["EUR"],
                         m5_extra_kg=m5["mass_g"] / 1e3, m5_extra_L=m5["vol_cm3"] / 1e3,
                         m5_wins_clearly=bool(m5["EUR"] < 0.5 * best_b[1]["stack_EUR"]))
    res["cost_table"] = dict(unit_cost_assumptions=COST, m5_extra_hardware_N16=m5, cases=cases, verdict_case_b=verdict_b,
                             verdict=("m = 5 does not win a steady-state case clearly: (b) continuous excitation is cheaper as m = 3 + bulk "
                                      "capacitance than as 32 extra legs (+winding), and (c) post-bypass gives no m = 5 advantage. "
                                      "m = 5 keeps the advantage of zero extra C and no electrolytic lifetime limit in (b)."
                                      if verdict_b and not verdict_b["m5_wins_clearly"] else
                                      "m = 5 wins case (b) on cost - see verdict_case_b"))
    res["summary"] = dict(
        H10_corrected_IM_crossfade=dict(envelope_factor_model=flat["envelope_factor"], Px_W=flat["Px_max_W"],
                                        C_req_mF_5pct=c_req(flat["Px_max_W"], f, 0.05) * 1e3, C_req_mF_10pct=c_req(flat["Px_max_W"], f, 0.10) * 1e3),
        H11s_meets_target=main_ok, cost_verdict=res["cost_table"]["verdict"])
    json.dump(res, open(OUT, "w"), indent=1, default=MS.fmt)
    print(json.dumps(res["summary"], indent=1, default=MS.fmt))
    print(json.dumps(dict(m5_extra=m5, verdict_b=verdict_b), indent=1, default=MS.fmt))
    for k, v in cases.get("b_H03s_continuous_excitation", {}).items():
        for frac in ("5pct", "10pct"):
            print(k, frac, round(v[frac]["C_required_mF"], 2), {kk: (b["n"], round(b["stack_EUR"]), round(b["stack_vol_L"], 2), round(b.get("life_h") or 0))
                                                                 for kk, b in v[frac]["banks"].items()})
    for d_, tab0 in pb.items():
        if not isinstance(tab0, dict):
            continue
        for pr_, tab in tab0.items():
            for mode, r in tab.items():
                if not isinstance(r, dict):
                    continue
                print(d_, pr_, mode, {k: (round(v["fundamental_ratio"], 4), v["voltage_admissible"], v["UMP_orders_p_pm_1"], list(v["new_harmonics_rel"])[:6])
                                 for k, v in r.items() if isinstance(v, dict)})


if __name__ == "__main__":
    main()

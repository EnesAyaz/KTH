"""T08 - SPB module count N x module phase number m x slot count Q x pole-pair sets (D05, D06).
Value screens for the gap loop: H01 (zero-hardware pole changing), H02 (system kVA/loss), H04 (m > 3), H05 (cell parking).

Run from repo root:
  python 02_analytics/module_count_sweep.py            # everything
  python 02_analytics/module_count_sweep.py --only H01 # feasibility + screen_H01.json only (fast)
Outputs (02_analytics/results/):
  module_count_sweep.json (master), screen_H01.json, screen_H02.json, screen_H04.json, screen_H05.json
Assumptions: 02_analytics/assumptions.md, section T08.

Model
-----
Stator: Q coils (double layer, coil k in slot k, pitch y). N modules in series on the 1200 V link, each an
m-leg bridge with an isolated neutral (m = 3, 5, 6, 7, 9). Legs L = m N, each leg drives c = Q/L coils in series
(fixed wiring, coil polarity +/-1). Electronic mode p: coil k gets electrical angle p 2 pi k / Q.
A mode is available with ZERO extra hardware iff, with the same wiring:
  (i) all leg phasors have equal magnitude (equal module power),
  (ii) in every module the unit leg phasors sum to zero (isolated neutral, no zero-sequence current),
  (iii) [constant module power, needed by the series DC stack] their squares also sum to zero.
"""
from __future__ import annotations

import copy
import csv
import datetime as _dt
import importlib.util
import itertools
import json
import math
import os
import sys
from functools import lru_cache

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KTH = os.path.dirname(ROOT)
sys.path.insert(0, HERE)
os.environ.setdefault("SPB_P_RATED_KW", "300")
import torque_speed_envelope as T3  # noqa: E402
import fair_baselines as FB         # noqa: E402
import drivetrain_losses as DL      # noqa: E402

GAN_DIR = os.path.join(KTH, "Analytical Loss Calculations - GaN")
_spec = importlib.util.spec_from_file_location("epc2361_loss", os.path.join(GAN_DIR, "epc2361_loss.py"))
EPC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(EPC)
DEVICE_CSV = os.path.join(KTH, "PCB-Design", "reports", "paper", "icpe", "GaN_device_voltage_class_comparison_data.csv")
RES = os.path.join(ROOT, "02_analytics", "results")
OUT = {k: os.path.join(RES, f) for k, f in (("master", "module_count_sweep.json"), ("H01", "screen_H01.json"),
                                             ("H02", "screen_H02.json"), ("H04", "screen_H04.json"), ("H05", "screen_H05.json"))}

V_DC = T3.INV["V_dc_V"]
N_LIST = [2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24]
M_LIST = [3, 5, 6, 7, 9]
Q_LIST = [24, 30, 36, 40, 42, 45, 48, 54, 56, 60, 63, 70, 72, 80, 84, 90, 96, 105, 108, 112, 120, 126, 135, 144]
Q_PRACTICAL = (36, 96)          # slot pitch 28.8 .. 10.8 mm at the 330 mm bore
P_MAX = 8                       # 2p <= 16
RPM = T3.RPM
GEAR_VARIANT = "EU2017"         # leader: EU 2017/2400 regulatory baseline in the screens (certified_like also reported)


# ----------------------------------------------------------------------------------
# 1. Feasibility engine
# ----------------------------------------------------------------------------------
def leg_families(Q, L):
    c = Q // L
    fam = {"spaced": [[l + i * L for i in range(c)] for l in range(L)],
           "contiguous": [[l * c + i for i in range(c)] for l in range(L)]}
    return fam


def sign_patterns(c):
    if c == 1:
        return [(1,)]
    if c <= 4:
        return [(1,) + t for t in itertools.product((1, -1), repeat=c - 1)]
    return [tuple([1] * c), tuple((-1) ** i for i in range(c))]


def module_partitions(L, N, m):
    return {"interleaved": [[j + t * N for t in range(m)] for j in range(N)],
            "block": [[j * m + t for t in range(m)] for j in range(N)]}


def leg_phasor(legs, signs, Q, p):
    k = np.array(legs)                         # L x c
    s = np.array(signs)[None, :]
    return np.sum(s * np.exp(1j * p * 2 * np.pi * k / Q), axis=1)


def mode_ok(P, modules, tol=1e-6):
    """Return (balanced, constant_power) for leg phasors P under a module partition."""
    mag = np.abs(P)
    if mag.min() < 1e-9 or (mag.max() - mag.min()) > tol * mag.max():
        return False, False
    U = P / mag
    M = np.array(modules)
    s1 = np.abs(U[M].sum(axis=1)).max()
    s2 = np.abs((U[M] ** 2).sum(axis=1)).max()
    return bool(s1 < 1e-6), bool(s1 < 1e-6 and s2 < 1e-6)


def exact_match3(P_modes):
    """m = 3 only: any partition of legs into balanced triples, all modes at once (signature classes, memoised)."""
    mags = np.abs(P_modes)
    if mags.min() < 1e-9 or np.any(mags.max(axis=0) - mags.min(axis=0) > 1e-6 * mags.max(axis=0)):
        return None
    deg = np.round(np.degrees(np.angle(P_modes)) % 360.0, 3) % 360.0
    sig = [tuple(float(x) for x in r) for r in deg]
    classes = {}
    for li, sg in enumerate(sig):
        classes.setdefault(sg, []).append(li)
    keys = sorted(classes)
    idx = {k: i for i, k in enumerate(keys)}
    nm = P_modes.shape[1]
    part = []
    for sg in keys:
        lst = []
        for sgn in itertools.product((1, -1), repeat=nm):
            b = tuple(round((a + 120.0 * s_) % 360.0, 3) % 360.0 for a, s_ in zip(sg, sgn))
            c = tuple(round((a - 120.0 * s_) % 360.0, 3) % 360.0 for a, s_ in zip(sg, sgn))
            if b in idx and c in idx:
                lst.append((idx[b], idx[c]))
        part.append(lst)

    @lru_cache(maxsize=None)
    def solve(counts):
        if sum(counts) == 0:
            return ()
        a = next(i for i, c in enumerate(counts) if c)
        for b, c in part[a]:
            cl = list(counts)
            cl[a] -= 1
            if cl[b] <= 0:
                continue
            cl[b] -= 1
            if cl[c] <= 0:
                continue
            cl[c] -= 1
            r = solve(tuple(cl))
            if r is not None:
                return ((a, b, c),) + r
        return None
    sol = solve(tuple(len(classes[k]) for k in keys))
    if sol is None:
        return None
    pools = {i: list(classes[k]) for i, k in enumerate(keys)}
    return [[pools[a].pop(), pools[b].pop(), pools[c].pop()] for a, b, c in sol]


def pitch_factor(p, y, Q):
    return abs(math.sin(p * y * math.pi / Q))


def best_pitch(Q, p_hi, p_lo):
    best = None
    for y in range(1, max(2, Q // (2 * p_lo) + 1)):
        sc = pitch_factor(p_hi, y, Q) ** 2 + pitch_factor(p_lo, y, Q) ** 2
        if best is None or sc > best[0] + 1e-12:
            best = (sc, y)
    return best[1]


def grouped_mmf(legs, signs, Q, y, p):
    """Numerical winding factor and differential-leakage coefficient of the grouped winding in mode p."""
    P = leg_phasor(legs, signs, Q, p)
    ang = np.angle(P)
    Islot = np.zeros(Q)
    for li, coils in enumerate(legs):
        for k, s in zip(coils, signs):
            i = s * math.cos(ang[li])
            Islot[k % Q] += i
            Islot[(k + y) % Q] -= i
    nth = 4096
    pos = ((np.arange(Q) + 0.5) / Q * nth).astype(int)
    dF = np.zeros(nth)
    dF[pos] = Islot
    F = np.cumsum(dF)
    F -= F.mean()
    cF = np.abs(np.fft.rfft(F)) / nth * 2
    kw = cF[p] * math.pi * p / Q
    cF[p] = 0.0
    cF[0] = 0.0
    sig = float(np.sum(cF[:400] ** 2) / cF_fund(kw, Q, p) ** 2)
    return float(kw), sig


def cF_fund(kw, Q, p):
    return kw * Q / (math.pi * p)


def rule_spaced_interleaved(Q, N, m, p):
    """Closed-form rule (derived): spaced wiring (coils m N slots apart, all +), interleaved modules.
    Mode p works with k_d = 1 iff c | p and m does not divide p/c; constant module power iff also m does not divide 2p/c."""
    c = Q // (m * N)
    if p % c:
        return False, False
    pp = p // c
    bal = pp % m != 0
    return bal, bal and (2 * pp) % m != 0


def screen_combo(N, m, Q):
    """All wirings x partitions for one (N, m, Q): feasible mode sets and per-mode distribution factors."""
    L = m * N
    if Q % L:
        return None
    c = Q // L
    pmax = min(P_MAX, Q // 6)
    wirings = []
    for fname, legs in leg_families(Q, L).items():
        for s in sign_patterns(c):
            P = {p: leg_phasor(legs, s, Q, p) for p in range(1, pmax + 1)}
            parts = module_partitions(L, N, m)
            for pname, modules in parts.items():
                modes = {}
                for p in range(1, pmax + 1):
                    bal, cp = mode_ok(P[p], modules)
                    if bal:
                        modes[p] = dict(kd=float(np.abs(P[p][0]) / c), const_power=cp,
                                        system_phases=len({round(float(np.degrees(np.angle(z))) % 360.0, 3) for z in P[p]}))
                if modes:
                    wirings.append(dict(family=fname, signs=list(s), partition=pname, legs=legs, modules=modules, modes=modes))
            if m == 3 and L <= 72:
                # exact triple matching for pairs of modes (catches partitions the two structured ones miss)
                for p1 in range(1, pmax + 1):
                    for p2 in range(1, p1):
                        tri = exact_match3(np.stack([P[p1], P[p2]], axis=1))
                        if tri is None:
                            continue
                        modes = {}
                        for p in (p1, p2):
                            bal, cp = mode_ok(P[p], tri)
                            modes[p] = dict(kd=float(np.abs(P[p][0]) / c), const_power=cp,
                                            system_phases=len({round(float(np.degrees(np.angle(z))) % 360.0, 3) for z in P[p]}))
                        wirings.append(dict(family=fname, signs=list(s), partition=f"matched_{p1}_{p2}", legs=legs,
                                            modules=tri, modes=modes))
    return dict(N=N, m=m, Q=Q, c=c, legs=L, wirings=wirings)


def pairs_from(combo):
    """Best wiring per (p_hi, p_lo); y chosen per pair; k_w = k_p k_d, MMF-checked."""
    best = {}
    for w in combo["wirings"]:
        ps = sorted(w["modes"])
        for p1, p2 in itertools.combinations(ps, 2):
            hi, lo = max(p1, p2), min(p1, p2)
            y = best_pitch(combo["Q"], hi, lo)
            kd_hi, kd_lo = w["modes"][hi]["kd"], w["modes"][lo]["kd"]
            kw = [pitch_factor(hi, y, combo["Q"]) * kd_hi, pitch_factor(lo, y, combo["Q"]) * kd_lo]
            cp = w["modes"][hi]["const_power"] and w["modes"][lo]["const_power"]
            score = (cp, kw[0] ** 2 + kw[1] ** 2)
            key = f"{2 * hi}/{2 * lo}"
            if key not in best or score > best[key]["_score"]:
                best[key] = dict(_score=score, p=[hi, lo], y_slots=y, kw=kw, kd=[kd_hi, kd_lo],
                                 kp=[pitch_factor(hi, y, combo["Q"]), pitch_factor(lo, y, combo["Q"])],
                                 const_power=cp, family=w["family"], signs=w["signs"], partition=w["partition"],
                                 system_phases=[w["modes"][hi]["system_phases"], w["modes"][lo]["system_phases"]],
                                 all_modes_same_wiring=sorted(w["modes"]), _w=w)
    for v in best.values():
        w = v.pop("_w")
        v.pop("_score")
        kwh, sdh = grouped_mmf(w["legs"], w["signs"], combo["Q"], v["y_slots"], v["p"][0])
        kwl, sdl = grouped_mmf(w["legs"], w["signs"], combo["Q"], v["y_slots"], v["p"][1])
        v["kw_mmf"] = [kwh, kwl]
        v["sigma_diff"] = [sdh, sdl]
        v["module_example_legs"] = w["modules"][0]
        v["module_example_coils"] = [w["legs"][i] for i in w["modules"][0]]
    return best


# ----------------------------------------------------------------------------------
# 2. Devices and inverter (Enes's EPC2361 model, reused; per-class parameters swapped)
# ----------------------------------------------------------------------------------
DERATING = 0.75
DERATING_PARK_MAX = 0.80        # H05: max V_module/V_class allowed when modules are parked
DEV_PREF = {100: "EPC2361", 200: "EPC2304", 350: "EPC2050", 650: "IGT65R025D2"}
I_REF_EPC2361 = 40.0


def load_devices():
    rows = {}
    with open(DEVICE_CSV) as f:
        for r in csv.DictReader(f):
            rows[r["Device"]] = dict(V_class=float(r["Voltage_class_V"]), Rds_typ_mohm=float(r["Rds_typ_25C_mOhm"]),
                                     Qoss_nC=float(r["Qoss_nC"]), Vtest=float(r["Vtest_V"]))
    return rows


DEVICES = load_devices()


def device_for(V_mod, derating=DERATING):
    for vc in sorted(DEV_PREF):
        if V_mod <= derating * vc + 1e-9:
            return DEV_PREF[vc], vc, True
    return DEV_PREF[650], 650, False


def loss_inputs(dev, V_mod, I_dev):
    d, ref = DEVICES[dev], DEVICES["EPC2361"]
    base = EPC.LossInputs()
    qoss = d["Qoss_nC"] * math.sqrt(V_mod / d["Vtest"])
    kq = qoss / (ref["Qoss_nC"] * math.sqrt(75.0 / ref["Vtest"]))
    kr = d["Rds_typ_mohm"] / ref["Rds_typ_mohm"]
    li = copy.copy(base)
    li.vbus, li.ac_rms = V_mod, I_dev
    li.rds25_mohm, li.rds_max_mohm = base.rds25_mohm * kr, base.rds_max_mohm * kr
    li.qoss_nc, li.qoss_voltage = qoss, V_mod
    li.eoss_uj = base.eoss_uj * kq * V_mod / 75.0
    for f in ("qg_nc", "qgd_nc", "qgs2_nc", "qgsth_nc", "qgs1_nc"):
        setattr(li, f, getattr(base, f) * kq)
    return li


def n_parallel(dev, I_leg_max):
    I_dev_max = I_REF_EPC2361 / math.sqrt(DEVICES[dev]["Rds_typ_mohm"] / DEVICES["EPC2361"]["Rds_typ_mohm"])
    return max(1, math.ceil(I_leg_max / I_dev_max - 1e-9)), I_dev_max


def leg_loss(dev, V_mod, I_leg, n_par):
    if I_leg <= 0:
        I_leg = 1e-3
    try:
        r = EPC.calculate(loss_inputs(dev, V_mod, I_leg / n_par))
    except ValueError as e:
        return dict(ok=False, error=str(e))
    return dict(ok=True, P_leg_W=n_par * r["total_loss"], Tj_C=r["junction_temperature"],
                parts_W={k: n_par * r[k] for k in ("conduction", "switching_overlap", "coss_eoss", "gate_drive",
                                                     "dead_time_reverse_conduction")})


def k_m(m):
    """Max fundamental phase-peak voltage / V_dc of an m-leg bridge with isolated neutral (symmetric)."""
    return 1.0 / (2.0 * math.cos(math.pi / (2 * m))) if m % 2 else 0.5


def inverter_design(N, m):
    V_mod = V_DC / N
    dev, vc, ok = device_for(V_mod)
    L = m * N
    V_leg = T3.INV["m_margin"] * k_m(m) * V_mod / math.sqrt(2)
    # equivalence to the 48-leg reference machine (same total VA): I_leg = I_eq * (48 VMAX)/(L V_leg)
    scale_I = 48 * T3.VMAX / (L * V_leg)
    I_max = T3.IMAX * scale_I
    n_par, I_dev_max = n_parallel(dev, I_max)
    return dict(N=N, m=m, V_module_V=V_mod, device=dev, V_class_V=vc, derating=V_mod / vc, within_derating=ok,
                legs=L, V_leg_rms_max_V=V_leg, I_leg_rms_max_A=I_max, I_scale_vs_48leg=scale_I,
                devices_parallel=n_par, I_device_max_A=I_dev_max, devices_total=2 * L * n_par,
                converter_kVA=L * V_leg * I_max / 1e3, installed_semiconductor_kVA=2 * L * n_par * vc * I_dev_max / 1e3)


def inverter_loss(inv, I_eq, n_active=None, V_mod=None, legs=None):
    """Total inverter loss for an operating point given in 48-leg-equivalent current I_eq."""
    I_leg = I_eq * inv["I_scale_vs_48leg"]
    n = n_active or inv["devices_parallel"]
    L = legs or inv["legs"]
    r = leg_loss(inv["device"], V_mod or inv["V_module_V"], I_leg * inv["legs"] / L, n)
    return (L * r["P_leg_W"], r) if r["ok"] else (None, r)


# ----------------------------------------------------------------------------------
# 3. Pole-changing IM (T03b approach) for a winding (48-leg equivalent)
# ----------------------------------------------------------------------------------
KW_REF = abs(math.sin(4 * 7 * math.pi / 48))


def pc_im_designs(Q, pr):
    p_hi, p_lo = pr["p"]
    N_leg = T3.ST["N_c"] * KW_REF / pr["kw"][0]
    out = {}
    for p, kw, sd in ((p_hi, pr["kw"][0], pr["sigma_diff"][0]), (p_lo, pr["kw"][1], pr["sigma_diff"][1])):
        d = FB.make_design(p, Q, pr["y_slots"], Q / 48.0, T3.ST["R_gap_m"], float("nan"), N_leg, name=f"2p{2 * p}",
                           h_y=T3.ST["yoke_h_m"])
        r = kw / pitch_factor(p, pr["y_slots"], Q)
        Lm0 = d["Lm_H"]
        d["Lm_H"] *= r ** 2
        d["k_w"] = kw
        for k in ("psi_rms_per_T", "psi_cap_rms_Wb"):
            d[k] *= r
        for k in ("R_r_ohm", "R_r_bar_ohm", "R_r_ring_ohm", "L_sigma_r_H"):
            d[k] *= r ** 2
        kc = T3.ST["kc_ksat"] / 1.05
        d["L_sigma_s_H"] += (sd * r ** 2 - d["sigma_diff"]) * Lm0 * kc
        d["sigma_diff"] = sd
        out[f"2p{2 * p}"] = d
    return out


def pc_im_eval(designs, inv=None, points=(("cruise_85kmh_flat", 85.0, 0.0), ("cruise_60kmh_flat", 60.0, 0.0))):
    NG = FB.NG_FULL
    keys = list(designs)
    T = {k: FB.envelope(designs[k], NG) for k in keys}
    Tc = np.maximum(T[keys[0]], T[keys[1]])
    m = FB.metrics(Tc, NG, FB.G_REF)
    TN = {k: T3.INV["P_rated_W"] / (FB.metrics(T[k], NG, FB.G_REF)["n_base_rpm"] * RPM) for k in keys}
    case = dict(kind="IM", designs=designs, T_N=TN, rotor=DL.rotor_from_design(T3.ST["R_gap_m"]), G=FB.G_REF,
                topo=("single", None))
    res = dict(T_peak_Nm=m["T_peak_Nm"], max_start_grade_pct=m["max_start_grade_pct"], CPSR=m["CPSR"],
               CPSR_capped=m["CPSR_capped_by_eval_range"], P_at_90kmh_kW=m["P_at_vmax_W"] / 1e3,
               T_peak_per_converter_kVA_Nm=m["T_peak_Nm"] / (inv["converter_kVA"] if inv else 1.0),
               crossover_speed_rpm=T3.crossover(T[keys[0]], T[keys[1]]), points={})
    for name, v, gr in points:
        out = {}
        for gv in (GEAR_VARIANT, "certified_like"):
            ds = DL.GEAR["drag_scale_variants"][gv]
            r = DL.evaluate(case, v, gr, ds)
            if not r or not r.get("feasible"):
                out[gv] = None
                continue
            P_in = r["wheel_power_W"] / r["eta_drivetrain_wheel_over_elec"]
            Pinv = inverter_loss(inv, r["I_rms_A"])[0] if inv else None
            out[gv] = dict(mode=r["mode"], n_motor_rpm=r["n_motor_rpm"], T_motor_Nm=r["T_motor_Nm"], I_eq_rms_A=r["I_rms_A"],
                           PF=r["PF"], P_wheel_W=r["wheel_power_W"], P_em_W=r["P_em_loss_W"], P_fw_W=r["P_mech_W"], P_gear_W=r["P_gear_W"],
                           P_inverter_W=Pinv, eta_machine_gear=r["eta_drivetrain_wheel_over_elec"],
                           P_system_loss_W=(P_in - r["wheel_power_W"]) + (Pinv or 0.0),
                           eta_dc_to_wheel=r["wheel_power_W"] / (P_in + Pinv) if Pinv is not None else None)
        res["points"][name] = out
    if inv:
        Pst, rst = inverter_loss(inv, T3.IMAX)
        res["start_inverter_loss_W"] = Pst
        res["start_inverter_Tj_C"] = rst.get("Tj_C")
    return res, case


# ----------------------------------------------------------------------------------
# 4. Fixed-pole SPB baseline with the same N (T03b fixed 2p=4, m = 3)
# ----------------------------------------------------------------------------------
def fixed_baseline_eval(inv_same, fb):
    out = {}
    for key, Gk in (("fixed_2p4_freeGear", None), ("fixed_2p4_G9.80_scaled_inverter", FB.G_REF)):
        d = fb["machines"]["fixed_2p4"]["design"]
        G = fb["machines"]["fixed_2p4"]["metrics"]["gear_ratio"] if Gk is None else Gk
        case = dict(kind="IM", designs={"2p4": d}, T_N={"2p4": fb["machines"]["fixed_2p4"]["realistic_losses"]["T_N_Nm"]},
                    rotor=DL.rotor_from_design(d["R_gap_m"]), G=G, topo=("single", None))
        inv = dict(inv_same)
        if Gk is not None:     # inverter scaled to meet the 12 % start at G = 9.80
            k = fb["machines"]["fixed_2p4"]["at_G_9p80"]["current_factor_needed_for_start"]
            inv["I_leg_rms_max_A"] *= k
            inv["devices_parallel"] = n_parallel(inv["device"], inv["I_leg_rms_max_A"])[0]
            inv["devices_total"] = 2 * inv["legs"] * inv["devices_parallel"]
            inv["converter_kVA"] *= k
            inv["current_factor_for_start"] = k
        pts = {}
        for name, v, gr in (("cruise_85kmh_flat", 85.0, 0.0), ("cruise_60kmh_flat", 60.0, 0.0)):
            r = DL.evaluate(case, v, gr, DL.GEAR["drag_scale_variants"][GEAR_VARIANT])
            if not r or not r.get("feasible"):
                pts[name] = None
                continue
            P_in = r["wheel_power_W"] / r["eta_drivetrain_wheel_over_elec"]
            Pinv = inverter_loss(inv, r["I_rms_A"])[0]
            pts[name] = dict(n_motor_rpm=r["n_motor_rpm"], I_eq_rms_A=r["I_rms_A"], P_em_W=r["P_em_loss_W"], P_fw_W=r["P_mech_W"],
                             P_gear_W=r["P_gear_W"], P_inverter_W=Pinv, P_system_loss_W=(P_in - r["wheel_power_W"]) + (Pinv or 0),
                             eta_dc_to_wheel=r["wheel_power_W"] / (P_in + Pinv) if Pinv else None)
        Pst = inverter_loss(inv, T3.IMAX * inv.get("current_factor_for_start", 1.0))[0]
        out[key] = dict(gear_ratio=G, inverter={k: inv[k] for k in ("device", "devices_parallel", "devices_total", "converter_kVA")},
                        start_inverter_loss_W=Pst, points=pts)
    return out


# ----------------------------------------------------------------------------------
# 5. H05: cell parking
# ----------------------------------------------------------------------------------
def h05_screen(inv, designs, case):
    out = dict(note="SPB modules are in series on the 1200 V link: parking k modules raises the others to 1200/(N-k). "
                    "The limit is the device rating (<= 0.80 V_class), not the machine voltage. Parked coil groups carry no "
                    "current, so the active ones carry N/(N-k) more current for the same torque (stator copper x N/(N-k)). "
                    "Alternative: shed parallel devices inside each switch position (no voltage penalty).",
               N=inv["N"], m=inv["m"], V_class_V=inv["V_class_V"])
    N = inv["N"]
    k_max = max(0, N - math.ceil(V_DC / (DERATING_PARK_MAX * inv["V_class_V"]) - 1e-9))
    out["k_max_parked_modules_by_device_rating"] = k_max
    pts = {}
    for name, v, gr in (("cruise_85kmh_flat", 85.0, 0.0), ("cruise_60kmh_flat", 60.0, 0.0)):
        per_mode = {}
        for mode, d in designs.items():
            single = dict(case, designs={mode: d}, T_N={mode: case["T_N"][mode]})
            r = DL.evaluate(single, v, gr, DL.GEAR["drag_scale_variants"][GEAR_VARIANT])
            if not r or not r.get("feasible"):
                per_mode[mode] = None
                continue
            I_eq = r["I_rms_A"]
            P_all, _ = inverter_loss(inv, I_eq)
            Pcu = r["em_parts_W"]["P_cu_stator_W"]
            series = []
            for k in range(0, k_max + 1):
                Vp = V_DC / (N - k)
                P_k, rr = inverter_loss(inv, I_eq, V_mod=Vp, legs=inv["m"] * (N - k))
                series.append(dict(k_parked=k, V_module_V=Vp, P_inverter_W=P_k, dP_stator_cu_W=Pcu * (N / (N - k) - 1),
                                   dP_total_vs_all_active_W=None if P_k is None or P_all is None else (P_k - P_all) + Pcu * (N / (N - k) - 1)))
            shed = []
            for n_a in range(1, inv["devices_parallel"] + 1):
                P_s, rr = inverter_loss(inv, I_eq, n_active=n_a)
                shed.append(dict(devices_active=n_a, P_inverter_W=P_s, Tj_C=rr.get("Tj_C")))
            valid = [s for s in shed if s["P_inverter_W"] is not None]
            best = min(valid, key=lambda s: s["P_inverter_W"]) if valid else None
            per_mode[mode] = dict(I_eq_rms_A=I_eq, V_needed_fraction=None, P_inverter_all_active_W=P_all,
                                  series_module_parking=series, parallel_device_shedding=dict(best=best, sweep=shed))
        pts[name] = per_mode
    out["points"] = pts
    return out


# ----------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------
def fmt(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    today = _dt.date.today().isoformat()
    meta = dict(script="02_analytics/module_count_sweep.py", task="T08 (+ gap-loop screens H01/H02/H04/H05)", date=today,
                P_rated_W=T3.INV["P_rated_W"], V_dc_V=V_DC, assumptions="02_analytics/assumptions.md#t08",
                gear_variant_in_screens=GEAR_VARIANT)
    # ---- H01 feasibility
    table, rule_check = {}, dict(agree=0, disagree=[])
    combos = {}
    for N in N_LIST:
        for m in M_LIST:
            for Q in Q_LIST:
                if Q % (m * N) or Q < 2 * m:
                    continue
                cb = screen_combo(N, m, Q)
                if cb is None:
                    continue
                prs = pairs_from(cb)
                combos[(N, m, Q)] = (cb, prs)
                # rule check (spaced, all +, interleaved)
                for w in cb["wirings"]:
                    if w["family"] == "spaced" and w["partition"] == "interleaved" and all(s == 1 for s in w["signs"]):
                        for p in range(1, min(P_MAX, Q // 6) + 1):
                            pred = rule_spaced_interleaved(Q, N, m, p)
                            got = (p in w["modes"] and w["modes"][p]["kd"] > 1 - 1e-9,
                                   p in w["modes"] and w["modes"][p]["const_power"] and w["modes"][p]["kd"] > 1 - 1e-9)
                            if pred == got:
                                rule_check["agree"] += 1
                            else:
                                rule_check["disagree"].append([N, m, Q, p, list(pred), list(got)])
                states = sorted({p for w in cb["wirings"] for p in w["modes"]})
                table[f"N{N}_m{m}_Q{Q}"] = dict(N=N, m=m, Q=Q, coils_per_leg=Q // (m * N), Q_practical=Q_PRACTICAL[0] <= Q <= Q_PRACTICAL[1],
                                                modes_any_wiring_2p=[2 * p for p in states],
                                                pole_phase_states_best_wiring=max(([2 * p for p in sorted(w["modes"])] for w in cb["wirings"]), key=len, default=[]),
                                                pairs={k: {kk: vv for kk, vv in v.items()} for k, v in prs.items()})
        print("N", N, "combos", sum(1 for k in combos if k[0] == N))

    def design_rank(item):
        key, pr, N, m, Q = item
        ratio = pr["p"][0] / pr["p"][1]
        return (pr["const_power"], Q_PRACTICAL[0] <= Q <= Q_PRACTICAL[1], abs(ratio - 2) < 1e-9,
                pr["kw"][0] ** 2 + pr["kw"][1] ** 2)
    cands = []
    for (N, m, Q), (cb, prs) in combos.items():
        for key, pr in prs.items():
            if pr["p"][0] in (2, 3, 4, 6) and pr["p"][0] / pr["p"][1] in (2.0, 3.0, 1.5):
                cands.append((key, pr, N, m, Q))
    cands.sort(key=design_rank, reverse=True)
    best_per_m = {}
    for c in cands:
        best_per_m.setdefault(c[3], c)
    best_per_N = {}
    for c in cands:
        if c[1]["p"] == [4, 2] or True:
            best_per_N.setdefault(c[2], c)
    top = []
    seen = set()
    for c in cands:
        sig = (c[2], c[3], c[0])
        if sig in seen:
            continue
        seen.add(sig)
        top.append(c)
        if len(top) >= 12:
            break

    def pack(c):
        key, pr, N, m, Q = c
        return dict(N=N, m=m, Q=Q, pair_2p=key, **{k: v for k, v in pr.items()})
    rule_txt = ("Zero-extra-hardware rule (proved for spaced wiring + interleaved modules, checked against the enumeration): "
                "with c = Q/(m N) coils per leg, coils of a leg m N slots apart and module j = legs {j + tN}, mode p is available "
                "with k_d = 1 iff c | p and m does not divide p/c; module power is constant (no 2nd-harmonic DC ripple in the "
                "series stack) iff also m does not divide 2p/c. A pole pair (p1, p2) works iff both satisfy it with the same wiring. "
                "Winding factor = pitch factor sin(p y pi/Q) x k_d. Other wirings (contiguous belts, matched triples) add modes "
                "with k_d < 1. Example: N = 16, m = 3, Q = 48 (c = 1): every p not divisible by 3 -> 8/4, 4/2, 16/8 yes; 6/x no.")
    h01 = dict(meta=dict(meta, screen="H01", metric="feasible (N, m, Q, p1/p2) table + winding factors per mode"),
               rule=rule_txt, rule_check=rule_check,
               best_designs=[pack(c) for c in top], best_per_m={str(k): pack(v) for k, v in best_per_m.items()},
               best_per_N={str(k): pack(v) for k, v in sorted(best_per_N.items())},
               feasible_table=table)
    os.makedirs(RES, exist_ok=True)
    json.dump(h01, open(OUT["H01"], "w"), indent=1, default=fmt)
    print("H01 written:", len(table), "combos; rule check agree", rule_check["agree"], "disagree", len(rule_check["disagree"]))
    for c in top[:8]:
        print("  top", c[2], c[3], c[4], c[0], [round(x, 3) for x in c[1]["kw"]], c[1]["const_power"], c[1]["family"], c[1]["partition"])
    if only == "H01":
        return

    # ---- inverter per N (m = 3) and pole-changing IM per N (master), H02/H04/H05
    fb = json.load(open(FB.OUT_JSON))
    master = dict(meta=dict(meta, inputs=["fair_baselines.json (T03b)", "drivetrain_losses.py (T03d; EU2017 + certified_like gear)",
                                         "epc2361_loss.py (Enes)", "GaN_device_voltage_class_comparison_data.csv (Enes)"]),
                  rule=rule_txt, per_N={}, per_N_m={})
    evals = {}

    def run_design(N, m, Q, pr):
        inv = inverter_design(N, m)
        des = pc_im_designs(Q, pr)
        ev, case = pc_im_eval(des, inv)
        return inv, des, ev, case
    for N in N_LIST:
        inv3 = inverter_design(N, 3)
        cand = [c for c in cands if c[2] == N and c[3] == 3 and c[0] == "8/4"] or [c for c in cands if c[2] == N and c[3] == 3]
        entry = dict(inverter_m3=inv3)
        if cand:
            key, pr, _, m, Q = cand[0]
            inv, des, ev, case = run_design(N, 3, Q, pr)
            evals[(N, 3)] = (inv, des, ev, case, key, Q, pr)
            entry["pole_changing_IM_m3"] = dict(pair_2p=key, Q=Q, winding={k: v for k, v in pr.items()}, **ev)
            entry["fixed_pole_baseline_same_N"] = fixed_baseline_eval(inv, fb)
        master["per_N"][str(N)] = entry
        e = entry.get("pole_changing_IM_m3")
        if e:
            c85 = e["points"]["cruise_85kmh_flat"][GEAR_VARIANT]
            print(f"N={N:2d} {inv3['device']:12s} npar={inv3['devices_parallel']:3d} dev={inv3['devices_total']:5d} pair {e['pair_2p']} Q{e['Q']} "
                  f"kw {[round(x, 3) for x in e['winding']['kw']]} T={e['T_peak_Nm']:.0f} grade={e['max_start_grade_pct']:.1f} CPSR={e['CPSR']:.2f} "
                  f"eta_dc_wheel={c85['eta_dc_to_wheel'] if c85 else None} Pinv={c85['P_inverter_W'] if c85 else None}")
    # m > 3: best design per m (H04) at the N of that design, plus N = 16 if available
    for m in M_LIST:
        sel = [c for c in cands if c[3] == m]
        picks = sel[:1] + [c for c in sel if c[2] == 16][:1]
        for c in picks:
            key, pr, N, m_, Q = c
            if (N, m) in evals and evals[(N, m)][4] == key:
                continue
            inv, des, ev, case = run_design(N, m, Q, pr)
            evals[(N, m)] = (inv, des, ev, case, key, Q, pr)
            master["per_N_m"][f"N{N}_m{m}"] = dict(inverter=inv, pole_changing_IM=dict(pair_2p=key, Q=Q, winding={k: v for k, v in pr.items()}, **ev))
            print(f"  m={m} N={N} Q={Q} {key} kw {[round(x, 3) for x in pr['kw']]} T={ev['T_peak_Nm']:.0f} CPSR={ev['CPSR']:.2f}")
    json.dump(master, open(OUT["master"], "w"), indent=1, default=fmt)

    # ---- H02
    h02 = dict(meta=dict(meta, screen="H02", metric="inverter kVA, device count, inverter loss (cruise, start), system loss at cruise vs fixed-pole SPB same N"),
               literature_comparison=dict(Raj2022=dict(pole_changing_inverter_kW=37, fixed_pole_inverter_kW=56, ratio=56 / 37,
                                                       note="pole-changing IM vs fixed-pole IM over the same torque-speed map"),
                                          this_work_kVA_ratio_fixed_over_PC_at_same_gear=fb["machines"]["fixed_2p4"]["at_G_9p80"]["current_factor_needed_for_start"],
                                          note="This work: fixed 2p=4 at G = 9.80 needs x1.74 the inverter current (kVA) of the PC IM for the 12 % start; "
                                               "Raj2022 ratio 1.51. With a free gear ratio the fixed IM needs the same kVA (T03b)."),
               device_area="not computed: package/die areas are not in the local data (request: EPC2361/EPC2304/EPC2050/IGT65R025D2 package areas)",
               designs={})
    for (N, m), (inv, des, ev, case, key, Q, pr) in sorted(evals.items()):
        base = master["per_N"].get(str(N), {}).get("fixed_pole_baseline_same_N") if m == 3 else None
        h02["designs"][f"N{N}_m{m}_Q{Q}_{key}"] = dict(inverter=inv, start_inverter_loss_W=ev.get("start_inverter_loss_W"),
                                                     start_Tj_C=ev.get("start_inverter_Tj_C"),
                                                     cruise=ev["points"], T_peak_Nm=ev["T_peak_Nm"], max_start_grade_pct=ev["max_start_grade_pct"],
                                                     fixed_pole_baseline_same_N=base)
    json.dump(h02, open(OUT["H02"], "w"), indent=1, default=fmt)
    print("H02 written")

    # ---- H04
    h04 = dict(meta=dict(meta, screen="H04", metric="torque per A (per converter kVA) and part-load efficiency vs m"),
               note="All m share the same total converter kVA (equivalence), so T_peak per kVA compares torque per ampere-turn across m. "
                    "Per-leg current scales as 1/(m k_m). Module voltage utilisation k_m: m=3 0.577, 5 0.526, 6 0.5, 7 0.513, 9 0.508.",
               per_m={})
    for (N, m), (inv, des, ev, case, key, Q, pr) in sorted(evals.items(), key=lambda x: (x[0][1], x[0][0])):
        h04["per_m"].setdefault(str(m), []).append(dict(N=N, Q=Q, pair_2p=key, kw=pr["kw"], sigma_diff=pr["sigma_diff"],
                                                      pole_phase_states=table.get(f"N{N}_m{m}_Q{Q}", {}).get("pole_phase_states_best_wiring"),
                                                      k_m=k_m(m), I_leg_max_A=inv["I_leg_rms_max_A"], T_peak_Nm=ev["T_peak_Nm"],
                                                      T_peak_per_converter_kVA=ev["T_peak_per_converter_kVA_Nm"],
                                                      max_start_grade_pct=ev["max_start_grade_pct"], CPSR=ev["CPSR"],
                                                      part_load=ev["points"]))
    json.dump(h04, open(OUT["H04"], "w"), indent=1, default=fmt)
    print("H04 written")

    # ---- H05 (reference N = 16, m = 3 and the best m = 3 design of each N in {8, 12, 24})
    h05 = dict(meta=dict(meta, screen="H05", metric="inverter (+ machine copper) loss at cruise, cells parked vs all active, per pole mode"),
               cases={})
    for N in (16, 8, 12, 24):
        if (N, 3) in evals:
            inv, des, ev, case, key, Q, pr = evals[(N, 3)]
            h05["cases"][f"N{N}_m3_Q{Q}_{key}"] = h05_screen(inv, des, case)
    json.dump(h05, open(OUT["H05"], "w"), indent=1, default=fmt)
    print("H05 written")


if __name__ == "__main__":
    main()

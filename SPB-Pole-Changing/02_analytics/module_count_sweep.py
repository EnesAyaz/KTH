"""T08 - SPB module-count sweep (D05: N free, N = 16 reference).

Run from repo root:  python 02_analytics/module_count_sweep.py
Output: 02_analytics/results/module_count_sweep.json
Assumptions: 02_analytics/assumptions.md, section T08.

Per N (2..24):
  1. Electronic pole-pair modes the coil groups can form, for practical slot counts Q (3N | Q):
     legs = 3N, each leg drives c = Q/(3N) coils in series (fixed wiring, coil polarity +/-1 allowed);
     module = 3 legs with an isolated neutral -> the three leg phasors must be balanced (sum 0, equal
     magnitude) in EVERY mode with the same wiring. Searched numerically (grouping families x signs x
     module matching); winding factor per mode = pitch factor x group distribution factor (MMF-checked).
  2. Module voltage 1200/N, device class (EPC/Infineon GaN set from Enes's ICPE comparison CSV),
     paralleling, inverter loss from Enes's EPC2361 model (calculate(), reused, device parameters swapped).
  3. Pole-changing IM (T03b approach, 300 kW): start grade, CPSR, P at 90 km/h, cruise efficiency
     (realistic IM losses + T03d friction/windage + certified-like single-stage gear) and inverter
     efficiency at cruise and rated.
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
OUT_JSON = os.path.join(ROOT, "02_analytics", "results", "module_count_sweep.json")

V_DC = T3.INV["V_dc_V"]
N_LIST = [2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24]
Q_LIST = [24, 36, 48, 54, 60, 72, 96, 144]
Q_PRACTICAL = (36, 96)                   # slot pitch 28.8 .. 10.8 mm at the 330 mm bore
PAIRS_2P = [(8, 4), (4, 2), (12, 6), (16, 8), (6, 2), (12, 4), (6, 4), (12, 8)]
RPM = T3.RPM


# ----------------------------------------------------------------------------------
# 1. Coil-group / module feasibility
# ----------------------------------------------------------------------------------
def best_pitch(Q, p_hi, p_lo):
    best = None
    for y in range(1, Q // (2 * p_lo) + 1):
        kh, kl = abs(math.sin(p_hi * y * math.pi / Q)), abs(math.sin(p_lo * y * math.pi / Q))
        sc = kh ** 2 + kl ** 2
        if best is None or sc > best[0] + 1e-12:
            best = (sc, y, kh, kl)
    return best[1], best[2], best[3]


def leg_families(Q, N):
    L, c = 3 * N, Q // (3 * N)
    fam = {"spaced": [[l + i * L for i in range(c)] for l in range(L)],
           "contiguous": [[l * c + i for i in range(c)] for l in range(L)]}
    if c > 1 and c % 2 == 0:   # pairs of spaced blocks (half-contiguous) - a third topology
        h = c // 2
        fam["paired"] = [[(l * 2 + j) % (2 * L) + i * 2 * L for i in range(h) for j in (0,)] +
                         [(l * 2 + 1) % (2 * L) + i * 2 * L for i in range(h)] for l in range(L)]
        if sorted(sum(fam["paired"], [])) != list(range(Q)):
            del fam["paired"]
    return fam


def leg_phasors(legs, Q, modes, signs):
    out = np.zeros((len(legs), len(modes)), complex)
    for li, coils in enumerate(legs):
        for k, s in zip(coils, signs):
            for mi, p in enumerate(modes):
                out[li, mi] += s * np.exp(1j * p * 2 * np.pi * k / Q)
    return out


def best_signs(legs, Q, modes):
    """Fixed coil polarities (same pattern for every leg) maximising the worst-mode distribution factor."""
    c = len(legs[0])
    best = None
    for tail in itertools.product((1, -1), repeat=c - 1):
        s = (1,) + tail
        P = leg_phasors(legs[:1], Q, modes, s)[0]
        kd = np.abs(P) / c
        score = (round(float(kd.min()), 9), round(float(kd.prod()), 9))
        if best is None or score > best[0]:
            best = (score, s)
    return best[1]


def match_modules(P, tol=1e-6):
    """Partition legs into balanced triples for all modes simultaneously (backtracking)."""
    n = P.shape[0]
    mag = np.abs(P)
    if np.any(mag.max(axis=0) - mag.min(axis=0) > tol * np.maximum(mag.max(axis=0), 1)):
        return None                                   # unequal leg magnitudes -> unequal module power
    if np.any(mag.min(axis=0) < 1e-9):
        return None
    U = P / mag
    free = set(range(n))
    triples = []
    cand = {}
    for a in range(n):
        lst = []
        for b in range(a + 1, n):
            for c_ in range(b + 1, n):
                if np.all(np.abs(U[a] + U[b] + U[c_]) < 1e-6):
                    lst.append((b, c_))
        cand[a] = lst

    def bt():
        if not free:
            return True
        a = min(free)
        for b, c_ in cand[a]:
            if b in free and c_ in free:
                free.difference_update((a, b, c_))
                triples.append((a, b, c_))
                if bt():
                    return True
                triples.pop()
                free.update((a, b, c_))
        return False
    return triples if bt() else None


def grouped_mmf_kw(legs, signs, Q, y, p, Nc=1.0):
    """Numerical fundamental winding factor and differential-leakage coefficient for the grouped winding."""
    P = leg_phasors(legs, Q, [p], signs)[:, 0]
    ang = np.angle(P)
    th = np.linspace(0, 2 * np.pi, 4096, endpoint=False)
    Islot = np.zeros(Q)
    for li, coils in enumerate(legs):
        for k, s in zip(coils, signs):
            i = s * math.cos(ang[li] if True else 0.0)
            Islot[k % Q] += Nc * i
            Islot[(k + y) % Q] -= Nc * i
    pos = 2 * np.pi * (np.arange(Q) + 0.5) / Q
    F = np.zeros_like(th)
    for sl in range(Q):
        F += Islot[sl] * (th >= pos[sl])
    F -= F.mean()
    cF = np.abs(np.fft.rfft(F)) / len(th) * 2
    kw = cF[p] * math.pi * p / (Q * Nc)
    cF[p] = 0.0
    cF[0] = 0.0
    sig = float(np.sum(cF[:300] ** 2) / (kw * Q * Nc / (math.pi * p)) ** 2)
    return float(kw), sig


def feasibility(N, Q, pair2p):
    p_hi, p_lo = pair2p[0] // 2, pair2p[1] // 2
    if Q % (3 * N):
        return None
    y, kp_hi, kp_lo = best_pitch(Q, p_hi, p_lo)
    best = None
    for fname, legs in leg_families(Q, N).items():
        s = best_signs(legs, Q, [p_hi, p_lo])
        P = leg_phasors(legs, Q, [p_hi, p_lo], s)
        tr = match_modules(P)
        if tr is None:
            continue
        c = len(legs[0])
        kd = np.abs(P[0]) / c
        kw_hi, sd_hi = grouped_mmf_kw(legs, s, Q, y, p_hi)
        kw_lo, sd_lo = grouped_mmf_kw(legs, s, Q, y, p_lo)
        rec = dict(family=fname, coils_per_leg=c, signs=list(s), y_slots=y,
                   kp=[kp_hi, kp_lo], kd=[float(kd[0]), float(kd[1])],
                   kw=[kp_hi * float(kd[0]), kp_lo * float(kd[1])], kw_mmf=[kw_hi, kw_lo],
                   sigma_diff=[sd_hi, sd_lo], module_example=[legs[i] for i in tr[0]])
        if best is None or sum(k * k for k in rec["kw"]) > sum(k * k for k in best["kw"]):
            best = rec
    return best


# ----------------------------------------------------------------------------------
# 2. Devices and inverter loss (Enes's EPC2361 model, parameters swapped per class)
# ----------------------------------------------------------------------------------
DERATING = 0.75          # V_module <= 0.75 V_class (reference: 75 V on the 100 V EPC2361)
DEV_PREF = {100: "EPC2361", 200: "EPC2304", 350: "EPC2050", 650: "IGT65R025D2"}  # lowest D-FoM / R per class in the CSV
I_REF_EPC2361 = 40.0     # A rms per device: Enes's model default operating point (one EPC2361 per position)


def load_devices():
    rows = {}
    with open(DEVICE_CSV) as f:
        for r in csv.DictReader(f):
            rows[r["Device"]] = dict(V_class=float(r["Voltage_class_V"]), Rds_typ_mohm=float(r["Rds_typ_25C_mOhm"]),
                                     Qoss_nC=float(r["Qoss_nC"]), Vtest=float(r["Vtest_V"]))
    return rows


DEVICES = load_devices()


def device_for(V_mod):
    for vc in sorted(DEV_PREF):
        if V_mod <= DERATING * vc + 1e-9:
            return DEV_PREF[vc], vc, True
    return DEV_PREF[650], 650, False   # no class in the set with the derating margin


def loss_inputs(dev, V_mod, I_dev):
    d = DEVICES[dev]
    ref = DEVICES["EPC2361"]
    base = EPC.LossInputs()
    qoss = d["Qoss_nC"] * math.sqrt(V_mod / d["Vtest"])                   # Q_oss ~ V^0.5 (Coss ~ V^-0.5)
    qoss_ref = ref["Qoss_nC"] * math.sqrt(75.0 / ref["Vtest"])
    kq = qoss / qoss_ref                                                  # gate charges scaled with Q_oss (assumption)
    kr = d["Rds_typ_mohm"] / ref["Rds_typ_mohm"]
    li = copy.replace(base) if hasattr(copy, "replace") else copy.copy(base)
    li.vbus = V_mod
    li.ac_rms = I_dev
    li.rds25_mohm = base.rds25_mohm * kr
    li.rds_max_mohm = base.rds_max_mohm * kr
    li.qoss_nc = qoss
    li.qoss_voltage = V_mod
    li.eoss_uj = base.eoss_uj * kq * V_mod / 75.0
    for f in ("qg_nc", "qgd_nc", "qgs2_nc", "qgsth_nc", "qgs1_nc"):
        setattr(li, f, getattr(base, f) * kq)
    return li


def n_parallel(dev, I_leg_max):
    r = DEVICES[dev]["Rds_typ_mohm"] / DEVICES["EPC2361"]["Rds_typ_mohm"]
    I_dev_max = I_REF_EPC2361 / math.sqrt(r)          # equal conduction loss per device as EPC2361 at 40 A
    return max(1, math.ceil(I_leg_max / I_dev_max - 1e-9)), I_dev_max


def leg_loss(dev, V_mod, I_leg, n_par):
    li = loss_inputs(dev, V_mod, I_leg / n_par)
    try:
        r = EPC.calculate(li)
    except ValueError as e:
        return dict(ok=False, error=str(e))
    return dict(ok=True, P_leg_W=n_par * r["total_loss"], Tj_C=r["junction_temperature"],
                parts_W={k: n_par * r[k] for k in ("conduction", "switching_overlap", "coss_eoss", "gate_drive",
                                                     "dead_time_reverse_conduction")},
                stress_V=V_mod + r["overshoot_voltage"])


# ----------------------------------------------------------------------------------
# 3. Pole-changing IM per N (T03b approach)
# ----------------------------------------------------------------------------------
def pc_im_designs(Q, y, kw_hi, kw_lo, sd_hi, sd_lo, pair2p):
    """T03 geometry (R = 165 mm, 25 mm yoke); Q-equivalent 48-leg model with the grouped winding factors.
    Turns set so N_leg*k_w in the high-pole mode equals the T03 machine (same EMF per volt)."""
    p_hi, p_lo = pair2p[0] // 2, pair2p[1] // 2
    kw_ref = abs(math.sin(4 * 7 * math.pi / 48))
    N_leg = T3.ST["N_c"] * kw_ref / kw_hi
    out = {}
    for p, kw, sd in ((p_hi, kw_hi, sd_hi), (p_lo, kw_lo, sd_lo)):
        d = FB.make_design(p, Q, y, Q / 48.0, T3.ST["R_gap_m"], float("nan"), N_leg, name=f"2p{2 * p}", h_y=T3.ST["yoke_h_m"])
        kp = abs(math.sin(p * y * math.pi / Q))
        r = kw / kp                                    # group distribution factor
        Lm_old = d["Lm_H"]
        for k in ("Lm_H",):
            d[k] *= r ** 2
        d["k_w"] = kw
        d["psi_rms_per_T"] *= r
        d["psi_cap_rms_Wb"] *= r
        d["R_r_ohm"] *= r ** 2
        d["R_r_bar_ohm"] *= r ** 2
        d["R_r_ring_ohm"] *= r ** 2
        d["L_sigma_r_H"] *= r ** 2
        d["L_sigma_s_H"] += (sd - d["sigma_diff"]) * Lm_old * r ** 2 * T3.ST["kc_ksat"] / 1.05 + d["sigma_diff"] * Lm_old * (r ** 2 - 1) * T3.ST["kc_ksat"] / 1.05
        d["sigma_diff"] = sd
        out[f"2p{2 * p}"] = d
    return out


def pc_im_eval(designs, pair2p, inv):
    NG = FB.NG_FULL
    keys = list(designs)
    T = {k: FB.envelope(designs[k], NG) for k in keys}
    Tc = np.maximum(T[keys[0]], T[keys[1]])
    m = FB.metrics(Tc, NG, FB.G_REF)
    TN = {k: T3.INV["P_rated_W"] / (FB.metrics(T[k], NG, FB.G_REF)["n_base_rpm"] * RPM) for k in keys}
    case = dict(kind="IM", designs=designs, T_N=TN, rotor=DL.rotor_from_design(T3.ST["R_gap_m"]), G=FB.G_REF,
                topo=("single", None))
    cr = DL.evaluate(case, 85.0, 0.0, DL.GEAR["drag_scale_variants"]["certified_like"])
    res = dict(T_peak_Nm=m["T_peak_Nm"], max_start_grade_pct=m["max_start_grade_pct"], CPSR=m["CPSR"],
               CPSR_capped=m["CPSR_capped_by_eval_range"], P_at_90kmh_kW=m["P_at_vmax_W"] / 1e3,
               crossover_speed_rpm=T3.crossover(T[keys[0]], T[keys[1]]) if True else None)
    if cr and cr.get("feasible"):
        P_in = cr["wheel_power_W"] / cr["eta_drivetrain_wheel_over_elec"]
        P_inv = inv["cruise_inverter_loss_fn"](cr["I_rms_A"])
        res["cruise_85kmh"] = dict(mode=cr["mode"], n_motor_rpm=cr["n_motor_rpm"], T_motor_Nm=cr["T_motor_Nm"],
                                   I_rms_A=cr["I_rms_A"], PF=cr["PF"], eta_motor_incl_fw=cr["eta_motor_incl_fw"],
                                   eta_motor_gear_wheel_over_elec=cr["eta_drivetrain_wheel_over_elec"],
                                   P_inverter_W=P_inv, eta_inverter=P_in / (P_in + P_inv) if P_inv is not None else None,
                                   eta_dc_to_wheel=cr["wheel_power_W"] / (P_in + P_inv) if P_inv is not None else None)
    else:
        res["cruise_85kmh"] = dict(feasible=False)
    return res


# ----------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------
def main():
    I_max = T3.IMAX
    res = dict(meta=dict(script="02_analytics/module_count_sweep.py", task="T08", date=_dt.date.today().isoformat(),
                         P_rated_W=T3.INV["P_rated_W"], V_dc_V=V_DC,
                         inputs=["board/decisions.md D05", "02_analytics/fair_baselines.py (T03b IM model)",
                                 "02_analytics/drivetrain_losses.py (T03d friction/windage, certified-like gear)",
                                 "../Analytical Loss Calculations - GaN/epc2361_loss.py (calculate(), reused)",
                                 "../PCB-Design/reports/paper/icpe/GaN_device_voltage_class_comparison_data.csv"],
                         assumptions="02_analytics/assumptions.md#t08",
                         notes=["Per-leg current is independent of N (N x V_module = 1200 V): I_max = %.1f A rms per leg at 300 kW." % I_max,
                                "Converter kVA (3N V_ph I_max) is therefore the same for every N; installed semiconductor VA (V_class x I) is not.",
                                "Machine for each N is the T03 geometry mapped to a 48-leg equivalent with the grouped winding factors."]),
               pole_modes={}, per_N={})
    # 1. feasibility table
    for N in N_LIST:
        tab = {}
        for Q in Q_LIST:
            if Q % (3 * N):
                continue
            for pr in PAIRS_2P:
                if Q < 3 * pr[0] // 2 * 2:      # need at least ~3 slots per pole pair in the high mode
                    continue
                r = feasibility(N, Q, pr)
                tab[f"Q{Q}_{pr[0]}/{pr[1]}"] = r if r else None
        res["pole_modes"][str(N)] = tab
        print(N, "feasible:", sorted(k for k, v in tab.items() if v))

    # 2 + 3. per-N inverter and pole-changing IM
    for N in N_LIST:
        V_mod = V_DC / N
        dev, vc, ok_margin = device_for(V_mod)
        n_par, I_dev_max = n_parallel(dev, I_max)
        legs = 3 * N
        rated = leg_loss(dev, V_mod, I_max, n_par)
        V_ph = T3.INV["m_margin"] * V_mod / math.sqrt(3) / math.sqrt(2)
        S_conv = legs * V_ph * I_max
        inv = dict(V_module_V=V_mod, device=dev, V_class_V=vc, derating_ratio=V_mod / vc, within_derating=ok_margin,
                   devices_parallel_per_switch=n_par, I_device_max_A=I_dev_max, legs=legs,
                   devices_total=legs * 2 * n_par, converter_kVA=S_conv / 1e3,
                   converter_kVA_per_kW=S_conv / T3.INV["P_rated_W"],
                   installed_semiconductor_kVA=legs * 2 * vc * I_max / 1e3,
                   installed_semiconductor_kVA_per_kW=legs * 2 * vc * I_max / T3.INV["P_rated_W"],
                   rated_point=dict(I_leg_A=I_max, **rated,
                                    P_inverter_W=legs * rated["P_leg_W"] if rated["ok"] else None,
                                    eta_inverter=(T3.INV["P_rated_W"] / 0.95) / (T3.INV["P_rated_W"] / 0.95 + legs * rated["P_leg_W"]) if rated["ok"] else None))

        def inv_loss(I_leg, dev=dev, V_mod=V_mod, n_par=n_par, legs=legs):
            r = leg_loss(dev, V_mod, I_leg, n_par)
            return legs * r["P_leg_W"] if r["ok"] else None
        inv["cruise_inverter_loss_fn"] = inv_loss
        # pole-changing IM: prefer 8/4; Q preference 48, 72, 96, 36, 60, 54, 24, 144
        im = None
        for pr in [(8, 4), (12, 6), (4, 2), (16, 8)]:
            for Q in (48, 72, 96, 36, 60, 54, 24, 144):
                f = res["pole_modes"][str(N)].get(f"Q{Q}_{pr[0]}/{pr[1]}")
                if f:
                    im = (pr, Q, f)
                    break
            if im:
                break
        entry = dict(inverter={k: v for k, v in inv.items() if k != "cruise_inverter_loss_fn"})
        if im:
            pr, Q, f = im
            des = pc_im_designs(Q, f["y_slots"], f["kw"][0], f["kw"][1], f["sigma_diff"][0], f["sigma_diff"][1], pr)
            ev = pc_im_eval(des, pr, inv)
            entry["pole_changing_IM"] = dict(pair_2p=list(pr), Q=Q, Q_practical=Q_PRACTICAL[0] <= Q <= Q_PRACTICAL[1],
                                             winding=f, N_leg_turns_equivalent_48leg=des[list(des)[0]]["N_leg_turns"], **ev)
            if ev["cruise_85kmh"].get("P_inverter_W") is not None:
                entry["inverter"]["cruise_point"] = dict(I_leg_A=ev["cruise_85kmh"]["I_rms_A"], P_inverter_W=ev["cruise_85kmh"]["P_inverter_W"],
                                                         eta_inverter=ev["cruise_85kmh"]["eta_inverter"])
        else:
            entry["pole_changing_IM"] = None
        res["per_N"][str(N)] = entry
        pi = entry["pole_changing_IM"]
        print(f"N={N:2d} Vmod={V_mod:6.1f} {dev:12s} class {vc:.0f} ({V_mod / vc:.2f}) npar={n_par:3d} rated inv eta="
              f"{inv['rated_point']['eta_inverter'] if rated['ok'] else 'n/a'}  IM:",
              None if pi is None else (pi["pair_2p"], pi["Q"], [round(x, 3) for x in pi["winding"]["kw"]], round(pi["T_peak_Nm"]),
                                       round(pi["max_start_grade_pct"], 2), round(pi["CPSR"], 2), round(pi["P_at_90kmh_kW"], 1),
                                       {k: (round(v, 4) if isinstance(v, float) else v) for k, v in pi["cruise_85kmh"].items()
                                        if k in ("mode", "eta_motor_gear_wheel_over_elec", "eta_inverter", "eta_dc_to_wheel", "P_inverter_W")}))
    # sanity: N = 16 reproduces the T03b pole-changing IM, and EPC2361 at its default point reproduces Enes's model
    ref = EPC.calculate(EPC.LossInputs())
    sw = loss_inputs("EPC2361", 75.0, 40.0)
    mine = EPC.calculate(sw)
    fb = json.load(open(FB.OUT_JSON))
    pc = fb["summary"]["pole_changing_2p8_4_T03"]
    p16 = res["per_N"]["16"]["pole_changing_IM"]
    res["sanity_checks"] = dict(
        EPC2361_default_total_loss_W=[ref["total_loss"], mine["total_loss"]],
        N16_T_peak_vs_T03b=[p16["T_peak_Nm"], pc["T_peak_Nm"]],
        N16_P90_vs_T03b_kW=[p16["P_at_90kmh_kW"], pc["P_at_90kmh_kW"]],
        N16_kw_vs_T03=[p16["winding"]["kw"], [abs(math.sin(4 * 7 * math.pi / 48)), abs(math.sin(2 * 7 * math.pi / 48))]],
        rule_check_Q48_N16_6pole_infeasible=res["pole_modes"]["16"].get("Q48_6/2") is None)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(res, fh, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else str(o))
    print(json.dumps(res["sanity_checks"], indent=1, default=float))


if __name__ == "__main__":
    main()

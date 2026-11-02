"""Gap-loop value screen H10 - series-stack cell power balance under SPB pole changing.

Run from repo root:  python 02_analytics/screen_H10.py
Output: 02_analytics/results/screen_H10.json
Assumptions: 02_analytics/assumptions.md, section H10.

Physics
-------
SPB cells are in series on the DC link, so every cell carries the same average DC current I_dc. Cell j's capacitor
obeys C dV_j/dt = I_dc - P_j/V_j. Two kinds of disturbance:
  * average (DC) power imbalance  dP_j  -> drift  dV/dt = dP_j/(V C)
  * power pulsation P~ at f        -> ripple dV_pk = P~/(2 pi f V C)
Module power with leg voltages/currents of spatial orders a (voltage) and b (current) at electrical angles
a*theta_k, b*theta_k (theta_k = coil position, legs of one module at theta_0 + 2 pi t/(m c)):
  P_j = sum_k v_k i_k = V I [ sum_k cos((w_a - w_b) t + (a-b) theta_k + ..) + sum_k cos((w_a + w_b) t + (a+b) theta_k + ..) ]
  -> the difference term survives iff m | (a-b)/c, the sum term iff m | (a+b)/c (amplitude m V I).
With a = b (one mode): sum term at 2w survives iff m | 2a/c  -> the T08 constant-power condition.
"""
from __future__ import annotations

import csv
import datetime as _dt
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
import module_count_sweep as MS   # noqa: E402  (winding engine, inverter data)
import torque_speed_envelope as T3  # noqa: E402

OUT = os.path.join(ROOT, "02_analytics", "results", "screen_H10.json")
BOM = os.path.join(KTH, "PCB-Design", "hardware", "spb-bb-revb-load", "fab", "spb-bb-revb-load-bom.csv")
SIM_IM = os.path.join(ROOT, "03_simulation", "results", "im_pole_transition.json")
SIM_WRSM = os.path.join(ROOT, "03_simulation", "results", "wrsm_pole_transition_ksweep.json")
H03 = os.path.join(ROOT, "02_analytics", "results", "screen_H03.json")

V_MOD = 75.0
RIPPLE_ALLOWED = 0.05                 # +/- 5 % of V_module (assumption)
BOARDS_PER_MODULE = 6                 # 3 legs x 2 parallel 150 kW blocks (SPB reference, CLAUDE.md fixed facts)
RETENTION = (0.35, 1.0)               # X7S 100 V at 75 V DC bias: retained fraction assumed 0.35 (worst) .. 1.0 (nominal)
P_MOD_RATED = T3.INV["P_rated_W"] / 16


# ----------------------------------------------------------------------------------
def board_capacitance_uF():
    """Bus capacitors (>= 100 V rating) on the Rev B load board."""
    tot, parts = 0.0, []
    with open(BOM, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    for r in rows:
        if len(r) < 3 or not r[0].isdigit():
            continue
        val = r[2]
        if "100V" in val.replace(" ", "") and "uF" in val:
            uf = float(val.split("uF")[0])
            tot += int(r[0]) * uf
            parts.append(dict(qty=int(r[0]), value=val, part=r[4] if len(r) > 4 else ""))
    return tot, parts


C_BOARD_uF, C_PARTS = board_capacitance_uF()
C_MOD = {k: BOARDS_PER_MODULE * C_BOARD_uF * 1e-6 * r for k, r in (("worst_retained", RETENTION[0]), ("nominal", RETENTION[1]))}


def ripple(P_pulse, f, C, V=V_MOD):
    return P_pulse / (2 * math.pi * f * V * C)


def c_required(P_pulse, f, V=V_MOD, dv=RIPPLE_ALLOWED * V_MOD):
    return P_pulse / (2 * math.pi * f * V * dv)


def drift(dP, C, V=V_MOD):
    return dP / (V * C)


def pulsation_record(name, P_pulse, f, mean_P=None, note=""):
    rec = dict(case=name, P_pulse_amplitude_W=P_pulse, f_Hz=f, note=note,
               ripple_pk_V={k: ripple(P_pulse, f, C) for k, C in C_MOD.items()},
               C_required_mF_for_5pct=c_required(P_pulse, f) * 1e3,
               C_available_mF=C_MOD_mF)
    if mean_P:
        rec["P_pulse_over_module_mean"] = P_pulse / mean_P
    rec["admissible_with_available_C"] = bool(rec["C_required_mF_for_5pct"] <= C_MOD_mF["worst_retained"])
    rec["admissible_with_nominal_C"] = bool(rec["C_required_mF_for_5pct"] <= C_MOD_mF["nominal"])
    return rec


C_MOD_mF = {k: v * 1e3 for k, v in C_MOD.items()}


# ----------------------------------------------------------------------------------
def cross_rule(m, c, a, b):
    """Which cross-power terms survive in a module (spaced wiring, interleaved modules)."""
    def div(x):
        return x % c == 0 and (x // c) % m == 0
    return dict(sum_term=div(a + b), difference_term=div(abs(a - b)))


def steady_state_table():
    """All (N, m, Q, p) modes from the T08 engine: average imbalance, pulsation fraction, eccentricity sensitivity."""
    rows, viol = [], []
    for N in MS.N_LIST:
        for m in MS.M_LIST:
            for Q in MS.Q_LIST:
                if Q % (m * N) or Q < 2 * m:
                    continue
                cb = MS.screen_combo(N, m, Q)
                if not cb:
                    continue
                for w in cb["wirings"]:
                    if w["partition"].startswith("matched"):
                        continue
                    for p, md in w["modes"].items():
                        P = MS.leg_phasor(w["legs"], w["signs"], Q, p)
                        U = P / np.abs(P)
                        Mx = np.array(w["modules"])
                        avg = np.abs(P[Mx]).sum(axis=1)                      # unity-PF module power proxy
                        avg_imb = float((avg.max() - avg.min()) / avg.mean())
                        puls = float(np.abs((U[Mx] ** 2).sum(axis=1)).max() / m)
                        # static eccentricity 10 %: coil EMF x (1 + 0.1 cos(theta_coil)); module power proxy
                        th = 2 * np.pi * np.array(w["legs"]) / Q
                        ecc = (1 + 0.1 * np.cos(th)).mean(axis=1)              # per leg
                        e_mod = ecc[Mx].mean(axis=1)
                        ecc_imb = float((e_mod.max() - e_mod.min()) / e_mod.mean())
                        r = dict(N=N, m=m, Q=Q, p=p, family=w["family"], partition=w["partition"], kd=md["kd"],
                                 avg_imbalance_pct=100 * avg_imb, pulsation_fraction_2f=puls,
                                 eccentricity10pct_imbalance_pct=100 * ecc_imb)
                        rows.append(r)
                        if puls > 1e-6:
                            viol.append(r)
    return rows, viol


# ----------------------------------------------------------------------------------
def main():
    res = dict(meta=dict(script="02_analytics/screen_H10.py", screen="H10", date=_dt.date.today().isoformat(),
                         metric="per-cell power imbalance (%), capacitor drift (V/s) / ripple, balancing headroom",
                         inputs=["02_analytics/module_count_sweep.py (winding engine)", "03_simulation/results/im_pole_transition.json",
                                 "03_simulation/results/wrsm_pole_transition_ksweep.json", "02_analytics/results/screen_H03.json (other analyst)",
                                 "../PCB-Design/hardware/spb-bb-revb-load/fab/spb-bb-revb-load-bom.csv"],
                         assumptions="02_analytics/assumptions.md#h10"),
               cell_capacitance=dict(board_bus_capacitors=C_PARTS, board_nominal_uF=C_BOARD_uF, boards_per_module=BOARDS_PER_MODULE,
                                     retention_assumed=RETENTION, C_module_mF=C_MOD_mF,
                                     source="Rev B load board BOM (100 V X7S MLCCs: 40 x 1 uF + 20 x 22 uF). PCB-Design/docs/capacitor-selection-p1.md: "
                                            "no DC-bias-retained value verified -> 0.35 retention assumed as worst case; no external bulk link defined yet. "
                                            "Boards per module = 3 legs x 2 parallel blocks (SPB reference) - assumption."),
               limits=dict(V_module_V=V_MOD, ripple_allowed_pk_V=RIPPLE_ALLOWED * V_MOD, P_module_rated_W=P_MOD_RATED))

    # 1. DC drift per 1 % imbalance
    res["drift_per_1pct_imbalance"] = {
        pt: {k: dict(dP_W=0.01 * P, dVdt_V_per_s=drift(0.01 * P, C), t_to_5pct_ms=1e3 * RIPPLE_ALLOWED * V_MOD / drift(0.01 * P, C))
             for k, C in C_MOD.items()}
        for pt, P in (("rated_18.75kW_per_module", P_MOD_RATED), ("cruise_9.7kW_per_module", 155e3 / 16))}

    # 2. steady states
    rows, viol = steady_state_table()
    adm = [r for r in rows if r["pulsation_fraction_2f"] < 1e-6 and r["avg_imbalance_pct"] < 1e-6]
    res["steady_state"] = dict(
        n_modes=len(rows), n_constant_power=len(adm), n_pulsating=len(viol),
        average_imbalance_max_pct=max(r["avg_imbalance_pct"] for r in rows),
        note="Every mode that passes the T08 rule (i)+(ii) has zero average imbalance (equal leg magnitudes, symmetric machine). "
             "Modes failing (iii) pulsate at 2 f_e with the listed fraction of module power (unity PF; / PF otherwise).",
        eccentricity_10pct=dict(interleaved_max_pct=max((r["eccentricity10pct_imbalance_pct"] for r in rows if r["partition"] == "interleaved"), default=None),
                                block_max_pct=max((r["eccentricity10pct_imbalance_pct"] for r in rows if r["partition"] == "block"), default=None),
                                note="interleaved modules (coils spread 360/m deg mech) cancel static eccentricity to first order; block modules do not -> DC drift"),
        pulsating_examples=[]
    )
    seen = set()
    for r in sorted(viol, key=lambda r: (-r["pulsation_fraction_2f"], r["N"])):
        key = (r["m"], r["p"], round(r["pulsation_fraction_2f"], 3))
        if key in seen:
            continue
        seen.add(key)
        f2 = 2 * r["p"] * 1151 / 60          # 2 f_e at the 8-pole base speed as a reference speed
        rec = pulsation_record(f"N{r['N']}_m{r['m']}_Q{r['Q']}_2p{2 * r['p']}", r["pulsation_fraction_2f"] * P_MOD_RATED * 16 / r["N"],
                               f2, mean_P=P_MOD_RATED * 16 / r["N"], note="steady state at rated power, 2 f_e at 1151 rpm")
        rec.update(fraction=r["pulsation_fraction_2f"])
        res["steady_state"]["pulsating_examples"].append(rec)
        if len(res["steady_state"]["pulsating_examples"]) >= 10:
            break
    # eccentricity drift example (block partition, worst)
    eb = res["steady_state"]["eccentricity_10pct"]["block_max_pct"]
    if eb:
        res["steady_state"]["eccentricity_10pct"]["block_drift_V_per_s_rated"] = {k: drift(eb / 100 * P_MOD_RATED, C) for k, C in C_MOD.items()}

    # 3. cross-mode rule table (transitions, injection)
    rule = {}
    for m in MS.M_LIST:
        for (a, b, label) in ((4, 2, "8/4 overlap"), (6, 2, "12/4 overlap"), (4, 8, "p=4 + inj. order 8 (H03)"), (2, 10, "2p4 + nu=10 (WRSM)"),
                              (4, 20, "2p8 + nu=20 (WRSM)"), (2, 14, "2p4 + nu=14 (WRSM)")):
            if a % m == 0 or b % m == 0:
                rule[f"m{m}_{label}"] = dict(injectable=False)
                continue
            rule[f"m{m}_{label}"] = dict(injectable=True, **cross_rule(m, 1, a, b))
    res["cross_mode_rule"] = dict(
        statement="Two simultaneous spatial orders a, b (both injectable, m does not divide a, b; c = 1) give module power pulsation "
                  "at f_a + f_b iff m | (a+b) and at |f_a - f_b| iff m | (a-b), amplitude m V_a I_b (+ m V_b I_a). "
                  "For m = 3 one of the two always holds (a, b in {1, 2} mod 3) -> every overlap / injection pulsates every cell. "
                  "For prime m >= 5 choose a != +-b (mod m) -> no pulsation.",
        table=rule)

    # 4. IM handover (simulator)
    sim = json.load(open(SIM_IM))
    bs = sim["best_schedule"]["grade_0pct"]
    n0 = bs["n0_rpm"]
    V8, I8, V4, I4 = bs["ss_before"]["V"], bs["ss_before"]["I"], bs["ss_after"]["V"], bs["ss_after"]["I"]
    f8, f4 = 4 * n0 / 60, 2 * n0 / 60
    P_mean = bs["T_req_Nm"] * n0 * T3.RPM / 16
    Pp = 3 * (V8 * I4 + V4 * I8)
    im = dict(source="03_simulation/results/im_pole_transition.json best_schedule grade_0pct (ss_before = 2p8, ss_after = 2p4; rms per coil)",
              V8_rms_V=V8, I8_rms_A=I8, V4_rms_V=V4, I4_rms_A=I4, overlap_s=bs["params"]["t_d"],
              m3=pulsation_record("IM 8->4 handover, full overlap, m=3", Pp, f8 + f4, P_mean,
                                  "sum-frequency term (2p8 positive, 2p4 negative sequence in each module); worst-case aligned"),
              m5_or_7_or_9="no pulsation (m does not divide 6 or 2): overlap admissible",
              max_overlap_product_for_5pct={k: dict(P_allowed_W=2 * math.pi * (f8 + f4) * V_MOD * RIPPLE_ALLOWED * V_MOD * C,
                                                    I_cross_allowed_A=2 * math.pi * (f8 + f4) * V_MOD * RIPPLE_ALLOWED * V_MOD * C / (3 * max(V8, V4)))
                                            for k, C in C_MOD.items()},
              torque_gap_without_overlap_s=next((c["torque_gap_below90pct_s"] for c in sim["cases"] if c["params"]["t_d"] <= 0.011), None))
    res["transition_IM_handover"] = im

    # 5. WRSM k-sweep (FE_MMF) and steady 2p4 circulating harmonics (simulator)
    ws = json.load(open(SIM_WRSM))
    tr = {f"gs{int(t['gs'])}_grade{t['grade_pct']:.0f}": t for t in ws["transitions"]}
    fm = 4 * 2100 / 60
    E_other = 0.5 * T3.VMAX       # assumption: mid-sweep (k = 0) back-EMF of the non-loaded order ~ half the voltage limit
    wr = {}
    for k_, t in tr.items():
        Ipk = t["I_rms_max_A"]
        wr[k_] = pulsation_record(f"WRSM k-sweep {k_}, m=3", 3 * E_other * Ipk, (4 + 2) * 2100 / 60,
                                  t["T_req_Nm"] * 2100 * T3.RPM / 16, "E_other = 0.5 V_max (assumed), I = sim I_rms_max")
    circ = {}
    for c in ws["harmonic"]["circulating"]:
        if c["n_rpm"] not in (2100, 4250):
            continue
        p = 2 if c["mode"] == "2p4" else 4
        nu = c["nu"]
        I_fund = 120.0                            # cruise-level fundamental current (assumption)
        Pp_c = 3 * (T3.VMAX * c["I_circ_rms_A"] + c["E_rms_V"] * I_fund)
        cr = cross_rule(3, 1, p, nu)
        f = ((p + nu) if cr["sum_term"] else abs(nu - p)) * c["n_rpm"] / 60
        circ[f"{c['mode']}_nu{nu}_{c['n_rpm']}rpm"] = dict(pulsation_record(f"WRSM {c['mode']} steady, nu={nu}", Pp_c, f, None,
                                                                             "3 (V_max I_circ + E_nu I_fund), I_fund = 120 A assumed"), **cr)
    res["transition_WRSM_ksweep"] = wr
    res["steady_WRSM_space_harmonics_m3"] = circ

    # 6. H03 harmonic injection
    h03 = None
    if os.path.exists(H03):
        h3 = json.load(open(H03))
        a = h3["meta"]["assumptions"]
        I_inj = a["I_inj_budget_over_Imax"] * T3.IMAX
        nu = h3["injection_choice"]["order"]
        P_field = 4000.0
        V_inj = P_field / (48 * I_inj)
        I_fund = 120.0
        out = {}
        for pt, n in (("50kmh", h3["capability"]["50kmh"]["speed_rpm"]), ("85kmh", h3["capability"]["85kmh"]["speed_rpm"])):
            fi = h3["capability"]["50kmh" if pt == "50kmh" else "85kmh"]["f_inj_Hz"]
            fe = 4 * n / 60
            cr = cross_rule(3, 1, 4, nu)
            f = fe + fi if cr["sum_term"] else abs(fe - fi)
            Pp_h = 3 * (T3.VMAX * I_inj + V_inj * I_fund)
            out[pt] = dict(pulsation_record(f"H03 injection nu={nu} at {pt}, m=3", Pp_h, max(f, 1.0), 155e3 / 16,
                                            "3 (V_fund I_inj + V_inj I_fund); I_inj = H03 budget 0.15 I_max; P_field 4 kW over 48 legs"),
                           f_e_Hz=fe, f_inj_Hz=fi, **cr)
        h03 = dict(source="02_analytics/results/screen_H03.json (other analyst instance)", order=nu, I_inj_A=I_inj, points=out,
                   m5_alternative="with m = 5 and p = 4, any injectable order nu = 2, 3 (mod 5) gives no pulsation (e.g. nu = 2, 3, 7, 8, 12, 13)")
    res["harmonic_injection_H03"] = h03

    # 7. H09 turn-change schemes
    res["H09_turn_change"] = dict(
        open_end_two_modules=dict(average_imbalance="share alpha of the coil voltage set by modulation: P_A = alpha P, P_B = (1 - alpha) P; "
                                                    "alpha = 0.5 balanced, and alpha is itself a balancing knob (full +-100 % of the pair power)",
                                  isolated_neutral="a module whose 3 legs all feed open-end coils to one partner module keeps zero current sum -> admissible",
                                  hardware="switching between star (2p8) and open-end (2p4) connection needs contactors/extra legs - outside H10",
                                  pulsation="none if both modules carry the same balanced set"),
        dc_voltage_reallocation=dict(condition="admissible iff P_j / V_j is equal for all cells (same I_dc); a 1 % mismatch drifts as in drift_per_1pct_imbalance",
                                     note="per-mode reallocation must move module power in exact proportion to the new cell voltages, through the balancing knobs below"),
        cell_to_coil_reassignment=dict(note="reassigning coils to modules electronically is not possible without switches; any reassignment that leaves "
                                            "modules with unequal coil counts gives average imbalance = (coil-count spread)/(mean)"))

    # 8. balancing headroom
    bal = {}
    for pt, V, Pm in (("cruise_85kmh", T3.VMAX, 155e3 / 16), ("base_speed_rated", T3.VMAX, P_MOD_RATED), ("standstill_start", T3.IMAX * 2.16e-3, 3 * T3.IMAX ** 2 * 2.16e-3)):
        per_A = 3 * V
        bal[pt] = dict(module_power_W=Pm, shift_per_ampere_W_per_A=per_A,
                       I_b_for_1pct_A=0.01 * Pm / per_A, I_b_for_10pct_A=0.1 * Pm / per_A,
                       extra_cu_loss_for_10pct_W=48 * (0.1 * Pm / per_A) ** 2 * 2.16e-3)
    res["balancing_headroom"] = dict(
        zero_sequence_circulation=dict(headroom_W=0.0, why="isolated neutrals: no current path between modules"),
        per_module_common_mode_voltage=dict(headroom_W=0.0, why="CM voltage drives no current in an isolated-neutral module; it only moves the neutral potential"),
        same_frequency_balancing_order=dict(
            principle="inject a current of order b with m | (p - b)/c (and m not dividing b) at f_e: the difference term is DC, "
                      "dP_j = m V I_b cos(phi_j), phi_j varies with the module position -> zero-sum redistribution; orders b = p +- m, p +- 2m, ... "
                      "give all spatial harmonics over the N modules (complete basis for zero-mean imbalance vectors)",
            m3_orders_for_p4=[1, 7, 10, 13], m5_orders_for_p4=[9, 14, 1 if False else 19],
            m5_note="for m = 5 the balancing orders (b = 9, 14, 19 for p = 4) are high and have low winding factors -> weaker knob per ampere; "
                    "the same property that removes cross-mode pulsation removes the low-order balancing knobs",
            numbers_m3=bal,
            limits="needs back-EMF (speed > 0): at standstill the knob is only I R; the b-order field induces rotor currents in an IM (extra loss, small torque ripple)"),
        module_current_scaling=dict(principle="scale module j currents by (1 + e_j), sum e_j = 0: dP_j = e_j P_j; equivalent to a set of b-orders; distorts MMF by |e|"),
        dc_side=dict(note="cell-to-cell DC-DC balancers or a bypass would be extra hardware (not zero-hardware)"),
        verdict="DC (average) imbalances are cheap to correct: 1 % costs about 1 A of balancing current at cruise. "
                "AC pulsations at f_a + f_b are not removable by these knobs within the module current budget at the 100s-of-W/A scale and must be avoided "
                "(mode/order choice, m >= 5) or absorbed by capacitance.")

    # 9. admissible mode set
    imm3 = im["m3"]
    res["admissible_mode_set"] = dict(
        steady_modes="admissible iff T08 rule (i) equal leg magnitude, (ii) module unit-sum zero, (iii) module square-sum zero; "
                     f"{res['steady_state']['n_constant_power']} of {res['steady_state']['n_modes']} enumerated modes pass; (iii)-violators need C_required (see examples) "
                     "or are excluded. Prefer interleaved module partitions (eccentricity cancels).",
        IM_handover_m3=dict(admissible=imm3["admissible_with_available_C"], C_required_mF=imm3["C_required_mF_for_5pct"],
                            ripple_pk_V=imm3["ripple_pk_V"],
                            rule="overlapped 8->4 handover pulsates each cell at f8 + f4; admissible only as a sequential handover with cross product "
                                 "below max_overlap_product_for_5pct, i.e. essentially no overlap -> torque gap (simulator: ~0.13 s at t_d = 0.01 s)"),
        IM_handover_m5plus="admissible with full overlap (torque-gap-free) when m does not divide (p1 +- p2)/c",
        WRSM_ksweep_m3={k: dict(admissible=v["admissible_with_available_C"], C_required_mF=v["C_required_mF_for_5pct"]) for k, v in wr.items()},
        H03_injection_m3=None if not h03 else {k: dict(admissible=v["admissible_with_available_C"], C_required_mF=v["C_required_mF_for_5pct"])
                                               for k, v in h03["points"].items()},
        H03_injection_m5="admissible with nu != +-p (mod 5)",
        H09_open_end="admissible (alpha = 0.5), alpha doubles as a balancing knob; star/open-end switching is hardware",
        H05_series_parking="inadmissible without DC bypass hardware: a parked cell (P_j = 0) still carries I_dc and charges at I_dc/C "
                           f"(e.g. I_dc = 250 A -> {250 / C_MOD['worst_retained']:.0f} V/s)")
    res["summary_text"] = (
        "H10 screen. Average (DC) imbalance is zero for every mode that passes the T08 winding rule and is cheap to trim with same-frequency "
        "balancing orders (about 1 A per 1 % at cruise). The binding constraint is AC power pulsation: in a 3-leg isolated-neutral module any two "
        "simultaneous spatial orders a, b give pulsation at f_a + f_b or |f_a - f_b| with amplitude 3 V I. This hits (1) the overlapped IM 8/4 "
        f"handover ({imm3['P_pulse_amplitude_W'] / 1e3:.1f} kW per cell at {imm3['f_Hz']:.0f} Hz, {imm3['P_pulse_over_module_mean']:.1f}x the cell mean, "
        f"C needed {imm3['C_required_mF_for_5pct']:.1f} mF vs {C_MOD_mF['worst_retained']:.1f}-{C_MOD_mF['nominal']:.1f} mF available), (2) the WRSM k-sweep, "
        "(3) H03 harmonic excitation, (4) steady WRSM space harmonics. For prime m >= 5 the pulsation vanishes when a != +-b (mod m), so m = 5/7 makes "
        "overlapped (torque-gap-free) transitions and harmonic excitation admissible, at the cost of weaker low-order balancing knobs. Series-cell "
        "parking (H05) is inadmissible without bypass hardware. Admissible set: steady modes with rule (i)-(iii); m = 3 transitions sequential "
        "(torque gap) or with sized capacitance; m >= 5 overlapped transitions with m not dividing (p1 +- p2)/c.")
    # sanity: time-domain module power for two simultaneous orders (unit V, I, rms), N = 16, c = 1
    def module_power_pp(m, pa, pb, fa=140.0, fb=70.0, N=16):
        Q = m * N
        t = np.linspace(0, 0.2, 40001)
        legs = [0 + k * N for k in range(m)]                      # module 0, interleaved
        P = np.zeros_like(t)
        for k in legs:
            th = 2 * np.pi * k / Q
            v = math.sqrt(2) * np.cos(2 * np.pi * fa * t + pa * th)
            i = math.sqrt(2) * np.cos(2 * np.pi * fb * t + pb * th)
            P += v * i
        return float((P.max() - P.min()) / 2), float(P.mean())
    res["sanity_time_domain"] = {f"m{m}_orders_{a}_{b}": dict(zip(("pulsation_amp_per_VI", "mean_per_VI"), module_power_pp(m, a, b)))
                                 for m, a, b in ((3, 4, 2), (5, 4, 2), (7, 4, 2), (3, 4, 8), (5, 4, 8), (6, 4, 2))}
    res["sanity_time_domain"]["m3_orders_4_4_same_frequency"] = dict(zip(("pulsation_amp_per_VI", "mean_per_VI"), module_power_pp(3, 4, 4, 140.0, 140.0)))
    res["sanity_time_domain"]["m6_orders_3_3_same_frequency"] = dict(zip(("pulsation_amp_per_VI", "mean_per_VI"), module_power_pp(6, 3, 3, 105.0, 105.0)))
    res["sanity_time_domain"]["expected"] = "m3 (4,2): 3; m5/m7 (4,2): 0; m3 (4,8): 3; m5 (4,8): 0; m6 (4,2): 6; one mode (4,4) m3 at one frequency: 0 pulsation, mean 3 cos; one mode p=3 in m6: pulsation 6 (fails rule iii)"
    json.dump(res, open(OUT, "w"), indent=1, default=MS.fmt)
    print(res["summary_text"])
    print(json.dumps(dict(C=res["cell_capacitance"]["C_module_mF"], drift=res["drift_per_1pct_imbalance"],
                          steady={k: v for k, v in res["steady_state"].items() if k != "pulsating_examples"},
                          IM=imm3, rule=res["cross_mode_rule"]["table"]), indent=1, default=MS.fmt)[:6000])
    for k, v in wr.items():
        print("WRSM", k, round(v["P_pulse_amplitude_W"]), round(v["C_required_mF_for_5pct"], 2), v["admissible_with_available_C"])
    for k, v in circ.items():
        print("circ", k, round(v["P_pulse_amplitude_W"]), round(v["f_Hz"]), round(v["C_required_mF_for_5pct"], 2), v["admissible_with_available_C"])
    if h03:
        for k, v in h03["points"].items():
            print("H03", k, round(v["P_pulse_amplitude_W"]), round(v["f_Hz"]), round(v["C_required_mF_for_5pct"], 2), v["admissible_with_available_C"])
    for e in res["steady_state"]["pulsating_examples"][:6]:
        print("steady", e["case"], round(e["fraction"], 3), round(e["C_required_mF_for_5pct"], 2))


if __name__ == "__main__":
    main()

"""Item 2: independent test of the analyst result 'WRSM pole change gives nothing'."""
import json, math, datetime
import numpy as np
import spb_core as c, wrsm_model as w, sync_model as s

OUT = {}
SP = np.array([300, 1000, 1500, 2100, 3000, 4250, 4500, 6000, 7500, 9000.0])
GS = 4.0
w.GS["v"] = GS
J = c.J
mpw = J["machine_parameters"]["WRSM"]

# --- 1. magnetising-inductance scaling from winding functions / rotor patterns ------------------------------------
sc = {}
sc["Lm_winding_function_p2_over_p4"] = c.L_m_fund(2) / c.L_m_fund(4)
sc["analyst_scaling_kw2_over_kw4_sq_times_4"] = (c.kw(2) / c.kw(4)) ** 2 * (4 / 2) ** 2
sc["kw_p4"], sc["kw_p2"] = c.kw(4), c.kw(2)
sc["L_sigma_total_H"] = {"2p8": c.L_sigma_mode(4) + c.L_diff(4), "2p4": c.L_sigma_mode(2) + c.L_diff(2)}
sc["analyst_L_sigma_H"] = {"2p8": mpw["2p8"]["L_sigma_s_H"], "2p4": mpw["2p4"]["L_sigma_s_H"]}


def small_signal(mode, If, a=8.0):
    pd0, pq0, r0 = w.solve_point(mode, 0, 0, If)
    pd1, _, _ = w.solve_point(mode, -a, 0, If)
    _, pq2, _ = w.solve_point(mode, 0, a, If)
    return dict(psi_f_rms=pd0 / c.SQ2, Ld=(pd0 - pd1) / a, Lq=pq2 / a, By=float(r0["By"].max()), Bt=float(r0["Bt"].max()))


ss = {}
for mode in ("2p8", "2p4"):
    ss[mode] = {f"If={f}": small_signal(mode, f) for f in (0.0, 0.3, 0.655, 1.0)}
sc["small_signal_gs4"] = ss
sc["Ld_ratio_2p4_over_2p8_at_If0"] = ss["2p4"]["If=0.0"]["Ld"] / ss["2p8"]["If=0.0"]["Ld"]
sc["Lq_ratio_2p4_over_2p8_at_If0"] = ss["2p4"]["If=0.0"]["Lq"] / ss["2p8"]["If=0.0"]["Lq"]
sc["psi_f_ratio_2p4_over_2p8"] = {k: ss["2p4"][k]["psi_f_rms"] / ss["2p8"][k]["psi_f_rms"] for k in ss["2p8"]}
sc["analyst_psi_f_ratio_same_If"] = mpw["pole_change"]["psi_ratio_p2_over_p4_same_If"]
Ifs = np.linspace(0, 1, 21)
by4 = [w.solve_point("2p4", 0, 0, f)[2]["By"].max() for f in Ifs]
by8 = [w.solve_point("2p8", 0, 0, f)[2]["By"].max() for f in Ifs]
psi4 = [w.solve_point("2p4", 0, 0, f)[0] / c.SQ2 for f in Ifs]
psi8 = [w.solve_point("2p8", 0, 0, f)[0] / c.SQ2 for f in Ifs]
sc["noload_curves"] = dict(If=Ifs.tolist(), By_2p4_T=by4, By_2p8_T=by8, psi_f_2p4_Wb=psi4, psi_f_2p8_Wb=psi8)
OUT["scaling"] = sc

# --- 2. variants: envelope of both modes, hybrid gain --------------------------------------------------------------
_orig = dict(YOKE_H=c.YOKE_H, RYM=c.RYM, LY=c.LY, AY=c.AY, M_YOKE=c.M_YOKE, NC=c.NC, RS=c.RS)


def set_geo(yoke_scale=1.0, nc_scale=1.0):
    c.YOKE_H = _orig["YOKE_H"] * yoke_scale
    c.RYM = c.R + c.SLOT_H + c.YOKE_H / 2
    c.LY = 2 * math.pi * c.RYM / c.Q
    c.AY = c.KST * c.LST * c.YOKE_H
    c.M_YOKE = _orig["M_YOKE"] * yoke_scale
    c.NC = _orig["NC"] * nc_scale
    c.RS = _orig["RS"] * nc_scale ** 2            # slot area fixed: half the turns -> 2x conductor area -> R/4


def build_map(mode, tag):
    ID = np.linspace(-450, 60, 12); IQ = np.linspace(0, 450, 10); IF = np.array([0, .2, .4, .6, .8, 1.0])
    out = np.zeros((len(ID), len(IQ), len(IF), 4))
    for a, idv in enumerate(ID):
        for b, iqv in enumerate(IQ):
            U = None
            for f, ifv in enumerate(IF):
                pd, pq, r = w.solve_point(mode, idv, iqv, ifv, U); U = r["U"]
                out[a, b, f] = (pd, pq, r["Bt"].max(), r["By"].max())
    np.savez(f"{c.ROOT}/03_simulation/scratch/wrsm_map_{mode}{tag}.npz", ID=ID, IQ=IQ, IF=IF, out=out)


VAR = {
    "baseline": dict(yoke=1.0, nc2p4=1.0, desc="as specified (yoke 25 mm, 3 turns both modes)"),
    "yoke_x2": dict(yoke=2.0, nc2p4=1.0, desc="stator yoke 50 mm (sized for 2p=4 flux)"),
    "turns_half_2p4": dict(yoke=1.0, nc2p4=0.5, desc="2p=4 runs with half the turns per coil (Dahlander-like series/parallel)"),
    "yoke_x2_turns_half": dict(yoke=2.0, nc2p4=0.5, desc="both"),
}
res = {}
for name, v in VAR.items():
    set_geo(v["yoke"], 1.0)
    tag8 = "_gs4" if name == "baseline" else f"_gs4_{name}8"
    if name != "baseline":
        build_map("2p8", tag8)
    w8 = s.Sync("WRSM", "2p8", tag=tag8)
    set_geo(v["yoke"], v["nc2p4"])
    tag4 = "_gs4" if name == "baseline" else f"_gs4_{name}4"
    if name != "baseline":
        build_map("2p4", tag4)
    w4 = s.Sync("WRSM", "2p4", tag=tag4)
    T8, T4 = [], []
    for n in SP:
        set_geo(v["yoke"], 1.0); t8, d8 = w8.envelope(n)
        set_geo(v["yoke"], v["nc2p4"]); t4, d4 = w4.envelope(n)
        T8.append(t8); T4.append(t4)
    T8, T4 = np.array(T8), np.array(T4)
    hyb = np.maximum(T8, T4)
    better = np.where(T4 > T8 * 1.001)[0]
    res[name] = dict(desc=v["desc"], speed_rpm=SP.tolist(), T_2p8=T8.tolist(), T_2p4=T4.tolist(),
                     T_ratio=(T4 / T8).tolist(), crossover_rpm=float(SP[better[0]]) if len(better) else None,
                     P_hybrid_over_P_2p8_at_4500=float(np.interp(4500, SP, hyb) / np.interp(4500, SP, T8)),
                     P_hybrid_over_P_2p8_at_9000=float(hyb[-1] / T8[-1]))
    print(name, [round(x) for x in T8], [round(x) for x in T4], res[name]["crossover_rpm"], flush=True)
set_geo(1.0, 1.0)
OUT["variants"] = res


# --- 3. per-unit dq model of OPT-Bipolar-Field-Excitation/analysis/4_design_studies/torque_speed_switching.m (ported) ---
def enes_model(kw4=0.808, kw2=0.760, xq4=0.31, alpha=2 / 3, turns_halved=True, fmax=429 / 381):
    kd = alpha + math.sin(alpha * math.pi) / math.pi
    kq = alpha - math.sin(alpha * math.pi) / math.pi + 2 / (3 * math.pi) * math.cos(alpha * math.pi / 2)
    xd4 = xq4 * kd / kq
    c4 = 4 / math.pi * math.sin(alpha * math.pi / 2); c2 = 8 / math.pi * math.cos(math.pi / 4) * math.sin(alpha * math.pi / 4)
    k2 = (kw2 / kw4) * (c2 / c4) * 2 / 2
    x2 = xq4 * (kw2 / kw4) ** 2 * (alpha / kq)
    if not turns_halved:             # same turns in both modes: flux linkage x2, reactance x4
        k2, x2 = k2 * 2, x2 * 4
    F, B, I = np.meshgrid(np.linspace(0, fmax, 101), np.linspace(-10, 90, 101) * math.pi / 180, np.linspace(0.5, 2, 16), indexing="ij")
    id_, iq = -I * np.sin(B), I * np.cos(B)
    P4 = (F + xd4 * id_, xq4 * iq); P4T = P4[0] * iq - P4[1] * id_
    P2 = (k2 * F + x2 * id_, x2 * iq); P2T = (P2[0] * iq - P2[1] * id_) / 2
    T4max = P4T[I <= 1].max(); g = (P4T >= 0.999 * T4max) & (I <= 1)
    Vmax = np.hypot(P4[0][g], P4[1][g]).min()
    n = np.linspace(0.02, 2.0, 100)
    out = []
    for x in n:
        r = []
        for (psd, psq, T), w_ in (((P4[0], P4[1], P4T), x), ((P2[0], P2[1], P2T), x / 2)):
            ok = (I <= 1 + 1e-9) & (w_ * np.hypot(psd, psq) <= Vmax + 1e-9)
            r.append(T[ok].max() if ok.any() else np.nan)
        out.append(r)
    out = np.array(out)
    better = np.where(out[:, 1] > out[:, 0] + 1e-3)[0]
    return dict(k2=k2, x2=x2, xq4=xq4, xd4=xd4, x2_over_xq4=x2 / xq4, T4_low=out[0, 0], T2_low=out[0, 1], T2_over_T4_low=out[0, 1] / out[0, 0],
                crossover_speed_over_n4_base=float(n[better[0]]) if len(better) else None,
                T2_over_T4_at_2x_base=float(out[-1, 1] / out[-1, 0]) if out[-1, 0] > 0 else None,
                speed_over_n4=n.tolist(), T4=out[:, 0].tolist(), T2=out[:, 1].tolist())


OUT["enes_kx"] = {"dahlander_turns_halved": enes_model(turns_halved=True), "same_turns_both_modes": enes_model(turns_halved=False)}
for k, v in OUT["enes_kx"].items():
    print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a not in ("speed_over_n4", "T4", "T2")})
OUT["spb_geometry_ratios"] = dict(kw2_over_kw4=c.kw(2) / c.kw(4), x_ratio_same_turns=(c.kw(2) / c.kw(4)) ** 2 * 4,
                                  x_ratio_half_turns=(c.kw(2) / c.kw(4)) ** 2 * 1.0)
meta = dict(script="03_simulation/run_wrsm_study.py", task="T04 item 2", date=str(datetime.date.today()),
            inputs=["Field Excitation/FE_MMF.m patterns", "OPT-Bipolar-Field-Excitation/analysis/4_design_studies/torque_speed_switching.m (ported)",
                    "02_analytics/results/torque_speed_envelope.json"],
            note=f"WRSM MEC with effective gap x{GS} (config B), rotor pole arc 0.7, interpolar permeance 0.08")
json.dump(dict(meta=meta, **OUT), open("results/wrsm_pole_change_study.json", "w"), indent=1, default=float)

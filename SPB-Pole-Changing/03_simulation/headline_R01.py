"""R01 item 3/4: headline numbers (IM crossover, CPSR, start grade, cruise efficiency) of the simulator on the agreed geometry at 300 kW,
next to the analyst's 300 kW file.  Run with  SPB_P_KW=300 python headline_R01.py"""
import json, math, os, datetime
import numpy as np
os.environ.setdefault("SPB_P_KW", "300")
import spb_core as c, sync_model as s

c.CAP_MODE["mode"] = "an_caps"
V = c.VEH
A = json.load(open(os.path.join(c.ROOT, "02_analytics", "results", "torque_speed_envelope_300kW.json")))
N = np.linspace(60, 9000, 150)


def start_grade(T):
    F = T * V["gear_ratio"] * V["eta_gear"] / V["wheel_radius_m"]
    mg, cr = V["mass_kg"] * V["g_m_s2"], V["Crr"]
    x = F / (mg * math.sqrt(1 + cr * cr))
    if x >= 1:
        return 100.0
    a = math.asin(x) - math.atan(cr)
    return 100 * math.tan(max(a, 0))


def metrics(T, p):
    Tp = T.max()
    nb = N[np.where(T >= 0.99 * Tp)[0].max()]
    Pb = np.interp(nb, N, p)
    band = np.where((p >= 0.95 * Pb) & (N >= nb))[0]
    # contiguous band
    end = nb
    for i in range(np.where(N >= nb)[0][0], len(N)):
        if p[i] >= 0.95 * Pb:
            end = N[i]
        else:
            break
    return dict(T_peak_Nm=float(Tp), n_base_rpm=float(nb), P_base_kW=float(Pb / 1e3), n_const_power_end_rpm=float(end), CPSR=float(end / nb),
                P_at_4500_kW=float(np.interp(4500, N, p) / 1e3), max_start_grade_pct=start_grade(Tp))


def crossover(T_hi_p, T_lo_p):
    better = T_lo_p > T_hi_p
    idx = np.where(~better)[0]
    if len(idx) == 0:
        return float(N[0])
    k = idx.max() + 1
    return float(N[k]) if k < len(N) else None


out = {}
P4, P2 = c.im_params(4), c.im_params(2)
T8 = np.array([c.im_envelope(P4, n)[0] for n in N]); T4 = np.array([c.im_envelope(P2, n)[0] for n in N])
Tc = np.maximum(T8, T4)
out["IM"] = dict(metrics_combined=metrics(Tc, Tc * N * c.RPM), metrics_2p8=metrics(T8, T8 * N * c.RPM), crossover_rpm=crossover(T8, T4),
                 T_2p8=T8.tolist(), T_2p4=T4.tolist())
# cruise (IM, same loss bookkeeping as T04: machine only, own friction law)
cr = c.im_loss_point(P2, 4250.0, 351.876)
out["IM"]["cruise_2p4"] = {k: cr.get(k) for k in ("eta", "I_rms_A", "V_rms_V", "P_cu_stator_W", "P_cu_rotor_W", "P_fe_W")} if cr else None
cr8 = c.im_loss_point(P4, 4250.0, 351.876)
out["IM"]["cruise_2p8"] = {k: cr8.get(k) for k in ("eta", "I_rms_A")} if cr8 else "not reachable"

w8, w4 = s.Sync("WRSM", "2p8", tag="_R01"), s.Sync("WRSM", "2p4", tag="_R01")
W8 = np.array([w8.envelope(n)[0] for n in N]); W4 = np.array([w4.envelope(n)[0] for n in N])
Wc = np.maximum(W8, W4)
out["WRSM"] = dict(metrics_combined=metrics(Wc, Wc * N * c.RPM), metrics_2p8=metrics(W8, W8 * N * c.RPM), crossover_rpm=crossover(W8, W4), T_2p8=W8.tolist(), T_2p4=W4.tolist())
for key, m in (("cruise_2p8", w8), ("cruise_2p4", w4)):
    r = m.loss_point(4250.0, 351.876)
    out["WRSM"][key] = {k: r.get(k) for k in ("eta", "I_rms_A", "V_rms_V", "P_cu_stator_W", "P_fe_W", "P_field_W")} if r else "not reachable"
pm = s.Sync("PMSM", "2p8")
Tp = np.array([pm.envelope(n)[0] for n in N])
out["PMSM"] = dict(metrics=metrics(Tp, Tp * N * c.RPM))
r = pm.loss_point(4250.0, 351.876)
out["PMSM"]["cruise"] = {k: r.get(k) for k in ("eta", "I_rms_A")}

# analyst 300 kW numbers
am = A["machines"]
spd = np.array(A["speed_rpm"])
def an_cross(hi, lo):
    a = np.array(am[hi]["torque_Nm"]); b = np.array(am[lo]["torque_Nm"])
    idx = np.where(b <= a)[0]
    return float(spd[idx.max() + 1]) if len(idx) and idx.max() + 1 < len(spd) else None
out["analyst_300kW"] = dict(
    IM_combined=am["IM"]["combined"]["metrics"], WRSM_combined=am["WRSM_freeId"]["combined"]["metrics"], PMSM=am["PMSM"]["2p8"]["metrics"],
    IM_crossover_rpm=an_cross("IM"if False else "IM", "IM") if False else None,
    cruise={k: A["efficiency_points"]["cruise_85kmh_road_load"][k] for k in ("IM_2p4", "WRSM_freeId_2p8", "PMSM_2p8")})
t8 = np.array(am["IM"]["2p8"]["torque_Nm"]); t4 = np.array(am["IM"]["2p4"]["torque_Nm"])
idx = np.where(t4 <= t8)[0]
out["analyst_300kW"]["IM_crossover_rpm"] = float(spd[idx.max() + 1])
w8a = np.array(am["WRSM_freeId"]["2p8"]["torque_Nm"]); w4a = np.array(am["WRSM_freeId"]["2p4"]["torque_Nm"])
out["analyst_300kW"]["WRSM_2p4_over_2p8_at_4500"] = float(np.interp(4500, spd, w4a) / np.interp(4500, spd, w8a))
out["sim_WRSM_2p4_over_2p8_at_4500"] = float(np.interp(4500, N, W4) / np.interp(4500, N, W8))
out["meta"] = dict(script="03_simulation/headline_R01.py", task="R01", date=str(datetime.date.today()), I_max_A=c.IMAX, geometry="data/machine_geometry.json (agreed)",
                   note="IM with imposed tooth (1.65 T tip) / yoke (1.45 T) limits; WRSM = chosen gap in derived.wrsm; speed grid 60 rpm")
json.dump(out, open("results/headline_R01.json", "w"), indent=1, default=float)
for k in ("IM", "WRSM"):
    print(k, out[k]["metrics_combined"], "crossover", out[k]["crossover_rpm"])
    print("  cruise", {kk: out[k][kk] for kk in out[k] if kk.startswith("cruise")})
print("analyst", out["analyst_300kW"]["IM_combined"]["CPSR"], out["analyst_300kW"]["IM_crossover_rpm"], out["analyst_300kW"]["IM_combined"]["max_start_grade_pct"])
print("PMSM", out["PMSM"])
print("WRSM 2p4/2p8 @4500: sim", out["sim_WRSM_2p4_over_2p8_at_4500"], "analyst", out["analyst_300kW"]["WRSM_2p4_over_2p8_at_4500"])

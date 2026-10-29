import json, sys, time, datetime
import numpy as np
import spb_core as c, sync_model as s

J = c.J; sp = np.array(J["speed_rpm"])
mp = J["machine_parameters"]["IM"]


def an_T(mach, key, n):
    return float(np.interp(n, sp, J["machines"][mach][key]["torque_Nm"]))


def err(a, b):
    return 100.0 * (b - a) / a if a not in (0, None) else None


rows = []        # (group, point, quantity, analyst, sim, err)
extra = {}


def add(group, point, q, a, sm):
    rows.append(dict(machine=group, point=point, quantity=q, analyst=a, sim=sm, err_pct=err(a, sm) if a else None))


# ---------------- IM envelope (flux limits of the analyst applied -> isolates leakage/physics) ----------------
IMP = {4: c.im_params(4), 2: c.im_params(2)}
IM_ENV = [(4, "2p8", 1000), (4, "2p8", 3000), (4, "2p8", 4500), (2, "2p4", 2100), (2, "2p4", 4500), (2, "2p4", 6000)]
im_env_out = []
for mode in ("an_caps", "mec"):
    c.CAP_MODE["mode"] = mode
    for p, key, n in IM_ENV:
        T, d = c.im_envelope(IMP[p], n)
        q = dict(IMP[p]); a = mp[key]
        q["Lsig_s"], q["Lsig_r"], q["Rr"] = a["L_sigma_s_H"], a["L_sigma_r_H"], a["R_r_ohm"]
        T2, _ = c.im_envelope(q, n)
        im_env_out.append(dict(cap_mode=mode, machine=f"IM {key}", n_rpm=n, T_sim=T, T_sim_with_analyst_leakage=T2,
                               T_analyst=an_T("IM", key, n), V=d["V"], I=d["I"], psi=d["psi"], Bt=d["Bt"]))
        if mode == "an_caps":
            add(f"IM {key}", f"{n} rpm, envelope", "torque_Nm", an_T("IM", key, n), T)
            add(f"IM {key}", f"{n} rpm, envelope", "V_rms_V (limit)", J["inverter"]["V_ph_rms_max_V"], d["V"])
            add(f"IM {key}", f"{n} rpm, envelope", "I_rms_A (limit)", J["inverter"]["I_module_rms_max_A"], d["I"])
extra["IM_envelope"] = im_env_out
c.CAP_MODE["mode"] = "an_caps"

# ---------------- PMSM envelope ---------------------------------------------------------------------------
pm = s.Sync("PMSM", "2p8")
for n in (1000, 2100, 4500, 6000):
    T, d = pm.envelope(n)
    add("PMSM 2p8", f"{n} rpm, envelope", "torque_Nm", an_T("PMSM", "2p8", n), T)
    add("PMSM 2p8", f"{n} rpm, envelope", "I_rms_A at max T", J["inverter"]["I_module_rms_max_A"], d["I"])
extra["PMSM_fine_grid_4500"] = pm.envelope(4500, nid=161, niq=161)[0]

# ---------------- WRSM envelope (two sim configurations) --------------------------------------------------
wr = {}
for tag in ("", "_gs4"):
    for mode in ("2p8", "2p4"):
        wr[(tag, mode)] = s.Sync("WRSM", mode, tag=tag)
wr_out = []
for tag, lab in (("_gs4", "B"), ("", "A")):
    for mode in ("2p8", "2p4"):
        for n in (1000, 2100, 4250, 4500):
            T, d = wr[(tag, mode)].envelope(n)
            a = an_T("WRSM_freeId", mode, n)
            wr_out.append(dict(config=lab, mode=mode, n_rpm=n, T_sim=T, T_analyst_freeId=a, T_analyst_Id0=an_T("WRSM_Id0", mode, n),
                               I_f_pu=d["If"], id_A=d["id"], iq_A=d["iq"], V=d["V"], I=d["I"]))
            if lab == "B":
                add(f"WRSM {mode}", f"{n} rpm, envelope (free I_d, I_f)", "torque_Nm", a, T)
extra["WRSM_envelope"] = wr_out

# ---------------- loss / current / voltage at analyst efficiency points -----------------------------------
EP = J["efficiency_points"]
KEYS = [("I_rms_A", "I_rms_A"), ("V_rms_V", "V_rms_V"), ("P_cu_stator_W", "P_cu_stator_W"), ("P_fe_W", "P_fe_W"), ("eta", "eta"), ("PF", "PF")]
eff_out = []
for pname, pt in EP.items():
    n, T = pt["speed_rpm"], pt["torque_Nm"]
    for key, ak, simf in (("IM_2p8", "2p8", lambda n, T: c.im_loss_point(IMP[4], n, T)),
                          ("IM_2p4", "2p4", lambda n, T: c.im_loss_point(IMP[2], n, T)),
                          ("PMSM_2p8", "2p8", lambda n, T: pm.loss_point(n, T)),
                          ("WRSM_freeId_2p8", "2p8", lambda n, T: wr[("_gs4", "2p8")].loss_point(n, T)),
                          ("WRSM_freeId_2p4", "2p4", lambda n, T: wr[("_gs4", "2p4")].loss_point(n, T))):
        a = pt.get(key)
        r = simf(n, T)
        rec = dict(point=pname, machine=key, n_rpm=n, T_Nm=T, analyst=a, sim=None if r is None else {k: r.get(k) for k in
                   ("I_rms_A", "V_rms_V", "P_cu_stator_W", "P_cu_rotor_W", "P_fe_W", "P_field_W", "eta", "PF", "P_mech_W")})
        if r is not None:
            rec["sim_extra"] = {k: r.get(k) for k in ("id", "iq", "If", "psi", "wsl")}
        eff_out.append(rec)
        if a is not None and r is not None:
            for qn, qk in (("I_rms_A", "I_rms_A"), ("V_rms_V", "V_rms_V"), ("P_cu_stator_W", "P_cu_stator_W"), ("P_fe_W", "P_fe_W"), ("eta_pct", "eta")):
                av = a[qk] * (100 if qn == "eta_pct" else 1); sv = r[qk] * (100 if qn == "eta_pct" else 1)
                add(key, f"{pname} ({n:.0f} rpm, {T:.0f} Nm)", qn, av, sv)
            if key.startswith("IM"):
                add(key, f"{pname} ({n:.0f} rpm, {T:.0f} Nm)", "P_cu_rotor_W", a["P_cu_rotor_W"], r["P_cu_rotor_W"])
            if key.startswith("WRSM"):
                add(key, f"{pname} ({n:.0f} rpm, {T:.0f} Nm)", "P_field_W", a["P_field_W"], r["P_field_W"])
        elif a is not None and r is None:
            rec["note"] = "analyst reachable, sim not reachable"
        elif a is None and r is not None:
            rec["note"] = "analyst NOT reachable, sim reachable"
extra["efficiency_points"] = eff_out
json.dump(dict(meta=dict(script="03_simulation/run_validation.py", task="T04", date=str(datetime.date.today()),
                         inputs=["02_analytics/results/torque_speed_envelope.json (350 kW, read-only)"],
                         note="IM sim uses the analyst's tooth/yoke flux caps (CAP_MODE=an_caps) in the primary table; soft MEC saturation in extra.IM_envelope[cap_mode=mec]. WRSM sim = config B (effective gap x4, field MMF x4)."),
               rows=rows, extra=extra), open("results/validation_points.json", "w"), indent=1, default=float)
bad = [r for r in rows if r["err_pct"] is not None and abs(r["err_pct"]) > 5]
print(len(rows), "rows;", len(bad), ">5 %")
for r in rows:
    print(f'{r["machine"]:16s} {r["point"]:44s} {r["quantity"]:22s} {r["analyst"]:12.4g} {r["sim"]:12.4g} {r["err_pct"] if r["err_pct"] is None else round(r["err_pct"],1)}')
for e in eff_out:
    if "note" in e: print("NOTE", e["point"], e["machine"], e["note"])

"""R01 stage 2: quantities derived from data/machine_geometry.json -> appended as `derived` (single file for both models)."""
import json, math, os, sys, subprocess, datetime
import numpy as np
os.environ["SPB_GEOM"] = "agreed"
import spb_core as c, wrsm_model as w

J = c.J
G = c.GEOM["rotor_wrsm"]
kcs = c.GEOM["airgap"]["carter_stator"]
B0 = G["B0_noload_T"]
LB = c.VMAX / (c.IMAX * 4 * 1200 * c.RPM)          # T03 per-unit inductance base (350 kW current), 1.864e-4 H
LB300 = LB * c.IMAX / (c.IMAX * 266.09 / 310.44)
PSIB = c.VMAX / (4 * 1200 * c.RPM)
D = {}

# ---------------- A. IM leakage ---------------------------------------------------------------------------------
mp = J["machine_parameters"]["IM"]
laa, lbb, lab = c.slot_lambdas()
D["slot_lambda"] = dict(top_self=laa, bottom_self=lbb, mutual=lab, analyst_self=1.2, analyst_mutual=0.4,
                        note="units of mu0*L_stk*N_c^2; top air 6.6 mm and tooth tip 1.5 mm over a 3 mm opening included")
im = {}
for p, key in ((4, "2p8"), (2, "2p4")):
    par = c.im_params(p)
    a = mp[key]
    im[key] = dict(
        L_slot_H=dict(agreed=par["Lslot"], analyst=a["L_slot_H"]),
        L_end_H=dict(agreed=par["Lend"], analyst=a["L_end_H"]),
        L_diff_stator_H=dict(agreed=par["Ldiff_s"], analyst=a["L_diff_H"]),
        L_sigma_s_H=dict(agreed=par["Lsig_s"], analyst=a["L_sigma_s_H"]),
        L_sigma_r_referred_H=dict(agreed=par["Lsig_r"], analyst=a["L_sigma_r_H"]),
        R_r_referred_ohm=dict(agreed=par["Rr"], analyst=a["R_r_ohm"]),
        L_m_linear_H=dict(agreed=par["Lm"], analyst=a["Lm_H"], note="agreed uses g_eff = 1.076 mm (Carter only); analyst 1.3 mm (Carter*saturation)"),
        k_w=c.kw(p))
D["im_leakage"] = im

# ---------------- B. flux caps ----------------------------------------------------------------------------------
caps = {}
for p, key in ((4, "2p8"), (2, "2p4")):
    ic, pc, btc, byc = c.mag_curve(p)
    ok_t = btc <= c.B_TOOTH_CAP
    ok_y = byc <= c.B_YOKE_CAP
    i_t = np.where(ok_t)[0].max(); i_y = np.where(ok_y)[0].max()
    ik = min(i_t, i_y)
    # analytic fundamental gap-flux-density caps from geometry (sinusoidal field)
    Bg_tooth = c.B_TOOTH_CAP * c.KST * c.TOOTH_W_TIP / c.TAU / c.R * (c.R)  # placeholder replaced below
    tau_s = 2 * math.pi * c.R / c.Q
    Bg_tooth = c.B_TOOTH_CAP * c.KST * c.TOOTH_W_TIP / tau_s
    Bg_yoke = c.B_YOKE_CAP * p * c.YOKE_H * c.KST / c.R
    caps[key] = dict(psi_cap_rms_Wb=dict(agreed=float(pc[ik]), analyst=J["machine_parameters"]["IM"][key]["psi_cap_rms_Wb"]),
                     limiting="yoke" if i_y < i_t else "tooth",
                     psi_at_tooth_limit_Wb=float(pc[i_t]), psi_at_yoke_limit_Wb=float(pc[i_y]),
                     Bg1_cap_T_analytic=dict(tooth=Bg_tooth, yoke=Bg_yoke, analyst=J["machine_parameters"]["IM"][key]["B_gap_cap_T"]),
                     I_mag_at_cap_A_rms=float(ic[ik]), k_sat_secant_at_cap=float((ic[ik] / pc[ik]) * c.L_m_fund(p)))
    # magnetising curve table for the analyst (downsampled)
    sel = np.unique(np.concatenate([np.arange(0, len(ic), 4), [ik]]))
    caps[key]["magnetising_curve"] = dict(i_m_rms_A=ic[sel].tolist(), psi_m_rms_Wb=pc[sel].tolist(), B_tooth_tip_peak_T=btc[sel].tolist(), B_yoke_peak_T=byc[sel].tolist(),
                                          note="stator mode p, d-axis, smooth rotor; psi = fundamental airgap flux linkage per coil (leakage excluded)")
D["flux_caps"] = caps

# ---------------- C. WRSM: gap, L_d, L_q, field MMF, field copper, tau_f -----------------------------------------
def wrsm_design(gm_mm, quick=False):
    geff = gm_mm * 1e-3 * kcs
    gs = geff / c.GEFF
    w.GS["v"] = gs
    w.RINT["v"] = geff / G["interpolar_path_length_m"]
    F = B0 * geff / c.MU0
    res = dict(g_mech_mm=gm_mm, g_eff_mm=geff * 1e3, F_pole_At=F)
    for mode in ("2p8", "2p4"):
        pd0, pq0, r0 = w.solve_point(mode, 0, 0, 1.0)
        pd1, _, _ = w.solve_point(mode, -20, 0, 1.0)
        _, pq2, _ = w.solve_point(mode, 0, 20, 1.0)
        res[mode] = dict(psi_f_rms_Wb=pd0 / c.SQ2, L_d_H=(pd0 - pd1) / 20, L_q_H=pq2 / 20, L_d_pu=(pd0 - pd1) / 20 / LB, L_q_pu=pq2 / 20 / LB,
                         B_stator_yoke_T=float(r0["By"].max()))
    # rotor copper
    Rro = c.R - gm_mm * 1e-3
    rm = Rro - G["field_slot_depth_m"] / 2
    wsl = 2 * math.pi * rm / G["poles"] - G["pole_body_width_m"]
    A_cu = G["field_fill"] * wsl * G["field_slot_depth_m"] / 2
    P_f = G["poles"] * G["rho_cu_120C_ohm_m"] * G["mean_turn_length_m"] * F ** 2 / A_cu
    # field circuit: permeance of one pole + interpolar leakage
    P_pole = c.MU0 * Rro * G["pole_arc_ratio"] * 2 * math.pi / G["poles"] * c.LST / geff
    Lam = c.MU0 * c.LST * G["field_slot_depth_m"] / wsl
    n = G["poles"]
    lap = 2 * np.eye(n) - np.roll(np.eye(n), 1, 0) - np.roll(np.eye(n), -1, 0)
    for mode, pat in (("2p8", np.array(G["pattern_2p8"], float)), ("2p4", np.array(G["pattern_2p4"], float))):
        Wm = 0.5 * F ** 2 * pat @ (P_pole * (np.eye(n) - 1 / n)) @ pat
        Wl = 0.5 * F ** 2 * pat @ (Lam * lap) @ pat
        res[mode].update(W_main_J=Wm, W_leak_J=Wl, leak_factor=(Wm + Wl) / Wm, tau_f_s=2 * (Wm + Wl) / P_f)
    # rotor yoke flux density check (2p4 carries twice the flux of 2p8)
    Phi = B0 * G["pole_arc_ratio"] * 2 * math.pi * Rro / n * c.LST
    h_ry = Rro - G["field_slot_depth_m"] - G["shaft_radius_m"]
    res["rotor"] = dict(A_cu_per_coil_side_mm2=A_cu * 1e6, J_f_A_mm2=F / A_cu / 1e6, P_field_full_W=P_f, interpolar_slot_width_mm=wsl * 1e3,
                        rotor_yoke_thickness_mm=h_ry * 1e3, B_rotor_yoke_2p8_T=Phi / (2 * h_ry * c.LST * c.KST), B_rotor_yoke_2p4_T=2 * Phi / (2 * h_ry * c.LST * c.KST),
                        B_pole_body_T=Phi / (G["pole_body_width_m"] * c.LST * c.KST * 1.0) / 1.0)
    return res


sweep = [wrsm_design(g) for g in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)]
D["wrsm_gap_sweep"] = sweep
# selection rule: smallest gap with L_d(2p=8, full field) <= 1.6 pu and J_f <= 6 A/mm2
chosen = next(s for s in sweep if s["2p8"]["L_d_pu"] <= 1.6 and s["rotor"]["J_f_A_mm2"] <= 6.0)
D["wrsm"] = dict(chosen_g_mech_mm=chosen["g_mech_mm"], g_eff_mm=chosen["g_eff_mm"], gs_vs_IM_geff=chosen["g_eff_mm"] * 1e-3 / c.GEFF, r_int=chosen["g_eff_mm"] * 1e-3 / G["interpolar_path_length_m"],
                 F_pole_At=chosen["F_pole_At"], P_field_full_W=chosen["rotor"]["P_field_full_W"], J_f_A_mm2=chosen["rotor"]["J_f_A_mm2"],
                 L_d_pu_2p8=chosen["2p8"]["L_d_pu"], L_q_pu_2p8=chosen["2p8"]["L_q_pu"], L_d_pu_2p4=chosen["2p4"]["L_d_pu"], L_q_pu_2p4=chosen["2p4"]["L_q_pu"],
                 psi_f_rms_Wb_2p8=chosen["2p8"]["psi_f_rms_Wb"], psi_f_rms_Wb_2p4=chosen["2p4"]["psi_f_rms_Wb"],
                 tau_f_s_2p8=chosen["2p8"]["tau_f_s"], tau_f_s_2p4=chosen["2p4"]["tau_f_s"], rotor=chosen["rotor"],
                 pu_base=dict(L_base_H=LB, psi_base_rms_Wb=PSIB, note="V_max/(I_max w_ref), w_ref = 4 pole pairs at 1200 rpm, 350 kW current (T03 base)"),
                 analyst=dict(L_d_pu=1.10, L_q_pu=0.65, psi_f_max_pu=0.85, P_field_W=4000.0, tau_f_s=0.0446, g_eff_mm_implied="about 1.3 mm for tau_f and F, about 5 mm for L_d"),
                 selection_rule="smallest g with L_d(2p=8, full field) <= 1.6 pu and J_f <= 6 A/mm2; field fill 0.5 of half an interpolar slot 55 mm deep")
D["wrsm"]["verdict"] = ("An analyst WRSM with L_d = 1.10 pu is not physical at the IM gap (g_eff 1.08 mm gives L_d = %.1f pu). A 300 kW, 8-pole WRSM in this stator needs a mechanical gap of about %.0f mm "
                        "(g_eff %.1f mm), %.0f A-turns per pole at B0 = 0.71 T, J_f = %.1f A/mm2 and %.1f kW of field copper. The analyst's 4 kW and 45 ms correspond to 737 A-turns, i.e. the IM gap."
                        % (sweep[0]["2p8"]["L_d_pu"], chosen["g_mech_mm"], chosen["g_eff_mm"], chosen["F_pole_At"], chosen["rotor"]["J_f_A_mm2"], chosen["rotor"]["P_field_full_W"] / 1e3))
print(D["wrsm"]["verdict"])
for s in sweep:
    print(s["g_mech_mm"], round(s["F_pole_At"]), round(s["rotor"]["J_f_A_mm2"], 1), round(s["rotor"]["P_field_full_W"]), "Ld/Lq 2p8", round(s["2p8"]["L_d_pu"], 2), round(s["2p8"]["L_q_pu"], 2),
          "2p4", round(s["2p4"]["L_d_pu"], 2), round(s["2p4"]["L_q_pu"], 2), "tau", round(s["2p8"]["tau_f_s"], 3), round(s["2p4"]["tau_f_s"], 3), "Bry", round(s["rotor"]["B_rotor_yoke_2p4_T"], 2))

g = json.load(open(c.GEOM_JSON))
g["rotor_wrsm"]["g_mechanical_m"] = chosen["g_mech_mm"] * 1e-3
g["rotor_wrsm"]["g_eff_m"] = chosen["g_eff_mm"] * 1e-3
g["rotor_wrsm"]["interpolar_permeance_ratio"] = D["wrsm"]["r_int"]
g["rotor_wrsm"]["field_MMF_per_pole_At"] = chosen["F_pole_At"]
g["rotor_wrsm"]["field_copper_P_full_W"] = chosen["rotor"]["P_field_full_W"]
g["derived"] = dict(meta=dict(script="03_simulation/compute_R01.py", date=str(datetime.date.today()), note="computed with the MEC/winding-function model of spb_core.py on this geometry"), **D)
json.dump(g, open(c.GEOM_JSON, "w"), indent=1, default=float)
# maps for the chosen WRSM geometry
subprocess.run([sys.executable, "build_maps.py", str(D["wrsm"]["gs_vs_IM_geff"]), str(D["wrsm"]["r_int"]), "_R01"], check=True)
print("done")

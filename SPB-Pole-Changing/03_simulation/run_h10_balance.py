"""H10 item 4: the balancing knob.  Inject a same-frequency current of order b into every coil (module j gets a phase offset by the spatial
position of its coils) at the cruise point (IM 2p=4, a = 2, 4250 rpm, 352 Nm) and measure, from the coil-level power P_j(t), how much average
power moves between cells per ampere, and what it costs (rotor loss, stator copper, voltage, torque)."""
import json, math, datetime
import numpy as np
import spb_core as c

c.CAP_MODE["mode"] = "an_caps"
NMOD = 16
n_rpm, T_req = 4250.0, 351.876
a = 2
par = {p: c.im_params(p) for p in (1, 2, 4, 5, 8)}
pt = c.im_loss_point(par[2], n_rpm, T_req)
psi, wsl = pt["psi"], pt["wsl"]
P = par[2]
im_c, ps_c = c.mag_curve(2)[0], c.mag_curve(2)[1]
im = float(np.interp(psi, ps_c, im_c))
Ir = -1j * wsl * psi / (P["Rr"] + 1j * wsl * P["Lsig_r"])
Is = im - Ir
we = a * n_rpm * c.RPM + wsl
Va = (P["Rs"] + 1j * we * P["Lsig_s"]) * Is + 1j * we * psi          # rms phasors per coil
Ia = Is
Om = n_rpm * c.RPM
Pmean_cell = 3 * np.real(Va * np.conj(Ia))                          # W, three coils of a cell
print("cruise: V %.2f V, I %.1f A, cell power %.0f W (check: shaft+losses %.0f W / 16)" % (abs(Va), abs(Ia), Pmean_cell, (T_req * Om + pt["Pcus"] + pt["Pcur"] + pt["Pfe"] + c.p_mech(n_rpm)) / 16))


def Zb(b):
    pb = abs(b)
    q = par[pb]
    wsl_b = we - b * Om
    Lr = q["Lm"] + q["Lsig_r"]
    psi_ratio = q["Lm"] * (q["Rr"] + 1j * wsl_b * q["Lsig_r"]) / (q["Rr"] + 1j * wsl_b * Lr)    # psi_m per unit stator current
    ir_ratio = -1j * wsl_b * q["Lm"] / (q["Rr"] + 1j * wsl_b * Lr)                                 # referred rotor current per stator current
    Z = q["Rs"] + 1j * we * q["Lsig_s"] + 1j * we * psi_ratio
    return Z, ir_ratio, psi_ratio, wsl_b, q


def avg_cell_power(b, Ib_rms, theta, Q=48, m=3):
    """cycle-averaged power of each of the 16 cells with mode a plus an injected current of order b at the same frequency."""
    Z, ir_ratio, psi_ratio, wsl_b, q = Zb(b)
    Ibp = Ib_rms * math.sqrt(2) * np.exp(1j * theta)
    Vbp = Z * Ibp
    Iap, Vap = Ia * math.sqrt(2), Va * math.sqrt(2)
    t = np.linspace(0, 2 * math.pi / we, 400, endpoint=False)
    out = np.zeros(NMOD)
    for j in range(NMOD):
        for ii in range(m):
            k = j + 16 * ii
            ak, bk = a * 2 * math.pi * k / Q, b * 2 * math.pi * k / Q
            v = np.real(Vap * np.exp(1j * (we * t - ak))) + np.real(Vbp * np.exp(1j * (we * t - bk)))
            i = np.real(Iap * np.exp(1j * (we * t - ak))) + np.real(Ibp * np.exp(1j * (we * t - bk)))
            out[j] += np.mean(v * i)
    return out


res = dict(meta=dict(script="03_simulation/run_h10_balance.py", task="H10 item 4", date=str(datetime.date.today()),
                     operating_point=dict(mode="IM 2p=4 (a=2)", n_rpm=n_rpm, T_Nm=T_req, V_rms=abs(Va), I_rms=abs(Ia), mean_cell_power_W=Pmean_cell)), cases=[])
base = avg_cell_power(2, 0.0, 0.0)
for b in (5, -1, 8, -4, 4, 1):
    best = None
    for th in np.linspace(0, 2 * math.pi, 73):
        d = avg_cell_power(b, 1.0, th) - base            # 1 A rms injected
        sp = np.max(np.abs(d - d.mean()))
        if best is None or sp > best[0]:
            best = (sp, th, d)
    sp, th, d = best
    Z, ir_ratio, psi_ratio, wsl_b, q = Zb(b)
    # cost of 1 A rms: rotor copper, stator copper, voltage
    Ibr = 1.0
    P_rot = c.M * q["Rr"] * abs(ir_ratio) ** 2 * Ibr ** 2
    P_cu = c.M * q["Rs"] * Ibr ** 2
    # torque of the injected mode: air-gap power / synchronous speed of order b at frequency we
    # torque from rotor power: P_rot_mech = P_ag - P_rot, T = P_ag / (we / b)
    Pag_b = c.M * np.real(1j * we * psi_ratio) * 1.0
    Tb = Pag_b / (we / b)
    need_I = 0.05 * Pmean_cell / sp if sp > 1e-3 else float('nan')
    case = dict(b=b, a_minus_b_mod_3=(a - b) % 3, W_per_A_rms=float(sp), percent_of_cell_power_per_A=float(100 * sp / Pmean_cell),
                best_phase_deg=float(np.degrees(th)), module_dP_W_per_A=d.tolist(), sum_over_modules_W=float(d.sum()),
                I_b_for_5pct_A_rms=float(need_I), I_b_over_I_a=float(need_I / abs(Ia)),
                cost_for_5pct=dict(rotor_cu_W=float(P_rot * need_I ** 2), stator_cu_W=float(P_cu * need_I ** 2), V_b_rms_V=float(abs(Z) * need_I),
                                   V_b_over_Vmax=float(abs(Z) * need_I / c.VMAX), torque_Nm=float(Tb * need_I ** 2), slip_freq_rad_s=float(wsl_b)))
    cost = case["cost_for_5pct"]
    case["watts_moved_per_watt_lost"] = float(0.05 * Pmean_cell / (cost["rotor_cu_W"] + cost["stator_cu_W"]))
    res["cases"].append(case)
    print(b, "(a-b) mod 3 =", case["a_minus_b_mod_3"], "W/A %.1f (%.2f %%/A)" % (sp, case["percent_of_cell_power_per_A"]), "sum over cells %.2f" % d.sum(),
          "I for 5 %% = %.1f A (%.1f %% of I_a)" % (need_I, 100 * need_I / abs(Ia)), {k: round(v, 3) for k, v in cost.items()}, flush=True)
json.dump(res, open("results/confirm_H10_balance.json", "w"), indent=1, default=float)

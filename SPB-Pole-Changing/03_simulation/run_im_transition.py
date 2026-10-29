"""Item 3a: IM 8 -> 4 pole transition at ~2100 rpm, time domain (two decoupled spatial modes p=4 and p=2 on the 48-coil stator).

State per mode m: stator current space vector i_m (amplitude, stationary frame of the mode), rotor flux psi_r,m (referred).
  dpsi_r/dt = -(Rr/Lr)(psi_r - Lm i_s) + j w_m psi_r      (cage mode p is spatially orthogonal to the cage mode of the other p)
  v = Rs i + sigma Ls di/dt + (Lm/Lr) dpsi_r/dt
  T = (M/2) p (Lm/Lr) Im(conj(psi_r) i_s)
Coupling of the two modes: shared inverter voltage and current budget (sum of the two waveforms in every coil), shared rotor speed.
Voltage budget: |v_4| + |v_2| <= V_pk,max (worst-case peak sum).  Current budget: |i_4|^2 + |i_2|^2 <= (sqrt2 I_max)^2.
"""
import json, math, datetime, sys
import numpy as np
import spb_core as c

c.CAP_MODE["mode"] = "an_caps"
VPK = c.SQ2 * c.VMAX
IPK = c.SQ2 * c.IMAX
V = c.VEH
M_EQ = V["mass_kg"] * V["mass_factor"]
G, ETA, RW = V["gear_ratio"], V["eta_gear"], V["wheel_radius_m"]
J_EQ = M_EQ * (RW / G) ** 2
CDA = 0.5 * V["rho_air_kg_m3"] * V["Cd"] * V["frontal_area_m2"]


def road_torque(n_rpm, grade):
    v = n_rpm * c.RPM * RW / G
    a = math.atan(grade)
    F = V["Crr"] * V["mass_kg"] * V["g_m_s2"] * math.cos(a) + CDA * v * v + V["mass_kg"] * V["g_m_s2"] * math.sin(a)
    return F * RW / G / ETA


class Mode:
    def __init__(self, p, psi_ref_ss):
        par = c.im_params(p)
        self.p = p
        im_c, ps_c, _, _ = c.mag_curve(p)
        Lm_sec = psi_ref_ss / np.interp(psi_ref_ss, ps_c, im_c)
        self.Lm = Lm_sec
        self.Ls = Lm_sec + par["Lsig_s"]
        self.Lr = Lm_sec + par["Lsig_r"]
        self.Rs, self.Rr = par["Rs"], par["Rr"]
        self.sig = 1 - Lm_sec ** 2 / (self.Ls * self.Lr)
        self.tau_r = self.Lr / self.Rr


def simulate(T_req, grade, n0=2100.0, t_end=0.5, dt=1e-4, t_d=0.02, t_f4=0.05, t_f2=0.03, tau_i=1e-3, Tc=0.015,
             psi2_scale=1.0, label="", active_demag=True, torque_first=True):
    # steady states before / after
    par4, par2 = c.im_params(4), c.im_params(2)
    T0 = T_req
    ss4 = c.im_loss_point(par4, n0, T0)
    ss2 = c.im_loss_point(par2, n0, T0)
    if ss4 is None or ss2 is None:
        return None
    m4 = Mode(4, ss4["psi"]); m2 = Mode(2, ss2["psi"] * psi2_scale)
    psi4_0, psi2_f = ss4["psi"] * c.SQ2, ss2["psi"] * c.SQ2 * psi2_scale        # amplitude
    # initial steady state phasors (rms -> amplitude), reference: psi_m real
    wsl = ss4["wsl"]
    Ir = -1j * wsl * ss4["psi"] / (par4["Rr"] + 1j * wsl * par4["Lsig_r"])
    im_ = np.interp(ss4["psi"], c.mag_curve(4)[1], c.mag_curve(4)[0])
    Is = im_ - Ir
    i4 = c.SQ2 * Is
    psir4 = c.SQ2 * (ss4["psi"] + par4["Lsig_r"] * Ir) * (m4.Lm / (m4.Lm))  # psi_r = psi_m + Lsig_r*i_r
    # consistent re-derivation with the (secant) dynamic parameters: psi_r = Lr*ir + Lm*is, ir = (psi_m/Lm) - is
    ir = (c.SQ2 * ss4["psi"]) / m4.Lm - i4
    psir4 = m4.Lr * ir + m4.Lm * i4
    i2 = 0j; psir2 = 0j
    Om = n0 * c.RPM
    th = 0.0                                                       # rotor angle (mech); stator-frame phasors rotate with it

    def deriv(state, t, ref):
        i4, psi4, i2, psi2, Om = state
        out = []
        ff = []
        dyn = []
        modes = ((m4, i4, psi4), (m2, i2, psi2))
        ctrl = ref(t)
        dpsi = []
        istar = []
        for (m, i, psi), cm in zip(modes, ctrl):
            wm = m.p * Om
            dp = -(m.Rr / m.Lr) * (psi - m.Lm * i) + 1j * wm * psi
            dpsi.append(dp)
            a = abs(psi)
            if cm["on"]:
                rho = psi / a if a > 1e-6 else 1.0 + 0j
                a = max(a, 2e-3)
                dsd = (a + m.tau_r * (cm["psi_ref"] - a) / Tc) / m.Lm
                dsd = float(np.clip(dsd, -0.9 * IPK, 0.9 * IPK)) if cm["psi_ref"] > 0 or not active_demag else float(np.clip(dsd, 0, 0.9 * IPK))
                isq = cm["T_ref"] / (c.M / 2 * m.p * (m.Lm / m.Lr) * a)
                istar.append((dsd + 1j * isq) * rho)
                wrho = np.imag(np.conj(psi) * dp) / (a * a) if abs(psi) > 2e-3 else 0.0
            else:
                istar.append(0j)
                wrho = 0.0
            ff.append(m.Rs * i + (m.Lm / m.Lr) * dp)
            dyn.append((istar[-1], wrho))
        # current budget (common scaling of the commands)
        mag = math.sqrt(abs(istar[0]) ** 2 + abs(istar[1]) ** 2)
        if mag > IPK:
            sc = IPK / mag
            istar = [x * sc for x in istar]
        dI = []
        vd = []
        for (m, i, psi), (ist, wrho) in zip(modes, dyn):
            ist = istar[0] if m is m4 else istar[1]
            didt = 1j * wrho * ist + (ist - i) / tau_i
            vd.append(m.sig * m.Ls * didt)
            dI.append(didt)
        # voltage budget
        ffm = [abs(x) for x in ff]
        dm = [abs(x) for x in vd]
        Vav = VPK - ffm[0] - ffm[1]
        g, s = 1.0, 1.0
        if Vav < 0:
            g = VPK / (ffm[0] + ffm[1] + 1e-12); s = 0.0
        elif dm[0] + dm[1] > Vav:
            s = Vav / (dm[0] + dm[1])
        di = []
        for k, (m, i, psi) in enumerate(modes):
            vapp = g * ff[k] + s * vd[k]
            di.append((vapp - ff[k]) / (m.sig * m.Ls))
        T4 = c.M / 2 * m4.p * (m4.Lm / m4.Lr) * np.imag(np.conj(psi4) * i4)
        T2 = c.M / 2 * m2.p * (m2.Lm / m2.Lr) * np.imag(np.conj(psi2) * i2)
        Tl = road_torque(Om / c.RPM, grade)
        dOm = (T4 + T2 - Tl) / J_EQ
        return (di[0], dpsi[0], di[1], dpsi[1], dOm), dict(T4=T4, T2=T2, Tl=Tl, v4=abs(g * ff[0] + s * vd[0]), v2=abs(g * ff[1] + s * vd[1]), s=s, g=g)

    def ref(t):
        # mode 4: torque ramps down over t_d, flux ref ramps to 0 over t_f4 (starting at t_d if torque_first else 0)
        r4 = max(0.0, 1.0 - t / t_d)
        t0f = 0.0
        f4 = max(0.0, 1.0 - max(0.0, t - t0f) / t_f4)
        # mode 2: flux ref ramps up over t_f2; torque = remaining demand
        f2 = min(1.0, t / t_f2)
        return ({"on": True, "psi_ref": psi4_0 * f4, "T_ref": T0 * r4},
                {"on": t > 0, "psi_ref": psi2_f * f2, "T_ref": 0.0})

    # mode 2 torque reference: take what mode 4 no longer provides, resolved inside the loop
    nsteps = int(t_end / dt)
    state = (i4, psir4, i2, psir2 + 1e-9, Om)
    log = []
    t = 0.0
    T2req = {"v": 0.0}

    def ref2(t):
        a, b = ref(t)
        return a, b

    for k in range(nsteps):
        # outer: T2 ref = T_req - T4 (mode 4 torque as currently produced)
        a, b = ref(t)
        T4now = c.M / 2 * m4.p * (m4.Lm / m4.Lr) * np.imag(np.conj(state[1]) * state[0])
        b["T_ref"] = max(0.0, T0 - T4now) * (1.0 if abs(state[3]) > 1e-3 else 0.0)

        def rf(tt, a=a, b=b):
            return (a, b)
        k1, d1 = deriv(state, t, rf)
        s2 = tuple(x + 0.5 * dt * y for x, y in zip(state, k1))
        k2, _ = deriv(s2, t + dt / 2, rf)
        s3 = tuple(x + 0.5 * dt * y for x, y in zip(state, k2))
        k3, _ = deriv(s3, t + dt / 2, rf)
        s4 = tuple(x + dt * y for x, y in zip(state, k3))
        k4, _ = deriv(s4, t + dt, rf)
        state = tuple(x + dt / 6 * (p1 + 2 * p2 + 2 * p3 + p4) for x, p1, p2, p3, p4 in zip(state, k1, k2, k3, k4))
        t += dt
        if k % 20 == 0:
            i4s, p4s, i2s, p2s, Oms = state
            log.append((t, d1["T4"], d1["T2"], d1["Tl"], abs(i4s), abs(i2s), abs(p4s), abs(p2s), Oms / c.RPM, d1["v4"], d1["v2"],
                        d1["s"], d1["g"]))
    L = np.array(log)
    t = L[:, 0]; Tt = L[:, 1] + L[:, 2]
    # coil-current peak and sliding rms
    irms = np.sqrt((L[:, 4] ** 2 + L[:, 5] ** 2) / 2)
    ipk_env = L[:, 4] + L[:, 5]
    below = np.where(Tt < 0.9 * T0)[0]
    gap = float(t[below[-1]] - t[below[0]]) if len(below) else 0.0
    # time to recover: last time torque is below 0.95 T0 within the sim
    below95 = np.where(Tt < 0.95 * T0)[0]
    t_rec = float(t[below95[-1]]) if len(below95) else 0.0
    deficit = float(np.trapezoid(np.maximum(T0 - Tt, 0), t))
    n_min = float(L[:, 8].min())
    v_kmh0 = n0 * c.RPM * RW / G * 3.6
    res = dict(label=label, grade_pct=grade * 100, T_req_Nm=T0, n0_rpm=n0, params=dict(t_d=t_d, t_f4=t_f4, t_f2=t_f2, Tc=Tc),
               torque_min_Nm=float(Tt.min()), torque_gap_below90pct_s=gap, t_recover95_s=t_rec,
               torque_deficit_Nms=deficit, speed_drop_rpm=float(n0 - n_min), speed_drop_kmh=float((n0 - n_min) * c.RPM * RW / G * 3.6),
               speed_drop_kmh_deficit_estimate=float(deficit / J_EQ * RW / G * 3.6),
               I_rms_peak_A=float(irms.max()), I_rms_peak_over_Imax=float(irms.max() / c.IMAX), I_rms_final_A=float(irms[-1]),
               I_peak_sum_env_A=float(ipk_env.max()), I_peak_limit_A=float(IPK),
               psi4_end_Wb=float(L[-1, 6] / c.SQ2), psi2_end_Wb=float(L[-1, 7] / c.SQ2), psi2_target_Wb=float(psi2_f / c.SQ2),
               v_pk_max_V=float((L[:, 9] + L[:, 10]).max()), v_pk_limit_V=VPK, v_limited_fraction_of_time=float(np.mean((L[:, 11] < 0.999) | (L[:, 12] < 0.999))),
               ss_before=dict(psi=ss4["psi"], I=ss4["I"], V=ss4["V"]), ss_after=dict(psi=ss2["psi"], I=ss2["I"], V=ss2["V"]))
    series = dict(t=t.tolist(), T4=L[:, 1].tolist(), T2=L[:, 2].tolist(), T_load=L[:, 3].tolist(), I4_pk=L[:, 4].tolist(), I2_pk=L[:, 5].tolist(),
                  psi4=(L[:, 6] / c.SQ2).tolist(), psi2=(L[:, 7] / c.SQ2).tolist(), n_rpm=L[:, 8].tolist(), I_rms=irms.tolist())
    return res, series


if __name__ == "__main__":
    out = {"cases": []}
    series_all = {}
    for grade in (0.0, 0.02):
        Tld = road_torque(2100.0, grade)
        print("grade", grade, "road-load torque at 2100 rpm", round(Tld, 1))
        for (t_d, t_f4, t_f2) in ((0.01, 0.03, 0.03), (0.02, 0.05, 0.05), (0.05, 0.1, 0.08), (0.01, 0.01, 0.01)):
            r = simulate(Tld, grade, t_d=t_d, t_f4=t_f4, t_f2=t_f2, label=f"handover td={t_d} tf4={t_f4} tf2={t_f2}")
            if r is None:
                print("not feasible"); continue
            res, ser = r
            out["cases"].append(res); series_all[f"g{grade}_{t_d}_{t_f4}_{t_f2}"] = ser
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items() if k not in ("params", "ss_before", "ss_after")})
    meta = dict(script="03_simulation/run_im_transition.py", task="T04 item 3a", date=str(datetime.date.today()),
                note="Two-mode (p=4, p=2) rotor-flux-oriented model; ideal current loops tau_i = 1 ms; secant L_m at the target flux; flux caps = analyst caps (an_caps).")
    json.dump(dict(meta=meta, **out), open("results/im_pole_transition.json", "w"), indent=1, default=float)
    np.savez("scratch/im_transition_series.npz", **{k + "__" + kk: np.array(vv) for k, v in series_all.items() for kk, vv in v.items()})

"""H10 confirmation with the nonlinear MEC ("MEC replay").

1. Currents of the two spatial modes come from the two-mode IM time-domain model (run_im_transition.simulate: overlapped or sequential handover),
   or from an ideal prescribed crossfade of two steady states.
2. Magnetising current of each mode i_m = i_s + i_r' (the MMF the iron sees).  Coil magnetising currents i_mag,k = sum_m Re[i_m e^{-j p_m k tau}] are
   fed to the nonlinear MEC (spb_core.mec_solve, smooth rotor, B-H iron) at every sample -> coil air-gap flux linkages psi_k(t) incl. cross saturation
   between the two orders (shared iron).  Cage reaction to saturation-generated orders is NOT included (upper bound for the combination orders).
3. v_k = R_s i_k + sum_m L_sigma,s(p_m) d i_m/dt + d psi_k/dt;  cell power P_j(t) = sum over the coils of module j of v_k i_k.
4. dP_j = P_j - mean_j P_j (removes the common mean power); sliding demodulation (window 1/70 s) at the product frequencies.
Run with SPB_Q=48 (3-leg modules) or SPB_Q=80 (5-leg modules, same pu machine, y = 11)."""
import os, sys, json, math, datetime, itertools
import numpy as np
import spb_core as c
import run_im_transition as r

c.CAP_MODE["mode"] = "an_caps"
Q = c.Q
MM = Q // 16
NMOD = 16
V0 = 75.0
TAU = c.TAU
ALPHA = np.arange(Q) * TAU
NS_STEP = 4                      # 0.4 ms replay sample


def modal(k_vals, p):
    return 2.0 / Q * (k_vals * np.exp(1j * p * ALPHA)).sum(axis=-1)


def coil_vals(zc, p):
    return np.real(zc[:, None] * np.exp(-1j * p * ALPHA)[None, :])


def demod(t, p, f, win):
    dt = t[1] - t[0]
    n = max(int(round(win / dt)), 2)
    z = p * np.exp(-2j * math.pi * f * t)
    cs = np.cumsum(np.concatenate([[0], z]))
    return 2 * np.abs((cs[n:] - cs[:-n]) / n)


def cell_power(v, i, t):
    P = np.zeros((len(t), NMOD))
    for j in range(NMOD):
        ks = [j + 16 * ii for ii in range(MM)]
        P[:, j] = (v[:, ks] * i[:, ks]).sum(axis=1)
    return P


def analyze(t, i4, i2, im4, im2, v4lin, v2lin, Mo, x_defs, f_sum, tag, extra):
    dt = t[1] - t[0]
    imag = coil_vals(im4, 4) + coil_vals(im2, 2)
    isc = coil_vals(i4, 4) + coil_vals(i2, 2)
    psi = np.zeros((len(t), Q)); U = None
    BT = np.zeros(len(t)); BY = np.zeros(len(t))
    for n in range(len(t)):
        rr = c.mec_solve(imag[n], c.rotor_smooth(), U)
        U = rr["U"]; psi[n] = rr["psi"]; BT[n] = rr["Bt"].max(); BY[n] = rr["By"].max()
    dpsi = np.gradient(psi, dt, axis=0)
    vleak = coil_vals(Mo["Lsig_s4"] * np.gradient(i4, dt), 4) + coil_vals(Mo["Lsig_s2"] * np.gradient(i2, dt), 2)
    vc = Mo["Rs"] * isc + vleak + dpsi
    vlin = coil_vals(v4lin, 4) + coil_vals(v2lin, 2)
    vm = {p: modal(vc, p) for p in (4, 2)}
    rel = {p: float(np.sqrt(np.mean(np.abs(vm[p] - (v4lin if p == 4 else v2lin)) ** 2)) / max(np.sqrt(np.mean(np.abs(v4lin if p == 4 else v2lin) ** 2)), 1e-9)) for p in (4, 2)}
    # spatial orders of d(psi)/dt other than the two drive orders: peak flux-derivative amplitude per order (V per coil, amplitude)
    orders = {}
    for p in range(1, 13):
        if Q == 48 and p % 3 == 0:
            continue
        if Q == 80 and p % 5 == 0:
            continue
        orders[p] = float(np.abs(modal(dpsi, p)).max())
    out = dict(tag=tag, Q=Q, m=MM, B_tooth_peak_max_T=float(BT.max()), B_yoke_peak_max_T=float(BY.max()), vmec_vs_vlin_rel_rms=rel, dpsi_order_peaks_V=orders, **extra)
    win = 1 / 70.0
    freqs = [70.0 * n for n in range(1, 9)]
    for name, v in (("mec", vc), ("lin", vlin)):
        P = cell_power(v, isc, t)
        dP = P - P.mean(axis=1, keepdims=True)
        amps, env = {}, {}
        for f in freqs + [f_sum]:
            A = np.max([demod(t, dP[:, j], f, win) for j in range(NMOD)], axis=0)
            amps[f] = float(A.max()); env[f] = A
        # peak per-cell pulsation: the largest of the line amplitudes; C from the worst-case sum of the spectral lines (exclude the f_sum duplicate)
        lines = {f: a for f, a in amps.items() if f in freqs}
        pk = max(amps.values()); fmain = max(amps, key=amps.get)
        Csum = sum(a / (V0 * 2 * math.pi * f) for f, a in lines.items())
        Cmain = amps[fmain] / (V0 * 2 * math.pi * fmain)
        out[name] = dict(mean_cell_power_W=float(P.mean()), pulsation_peak_W=pk, pulsation_main_Hz=fmain, amp_by_freq_W={f"{f:.0f}": a for f, a in amps.items()},
                         C_for_pm5pct_mF=float(Cmain / (0.05 * V0) * 1e3), C_for_pm10pct_mF=float(Cmain / (0.10 * V0) * 1e3),
                         C_all_lines_for_pm5pct_mF=float(Csum / (0.05 * V0) * 1e3), C_all_lines_for_pm10pct_mF=float(Csum / (0.10 * V0) * 1e3),
                         pulsation_over_mean=float(pk / max(abs(P.mean()), 1.0)))
        for C in (1.0e-3, 2.88e-3):
            vv = V0 - np.cumsum(dP, axis=0) * dt / (C * V0)
            w = int(round(0.01 / dt))
            rip = max(float((vv[k:k + w].max(axis=0) - vv[k:k + w].min(axis=0)).max()) for k in range(0, len(t) - w, w))
            slow = np.array([vv[k:k + w].mean(axis=0) for k in range(0, len(t) - w, w)])
            out[name][f"C_{C*1e3:.2f}mF"] = dict(ripple_pp_V=rip, v_min_V=float(vv.min()), v_max_V=float(vv.max()), slow_drift_max_V=float(np.abs(slow - V0).max()))
        if name == "mec":
            envs = env[f_sum]
            h = int(round(win / dt / 2))
            fits = {}
            for xn, xv in x_defs.items():
                xs = xv[h: h + len(envs)]
                sel = (xs > 0.02) & (xs < 0.98)
                if sel.sum() > 10:
                    w_ = xs[sel] * (1 - xs[sel]); a_ = envs[sel]
                    kap = float(np.dot(a_, w_) / np.dot(w_, w_))
                    fits[xn] = dict(kappa_W=kap, R2=float(1 - np.sum((a_ - kap * w_) ** 2) / max(np.sum((a_ - a_.mean()) ** 2), 1e-9)),
                                    peak_A_W=float(a_.max()), x_at_peak=float(xs[sel][np.argmax(a_)]), kappa_over_4=kap / 4.0)
            out["crossfade_fit"] = fits
            out["crossfade_trace"] = dict(t_s=t[h:h + len(envs)][::8].tolist(), A_W=envs[::8].tolist(), **{f"x_{k}": v[h:h + len(envs)][::8].tolist() for k, v in x_defs.items()})
            # analytic kernel check: amplitude = 1.5 |v4 i2 + v2 i4| (m = 3, sum-frequency term) using the MEC modal voltages
            if MM == 3:
                kern = 1.5 * np.abs(vm[4] * i2 + vm[2] * i4)
                out["kernel_check"] = dict(max_W=float(kern.max()), measured_max_W=amps[f_sum], ratio=float(amps[f_sum] / max(kern.max(), 1e-9)))
            comp = {}
            vmod = {p: coil_vals(vm[p], p) for p in (4, 2)}
            imod = {4: coil_vals(i4, 4), 2: coil_vals(i2, 2)}
            for a_, b_ in ((4, 2), (2, 4)):
                Pab = cell_power(vmod[a_], imod[b_], t)
                dPab = Pab - Pab.mean(axis=1, keepdims=True)
                comp[f"v_p{a_}_x_i_p{b_}"] = float(max(np.max([demod(t, dPab[:, j], f, win).max() for j in range(NMOD)]) for f in freqs + [f_sum]))
            out["product_terms_peak_W"] = comp
    return out


def replay(grade, params, seq=None, tag="", t_end=1.3, n0=2100.0, h11s=None):
    Tld = r.road_torque(n0, grade)
    kw = dict(t_end=t_end, dt=1e-4, full_log=True, **params)
    if seq is not None:
        kw["seq_eps"] = seq
    if h11s is not None:
        kw["h11s"] = h11s
    res, ser = r.simulate(Tld, grade, **kw)
    Mo = ser["modes"]
    cp = ser["cplx"][::NS_STEP]
    t = np.array([x[0] for x in cp]); i4 = np.array([x[1] for x in cp]); i2 = np.array([x[2] for x in cp])
    v4 = np.array([x[3] for x in cp]); v2 = np.array([x[4] for x in cp]); p4 = np.array([x[5] for x in cp]); p2 = np.array([x[6] for x in cp])
    im4 = i4 + (p4 - Mo["Lm4"] * i4) / Mo["Lr4"]; im2 = i2 + (p2 - Mo["Lm2"] * i2) / Mo["Lr2"]
    T4 = c.M / 2 * 4 * (Mo["Lm4"] / Mo["Lr4"]) * np.imag(np.conj(p4) * i4); T2 = c.M / 2 * 2 * (Mo["Lm2"] / Mo["Lr2"]) * np.imag(np.conj(p2) * i2)
    x_t = T2 / np.maximum(np.abs(T4) + np.abs(T2), 1e-6)
    x_f = np.abs(p2) / np.maximum(np.abs(p2) + np.abs(p4), 1e-9)
    x_i = np.abs(i2) / np.maximum(np.abs(i2) + np.abs(i4), 1e-9)
    f_sum = (np.angle(i4[1:] * np.conj(i4[:-1])).mean() + np.angle(i2[1:] * np.conj(i2[:-1])).mean()) / (t[1] - t[0]) / (2 * math.pi)
    f_sum = 210.0 if abs(f_sum - 210.0) > 15 else 210.0
    extra = dict(grade_pct=grade * 100, params=params, seq_eps=seq, torque_min_over_request=res["torque_min_Nm"] / res["T_req_Nm"],
                 dq_result={k: res[k] for k in ("torque_min_Nm", "T_req_Nm", "torque_gap_below90pct_s", "t_recover95_s", "speed_drop_kmh", "I_rms_peak_over_Imax", "torque_deficit_Nms")},
                 trigger_t=Mo["trigger_t"], psi_r4_residual_at_end_over_start=float(abs(p4[-1]) / abs(p4[0])))
    out = analyze(t, i4, i2, im4, im2, v4, v2, Mo, dict(torque=x_t, flux=x_f, current=x_i), f_sum, tag, extra)
    return out


def ideal_crossfade(law, n0=2100.0, grade=0.0, Tx=0.3):
    """ideal crossfade of the two loss-optimal steady states at the same torque: amplitudes scale with a(x), b(x)."""
    Tld = r.road_torque(n0, grade)
    par4, par2 = c.im_params(4), c.im_params(2)
    ss4 = c.im_loss_point(par4, n0, Tld); ss2 = c.im_loss_point(par2, n0, Tld)
    Om = n0 * c.RPM

    def phasors(par, ss, p):
        wsl = ss["wsl"]; psi = ss["psi"]
        imc = float(np.interp(psi, c.mag_curve(p)[1], c.mag_curve(p)[0]))
        Ir = -1j * wsl * psi / (par["Rr"] + 1j * wsl * par["Lsig_r"])
        Is = imc - Ir
        we = p * Om + wsl
        return c.SQ2 * Is, c.SQ2 * imc, we, par
    Is4, Im4, w4, _ = phasors(par4, ss4, 4); Is2, Im2, w2, _ = phasors(par2, ss2, 2)
    dt = 1e-4 * NS_STEP
    t = np.arange(0, 0.1 + Tx + 0.1, dt)
    x = np.clip((t - 0.1) / Tx, 0, 1)
    if law == "linear_amplitude":
        a, b = 1 - x, x                       # psi and i of each mode scale linearly: cross product ~ x(1-x)
    elif law == "constant_torque":
        a, b = np.sqrt(1 - x), np.sqrt(x)     # torque ~ psi*i ~ a^2, b^2: torque shares add up to the request
    else:
        raise ValueError(law)
    ph4 = np.exp(1j * w4 * t); ph2 = np.exp(1j * w2 * t)
    i4 = a * Is4 * ph4; i2 = b * Is2 * ph2; im4 = a * Im4 * ph4; im2 = b * Im2 * ph2
    Mo = dict(Rs=par4["Rs"], Lsig_s4=par4["Lsig_s"], Lsig_s2=par2["Lsig_s"])
    # linear-model terminal voltages: R i + L_sigma di/dt + j w L_m(sec) i_m
    Lm4 = ss4["psi"] * c.SQ2 / Im4; Lm2 = ss2["psi"] * c.SQ2 / Im2
    v4 = par4["Rs"] * i4 + 1j * w4 * par4["Lsig_s"] * i4 + 1j * w4 * Lm4 * im4
    v2 = par2["Rs"] * i2 + 1j * w2 * par2["Lsig_s"] * i2 + 1j * w2 * Lm2 * im2
    f_sum = (w4 + w2) / 2 / math.pi
    extra = dict(law=law, Tx_s=Tx, f_sum_Hz=f_sum, steady_amps=dict(I4_A=float(abs(Is4)), I2_A=float(abs(Is2)), psi4_Wb=float(ss4["psi"]), psi2_Wb=float(ss2["psi"])))
    return analyze(t, i4, i2, im4, im2, v4, v2, Mo, dict(share=x), f_sum, f"ideal_{law}", extra)


def brief(o):
    s = f'{o["tag"]}: MEC pulsation {o["mec"]["pulsation_peak_W"]:.0f} W @{o["mec"]["pulsation_main_Hz"]:.0f} Hz (lin {o["lin"]["pulsation_peak_W"]:.0f}), ' \
        f'C(+-5%) {o["mec"]["C_for_pm5pct_mF"]:.1f} mF, C(+-10%) {o["mec"]["C_for_pm10pct_mF"]:.1f} mF; vMEC/vlin {o["vmec_vs_vlin_rel_rms"]}'
    if "torque_min_over_request" in o:
        s += f' | Tmin/Treq {o["torque_min_over_request"]:.2f} gap90 {o["dq_result"]["torque_gap_below90pct_s"]:.3f}s'
    if "product_terms_peak_W" in o:
        s += " | terms " + str({k: round(v) for k, v in o["product_terms_peak_W"].items()})
    if "crossfade_fit" in o:
        s += " | fit " + str({k: (round(v["kappa_over_4"]), round(v["R2"], 2), round(v["peak_A_W"])) for k, v in o["crossfade_fit"].items()})
    if "kernel_check" in o:
        s += f' | kernel {o["kernel_check"]["ratio"]:.2f}'
    return s


if __name__ == "__main__":
    sch = json.load(open(f"results/h10_schedule_search_Q{Q}.json"))
    p_flat = sch["grade_0pct"][0]["params"]; p_2 = sch["grade_2pct"][0]["params"]
    RES = dict(meta=dict(script="03_simulation/run_h10_mec.py", task="H10 confirmation (nonlinear MEC)", date=str(datetime.date.today()), Q=Q, coils_per_module=MM,
                         geometry="agreed (data/machine_geometry.json)" + ("" if Q == 48 else "; Q=80, y=11, slot and conductor width x 48/80, coil current x 48/80"),
                         schedules=dict(flat=p_flat, grade2=p_2), note="cage reaction to saturation-generated orders neglected (upper bound for the combination-order pulsation); controller includes active demagnetisation (fixed 2026-11-02)"), cases=[])
    outf = f"results/confirm_H10_mec_Q{Q}.json"
    def save(o):
        RES["cases"].append(o); print(brief(o), flush=True); json.dump(RES, open(outf, "w"), indent=1, default=float)
    for grade, p in ((0.0, p_flat), (0.02, p_2)):
        save(replay(grade, p, None, tag=f"overlapped_{grade*100:.0f}pct"))
    for law in ("linear_amplitude", "constant_torque"):
        save(ideal_crossfade(law))
    if Q == 48:
        for grade in (0.0, 0.02):
            for eps in (0.02, 0.05, 0.15, 0.30):
                save(replay(grade, dict(t_d=0.02, t_f4=0.05, t_f2=0.1), eps, tag=f"sequential_{grade*100:.0f}pct_eps{eps}"))
            for C in (1.0e-3, 2.88e-3):
                Pall = 0.10 * V0 * 2 * math.pi * 210.0 * C * V0
                save(replay(grade, dict(t_d=0.02, t_f4=0.01, t_f2=0.01), None, tag=f"H11s_{grade*100:.0f}pct_C{C*1e3:.2f}mF", t_end=0.7, h11s=dict(eps=0.02, gate=0.05, P_allow=Pall)))

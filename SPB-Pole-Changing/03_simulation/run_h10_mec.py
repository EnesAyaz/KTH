"""H10 confirmation with the nonlinear MEC ("MEC replay").

1. The two-mode IM time-domain model (run_im_transition.simulate) gives the stator currents i_s,m(t) and rotor fluxes of the two spatial modes.
2. Magnetising current of each mode i_m = i_s + i_r' (the MMF the iron sees).  The coil magnetising currents  i_mag,k = sum_m Re[i_m e^{-j p_m k tau}]
   are fed to the nonlinear MEC (spb_core.mec_solve, smooth rotor, B-H iron) at every sample -> coil air-gap flux linkages psi_k(t) including cross
   saturation between the two orders (iron shared by both).  The cage reaction to saturation-generated orders is NOT included (upper bound).
3. Coil voltages v_k = R_s i_k + sum_m L_sigma,s(p_m) d i_m/dt + d psi_k/dt;  cell power P_j(t) = sum over the m coils of module j of v_k i_k.
4. Pulsation is read from dP_j = P_j - mean_j P_j (removes the common-mode mean power) by sliding demodulation (window 1/70 s) at multiples of 70 Hz.
Run with SPB_Q=48 (3-leg modules, 16 x 3 coils) or SPB_Q=80 (5-leg modules, 16 x 5 coils, same pu machine, y = 11)."""
import os, sys, json, math, datetime, itertools
import numpy as np
import spb_core as c
import run_im_transition as r

c.CAP_MODE["mode"] = "an_caps"
Q = c.Q
MM = Q // 16                      # coils per module (= phases per module m)
NMOD = 16
V0 = 75.0
TAU = c.TAU
ALPHA = np.arange(Q) * TAU
NS_STEP = 2                       # replay sample = NS_STEP * dt = 0.2 ms


def modal(k_vals, p):
    """spatial projection of a per-coil quantity onto order p (complex amplitude, same convention as the dq model)"""
    return 2.0 / Q * (k_vals * np.exp(1j * p * ALPHA)).sum(axis=-1)


def coil_vals(zc, p):
    """per-coil values of complex-amplitude mode quantity zc(t) (N,) -> (N, Q)"""
    return np.real(zc[:, None] * np.exp(-1j * p * ALPHA)[None, :])


def run_dq(grade, params, seq=None, t_end=1.3, n0=2100.0):
    Tld = r.road_torque(n0, grade)
    kw = dict(t_end=t_end, dt=1e-4, full_log=True, **params)
    if seq is not None:
        kw["seq_eps"] = seq
    res, ser = r.simulate(Tld, grade, **kw)
    cp = ser["cplx"][::NS_STEP]
    return res, ser, dict(t=np.array([x[0] for x in cp]), i4=np.array([x[1] for x in cp]), i2=np.array([x[2] for x in cp]),
                          v4=np.array([x[3] for x in cp]), v2=np.array([x[4] for x in cp]), psr4=np.array([x[5] for x in cp]), psr2=np.array([x[6] for x in cp])), ser["modes"]


def demod(t, p, f, win):
    dt = t[1] - t[0]
    n = max(int(round(win / dt)), 2)
    z = p * np.exp(-2j * math.pi * f * t)
    cs = np.cumsum(np.concatenate([[0], z]))
    return 2 * np.abs((cs[n:] - cs[:-n]) / n)


def replay(grade, params, seq=None, tag=""):
    res, ser, S, Mo = run_dq(grade, params, seq)
    t = S["t"]; dt = t[1] - t[0]
    Lm4, Lr4, Lm2, Lr2 = Mo["Lm4"], Mo["Lr4"], Mo["Lm2"], Mo["Lr2"]
    im4 = S["i4"] + (S["psr4"] - Lm4 * S["i4"]) / Lr4
    im2 = S["i2"] + (S["psr2"] - Lm2 * S["i2"]) / Lr2
    imag = coil_vals(im4, 4) + coil_vals(im2, 2)                  # (N, Q) coil magnetising currents
    isc = coil_vals(S["i4"], 4) + coil_vals(S["i2"], 2)           # terminal currents
    psi = np.zeros((len(t), Q)); U = None
    BT = np.zeros(len(t)); BY = np.zeros(len(t))
    for n in range(len(t)):
        rr = c.mec_solve(imag[n], c.rotor_smooth(), U)
        U = rr["U"]; psi[n] = rr["psi"]; BT[n] = rr["Bt"].max(); BY[n] = rr["By"].max()
    dpsi = np.gradient(psi, dt, axis=0)
    di4 = np.gradient(S["i4"], dt); di2 = np.gradient(S["i2"], dt)
    vleak = coil_vals(Mo["Lsig_s4"] * di4, 4) + coil_vals(Mo["Lsig_s2"] * di2, 2)
    vc = Mo["Rs"] * isc + vleak + dpsi                              # (N, Q) coil terminal voltages
    # linear-model voltage for comparison (what run_h10.py used)
    vlin = coil_vals(S["v4"], 4) + coil_vals(S["v2"], 2)
    # modal projections of the MEC voltage
    vm = {p: modal(vc, p) for p in (4, 2)}
    cmp_ = {p: float(np.sqrt(np.mean(np.abs(vm[p] - (S["v4"] if p == 4 else S["v2"])) ** 2)) / max(np.sqrt(np.mean(np.abs(S["v4" if p == 4 else "v2"]) ** 2)), 1e-9)) for p in (4, 2)}
    # spatial spectrum of the MEC flux linkage derivative (orders present besides 4 and 2)
    spec = {}
    for p in range(1, 13):
        if p % 3 == 0 and Q == 48:
            continue
        z = modal(dpsi, p)
        spec[p] = float(np.abs(z).max())
    # modes, torque share
    def torque(p, Lm, Lr, psr, i):
        return c.M / 2 * p * (Lm / Lr) * np.imag(np.conj(psr) * i)
    T4 = torque(4, Lm4, Lr4, S["psr4"], S["i4"]); T2 = torque(2, Lm2, Lr2, S["psr2"], S["i2"])
    x = T2 / np.maximum(np.abs(T4) + np.abs(T2), 1e-6)
    out = dict(tag=tag, Q=Q, m=MM, grade_pct=grade * 100, params=params, seq_eps=seq, dq_result={k: res[k] for k in ("torque_min_Nm", "T_req_Nm", "torque_gap_below90pct_s", "t_recover95_s", "speed_drop_kmh", "I_rms_peak_over_Imax")},
               vmec_vs_vdq_rel_rms=cmp_, B_tooth_peak_max_T=float(BT.max()), B_yoke_peak_max_T=float(BY.max()), dpsi_order_peaks_Vs=spec, trigger_t=Mo["trigger_t"])
    out["torque_min_over_request"] = res["torque_min_Nm"] / res["T_req_Nm"]

    def cell_power(v, i):
        P = np.zeros((len(t), NMOD))
        for j in range(NMOD):
            ks = [j + 16 * ii for ii in range(MM)]
            P[:, j] = (v[:, ks] * i[:, ks]).sum(axis=1)
        return P

    freqs = [70.0 * n for n in range(1, 9)]
    win = 1 / 70.0
    for name, v in (("mec", vc), ("lin", vlin)):
        P = cell_power(v, isc)
        dP = P - P.mean(axis=1, keepdims=True)
        amps = {}
        tw = t[: len(t) - int(round(win / dt))]
        env = {}
        for f in freqs:
            A = np.max([demod(t, dP[:, j], f, win) for j in range(NMOD)], axis=0)    # envelope vs time (max over cells)
            amps[f] = float(A.max()); env[f] = A
        pk = max(amps.values()); fmain = max(amps, key=amps.get)
        # worst-case capacitor ripple: sum over frequencies of A_f / (V0 w_f C) <= dV  ->  C = sum A_f/(V0 w_f dV)
        Csum = sum(a / (V0 * 2 * math.pi * f) for f, a in amps.items())
        out[name] = dict(mean_cell_power_W=float(P.mean()), pulsation_peak_W=pk, pulsation_main_Hz=fmain, amp_by_freq_W={f"{f:.0f}": a for f, a in amps.items()},
                         C_for_pm5pct_mF=float(Csum / (0.05 * V0) * 1e3), C_for_pm10pct_mF=float(Csum / (0.10 * V0) * 1e3),
                         pulsation_over_mean=float(pk / max(abs(P.mean()), 1.0)))
        # open-loop cell voltage (linearised) for two capacitor sizes
        for C in (1.0e-3, 2.88e-3):
            vv = V0 - np.cumsum(dP, axis=0) * dt / (C * V0)
            w = int(round(0.01 / dt))
            rip = max(float((vv[k:k + w].max(axis=0) - vv[k:k + w].min(axis=0)).max()) for k in range(0, len(t) - w, w))
            slow = np.array([vv[k:k + w].mean(axis=0) for k in range(0, len(t) - w, w)])
            out[name][f"C_{C*1e3:.2f}mF"] = dict(ripple_pp_V=rip, v_min_V=float(vv.min()), v_max_V=float(vv.max()), slow_drift_max_V=float(np.abs(slow - V0).max()))
        if name == "mec":
            env210 = env[210.0]
            xs = x[: len(env210)] if False else x[int(round(win / dt / 2)): int(round(win / dt / 2)) + len(env210)]
            out["crossfade"] = dict(t_s=tw[: len(env210)][::10].tolist(), x_mode2_share=xs[::10].tolist(), A210_W=env210[::10].tolist())
            sel = (xs > 0.02) & (xs < 0.98)
            if sel.sum() > 10:
                xv, av = xs[sel], env210[sel]
                kap = float(np.dot(av, xv * (1 - xv)) / np.dot(xv * (1 - xv), xv * (1 - xv)))
                pred = kap * xv * (1 - xv)
                out["crossfade"]["kappa_W"] = kap
                out["crossfade"]["R2_vs_x1mx"] = float(1 - np.sum((av - pred) ** 2) / np.sum((av - av.mean()) ** 2))
                out["crossfade"]["peak_A210_W"] = float(av.max()); out["crossfade"]["x_at_peak"] = float(xv[np.argmax(av)])
        # decomposition into products of modes (m3: only (4+2)=6 divisible by 3 survives; m5: none)
        if name == "mec":
            comp = {}
            vmod = {p: coil_vals(vm[p], p) for p in (4, 2)}
            imod = {4: coil_vals(S["i4"], 4), 2: coil_vals(S["i2"], 2)}
            for a_, b_ in ((4, 2), (2, 4), (4, 4), (2, 2)):
                Pab = cell_power(vmod[a_], imod[b_])
                dPab = Pab - Pab.mean(axis=1, keepdims=True)
                comp[f"v_p{a_}_x_i_p{b_}"] = float(max(np.max([demod(t, dPab[:, j], f, win).max() for j in range(NMOD)]) for f in freqs))
            out["product_terms_peak_W"] = comp
            # residual of the order-4 (8-pole) rotor flux during the sequential handover: EMF of residual flux against i_p2
            out["psi_r4_end_over_start"] = float(np.abs(S["psr4"][-1]) / np.abs(S["psr4"][0]))
    return out


if __name__ == "__main__":
    best = json.load(open("results/confirm_H10_handover_agreed.json"))
    p_flat = best["flat_schedule_search"][0]["params"]
    p_2 = dict(t_d=0.02, t_f4=0.15, t_f2=0.15)
    RES = dict(meta=dict(script="03_simulation/run_h10_mec.py", task="H10 confirmation (nonlinear MEC)", date=str(datetime.date.today()), Q=Q, coils_per_module=MM,
                         geometry="agreed (data/machine_geometry.json)" + ("" if Q == 48 else "; Q=80, y=11, slot width and conductor width scaled by 48/80, coil current x 48/80"),
                         note="cage reaction to saturation-generated orders neglected (upper bound for the combination-order pulsation)"), cases=[])
    jobs = []
    for grade, p in ((0.0, p_flat), (0.02, p_2)):
        jobs.append(("overlapped", grade, p, None))
    if Q == 48:
        for grade in (0.0, 0.02):
            for eps in (0.05, 0.15, 0.30):
                jobs.append((f"sequential_eps{eps}", grade, dict(t_d=0.02, t_f4=0.05, t_f2=0.1), eps))
    for tag, grade, p, eps in jobs:
        o = replay(grade, p, eps, tag=tag)
        RES["cases"].append(o)
        print(tag, f"grade {grade*100:.0f}%", "Tmin/Treq %.2f" % o["torque_min_over_request"], "gap %.3f" % o["dq_result"]["torque_gap_below90pct_s"],
              "| MEC: pulsation %.0f W @%.0f Hz, C(+-5%%) %.1f mF, C(+-10%%) %.1f mF" % (o["mec"]["pulsation_peak_W"], o["mec"]["pulsation_main_Hz"], o["mec"]["C_for_pm5pct_mF"], o["mec"]["C_for_pm10pct_mF"]),
              "| lin: %.0f W" % o["lin"]["pulsation_peak_W"], "| vMEC/vdq", {k: round(v, 3) for k, v in o["vmec_vs_vdq_rel_rms"].items()},
              "| terms", {k: round(v) for k, v in o["product_terms_peak_W"].items()}, "| xfade", {k: round(v, 3) for k, v in o.get("crossfade", {}).items() if isinstance(v, float)}, flush=True)
        json.dump(RES, open(f"results/confirm_H10_mec_Q{Q}.json", "w"), indent=1, default=float)

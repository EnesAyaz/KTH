"""Independent confirmation of the H10 claim (series-stack cell power pulsation during overlapped pole handover).
Own equations: coil currents/voltages are rebuilt from the two-mode IM time-domain model (run_im_transition.simulate), the cell power is
P_j(t) = sum over the coils of module j of v_k(t) i_k(t) (isolated neutral: the star load power is the sum of the phase powers), and each cell has
C dv_j/dt = I_s - P_j/v_j with the stack current fixed by the stiff link  (sum_j v_j = 1200 V  =>  I_s = mean_j P_j/v_j)."""
import json, math, itertools, datetime, os
import numpy as np
import spb_core as c
import run_im_transition as r

c.CAP_MODE["mode"] = "an_caps"
NMOD = 16
VCELL = 75.0


def cell_power(cplx, Q, m, iscale=1.0, orders=(4, 2)):
    """P_j(t) for the 16 modules; module j has coils j + 16*i, i = 0..m-1 (Q = 16*m coils)."""
    t = np.array([x[0] for x in cplx])
    i4 = np.array([x[1] for x in cplx]) * iscale; i2 = np.array([x[2] for x in cplx]) * iscale
    v4 = np.array([x[3] for x in cplx]); v2 = np.array([x[4] for x in cplx])
    P = np.zeros((len(t), NMOD))
    for j in range(NMOD):
        for ii in range(m):
            k = j + 16 * ii
            a4 = orders[0] * 2 * math.pi * k / Q; a2 = orders[1] * 2 * math.pi * k / Q
            vk = np.real(v4 * np.exp(-1j * a4)) + np.real(v2 * np.exp(-1j * a2))
            ik = np.real(i4 * np.exp(-1j * a4)) + np.real(i2 * np.exp(-1j * a2))
            P[:, j] += vk * ik
    return t, P


def demod(t, p, f, win):
    """amplitude of the component of p at frequency f, sliding window `win` seconds"""
    dt = t[1] - t[0]
    n = int(win / dt)
    z = p * np.exp(-2j * math.pi * f * t)
    cs = np.cumsum(np.concatenate([[0], z]))
    a = (cs[n:] - cs[:-n]) / n
    return 2 * np.abs(a)


def dc_side(t, P, C, v0=VCELL):
    """linearised cell voltage (constant-power load is open-loop unstable without a balancing loop, so the open-loop law is linearised about V0):
    C dv_j/dt = (Pbar - P_j)/V0, Pbar = mean_j P_j (stiff 1200 V link fixes the stack current)."""
    dt = t[1] - t[0]
    dP = P - P.mean(axis=1, keepdims=True)
    v = v0 - np.cumsum(dP, axis=0) * dt / (C * v0)
    return v


def stats(t, P, Q, label, f_pulse, Cs=(1.0e-3, 2.88e-3)):
    res = dict(label=label, mean_cell_power_W=float(P.mean()), peak_cell_power_W=float(P.max()))
    amps = {}
    for f in f_pulse:
        A = max(demod(t, P[:, j], f, 1 / 35.0).max() for j in range(0, NMOD, 3))
        amps[f] = float(A)
        res[f"pulsation_amp_W_at_{f:.0f}Hz"] = float(A)
    res["pulsation_amp_max_W"] = max(amps.values())
    f_main = max(amps, key=amps.get)
    res["pulsation_main_Hz"] = f_main
    res["pulsation_over_mean_cell_power"] = res["pulsation_amp_max_W"] / max(abs(res["mean_cell_power_W"]), 1.0)
    res["C_required_for_5V_pk_ripple_mF"] = res["pulsation_amp_max_W"] / (VCELL * 2 * math.pi * f_main * 5.0) * 1e3
    for C in Cs:
        v = dc_side(t, P, C)
        w = int(0.01 / (t[1] - t[0]))
        rip = max(float((v[k:k + w].max(axis=0) - v[k:k + w].min(axis=0)).max()) for k in range(0, len(t) - w, w))
        slow = np.array([v[k:k + w].mean(axis=0) for k in range(0, len(t) - w, w)])
        res[f"C_{C*1e3:.2f}mF"] = dict(ripple_pp_V_10ms_window=rip, ripple_amp_est_V=res["pulsation_amp_max_W"] / (VCELL * 2 * math.pi * f_main * C),
                                        v_min_V=float(v.min()), v_max_V=float(v.max()), slow_drift_max_V=float(np.abs(slow - VCELL).max()),
                                        end_minus_start_V=float(np.abs(v[-1] - v[0]).max()), exceeds_cell_rating_80V=bool(v.max() > 80.0 or v.min() < 20.0))
    return res


def run_case(name, grade, params, Q, m, iscale, n0=2100.0, t_end=1.3, seq=None):
    Tld = r.road_torque(n0, grade)
    kw = dict(t_end=t_end, dt=1e-4, full_log=True, **params)
    if seq is not None:
        kw["seq_eps"] = seq
    res, ser = r.simulate(Tld, grade, label=name, **kw)
    t, P = cell_power(ser["cplx"], Q, m, iscale)
    f4 = 4 * n0 * c.RPM / 2 / math.pi; f2 = 2 * n0 * c.RPM / 2 / math.pi
    st = stats(t, P, Q, name, (f4 + f2, abs(f4 - f2)))
    T = np.array(ser["T4"]) + np.array(ser["T2"])
    st.update(torque_min_Nm=res["torque_min_Nm"], torque_min_over_request=res["torque_min_Nm"] / Tld, torque_gap_below90pct_s=res["torque_gap_below90pct_s"],
              t_recover95_s=res["t_recover95_s"], torque_deficit_Nms=res["torque_deficit_Nms"], I_rms_peak_over_Imax=res["I_rms_peak_over_Imax"],
              speed_drop_kmh=res["speed_drop_kmh"], params=params, grade_pct=grade * 100, m=m, Q=Q)
    return st, (t, P, res)


if __name__ == "__main__":
    OUT = dict(meta=dict(script="03_simulation/run_h10.py", task="H10 confirmation", date=str(datetime.date.today()),
                         method="coil-level P_j(t) from the two-mode IM model + 16 series cells with C_cell on a stiff link; see confirm_H10.md"), cases=[])
    OUT["geometry"] = "legacy" if c.LEGACY else "agreed"
    cand0 = []
    for td, tf4, tf2 in itertools.product((0.1, 0.25, 0.4), (0.02, 0.06, 0.15), (0.08, 0.15, 0.3)):
        res, _ = r.simulate(r.road_torque(2100.0, 0.0), 0.0, t_end=1.3, dt=2e-4, t_d=td, t_f4=tf4, t_f2=tf2)
        cand0.append((res["torque_min_Nm"] / res["T_req_Nm"], res["I_rms_peak_over_Imax"], dict(t_d=td, t_f4=tf4, t_f2=tf2)))
    cand0.sort(key=lambda x: -x[0])
    OUT["flat_schedule_search"] = [dict(min_over_request=a_, I_over_Imax=b_, params=p_) for a_, b_, p_ in cand0[:6]]
    print("flat-road search:", [(round(a_, 3), p_) for a_, b_, p_ in cand0[:4]], flush=True)
    p0 = cand0[0][2]; p2 = dict(t_d=0.02, t_f4=0.15, t_f2=0.15)
    # 1. overlapped, m = 3
    for name, grade, par in (("overlapped_flat_m3", 0.0, p0), ("overlapped_2pct_m3", 0.02, p2)):
        st, _ = run_case(name, grade, par, 48, 3, 1.0)
        OUT["cases"].append(st); print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items() if not isinstance(v, dict)}, flush=True)
        for kk in ("C_1.00mF", "C_2.88mF"):
            print("   ", kk, st[kk], flush=True)
    # 2. sequential (no overlap): mode 2 starts when |psi_r4| < 5 % of its initial value
    seqbest = None
    for grade in (0.0, 0.02):
        cand = []
        for tf4, tf2 in itertools.product((0.02, 0.05), (0.05, 0.1, 0.15)):
            par = dict(t_d=0.02, t_f4=tf4, t_f2=tf2)
            st, _ = run_case(f"sequential_{grade*100:.0f}pct_tf4_{tf4}_tf2_{tf2}", grade, par, 48, 3, 1.0, seq=0.05)
            cand.append(st)
        b = min(cand, key=lambda x: x["torque_deficit_Nms"])
        OUT["cases"].append(b)
        OUT.setdefault("sequential_all", []).extend(cand)
        print("SEQ best", grade, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in b.items() if not isinstance(v, dict)}, b["C_1.00mF"], flush=True)
    # 3. m = 5 stator (N = 16 modules x 5 coils, Q = 80): same pu machine, 5-leg modules; overlapped schedule search to keep >= 90 %
    cand = cand0
    for name, grade, par in (("overlapped_flat_m5", 0.0, p0), ("overlapped_2pct_m5", 0.02, p2)):
        st, _ = run_case(name, grade, par, 80, 5, 48 / 80)
        OUT["cases"].append(st); print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items() if not isinstance(v, dict)}, flush=True)
        print("   ", st["C_1.00mF"], st["C_2.88mF"])
    json.dump(OUT, open("results/confirm_H10_handover_%s.json" % OUT["geometry"], "w"), indent=1, default=float)

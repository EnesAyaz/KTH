"""Item 3b + 4: WRSM pole transition (field reversal strategies) and the 10th-order rotor harmonic.

Field circuit: 8 pole coils j, MMF F_j = N_f I_j.  Flux per pole (infinite-permeability iron, zero net flux):
   Phi = G F,  G = P_pole (I - 11^T/8) + Lam_ip * Lap     (Lap = ring Laplacian: 2 on diagonal, -1 to both neighbours)
   v_j = R I_j + N_f^2 (G dI/dt)_j.  Group copper at full I_f = 4 kW (shared input) -> R I_r^2 = 500 W per pole,
   so L/R = G F_r^2 / 500 W and no turn count is needed.
Stator side: fundamental flux of mode p from each pole by superposition of single-pole MEC solutions (scaled so that the pure
patterns at full field reproduce the saturated MEC value).  Quasi-static torque availability under the SPB voltage budget
(|v_4|+|v_2| <= V_pk) and current budget (|i_4|^2+|i_2|^2 <= I_pk^2), then the vehicle ODE.
"""
import json, math, datetime
import numpy as np
from scipy.optimize import minimize
import spb_core as c, wrsm_model as w, sync_model as s

VPK, IPK = c.SQ2 * c.VMAX, c.SQ2 * c.IMAX
V = c.VEH
M_EQ = V["mass_kg"] * V["mass_factor"]; G_R, ETA, RW = V["gear_ratio"], V["eta_gear"], V["wheel_radius_m"]
J_EQ = M_EQ * (RW / G_R) ** 2
CDA = 0.5 * V["rho_air_kg_m3"] * V["Cd"] * V["frontal_area_m2"]
NPOLE = 8
ARC = w.ARC
H_POLE, W_IP = 0.045, 0.020           # interpolar leakage geometry (assumption: pole body 45 mm high, 20 mm slot between poles)


def road_torque(n_rpm, grade):
    v = n_rpm * c.RPM * RW / G_R
    a = math.atan(grade)
    F = V["Crr"] * V["mass_kg"] * V["g_m_s2"] * math.cos(a) + CDA * v * v + V["mass_kg"] * V["g_m_s2"] * math.sin(a)
    return F * RW / G_R / ETA


def field_matrices(gs):
    P = c.MU0 * c.R * (ARC * 2 * math.pi / NPOLE) * c.LST / (c.GEFF * gs)
    Lam = c.MU0 * c.LST * H_POLE / W_IP
    lap = 2 * np.eye(NPOLE) - np.roll(np.eye(NPOLE), 1, 0) - np.roll(np.eye(NPOLE), -1, 0)
    Gm = P * (np.eye(NPOLE) - 1.0 / NPOLE) + Lam * lap
    Fr = w.F_MAX * gs
    return Gm, Fr, P, Lam


def tau_numbers(gs):
    Gm, Fr, P, Lam = field_matrices(gs)
    out = {}
    for name, pat in (("2p8", w.PAT["2p8"]), ("2p4", w.PAT["2p4"])):
        W_main = 0.5 * Fr ** 2 * pat @ (P * (np.eye(NPOLE) - 1 / NPOLE)) @ pat
        W_lk = 0.5 * Fr ** 2 * pat @ (Lam * (2 * np.eye(NPOLE) - np.roll(np.eye(NPOLE), 1, 0) - np.roll(np.eye(NPOLE), -1, 0))) @ pat
        out[name] = dict(W_main_J=W_main, W_leak_J=W_lk, leak_factor=(W_main + W_lk) / W_main, tau_f_s=2 * (W_main + W_lk) / 4000.0)
    return out


def psi_unit(gs, p):
    """complex fundamental-p flux linkage amplitude (Wb, peak) per pole at full per-pole MMF; single-pole MEC solves (linear)."""
    w.GS["v"] = gs
    th = 0.0
    Fp = np.zeros(NPOLE); Fp[0] = -w.F_MAX
    rot = c.rotor_salient(th, Fp, arc=ARC, gs=gs)
    r = c.mec_solve(np.zeros(c.Q), rot)
    return 2 / c.M * np.sum(r["psi"] * np.exp(-1j * p * c.COIL_ANG))


def psi_f_from_poles(I, U):
    """I: pole currents (pu of rated), U = {p: unit complex flux of pole0}; returns {p: complex amplitude} (rotor-frame)."""
    out = {}
    for p, u in U.items():
        out[p] = sum(I[j] * u * np.exp(-1j * p * j * 2 * math.pi / NPOLE) for j in range(NPOLE))
    return out


def pat_current(kB, A=1.0):
    # group A coils 0,3,4,7 fixed (+1,-1,+1,-1); group B coils 1,2,5,6: (kB, -kB, kB, -kB) with kB=-1 -> 2p8, +1 -> 2p4
    return np.array([A, kB, -kB, -A, A, kB, -kB, -A])


def sync_eff(gs, mode):
    tag = "_gs4" if gs == 4.0 else ""
    d = np.load(f"{c.ROOT}/03_simulation/scratch/wrsm_map_{mode}{tag}.npz")
    from scipy.interpolate import RegularGridInterpolator
    it = RegularGridInterpolator((d["ID"], d["IQ"], d["IF"]), d["out"][..., :2])
    p0 = it([0, 0, 1.0])[0]
    Ld = (it([-150.0, 0, 1.0])[0][0] - p0[0]) / -150.0
    Lq = it([0, 150.0, 1.0])[0][1] / 150.0
    return float(p0[0]), float(Ld), float(Lq)


def torque_avail(psi_f, Om, Ld, Lq, T_req):
    """max torque of the two stator modes with ONE shared voltage and current budget; returns (T, i-vector)."""
    modes = [4, 2]
    wm = {p: p * Om for p in modes}

    def Tfun(x):
        T = 0
        for k, p in enumerate(modes):
            idv, iqv = x[2 * k], x[2 * k + 1]
            T += c.M / 2 * p * (psi_f[p] * iqv + (Ld[p] - Lq[p]) * idv * iqv)
        return T

    def vmag(x):
        tot = 0
        for k, p in enumerate(modes):
            idv, iqv = x[2 * k], x[2 * k + 1]
            pd = psi_f[p] + Ld[p] * idv; pq = Lq[p] * iqv
            tot += math.hypot(c.RS * idv - wm[p] * pq, c.RS * iqv + wm[p] * pd)
        return tot

    cons = [{"type": "ineq", "fun": lambda x: VPK - vmag(x)}, {"type": "ineq", "fun": lambda x: IPK ** 2 - (x ** 2).sum()},
            {"type": "ineq", "fun": lambda x: -x[0]}, {"type": "ineq", "fun": lambda x: -x[2]}]
    best = (0.0, np.zeros(4))
    for x0 in (np.array([-50, 100, -50, 100.0]), np.array([-200, 50, -50, 20.0]), np.array([-20, 150, -150, 100.0]), np.array([-300, 100, -100, 50.0]), np.array([-100, 20, -200, 150.0])):
        for tgt in (None,):
            r = minimize(lambda x: -Tfun(x), x0, constraints=cons, method="SLSQP", options=dict(maxiter=120, ftol=1e-6))
            if r.success or True:
                x = r.x
                if vmag(x) <= VPK * 1.001 and (x ** 2).sum() <= IPK ** 2 * 1.001 and x[0] <= 1e-6 and x[2] <= 1e-6:
                    Tv = Tfun(x)
                    if Tv > best[0]:
                        best = (Tv, x)
    return best


def run_strategy(gs, strategy, n0, grade, T_req, dt=1e-3, t_end=1.6):
    Gm, Fr, P, Lam = field_matrices(gs)
    Rr_over = Fr ** 2 / 500.0              # N_f^2/R   [At^2/W]; L/R = G*Fr^2/500
    A = (Gm + P * np.ones((NPOLE, NPOLE)) / NPOLE) * Rr_over                        # tau matrix: dI/dt = A^-1 (v/Vr - I)   with v normalised by rated voltage R*I_r
    Ainv = np.linalg.inv(A)
    U = {4: psi_unit(gs, 4), 2: psi_unit(gs, 2)}
    # scale to reproduce saturated pure-pattern fluxes
    tag = "_gs4" if gs == 4.0 else ""
    eff = {}
    for mode, p in (("2p8", 4), ("2p4", 2)):
        pf, Ld, Lq = sync_eff(gs, mode)
        lin = abs(psi_f_from_poles(w.PAT[mode], {p: U[p]})[p])
        eff[p] = dict(scale=pf / lin, Ld=Ld, Lq=Lq, psi_pure=pf)
    # initial: 2p8 -> 2p4 or 4 -> 8; here 2p8 -> 2p4 (kB: -1 -> +1)
    k0, k1 = -1.0, 1.0
    I = pat_current(k0)
    t = 0.0
    Om = n0 * c.RPM
    forced, blank, tfree = 3.0, 0.02, None
    log = []
    state_phase = "init"
    t_blank_end = None
    nsteps = int(t_end / dt)
    for stp in range(nsteps):
        # voltage on group B coils (pu of rated voltage, +1 drives toward +I), group A holds +-1
        vB_target = None
        I_B = I[1]                                # coil 1 current (pu); coil 2 = -I_B; mirrors
        target = k1
        if strategy == "freewheel_blank_unforced":
            if state_phase == "init":
                state_phase = "freewheel"
            if state_phase == "freewheel":
                vB = 0.0                          # free-wheel (diode path, small drop neglected)
                if abs(I_B) < 0.05:
                    state_phase = "blank"; t_blank_end = t + blank
            elif state_phase == "blank":
                vB = 0.0
                if t >= t_blank_end:
                    state_phase = "build"
            else:
                vB = 1.0 if target > I_B else -1.0
        elif strategy == "forced_3x":
            vB = forced * np.sign(target - I_B) if abs(target - I_B) > 0.02 else float(np.clip((target - I_B) * 50 + 1.0 * 0, -1, 1) + 0)
            if abs(I_B - target) <= 0.02:
                vB = 1.0 * np.sign(target)         # hold at rated
        elif strategy == "ksweep_forced":
            # follow a linear k ramp but never faster than the forced-voltage limit allows (P4 pattern, gradual)
            Tsw = 0.4
            Iref = -1.0 + 2.0 * min(t / Tsw, 1.0)
            vB = float(np.clip(Iref + A[1, 1] * (2.0 / Tsw if t < Tsw else 0.0) + 2.0 * (Iref - I_B), -forced, forced))
        vvec = np.array([1.0, vB, -vB, -1.0, 1.0, vB, -vB, -1.0])
        dI = Ainv @ (vvec - I)                   # (v - R I) / (R) in pu with rated R,  tau in s
        I = I + dt * dI
        I = np.clip(I, -1.0, 1.0)
        psi = psi_f_from_poles(I, U)
        psi_f = {p: abs(psi[p]) * eff[p]["scale"] / c.SQ2 * c.SQ2 for p in (4, 2)}   # amplitude (peak)
        if stp % 10 == 0:
            Ld = {p: eff[p]["Ld"] for p in (4, 2)}; Lq = {p: eff[p]["Lq"] for p in (4, 2)}
            Tav, x = torque_avail(psi_f, Om, Ld, Lq, T_req)
            Tm = min(T_req, Tav)
            Tl = road_torque(Om / c.RPM, grade)
            log.append((t, I[1], psi_f[4], psi_f[2], Tav, Tm, Tl, Om / c.RPM, math.sqrt((x ** 2).sum() / 2) if Tav > 0 else 0))
        # vehicle (use the last Tm)
        Tm = log[-1][5] if log else T_req
        Tl = road_torque(Om / c.RPM, grade)
        Om += dt * (Tm - Tl) / J_EQ
        t += dt
    L = np.array(log)
    tt, Tm = L[:, 0], L[:, 5]
    below = np.where(Tm < 0.9 * T_req)[0]
    gap = float(tt[below[-1]] - tt[below[0]] + 0.01) if len(below) else 0.0
    return dict(strategy=strategy, grade_pct=grade * 100, T_req_Nm=T_req, n0_rpm=n0, gs=gs,
                torque_min_Nm=float(Tm.min()), torque_gap_below90pct_s=gap,
                t_I_B_zero_cross_s=float(tt[np.where(L[:, 1] >= 0)[0][0]]) if (L[:, 1] >= 0).any() else None,
                t_I_B_95pct_s=float(tt[np.where(L[:, 1] >= 0.95)[0][0]]) if (L[:, 1] >= 0.95).any() else None,
                t_recover95_s=float(tt[np.where(Tm < 0.95 * T_req)[0][-1]]) if (Tm < 0.95 * T_req).any() else 0.0,
                deficit_Nms=float(np.trapezoid(np.maximum(T_req - Tm, 0), tt)),
                speed_drop_rpm=float(n0 - L[:, 7].min()), speed_drop_kmh=float((n0 - L[:, 7].min()) * c.RPM * RW / G_R * 3.6),
                I_rms_max_A=float(L[:, 8].max()), I_rms_max_over_Imax=float(L[:, 8].max() / c.IMAX)), dict(t=tt, I_B=L[:, 1], psi4=L[:, 2], psi2=L[:, 3], T_avail=L[:, 4], T=Tm, n=L[:, 7])


def harmonic_study():
    """Item 4: 10th-order rotor harmonic in 2p=4 mode: EMF in the 48 coils and circulating current inside the 16 modules."""
    out = {}
    npts = 7200
    th = np.linspace(0, 2 * math.pi, npts, endpoint=False)
    for mode in ("2p4", "2p8"):
        B = np.zeros(npts)
        for j, sgn in enumerate(w.PAT[mode]):
            d = np.angle(np.exp(1j * (th - j * 2 * math.pi / NPOLE)))
            B += sgn * (np.abs(d) <= ARC * math.pi / NPOLE)
        spec = np.fft.rfft(B) / npts * 2
        out[mode] = {int(n): float(abs(spec[n])) for n in (2, 4, 6, 10, 12, 14, 20)}
    res = {"rotor_field_harmonics_rel_B0": out}
    # per-coil EMF of harmonic order nu (rms, per unit speed): E_nu = nu*Om * psi_nu ; psi_nu = N_c*kw*(2 R L/nu) * B_nu /sqrt2 (point-conductor coil)
    hh = []
    gs = 4.0
    sc_B0 = 0.7122233430090569                  # T at I_f = 1 (analyst B0 at psi_f,max, same field MMF as the MEC)
    for mode, nus in (("2p4", (2, 6, 10, 14)), ("2p8", (4, 12, 20))):
        for nu in nus:
            Bnu = sc_B0 * out[mode].get(nu, 0.0)
            kwn = abs(math.sin(nu * c.Y * math.pi / c.Q))
            psi_nu = c.NC * kwn * (2 * c.R * c.LST / nu) * Bnu / c.SQ2
            # module test: coils j, j+16, j+32 -> phase shift 120 deg * nu
            sh = (nu * 120) % 360
            zero_seq = abs(((nu * 120) % 360)) < 1e-9
            Ls = c.L_sigma_mode(nu % 48 if nu % 48 else 48) if False else None
            hh.append(dict(mode=mode, nu=nu, B_rel=out[mode].get(nu, 0.0), kw=kwn, psi_rms_Wb=psi_nu, phase_shift_in_module_deg=sh,
                           zero_sequence=bool(zero_seq)))
    res["harmonics"] = hh
    # circulating current for the non-zero-sequence harmonics: i = E / Z, Z = Rs + j w_nu (L_sigma(nu) + L_diff(nu) + L_mag(nu))
    circ = []
    fund = {"2p4": 2, "2p8": 4}
    for h in hh:
        nu = h["nu"]
        if h["zero_sequence"] or nu == fund[h["mode"]]:
            continue
        for n_rpm in (1000, 2100, 3000, 4250, 4500, 6000):
            wv = nu * n_rpm * c.RPM
            E = wv * h["psi_rms_Wb"]
            # self impedance of mode nu of the 48-coil stator: Rs + jw (L_total(nu) + leakage(nu)); module neutral isolated: 3-wire balanced -> no extra factor
            Lnu = c.L_mode_total(nu) + c.L_sigma_mode(nu)
            Z = complex(c.RS, wv * Lnu)
            Ic = E / abs(Z)
            circ.append(dict(mode=h["mode"], nu=nu, n_rpm=n_rpm, f_Hz=wv / 2 / math.pi, E_rms_V=E, Z_ohm=abs(Z), L_nu_H=Lnu, I_circ_rms_A=Ic,
                             I_circ_over_Imax=Ic / c.IMAX, P_cu_W=c.M * c.RS * Ic ** 2, E_over_Vmax=E / c.VMAX))
    res["circulating"] = circ
    return res


if __name__ == "__main__":
    import sys
    ONLY = sys.argv[1:] 
    out = {}
    out["tau_f"] = {f"gs{g:g}": tau_numbers(g) for g in (1.0, 4.0)}
    print(json.dumps(out["tau_f"], indent=1, default=float))
    out["harmonic"] = harmonic_study()
    for r in out["harmonic"]["circulating"]:
        if r["n_rpm"] in (2100, 4500):
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    out["transitions"] = []
    ser = {}
    for gs in (4.0, 1.0):
        for grade in (0.0, 0.02):
            Tr = road_torque(2100.0, grade)
            for strat in (ONLY or ("freewheel_blank_unforced", "forced_3x")):
                r, sr = run_strategy(gs, strat, 2100.0, grade, Tr)
                out["transitions"].append(r)
                ser[f"gs{gs:g}_g{grade}_{strat}"] = sr
                print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    meta = dict(script="03_simulation/run_wrsm_transition.py", task="T04 items 3b and 4", date=str(datetime.date.today()),
                note="Field circuit from pole-level permeance matrix with interpolar leakage (assumed 45x20 mm); stator torque availability quasi-static under shared V/I budget; speed 2100 rpm 2p8 -> 2p4")
    fn = "results/wrsm_pole_transition_ksweep.json" if ONLY else "results/wrsm_pole_transition.json"
    json.dump(dict(meta=meta, **out), open(fn, "w"), indent=1, default=float)
    np.savez("scratch/wrsm_transition_series%s.npz" % ("_ksweep" if ONLY else ""), **{k + "__" + kk: np.array(vv) for k, v in ser.items() for kk, vv in v.items()})

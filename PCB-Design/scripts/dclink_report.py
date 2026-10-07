"""
DC-link capacitor sizing study for the 75 V / 100 A_rms EPC2361 phase leg.

    python scripts/dclink_report.py
      -> reports/dc-link/figures/*.pdf|png, reports/dc-link/data/dclink.json, reports/dc-link/numbers.tex

1. RMS ripple current: single leg and three legs on a shared bus, time-domain PWM vs analytical formulas
2. Peak-peak voltage ripple per uF -> capacitance vs ripple target for several switching frequencies
3. Low-frequency ripple of a stand-alone single-phase half bridge (split DC link)
4. Current sharing between the local 0805 MLCCs, the three 1210 bank rows and the external bus, from the
   ripple spectrum and the Q3D copper matrix (BB_PL_2oz): RMS current and ESR loss per capacitor
"""
import json
import math
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "dc-link")
for d in ("figures", "data"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
Q3D = os.path.join(ROOT, "simulation", "bb_q3d", "results")

VDC, I_RMS = 75.0, 100.0
I_PK = math.sqrt(2) * I_RMS
F_SW = 50e3
FREQS = (20e3, 50e3, 100e3, 200e3)


# ------------------------------------------------------------------ PWM simulation
def pwm(M, phi, svpwm=True, fsw=F_SW, f1=200.0, npts=200):
    """Ideal 2-level 3-phase inverter, common triangular carrier. Returns t, leg-A input current, total input current."""
    n_sw = int(round(fsw / f1))
    t = np.arange(n_sw * npts) / (fsw * npts)
    th = 2 * np.pi * f1 * t
    refs = np.array([M * np.sin(th - k * 2 * np.pi / 3) for k in range(3)])
    if svpwm:
        refs = refs - 0.5 * (refs.max(axis=0) + refs.min(axis=0))
    carrier = 2 * np.abs(2 * ((t * fsw) % 1.0) - 1) - 1
    s = (refs > carrier).astype(float)
    i = np.array([I_PK * np.sin(th - k * 2 * np.pi / 3 - phi) for k in range(3)])
    legs = s * i
    return t, legs[0], legs.sum(axis=0), npts


def hf(i_in, npts):
    """Switching-frequency part: current minus its switching-period average (the bulk / source supplies the average)."""
    x = i_in.reshape(-1, npts)
    return (x - x.mean(axis=1, keepdims=True)).ravel()


def vpp_per_uF(i_c, npts, fsw):
    """Worst switching-period peak-peak capacitor voltage for 1 uF."""
    dt = 1.0 / (fsw * npts)
    v = (np.cumsum(i_c) * dt / 1e-6).reshape(-1, npts)
    return float((v.max(axis=1) - v.min(axis=1)).max())


# ------------------------------------------------------------------ analytical
def leg_hf_analytic(M, phi):
    """Single leg, SPWM: I_HF^2 = <d(1-d) i^2>, d = (1 + M sin)/2, i = I_pk sin(th - phi)."""
    return I_PK * 0.5 * math.sqrt(max(0.0, 0.5 - M ** 2 * (0.25 + math.cos(2 * phi) / 8)))


def three_phase_analytic(M, phi):
    """Kolar & Round: I_C = I_pk sqrt(M [sqrt3/(4 pi) + cos^2 phi (sqrt3/pi - 9M/16)]) (SPWM, peak phase current)."""
    return I_PK * math.sqrt(max(0.0, M * (math.sqrt(3) / (4 * math.pi) + math.cos(phi) ** 2 * (math.sqrt(3) / math.pi - 9 * M / 16))))


# ------------------------------------------------------------------ Q3D current sharing
def load_q3d(tag="BB_PL_2oz"):
    lines = open(os.path.join(Q3D, tag + "_matrix.txt")).read().splitlines()

    def block(title):
        for i, l in enumerate(lines):
            if l.strip() == title:
                names = lines[i + 1].split()
                return names, np.array([[float(v) for v in r.split()[1:]] for r in lines[i + 2:i + 2 + len(names)]])
    names, L = block("AC Inductance Matrix")
    _, Rdc = block("DC Resistance Matrix")
    _, Rac = block("AC Resistance Matrix")
    sinks = {}
    for l in open(os.path.join(Q3D, tag + "_terminals.txt")):
        if l.strip() and not l.startswith("#"):
            p = l.split()
            sinks[p[0]] = p[1]
    # the AC net carries no DC-link current and would float: keep the DC+ / DC- nets only
    keep = [k for k, n in enumerate(names) if not n.startswith("AC:")]
    names = [names[k] for k in keep]
    L, Rdc, Rac = L[np.ix_(keep, keep)], Rdc[np.ix_(keep, keep)], Rac[np.ix_(keep, keep)]
    br = [(n.split(":")[1], sinks[n.split(":")[0]]) for n in names]
    return names, L * 1e-9, (Rdc, Rac), br


def r_of_f(R, f):
    """Copper resistance vs frequency: Q3D DC value rising as sqrt(f) (skin effect) to the 100 MHz AC value."""
    Rdc, Rac = R
    return Rdc + (Rac - Rdc) * min(1.0, math.sqrt(f / 1e8))


CAPS = {  # group: (P terminal, N terminal, n parts, C_eff each, ESR each, ESL each)
    "local_L": ("CapPL", "CapNL", 6, 0.45e-6, 6e-3, 0.48e-9),
    "local_R": ("CapPR", "CapNR", 6, 0.45e-6, 6e-3, 0.48e-9),
    "row1": ("CapB1P", "CapB1N", 8, 3.0e-6, 3e-3, 0.5e-9),
    "row2": ("CapB2P", "CapB2N", 8, 3.0e-6, 3e-3, 0.5e-9),
    "row3": ("CapB3P", "CapB3N", 8, 3.0e-6, 3e-3, 0.5e-9),
}
EXT = dict(L=20e-9, R=2e-3, C=1e-3, ESR=20e-3)   # busbar to the shared bulk / other blocks


def sharing(freqs, q3d, ext=True):
    """Fraction of a leg ripple current harmonic carried by each capacitor group and by the external bus, per frequency.
    Source: the leg draws the current from both QH drains and returns it to both QL sources."""
    names, L, R, br = q3d
    nodes = sorted({n for b in br for n in b} | ({"ext"} if ext else set()))
    gnd = "T_DCN"
    idx = {n: i for i, n in enumerate([n for n in nodes if n != gnd])}
    elems = [(a, b, "cu", k) for k, (a, b) in enumerate(br)]
    for g, (p, n, cnt, C, esr, esl) in CAPS.items():
        elems.append((p, n, g, None))
    if ext:
        elems.append(("T_DCP", "ext", "ext_L", None))
        elems.append(("ext", "T_DCN", "ext_C", None))
    nv, ne = len(idx), len(elems)
    out = {g: [] for g in list(CAPS) + (["ext"] if ext else [])}
    Rpair = R
    for f in freqs:
        w = 2 * math.pi * f
        R = r_of_f(Rpair, f)
        A = np.zeros((nv + ne, nv + ne), complex)
        rhs = np.zeros(nv + ne, complex)
        for k, (a, b, kind, ref) in enumerate(elems):
            col = nv + k
            for node, sg in ((a, 1.0), (b, -1.0)):
                if node in idx:
                    A[idx[node], col] += sg
                    A[col, idx[node]] += sg
            if kind == "cu":
                for j, (_, _, kj, rj) in enumerate(elems[:len(br)]):
                    A[col, nv + j] -= (R[ref, rj] + 1j * w * L[ref, rj])
            elif kind in CAPS:
                p_, n_, cnt, C, esr, esl = CAPS[kind]
                A[col, col] -= (esr + 1 / (1j * w * C) + 1j * w * esl) / cnt
            elif kind == "ext_L":
                A[col, col] -= EXT["R"] + 1j * w * EXT["L"]
            else:
                A[col, col] -= EXT["ESR"] + 1 / (1j * w * EXT["C"])
        for node, cur in (("QH_D_L", -0.5), ("QH_D_R", -0.5), ("QL_S_L", 0.5), ("QL_S_R", 0.5)):
            if node in idx:
                rhs[idx[node]] += cur
        x = np.linalg.solve(A, rhs)
        for k, (a, b, kind, ref) in enumerate(elems):
            if kind in CAPS:
                out[kind].append(abs(x[nv + k]))
            elif kind == "ext_L":
                out["ext"].append(abs(x[nv + k]))
    return {g: np.array(v) for g, v in out.items()}


def spectrum(i_c, fs_sample):
    """One-sided RMS amplitude per FFT bin (window = one fundamental period, exact periodicity)."""
    X = np.fft.rfft(i_c) / len(i_c)
    amp = np.abs(X) * math.sqrt(2)
    amp[0] = 0.0
    f = np.fft.rfftfreq(len(i_c), 1 / fs_sample)
    return f, amp


# ------------------------------------------------------------------ main
def main():
    res = {}
    Ms = np.round(np.arange(0.05, 1.151, 0.05), 3)
    pfs = (1.0, 0.9, 0.7, 0.5, 0.0)
    grid = []
    for pf in pfs:
        phi = math.acos(pf)
        for M in Ms:
            row = dict(M=float(M), pf=pf)
            for mode, sv in (("svpwm", True), ("spwm", False)):
                if mode == "spwm" and M > 1.0:
                    continue
                t, ia, itot, npts = pwm(M, phi, svpwm=sv)
                ca, ct = hf(ia, npts), hf(itot, npts)
                row["leg_" + mode] = float(np.sqrt(np.mean(ca ** 2)))
                row["tot_" + mode] = float(np.sqrt(np.mean(ct ** 2)))
                row["vleg_" + mode] = vpp_per_uF(ca, npts, F_SW)
                row["vtot_" + mode] = vpp_per_uF(ct, npts, F_SW)
            row["leg_ana"] = leg_hf_analytic(M, phi) if M <= 1.0 else float("nan")
            row["tot_ana"] = three_phase_analytic(M, phi) if M <= 1.0 else float("nan")
            grid.append(row)
    res["grid"] = grid
    worst = lambda key: max(grid, key=lambda r: r.get(key, 0))
    W = {k: worst(k) for k in ("leg_svpwm", "tot_svpwm", "vleg_svpwm", "vtot_svpwm")}
    res["worst"] = W
    rated = [r for r in grid if abs(r["M"] - 1.0) < 1e-9 and r["pf"] == 1.0][0]
    res["rated"] = rated
    # ripple constant K = dVpp * C * f (V * uF * kHz scale-free): C_req = K / (dV f)
    K_leg = W["vleg_svpwm"]["vleg_svpwm"] * 1e-6 * F_SW     # V*F*Hz
    K_3ph = W["vtot_svpwm"]["vtot_svpwm"] * 1e-6 * F_SW
    res.update(K_leg=K_leg, K_3ph=K_3ph, K_leg_simple=I_PK / 4)   # I_pk/(4 f C) at d = 0.5
    targets = np.array([0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0])
    creq = {f: dict(leg=(K_leg / (targets * f) * 1e6).tolist(), three=(K_3ph / (targets * f) * 1e6).tolist(),
                    three_per_block=(K_3ph / 3 / (targets * f) * 1e6).tolist()) for f in FREQS}
    res["creq"] = dict(targets=targets.tolist(), table=creq)

    # LF ripple of a stand-alone single-phase half bridge with a split DC link: each half carries i/2
    f1s = (50, 100, 200, 500, 1000)
    res["lf"] = {f1: dict(C_half_mF_3V=I_PK / (2 * math.pi * f1 * 3.0) * 1e3) for f1 in f1s}

    # ---------------- current sharing (rated point and worst leg current) ----------------
    q3d = load_q3d()
    share_res = {"isolated": {}, "bus": {}}
    fr = np.logspace(3, 8, 400)
    for label, (M, pf) in (("rated", (1.0, 1.0)), ("worst", (W["leg_svpwm"]["M"], W["leg_svpwm"]["pf"]))):
        t, ia, itot, npts = pwm(M, math.acos(pf), svpwm=True, npts=400)
        ca = hf(ia, npts)
        f, amp = spectrum(ca, F_SW * npts)
        keep = amp ** 2 > 1e-7 * np.sum(amp ** 2)          # bins holding the energy
        f_k, a_k = f[keep], amp[keep]
        for scen, ext in (("isolated", False), ("bus", True)):
            ratio = sharing(f_k, q3d, ext=ext)
            grp = {}
            for g, r in ratio.items():
                irms = float(np.sqrt(np.sum((a_k * r) ** 2)))
                n = CAPS[g][2] if g in CAPS else 1
                esr = CAPS[g][4] if g in CAPS else EXT["ESR"]
                grp[g] = dict(I_group=irms, I_per_cap=irms / n, P_per_cap=(irms / n) ** 2 * esr, P_group=(irms / n) ** 2 * esr * n)
            share_res[scen][label] = dict(M=M, pf=pf, I_leg_hf=float(np.sqrt(np.mean(ca ** 2))), groups=grp,
                                          energy_kept=float(np.sum(a_k ** 2) / np.sum(amp ** 2)))
        if label == "rated":
            res["spectrum_rated"] = dict(f=f_k.tolist(), a=a_k.tolist())
    for scen, ext in (("isolated", False), ("bus", True)):
        rr = sharing(fr, q3d, ext=ext)
        res["sharing_curve_" + scen] = dict(f=fr.tolist(), **{g: v.tolist() for g, v in rr.items()})
    res["sharing"] = share_res
    json.dump(res, open(os.path.join(OUT, "data", "dclink.json"), "w"), indent=1, default=float)

    # ---------------- figures ----------------
    FIG = os.path.join(OUT, "figures")
    cols = dict(zip(pfs, ("C0", "C1", "C2", "C3", "C4")))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for pf in pfs:
        g = [r for r in grid if r["pf"] == pf]
        M = [r["M"] for r in g]
        ax[0].plot(M, [r["leg_svpwm"] for r in g], "-", color=cols[pf], label="cos phi=%.1f" % pf)
        ax[0].plot(M, [r["leg_ana"] for r in g], ":", color=cols[pf])
        ax[1].plot(M, [r["tot_svpwm"] for r in g], "-", color=cols[pf], label="cos phi=%.1f" % pf)
        ax[1].plot(M, [r["tot_ana"] for r in g], ":", color=cols[pf])
    ax[0].set_title("Single leg: HF capacitor current", fontsize=10)
    ax[1].set_title("Three legs on one bus: total HF capacitor current", fontsize=10)
    for a in ax:
        a.set_xlabel("modulation index M")
        a.set_ylabel("A rms (solid: SVPWM simulation, dotted: SPWM formula)")
        a.grid(alpha=0.3)
        a.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "irms.pdf"))
    fig.savefig(os.path.join(FIG, "irms.png"), dpi=130)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for f, c in zip(FREQS, ("C0", "C1", "C2", "C3")):
        ax[0].loglog(targets, creq[f]["leg"], "-o", ms=3, color=c, label="%.0f kHz" % (f / 1e3))
        ax[1].loglog(targets, creq[f]["three_per_block"], "-o", ms=3, color=c, label="%.0f kHz" % (f / 1e3))
    for a, title in zip(ax, ("Single leg (own capacitors only)", "Three legs on one bus: per leg (total / 3)")):
        a.set_title(title, fontsize=10)
        a.set_xlabel("allowed peak-peak ripple [V]  (75 V bus: 1.5 V = 2 %)")
        a.set_ylabel("required effective capacitance [uF]")
        a.grid(alpha=0.3, which="both")
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "creq.pdf"))
    fig.savefig(os.path.join(FIG, "creq.png"), dpi=130)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for scen, ls in (("isolated", "-"), ("bus", "--")):
        sc = res["sharing_curve_" + scen]
        for g, lab, c in (("local_L", "local 0805 bank, one cell", "C0"), ("row1", "1210 row 1", "C1"),
                          ("row2", "1210 row 2", "C2"), ("row3", "1210 row 3", "C3"), ("ext", "external bus", "C4")):
            if g in sc:
                ax[0].semilogx(sc["f"], sc[g], ls, color=c, label=lab + ("" if scen == "isolated" else " (with bus)"))
    ax[0].set_xlabel("frequency [Hz]")
    ax[0].set_ylabel("share of the leg ripple current")
    ax[0].set_title("Current division (Q3D copper + capacitor C/ESR/ESL)", fontsize=10)
    ax[0].legend(fontsize=7)
    ax[0].grid(alpha=0.3, which="both")
    sp = res["spectrum_rated"]
    ax[1].semilogx(sp["f"], sp["a"], ".", ms=2)
    ax[1].set_xlabel("frequency [Hz]")
    ax[1].set_ylabel("A rms per bin")
    ax[1].set_title("Leg ripple current spectrum, M = 1, cos phi = 1, 50 kHz", fontsize=10)
    ax[1].grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "sharing.pdf"))
    fig.savefig(os.path.join(FIG, "sharing.png"), dpi=130)

    # ---------------- macros ----------------
    sr, sw = share_res["isolated"]["rated"]["groups"], share_res["isolated"]["worst"]["groups"]
    br_, bw_ = share_res["bus"]["rated"]["groups"], share_res["bus"]["worst"]["groups"]
    mac = dict(
        BLocalCap="%.2f" % br_["local_L"]["I_per_cap"], BRowOne="%.2f" % br_["row1"]["I_per_cap"],
        BRowTwo="%.2f" % br_["row2"]["I_per_cap"], BRowThree="%.2f" % br_["row3"]["I_per_cap"], BExt="%.1f" % br_["ext"]["I_group"],
        BWLocalCap="%.2f" % bw_["local_L"]["I_per_cap"], BWRowThree="%.2f" % bw_["row3"]["I_per_cap"], BWExt="%.1f" % bw_["ext"]["I_group"],
        PcapRatedBus="%.3f" % sum(v["P_group"] for k, v in br_.items() if k != "ext"),
        Ipk="%.0f" % I_PK,
        IlegWorst="%.1f" % W["leg_svpwm"]["leg_svpwm"], IlegWorstM="%.2f" % W["leg_svpwm"]["M"],
        IlegWorstPf="%.1f" % W["leg_svpwm"]["pf"], IlegRated="%.1f" % rated["leg_svpwm"],
        ItotWorst="%.1f" % W["tot_svpwm"]["tot_svpwm"], ItotWorstM="%.2f" % W["tot_svpwm"]["M"],
        ItotWorstPf="%.1f" % W["tot_svpwm"]["pf"], ItotRated="%.1f" % rated["tot_svpwm"],
        KlegV="%.0f" % (W["vleg_svpwm"]["vleg_svpwm"]), KtotV="%.0f" % (W["vtot_svpwm"]["vtot_svpwm"]),
        KlegSimple="%.0f" % (I_PK / (4 * F_SW) / 1e-6),
        CLegFifty="%.0f" % (K_leg / (1.5 * 50e3) * 1e6), CTotFifty="%.0f" % (K_3ph / (1.5 * 50e3) * 1e6),
        CBlockFifty="%.0f" % (K_3ph / 3 / (1.5 * 50e3) * 1e6), CBlockFiftyThree="%.0f" % (K_3ph / 3 / (3.0 * 50e3) * 1e6),
        LfFifty="%.0f" % res["lf"][50]["C_half_mF_3V"], LfFive="%.1f" % res["lf"][500]["C_half_mF_3V"],
        ShLocal="%.2f" % (sr["local_L"]["I_group"] + sr["local_R"]["I_group"]),
        ShLocalCap="%.2f" % sr["local_L"]["I_per_cap"], ShRowOne="%.2f" % sr["row1"]["I_per_cap"],
        ShRowTwo="%.2f" % sr["row2"]["I_per_cap"], ShRowThree="%.2f" % sr["row3"]["I_per_cap"],
        WLocalCap="%.2f" % sw["local_L"]["I_per_cap"], WRowOne="%.2f" % sw["row1"]["I_per_cap"],
        WRowTwo="%.2f" % sw["row2"]["I_per_cap"], WRowThree="%.2f" % sw["row3"]["I_per_cap"],
        PcapRated="%.3f" % sum(v["P_group"] for k, v in sr.items() if k != "ext"),
        PcapWorst="%.3f" % sum(v["P_group"] for k, v in sw.items() if k != "ext"),
    )
    # capacitance table for the report: 1 %, 2 %, 4 % peak-peak ripple
    rows = []
    for f in FREQS:
        cells = []
        for dv in (0.75, 1.5, 3.0):
            c_leg = K_leg / (dv * f) * 1e6
            c_blk = K_3ph / 3 / (dv * f) * 1e6
            cells.append("%.0f & %.0f (%d)" % (c_leg, c_blk, math.ceil(max(c_blk - 5.4, 0) / 3.0)))
        rows.append("%.0f\\,kHz & %s \\\\" % (f / 1e3, " & ".join(cells)))
    with open(os.path.join(OUT, "creq_table.tex"), "w") as fh:
        fh.write("% generated by scripts/dclink_report.py\n\\newcommand{\\CreqRows}{%\n" + "\n".join(rows) + "\n}\n")
    with open(os.path.join(OUT, "numbers.tex"), "w") as fh:
        fh.write("% generated by scripts/dclink_report.py\n")
        for k, v in mac.items():
            fh.write("\\newcommand{\\%s}{%s}\n" % (k, v))
    print(json.dumps(mac, indent=1))
    print("C_req table (uF eff):")
    for f in FREQS:
        print("  %3.0f kHz leg:" % (f / 1e3), " ".join("%.0f" % v for v in creq[f]["leg"]),
              "| 3ph per block:", " ".join("%.0f" % v for v in creq[f]["three_per_block"]))
    for scen in ("isolated", "bus"):
        for lab in ("rated", "worst"):
            s = share_res[scen][lab]
            print(scen, lab, s["M"], s["pf"], "I_leg_hf %.1f" % s["I_leg_hf"],
                  {g: (round(v["I_group"], 2), round(v["I_per_cap"], 2)) for g, v in s["groups"].items()})


if __name__ == "__main__":
    main()

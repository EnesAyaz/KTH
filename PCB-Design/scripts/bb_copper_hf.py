"""
PCB copper loss of the building block including the switching-frequency harmonics, and the high-/low-side
device loss split, for SPWM and SVM (carrier-based, min-max injection) with a sinusoidal load current.

    python scripts/bb_copper_hf.py   -> reports/building-block/data/copper_hf.json, figures/copper_hf.pdf|png

Network (frequency domain, one solve per harmonic):
  - Q3D partial R(f), L(f) matrices of all three nets (BB_PL_2oz): branches from each source terminal to its net sink.
    R(f), L(f) from the Q3D frequency sweep (simulation/bb_q3d/results/sweep); without it, the DC matrix plus the
    100 MHz matrix blended as sqrt(f) is used and the result is flagged.
  - MLCC groups (2 x 6 x 0805 local, 3 x 8 x 1210 bank) with C_eff, ESR, ESL.
  - DC supply: T_DCP and T_DCN each through Z_ext/2 to the external node X (ideal source = AC short).
  - Switched FET currents as current sources, split equally between the two cells:
      QH: s*i from QH_D to QH_S;  QL: (1-s)*i from QL_S to QL_D;  load: i out of T_AC, returned at X.
Copper loss = sum over harmonics of Re(I^H R(f) I) / 2 (DC bin: I^T R I).
"""
import glob
import json
import math
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q3D = os.path.join(ROOT, "simulation", "bb_q3d", "results")
REP = os.path.join(ROOT, "reports", "building-block")
VDC, I_RMS = 75.0, 100.0
I_PK = math.sqrt(2) * I_RMS
F_SW, F1, NPTS = 50e3, 200.0, 200

CAPS = {  # group: (P terminal, N terminal, n parts, C_eff each, ESR each, ESL each)   (as in dclink_report.py)
    "local_L": ("CapPL", "CapNL", 6, 0.45e-6, 6e-3, 0.48e-9),
    "local_R": ("CapPR", "CapNR", 6, 0.45e-6, 6e-3, 0.48e-9),
    "row1": ("CapB1P", "CapB1N", 8, 3.0e-6, 3e-3, 0.5e-9),
    "row2": ("CapB2P", "CapB2N", 8, 3.0e-6, 3e-3, 0.5e-9),
    "row3": ("CapB3P", "CapB3N", 8, 3.0e-6, 3e-3, 0.5e-9),
}
EXT = dict(R=2e-3, L=20e-9)    # busbar / cable to the module DC link (split equally between DC+ and DC-)


# ------------------------------------------------------------------ Q3D matrices
def _block(lines, title):
    for i, line in enumerate(lines):
        if line.strip() == title:
            names = lines[i + 1].split()
            return names, np.array([[float(v) for v in r.split()[1:]] for r in lines[i + 2:i + 2 + len(names)]])
    return None, None


def _sinks():
    s = {}
    for line in open(os.path.join(Q3D, "BB_PL_2oz_terminals.txt")):
        if line.strip() and not line.startswith("#"):
            p = line.split()
            s[p[0]] = p[1]
    return s


def load_rl():
    """Return names, branches and a function f -> (R, L) [ohm, H]."""
    base = open(os.path.join(Q3D, "BB_PL_2oz_matrix.txt")).read().splitlines()
    names, L100 = _block(base, "AC Inductance Matrix")
    _, R100 = _block(base, "AC Resistance Matrix")
    _, Rdc = _block(base, "DC Resistance Matrix")
    sinks = _sinks()
    br = [(n.split(":")[1], sinks[n.split(":")[0]]) for n in names]
    files = sorted(glob.glob(os.path.join(Q3D, "sweep", "BB_PL_2oz_f*.txt")),
                   key=lambda p: int(os.path.basename(p)[11:-4]))
    table = []
    for p in files:
        lines = open(p).read().splitlines()
        n2, L = _block(lines, "AC Inductance Matrix")
        _, R = _block(lines, "AC Resistance Matrix")
        if n2 is None or R is None:
            continue
        perm = [n2.index(n) for n in names]
        table.append((float(os.path.basename(p)[11:-4]), R[np.ix_(perm, perm)], L[np.ix_(perm, perm)] * 1e-9))
    if len(table) >= 3:
        fs = np.array([t[0] for t in table])
        Rs = np.array([t[1] for t in table])
        Ls = np.array([t[2] for t in table])

        def rl(f):
            if f <= 0:
                return Rdc, Ls[0]
            x = np.log10(np.clip(f, fs[0], fs[-1]))
            k = int(np.clip(np.searchsorted(np.log10(fs), x) - 1, 0, len(fs) - 2))
            a = (x - np.log10(fs[k])) / (np.log10(fs[k + 1]) - np.log10(fs[k]))
            R = Rs[k] + a * (Rs[k + 1] - Rs[k])
            if f < fs[0]:
                R = Rdc + (Rs[0] - Rdc) * f / fs[0]
            return R, Ls[k] + a * (Ls[k + 1] - Ls[k])
        return names, br, rl, "q3d_sweep (%d points, %g Hz - %g Hz)" % (len(fs), fs[0], fs[-1])

    def rl(f):
        return Rdc + (R100 - Rdc) * min(1.0, math.sqrt(max(f, 0.0) / 1e8)), L100 * 1e-9
    return names, br, rl, "placeholder: DC + 100 MHz blended as sqrt(f)"


# ------------------------------------------------------------------ PWM
def pwm(M, phi, mode):
    n_sw = int(round(F_SW / F1))
    t = np.arange(n_sw * NPTS) / (F_SW * NPTS)
    th = 2 * np.pi * F1 * t
    refs = np.array([M * np.sin(th - k * 2 * np.pi / 3) for k in range(3)])
    if mode == "SVM":
        refs = refs - 0.5 * (refs.max(axis=0) + refs.min(axis=0))
    carrier = 2 * np.abs(2 * ((t * F_SW) % 1.0) - 1) - 1
    s = (refs[0] > carrier).astype(float)
    i = I_PK * np.sin(th - phi)
    d = 0.5 * (1 + refs[0])
    return t, s, i, d, th


# ------------------------------------------------------------------ network
def build(names, br):
    nodes = sorted({n for b in br for n in b} | {"X"})
    gnd = "X"
    idx = {n: k for k, n in enumerate([n for n in nodes if n != gnd])}
    elems = [("cu", a, b, k) for k, (a, b) in enumerate(br)]
    for g, (p, n, *_r) in CAPS.items():
        elems.append(("cap", p, n, g))
    elems.append(("ext", "T_DCP", "X", None))
    elems.append(("ext", "T_DCN", "X", None))
    elems.append(("ref", "T_AC", "X", None))   # 1 MOhm: fixes the potential of the AC net (load = current source)
    return idx, elems, gnd


def solve(idx, elems, R, L, f, inj):
    """Modified nodal analysis; returns element currents (complex amplitudes). inj: {node: complex current in}."""
    w = 2 * math.pi * f
    nv, ne = len(idx), len(elems)
    nb = sum(1 for e in elems if e[0] == "cu")
    A = np.zeros((nv + ne, nv + ne), complex)
    rhs = np.zeros(nv + ne, complex)
    for k, (kind, a, b, ref) in enumerate(elems):
        col = nv + k
        for node, sg in ((a, 1.0), (b, -1.0)):
            if node in idx:
                A[idx[node], col] += sg
                A[col, idx[node]] += sg
        if kind == "cu":
            A[col, nv:nv + nb] -= R[ref] + 1j * w * L[ref]
        elif kind == "cap":
            _p, _n, cnt, C, esr, esl = CAPS[ref]
            if f == 0:
                A[col, col] = 1.0          # open circuit: force zero current
                for node, sg in ((a, 1.0), (b, -1.0)):
                    if node in idx:
                        A[col, idx[node]] = 0.0
            else:
                A[col, col] -= (esr + 1 / (1j * w * C) + 1j * w * esl) / cnt
        elif kind == "ref":
            A[col, col] -= 1e6
        else:
            A[col, col] -= EXT["R"] / 2 + 1j * w * EXT["L"] / 2
    for node, cur in inj.items():
        if node in idx:
            rhs[idx[node]] += cur
    return np.linalg.solve(A, rhs)[nv:]


def injections(a, i):
    """Node current injections for complex harmonic amplitudes a = (s i), i (load)."""
    b = i - a                                  # (1-s) i
    inj = {}
    for side in ("L", "R"):
        inj["QH_D_" + side] = inj.get("QH_D_" + side, 0) - a / 2
        inj["QH_S_" + side] = inj.get("QH_S_" + side, 0) + a / 2
        inj["QL_D_" + side] = inj.get("QL_D_" + side, 0) + b / 2
        inj["QL_S_" + side] = inj.get("QL_S_" + side, 0) - b / 2
    inj["T_AC"] = -i
    inj["X"] = i
    return inj


def copper(M, phi, mode, names, br, rl):
    t, s, i, d, th = pwm(M, phi, mode)
    a_t = s * i
    N = len(t)
    A = np.fft.rfft(a_t) / N
    I = np.fft.rfft(i) / N
    f = np.fft.rfftfreq(N, 1 / (F_SW * NPTS))
    amp = np.abs(A) ** 2 + np.abs(I) ** 2
    keep = np.where(amp > 1e-9 * amp.sum())[0]
    idx, elems, gnd = build(names, br)
    nb = len(br)
    nets = {"DCP": [k for k, n in enumerate(names) if n.startswith("DCP:")],
            "DCN": [k for k, n in enumerate(names) if n.startswith("DCN:")],
            "AC": [k for k, n in enumerate(names) if n.startswith("AC:")]}
    p_lf = {n: 0.0 for n in nets}
    p_hf = {n: 0.0 for n in nets}
    p_cap = {g: 0.0 for g in CAPS}
    i_cap2 = {g: 0.0 for g in CAPS}
    spec = []
    for k in keep:
        fk = float(f[k])
        scale = 1.0 if k == 0 else 2.0        # one-sided amplitude (peak) = 2 |X|
        R, L = rl(fk)
        x = solve(idx, elems, R, L, fk, injections(scale * A[k], scale * I[k]))
        ib = x[:nb]
        fac = 1.0 if k == 0 else 0.5
        tot = 0.0
        for n, ks in nets.items():
            p = fac * float(np.real(np.conj(ib[ks]) @ R[np.ix_(ks, ks)] @ ib[ks]))
            (p_lf if fk < F_SW / 2 else p_hf)[n] += p
            tot += p
        for e, (kind, *_r, ref) in enumerate(elems):
            if kind == "cap":
                cnt, esr = CAPS[ref][2], CAPS[ref][4]
                i_cap2[ref] += fac * abs(x[e]) ** 2
                p_cap[ref] += fac * abs(x[e]) ** 2 / cnt * esr
        spec.append((fk, tot))
    # device loss split (sinusoidal current, continuous PWM)
    return dict(M=M, pf=round(math.cos(phi), 3), mode=mode,
                cu_lf=p_lf, cu_hf=p_hf, cu_lf_total=sum(p_lf.values()), cu_hf_total=sum(p_hf.values()),
                cap_I_rms={g: math.sqrt(v) for g, v in i_cap2.items()}, cap_P=p_cap, cap_P_total=sum(p_cap.values()),
                spectrum=spec, bins=len(keep))


def device_split(M, phi, mode, pon, poff, rds_hot, n=2, t_dead=10e-9, vsd=1.95, rsd=5e-3):
    """Per-switch losses for QH and QL over one fundamental period (continuous PWM, sinusoidal current).
    Conduction: QH conducts d*i^2, QL (1-d)*i^2. Hard switching (Eon+Eoff) occurs in the switch that carries the
    load current in its forward direction: QH for i > 0 (current out of the leg), QL for i < 0. Dead time: the
    complementary switch reverse-conducts, i.e. QL for i > 0 and QH for i < 0."""
    _t, _s, i, d, th = pwm(M, phi, mode)
    r = rds_hot / n
    ia = np.abs(i)
    e = np.polyval(pon, ia) + np.polyval(poff, ia)
    pdead = 2 * F_SW * t_dead * (vsd * ia + rsd / n * ia ** 2)
    pos = i > 0
    out = {}
    for sw, cond, hard, dead in (("QH", d * i ** 2, pos, ~pos), ("QL", (1 - d) * i ** 2, ~pos, pos)):
        out[sw] = dict(cond=float(np.mean(cond) * r), sw=float(np.mean(np.where(hard, e, 0.0)) * F_SW),
                       dead=float(np.mean(np.where(dead, pdead, 0.0))))
        out[sw]["total"] = sum(out[sw].values())
    return out


def main():
    names, br, rl, src = load_rl()
    sz = json.load(open(os.path.join(REP, "data", "sizing.json")))
    rs = json.load(open(os.path.join(REP, "data", "results.json")))
    S = sz["spec"]
    rds_hot = S["Rds_25_typ"] * S["Rds_factor_100C"]
    pon, poff = np.array(rs["energy"]["fit_on"]), np.array(rs["energy"]["fit_off"])
    cases = [(1.0, 0.0, "SPWM"), (1.0, 0.0, "SVM"), (1.15, 0.0, "SVM"),
             (1.0, math.acos(0.8), "SPWM"), (1.0, math.acos(0.8), "SVM")]
    res = dict(source=src, ext=EXT, previous_dc_model_W=rs["P_cu"], cases=[])
    for M, phi, mode in cases:
        c = copper(M, phi, mode, names, br, rl)
        c["devices"] = device_split(M, phi, mode, pon, poff, rds_hot)
        res["cases"].append(c)
        print("%-4s M=%.2f pf=%.1f  Cu LF %.3f W  Cu HF %.3f W  (%s)  caps %.3f W  | QH %.2f W  QL %.2f W" % (
            mode, M, math.cos(phi), c["cu_lf_total"], c["cu_hf_total"],
            ", ".join("%s %.3f" % (k, v) for k, v in c["cu_hf"].items()), c["cap_P_total"],
            c["devices"]["QH"]["total"], c["devices"]["QL"]["total"]))
    # sensitivity: modulation index (SVM) and switching frequency (SVM, M = 1, pf = 1)
    global F_SW
    res["vs_M"] = []
    for pf in (1.0, 0.8):
        for M in (0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.15):
            c = copper(M, math.acos(pf), "SVM", names, br, rl)
            res["vs_M"].append(dict(M=M, pf=pf, cu_lf=c["cu_lf_total"], cu_hf=c["cu_hf_total"], caps=c["cap_P_total"]))
            print("vs M: pf=%.1f M=%.2f  LF %.3f  HF %.3f  caps %.3f" % (pf, M, c["cu_lf_total"], c["cu_hf_total"], c["cap_P_total"]))
    res["vs_f"] = []
    for fsw in (20e3, 50e3, 100e3, 200e3):
        F_SW = fsw
        c = copper(1.0, 0.0, "SVM", names, br, rl)
        res["vs_f"].append(dict(f=fsw, cu_lf=c["cu_lf_total"], cu_hf=c["cu_hf_total"], caps=c["cap_P_total"]))
        print("vs f: %3.0f kHz  LF %.3f  HF %.3f  caps %.3f" % (fsw / 1e3, c["cu_lf_total"], c["cu_hf_total"], c["cap_P_total"]))
    F_SW = 50e3
    json.dump(res, open(os.path.join(REP, "data", "copper_hf.json"), "w"), indent=1, default=float)

    # figure: R(f) of the main paths and copper-loss spectrum
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    fr = np.logspace(2, 8, 200)
    for lab in ("DCP:QH_D_L", "DCN:QL_S_L", "AC:QH_S_L", "DCP:CapPL", "DCP:CapB1P"):
        k = names.index(lab)
        ax[0].loglog(fr, [rl(x)[0][k, k] * 1e3 for x in fr], label=lab)
    ax[0].axvline(F_SW, color="k", ls=":", lw=0.8)
    ax[0].set_xlabel("frequency [Hz]")
    ax[0].set_ylabel("branch self resistance [m$\\Omega$]")
    ax[0].set_title("Q3D copper resistance vs frequency (%s)" % ("sweep" if src.startswith("q3d") else "placeholder"),
                    fontsize=9)
    ax[0].legend(fontsize=7)
    c = res["cases"][1]
    sf = np.array(c["spectrum"])
    ax[1].bar(range(2), [c["cu_lf_total"], c["cu_hf_total"]], color=["C0", "C1"])
    ax[1].set_xticks(range(2))
    ax[1].set_xticklabels(["< f$_{sw}$/2 (load current)", "$\\geq$ f$_{sw}$/2 (switching harmonics)"])
    ax[1].set_ylabel("PCB copper loss per leg [W]")
    ax[1].set_title("SVM, M = 1, cos$\\varphi$ = 1, 50 kHz", fontsize=9)
    for x, v in enumerate([c["cu_lf_total"], c["cu_hf_total"]]):
        ax[1].text(x, v, "%.3f W" % v, ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(REP, "figures", "copper_hf.pdf"))
    fig.savefig(os.path.join(REP, "figures", "copper_hf.png"), dpi=130)
    print("R/L source:", src, "| previous DC model:", round(rs["P_cu"], 3), "W")


if __name__ == "__main__":
    main()

"""
DPT sequence on the board's own DC link (independent review 2026-11-04, item S1): L_load 1 uH, 80 V pre-charge, no bulk
capacitor. Variant of revb_q3d_spice.py, which is imported and NOT changed; nothing is written to simulation/bb_spice
itself or to reports/slides/data.

    python simulation/bb_q3d/revb_q3d_spice_dpt1uh.py run  [case ...]   build + LTspice (parallel) -> simulation/bb_spice/dpt_1uH_80V/
    python simulation/bb_q3d/revb_q3d_spice_dpt1uh.py post [case ...]   read .raw -> dpt_1uH_80V/results.json, results.csv

Each deck is the text that revb_q3d_spice.netlist() produces for ("dpt", R_g,on 3.5 Ohm, extracted gate), with only:
  - the sequence parameters (VBUS, TON1, LLOAD, TOFF, TON2),
  - the Q3D matrix (tag dpt_swv1 = current board; "dpt" = 2026-10-22 matrix of the committed result),
  - the supply: "V1 + Cbulk 1 mF + Lbus 20 nH" -> "V1 + Rchg 1 kOhm" (bank charged at the .op point, supply effectively
    disconnected during the pulses: 6 V sag -> 6 mA),
  - optional scaling of bank and bypass C, a longer .save list and the .include path (one folder deeper).
"""
import csv
import json
import os
import re
import subprocess
import sys
import time

import numpy as np
from scipy.signal import lfilter, medfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revb_q3d_spice as base                     # noqa: E402  (guarded main, nothing runs on import)

OUT = os.path.join(base.ROOT, "simulation", "bb_spice", "dpt_1uH_80V")
base.SP = OUT                                     # netlist(), run(), meas() now work in the new folder only
TAG_NEW, TAG_OLD = "BB_PL_LOOP_dpt_swv1", "BB_PL_LOOP_dpt"
L_OLD = 10.667e-6 * 75 / 322.0                    # 2.4845 uH, the committed LLOAD
PAR = 5                                           # LTspice runs at a time
TRIM = os.path.join(OUT, "trim.json")             # measured pulse lengths {"B": s, "D": s}
_trim = json.load(open(TRIM)) if os.path.exists(TRIM) else {}
TON_B = _trim.get("B", 4.1e-6)
TON_D = _trim.get("D", 11.5e-6)


def case(tag=TAG_NEW, bulk=False, v=80.0, ton=None, l=1e-6, toff=0.75e-6, ton2=0.3e-6, cs=1.0, tail=0.3e-6, maxstep=0.1e-9, skew=0.0, lac=1.0, msign=1):
    return dict(tag=tag, bulk=bulk, v=v, ton=TON_B if ton is None else ton, l=l, toff=toff, ton2=ton2, cs=cs, tail=tail,
                maxstep=maxstep, skew=skew, lac=lac, msign=msign)


CASES = {
    "A_ref_oldmatrix": case(TAG_OLD, True, 75.0, 10.667e-6, L_OLD, 1e-6, 0.5e-6),
    "A_ref_swv1": case(TAG_NEW, True, 75.0, 10.667e-6, L_OLD, 1e-6, 0.5e-6),
    "B": case(),
    "B_oldmatrix": case(TAG_OLD),
    "B_tail": case(tail=130e-6, maxstep=2e-9),         # end of the burst: same deck, longer .tran, coarser maximum step
    "C_L1u2": case(l=1.2e-6),
    "C_bank_m20": case(cs=0.8),
    "C_bank_p20": case(cs=1.2),
    "C_off0u5": case(toff=0.5e-6),
    "C_off1u": case(toff=1.0e-6),
    # U1-U2 skew: PWM of pair B (cells 3, 4, driver U2) later than pair A (cells 1, 2, U1) on every edge; negative = pair A later.
    # The deck's Lac = 1 nH per cell (placeholder, pair to pair 1 nH) is far below the extraction: BB_PL_LX_dpt gives 27 to 60 nH
    # between switch nodes and 22.5 nH between the tied pairs (before the SW vias; x 7.5/9.7 from the swac sub-model = 17 nH).
    # Lac = 18 nH per cell gives 18 nH pair to pair, 36 nH cell to cell. The S_* cases at 1 nH are kept only as the bound.
    "B_Lac18": case(lac=18.0),
    "L18_skew1": case(skew=1e-9, lac=18.0),
    "L18_skew2": case(skew=2e-9, lac=18.0),
    "L18_skew3": case(skew=3e-9, lac=18.0),
    "L18_skew6": case(skew=6e-9, lac=18.0),
    "L18_skew9": case(skew=9e-9, lac=18.0),
    "L18_skew13": case(skew=13e-9, lac=18.0),
    "L18_skew13_Alate": case(skew=-13e-9, lac=18.0),
    "S_skew3": case(skew=3e-9),
    "S_skew6": case(skew=6e-9),
    "S_skew9": case(skew=9e-9),
    "S_skew13": case(skew=13e-9),
    "S_skew13_Alate": case(skew=-13e-9),
    # the commutation-to-gate coupling sources Bm: off (msign 0) and flipped (-1), to separate the cell-to-cell oscillation
    # seen in the L18_skew cases from the skew itself
    "M0_skew0": case(lac=18.0, msign=0),
    "M0_skew1": case(skew=1e-9, lac=18.0, msign=0),
    "M0_skew2": case(skew=2e-9, lac=18.0, msign=0),
    "M0_skew3": case(skew=3e-9, lac=18.0, msign=0),
    "M0_skew6": case(skew=6e-9, lac=18.0, msign=0),
    "M0_skew9": case(skew=9e-9, lac=18.0, msign=0),
    "M0_skew13": case(skew=13e-9, lac=18.0, msign=0),
    "Mneg_skew3": case(skew=3e-9, lac=18.0, msign=-1),
    "Mneg_skew13": case(skew=13e-9, lac=18.0, msign=-1),
    "D_2u48_unchanged": case(v=75.0, ton=10.667e-6, l=L_OLD, toff=1e-6, ton2=0.5e-6),
    "D_2u48_to322A": case(v=75.0, ton=TON_D, l=L_OLD, toff=1e-6, ton2=0.5e-6),
}


def build(name):
    c = CASES[name]
    base.MODELS["dpt"] = c["tag"]
    src = base.netlist("dpt", base.RG_BOARD, True)          # -> OUT/REVB_Q3D_dpt.cir (temporary name)
    p = os.path.join(OUT, src)
    txt = open(p).read()
    os.remove(p)
    txt = txt.replace(".include ../LMG1210-EPC2361/EPC2361.lib", ".include ../../LMG1210-EPC2361/EPC2361.lib")
    txt, k = re.subn(r"^\.param VBUS=.*$", ".param VBUS=%.6g IPK=322 TON1=%.7g LLOAD=%.7g" % (c["v"], c["ton"], c["l"]),
                     txt, flags=re.M)
    assert k == 1
    txt, k = re.subn(r"^\.param TSTART=.*$", ".param TSTART=0.5u TOFF=%.6g TON2=%.6g" % (c["toff"], c["ton2"]), txt, flags=re.M)
    assert k == 1
    if c["msign"] != 1:
        rep = (lambda m: m.group(1) + "0") if c["msign"] == 0 else (lambda m: m.group(1) + "-(" + m.group(2) + ")")
        txt, k = re.subn(r"^(Bm\S+ \S+ \S+ V=)(.*)$", rep, txt, flags=re.M)
        assert k == 8, k
    if c["lac"] != 1.0:
        txt, k = re.subn(r"^(Lac\d QH_S_\d ACO )1n( Rser=0\.1m)$", lambda m: "%s%gn%s" % (m.group(1), c["lac"], m.group(2)), txt, flags=re.M)
        assert k == 4
    if c["skew"]:
        pat = r"\{(TSTART(?:\+1n)?|T1(?:\+1n)?|T2(?:\+1n)?|T2\+TON2(?:\+1n)?)\}"
        src = "VLOB" if c["skew"] > 0 else "VLOA"

        def sk(m):
            return re.sub(pat, lambda q: "{%s+%gn}" % (q.group(1), abs(c["skew"]) * 1e9), m.group(0))
        txt, k = re.subn(r"^%s .*$" % src, sk, txt, flags=re.M)
        assert k == 1
    if c["tail"] != 0.3e-6 or c["maxstep"] != 0.1e-9:
        txt, k = re.subn(r"TEND=\{T2\+TON2\+0\.3u\}", "TEND={T2+TON2+%g}" % c["tail"], txt)
        assert k == 1
        txt, k = re.subn(r"^\.tran 0 \{TEND\} 0 0\.1n$", ".tran 0 {TEND} 0 %g" % c["maxstep"], txt, flags=re.M)
        assert k == 1
    if not c["bulk"]:
        txt, k = re.subn(r"^Cbulk VS 0 1m Rser=20m\nLbus VS BP 20n Rser=2m$", "Rchg VS BP 1k", txt, flags=re.M)
        assert k == 1
    if c["cs"] != 1.0:
        def sc(m):
            return "%s%.5gu%s" % (m.group(1), float(m.group(2)) * c["cs"], m.group(3))
        txt, k = re.subn(r"^((?:Cbank|CCapPb?_\d) \S+ \S+ )([0-9.]+)u( .*)$", sc, txt, flags=re.M)
        assert k == 9, k
    extra = ["V(BP)", "V(BN)"] + ["V(CapP_%d)" % i for i in range(1, 5)] + ["V(CapN_%d)" % i for i in range(1, 5)] + \
            ["I(Lac%d)" % i for i in range(1, 5)] + ["V(RSI_%d)" % i for i in range(1, 5)]
    txt, k = re.subn(r"^\.save (.*)$", lambda m: ".save " + m.group(1) + " " + " ".join(extra), txt, flags=re.M)
    assert k == 1
    txt = txt.replace("* Leg board 'dpt'", "* DPT 1 uH/80 V study, case %s (generated from revb_q3d_spice.netlist): Leg board 'dpt'" % name, 1)
    open(os.path.join(OUT, name + ".cir"), "w").write(txt)
    return name + ".cir"


def run_all(names):
    todo = [(n, build(n)) for n in names]
    live = []
    while todo or live:
        while todo and len(live) < PAR:
            n, cir = todo.pop(0)
            print("start", n, flush=True)
            live.append((n, subprocess.Popen([base.LTS, "-b", os.path.join(OUT, cir)], cwd=OUT), time.time()))
        time.sleep(2)
        for it in live[:]:
            if it[1].poll() is not None:
                print("done ", it[0], "%.0f s" % (time.time() - it[2]), flush=True)
                live.remove(it)


# ------------------------------------------------------------------ raw reader
def read_raw(path):
    b = open(path, "rb").read()
    mark = "Binary:\n".encode("utf-16-le")
    i = b.index(mark)
    head = b[:i].decode("utf-16-le")
    nv = int(re.search(r"No\. Variables:\s*(\d+)", head).group(1))
    npt = int(re.search(r"No\. Points:\s*(\d+)", head).group(1))
    names = [l.split("\t")[2] for l in head.split("Variables:\n")[1].splitlines() if l.strip()]
    assert len(names) == nv
    d = np.frombuffer(b, dtype=np.dtype([("t", "<f8"), ("v", "<f4", (nv - 1,))]), count=npt, offset=i + len(mark))
    t = np.abs(d["t"]).copy()
    v = d["v"].astype(float)
    return t, {n.lower(): v[:, k - 1] for k, n in enumerate(names) if k}


def uniform(t, x, dt=0.05e-9):
    tu = np.arange(t[0], t[-1], dt)
    return tu, np.interp(tu, t, x)


MASK = []                                         # solver-fault windows of the current case, set in post()


def good(t):
    """False inside the solver-fault windows. At the first turn-on (load current near 0) V_DS and the LS current ring
    through zero, where the EPC model has an if() branch; in some decks the solver then takes 1e-18 s steps, produces one
    1e9 V sample and the kick rings for about 400 ns. Not physical, gone well before T1, so it is cut out of every peak."""
    g = np.ones(len(t), bool)
    for a, b in MASK:
        g &= ~((t >= a) & (t <= b))
    return g


def find_mask(t, vmax):
    seeds = t[vmax > 1000.0]                      # solver values only; a real overshoot must never be masked
    out = []
    for x in seeds:
        if out and x - out[-1][1] < 500e-9:
            out[-1][1] = float(x)
        else:
            out.append([float(x), float(x)])
    return [(a - 1e-9, b + 500e-9) for a, b in out]


def clean(t, x, a, b, dt=0.1e-9, k=5):
    """uniform grid + 0.5 ns running median: removes the femtosecond-step solver spikes (one to five samples, see A at
    the first turn-on), keeps the ring (period about 7 ns)"""
    m = (t >= a) & (t <= b) & good(t)
    if m.sum() < 8:
        return np.array([a]), np.array([np.nan])  # window lost to a solver fault
    tu, xu = uniform(t[m], x[m], dt)
    return tu, medfilt(xu, k)


def box(x, n):
    return np.convolve(x, np.ones(n) / n, "same")


class W:
    def __init__(self, t, d):
        self.t, self.d = t, d

    def __call__(self, n):
        return self.d[n.lower()]

    def vd(self, a, b):
        return self.d[a.lower()] - self.d[b.lower()]

    def at(self, x, t0):
        return float(np.interp(t0, self.t, x))

    def win(self, a, b):
        return (self.t >= a) & (self.t <= b)

    def mx(self, x, a, b):
        return float(x[self.win(a, b)].max())

    def mn(self, x, a, b):
        return float(x[self.win(a, b)].min())

    def integ(self, y, a, b):
        m = self.win(a, b)
        return float(np.trapezoid(y[m], self.t[m]))

    def cmx(self, x, a, b):
        return float(clean(self.t, x, a, b)[1].max())

    def cmn(self, x, a, b):
        return float(clean(self.t, x, a, b)[1].min())

    def settle(self, x, a, b, band):
        """fast loop ring only: signal minus its 20 ns running mean (removes the 1.3 MHz row ring and the ramp).
        Returns (time after a of the last excursion beyond +-band or 0, ring amplitude in the last 40 ns of [a, b])"""
        tt, xx = clean(self.t, x, a, b)
        if len(tt) < 400:
            return float("nan"), float("nan")
        e = np.abs(xx - box(xx, 200))[100:-100]        # drop the ends of the running mean
        tt = tt[100:-100]
        idx = np.nonzero(e > band)[0]
        q = e[tt >= b - 50e-9]
        return (0.0 if len(idx) == 0 else float(tt[idx[-1]] - a)), (float(q.max()) if len(q) else float("nan"))


# EPC2361 datasheet Fig. 12, single pulse, read off by eye (+-30 %), in K/W: Zjb x R_thJB 1.5, Zjc x R_thJC 0.2
ZTH_T = np.array([1e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1])
ZJB = 1.5 * np.array([7e-4, 0.007, 0.02, 0.05, 0.08, 0.14, 0.32, 0.65, 0.92, 1.0])
ZJC = 0.2 * np.array([0.015, 0.08, 0.13, 0.2, 0.4, 0.68, 0.9, 1.0, 1.0, 1.0])


def tail(w, c, T1, T2, T3, TE, vh, iload, bus):
    t = w.t
    r = {}
    after = t > T3 + 100e-9
    i3 = r["I_T3peak"] = w.mx(iload, T3 - 50e-9, T3 + 150e-9)
    z = np.nonzero(after & (iload <= 0))[0]
    r["reached_zero"] = bool(len(z))
    tz = float(t[z[0]]) if len(z) else TE
    r["t_zero_after_T3_us"] = (tz - T3) * 1e6
    r["t_50pct_after_T3_us"] = (float(t[np.nonzero(after & (iload <= 0.5 * i3))[0][0]]) - T3) * 1e6
    r["I_at_T3plus300ns"] = w.at(iload, T3 + 300e-9)
    r["E_L_at_T3_mJ"] = 0.5 * c["l"] * i3 ** 2 * 1e3
    r["dIdt_start_A_us"] = (w.at(iload, T3 + 300e-9) - w.at(iload, T3 + 5.3e-6)) / 5.0
    r["dIdt_end_A_us"] = (w.at(iload, tz - 6e-6) - w.at(iload, tz - 1e-6)) / 5.0
    r["V_HS_rev_at_start"] = float(np.mean([w.at(vh[i], T3 + 300e-9) for i in vh]))
    r["V_HS_rev_at_half"] = float(np.mean([w.at(vh[i], T3 + 0.5 * (tz - T3)) for i in vh]))
    grid = np.arange(T3 + 100e-9, tz, 20e-9)
    p = {}
    for i in vh:
        pw = vh[i] * w("I(VIH%d)" % i)                     # both negative in reverse conduction
        p[i] = np.interp(grid, t, pw)
        r["E_HS%d_tail_mJ" % i] = w.integ(pw, T3 + 100e-9, tz) * 1e3
        r["E_HS%d_offtime_mJ" % i] = w.integ(pw, T1, T2) * 1e3
    r["E_HS_tail_sum_mJ"] = sum(r["E_HS%d_tail_mJ" % i] for i in vh)
    r["E_HS_offtime_sum_mJ"] = sum(r["E_HS%d_offtime_mJ" % i] for i in vh)
    r["P_HS_peak_W"] = max(float(p[i].max()) for i in vh)
    r["I_HS_cells_T3plus5us"] = [-w.at(w("I(Lac%d)" % i), T3 + 5e-6) for i in vh]
    # junction rise: convolution of the power of the hottest FET with dZ/dt (datasheet Fig. 12)
    hot = max(p, key=lambda i: r["E_HS%d_tail_mJ" % i])
    dt = 20e-9
    tt = np.arange(1, len(grid) * 2) * dt
    res = {}
    for nm, Z in (("jb", ZJB), ("max_jb_jc", np.maximum(ZJB, ZJC))):
        zt = np.exp(np.interp(np.log(tt), np.log(ZTH_T), np.log(Z)))
        h = np.diff(np.r_[0, zt])
        dT = np.convolve(p[hot], h)[:len(tt)]
        res[nm] = dict(dT_peak_K=float(dT.max()), t_peak_us=float(tt[np.argmax(dT)] * 1e6))
    r["thermal"] = res
    e = w.win(tz, TE)
    r["after_zero_us"] = (TE - tz) * 1e6
    if e.sum() > 10:
        hs = sum(vh[i] for i in vh) / 4
        r["HS_VDS_after_zero_max"] = float(hs[e].max())
        r["HS_VDS_after_zero_min"] = float(hs[e].min())
        r["LS_VDS_after_zero_max"] = max(float(w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i)[e].max()) for i in vh)
        r["LS_VDS_after_zero_min"] = min(float(w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i)[e].min()) for i in vh)
        r["I_after_zero_absmax"] = float(np.abs(iload[e]).max())
    r["bus_T3"], r["bus_tz"], r["bus_end"] = w.at(bus, T3), w.at(bus, tz), w.at(bus, TE)
    r["bus_max_after_T3"] = float(bus[w.win(T3, TE)].max())
    return r


def lp1(x, dt, fc):
    a = 1 - np.exp(-2 * np.pi * fc * dt)
    y, _ = lfilter([a], [1, -(1 - a)], x, zi=[x[0] * (1 - a)])
    return y


def ringf(t, x, a, b):
    """dominant frequency of the fast ring in [a, b] (signal minus its 20 ns running mean), Hz"""
    tu, xu = uniform(t[(t >= a) & (t <= b)], x[(t >= a) & (t <= b)], 0.1e-9)
    e = (xu - box(xu, 200))[100:-100]
    f = np.fft.rfftfreq(len(e) * 8, 0.1e-9)
    sp = np.abs(np.fft.rfft(e * np.hanning(len(e)), len(e) * 8))
    return float(f[np.argmax(sp * (f > 30e6))])


def port(w, vl, vh, row, T0, T1, T2, T3, TE):
    """What the bench reads on the LS V_DS port: Q3D has no terminal at the MMCX, so the drain side is bounded by the two
    AC-net nodes (QL_D = LS drain pad, QH_S = HS source pad / AC sink), the return is the LSRC via in the shunt IN land = RSI node
    (electrical review S3). Filters: first-order 100 / 200 MHz on a 0.05 ns grid. No probe or cable loading, no cable ringing."""
    t = w.t
    cells = (1, 2, 3, 4)
    dt = 0.05e-9
    out = {}
    for ev, a, b in (("off1", T1, T1 + 150e-9), ("off2", T3, min(T3 + 150e-9, TE))):
        o = {}
        for nm, f in (("die", lambda i: vl[i]), ("port_QLD_RSI", lambda i: w.vd("V(QL_D_%d)" % i, "V(RSI_%d)" % i)),
                      ("port_QHS_RSI", lambda i: w.vd("V(QH_S_%d)" % i, "V(RSI_%d)" % i))):
            for fc, lab in ((None, ""), (200e6, "_200MHz"), (100e6, "_100MHz")):
                pk = []
                for i in cells:
                    m = w.win(a - 200e-9, b)
                    tu, xu = uniform(t[m], f(i)[m], dt)
                    if fc:
                        xu = lp1(xu, dt, fc)
                    pk.append(float(xu[tu >= a].max()))
                o[nm + lab] = pk
        # plateau: mean of the die signal 40 to 60 ns after the edge region
        o["plateau"] = [float(vl[i][w.win(a + 60e-9, a + 100e-9)].mean()) for i in cells]
        o["ring_MHz"] = ringf(t, vl[1], a + 40e-9, min(a + 240e-9, TE)) / 1e6
        out[ev] = o
    out["ring_on2_HS_MHz"] = ringf(t, vh[1], T2 + 35e-9, T3) / 1e6
    out["ring_on1_HS_MHz"] = ringf(t, vh[1], T0 + 35e-9, T0 + 300e-9) / 1e6
    return out


def post(name):
    c = CASES[name]
    t, d = read_raw(os.path.join(OUT, name + ".raw"))
    w = W(t, d)
    T0 = 0.5e-6
    T1 = T0 + c["ton"]
    T2 = T1 + c["toff"]
    T3 = T2 + c["ton2"]
    TE = float(t[-1])
    cells = (1, 2, 3, 4)
    vl = {i: w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in cells}
    vh = {i: w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in cells}
    il = {i: w("I(VIL%d)" % i) for i in cells}
    gl = {i: w.vd("V(gL%d)" % i, "V(QL_S_%d)" % i) for i in cells}
    gh = {i: w.vd("V(gH%d)" % i, "V(QH_S_%d)" % i) for i in cells}
    iload = -w("I(Lload)")
    bus = w.vd("V(BP)", "V(BN)")
    row = sum(w.vd("V(CapP_%d)" % i, "V(CapN_%d)" % i) for i in cells) / 4
    W150 = 150e-9
    MASK[:] = find_mask(t, np.max([np.abs(vh[i]) for i in cells] + [np.abs(vl[i]) for i in cells], axis=0))
    W70 = 70e-9                                   # first turn-on: peak window ends before the first solver fault (+80 ns)
    r = dict(case=name, matrix=c["tag"], bulk_1mF=c["bulk"], L_load_uH=c["l"] * 1e6, V_precharge=c["v"], TON1_us=c["ton"] * 1e6,
             TOFF_us=c["toff"] * 1e6, TON2_ns=c["ton2"] * 1e9, C_scale=c["cs"])
    r["solver_fault_windows_ns"] = [[round(x * 1e9, 1) for x in q] for q in MASK]
    r["bus_t0"] = w.at(bus, 1e-9)
    r["bus_T1"] = w.at(bus, T1)
    r["bus_T2"] = w.at(bus, T2)
    r["bus_T3"] = w.at(bus, T3)
    r["bus_end"] = w.at(bus, TE)
    # bypass row (at the cells), 50 ns mean before the edges
    r["row_T1"] = float(row[w.win(T1 - 50e-9, T1)].mean())
    r["row_T2"] = float(row[w.win(T2 - 50e-9, T2)].mean())
    r["I_T1_edge"] = w.at(iload, T1)
    wp = w.win(T1 - 50e-9, T1 + W150)
    r["I_T1_peak"] = float(iload[wp].max())
    r["t_Ipk_after_edge_ns"] = (float(t[wp][np.argmax(iload[wp])]) - T1) * 1e9
    r["I_cell_T1"] = [w.at(il[i], T1) for i in cells]
    r["I_T2"] = w.at(iload, T2)
    r["I_cell_T2_HS"] = [-w.at(w("I(Lac%d)" % i), T2) for i in cells]
    r["I_T3_edge"] = w.at(iload, T3)
    r["I_T3_peak"] = w.mx(iload, T3 - 50e-9, min(T3 + W150, TE))
    r["I_cell_T3"] = [w.at(il[i], T3) for i in cells]
    r["I_decay_off"] = r["I_T1_peak"] - r["I_T2"]
    r["I_decay_A_per_us"] = (w.at(iload, T1 + 200e-9) - w.at(iload, T2)) / (T2 - T1 - 200e-9) * 1e-6
    r["V_HS_DS_end_off"] = float(np.mean([vh[i][w.win(T2 - 100e-9, T2)].mean() for i in cells]))
    # voltages
    r["VLS_pk_off1"] = max(w.cmx(vl[i], T1, T1 + W150) for i in cells)
    r["VLS_pk_off2"] = max(w.cmx(vl[i], T3, min(T3 + W150, TE)) for i in cells)
    r["VLS_pk_all"] = max(w.cmx(vl[i], 0, TE) for i in cells)
    r["VHS_pk_on1"] = max(w.cmx(vh[i], T0, T0 + W70) for i in cells)
    r["VHS_pk_on2"] = max(w.cmx(vh[i], T2, T2 + W150) for i in cells)
    r["VHS_pk_all"] = max(w.cmx(vh[i], 0, TE) for i in cells)
    r["VHS_pk_on2_cells"] = [w.cmx(vh[i], T2, T2 + W150) for i in cells]
    r["raw_peaks"] = dict(VHS_on1=max(w.mx(vh[i], T0, T0 + W70) for i in cells), VHS_on2=max(w.mx(vh[i], T2, T2 + W150) for i in cells),
                          VLS_off1=max(w.mx(vl[i], T1, T1 + W150) for i in cells),
                          VLS_off2=max(w.mx(vl[i], T3, min(T3 + W150, TE)) for i in cells),
                          VHS_all=max(float(vh[i].max()) for i in cells), VLS_all=max(float(vl[i].max()) for i in cells))
    # 1.3 MHz ring between the bypass rows and L_b: row voltage excursion in the off-time
    rl = row[w.win(T1, T2)]
    r["row_off_max"], r["row_off_min"] = float(rl.max()), float(rl.min())
    # per-FET peaks for the sharing check (first and second turn-on / turn-off)
    sk = abs(c["skew"]) + 60e-9
    r["I_FET_pk"] = dict(on1=[w.cmx(il[i], T0, T0 + W70) for i in cells], off1=[w.cmx(il[i], T1 - 10e-9, T1 + sk) for i in cells],
                         on2=[w.cmx(il[i], T2, T2 + W150) for i in cells], off2=[w.cmx(il[i], T3 - 10e-9, T3 + sk) for i in cells])
    r["VLS_cells"] = dict(off1=[w.cmx(vl[i], T1, T1 + W150) for i in cells], off2=[w.cmx(vl[i], T3, min(T3 + W150, TE)) for i in cells])
    r["VHS_cells"] = dict(on1=[w.cmx(vh[i], T0, T0 + W70) for i in cells], on2=[w.cmx(vh[i], T2, T2 + W150) for i in cells])
    r["VLS_raw_cells"] = dict(off1=[w.mx(vl[i], T1, T1 + W150) for i in cells], off2=[w.mx(vl[i], T3, min(T3 + W150, TE)) for i in cells])
    r["VHS_raw_cells"] = dict(on1=[w.mx(vh[i], T0, T0 + W70) for i in cells], on2=[w.mx(vh[i], T2, T2 + W150) for i in cells])
    if "v(rsi_1)" in d and not c["skew"]:
        r["port"] = port(w, vl, vh, row, T0, T1, T2, T3, TE)
    # energy: same definition as the committed deck: V_DS x I(drain pin), 150 ns from the PWM edge, sum of the four LS FETs

    def e(a, b):
        return [w.integ(vl[i] * il[i], a, b) * 1e6 for i in cells]
    r["Eon_cells"], r["Eoff_cells"] = e(T2, T2 + W150), e(T1, T1 + W150)
    r["Eon"], r["Eoff"] = sum(r["Eon_cells"]), sum(r["Eoff_cells"])
    r["Eon1_I0"] = sum(e(T0, T0 + W70))              # to +70 ns: before any solver fault
    r["Eoff2"] = sum(e(T3, min(T3 + W150, TE)))
    r["Eon_50ns"] = sum(e(T2, T2 + 50e-9))
    r["Eon_100ns"] = sum(e(T2, T2 + 100e-9))
    r["Eon_250ns"] = sum(e(T2, min(T2 + 250e-9, T3)))

    # di/dt, dv/dt: max slope over 1 ns, per FET (A/ns, V/ns)
    def slope(x, a, b, sgn):
        m = w.win(a, b)
        tu, xu = uniform(t[m], x[m])
        n = 20
        return float((sgn * (xu[n:] - xu[:-n])).max())
    r["didt_on"] = max(slope(il[i], T2, T2 + W150, 1) for i in cells)
    r["didt_off"] = max(slope(il[i], T1, T1 + W150, -1) for i in cells)
    r["dvdt_on"] = max(slope(vl[i], T2, T2 + W150, -1) for i in cells)
    r["dvdt_off"] = max(slope(vl[i], T1, T1 + W150, 1) for i in cells)
    # gate (package pin to source pin of the model; the 0.4 Ohm rg of the model is inside)
    r["HS_bump_on2"] = max(w.cmx(gh[i], T2, T2 + W150) for i in cells)
    r["HS_bump_on1"] = max(w.cmx(gh[i], T0, T0 + W150) for i in cells)
    r["HS_VGS_max"] = max(w.cmx(gh[i], 0, TE) for i in cells)
    r["HS_VGS_min"] = min(w.cmn(gh[i], 0, TE) for i in cells)
    off = w.win(T1 + 60e-9, T2 - 1e-9)                      # LS gate off, after the turn-off edge
    r["LS_VGS_max"] = max(w.cmx(gl[i], 0, TE) for i in cells)
    r["LS_VGS_min"] = min(w.cmn(gl[i], 0, TE) for i in cells)
    r["LS_VGS_offstate_max"] = max(float(gl[i][off].max()) for i in cells)
    # turn-on timing and settling of the second pulse (worst cell)
    r["ton_delay_ns"] = None
    m = w.win(T2, T3)
    for i in cells:
        k = np.nonzero(vl[i][m] < 0.1 * r["bus_T2"])[0]
        if len(k):
            r["ton_delay_ns"] = max(r["ton_delay_ns"] or 0, (float(t[m][k[0]]) - T2) * 1e9)
    S = {}
    # fast loop ring, worst cell; t is from the PWM edge; the first 35 to 45 ns (switching edge itself) are excluded
    for key, sig, e0, off0, b, band in (("LS_VDS_after_off1_2V", vl, T1, 45e-9, T2, 2.0), ("LS_VDS_after_off1_5pct", vl, T1, 45e-9, T2, 3.75),
                                        ("HS_VDS_after_on2_2V", vh, T2, 35e-9, T3, 2.0), ("HS_VDS_after_on2_5pct", vh, T2, 35e-9, T3, 3.75),
                                        ("LS_I_after_on2_2A", il, T2, 35e-9, T3, 2.0), ("LS_I_after_on2_4A", il, T2, 35e-9, T3, 4.0),
                                        ("HS_VDS_after_on1_2V", vh, T0, 35e-9, T1, 2.0)):
        res = [w.settle(sig[i], e0 + off0, b, band) for i in cells]
        S[key] = dict(t_from_edge_ns=(max(x[0] for x in res) + off0) * 1e9, resid_end=max(x[1] for x in res))
    r["settle"] = S
    if c["tail"] > 1e-6:
        r["tail"] = tail(w, c, T1, T2, T3, TE, vh, iload, bus)
    m = base.meas(name + ".cir")
    r["meas_deck"] = dict(Eon=sum(m["eon%d" % i][0] for i in cells) * 1e6, Eoff=sum(m["eoff%d" % i][0] for i in cells) * 1e6,
                          VHpk=max(m["vhpk%d" % i][0] for i in cells), Vpk=max(m["vpk%d" % i][0] for i in cells),
                          didt_on=max(m["didton%d" % i][0] for i in cells) / 1e9,
                          didt_off=-min(m["didtoff%d" % i][0] for i in cells) / 1e9,
                          bump=max(m["bump%d" % i][0] for i in cells), Iload=m["iload"][0])
    return r


def read_limits(name="B"):
    """Reading limits: the fast part of the waveform (signal minus its 20 ns running mean) is scaled until the worst cell
    reaches 100 V at the die, then filtered first-order and read. Hand-side scaling of a simulated waveform: linear ring
    assumed. LS: as seen across the die and at the port bound. HS: die only, there is no HS port."""
    c = CASES[name]
    t, d = read_raw(os.path.join(OUT, name + ".raw"))
    w = W(t, d)
    T0 = 0.5e-6
    T1 = T0 + c["ton"]
    T2 = T1 + c["toff"]
    T3 = T2 + c["ton2"]
    TE = float(t[-1])
    dt = 0.05e-9
    cells = (1, 2, 3, 4)
    sig = {"LS_off1": ({i: w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in cells}, T1, T1 + 150e-9),
           "LS_off2": ({i: w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in cells}, T3, TE),
           "HS_on1": ({i: w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in cells}, T0, T0 + 70e-9),
           "HS_on2": ({i: w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in cells}, T2, T2 + 150e-9)}
    out = {}
    for ev, (v, a, b) in sig.items():
        o = {"die_as_simulated": 0.0}
        best = None
        for i in cells:
            m = w.win(a - 200e-9, b)
            tu, xu = uniform(t[m], v[i][m], dt)
            k = tu >= a
            if xu[k].max() > o["die_as_simulated"]:
                o["die_as_simulated"] = float(xu[k].max())
                best = (tu, xu, k)
        tu, xu, k = best
        ip = int(np.argmax(np.where(k, xu, -1e9)))
        r0 = int(np.nonzero(k & (xu > 0.8 * xu[ip]))[0][0])        # end of the rising edge; only the ring after it is scaled
        seg = xu[r0:]
        n = 200                                     # 20 ns running mean on the post-edge part (reflected at the edge)
        slow = xu.copy()
        slow[r0:] = box(np.pad(seg, n, mode="reflect"), 2 * n)[n:-n]
        fast = xu - slow
        o["base_at_peak"] = float(slow[ip])
        alpha = (100.0 - slow[ip]) / fast[ip]
        o["ring_scale_to_100V"] = float(alpha)
        for fc, lab in ((100e6, "100MHz"), (200e6, "200MHz"), (500e6, "500MHz")):
            o["read_as_simulated_" + lab] = float(lp1(xu, dt, fc)[k].max())
            o["read_when_die_100V_" + lab] = float(lp1(slow + alpha * fast, dt, fc)[k].max())
        out[ev] = o
    json.dump(out, open(os.path.join(OUT, "read_limits.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


def figure():
    """case B: whole shot and the three edges; case B_tail: decay of the load current"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    c = CASES["B"]
    t, d = read_raw(os.path.join(OUT, "B.raw"))
    w = W(t, d)
    T0 = 0.5e-6
    T1 = T0 + c["ton"]
    T2 = T1 + c["toff"]
    T3 = T2 + c["ton2"]
    cells = (1, 2, 3, 4)
    vl = [w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in cells]
    vh = [w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in cells]
    il = [w("I(VIL%d)" % i) for i in cells]
    row = sum(w.vd("V(CapP_%d)" % i, "V(CapN_%d)" % i) for i in cells) / 4
    bus = w.vd("V(BP)", "V(BN)")
    fig, ax = plt.subplots(3, 2, figsize=(11, 8))
    a = ax[0, 0]
    a.plot(t * 1e6, -w("I(Lload)"), "k", lw=1)
    a.set_ylabel("I_load (A)")
    b = a.twinx()
    b.plot(t * 1e6, bus, "C3", lw=1, label="bank")
    b.plot(t * 1e6, row, "C0", lw=.4, label="bypass rows")
    b.set_ylabel("V (V)")
    b.set_ylim(60, 100)
    b.legend(loc="lower right", fontsize=8)
    a.set_title("Case B: 1 uH, 80 V, board bank only (Q3D dpt_swv1)", fontsize=10)
    t2, d2 = read_raw(os.path.join(OUT, "B_tail.raw"))
    ax[0, 1].plot(t2 * 1e6, -d2["i(lload)"], "k", lw=1)
    ax[0, 1].set_ylabel("I_load (A)")
    ax[0, 1].set_title("Case B_tail: decay through HS reverse conduction", fontsize=10)
    for k, (nm, e, x, y, yl) in enumerate((("first turn-on, about 0 A", T0, vh, il, "HS V_DS"), ("first turn-off, 322 A", T1, vl, il, "LS V_DS"),
                                           ("second turn-on", T2, vh, il, "HS V_DS"), ("second turn-off, 340 A", T3, vl, il, "LS V_DS"))):
        a = ax[1 + k // 2, k % 2]
        m = w.win(e - 10e-9, e + 280e-9)
        for i in range(4):
            a.plot((t[m] - e) * 1e9, x[i][m], lw=.5)
        a.axhline(100, color="r", lw=.6, ls="--")
        a.set_ylabel(yl + " (V)")
        a.set_ylim(-10, 110)
        b = a.twinx()
        for i in range(4):
            b.plot((t[m] - e) * 1e9, y[i][m], lw=.4, color="0.6")
        b.set_ylabel("I_LS per FET (A)")
        a.set_title(nm, fontsize=10)
        a.set_xlabel("ns from PWM edge")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "case_B_waveforms.png"), dpi=130)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    names = sys.argv[2:] or list(CASES)
    if mode == "run":
        run_all(names)
    if mode == "build":
        for n in names:
            print(build(n))
    if mode == "figure":
        figure()
    if mode == "limits":
        read_limits()
    if mode == "post":
        p = os.path.join(OUT, "results.json")
        old = json.load(open(p)) if os.path.exists(p) else {}
        for n in names:
            old[n] = post(n)
        json.dump(old, open(p, "w"), indent=1)
        keys = [k for k, v in next(iter(old.values())).items() if not isinstance(v, (dict, list))]
        with open(os.path.join(OUT, "results.csv"), "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(keys)
            for r in old.values():
                wr.writerow([r.get(k) for k in keys])
        for n in names:
            print(json.dumps(old[n], indent=0))


if __name__ == "__main__":
    main()

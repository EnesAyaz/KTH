"""
R_ON x U1-U2 skew sweep for the staged DPT bring-up. Wraps simulation/bb_q3d/revb_q3d_spice_dpt1uh.py (not changed): same deck
(Q3D dpt_swv1, Lac 18 nH per cell, 1 uH, board bank, supply through 1 kOhm), output only in this folder.

    python run_ron_skew.py trim            short zero-skew runs, writes trim.json (first pulse per stage and R_ON)
    python run_ron_skew.py run  [regex]    LTspice for the cases matching regex (all if none), skips finished ones
    python run_ron_skew.py post [regex]    raw -> results.json, results.csv

Case names: <prefix>V<bus>_R<R_ON>_s<skew ns>, prefix M0_ = coupling sources Bm off. Skew: pair B (cells 3, 4, U2) late on every edge.
R_ON is R7, R9, R26, R28 (HS and LS channels): R_G,on = 0.5 + 2 R_ON per device. R_OFF 0 Ohm, D_OFF path unchanged.
"""
import csv
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "bb_q3d"))
import revb_q3d_spice_dpt1uh as m                 # noqa: E402

base = m.base
m.OUT = HERE
base.SP = HERE
m.PAR = 6
m.port = lambda *a: None                          # the probe study is not repeated here
TRIMF = os.path.join(HERE, "trim.json")
STAGES = {40: (100.0, 2.5e-6), 60: (200.0, 3.5e-6), 80: (322.0, 4.167e-6)}     # bus: target A, hand pulse
RONS = (1.5, 2.0, 3.0, 5.0)
SKEWS = (0.0, 1.0, 2.0, 3.0)
trim = json.load(open(TRIMF)) if os.path.exists(TRIMF) else {}


def tag(r):
    return ("%g" % r).replace(".", "p")


def name(v, r, s, m0=False):
    return "%sV%d_R%s_s%s" % ("M0_" if m0 else "", v, tag(r), tag(s))


def mk(v, r, s, m0=False):
    c = m.case(v=float(v), ton=trim.get("%d_%g" % (v, r), STAGES[v][1]), skew=s * 1e-9, lac=18.0, msign=0 if m0 else 1)
    c["rgon"] = 0.5 + 2 * r
    c["ron"], c["stage"], c["skew_ns"], c["bm"] = r, v, s, not m0
    return c


GRID = {}
for v in (80, 60, 40):                            # 80 V first: it must be complete
    for r in RONS:
        for s in SKEWS:
            GRID[name(v, r, s)] = mk(v, r, s)
for r in (1.5, 3.0):
    for s in (0.5, 1.5):
        GRID[name(80, r, s)] = mk(80, r, s)
for r in RONS:
    for s in SKEWS:
        GRID[name(80, r, s, True)] = mk(80, r, s, True)
for r in (1.5, 3.0):
    for s in (0.5, 1.5):
        GRID[name(80, r, s, True)] = mk(80, r, s, True)
for r in (2.0, 5.0):                              # added after the first 80 V result: the limit was below 1 ns there
    GRID[name(80, r, 0.5)] = mk(80, r, 0.5)
# diagnostic cases, 80 V. X_Rg: same R_G,on 3.5 Ohm but R_G 1.5 Ohm per FET and R_ON 1 Ohm (the shared R_ON does not damp the mode
# between the two gates of a pair, R_G does). X_Vf: D_OFF with 0.3 V forward drop instead of the ideal 0 V of the deck.
for sk in (1.0, 2.0, 3.0):
    c = mk(80, 1.5, sk)
    c["rg"], c["ron"] = 1.5, 1.0
    GRID["X_Rg1p5_R1_s%s" % tag(sk)] = c
for r in (1.5, 3.0, 5.0):
    c = mk(80, r, 0.0)
    c["vf"] = 0.3
    GRID["X_Vf0p3_R%s_s0" % tag(r)] = c
c = mk(80, 1.5, 1.0)
c["vf"] = 0.3
GRID["X_Vf0p3_R1p5_s1"] = c
# repeat of faulted cases, bus +0.01 V: different solver step path, shows what a first-turn-on fault changed
for v_, r_, s_ in ((80, 1.5, 0.5), (80, 1.5, 1.0), (80, 5.0, 0.5), (60, 1.5, 1.0), (60, 2.0, 0.0)):
    c = mk(v_, r_, s_)
    c["v"] = v_ + 0.01
    GRID["Y_" + name(v_, r_, s_)] = c
m.CASES = GRID

_build = m.build


def build(n):
    c = m.CASES[n]
    base.RG_BOARD = c["rgon"]
    base.R_G_FET = c.get("rg", 0.5)
    out = _build(n)
    base.R_G_FET = 0.5
    if "vf" in c:
        p_ = os.path.join(HERE, out)
        txt = open(p_).read()
        a = ".model DID D(Ron=1m Roff=1G Vfwd=0)"
        assert a in txt
        # own model for the D_OFF parts only; the driver output diodes stay ideal
        txt = txt.replace(a, a + "\n.model DOF D(Ron=50m Roff=1G Vfwd=%g)" % c["vf"])
        txt, k = re.subn(r"^(Doff[HL][AB] \S+ \S+) DID$", r"\1 DOF", txt, flags=re.M)
        assert k == 4, k
        open(p_, "w").write(txt)
    return out


m.build = build


def do_trim():
    cases = {}
    for v in STAGES:
        for r in RONS:
            c = mk(v, r, 0.0)
            c.update(ton=STAGES[v][1], toff=0.15e-6, ton2=0.05e-6)    # only the first turn-off is needed
            cases["P1_%d_%s" % (v, tag(r))] = c
    m.CASES = cases
    m.run_all(list(cases))
    out = {}
    for n, c in cases.items():
        t, d = m.read_raw(os.path.join(HERE, n + ".raw"))
        w = m.W(t, d)
        T1 = 0.5e-6 + c["ton"]
        il = -w("I(Lload)")
        pk = w.mx(il, T1 - 50e-9, T1 + 100e-9)
        sl = (w.at(il, T1) - w.at(il, T1 - 0.5e-6)) / 0.5e-6
        tgt = STAGES[int(c["stage"])][0]
        out["%d_%g" % (c["stage"], c["ron"])] = c["ton"] + (tgt - pk) / sl
        print(n, "peak %.1f A, slope %.1f A/us, -> TON %.4f us" % (pk, sl * 1e-6, out["%d_%g" % (c["stage"], c["ron"])] * 1e6), flush=True)
    json.dump(out, open(TRIMF, "w"), indent=1)


def extras(n, r):
    c = m.CASES[n]
    t, d = m.read_raw(os.path.join(HERE, n + ".raw"))
    w = m.W(t, d)
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
    W = 250e-9
    e = dict(R_ON=c["ron"], stage_V=c["stage"], skew_ns=c["skew_ns"], Bm=c["bm"], t_end_us=TE * 1e6, R_G=c.get("rg", 0.5), D_OFF_Vf=c.get("vf", 0))
    # peaks: filtered (0.5 ns median, faults masked), windows wide enough for the slow edges of the higher R_ON
    e["HS_on1"] = max(w.cmx(vh[i], T0, T0 + W) for i in cells)
    e["HS_on2"] = max(w.cmx(vh[i], T2, T3) for i in cells)
    e["LS_off1"] = max(w.cmx(vl[i], T1, T1 + 200e-9) for i in cells)
    e["LS_off2"] = max(w.cmx(vl[i], T3, TE) for i in cells)
    e["VDS_max"] = max(e["HS_on1"], e["HS_on2"], e["LS_off1"], e["LS_off2"])
    e["raw_max"] = max(float(np.nanmax(x)) for x in list(vh.values()) + list(vl.values()))
    e["HS_VGS_min"], e["LS_VGS_min"] = r["HS_VGS_min"], r["LS_VGS_min"]
    e["HS_bump"] = max(r["HS_VGS_max"], -9)
    e["LS_VGS_max"] = r["LS_VGS_max"]
    e["t_HS_min_ns"] = None
    tu, xs = None, None
    for i in cells:
        a, b = m.clean(t, gh[i], 0, TE)
        if xs is None or b.min() < xs:
            xs, tu = float(np.nanmin(b)), float(a[np.nanargmin(b)])
    for lab, ev in (("T0", T0), ("T1", T1), ("T2", T2), ("T3", T3)):
        if tu >= ev:
            e["t_HS_min_ns"] = "%s+%.0f" % (lab, (tu - ev) * 1e9)

    def spread(a, b):
        y = []
        for i in cells:
            tt, x = m.clean(t, il[i], a, b)
            y.append(m.box(x, 10))                # 1 ns mean
        n_ = min(len(q) for q in y)
        y = np.array([q[:n_] for q in y])[:, 10:-10]
        return float(np.nanmax(y.max(axis=0) - y.min(axis=0))) if y.size else float("nan")

    def endmean(T):
        v = [float(il[i][w.win(T - 20e-9, T)].mean()) for i in cells]
        return v
    e["imb_edge_on2"] = spread(T2, T2 + 150e-9)
    e["imb_edge_off1"] = spread(T1 - 10e-9, T1 + 60e-9)
    e["imb_edge_on1"] = spread(T0, T0 + 150e-9)
    a1, a3 = endmean(T1), endmean(T3)
    e["I_end1_cells"], e["I_end2_cells"] = a1, a3
    e["imb_end1"], e["imb_end2"] = max(a1) - min(a1), max(a3) - min(a3)
    e["I_pk_on2_max"] = max(w.cmx(il[i], T2, T2 + 150e-9) for i in cells)
    # in-pair anti-phase ring in the second turn-on (peak to peak of I_a - I_b)
    pp = []
    for a, b in ((1, 2), (3, 4)):
        q = il[a] - il[b]
        k = w.win(T2, T3)
        pp.append(float(q[k].max() - q[k].min()) if k.sum() else float("nan"))
    e["pair_diff_pp"] = max(pp)
    # is the turn-on finished inside the second pulse?
    k = w.win(T2, T3)
    e["t_VDS10_ns"] = r["ton_delay_ns"]
    tg = []
    for i in cells:
        z = np.nonzero(gl[i][k] > 4.5)[0]
        tg.append((float(t[k][z[0]]) - T2) * 1e9 if len(z) else None)
    e["t_VGS45_ns"] = None if any(x is None for x in tg) else max(tg)
    e["VGS_LS_T3_min"] = min(w.at(gl[i], T3 - 1e-9) for i in cells)
    e["VDS_LS_T3_max"] = max(w.at(vl[i], T3 - 1e-9) for i in cells)
    e["ring_I_end2"] = max(float(np.nanmax(il[i][w.win(T3 - 40e-9, T3)]) - np.nanmin(il[i][w.win(T3 - 40e-9, T3)])) for i in cells) / 2
    for k_ in ("bus_T1", "bus_T2", "row_T2", "bus_T3", "I_T1_peak", "I_T2", "I_T3_peak", "Eon", "Eoff", "Eoff2", "Eon_250ns", "didt_on", "didt_off",
               "dvdt_on", "dvdt_off", "TON1_us", "solver_fault_windows_ns", "Eon_cells", "Eoff_cells"):
        e[k_] = r[k_]
    return e


def main():
    mode = sys.argv[1]
    rx = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    names = [n for n in m.CASES if not rx or rx.search(n)]
    if mode == "trim":
        do_trim()
    if mode == "run":
        def finished(n):
            p = os.path.join(HERE, n + ".log")
            if not os.path.exists(p):
                return False
            b = open(p, "rb").read()
            return "Total elapsed time".encode("utf-16-le") in b or b"Total elapsed time" in b
        todo = [n for n in names if not finished(n)]
        print(len(todo), "to run of", len(names), flush=True)
        m.run_all(todo)
    if mode == "post":
        p = os.path.join(HERE, "results.json")
        old = json.load(open(p)) if os.path.exists(p) else {}
        for n in names:
            if not os.path.exists(os.path.join(HERE, n + ".raw")):
                continue
            try:
                old[n] = extras(n, m.post(n))
            except Exception as ex:                # a run that stopped early is reported, not hidden
                old[n] = dict(failed=repr(ex)[:200], R_ON=m.CASES[n]["ron"], stage_V=m.CASES[n]["stage"], skew_ns=m.CASES[n]["skew_ns"], Bm=m.CASES[n]["bm"])
                print("FAILED", n, old[n]["failed"], flush=True)
        json.dump(old, open(p, "w"), indent=1)
        keys = ["R_ON", "stage_V", "skew_ns", "Bm", "TON1_us", "I_T1_peak", "bus_T1", "row_T2", "I_T3_peak", "HS_on1", "HS_on2", "LS_off1", "LS_off2", "HS_VGS_min", "HS_bump",
                "LS_VGS_min", "LS_VGS_max", "imb_edge_on2", "imb_edge_off1", "imb_end1", "imb_end2", "pair_diff_pp", "Eon", "Eon_250ns", "Eoff", "didt_on", "didt_off",
                "t_VDS10_ns", "t_VGS45_ns", "VGS_LS_T3_min", "ring_I_end2", "solver_fault_windows_ns", "failed"]
        with open(os.path.join(HERE, "results.csv"), "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["case"] + keys)
            for n in sorted(old):
                wr.writerow([n] + [old[n].get(k) for k in keys])
        print("posted", len(names), flush=True)


if __name__ == "__main__":
    main()

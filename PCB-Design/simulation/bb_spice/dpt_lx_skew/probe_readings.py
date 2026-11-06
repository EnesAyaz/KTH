"""
Probe-filtered readings from the existing dpt_lx_skew raws (no new Q3D or SPICE). Same method as read_limits() of the 1 uH / 80 V study:
0.05 ns grid, first-order low pass at 100 / 200 / 500 MHz, 200 ns lead-in, peak inside the event window.

Port (MMCX): the Q3D model has no terminal there. Return = RSI_c (LSRC via in the shunt land, review S3); drain side bounded by the two AC-net
nodes QL_D_c and QH_S_c. "die" = model pins V(dL, QL_S) / V(dH, QH_S); the deck has no package inductance. Cells 1-4 = J6, J9, J15, J18 (Q3, Q4, Q7, Q8).
Solver-fault windows are removed before gridding. Spikes below the 1000 V fault seed are removed too: a grid sample more than 5 V from its 0.45 ns
running median is replaced by the median (a real 211 MHz ring moves under 3 V in that span, and the median follows an edge); counts are in
"spikes" of the output. Writes probe_readings.json.
"""
import json
import os
import sys

import numpy as np
from scipy.signal import medfilt

_a, sys.argv = sys.argv, ["x", "none"]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_lx_skew as s                           # noqa: E402

m = s.m
DT = 0.05e-9
CELLS = (1, 2, 3, 4)
PORT = {1: "J6", 2: "J9", 3: "J15", 4: "J18"}
BW = ((None, "raw"), (500e6, "500MHz"), (200e6, "200MHz"), (100e6, "100MHz"))
T15 = {"500MHz": 98.0, "200MHz": 93.0, "100MHz": 87.0}


SPIKES = {}


class Case:
    def __init__(self, n):
        self.n = n
        self.c = m.CASES[n]
        p = os.path.join(HERE, n + ".raw")
        if not os.path.exists(p):
            raise FileNotFoundError(n)
        self.t, self.d = m.read_raw(p)
        self.w = m.W(self.t, self.d)
        w = self.w
        self.T0 = 0.5e-6
        self.T1 = self.T0 + self.c["ton"]
        self.T2 = self.T1 + self.c["toff"]
        self.T3 = self.T2 + self.c["ton2"]
        self.TE = float(self.t[-1])
        self.vl = {i: w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in CELLS}
        self.vh = {i: w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in CELLS}
        self.pd = {i: w.vd("V(QL_D_%d)" % i, "V(RSI_%d)" % i) for i in CELLS}
        self.ps = {i: w.vd("V(QH_S_%d)" % i, "V(RSI_%d)" % i) for i in CELLS}
        self.mask = m.find_mask(self.t, np.max([np.abs(self.vh[i]) for i in CELLS] + [np.abs(self.vl[i]) for i in CELLS], axis=0))

    def grid(self, x, a, b):
        m.MASK[:] = self.mask
        k = self.w.win(a - 200e-9, b) & m.good(self.t)
        tu, xu = m.uniform(self.t[k], x[k], DT)
        md = medfilt(xu, 9)
        bad = (np.abs(xu - md) > 5.0) & (np.arange(len(xu)) > 4) & (np.arange(len(xu)) < len(xu) - 4)
        if bad.any():
            key = "%s @ %.1f ns" % (self.n, a * 1e9)
            q = SPIKES.setdefault(key, dict(samples=0, largest_V=0.0, first_ns_after_event=None))
            q["samples"] = max(q["samples"], int(bad.sum()))
            q["largest_V"] = max(q["largest_V"], round(float(np.abs(xu - md)[bad].max()), 1))
            f = round(float((tu[bad][0] - a) * 1e9), 2)
            q["first_ns_after_event"] = f if q["first_ns_after_event"] is None else min(q["first_ns_after_event"], f)
            xu = np.where(bad, md, xu)
        return tu, xu

    def read(self, x, a, b):
        tu, xu = self.grid(x, a, b)
        sel = tu >= a
        return {lab: round(float((m.lp1(xu, DT, fc) if fc else xu)[sel].max()), 2) for fc, lab in BW}


def ls_table(cs):
    out = {}
    for ev, a, b in (("off1", cs.T1, cs.T1 + 150e-9), ("off2", cs.T3, min(cs.T3 + 150e-9, cs.TE))):
        out[ev] = {}
        for i in CELLS:
            out[ev]["cell%d_%s" % (i, PORT[i])] = dict(die=cs.read(cs.vl[i], a, b), port_QLD_RSI=cs.read(cs.pd[i], a, b), port_QHS_RSI=cs.read(cs.ps[i], a, b))
    return out


def hs_table(cs):
    # first turn-on window stops at +70 ns, before any solver fault, as in the earlier studies
    out = {}
    for ev, a, b in (("on1", cs.T0, cs.T0 + 70e-9), ("on2", cs.T2, cs.T2 + 150e-9)):
        out[ev] = {"cell%d" % i: cs.read(cs.vh[i], a, b) for i in CELLS}
    return out


def split(xu, r0, n=200):
    slow = xu.copy()
    slow[r0:] = m.box(np.pad(xu[r0:], n, mode="reflect"), 2 * n)[n:-n]
    return slow, xu - slow


def read_limit(cs, ev, a, b):
    """fast ring of all cells scaled by one factor until the worst cell reaches 100 V at the die, then each cell read through each filter"""
    g = {}
    for i in CELLS:
        tu, xu = cs.grid(cs.vl[i], a, b)
        k = tu >= a
        ip = int(np.argmax(np.where(k, xu, -1e9)))
        r0 = int(np.nonzero(k & (xu > 0.8 * xu[ip]))[0][0])
        g[i] = (tu, xu, k, ip, r0)
    worst = max(CELLS, key=lambda i: g[i][1][g[i][3]])
    tu, xu, k, ip, r0 = g[worst]
    slow, fast = split(xu, r0)
    alpha = (100.0 - slow[ip]) / fast[ip]
    res = dict(event=ev, worst_cell=worst, worst_port=PORT[worst], die_as_simulated=round(float(xu[ip]), 2), base_at_peak=round(float(slow[ip]), 2), ring_scale=round(float(alpha), 3), cells={})
    for i in CELLS:
        o = {}
        for nm, sig in (("die", cs.vl[i]), ("port_QLD_RSI", cs.pd[i]), ("port_QHS_RSI", cs.ps[i])):
            t2, x2 = cs.grid(sig, a, b)
            k2 = t2 >= a
            sl, fa = split(x2, g[i][4])
            y = sl + alpha * fa
            o[nm] = {lab: round(float((m.lp1(y, DT, fc) if fc else y)[k2].max()), 2) for fc, lab in BW}
        res["cells"]["cell%d_%s" % (i, PORT[i])] = o
    return res


def gate_table(cs):
    """HS V_GS per cell: minimum and time below -3.7 V, at the pin and (gate probes present) at the die"""
    out = {}
    m.MASK[:] = cs.mask
    for i in CELLS:
        pin = cs.w.vd("V(gH%d)" % i, "V(QH_S_%d)" % i)
        die = pin - 0.4 * cs.w("I(VGH%d)" % i)
        o = {}
        for lab, x in (("pin", pin), ("die", die)):
            tu, xu = m.clean(cs.t, x, 0, cs.TE)
            o[lab + "_min_V"] = round(float(np.nanmin(xu)), 2)
            o[lab + "_ns_below_m3p7"] = round(float((xu < -3.7).sum() * 0.1), 1)
            o[lab + "_ns_below_m4p0"] = round(float((xu < -4.0).sum() * 0.1), 1)
        out["cell%d" % i] = o
    return out


def main():
    missing, noport = [], []
    want = ["V80_R1p5_s0", "V80_R1p5_s0p5", "DIE2_LOW_V10_R1p5_s0", "DIE2_LOW_V20_R1p5_s0", "V40_R3_s3", "V60_R1p5_s1"]
    C = {}
    for n in want:
        try:
            C[n] = Case(n)
            if "v(rsi_1)" not in C[n].d:
                noport.append(n)
        except FileNotFoundError:
            missing.append(n)
    print("missing raws:", missing, "no RSI node:", noport)
    res = dict(method=__doc__.strip(), missing_raw=missing, missing_RSI=noport,
               faults={n: [[round(x * 1e9) for x in q] for q in c.mask] for n, c in C.items()},
               runs={n: dict(bus_T1=round(float(c.w.at(c.w.vd("V(BP)", "V(BN)"), c.T1)), 2), bus_T3=round(float(c.w.at(c.w.vd("V(BP)", "V(BN)"), c.T3)), 2),
                             I_end1=[round(float(c.w("I(VIL%d)" % i)[c.w.win(c.T1 - 20e-9, c.T1)].mean()), 1) for i in CELLS],
                             I_end2=[round(float(c.w("I(VIL%d)" % i)[c.w.win(c.T3 - 20e-9, c.T3)].mean()), 1) for i in CELLS]) for n, c in C.items()})
    res["item1_LS"] = {n: ls_table(C[n]) for n in want[:2]}
    res["item1_HS"] = {n: hs_table(C[n]) for n in want[:2]}
    res["item2_LS_lower_stages"] = {n: ls_table(C[n]) for n in want[2:]}
    g = {n: gate_table(C[n]) for n in want[2:4]}
    a, b = g["DIE2_LOW_V10_R1p5_s0"], g["DIE2_LOW_V20_R1p5_s0"]
    interp = {}
    for lab in ("pin", "die"):
        y10 = min(a["cell%d" % i][lab + "_min_V"] for i in (2, 3))
        y20 = min(b["cell%d" % i][lab + "_min_V"] for i in (2, 3))
        interp[lab] = dict(V_at_10V=y10, V_at_20V=y20, bus_at_m3p7_V=round(10 + 10 * (-3.7 - y10) / (y20 - y10), 1), bus_at_m4p0_V=round(10 + 10 * (-4.0 - y10) / (y20 - y10), 1))
    res["item3_HS_VGS"] = g
    res["item3_interpolation_ESTIMATE_ONLY"] = dict(note="straight line through the 10 V and 20 V runs, inner HS cells, 2.56 us pulse, R_ON 1.5, zero skew; not simulated at that bus", **interp)
    # item 4
    lim = {}
    for n in want[:2]:
        c = C[n]
        lim[n] = [read_limit(c, "off1", c.T1, c.T1 + 150e-9), read_limit(c, "off2", c.T3, min(c.T3 + 150e-9, c.TE))]
    t = {}
    for n in want[:2]:
        rows = {}
        for ev in ("off1", "off2"):
            for nm in ("die", "port_QLD_RSI"):
                for lab in T15:
                    best = max(res["item1_LS"][n][ev].items(), key=lambda kv: kv[1][nm][lab])
                    rows["%s_%s_%s" % (ev, nm, lab)] = dict(worst=best[0], read=best[1][nm][lab], T15=T15[lab], margin=round(T15[lab] - best[1][nm][lab], 2))
        t[n] = rows
    res["item4_T15_margin"] = t
    res["item4_read_when_worst_die_100V"] = lim
    res["spikes"] = SPIKES
    print("spikes replaced:", json.dumps(SPIKES))
    json.dump(res, open(os.path.join(HERE, "probe_readings.json"), "w"), indent=1)
    # plain print
    for key in ("item1_LS", "item2_LS_lower_stages"):
        for n, x in res[key].items():
            print("\n", key, n, "bus", res["runs"][n]["bus_T1"], "I_end1", res["runs"][n]["I_end1"], "I_end2", res["runs"][n]["I_end2"], "faults", res["faults"][n])
            for ev in x:
                for cl, q in x[ev].items():
                    f = lambda d: "%6.1f %6.1f %6.1f %6.1f" % tuple(d[k] for k in ("raw", "500MHz", "200MHz", "100MHz"))
                    print("  %s %-10s die %s | QLD %s | QHS %s" % (ev, cl, f(q["die"]), f(q["port_QLD_RSI"]), f(q["port_QHS_RSI"])))
    for n, x in res["item1_HS"].items():
        print("\n HS", n)
        for ev in x:
            for cl, d in x[ev].items():
                print("  %s %s %6.1f %6.1f %6.1f %6.1f" % (ev, cl, d["raw"], d["500MHz"], d["200MHz"], d["100MHz"]))
    print("\n gate")
    for n, x in g.items():
        for cl, d in x.items():
            print(" ", n, cl, d)
    print(json.dumps(res["item3_interpolation_ESTIMATE_ONLY"]))
    for n, r in t.items():
        print("\n T15", n)
        for k, v in r.items():
            print("  ", k, v)
    for n, r in lim.items():
        for e in r:
            print("\n limit", n, {k: v for k, v in e.items() if k != "cells"})
            for cl, q in e["cells"].items():
                print("  ", cl, "die", q["die"], "QLD", q["port_QLD_RSI"])


if __name__ == "__main__":
    main()

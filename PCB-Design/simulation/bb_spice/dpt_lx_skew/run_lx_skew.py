"""
Skew limits with the extracted switch-node network. Wraps ../dpt_ron_skew/run_ron_skew.py (not changed); output only in this folder.

    python run_lx_skew.py trim | run [regex] | post [regex]

Deck: as the R_ON sweep, but the star "Lac 18 nH per cell" is replaced by SWNET: a coupled network between the four switch nodes and
the load bolt J_AC, from the AC block of BB_PL_LX_dpt_swv1 (L at 100 MHz, every mutual as K; R matrix through behavioural sources as
in revb_q3d_spice.subckt; RSEL dc or ac). The commutation loops stay in BB_PL_LOOP_dpt_swv1, so the 0.646 nH per cell is unchanged:
in the LX matrix the cell loop is the small difference of two 40 nH entries, too ill-conditioned for K statements. Lac1..4 stay as
1 pH / 1 uOhm current probes, so the post-processing is the same.
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "dpt_ron_skew"))
_argv, sys.argv = sys.argv, ["x", "none"]
import run_ron_skew as rs                         # noqa: E402
sys.argv = _argv

m, base = rs.m, rs.base
rs.HERE = HERE
m.OUT = HERE
base.SP = HERE
m.PAR = 6
TRIMF = os.path.join(HERE, "trim.json")
trim = json.load(open(TRIMF)) if os.path.exists(TRIMF) else {}
RON_TRIM = rs.trim
LX = "BB_PL_LX_dpt_swv1"
NODES = ["QH_S_2", "QH_S_3", "QH_S_4", "J_AC"]


def swnet(rsel):
    q = base.load(LX)
    ix = {n.split(":")[1]: i for i, n in enumerate(q["names"])}
    h = [ix[n] for n in NODES]
    L = q["Lac"][np.ix_(h, h)]
    L = 0.5 * (L + L.T)
    assert np.linalg.eigvalsh(L).min() > 0
    R = q["Rdc" if rsel == "dc" else "Rac"][np.ix_(h, h)]
    R = 0.5 * (R + R.T)
    out = [".subckt SWNET n1 n2 n3 n4 nac", "* AC block of %s, reference node n1 (QH_S_1), R matrix: %s" % (LX, rsel)]
    pins = ["n2", "n3", "n4", "nac"]
    for i in range(4):
        out.append("L%d %s m%d %.9gn" % (i, pins[i], i, L[i, i] * 1e9))
        out.append("B%d m%d n1 V=%s" % (i, i, "+".join("%.6g*I(L%d)" % (R[i, j], j) for j in range(4))))
    for i in range(4):
        for j in range(i + 1, 4):
            out.append("K%d_%d L%d L%d %.9f" % (i, j, i, j, L[i, j] / math.sqrt(L[i, i] * L[j, j])))
    out.append(".ends SWNET")
    return "\n".join(out)


def tag(r):
    return ("%g" % r).replace(".", "p")


def name(v, r, s, m0=False, rg=False, ac=False):
    return "%s%s%sV%d_R%s_s%s" % ("M0_" if m0 else "", "RG_" if rg else "", "RAC_" if ac else "", v, tag(r), tag(s))


def mk(v, r, s, m0=False, rg=False, ac=False, ton=None):
    k = "%d_%g%s" % (v, r, "rg" if rg else "")
    # Bm off = sources scaled by 1e-6, not V=0: with the extracted network a literal V=0 stalls the .op search (Gmin and source stepping fail)
    c = m.case(v=float(v), ton=ton or trim.get(k, RON_TRIM["%d_%g" % (v, 1.5 if rg else r)]), skew=s * 1e-9, lac=1.0, msign=1)
    c["bmscale"] = 1e-6 if m0 else 1
    c["rgon"] = 3.5 if rg else 0.5 + 2 * r
    c["ron"], c["stage"], c["skew_ns"], c["bm"] = (1.0 if rg else r), v, s, not m0
    if rg:
        c["rg"] = 1.5
    c["rsel"] = "ac" if ac else "dc"
    return c


G = {}
for m0 in (False, True):
    for r in (1.5, 2.0):
        for s in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0):
            G[name(80, r, s, m0)] = mk(80, r, s, m0)
    for s in (0.0, 1.0, 1.5, 2.0):
        G[name(80, 1.0, s, m0, True)] = mk(80, 1.0, s, m0, True)
for r in (1.5, 3.0):
    for s in (1.0, 1.5, 2.0, 3.0):
        G[name(60, r, s)] = mk(60, r, s)
G[name(40, 3.0, 3.0)] = mk(40, 3.0, 3.0)
# die-node diagnostic: same decks with a 0 V probe in every gate lead; die V_GS = pin V_GS - 0.4 Ohm x gate current (rg of the EPC model)
for v_, r_, s_, rg_ in ((80, 1.5, 0.0, False), (80, 1.5, 1.0, False), (80, 2.0, 0.5, False), (80, 1.0, 0.0, True), (80, 1.0, 1.5, True)):
    c = mk(v_, r_, s_, rg=rg_)
    c["die"] = True
    G["DIE2_" + name(v_, r_, s_, rg=rg_)] = c
# off level as a bench setting (V_ISO): -1.9 V is V_ISO 7 V; V_ISO 6 V -> -0.9 V, 5.1 V -> 0 V. Die gate probes on.
for voff, lab in ((-0.9, "m0p9"), (0.0, "0")):
    for v_, r_, s_ in ((80, 1.5, 0.0), (80, 1.5, 1.0)):
        c = mk(v_, r_, s_)
        c["die"], c["voff"] = True, voff
        G["DIE2_Voff%s_" % lab + name(v_, r_, s_)] = c
# low-bus check of the split-driven dip, same 2.56 us pulse: about 50 A at 20 V, 25 A at 10 V (bus label only; pulse not trimmed)
for v_ in (20, 10):
    c = mk(40, 1.5, 0.0, ton=2.56e-6)
    c["v"], c["stage"], c["die"] = float(v_), v_, True
    G["DIE2_LOW_V%d_R1p5_s0" % v_] = c
m.CASES = G
_b = m.build


def build(n):
    out = _b(n)                                   # run_ron_skew.build: R_ON, R_G, skew, Bm; Lac stays 1 nH here and is replaced below
    p = os.path.join(HERE, out)
    txt = open(p).read()
    txt, k = re.subn(r"^Lac(\d) QH_S_\d ACO 1n Rser=0\.1m$", lambda q: "Lac%s QH_S_%s sw%s 1p Rser=1u" % (q.group(1), q.group(1), q.group(1)), txt, flags=re.M)
    assert k == 4, k
    if m.CASES[n]["bmscale"] != 1:
        txt, k = re.subn(r"^(Bm\S+ \S+ \S+ V=)(.*)$", lambda q: "%s%g*(%s)" % (q.group(1), m.CASES[n]["bmscale"], q.group(2)), txt, flags=re.M)
        assert k == 8, k
    if "voff" in m.CASES[n]:
        txt, k = re.subn(r"VOFF=-1\.9", "VOFF=%g" % m.CASES[n]["voff"], txt)
        assert k == 1, k
    a = "XCU "
    assert txt.count("\n" + a) == 1
    txt = txt.replace("\n" + a, "\n" + swnet(m.CASES[n]["rsel"]) + "\nXSW sw1 sw2 sw3 sw4 ACO SWNET\n" + a, 1)
    if m.CASES[n].get("die"):
        def probe(q):
            return "VG%s%s %s %si %s\nXQ%s%s %si %s" % (q.group(1), q.group(2), q.group(3), q.group(3), "0", q.group(1), q.group(2), q.group(3), q.group(4))
        txt, k = re.subn(r"^XQ([HL])(\d) (g[HL]\d) (.*EPC2361)$", probe, txt, flags=re.M)
        assert k == 8, k
        sv = " ".join("I(VG%s%d)" % (h, i) for h in "HL" for i in (1, 2, 3, 4))
        txt, k = re.subn(r"^\.save (.*)$", lambda q: ".save " + q.group(1) + " " + sv, txt, flags=re.M)
        assert k == 1
    open(p, "w").write(txt)
    return out


m.build = build


def do_trim():
    pts = ((80, 1.5, False), (80, 2.0, False), (80, 1.0, True), (60, 1.5, False), (60, 3.0, False), (40, 3.0, False))
    cases = {}
    for v, r, rg in pts:
        c = mk(v, r, 0.0, rg=rg, ton=RON_TRIM["%d_%g" % (v, 1.5 if rg else r)])
        c.update(toff=0.15e-6, ton2=0.05e-6)
        cases["P1_%d_%s%s" % (v, tag(r), "rg" if rg else "")] = c
    m.CASES = cases
    m.run_all(list(cases))
    out = {}
    for (v, r, rg), (n, c) in zip(pts, cases.items()):
        t, d = m.read_raw(os.path.join(HERE, n + ".raw"))
        w = m.W(t, d)
        T1 = 0.5e-6 + c["ton"]
        il = -w("I(Lload)")
        pk = w.mx(il, T1 - 50e-9, T1 + 100e-9)
        sl = (w.at(il, T1) - w.at(il, T1 - 0.5e-6)) / 0.5e-6
        tgt = rs.STAGES[v][0]
        out["%d_%g%s" % (v, r, "rg" if rg else "")] = c["ton"] + (tgt - pk) / sl
        print(n, "peak %.1f A -> TON %.4f us" % (pk, out["%d_%g%s" % (v, r, "rg" if rg else "")] * 1e6), flush=True)
    json.dump(out, open(TRIMF, "w"), indent=1)


def main():
    mode = sys.argv[1]
    rx = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    names = [n for n in m.CASES if not rx or rx.search(n)]
    if mode == "trim":
        do_trim()
    if mode == "build":
        for n in names[:1]:
            print(m.build(n))
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
                old[n] = rs.extras(n, m.post(n))
            except Exception as ex:
                c = m.CASES[n]
                old[n] = dict(failed=repr(ex)[:200], R_ON=c["ron"], stage_V=c["stage"], skew_ns=c["skew_ns"], Bm=c["bm"], R_G=c.get("rg", 0.5))
                print("FAILED", n, old[n]["failed"], flush=True)
        json.dump(old, open(p, "w"), indent=1)
        keys = ["R_ON", "R_G", "stage_V", "skew_ns", "Bm", "TON1_us", "I_T1_peak", "bus_T1", "row_T2", "I_T3_peak", "HS_on1", "HS_on2", "LS_off1", "LS_off2", "HS_VGS_min", "HS_bump",
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

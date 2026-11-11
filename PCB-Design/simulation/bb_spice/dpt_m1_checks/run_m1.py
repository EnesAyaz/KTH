"""
M1 model checks on the committed DPT board deck (no board change). Wraps ../dpt_gate_dip/run_gate_dip.py (not changed); output only here.

    python run_m1.py list | build | run [regex] | post [regex]

Deck edits on top of the gate-dip deck (Q3D BB_PL_LOOP_dpt_swv1 + SWNET from BB_PL_LX_dpt_swv1, 1 uH, board bank, die gate probes):
  eq    (a) the extracted node-to-bolt network SWNET is replaced by four equal uncoupled legs of <eq> nH (0.75 mOhm each): cells 1, 2 to
        bolt A, cells 3, 4 to bolt B. ASSUMPTION for the two-bolt board (hand estimate 20 nH), not an extraction.
  bar   bar between the two bolts, fed from its centre: <bar>/2 nH from each bolt to the load node; without it the bar is ideal (1 pH)
  kmap  (b) gate-Kelvin coupling of the gate legs from the gate extraction (m1b_hs_gate_k.json, driver held off): 1 = HS legs,
        2 = HS and LS legs. L_kb and the branch loop L_gb + L_kb - 2M stay as in the committed deck.
  kh    HS legs with a given k = M / L_kb (what-if for the G1 Kelvin reroute), branch loop unchanged
  dcx   (c) DC-side terms in series with the switch-node leg of each cell, from m1c_dc_side.json (written by m1c_post.py)
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "dpt_gate_dip"))
_argv, sys.argv = sys.argv, ["x", "none"]
import run_gate_dip as gd                         # noqa: E402
sys.argv = _argv
m, base, lx = gd.m, gd.base, gd.lx
gd.HERE = HERE
lx.HERE = HERE
m.OUT = HERE
base.SP = HERE
m.PAR = 6
CELLS = (1, 2, 3, 4)
KJ = json.load(open(os.path.join(HERE, "m1b_hs_gate_k.json")))["fets"]
REF = {("H", 1): "Q1", ("H", 2): "Q2", ("H", 3): "Q1", ("H", 4): "Q2", ("L", 1): "Q3", ("L", 2): "Q4", ("L", 3): "Q3", ("L", 4): "Q4"}
DCF = os.path.join(HERE, "m1c_dc_side.json")

G = {}


def add(**kw):
    G[gd.name(**kw)] = gd.mk(**kw)


# (a) equal take-off 20 nH, ideal bar, no tie: committed off level -1.9 V (Zener -2.2 / -1.6) and -1.5 V (-1.8 / -1.2)
for off in (-1.9, -1.5):
    lo, hi = round(off - 0.3, 1), round(off + 0.3, 1)
    add(voffH=off, voffL=off, eq=20)
    add(voffH=lo, voffL=lo, eq=20)
    add(voffH=hi, voffL=hi, eq=20)
    add(voffH=off, voffL=off, skew=0.5, eq=20)
    add(voffH=off, voffL=off, skew=0.5, bm=False, eq=20)
    add(voffH=lo, voffL=lo, skew=0.5, eq=20)
    add(voffH=lo, voffL=lo, skew=0.5, bm=False, eq=20)
    add(voffH=hi, voffL=hi, skew=0.5, eq=20)
    add(voffH=hi, voffL=hi, skew=0.5, bm=False, eq=20)
    for v in (20, 40):
        add(v=v, voffH=off, voffL=off, eq=20)
add(eq=20, bar=25)                                # sensitivity: 25 nH bar fed from its centre
# (b) the committed board (centre bolt, no tie) with the extracted gate-Kelvin coupling
for v in (20, 40, 80):
    add(v=v, kmap=1)
    add(v=v, kmap=2)
EXTRA = os.path.join(HERE, "extra_cases.json")
if os.path.exists(EXTRA):
    for kw in json.load(open(EXTRA)):
        add(**kw)
MSF = os.path.join(HERE, "maxstep.json")          # reruns of cases with LTspice solver faults: smaller maximum time step
if os.path.exists(MSF):
    for n_, v_ in json.load(open(MSF)).items():
        G[n_]["maxstep"] = v_
m.CASES = G
_b = gd.build


def legs(s_, c_, k=None):
    """(L_gb nH, K) for the gate leg of FET (side, cell); k = given M / L_kb, else from the extraction"""
    d = KJ[REF[(s_, c_)]]["off"]
    lk, br = d["L_kb_nH"], d["branch_nH"]
    mm = d["M_nH"] if k is None else k * lk
    lg = br - lk + 2 * mm
    return lg, mm / math.sqrt(lg * lk)


def build(n):
    c = m.CASES[n]
    out = _b(n)
    p = os.path.join(HERE, out)
    txt = open(p).read()
    w = c["what"]
    if "eq" in w:
        # ideal bar: the legs end on the load node directly (first version: 1 pH bar inductors; 11 of 23 runs had LTspice solver
        # faults in pulse 1 that left wrong cell currents, so the legs got Rpar and the 1 pH elements were removed)
        bolt = (lambda i: "boltA" if i < 3 else "boltB") if w.get("bar") else (lambda i: "ACO")
        new = "\n".join(["Leq%d sw%d %s %gn Rser=0.8m Rpar=2k" % (i, i, bolt(i), w["eq"]) for i in CELLS] +
                        (["LbarA boltA ACO %gn Rser=0.1m Rpar=2k" % (w["bar"] / 2.0),
                          "LbarB boltB ACO %gn Rser=0.1m Rpar=2k" % (w["bar"] / 2.0)] if w.get("bar") else []))
        assert txt.count("\nXSW sw1 sw2 sw3 sw4 ACO SWNET\n") == 1
        txt = txt.replace("\nXSW sw1 sw2 sw3 sw4 ACO SWNET\n", "\n" + new + "\n", 1)
    if "dcx" in w:
        # (c) bank-to-cell legs as coupled sets: Lbn (LS-on load path) = 4 I + D_LS, Lbp (HS-on path) = 4 I + D_HS (m1c_dc_side.json);
        # Lbp_c - Lbn_c coupled so that the bank-to-bypass loop of a cell stays 8 nH as in the committed deck
        dm = json.load(open(DCF))["deck_matrices_nH"]
        add_ = []
        for pn in "pn":
            M = np.array(dm["Lb" + pn])
            for i in CELLS:
                txt, k = re.subn(r"^(Lb%s%d \S+ \S+) 4n (Rser=\S+)$" % (pn, i),
                                 lambda q_: "%s %.4gn %s" % (q_.group(1), M[i - 1, i - 1], q_.group(2)), txt, flags=re.M)
                assert k == 1, k
                for j in CELLS:
                    if j > i:
                        add_.append("Kb%s%d%d Lb%s%d Lb%s%d %.5f" % (pn, i, j, pn, i, pn, j, M[i - 1, j - 1] / math.sqrt(M[i - 1, i - 1] * M[j - 1, j - 1])))
        for i in CELLS:
            lp, ln = dm["Lbp"][i - 1][i - 1], dm["Lbn"][i - 1][i - 1]
            add_.append("Kbpn%d Lbp%d Lbn%d %.5f" % (i, i, i, (lp + ln - 8.0) / 2 / math.sqrt(lp * ln)))
        assert txt.count("\nXCU ") == 1
        txt = txt.replace("\nXCU ", "\n" + "\n".join(add_) + "\nXCU ", 1)
    sides = {1: "H", 2: "HL"}.get(w.get("kmap"), "")
    for s_ in "HL":
        for i in CELLS:
            if s_ in sides or (s_ == "H" and "kh" in w):
                lg, kk = legs(s_, i, w.get("kh") if s_ == "H" else None)
                txt, k = re.subn(r"^(Lgb%s%d \S+ \S+) \S+$" % (s_, i), lambda q: "%s %.4gn" % (q.group(1), lg), txt, flags=re.M)
                assert k == 1, k
                txt, k = re.subn(r"^Kgk%s%d .*\n" % (s_, i), "", txt, flags=re.M)
                txt, k = re.subn(r"^(Lkb%s%d .*)$" % (s_, i), lambda q: "%s\nKgk%s%d Lgb%s%d Lkb%s%d %.4f" % (q.group(1), s_, i, s_, i, s_, i, -kk), txt, flags=re.M)
                assert k == 1, k
    open(p, "w").write(txt)
    return out


m.build = build


def metrics(n):
    e = gd.metrics(n)
    c = m.CASES[n]
    t, d = m.read_raw(os.path.join(HERE, n + ".raw"))
    w = m.W(t, d)
    T0 = 0.5e-6
    T1 = T0 + c["ton"]
    T2 = T1 + c["toff"]
    T3 = T2 + c["ton2"]
    TE = float(t[-1])
    # switch-node difference inside each pair, all four edges (on1 at T0, off1 at T1, on2 at T2, off2 at T3)
    for lab, (a, b) in (("12", (1, 2)), ("34", (3, 4))):
        x = w("V(QH_S_%d)" % a) - w("V(QH_S_%d)" % b)
        pk = []
        for t0 in (T0, T1, T2, T3):
            tu, xu = m.clean(t, x, t0 - 5e-9, min(t0 + 80e-9, TE))
            pk.append(float(np.nanmax(np.abs(xu))))
        e["SWdiff_%s_max_V" % lab] = round(max(pk), 2)
        e["SWdiff_%s_on1_off1_on2_off2_V" % lab] = [round(q, 2) for q in pk]
    e["SWdiff_pair_max_V"] = max(e["SWdiff_12_max_V"], e["SWdiff_34_max_V"])
    for s_ in "HL":
        die = {i: w.vd("V(g%s%d)" % (s_, i), "V(Q%s_S_%d)" % (s_, i)) - 0.4 * w("I(VG%s%d)" % (s_, i)) for i in CELLS}
        mn, mx = {}, {}
        for i in CELLS:
            tu, xu = m.clean(t, die[i], 0, TE)
            mn[i], mx[i] = float(np.nanmin(xu)), float(np.nanmax(xu))
        e[s_ + "S_die_min_cells"] = [round(mn[i], 2) for i in CELLS]
        e[s_ + "S_die_max_cells"] = [round(mx[i], 2) for i in CELLS]
        e[s_ + "S_inner_min"], e[s_ + "S_outer_min"] = round(min(mn[2], mn[3]), 2), round(min(mn[1], mn[4]), 2)
        e[s_ + "S_inner_max"], e[s_ + "S_outer_max"] = round(max(mx[2], mx[3]), 2), round(max(mx[1], mx[4]), 2)
    ic = e["I_end1_cells"]
    e["I_T1_total"] = round(sum(ic), 1)
    e["split_pct"] = [round(100 * (x * 4 / sum(ic) - 1), 1) for x in ic]
    vh = {i: w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in CELLS}
    vl = {i: w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in CELLS}
    e["HS_VDS_cells"] = [round(w.cmx(vh[i], 0, TE), 1) for i in CELLS]
    e["LS_VDS_cells"] = [round(w.cmx(vl[i], 0, TE), 1) for i in CELLS]
    e["m1a_pass"] = bool(e["SWdiff_pair_max_V"] < 1.0 and e["HS_VGS_min"] > -4.0)
    return e


KEYS = ["pass", "fails", "m1a_pass", "stage_V", "off_HS", "off_LS", "skew_ns", "Bm", "what", "SWdiff_pair_max_V", "SWdiff_12_max_V", "SWdiff_34_max_V",
        "SWdiff_12_on1_off1_on2_off2_V", "HS_VGS_min", "HS_inner_min", "HS_outer_min", "HS_inner_max", "HS_outer_max", "HS_bump_max", "HS_bump_margin_to_Vth0p8",
        "LS_VGS_min", "LS_inner_min", "LS_outer_min", "LS_inner_max", "LS_outer_max", "LS_bump_max", "HS_die_min_cells", "LS_die_min_cells",
        "I_T1_total", "I_end1_cells", "split_pct", "HS_VDS_max", "LS_VDS_max", "HS_VDS_cells", "LS_VDS_cells", "Eon", "Eon_250ns", "Eoff", "Eoff2", "didt_on", "didt_off",
        "cpl_Kelvin_leg_cell1_pk_A", "cpl_Kelvin_leg_cell2_pk_A", "HS_ns_below_m3p7_die", "LS_ns_below_m3p7_die", "faults", "t_end_us"]


def main():
    mode = sys.argv[1]
    rx = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    names = [n for n in m.CASES if not rx or rx.search(n)]
    if mode == "list":
        print(len(names), names)
    if mode == "build":
        for n in names:
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
                old[n] = metrics(n)
            except Exception as ex:
                old[n] = dict(failed=repr(ex)[:300])
                print("FAILED", n, old[n]["failed"], flush=True)
        json.dump(old, open(p, "w"), indent=1)
        with open(os.path.join(HERE, "results.csv"), "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["case"] + KEYS + ["failed"])
            for n in sorted(old):
                wr.writerow([n] + [old[n].get(k) for k in KEYS] + [old[n].get("failed")])
        print("posted", len(names), flush=True)


if __name__ == "__main__":
    main()

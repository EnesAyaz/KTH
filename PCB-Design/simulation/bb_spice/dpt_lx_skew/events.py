"""
HS and LS V_GS minimum per switching event (first turn-on T0, first turn-off T1, second turn-on T2, second turn-off T3), per cell, plus the
switch-node spread and the cell current at each turn-off. Separates the T1 event of the unequal split from the skew-driven events. Writes events.json.
"""
import json
import os
import sys

import numpy as np

_a, sys.argv = sys.argv, ["x", "none"]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_lx_skew as s                           # noqa: E402

m = s.m
sel = _a[1] if len(_a) > 1 else ""
out = {}
for n, c in m.CASES.items():
    if not n.startswith(sel) or not os.path.exists(os.path.join(HERE, n + ".raw")):
        continue
    t, d = m.read_raw(os.path.join(HERE, n + ".raw"))
    if t[-1] < 5e-6 and c["stage"] == 80:
        continue
    w = m.W(t, d)
    T0 = 0.5e-6
    T1 = T0 + c["ton"]
    T2 = T1 + c["toff"]
    T3 = T2 + c["ton2"]
    TE = float(t[-1])
    cells = (1, 2, 3, 4)
    vh = {i: w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in cells}
    vl = {i: w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in cells}
    m.MASK[:] = m.find_mask(t, np.max([np.abs(vh[i]) for i in cells] + [np.abs(vl[i]) for i in cells], axis=0))
    gh = {i: w.vd("V(gH%d)" % i, "V(QH_S_%d)" % i) for i in cells}
    gl = {i: w.vd("V(gL%d)" % i, "V(QL_S_%d)" % i) for i in cells}
    r = {}
    for lab, a, b in (("T0", T0, T0 + 250e-9), ("T1", T1, T1 + 150e-9), ("T2", T2, T3), ("T3", T3, TE)):
        r["HS_" + lab] = [round(w.cmn(gh[i], a, b), 2) for i in cells]
        r["LS_" + lab] = [round(w.cmn(gl[i], a, b), 2) for i in cells]
    for lab, T in (("T1", T1), ("T3", T3)):
        k = w.win(T, T + 60e-9)
        sw = {i: w("V(QH_S_%d)" % i)[k] for i in cells}
        r["SW_spread_%s" % lab] = round(float(max(np.max(np.abs(sw[1] - sw[2])), np.max(np.abs(sw[3] - sw[4])))), 2)
        r["I_%s" % lab] = [round(float(w("I(VIL%d)" % i)[w.win(T - 20e-9, T)].mean()), 1) for i in cells]
    out[n] = r
json.dump(out, open(os.path.join(HERE, "events.json"), "w"), indent=1)
for n in sorted(out):
    r = out[n]
    print("%-20s HS T1 %5.2f  T3 %5.2f T2 %6.2f T0 %5.2f | LS T1 %5.2f T3 %5.2f | SW spread T1 %4.1f T3 %4.1f | I T1 %s T3 %s" % (
        n, min(r["HS_T1"]), min(r["HS_T3"]), min(r["HS_T2"]), min(r["HS_T0"]), min(r["LS_T1"]), min(r["LS_T3"]), r["SW_spread_T1"], r["SW_spread_T3"], r["I_T1"], r["I_T3"]))

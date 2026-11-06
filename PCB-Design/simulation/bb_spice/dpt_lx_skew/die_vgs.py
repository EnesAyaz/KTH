"""
V_GS at the package pin against V_GS at the die (pin minus 0.4 Ohm rg of the EPC model x gate current) for the DIE2_* cases.
Writes die_vgs.json.
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
out = {}
for n, c in m.CASES.items():
    if not c.get("die"):
        continue
    t, d = m.read_raw(os.path.join(HERE, n + ".raw"))
    w = m.W(t, d)
    T0 = 0.5e-6
    T1 = T0 + c["ton"]
    T2 = T1 + c["toff"]
    T3 = T2 + c["ton2"]
    TE = float(t[-1])
    vmax = np.max([np.abs(d["v(dh%d)" % i] - d["v(qh_s_%d)" % i]) for i in (1, 2, 3, 4)], axis=0)
    m.MASK[:] = m.find_mask(t, vmax)
    r = dict(faults=[[round(x * 1e9) for x in q] for q in m.MASK])
    for h, H in (("h", "H"), ("l", "L")):
        pin = {i: w.vd("V(g%s%d)" % (H, i), "V(Q%s_S_%d)" % (H, i)) for i in (1, 2, 3, 4)}
        die = {i: pin[i] - 0.4 * w("I(VG%s%d)" % (H, i)) for i in (1, 2, 3, 4)}
        for lab, x in (("pin", pin), ("die", die)):
            r["%s_%s_min_cells" % (H + "S", lab)] = [round(w.cmn(x[i], 0, TE), 2) for i in (1, 2, 3, 4)]
            r["%s_%s_max_cells" % (H + "S", lab)] = [round(w.cmx(x[i], 0, TE), 2) for i in (1, 2, 3, 4)]
        # width of the excursion below -3.7 V at the die
        tu, xu = m.clean(t, die[2], T1, T1 + 60e-9)
        r[H + "S_die_cell2_ns_below_m3p7_after_T1"] = round(float((xu < -3.7).sum() * 0.1), 1)
    out[n] = r
    print(n, json.dumps(r))
json.dump(out, open(os.path.join(HERE, "die_vgs.json"), "w"), indent=1)

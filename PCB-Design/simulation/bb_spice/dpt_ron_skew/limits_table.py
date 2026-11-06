"""
Largest allowed U1-U2 skew per stage and R_ON from results.json. Criteria: V_GS not past -3.7 V (HS and LS), V_DS at the die below 100 V.
LS V_GS is judged twice: as simulated (ideal D_OFF, 0 V drop) and with the measured shift of the 0.3 V D_OFF cases (X_Vf0p3_*, +0.48 to
+0.58 V at 80 V; applied to the other skews and stages by hand). Writes limits.json, limits.csv.
"""
import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
LIM_G, LIM_V = -3.7, 100.0
VF_SHIFT = {1.5: R["X_Vf0p3_R1p5_s0"]["LS_VGS_min"] - R["V80_R1p5_s0"]["LS_VGS_min"],
            3.0: R["X_Vf0p3_R3_s0"]["LS_VGS_min"] - R["V80_R3_s0"]["LS_VGS_min"],
            5.0: R["X_Vf0p3_R5_s0"]["LS_VGS_min"] - R["V80_R5_s0"]["LS_VGS_min"]}
VF_SHIFT[2.0] = 0.5 * (VF_SHIFT[1.5] + VF_SHIFT[3.0])


def rows(v, r, bm):
    out = []
    for k, x in R.items():
        if k[0] in "XY" or "failed" in x:
            continue
        if x["stage_V"] == v and x["R_ON"] == r and x["Bm"] == bm:
            out.append(x)
    return sorted(out, key=lambda x: x["skew_ns"])


def cross(s, y, lim, sign):
    """first skew at which sign*(y - lim) < 0, linear between the points; None if never inside the grid; 0 if at zero skew"""
    for i in range(len(s)):
        if sign * (y[i] - lim) < 0:
            if i == 0:
                return 0.0
            return s[i - 1] + (s[i] - s[i - 1]) * (y[i - 1] - lim) / (y[i - 1] - y[i])
    return None


out = []
for bm in (True, False):
    for v in (80, 60, 40):
        for r in (1.5, 2.0, 3.0, 5.0):
            q = rows(v, r, bm)
            if not q:
                continue
            s = [x["skew_ns"] for x in q]
            hs = [x["HS_VGS_min"] for x in q]
            ls = [x["LS_VGS_min"] for x in q]
            lsv = [a + VF_SHIFT[r] for a in ls]
            vd = [x["VDS_max"] for x in q]
            c = dict(hs=cross(s, hs, LIM_G, 1), ls_ideal=cross(s, ls, LIM_G, 1), ls_vf=cross(s, lsv, LIM_G, 1), vds=cross(s, vd, LIM_V, -1))

            def allowed(keys):
                vals = [c[k] for k in keys if c[k] is not None]
                return min(vals) if vals else None
            a_vf, a_id = allowed(("hs", "ls_vf", "vds")), allowed(("hs", "ls_ideal", "vds"))
            bind = min((k for k in ("hs", "ls_vf", "vds") if c[k] is not None), key=lambda k: c[k], default="none in grid")

            def tested(lsl):
                ok = 0.0 if False else None
                for i, x in enumerate(q):
                    if hs[i] >= LIM_G and lsl[i] >= LIM_G and vd[i] < LIM_V:
                        ok = x["skew_ns"]
                    else:
                        break
                return ok
            t_vf = tested(lsv)
            i = s.index(t_vf) if t_vf is not None else None
            out.append(dict(stage_V=v, R_ON=r, Bm=bm, grid=s, max_tested_pass_Vf=t_vf, max_tested_pass_ideal=tested(ls), crossing_Vf_ns=a_vf, crossing_ideal_ns=a_id,
                            binding=bind, cross=c, margin_VGS_at_tested=None if i is None else round(min(hs[i], lsv[i]) - LIM_G, 2),
                            margin_VDS_at_tested=None if i is None else round(LIM_V - vd[i], 1)))
json.dump(dict(VF_SHIFT=VF_SHIFT, table=out), open(os.path.join(HERE, "limits.json"), "w"), indent=1)
with open(os.path.join(HERE, "limits.csv"), "w", newline="") as f:
    k = ["stage_V", "R_ON", "Bm", "max_tested_pass_Vf", "crossing_Vf_ns", "binding", "margin_VGS_at_tested", "margin_VDS_at_tested", "max_tested_pass_ideal", "crossing_ideal_ns"]
    w = csv.writer(f)
    w.writerow(k)
    for x in out:
        w.writerow([x[a] for a in k])
print("VF shift", {a: round(b, 2) for a, b in VF_SHIFT.items()})
for x in out:
    f2 = lambda v: "-" if v is None else "%.2f" % v
    print("Bm %-5s %d V R %.1f | tested Vf %s (cross %s, %s) mVGS %s mVDS %s | ideal tested %s cross %s" % (x["Bm"], x["stage_V"], x["R_ON"], f2(x["max_tested_pass_Vf"]), f2(x["crossing_Vf_ns"]), x["binding"],
          x["margin_VGS_at_tested"], x["margin_VDS_at_tested"], f2(x["max_tested_pass_ideal"]), f2(x["crossing_ideal_ns"])))

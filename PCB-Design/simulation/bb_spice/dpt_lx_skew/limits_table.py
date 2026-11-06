"""
Skew limits with the extracted network, from results.json and events.json. Criteria as in ../dpt_ron_skew/limits_table.py: V_GS not past -3.7 V
(HS and LS), die V_DS below 100 V. LS V_GS with the D_OFF 0.3 V shift of that sweep. Two views:
  full       all events
  skew only  HS V_GS at the second turn-on (T2) only: the T1 and T3 dips of the unequal split are present at zero skew and do not set a skew limit
Writes limits.json, limits.csv.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
E = json.load(open(os.path.join(HERE, "events.json")))
VF = json.load(open(os.path.join(HERE, "..", "dpt_ron_skew", "limits.json")))["VF_SHIFT"]
LG, LV = -3.7, 100.0


def cross(s, y, lim, sign):
    for i in range(len(s)):
        if sign * (y[i] - lim) < 0:
            if i == 0:
                return None if len(s) and s[0] > 0 and False else float(s[0]) if s[0] == 0 else "<%g" % s[0]
            return round(s[i - 1] + (s[i] - s[i - 1]) * (y[i - 1] - lim) / (y[i - 1] - y[i]), 2)
    return ">%g" % s[-1]


groups = {}
for n, x in R.items():
    if n.startswith("DIE") or "failed" in x:
        continue
    groups.setdefault((x["stage_V"], x["R_ON"], x.get("R_G", 0.5), x["Bm"]), []).append((x["skew_ns"], n, x))
rows = []
for k in sorted(groups, key=lambda q: (not q[3], -q[0], q[2], q[1])):
    v, r, rg, bm = k
    q = sorted(groups[k], key=lambda a: a[0])
    s = [a[0] for a in q]
    vd = [a[2]["VDS_max"] for a in q]
    hs_all = [a[2]["HS_VGS_min"] for a in q]
    ls = [a[2]["LS_VGS_min"] + VF.get("%g" % r, VF.get("1.5")) for a in q]
    t2 = [min(E[a[1]]["HS_T2"]) for a in q]
    t0 = [min(E[a[1]]["HS_T0"]) for a in q]
    hs_skew = [min(a, b) for a, b in zip(t2, t0)]
    c_v, c_t2, c_full, c_ls = cross(s, vd, LV, -1), cross(s, hs_skew, LG, 1), cross(s, hs_all, LG, 1), cross(s, ls, LG, 1)
    ok = [i for i in range(len(s)) if vd[i] < LV and hs_skew[i] >= LG and ls[i] >= LG]
    tested = None
    for i in range(len(s)):
        if i in ok:
            tested = s[i]
        else:
            break
    j = s.index(tested) if tested is not None else None
    rows.append(dict(stage_V=v, R_ON=r, R_G=rg, Bm=bm, grid=s, full_limit=c_full, skew_only_tested=tested, VDS_cross=c_v, HS_T2_cross=c_t2, LS_cross=c_ls,
                     HS_T1_min=min(min(E[a[1]]["HS_T1"]) for a in q), HS_T3_min=min(min(E[a[1]]["HS_T3"]) for a in q),
                     margin_VDS=None if j is None else round(LV - vd[j], 1), margin_VGS=None if j is None else round(min(hs_skew[j], ls[j]) - LG, 2)))
json.dump(rows, open(os.path.join(HERE, "limits.json"), "w"), indent=1)
keys = ["stage_V", "R_ON", "R_G", "Bm", "grid", "full_limit", "skew_only_tested", "VDS_cross", "HS_T2_cross", "LS_cross", "margin_VDS", "margin_VGS", "HS_T1_min", "HS_T3_min"]
with open(os.path.join(HERE, "limits.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(keys)
    for x in rows:
        w.writerow([x[k] for k in keys])
for x in rows:
    print({k: x[k] for k in keys if k != "grid"})

"""
Commutation loop per cell from the fast loop-only Q3D model (BB_PL_LOOP: cell band, bypass rows, shunts).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\loop_post.py
      -> results/loop_summary.json   (values in nH, AC matrix at 100 MHz)

Same loop definition as revb_post.py / bb_to_spice.py: HS FET of the cell shorted, bypass groups as their ESL
(top row ESL/6, bottom row ESL/n), UFCS shunt 120 pH, 1 A through the LS FET; loop = Im(V_LS)/w.
Cases: all four LS switching together (the real case) and each cell alone; with / without the bottom bypass row;
with the shunt and with the shunt replaced by a 0 pH link.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "revb_post.py"), encoding="utf-8").read().split("summary = {}")[0]
__file__ = os.path.join(HERE, "revb_post.py")
exec(_src)                                       # load(), Net, component data (ESL_0805, L_SHUNT, ...)

VT = os.environ.get("REVB_LOOP_TAG", "")
SFX = ("_" + VT) if VT else ""
leg = load("BB_PL_LOOP" + SFX)
names = [n.split(":")[1] for n in leg["names"]] + list({b for _, b in leg["branches"]})
w = 2 * math.pi * F_LOOP
n_bot = {c: NCAP.get("CapPb_%d" % c, 0) for c in range(1, 5)}
geo = json.load(open(os.path.join(RES, "revb_loop_geometry%s.json" % SFX)))
NB = {t[1]: len(t[3]) for t in geo["terminals"]}


def loop(cells, bottom=True, shunt=L_SHUNT):
    net = Net()
    net.group(leg["branches"], np.zeros_like(leg["Rac"]), leg["Lac"])
    for c in range(1, 5):
        net.add("QH_D_%d" % c, "QH_S_%d" % c, 0.0)
        net.add("CapP_%d" % c, "CapN_%d" % c, 1j * w * ESL_0805 / NB.get("CapP_%d" % c, 6))
        if bottom and NB.get("CapPb_%d" % c):
            net.add("CapPb_%d" % c, "CapNb_%d" % c, 1j * w * ESL_0805 / NB["CapPb_%d" % c])
        if "RSI_%d" % c in NB:                    # no shunt in the "noshunt" variant
            net.add("RSI_%d" % c, "RSN_%d" % c, 1j * w * shunt)
    inj = {}
    for c in cells:
        inj["QL_D_%d" % c] = 1.0
        inj["QL_S_%d" % c] = -1.0
    V, _, _ = net.solve(w, inj, "CapN_" + os.environ.get("REVB_LOOP_SINKCELL", "1"))
    return {"cell%d" % c: round(float(((V["QL_D_%d" % c] - V["QL_S_%d" % c]) / w).imag * 1e9), 4) for c in cells}


out = {"all_switching": loop([1, 2, 3, 4]),
       "all_switching_top_bypass_only": loop([1, 2, 3, 4], bottom=False),
       "all_switching_shunt_0pH": loop([1, 2, 3, 4], shunt=0.0),
       "each_alone": {k: v for c in range(1, 5) for k, v in loop([c]).items()},
       "matrix": open(os.path.join(RES, "BB_PL_LOOP%s_matrix.txt" % SFX)).readline().strip()}
vals = list(out["all_switching"].values())
out["mean_nH"] = round(sum(vals) / 4, 4)
out["overshoot_30Apns_V"] = round(75 + out["mean_nH"] * 30, 1)
json.dump(out, open(os.path.join(RES, "loop_summary%s.json" % SFX), "w"), indent=1)
print(json.dumps(out, indent=1))

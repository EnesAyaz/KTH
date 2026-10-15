"""
Breakdown of the commutation loop per cell of the final boards (fast loop model BB_PL_LOOP_<b>, AC 100 MHz):
copper only (bypass ESL 0, shunt 0 pH), + bypass ESL (6 top + 4 bottom 0805 per cell), + UFCS 120 pH (DPT board), and
the loop vs the number of top-row bypass MLCCs per cell (ESL / n, bottom row as built). All four LS FETs switching.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\loop_breakdown.py
      -> results/loop_breakdown.json
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "revb_post.py"), encoding="utf-8").read().split("_GEO = json.load")[0]
__file__ = os.path.join(HERE, "revb_post.py")
exec(_src)                                       # load(), Net, ESL_0805, L_SHUNT, F_LOOP
RES = os.path.join(HERE, "results")
w = 2 * math.pi * F_LOOP
out = {}
for b in ("dpt", "load"):
    if not os.path.exists(os.path.join(RES, "BB_PL_LOOP_%s_matrix.txt" % b)):
        continue
    leg = load("BB_PL_LOOP_" + b)
    geo = json.load(open(os.path.join(RES, "revb_loop_geometry_%s.json" % b)))
    NB = {t[1]: len(t[3]) for t in geo["terminals"]}
    shunt = any("RSI_%d" % c in NB for c in range(1, 5))

    def loop(n_top=None, esl=ESL_0805, l_sh=L_SHUNT):
        net = Net()
        net.group(leg["branches"], np.zeros_like(leg["Lac"]), leg["Lac"])
        for c in range(1, 5):
            net.add("QH_D_%d" % c, "QH_S_%d" % c, 0.0)
            nt = n_top or NB.get("CapP_%d" % c, 6)
            net.add("CapP_%d" % c, "CapN_%d" % c, 1j * w * esl / nt)
            if NB.get("CapPb_%d" % c):
                net.add("CapPb_%d" % c, "CapNb_%d" % c, 1j * w * esl / NB["CapPb_%d" % c])
            if shunt:
                net.add("RSI_%d" % c, "RSN_%d" % c, 1j * w * l_sh)
        inj = {}
        for c in range(1, 5):
            inj["QL_D_%d" % c] = 1.0
            inj["QL_S_%d" % c] = -1.0
        V, _, _ = net.solve(w, inj, "QH_D_1")
        return float(np.mean([((V["QL_D_%d" % c] - V["QL_S_%d" % c]) / w).imag * 1e9 for c in range(1, 5)]))

    cu = loop(esl=0.0, l_sh=0.0)
    esl_ = loop(l_sh=0.0)
    tot = loop()
    out[b] = dict(copper=cu, with_esl=esl_, total=tot, esl_part=esl_ - cu, shunt_part=tot - esl_, shunt=shunt,
                  vs_n_top={str(n): loop(n_top=n) for n in range(1, 13)})
    print(b, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out[b].items() if k != "vs_n_top"})
json.dump(out, open(os.path.join(RES, "loop_breakdown.json"), "w"), indent=1)

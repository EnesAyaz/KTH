"""
M1(b): gate-Kelvin coupling of the HS and LS gate legs from the existing gate extraction (BB_PL_GATE_dpt, AC matrix 100 MHz).
Reads only; uses the functions of ../../bb_q3d/gate_post.py (not changed, its json is not rewritten).

Bridge transfer L_t(q): 1 A from the Kelvin pad of one FET of a pair through the Kelvin copper to the Kelvin pad of the other FET
(die links open, gates open, driver holding off); L_t = Im(V_G - V_K)/w at FET q. This is the gate error per dI/dt of the
anti-phase Kelvin current. In the SPICE deck the same quantity is L_kb - M(gate leg, Kelvin leg).
Mapping for the deck (same three-number form as the LS legs): L_kb = Kelvin pad-to-pad / 2 (unchanged), M = L_kb - L_t,
L_gb = branch - L_kb + 2 M (branch loop unchanged), K = M / sqrt(L_gb L_kb).
"""
import json
import math
import os

HERE0 = os.path.dirname(os.path.abspath(__file__))
Q3D = os.path.normpath(os.path.join(HERE0, "..", "..", "bb_q3d"))
src = open(os.path.join(Q3D, "gate_post.py"), encoding="utf-8").read().split("ESLS = (")[0]
g = {"__file__": os.path.join(Q3D, "gate_post.py"), "__name__": "gp"}
exec(src, g)
build, FET, w, RES = g["build"], g["FET"], g["w"], g["RES"]
gs = json.load(open(os.path.join(RES, "gate_summary_dpt.json")))
sp, kp = gs["split_nH"]["esl0.4"], gs["kelvin_pair_nH"]


def bridge(ch, drv="off"):
    st = {"A": "off", "B": "off"}
    st[ch] = drv
    net = build(st, hs_on=False)
    net.simple = [x for x in net.simple if not x[0].startswith("K_Q")]
    q1, q2 = [k for k, v in FET.items() if v[1] == ch]
    V, _, _ = net.solve(w, {"K_" + q1: 1.0, "K_" + q2: -1.0}, "CapN_1")
    lt = {q: float(((V["G_" + q] - V["K_" + q]) / w).imag * 1e9) for q in (q1, q2)}
    lt[q1] = -lt[q1]                              # current leaves the pad of q1 into the copper: V_K rises there, error = -(V_G - V_K)
    pp = float(((V["K_" + q1] - V["K_" + q2]) / w).imag * 1e9)
    return lt, pp


out = {"model": "BB_PL_GATE_dpt Setup1:LastAdaptive, AC L at 100 MHz, driver block 1 (cells 1 + 2), bypass ESL 0.4 nH", "fets": {}}
for ch in "AB":
    for drv in ("off", "on"):
        lt, pp = bridge(ch, drv)
        for q in lt:
            lk = kp[ch] / 2
            br = sp[q]["branch"]
            mm = lk - lt[q]
            lg = br - lk + 2 * mm
            k = mm / math.sqrt(lg * lk) if lg > 0 else float("nan")
            d = out["fets"].setdefault(q, {})
            d[drv] = dict(L_t_nH=round(lt[q], 4), kelvin_pad_to_pad_nH=round(pp, 4), L_kb_nH=round(lk, 4), branch_nH=br, M_nH=round(mm, 4),
                          L_gb_nH=round(lg, 4), K=round(k, 4), k_review=round(1 - lt[q] / lk, 4))
# what the committed deck carries
deck = {"Q1": 3.723, "Q2": 3.723, "Q3": 3.505 * (1 - 0.5800), "Q4": 3.505 * (1 - 0.5786)}
for q in out["fets"]:
    out["fets"][q]["deck_L_t_nH"] = round(deck[q], 4)
json.dump(out, open(os.path.join(HERE0, "m1b_hs_gate_k.json"), "w"), indent=1)
print(json.dumps(out, indent=1))

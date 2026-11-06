"""
Values from the L_x extraction, old (BB_PL_LX_dpt, 2026-10-15, before the SW vias) against new (BB_PL_LX_dpt_swv1, current board):
  L_x HS / LS       same definition as final_post.py: pair A to pair B with the HS (LS) FETs closed, so the DC rails are in parallel
  AC-net paths      FETs open: switch node to switch node, pair to pair (tied), and each node to the load bolt J_AC (new only)
Writes lx_summary.json. final_numbers.json is not touched.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "bb_q3d"))
import revb_q3d_spice as b                        # noqa: E402

Net, L_SHUNT = b.Net, b.L_SHUNT
w = 2 * math.pi * b.F_LOOP
NODES = ["QH_S_2", "QH_S_3", "QH_S_4"]


def block(m, key, names):
    ix = {n.split(":")[1]: i for i, n in enumerate(m["names"])}
    q = [ix[n] for n in names]
    return m[key][np.ix_(q, q)]


def lx(leg):
    shunt = any(t.startswith("RSI_") for _, t in leg["branches"])
    out = {}
    for path in ("HS", "LS"):
        net = Net()
        net.group(leg["branches"], np.zeros_like(leg["Rac"]), leg["Lac"])
        for c in range(1, 5):
            if path == "HS":
                net.add("QH_D_%d" % c, "QH_S_%d" % c, 0.0)
            else:
                net.add("QL_D_%d" % c, "QL_S_%d" % c, 0.0)
                if shunt:
                    net.add("RSI_%d" % c, "RSN_%d" % c, 1j * w * L_SHUNT)
        sw = "QH_S_%d" if path == "HS" else "QL_D_%d"
        V, _, _ = net.solve(w, {sw % 1: -0.5, sw % 2: -0.5, sw % 3: 0.5, sw % 4: 0.5}, sw % 1)
        out[path] = float((((V[sw % 3] + V[sw % 4]) - (V[sw % 1] + V[sw % 2])) / 2 / w).imag * 1e9)
    return out


def acnet(m, names):
    """L in nH, R in mOhm between nodes, reference QH_S_1; matrix of branches 'names' to the sink"""
    L = block(m, "Lac", names) * 1e9
    out = dict(names=names, L_nH=np.round(L, 3).tolist())
    for k, lab in (("Rdc", "Rdc"), ("Rac", "Rac")):
        if k in m:
            out[lab + "_mOhm"] = np.round(block(m, k, names) * 1e3, 3).tolist()
    ix = {n: i for i, n in enumerate(names)}

    def diff(M, a, c):
        if a == "QH_S_1":
            return float(M[ix[c], ix[c]])
        return float(M[ix[a], ix[a]] + M[ix[c], ix[c]] - 2 * M[ix[a], ix[c]])
    pairs = [("QH_S_1", "QH_S_2"), ("QH_S_3", "QH_S_4"), ("QH_S_2", "QH_S_3"), ("QH_S_1", "QH_S_3"), ("QH_S_2", "QH_S_4"), ("QH_S_1", "QH_S_4")]
    out["node_to_node_nH"] = {a[-1] + "-" + c[-1]: round(diff(L, a, c), 3) for a, c in pairs}
    for k, lab in (("Rdc", "dc"), ("Rac", "ac")):
        if k in m:
            R = block(m, k, names) * 1e3
            out["node_to_node_R%s_mOhm" % lab] = {a[-1] + "-" + c[-1]: round(diff(R, a, c), 3) for a, c in pairs}
    # pair to pair, nodes of a pair tied (sink node 1 tied to 2, 3 tied to 4), at the three-node level
    h = [ix[n] for n in NODES]
    Ls = L[np.ix_(h, h)]
    i = np.linalg.solve(Ls, np.array([0.0, 1.0, 1.0]))
    out["pair_to_pair_tied_nH"] = round(float(1 / (i[1] + i[2])), 3)
    Zc = (block(m, "Rac", names)[np.ix_(h, h)] + 1j * w * L[np.ix_(h, h)] * 1e-9)
    i = np.linalg.solve(Zc, np.array([0.0, 1.0, 1.0]))
    z = 1 / (i[1] + i[2])
    out["pair_to_pair_tied_100MHz"] = dict(L_nH=round(float(z.imag / w * 1e9), 3), R_mOhm=round(float(z.real * 1e3), 3))
    if "J_AC" in ix:
        out["node_to_bolt_nH"] = {"1": round(float(L[ix["J_AC"], ix["J_AC"]]), 3)}
        for n in NODES:
            out["node_to_bolt_nH"][n[-1]] = round(diff(L, n, "J_AC"), 3)
    return out


def cross(m, names):
    """largest mutual between the AC-net branches used and the branches of the other nets, nH"""
    ix = {n.split(":")[1]: i for i, n in enumerate(m["names"])}
    a = [ix[n] for n in names]
    o = [i for i, n in enumerate(m["names"]) if not n.startswith("AC:")]
    return float(np.abs(m["Lac"][np.ix_(a, o)]).max() * 1e9)


res = {}
for lab, tag, names in (("old_2026-10-15", "BB_PL_LX_dpt", NODES), ("new_swv1", "BB_PL_LX_dpt_swv1", NODES + ["J_AC"])):
    p = os.path.join(b.RES, tag + "_matrix.txt")
    if not os.path.exists(p):
        continue
    m = b.load(tag)
    res[lab] = dict(lx_nH=lx(m), ac=acnet(m, names), cross_to_other_nets_max_nH=cross(m, names), loop_like_QH_QL_nH=[
        round(float(block(m, "Lac", ["QH_S_%d" % c, "QL_D_%d" % c]) @ np.array([1, -1]) @ np.array([1, -1])) * 1e9, 4) for c in (2, 3, 4)])
json.dump(res, open(os.path.join(HERE, "lx_summary.json"), "w"), indent=1)
print(json.dumps(res, indent=1))

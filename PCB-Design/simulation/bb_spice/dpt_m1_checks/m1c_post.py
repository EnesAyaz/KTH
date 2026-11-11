"""
M1(c): DC-side path inductance per cell from the L_x extraction with bank and DC terminals (BB_PL_LX_dpt_swv1dc, AC L at 100 MHz).
Reads only; uses load() / Net of ../../bb_q3d/revb_post.py (not changed). Run with the KiCad python.

Load path of the double-pulse test: bank -> DC+ plane -> J1 (J_DCP) -> load -> AC bolt (J_AC) -> AC bus -> cell.
  LS on (ramp):      cell -> LS FET -> shunt -> DC- plane -> bank parts -> DC+ plane -> J1
  HS on (freewheel): cell -> HS FET -> DC+ plane -> J1
Path matrix Z (4 x 4, nH): port i = the open FET of cell i (LS or HS), load shorted (J_DCP = J_AC), bank parts as their ESL
(1 nH per 2220, in parallel per group), bypass rows open (1.8 uF per cell cannot carry the load ramp), shunt 120 pH.
Reference "deck topology" on the same copper: every cell leaves at its own bypass pads (CapN_c for LS on, CapP_c for HS on) straight
to the load node. This is what the SPICE deck has (plus 4 nH per cell). DC side = Z - Z_ref: what the bank position and J1 / J2 add.
"""
import json
import math
import os
import sys

import numpy as np

HERE0 = os.path.dirname(os.path.abspath(__file__))
Q3D = os.path.normpath(os.path.join(HERE0, "..", "..", "bb_q3d"))
src = open(os.path.join(Q3D, "revb_post.py"), encoding="utf-8").read().split("summary = {}")[0]
g = {"__file__": os.path.join(Q3D, "revb_post.py"), "__name__": "rp"}
exec(src, g)
load, Net, RES = g["load"], g["Net"], g["RES"]
TAG = sys.argv[1] if len(sys.argv) > 1 else "BB_PL_LX_dpt_swv1dc"
q = load(TAG)
geo = json.load(open(os.path.join(RES, "revb_lx_geometry_%s.json" % TAG.split("BB_PL_LX_")[1])))
NB = {t[1]: len(t[3]) for t in geo["terminals"]}
w = 2 * math.pi * 100e6
L_SH, ESL_BANK, ESL_BYP = 0.12e-9, 1.0e-9, 0.48e-9
CELLS = (1, 2, 3, 4)
BANKG = sorted(n[6:] for n in NB if n.startswith("BankP"))


def net0(bank=True, bypass=False):
    net = Net()
    net.group(q["branches"], np.zeros_like(q["Lac"]), q["Lac"])
    for c in CELLS:
        net.add("RSI_%d" % c, "RSN_%d" % c, 1j * w * L_SH)
        if bypass:
            net.add("CapP_%d" % c, "CapN_%d" % c, 1j * w * ESL_BYP / NB["CapP_%d" % c])
            net.add("CapPb_%d" % c, "CapNb_%d" % c, 1j * w * ESL_BYP / NB["CapPb_%d" % c])
    if bank:
        for b in BANKG:
            net.add("BankP_" + b, "BankN_" + b, 1j * w * ESL_BANK / NB["BankP_" + b])
    return net


def zmat(side, ref=False):
    """path matrix in nH; side L: LS port (QL_D - QL_S), H: HS port (QH_S - QH_D). ref: exit at the cell's own bypass pads"""
    Z = np.zeros((4, 4))
    hi, lo = ("QL_D_%d", "QL_S_%d") if side == "L" else ("QH_S_%d", "QH_D_%d")
    for j in CELLS:
        net = net0(bank=not ref)
        if ref:
            for c in CELLS:
                for nm in ("CapN_%d", "CapNb_%d") if side == "L" else ("CapP_%d", "CapPb_%d"):
                    net.add(nm % c, "J_AC", 1e-9)
        else:
            net.add("J_DCP", "J_AC", 1e-9)
        V, _, _ = net.solve(w, {lo % j: 1.0, hi % j: -1.0}, "J_AC")
        for i in CELLS:
            Z[i - 1, j - 1] = ((V[lo % i] - V[hi % i]) / w).imag * 1e9
    return 0.5 * (Z + Z.T)


def split(Z):
    i = np.linalg.solve(Z, np.ones(4))
    return [round(float(x), 1) for x in 100 * (i * 4 / i.sum() - 1)]


out = {"model": TAG + ", AC L 100 MHz; bank ESL 1 nH per part, bypass open, shunt 120 pH, load shorted J_DCP = J_AC",
       "bank_groups": {b: NB["BankP_" + b] for b in BANKG}}
for side, lab in (("L", "LS_on"), ("H", "HS_on")):
    Zt, Zr = zmat(side), zmat(side, True)
    D = Zt - Zr
    out[lab] = dict(Z_total_nH=np.round(Zt, 3).tolist(), Z_cell_exit_nH=np.round(Zr, 3).tolist(), DC_side_nH=np.round(D, 3).tolist(),
                    DC_side_self_nH=[round(float(D[i, i]), 2) for i in range(4)],
                    DC_side_all_cells_equal_nH=[round(float(D[i].sum()), 2) for i in range(4)],
                    DC_side_relative_to_mean_nH=[round(float(D[i].sum() - D.sum() / 4), 2) for i in range(4)],
                    total_self_nH=[round(float(Zt[i, i]), 2) for i in range(4)],
                    inductive_split_pct_total=split(Zt), inductive_split_pct_cell_exit=split(Zr))
# equal take-off what-if: the AC side of each cell replaced by 20 nH (uncoupled), DC side from this extraction
for lab in ("LS_on", "HS_on"):
    D = np.array(out[lab]["DC_side_nH"])
    out[lab]["inductive_split_pct_equal20_plus_DC_side_plus_4nH"] = split(D + 24.0 * np.eye(4))
# bank loop seen from each bypass row (port CapP_c - CapN_c, bank shorted through its ESL): the deck has 4 + 4 nH per cell
lb = []
for c in CELLS:
    net = net0()
    V, _, _ = net.solve(w, {"CapP_%d" % c: 1.0, "CapN_%d" % c: -1.0}, "J_AC")
    lb.append(round(float(((V["CapP_%d" % c] - V["CapN_%d" % c]) / w).imag * 1e9), 3))
out["bank_to_bypass_loop_nH"] = lb
# deck mapping: Lbn set (LS-on path) = 4 I + D_LS, Lbp set (HS-on path) = 4 I + D_HS, P-N coupling per cell keeps the 8 nH bank loop
Ln, Lp = 4 * np.eye(4) + np.array(out["LS_on"]["DC_side_nH"]), 4 * np.eye(4) + np.array(out["HS_on"]["DC_side_nH"])
out["deck_matrices_nH"] = dict(Lbn=np.round(Ln, 3).tolist(), Lbp=np.round(Lp, 3).tolist(),
                               eig_Lbn=np.round(np.linalg.eigvalsh(Ln), 3).tolist(), eig_Lbp=np.round(np.linalg.eigvalsh(Lp), 3).tolist())
json.dump(out, open(os.path.join(HERE0, "m1c_dc_side.json"), "w"), indent=1)
print(json.dumps(out, indent=1))

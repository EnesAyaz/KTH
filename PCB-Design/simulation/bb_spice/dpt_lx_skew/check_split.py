"""
Independent check of the current split at the end of the first pulse, no SPICE: linear RL network of the AC block of BB_PL_LX_dpt_swv1.
Branch k from the bolt to switch node k carries i_k; all nodes are held at the same voltage (cells on, equal cell path r_c: FET + shunt +
loop copper), the bolt current is the ramp of the deck. Node voltages from the matrix referred to node 1. Prints i_k for several r_c,
with the 100 MHz L and with L + 15 % (low-frequency inductance is somewhat higher, the ratio matters), and at 2 and 4.2 us.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "bb_q3d"))
import revb_q3d_spice as b                        # noqa: E402

q = b.load("BB_PL_LX_dpt_swv1")
ix = {n.split(":")[1]: i for i, n in enumerate(q["names"])}
names = ["QH_S_2", "QH_S_3", "QH_S_4", "J_AC"]
h = [ix[n] for n in names]
L0, R0 = q["Lac"][np.ix_(h, h)], q["Rdc"][np.ix_(h, h)]
# unknowns: i2, i3, i4 into the cells from nodes 2..4 (cell 1 takes the rest); branch currents of the matrix (source -> sink n1):
# node 2..4 branches carry -i2.. (current leaves the net at those nodes), bolt branch carries +I
def sim(L, R, rc, T=4.2e-6, slope=74e6, n=4000):
    dt = T / n
    i = np.zeros(3)
    out = []
    A = L[:3, :3]
    for k in range(n):
        I = slope * (k + 1) * dt
        Ib = np.r_[-i, I]                         # branch currents, source -> n1
        v = R @ Ib                                # resistive drop node -> n1 (first 3 rows)
        i1 = I - i.sum()
        # node_k - n1 = v_k + L_k. dIb/dt ; node potentials must satisfy node_k - n1 = rc*(i_k - i1) ... all cells to a common rail
        dI = slope
        # L[:3,:3] @ (-di) + L[:3,3]*dI + v[:3] = rc*(i - i1) (cell k rail equal)
        rhs = L[:3, 3] * dI + v[:3] - rc * (i - i1)
        di = np.linalg.solve(A + rc * 0, rhs)
        i = i + di * dt
        out.append(np.r_[I - i.sum(), i])
    return np.array(out)


print("cells 1..4, A per cell at the end of the pulse")
for rc in (2e-3, 3e-3, 4e-3):
    for sc, lab in ((1.0, "L 100 MHz"), (1.15, "L +15 %")):
        y = sim(L0 * sc, R0, rc)
        print("r_cell %.0f mOhm, %-10s  4.2 us: %s   2 us: %s" % (rc * 1e3, lab, np.round(y[-1], 1), np.round(y[len(y) * 2 // 4 - 1 + 0], 1)))
print("static (R only, steady state):")
y = sim(L0, R0, 3e-3, T=200e-6, n=40000)
print(np.round(y[-1] / y[-1].sum() * 100, 2), "% of the load current")

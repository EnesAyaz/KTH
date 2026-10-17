"""
Gate loops of driver block 1 (cells 1 + 2, driver U1) and their coupling to the commutation loops, from the gate model
(BB_PL_GATE_dpt: power nets as in the loop model plus both gate networks, AC matrix at 100 MHz).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\gate_post.py
      -> results/gate_summary_dpt.json   (inductances in nH)

Circuit on the extracted copper (Net / load() from revb_post.py):
  FET die: Kelvin pad and power source joined (K_Q1 = QH_S_1, K_Q2 = QH_S_2, K_Q3 = QL_S_1, K_Q4 = QL_S_2); the gate is
  open (C_iss) except where the test current is injected.
  Gate parts: R_G 0.5 Ohm (R1..R4), R_ON 0.75 Ohm (R7, R9), R_OFF 0 Ohm (R8, R10), D_OFF (D1, D2) 0.1 Ohm when it conducts;
  driver output to VDD 0.85 Ohm (on) or to VEE 0.35 Ohm (off) (2EDF7275K 4 / 8 A); 1 uF output-side bypass (C13..C16)
  as its ESL (ESL_0603, 0.4 nH assumed; also reported with 0 nH = copper only).
  Power: as loop_post.py (bypass groups as their ESL, UFCS shunt 120 pH).
Results:
  gate_loop: Im(V_G - V_K)/w for 1 A injected at the gate pad and returned at the Kelvin pad, the other FET of the pair
    open; "on" = driver output high (R_ON path), "off" = driver output low (D_OFF + R_OFF parallel to R_ON).
  coupling: gate-Kelvin voltage at the die per unit di/dt of the commutation loop (forward direction: DC+ -> HS drain
    -> source -> SW -> LS drain -> source -> shunt -> DC-), per cell and both cells; two driver states: LS switching
    with HS held off (the double-pulse test) and the reverse. v_GK = M_eff * di/dt (30 A/ns and 10 pH -> 0.3 V).
  split: per-FET branch (R_G side) and the part shared by the pair (driver -> star), from single vs pair-driven
    injection, for the circuit model in revb_q3d_spice.py.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "revb_post.py"), encoding="utf-8").read().split("summary = {}")[0]
__file__ = os.path.join(HERE, "revb_post.py")
exec(_src)                                       # load(), Net, ESL_0805, L_SHUNT, F_LOOP, RES

TAGB = os.environ.get("REVB_LOOP_TAG", "dpt")
leg = load("BB_PL_GATE_" + TAGB)
geo = json.load(open(os.path.join(RES, "revb_gate_geometry_%s.json" % TAGB)))
NB = {t[1]: len(t[3]) for t in geo["terminals"]}
w = 2 * math.pi * F_LOOP
R_G, R_ON, R_OFF, R_D = 0.5, 0.75, 1e-3, 0.1
R_UP, R_DN = 0.85, 0.35
ESL_0603 = 0.4e-9
FET = {"Q1": ("QH_S_1", "A"), "Q2": ("QH_S_2", "A"), "Q3": ("QL_S_1", "B"), "Q4": ("QL_S_2", "B")}
CH = {"A": dict(rg=(("R1_1", "R1_2"), ("R2_2", "R2_1")), ron=("R7_1", "R7_2"), roff=("R8_1", "R8_2"),
                d=("D1_1", "D1_2"), out="U1_12", vdd="U1_13", vee="U1_11", cdd=("C13_1", "C13_2"),
                cee=("C14_1", "C14_2")),
      "B": dict(rg=(("R3_1", "R3_2"), ("R4_2", "R4_1")), ron=("R9_1", "R9_2"), roff=("R10_1", "R10_2"),
                d=("D2_1", "D2_2"), out="U1_9", vdd="U1_10", vee="U1_8", cdd=("C16_1", "C16_2"),
                cee=("C15_1", "C15_2"))}


def build(state, hs_on, esl=ESL_0603, ron=True):
    """state: driver output per channel, {"A": "on"/"off", "B": ...}; hs_on: HS channels conduct (power state);
    ron=False: R_ON path left open (turn-off path alone)."""
    net = Net()
    net.group(leg["branches"], np.zeros_like(leg["Rac"]), leg["Lac"])
    for c in (1, 2):
        if hs_on:
            net.add("QH_D_%d" % c, "QH_S_%d" % c, 0.0)
        net.add("CapP_%d" % c, "CapN_%d" % c, 1j * w * ESL_0805 / NB.get("CapP_%d" % c, 6))
        if NB.get("CapPb_%d" % c):
            net.add("CapPb_%d" % c, "CapNb_%d" % c, 1j * w * ESL_0805 / NB["CapPb_%d" % c])
        net.add("RSI_%d" % c, "RSN_%d" % c, 1j * w * L_SHUNT)
    for q, (src, ch) in FET.items():
        net.add("K_" + q, src, 0.0)               # Kelvin pad and power source meet at the die
    for ch, p in CH.items():
        for a, b in p["rg"]:
            net.add(a, b, R_G)
        if ron:
            net.add(*p["ron"], R_ON)
        net.add(*p["roff"], R_OFF)
        net.add(*p["cdd"], 1j * w * esl)
        net.add(*p["cee"], 1j * w * esl)
        if state[ch] == "on":
            net.add(p["out"], p["vdd"], R_UP)
        else:
            net.add(p["out"], p["vee"], R_DN)
            net.add(*p["d"], R_D)                 # D_OFF conducts at turn-off
    return net


def gate_loop(q, drv, esl=ESL_0603, both=False, ron=True):
    ch = FET[q][1]
    st = {"A": "off", "B": "off"}
    st[ch] = drv
    net = build(st, hs_on=False, esl=esl, ron=ron)
    pair = [k for k, v in FET.items() if v[1] == ch] if both else [q]
    inj = {}
    for k in pair:
        inj["G_" + k] = 1.0
        inj["K_" + k] = -1.0
    V, _, _ = net.solve(w, inj, "CapN_1")
    return round(float(((V["G_" + q] - V["K_" + q]) / w).imag * 1e9), 4)


def coupling(cells, state, esl=ESL_0603):
    """induced gate-Kelvin voltage at the die (gates open) per di/dt of the forward commutation-loop current, pH"""
    net = build(state, hs_on=True, esl=esl)
    inj = {}
    for c in cells:                                # 1 A through the LS position, as in loop_post.py
        inj["QL_D_%d" % c] = 1.0
        inj["QL_S_%d" % c] = -1.0
    V, _, _ = net.solve(w, inj, "CapN_1")
    # the injection drives the loop against the forward direction -> sign flipped; M_eff in pH (v_GK = M_eff di/dt)
    return {q: round(-float(((V["G_" + q] - V["K_" + q]) / w).imag * 1e9) * 1e3, 2) for q in FET}


def kelvin_pair(ch):
    """Kelvin trace between the two Kelvin pads of a pair (die links open): L_K1 + L_K2"""
    net = build({"A": "off", "B": "off"}, hs_on=False)
    net.simple = [x for x in net.simple if not (x[0].startswith("K_Q"))]
    q1, q2 = [k for k, v in FET.items() if v[1] == ch]
    V, _, _ = net.solve(w, {"K_" + q1: 1.0, "K_" + q2: -1.0}, "CapN_1")
    return round(float(((V["K_" + q1] - V["K_" + q2]) / w).imag * 1e9), 4)


ESLS = (0.0, 0.4e-9, 0.6e-9)
gl = {}
for q in FET:
    d = {}
    for e in ESLS:
        k = "esl%.1f" % (e * 1e9)
        d[k] = {"on": gate_loop(q, "on", e), "off": gate_loop(q, "off", e),
                "off_path_only": gate_loop(q, "off", e, ron=False),
                "on_pair_driven": gate_loop(q, "on", e, both=True),
                "off_path_only_pair_driven": gate_loop(q, "off", e, both=True, ron=False)}
    gl[q] = d
# split for the circuit model: shared part (driver -> star, both FETs of the pair) and the branch per FET
split = {}
for e in ESLS:
    k = "esl%.1f" % (e * 1e9)
    sp = {}
    for q in FET:
        g = gl[q][k]
        lc_on = g["on_pair_driven"] - g["on"]
        lc_off = g["off_path_only_pair_driven"] - g["off_path_only"]
        sp[q] = {"branch": round(g["on"] - lc_on, 4), "common_on": round(lc_on, 4), "common_off": round(lc_off, 4)}
    split[k] = sp
ST = {"ls_switching_hs_held_off": {"A": "off", "B": "on"}, "hs_switching_ls_held_off": {"A": "on", "B": "off"}}
cp = {name: {"both_cells": coupling([1, 2], st), "cell1_only": coupling([1], st), "cell2_only": coupling([2], st)}
      for name, st in ST.items()}
out = {"matrix": open(os.path.join(RES, "BB_PL_GATE_%s_matrix.txt" % TAGB)).readline().strip(),
       "note": "gate loops in nH for bypass ESL 0 / 0.4 / 0.6 nH (0603 1 uF, no published value); coupling in pH",
       "gate_loop_nH": gl, "split_nH": split, "coupling_pH": cp,
       "kelvin_pair_nH": {"A": kelvin_pair("A"), "B": kelvin_pair("B")},
       "v_gk_at_30Apns_V": {name: {q: round(v * 1e-12 * 30e9, 3) for q, v in c["both_cells"].items()}
                            for name, c in cp.items()}}
json.dump(out, open(os.path.join(RES, "gate_summary_%s.json" % TAGB), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("split_nH", "kelvin_pair_nH", "coupling_pH", "v_gk_at_30Apns_V")}, indent=1))

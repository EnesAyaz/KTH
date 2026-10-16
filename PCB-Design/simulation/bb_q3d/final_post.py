"""
Post-processing of the fast Q3D set of the two final Rev B boards (run_bb_q3d_final.cmd). Uses ONLY the result files
of that run (tags dpt / load):

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\final_post.py
    -> results/final_summary.json, results/final_sweep.csv, reports/slides/data/final_numbers.json

1  loop per cell             loop_summary_<b>.json (loop_post.py, BB_PL_LOOP_<b>)
2  DC sharing, copper loss   BB_PL_REVB_<b> (full board, DC R/L): leg current from the DC terminals through the four
                             cells (R_DS(on) at 100 C, shunt 1 mOhm on the DPT board) to the AC bolt pad
3  driver-pair inductance    BB_PL_LX_<b> (cells + AC bus, AC 100 MHz): L_x between the switch nodes of the two
   L_x                       driver pairs, HS-on and LS-on path (driver skew dI/dt = V_m / L_x)
2b DC-link port, L_b        BB_PL_BANK_load (terminals + bank + bypass, AC 1 MHz): hand-over inductance bypass ->
                             bank per cell, terminals -> bank
4  three-phase level         three load-test legs (bank model: R + L at 1 MHz, cells drawing at their bypass) on the
                             PCB busbar (BB_BUS_PCB, DC R/L below 1 MHz, AC above): DC distribution 250 A -> 3 x 83 A, ripple sharing at f_sw,
                             |Z| at the cells of leg a with and without the bus, bus leg-to-leg loop
Network method, component data and loop definition as in revb_post.py (modified nodal analysis on the Q3D branches).
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "revb_post.py"), encoding="utf-8").read().split("_GEO = json.load")[0]
__file__ = os.path.join(HERE, "revb_post.py")
exec(_src)                                       # Net, block(), component data (ESL_0805, R_FET, R_SHUNT, ...)
RES = os.path.join(HERE, "results")


def load_any(tag):
    """Q3D matrix export (DC only or DC + AC) and the terminal file -> branches (source, net sink)."""
    path = os.path.join(RES, tag + "_matrix.txt")
    if not os.path.exists(path):
        return None
    lines = open(path).read().splitlines()
    out = {}
    for key, t in (("Lac", "AC Inductance Matrix"), ("Rac", "AC Resistance Matrix"), ("Ldc", "DC Inductance Matrix"),
                   ("Rdc", "DC Resistance Matrix")):
        try:
            names, M = block(lines, t)
            out[key] = M * (1e-9 if key[0] == "L" else 1.0)
            out["names"] = names
        except (KeyError, ValueError):          # missing or N/A (R-only DC)
            pass
    sinks = {}
    tf = os.path.join(RES, tag + "_terminals.txt")
    if os.path.exists(tf):
        for line in open(tf):
            if line.strip() and not line.startswith("#"):
                p = line.split()
                sinks[p[0]] = p[1]
    else:
        sinks = {"DCP": "LUG_P", "DCN": "LUG_N"}
    out["branches"] = [(n.split(":")[1], sinks[n.split(":")[0]]) for n in out["names"]]
    out["src"] = [n.split(":")[1] for n in out["names"]]
    return out


def ncap(b):
    g = json.load(open(os.path.join(RES, "revb_geometry_%s.json" % b)))
    return {t[1]: len(t[3]) for t in g["terminals"]}


def caps_of(leg, NC):
    out = []
    for src in leg["src"]:
        if src.startswith("CapP"):
            out.append((src, "CapN" + src[4:], NC.get(src, 6), "0805"))
        elif src.startswith("BankP_"):
            out.append((src, "BankN_" + src[6:], NC.get(src, 1), "1210"))
    return out


S = {}
# ================================================================== 1 loop
for b in ("dpt", "load"):
    p = os.path.join(RES, "loop_summary_%s.json" % b)
    if os.path.exists(p):
        S.setdefault(b, {})["loop"] = json.load(open(p))

# ================================================================== 2 DC sharing and copper loss
for b in ("dpt", "load"):
    leg = load_any("BB_PL_REVB_" + b)
    if not leg:
        continue
    shunt = any(t == "RSI_1" for _, t in leg["branches"])
    dc = {}
    for path in ("HS", "LS"):
        net = Net()
        net.group(leg["branches"], leg["Rdc"], np.zeros_like(leg["Rdc"]))
        idx = []
        for c in range(1, 5):
            if path == "HS":
                idx.append(len(net.simple))
                net.add("QH_D_%d" % c, "QH_S_%d" % c, R_FET)
            else:
                idx.append(len(net.simple))
                net.add("QL_D_%d" % c, "QL_S_%d" % c, R_FET)
                if shunt:
                    net.add("RSI_%d" % c, "RSN_%d" % c, R_SHUNT)
        if path == "HS":
            V, Ig, Is = net.solve(0.0, {"J_DCP": 1.0, "J_AC": -1.0}, "J_AC")
            R = float((V["J_DCP"] - V["J_AC"]).real)
            r_dev = R_FET / 4
        else:
            V, Ig, Is = net.solve(0.0, {"J_AC": 1.0, "J_DCN": -1.0}, "J_DCN")
            R = float((V["J_AC"] - V["J_DCN"]).real)
            r_dev = (R_FET + (R_SHUNT if shunt else 0.0)) / 4
        fet = [float(abs(Is[i])) for i in idx]
        dc[path] = dict(R_total_mOhm=R * 1e3, R_copper_mOhm=(R - r_dev) * 1e3, share=[f / sum(fet) for f in fet],
                        imbalance_pct=(max(fet) / min(fet) - 1) * 100)
    dc["P_copper_W"] = I_RMS ** 2 * (dc["HS"]["R_copper_mOhm"] + dc["LS"]["R_copper_mOhm"]) / 2 * 1e-3
    dc["P_shunts_W"] = (I_RMS / 4) ** 2 * R_SHUNT * 4 * 0.5 if shunt else 0.0
    S.setdefault(b, {})["dc"] = dc

# ================================================================== 2b DC-link port (bank model, same copper on both boards)
bank = load_any("BB_PL_BANK_load")
if bank and "Lac" in bank:
    w = 2 * math.pi * 1e6
    lb = []
    for c in range(1, 5):                          # bypass of cell c -> bank (banks shorted, other bypass open)
        net = Net()
        net.group(bank["branches"], np.zeros_like(bank["Lac"]), bank["Lac"])
        for src in bank["src"]:
            if src.startswith("BankP_"):
                net.add(src, "BankN_" + src[6:], 0.0)
        V, _, _ = net.solve(w, {"CapP_%d" % c: 1.0, "CapN_%d" % c: -1.0}, "J_DCN")
        lb.append(float(((V["CapP_%d" % c] - V["CapN_%d" % c]) / w).imag * 1e9))
    net = Net()                                    # terminals -> bank (all bank groups shorted)
    net.group(bank["branches"], np.zeros_like(bank["Lac"]), bank["Lac"])
    for src in bank["src"]:
        if src.startswith("BankP_"):
            net.add(src, "BankN_" + src[6:], 0.0)
    V, _, _ = net.solve(w, {"J_DCP": 1.0}, "J_DCN")
    S["bank"] = dict(L_b_nH=lb, L_term_bank_nH=float((V["J_DCP"] / w).imag * 1e9))

# ================================================================== 3 L_x between the two driver pairs
for b in ("dpt", "load"):
    leg = load_any("BB_PL_LX_" + b)
    if not leg or "Lac" not in leg:
        continue
    shunt = any(t.startswith("RSI_") for _, t in leg["branches"])
    w = 2 * math.pi * F_LOOP
    lx = {}
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
        inj = {sw % 1: -0.5, sw % 2: -0.5, sw % 3: 0.5, sw % 4: 0.5}
        V, _, _ = net.solve(w, inj, sw % 1)
        lx[path] = float((((V[sw % 3] + V[sw % 4]) - (V[sw % 1] + V[sw % 2])) / 2 / w).imag * 1e9)
    lx["dI_per_ns_A"] = 75.0 / min(lx["HS"], lx["LS"])
    S.setdefault(b, {})["lx"] = lx

# ================================================================== 4 three legs on the busbar
leg = load_any("BB_PL_BANK_load")                # DC-link port: terminals, bank, bypass (cells draw at the bypass)
bus = load_any("BB_BUS_PCB")
if leg and bus and "Lac" in leg:
    NC = {t[1]: len(t[3]) for t in json.load(open(os.path.join(RES, "revb_bank_geometry_load.json")))["terminals"]}
    caps = caps_of(leg, NC)
    LEGS = (1, 2, 3)

    def system(with_bus=True):
        def build(w):
            ac = w > 2 * math.pi * 1e6 and "Lac" in bus
            net = Net()
            for k in (LEGS if with_bus else (1,)):
                pre = "L%d." % k
                net.group(leg["branches"], leg["Rdc"] if "Rdc" in leg else leg["Rac"], leg["Lac"], pre)
                for p, n_, cnt, kind in caps:
                    net.add(pre + p, pre + n_, cap_z(cnt, kind))
                if with_bus:
                    net.add(pre + "J_DCP", "L%d_J1" % k, 0.0)
                    net.add(pre + "J_DCN", "L%d_J2" % k, 0.0)
            if with_bus:
                net.group(bus["branches"], bus["Rac" if ac else "Rdc"], bus["Lac" if ac else "Ldc"])
            return net
        return build

    out = {}
    net = system()(0.0)
    inj = {"LUG_P": I_STACK, "LUG_N": -I_STACK}
    for k in LEGS:
        for c in range(1, 5):
            inj["L%d.CapP_%d" % (k, c)] = -I_LEG / 4
            inj["L%d.CapN_%d" % (k, c)] = I_LEG / 4
    V, Ig, Is = net.solve(0.0, inj, "LUG_N")
    Ib = Ig[len(LEGS)].real
    term = {bus["src"][i]: float(abs(Ib[i])) for i in range(len(Ib))}
    out["dc"] = dict(P_bus_W=float(Ib @ bus["Rdc"] @ Ib), I_terminal_A=term, I_terminal_max_A=max(term.values()))
    per_leg = len(caps) + 2
    for f in (50e3, 100e3):
        w = 2 * math.pi * f
        net = system()(w)
        inj = {}
        for c in range(1, 5):
            inj["L1.CapP_%d" % c] = -0.25
            inj["L1.CapN_%d" % c] = 0.25
        V, Ig, Is = net.solve(w, inj, "L1.J_DCN")
        share = [float(abs(np.sum(Is[k * per_leg:k * per_leg + len(caps)]))) for k in range(len(LEGS))]
        out["ripple_%dkHz" % (f / 1e3)] = dict(share_of_leg=[s / sum(share) for s in share])
    rows = []
    for f in np.logspace(4, 7.5, 141):
        w = 2 * math.pi * f
        row = [f]
        for wb in (True, False):
            net = system(wb)(w)
            inj = {"L1.CapP_%d" % c: -0.25 for c in range(1, 5)}
            inj.update({"L1.CapN_%d" % c: 0.25 for c in range(1, 5)})
            V, _, _ = net.solve(w, inj, "L1.J_DCN")
            row.append(abs(V["L1.CapP_1"] - V["L1.CapN_1"]))
        rows.append(row)
    rows = np.array(rows)
    np.savetxt(os.path.join(RES, "final_sweep.csv"), rows, delimiter=",",
               header="f_Hz,Zin_bus_Ohm,Zin_leg_alone_Ohm", comments="")
    zb = rows[:, 1]
    out["sweep_peaks_bus"] = [[float(rows[i, 0]), float(zb[i])] for i in range(1, len(zb) - 1)
                              if zb[i] > zb[i - 1] and zb[i] > zb[i + 1]]
    S["level"] = out

# ================================================================== 5 busbar alone: leg-to-leg loop
bus = load_any("BB_BUS_PCB")
if bus:
    out = S.setdefault("level", {})
    idx = {n: i for i, n in enumerate(bus["src"])}
    for tag, Lk, Rk in (("dc", "Ldc", "Rdc"), ("ac", "Lac", "Rac")):
        if Lk not in bus:
            continue
        r = {}
        for a, b_ in ((1, 2), (2, 3), (1, 3)):
            v = np.zeros(len(idx))
            v[idx["L%d_J1" % a]] += 1.0
            v[idx["L%d_J1" % b_]] -= 1.0
            v[idx["L%d_J2" % a]] -= 1.0
            v[idx["L%d_J2" % b_]] += 1.0
            r["L_leg%d%d_nH" % (a, b_)] = float(v @ bus[Lk] @ v) * 1e9
            r["R_leg%d%d_mOhm" % (a, b_)] = float(v @ bus[Rk] @ v) * 1e3
        out["bus_" + tag] = r
    # leg DC-link port: DC inductance from the DC terminals to the bank (all caps shorted)

json.dump(S, open(os.path.join(RES, "final_summary.json"), "w"), indent=1)
os.makedirs(os.path.join(ROOT, "reports", "slides", "data"), exist_ok=True)
json.dump(S, open(os.path.join(ROOT, "reports", "slides", "data", "final_numbers.json"), "w"), indent=1)
print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "loop"} if isinstance(v, dict) else v)
                  for k, v in S.items()}, indent=1)[:4000])

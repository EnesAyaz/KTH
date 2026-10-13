"""
Post-processing of the Rev B leg (BB_PL_REVB) and the PCB busbar (BB_BUS_PCB) Q3D extractions.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\revb_post.py
    -> results/revb_summary.json, results/revb_sweep.csv, reports/slides/data/revb_numbers.json

Every Q3D source is a branch from the source terminal to its net sink, with the full (coupled) R + jwL matrix.
The network is solved by modified nodal analysis; extra elements (FET, MLCC groups, shunt, connections between the
legs and the busbar) are added as branches with their own impedance.

1  Commutation loop per cell (leg alone, AC matrix at 100 MHz, as for Rev A in bb_to_spice.py): HS FET of the
   cell shorted, MLCC groups as their ESL, UFCS shunt as 120 pH, 1 A through the LS FET of all four cells together
   (and each cell alone); loop = Im(V_LS)/w.
2  DC paths (DC matrix): leg current from the DC terminals through the four cells (FET R_DS(on) included) to the
   AC terminals: copper resistance and current sharing between the cells, for the HS and the LS (incl. shunt) path.
3  Three legs on the PCB busbar (DC R/L up to 1 MHz, AC above): stack DC current 250 A from the lugs to 3 x 83 A
   (bus and leg copper loss, current per REDCUBE terminal); ripple current of one leg at f_sw shared by the MLCC
   banks of all three legs; input impedance sweep with and without the bus (inter-leg resonance).
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
ROOT = os.path.dirname(os.path.dirname(HERE))

# ------------------------------------------------------------------ component data (assumptions, see slides)
ESL_0805, ESL_1210 = 0.48e-9, 0.5e-9          # per MLCC (same values as Rev A, bb_to_spice.py)
ESR_0805, ESR_1210 = 10e-3, 3e-3              # per MLCC at f_sw (datasheet curves, approximate)
C_0805, C_1210 = 1e-6, 10e-6
DERATE = float(os.environ.get("REVB_DERATE", "0.35"))   # X7S 100 V at 75 V DC bias (30 - 45 %)
L_SHUNT, R_SHUNT = 0.12e-9, 1.0e-3            # PMK UFCS-R001
R_FET = 0.75e-3 * 1.49                        # EPC2361 R_DS(on) 0.75 mOhm typ x 1.49 (100 C)
I_LEG = 300e3 / 16 / 3 / 75.0                 # DC current per leg (83.3 A)
I_STACK = 300e3 / 1200.0                      # 250 A
I_RMS = 228.0
F_SW = 50e3
F_LOOP = 100e6


def block(lines, title):
    for i, line in enumerate(lines):
        if line.strip() == title:
            names = lines[i + 1].split()
            return names, np.array([[float(v) for v in r.split()[1:]] for r in lines[i + 2:i + 2 + len(names)]])
    raise KeyError(title)


def load(tag, sinks=None):
    lines = open(os.path.join(RES, tag + "_matrix.txt")).read().splitlines()
    out = {}
    for key, t in (("Lac", "AC Inductance Matrix"), ("Rac", "AC Resistance Matrix"), ("Ldc", "DC Inductance Matrix"),
                   ("Rdc", "DC Resistance Matrix")):
        names, M = block(lines, t)
        out[key] = M * (1e-9 if key[0] == "L" else 1.0)
    if sinks is None:
        sinks = {}
        for line in open(os.path.join(RES, tag + "_terminals.txt")):
            if line.strip() and not line.startswith("#"):
                p = line.split()
                sinks[p[0]] = p[1]
    out["names"] = names
    out["branches"] = [(n.split(":")[1], sinks[n.split(":")[0]]) for n in names]
    return out


class Net:
    """MNA with coupled branch groups and simple branches; tiny shunt conductance on every node."""

    def __init__(self):
        self.groups = []        # (branches[(a, b)], Z-callable(w) -> matrix)
        self.simple = []        # (a, b, z-callable(w))
        self.inj = {}

    def group(self, branches, R, L, prefix=""):
        br = [(prefix + a, prefix + b) for a, b in branches]
        self.groups.append((br, lambda w, R=R, L=L: R + 1j * w * L))
        return br

    def add(self, a, b, z):
        self.simple.append((a, b, z if callable(z) else (lambda w, z=z: z)))

    def solve(self, w, inj, gnd):
        nodes = set([gnd]) | set(inj)
        for br, _ in self.groups:
            for a, b in br:
                nodes |= {a, b}
        for a, b, _ in self.simple:
            nodes |= {a, b}
        nodes = sorted(nodes - {gnd})
        idx = {n: i for i, n in enumerate(nodes)}
        nb = sum(len(br) for br, _ in self.groups) + len(self.simple)
        nv = len(nodes)
        A = np.zeros((nv + nb, nv + nb), complex)
        rhs = np.zeros(nv + nb, complex)
        for i in range(nv):
            A[i, i] += 1e-9
        col = nv
        cols = []
        for br, zf in self.groups:
            Z = zf(w)
            c0 = col
            for k, (a, b) in enumerate(br):
                for node, s in ((a, 1.0), (b, -1.0)):
                    if node in idx:
                        A[idx[node], col + k] += s
                        A[col + k, idx[node]] += s
                A[col + k, c0:c0 + len(br)] -= Z[k]
            cols.append((c0, len(br)))
            col += len(br)
        scol = col
        for a, b, zf in self.simple:
            for node, s in ((a, 1.0), (b, -1.0)):
                if node in idx:
                    A[idx[node], col] += s
                    A[col, idx[node]] += s
            A[col, col] -= zf(w)
            col += 1
        for n, cur in inj.items():
            if n in idx:
                rhs[idx[n]] += cur
        x = np.linalg.solve(A, rhs)
        V = {n: x[i] for n, i in idx.items()}
        V[gnd] = 0.0
        I_groups = [x[c0:c0 + n] for c0, n in cols]
        I_simple = x[scol:col]
        return V, I_groups, I_simple


def cap_groups(names):
    """MLCC groups of a leg: (P terminal, N terminal, n parts, kind)."""
    out = []
    for n in names:
        src = n.split(":")[1]
        if src.startswith("CapP_"):
            out.append((src, "CapN_" + src[5:], 6, "0805"))
        elif src.startswith("BankP_"):
            g = src[6:]
            out.append((src, "BankN_" + g, 15 if g == "C" else 12, "1210"))
    return out


def cap_z(n, kind, with_c=True):
    esl, esr, c = (ESL_0805, ESR_0805, C_0805) if kind == "0805" else (ESL_1210, ESR_1210, C_1210)

    def z(w):
        zz = (esr + 1j * w * esl) / n
        if with_c:
            zz = zz + (1.0 / (1j * w * n * c * DERATE) if w > 0 else 1e12)
        return zz
    return z


summary = {}
leg = load("BB_PL_REVB") if os.path.exists(os.path.join(RES, "BB_PL_REVB_matrix.txt")) else None
bus = load("BB_BUS_PCB", {"DCP": "LUG_P", "DCN": "LUG_N"}) if os.path.exists(
    os.path.join(RES, "BB_BUS_PCB_matrix.txt")) else None

# ================================================================== 1 commutation loop
if leg:
    caps = cap_groups(leg["names"])
    w = 2 * math.pi * F_LOOP
    res = {}
    for label, use in (("local_only", [c for c in caps if c[0].startswith("CapP")]), ("local_and_bank", caps)):
        for shunt_l in (0.0, L_SHUNT):
            for which in ("all", 1, 2, 3, 4):
                cells = [1, 2, 3, 4] if which == "all" else [which]
                net = Net()
                net.group(leg["branches"], np.zeros_like(leg["Rac"]), leg["Lac"])
                for c in range(1, 5):
                    net.add("QH_D_%d" % c, "QH_S_%d" % c, 0.0)
                    net.add("RSI_%d" % c, "RSN_%d" % c, 1j * w * shunt_l)
                for p, n_, cnt, kind in use:
                    net.add(p, n_, 1j * w * (ESL_0805 if kind == "0805" else ESL_1210) / cnt)
                inj = {}
                for c in cells:
                    inj["QL_D_%d" % c] = inj.get("QL_D_%d" % c, 0) + 1.0
                    inj["QL_S_%d" % c] = inj.get("QL_S_%d" % c, 0) - 1.0
                V, _, _ = net.solve(w, inj, "J2")
                key = "%s_%s_%s" % (label, "shunt" if shunt_l else "noshunt", which)
                res[key] = {"L_cell%d_nH" % c: float(((V["QL_D_%d" % c] - V["QL_S_%d" % c]) / w).imag * 1e9)
                            for c in cells}
    summary["loop"] = res
    main = res["local_and_bank_shunt_all"]
    summary["L_cell_nH"] = main
    summary["L_cell_mean_nH"] = float(np.mean(list(main.values())))

    # ============================================================== 2 DC paths and sharing
    dc = {}
    for path in ("HS", "LS"):
        net = Net()
        net.group(leg["branches"], leg["Rdc"], leg["Ldc"])
        for c in range(1, 5):
            if path == "HS":
                net.add("QH_D_%d" % c, "QH_S_%d" % c, R_FET)
            else:
                net.add("QL_D_%d" % c, "QL_S_%d" % c, R_FET)
                net.add("RSI_%d" % c, "RSN_%d" % c, R_SHUNT)
        # DC terminals joined (bus), AC terminals joined (bar)
        net.add("J1", "J12", 0.0)
        net.add("J2", "J13", 0.0)
        for j in ("J24", "J26", "J27"):
            net.add("J25", j, 0.0)
        if path == "HS":
            V, Ig, Is = net.solve(0.0, {"J1": 1.0, "J25": -1.0}, "J25")
            R = float((V["J1"] - V["J25"]).real)
            fet = [float(abs(Is[c])) for c in range(4)]
            r_fets = R_FET / 4
        else:
            V, Ig, Is = net.solve(0.0, {"J25": 1.0, "J2": -1.0}, "J2")
            R = float((V["J25"] - V["J2"]).real)
            fet = [float(abs(Is[2 * c])) for c in range(4)]
            r_fets = (R_FET + R_SHUNT) / 4
        dc[path] = dict(R_total_mOhm=R * 1e3, R_copper_mOhm=(R - r_fets) * 1e3,
                        share=[f / sum(fet) for f in fet], imbalance_pct=(max(fet) / min(fet) - 1) * 100)
    dc["P_copper_W"] = I_RMS ** 2 * (dc["HS"]["R_copper_mOhm"] + dc["LS"]["R_copper_mOhm"]) / 2 * 1e-3
    dc["P_shunts_W"] = (I_RMS / 4) ** 2 * R_SHUNT * 4 * 0.5        # shunts conduct in the LS interval (~50 %)
    summary["dc_leg"] = dc

    # ============================================================== 2b block-to-block inductance L_x
    # driver skew: block 2 switches dt later -> circulating current dI = V_m dt / L_x through the joined AC copper
    # and back through the DC link copper (HS on in both blocks: DCP path; LS on: LSRC/shunt/DCN path)
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
                net.add("RSI_%d" % c, "RSN_%d" % c, 1j * w * L_SHUNT)
        sw = "QH_S_%d" if path == "HS" else "QL_D_%d"
        inj = {sw % 1: -0.5, sw % 2: -0.5, sw % 3: 0.5, sw % 4: 0.5}
        V, _, _ = net.solve(w, inj, sw % 1)
        lx[path] = float((((V[sw % 3] + V[sw % 4]) - (V[sw % 1] + V[sw % 2])) / 2 / w).imag * 1e9)
    lx["dI_per_ns_A"] = 75.0 * 1e-9 / (min(lx["HS"], lx["LS"]) * 1e-9)
    summary["block_to_block"] = lx

# ================================================================== 3 three legs on the busbar
if leg and bus:
    LEGS = (1, 2, 3)

    def system(with_bus=True, w_split=1e6):
        """returns a builder(w) -> Net for frequency w: DC matrices below w_split, AC above."""
        def build(w):
            ac = w > 2 * math.pi * w_split
            net = Net()
            for k in (LEGS if with_bus else (1,)):
                pre = "L%d." % k
                net.group(leg["branches"], leg["Rac" if ac else "Rdc"], leg["Lac" if ac else "Ldc"], pre)
                for p, n_, cnt, kind in cap_groups(leg["names"]):
                    net.add(pre + p, pre + n_, cap_z(cnt, kind))
                for c in range(1, 5):
                    net.add(pre + "RSI_%d" % c, pre + "RSN_%d" % c, lambda w: R_SHUNT + 1j * w * L_SHUNT)
                if with_bus:
                    for j in ("J1", "J2", "J12", "J13"):
                        net.add(pre + j, "L%d_%s" % (k, j), 0.0)
                else:
                    net.add(pre + "J1", pre + "J12", 0.0)
                    net.add(pre + "J2", pre + "J13", 0.0)
            if with_bus:
                net.group(bus["branches"], bus["Rac" if ac else "Rdc"], bus["Lac" if ac else "Ldc"])
            return net
        return build

    out = {}
    # 3a DC: 250 A from the lugs, 83 A per leg drawn at the cells (HS drain -> shunt SHLD, i.e. through the switch)
    net = system()(0.0)
    inj = {"LUG_P": I_STACK, "LUG_N": -I_STACK}
    for k in LEGS:
        for c in range(1, 5):
            inj["L%d.QH_D_%d" % (k, c)] = -I_LEG / 4
            inj["L%d.RSN_%d" % (k, c)] = I_LEG / 4
    V, Ig, Is = net.solve(0.0, inj, "LUG_N")
    gi = len(LEGS)                                   # group order: legs, then bus
    Ib = Ig[gi].real
    P_bus = float(Ib @ bus["Rdc"] @ Ib)
    P_legs = [float(Ig[k].real @ leg["Rdc"] @ Ig[k].real) for k in range(gi)]
    term = {bus["names"][i].split(":")[1]: float(abs(Ib[i])) for i in range(len(Ib))}
    out["dc"] = dict(P_bus_W=P_bus, P_leg_dc_W=P_legs, I_terminal_A=term, I_terminal_max_A=max(term.values()))

    # 3b ripple sharing at f_sw: 1 A drawn by the cells of leg 1, stack lugs open
    for f in (F_SW, 100e3):
        w = 2 * math.pi * f
        net = system()(w)
        inj = {}
        for c in range(1, 5):
            inj["L1.QH_D_%d" % c] = -0.25
            inj["L1.RSN_%d" % c] = 0.25
        V, Ig, Is = net.solve(w, inj, "L1.J2")
        # simple branches are added leg by leg: caps first (10 per leg), shunts (4), connections (4)
        per_leg = len(cap_groups(leg["names"])) + 4 + 4
        share = []
        for k in range(len(LEGS)):
            icap = Is[k * per_leg:k * per_leg + len(cap_groups(leg["names"]))]
            share.append(float(abs(np.sum(icap))))
        out["ripple_%dkHz" % (f / 1e3)] = dict(share_of_leg=[s / sum(share) for s in share],
                                               Zin_mOhm=float(abs(V["L1.QH_D_1"] - V["L1.RSN_1"])) * 1e3)
    # 3c impedance sweep at the cells of leg 1, with the bus (3 legs) and leg 1 alone
    rows = []
    for f in np.logspace(4, 7.5, 141):
        w = 2 * math.pi * f
        row = [f]
        for wb in (True, False):
            net = system(wb)(w)
            inj = {"L1.QH_D_%d" % c: -0.25 for c in range(1, 5)}
            inj.update({"L1.RSN_%d" % c: 0.25 for c in range(1, 5)})
            V, _, _ = net.solve(w, inj, "L1.J2")
            row.append(abs(V["L1.QH_D_1"] - V["L1.RSN_1"]))
        rows.append(row)
    rows = np.array(rows)
    np.savetxt(os.path.join(RES, "revb_sweep.csv"), rows, delimiter=",", header="f_Hz,Zin_bus_Ohm,Zin_leg_alone_Ohm",
               comments="")
    zb = rows[:, 1]
    pk = [i for i in range(1, len(zb) - 1) if zb[i] > zb[i - 1] and zb[i] > zb[i + 1]]
    out["sweep_peaks_bus"] = [[float(rows[i, 0]), float(zb[i])] for i in pk]
    # bus alone: leg-to-leg loop (DC+ in at leg a, out at leg b, DC- back), DC and AC matrices
    for tag, Lk, Rk in (("dc", "Ldc", "Rdc"), ("ac", "Lac", "Rac")):
        idx = {n.split(":")[1]: i for i, n in enumerate(bus["names"])}
        r = {}
        for a, b in ((1, 2), (2, 3), (1, 3)):
            v = np.zeros(len(idx))
            for j, s in (("J1", 0.5), ("J12", 0.5)):
                v[idx["L%d_%s" % (a, j)]] += s
                v[idx["L%d_%s" % (b, j)]] -= s
            for j, s in (("J2", 0.5), ("J13", 0.5)):
                v[idx["L%d_%s" % (a, j)]] -= s
                v[idx["L%d_%s" % (b, j)]] += s
            r["L_leg%d%d_nH" % (a, b)] = float(v @ bus[Lk] @ v) * 1e9
            r["R_leg%d%d_mOhm" % (a, b)] = float(v @ bus[Rk] @ v) * 1e3
        out["bus_" + tag] = r
    summary["system"] = out

json.dump(summary, open(os.path.join(RES, "revb_summary.json"), "w"), indent=1)
os.makedirs(os.path.join(ROOT, "reports", "slides", "data"), exist_ok=True)
json.dump(summary, open(os.path.join(ROOT, "reports", "slides", "data", "revb_numbers.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in summary.items() if k != "loop"}, indent=1))

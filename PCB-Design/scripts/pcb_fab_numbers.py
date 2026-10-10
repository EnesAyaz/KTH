"""
Numbers for reports/pcb-fab: gate-drive budget (EPC2361 datasheet, 2EDF7275K, split rail) and minimum copper
spacing between the isolation domains of the routed fabrication board (pads, tracks, vias; zones excluded).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\pcb_fab_numbers.py
-> reports/pcb-fab/numbers.tex, reports/pcb-fab/figures/*.png
"""
import json
import math
import os

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "reports", "pcb-fab")
FIG = os.path.join(REP, "figures")
os.makedirs(FIG, exist_ok=True)
BRD = os.path.join(ROOT, "hardware", "spb-bb-fab", "spb-bb-fab.kicad_pcb")

N = {}
# ------------------------------------------------------------------ gate drive budget
QG5 = 28e-9            # EPC2361 QG at 5 V, VDS 50 V (typ)
CISS = 3599e-12        # EPC2361 Ciss (typ)
RGI = 0.4
VDD, VEE = 5.05, -1.24  # split rail VDD-S and VEE-S
VLDO = 1.185 * (1 + 102 / 23.7)
NPAR = 2
QNEG = CISS * abs(VEE)                        # extra charge below 0 V (approx. Ciss, no Miller below Vth)
QFET = QG5 + QNEG
QCH = NPAR * QFET
R_PU, R_PD = 0.85, 0.35                       # 2EDF7275K typ output resistance
R_COM, R_IND = 0.75, 0.5
r_br = (R_IND + RGI) / NPAR
I_on = (VDD - VEE) / (R_PU + R_COM + r_br)
R_OFFC, VF, RD = 0.0, 0.40, 0.10            # turn-off path: R_OFF (0 R default) + Schottky (VF, dynamic R)
I_off = (VDD - VEE - VF) / (R_PD + R_OFFC + RD + r_br)
N["QFET"] = "%.1f" % (QFET * 1e9)
N["QCH"] = "%.0f" % (QCH * 1e9)
N["CissTwenty"] = "%.0f" % (20 * NPAR * CISS * 1e9)
N["CdecRatio"] = "%.0f" % (1e-6 / (NPAR * CISS))
N["Ion"] = "%.1f" % I_on
N["Ioff"] = "%.1f" % I_off
N["RgFet"] = "%.1f" % (NPAR * R_COM + R_IND)
N["RoffFet"] = "%.1f" % (NPAR * R_OFFC + R_IND)
N["IoffNoDiodeR"] = "%.1f" % ((VDD - VEE - VF) / (R_PD + RD + RGI / NPAR))
N["Vldo"] = "%.2f" % VLDO
I_DRV = 2.0e-3                                 # output-side quiescent current per channel (assumed, datasheet max order)
I_SH = (VLDO - (VDD - VEE) + VDD) / 2.2e3 if False else (VDD) / 2.2e3
I_DIV = VLDO / (102e3 + 23.7e3)
for f in (50e3, 100e3):
    k = "%d" % (f / 1e3)
    ig = QCH * f
    itot = ig + I_DRV + I_SH + I_DIV
    N["Ig" + ("Fifty" if f == 50e3 else "Hundred")] = "%.1f" % (ig * 1e3)
    N["Itot" + ("Fifty" if f == 50e3 else "Hundred")] = "%.1f" % (itot * 1e3)
    N["Pgate" + ("Fifty" if f == 50e3 else "Hundred")] = "%.0f" % (QCH * (VDD - VEE) * f * 1e3)
    N["Pldo" + ("Fifty" if f == 50e3 else "Hundred")] = "%.0f" % ((8.0 - VLDO) * itot * 1e3)
    N["Pch" + ("Fifty" if f == 50e3 else "Hundred")] = "%.0f" % (8.0 * itot * 1e3)
N["Ish"] = "%.1f" % (I_SH * 1e3)

# ------------------------------------------------------------------ heatsink estimate (rated point, paper numbers)
PDEV, PLEG, PLEGW = 1.91, 12.49, 14.34          # W per transistor, W per leg (typ / worst)
R_JC, A_FET = 0.2, 15e-6                         # K/W top, m^2 package top
T_PAD, K_PAD = 0.4e-3, 5.0                       # compressed gap pad thickness, W/mK
R_PAD = T_PAD / (K_PAD * A_FET)
R_SP, R_SA = 0.15, 0.65                          # spreader (estimate), LAM 4 K 50 12 at its fan
TA = 40.0
P_HS = 4 * PDEV
TJ = TA + PDEV * (R_JC + R_PAD) + P_HS * (R_SP + R_SA)
N["RPad"] = "%.1f" % R_PAD
N["THSrise"] = "%.0f" % (P_HS * (R_SP + R_SA))
N["TjHS"] = "%.0f" % TJ
N["PHS"] = "%.1f" % P_HS
N["TjHSWorst"] = "%.0f" % (TA + PDEV * PLEGW / PLEG * (R_JC + R_PAD) + P_HS * PLEGW / PLEG * (R_SP + R_SA))

# ------------------------------------------------------------------ board facts and domain spacing
b = pcbnew.LoadBoard(BRD)
bb = b.GetBoardEdgesBoundingBox()
N["BoardW"] = "%.1f" % pcbnew.ToMM(bb.GetWidth())
N["BoardH"] = "%.1f" % pcbnew.ToMM(bb.GetHeight())
N["NFoot"] = "%d" % len(b.GetFootprints())
nv = sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA")
nt = sum(1 for t in b.GetTracks() if t.GetClass() != "PCB_VIA")
N["NVia"] = "%d" % nv
N["NTrack"] = "%d" % nt
DOM = {"PRI": {"GNDI", "+12V", "PWM_H", "PWM_L", "DIS", "INA", "INB", "VDDI", "LEDA_12V"},
       "HS": {"SW", "OFFA", "LEDA_ISOA", "LEDA_VDDA", "VDDA", "VEEA", "ISOA_P", "ADJA", "OUTA", "GH_STAR", "GH_L", "GH_R"},
       "LS": {"DCN", "OFFB", "LEDA_ISOB", "LEDA_VDDB", "VDDB", "VEEB", "ISOB_P", "ADJB", "OUTB", "GL_STAR", "GL_L", "GL_R", "NTC"},
       "DCP": {"DCP", "HVA", "HVB"}}


def dom(n):
    for k, v in DOM.items():
        if n in v:
            return k
    return None


items = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        d = dom(p.GetNetname())
        if d is None:
            continue
        r = p.GetBoundingBox()
        lays = [l for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if p.IsOnLayer(l)]
        items.append((d, lays, "r", tuple(pcbnew.ToMM(v) for v in (r.GetLeft(), r.GetTop(), r.GetRight(), r.GetBottom()))))
for t in b.GetTracks():
    d = dom(t.GetNetname())
    if d is None:
        continue
    if t.GetClass() == "PCB_VIA":
        items.append((d, [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu], "c",
                      (pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y), pcbnew.ToMM(t.GetWidth()) / 2)))
    else:
        items.append((d, [t.GetLayer()], "s", (pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y),
                                               pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y),
                                               pcbnew.ToMM(t.GetWidth()) / 2)))


def samples(it):
    k, g = it[2], it[3]
    if k == "r":
        xa, ya, xb, yb = g
        pts = []
        for i in range(9):
            for j in range(9):
                pts.append((xa + (xb - xa) * i / 8, ya + (yb - ya) * j / 8, 0.0))
        return pts
    if k == "c":
        return [(g[0] + g[2] * math.cos(a), g[1] + g[2] * math.sin(a), 0.0) for a in [i * math.pi / 8 for i in range(16)]]
    n = max(2, int(math.hypot(g[2] - g[0], g[3] - g[1]) / 0.05))
    return [(g[0] + (g[2] - g[0]) * i / n, g[1] + (g[3] - g[1]) * i / n, g[4]) for i in range(n + 1)]


def dist(a, b):
    best = 1e9
    sb = samples(b)
    for (x, y, ra) in samples(a):
        for (u, v, rb) in sb:
            dd = math.hypot(x - u, y - v) - ra - rb
            if dd < best:
                best = dd
    return max(best, 0.0)


def bbox(it):
    k, g = it[2], it[3]
    if k == "r":
        return g
    if k == "c":
        return (g[0] - g[2], g[1] - g[2], g[0] + g[2], g[1] + g[2])
    return (min(g[0], g[2]) - g[4], min(g[1], g[3]) - g[4], max(g[0], g[2]) + g[4], max(g[1], g[3]) + g[4])


pairs = {}
LN = {pcbnew.F_Cu: "outer", pcbnew.B_Cu: "outer", pcbnew.In1_Cu: "inner", pcbnew.In2_Cu: "inner"}
for i, a in enumerate(items):
    ba = bbox(a)
    for bq in items[i + 1:]:
        if a[0] == bq[0]:
            continue
        common = set(a[1]) & set(bq[1])
        if not common:
            continue
        bb2 = bbox(bq)
        gap = max(bb2[0] - ba[2], ba[0] - bb2[2], bb2[1] - ba[3], ba[1] - bb2[3], 0)
        key = tuple(sorted((a[0], bq[0])))
        for l in common:
            kk = key + (LN[l],)
            if gap > pairs.get(kk, (9.0,))[0]:
                continue
            d = dist(a, bq)
            if d < pairs.get(kk, (9.0,))[0]:
                pairs[kk] = (d,)
SP = {}
for k, (d,) in sorted(pairs.items()):
    SP["-".join(k)] = round(d, 2)
    print(k, "%.2f" % d)
json.dump(SP, open(os.path.join(REP, "spacing.json"), "w"), indent=1)
name = {"PRI": "Pri", "HS": "Hs", "LS": "Ls", "DCP": "Dcp"}
for k, v in SP.items():
    a, c, l = k.split("-")
    N["Sp%s%s%s" % (name[a], name[c], l.capitalize())] = "%.2f" % v

with open(os.path.join(REP, "numbers.tex"), "w") as f:
    f.write("% generated by scripts/pcb_fab_numbers.py\n")
    for k, v in N.items():
        f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
print(json.dumps(N, indent=1))

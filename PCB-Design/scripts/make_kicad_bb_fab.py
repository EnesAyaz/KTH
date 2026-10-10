"""
Fabrication layout (Rev A) of the SPB leg building block: 2 x EPC2361 per switch, 2EDF7275K (bottom side), two
MGN1S1208MC isolated gate supplies with +5.0 V / -1.24 V split rails, REDCUBE power terminals, lab header.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\make_kicad_bb_fab.py

Writes hardware/spb-bb-fab/spb-bb-fab.kicad_pcb (+ .kicad_pro), runs zone fill and DRC (drc_report.txt).
Power copper follows simulation/bb_q3d/bb_geometry.py with the fabrication parameters FAB below (wider driver
corridor); every pad, via, zone and track carries a net. Engineering review and Q3D re-extraction of this layout
are required before ordering (see reports/pcb-fab).
"""
import math
import os
import sys

KI = "C:/Program Files/KiCad/7.0/share/kicad"
os.environ.setdefault("KICAD7_3DMODEL_DIR", KI + "/3dmodels")
os.environ.setdefault("KICAD7_FOOTPRINT_DIR", KI + "/footprints")
os.environ.setdefault("KICAD7_SYMBOL_DIR", KI + "/symbols")
import pcbnew  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "simulation", "bb_q3d"))
import bb_geometry as geo  # noqa: E402

OUT = os.path.join(ROOT, "hardware", "spb-bb-fab")
os.makedirs(OUT, exist_ok=True)
NAME = "spb-bb-fab"
FP = KI + "/footprints/"
EPC_LIB = os.path.join(ROOT, "hardware", "epc2361-cell", "epc2361-cell.pretty")
MM = pcbnew.FromMM

# ------------------------------------------------------------------ fabrication geometry
FAB = dict(xc=9.5, x_edge=16.0, bank_x=(5.75, 8.75, 11.75, 14.75), cap_p=1.6)
G = geo.build(FAB)
P, Y = G["params"], G["rows"]
XE = P["x_edge"]
XC = P["xc"]
EDGE = 1.0                                   # copper-free board margin (functional; insulation per report)
TZ = 10.0                                    # DC terminal zone
TAB = 46.2                                   # tab: AC terminal, gate supplies, header
XO = XE + EDGE + 4.0                         # +4 mm per side: heatsink holes and probe pads beside the cells
YT = Y["p1"][0] - TZ
Y0, Y1 = YT - EDGE, Y["t_ac"][1] + TAB
YQH = sum(Y["qhd"]) / 2 + 1.0                # FET body centres (stripe pads span +-1.7 mm)
YQL = sum(Y["qld"]) / 2 + 1.0
LAYER = {"L1": pcbnew.F_Cu, "L2": pcbnew.In1_Cu, "L3": pcbnew.In2_Cu, "L4": pcbnew.B_Cu}

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(1.6))
ds.m_MinClearance = MM(0.15)
ds.m_TrackMinWidth = MM(0.15)
ds.m_ViasMinSize = MM(0.45)
ds.m_MinThroughDrill = MM(0.25)
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(MM(0.15))
nc.SetTrackWidth(MM(0.25))
nc.SetViaDiameter(MM(0.6))
nc.SetViaDrill(MM(0.3))

NETS = {}


def net(name):
    if name not in NETS:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        NETS[name] = n
    return NETS[name]


def vec(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def seg(layer, pts, width, n):
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(vec(x0, y0))
        t.SetEnd(vec(x1, y1))
        t.SetWidth(MM(width))
        t.SetLayer(layer)
        t.SetNet(net(n))
        board.Add(t)


def via(x, y, n, d=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetWidth(MM(d))
    v.SetDrill(MM(drill))
    v.SetNet(net(n))
    v.SetIsFree(True)                           # keep the scripted net (KiCad would otherwise re-net it on save)
    board.Add(v)
    return v


def zone(layer, n, pts, prio=0, clearance=0.2, minw=0.2):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net(n))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(minw))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(MM(x), MM(y))
    board.Add(z)
    return z


def rect_zone(layer, n, x0, x1, y0, y1, prio=0, clearance=0.2):
    return zone(layer, n, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], prio, clearance)


def keepout(layer, x0, x1, y0, y1):
    """rule area: no copper pour (tracks and vias allowed) - used for the Kelvin slots in the L2 DC- plane."""
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowTracks(False)
    z.SetDoNotAllowVias(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        ol.Append(MM(x), MM(y))
    board.Add(z)


def text(s, x, y, size=0.8, layer=pcbnew.F_SilkS, mirror=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(vec(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    if mirror:
        t.SetMirrored(True)
    board.Add(t)


PARTS = []


def place(lib, name, ref, value, x, y, rot=0.0, bottom=False, nets=None, mpn="", model=None):
    fp = pcbnew.FootprintLoad(lib, name)
    if fp is None:
        raise RuntimeError("footprint not found: %s / %s" % (lib, name))
    return finish(fp, ref, value, x, y, rot, bottom, nets, mpn, name, model)


FPNICK = [("R_", "Resistor_SMD"), ("C_", "Capacitor_SMD"), ("D_SOD", "Diode_SMD"), ("MSOP", "Package_SO"), ("HVSSOP", "Package_SO"),
          ("SOT-23", "Package_TO_SOT_SMD"), ("PinHeader", "Connector_PinHeader_2.54mm"),
          ("Wuerth", "TerminalBlock_Wuerth"), ("TestPoint", "TestPoint"), ("MountingHole", "MountingHole"),
          ("EPC2361", "epc2361-cell"), ("2EDF", "spb_fab"), ("Murata_MGN1", "spb_fab"), ("LED_", "LED_SMD"),
          ("Probe_", "spb_fab"), ("HS_", "spb_fab")]


def finish(fp, ref, value, x, y, rot, bottom, nets, mpn, fpname, model=None):
    for pre, nick in FPNICK:
        if fpname.startswith(pre):
            fp.SetFPID(pcbnew.LIB_ID(nick, fpname))
            break
    fp.SetReference(ref)
    fp.SetValue(value)
    board.Add(fp)
    fp.SetPosition(vec(x, y))
    fp.SetOrientationDegrees(rot)
    if bottom:
        fp.Flip(fp.GetPosition(), False)
    for m in fp.Models():
        m.m_Filename = m.m_Filename.replace("${KICAD6_3DMODEL_DIR}", "${KICAD7_3DMODEL_DIR}")
    if fpname.startswith("HVSSOP") and not model:
        # KiCad 7 ships no HVSSOP-8 model; the MSOP-8-1EP 3x3 body has the same outline
        model = "${KICAD7_3DMODEL_DIR}/Package_SO.3dshapes/MSOP-8-1EP_3x3mm_P0.65mm_EP1.68x1.88mm.wrl"
    if model:
        fp.Models().clear()
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = model.replace("\\", "/")
        fp.Models().push_back(m)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    if nets:
        for pad in fp.Pads():
            k = pad.GetNumber()
            if k in nets and nets[k]:
                pad.SetNet(net(nets[k]))
    PARTS.append(dict(ref=ref, value=value, footprint=fpname, mpn=mpn, x=x, y=y, rot=rot,
                      side="bottom" if bottom else "top"))
    return fp


def custom_fp(name, pads, courtyard, descr="", model=None, paste=True):
    """pads: list of (number, x, y, w, h, shape) top view; SMD; shape rr / r / c."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID("spb_fab", name))
    fp.SetDescription(descr)
    for num, x, y, w, h, shape in pads:
        p = pcbnew.PAD(fp)
        p.SetNumber(num)
        p.SetShape({"rr": pcbnew.PAD_SHAPE_ROUNDRECT, "c": pcbnew.PAD_SHAPE_CIRCLE}.get(shape, pcbnew.PAD_SHAPE_RECT))
        if shape == "rr":
            p.SetRoundRectRadiusRatio(0.25)
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        ls = p.SMDMask()
        if not paste:
            ls.RemoveLayer(pcbnew.F_Paste)
        p.SetLayerSet(ls)
        p.SetSize(pcbnew.VECTOR2I(MM(w), MM(h)))
        p.SetPos0(vec(x, y))
        p.SetPosition(vec(x, y))
        fp.Add(p)
    x0, y0, x1, y1 = courtyard
    for (a, b), (c, d) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        for lay, w in (((pcbnew.F_CrtYd, 0.05), (pcbnew.F_Fab, 0.1)) if pads else ((pcbnew.F_Fab, 0.1),)):
            sh = pcbnew.FP_SHAPE(fp)
            sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
            sh.SetStart0(vec(a, b))
            sh.SetEnd0(vec(c, d))
            sh.SetLayer(lay)
            sh.SetWidth(MM(w))
            sh.SetDrawCoord()
            fp.Add(sh)
    if model:
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = "${KIPRJMOD}/3d/" + model
        fp.Models().push_back(m)
    return fp


def lga13():
    """2EDF7275K PG-TFLGA-13-4 (datasheet Fig. 22, top view): 0.35 x 0.75 mm pads, 0.65 mm pitch, rows 4.1 mm apart.
    Bottom row (y = +2.05): pins 1..7 left to right (pin 1 = GNDI); top row (y = -2.05), left to right:
    13 VDDA, 12 OUTA, 11 GNDA, (no pad), 10 VDDB, 9 OUTB, 8 GNDB."""
    pads = [(str(k + 1), -1.95 + 0.65 * k, 2.05, 0.35, 0.75, "rr") for k in range(7)]
    for num, x in (("13", -1.95), ("12", -1.3), ("11", -0.65), ("10", 0.65), ("9", 1.3), ("8", 1.95)):
        pads.append((num, x, -2.05, 0.35, 0.75, "rr"))
    return custom_fp("2EDF7275K_PG-TFLGA-13-4", pads, (-2.6, -2.5, 2.6, 2.5), "Infineon 2EDF7275K, datasheet Rev 3.0 Fig. 22",
                     model="2EDF7275K_PG-TFLGA-13-4.wrl")


def mgn1():
    """Murata MGN1 single-output SMD (datasheet KDC_MGN1_B02 p.17, top view): pads 1.0 x 2.3 mm, columns at x = +-5.625
    (outer) and +-4.375 (inner), rows at y = -+5.5. Top view: inputs right (1 -Vin outer-top, 2 -Vin inner-top,
    20 +Vin outer-bottom, 19 +Vin inner-bottom), outputs left (10 0V outer-top, 9 0V inner-top, 11 +Vout outer-bottom,
    12 +Vout inner-bottom)."""
    pads = []
    for num, x, y in (("1", 5.625, -5.5), ("2", 4.375, -5.5), ("20", 5.625, 5.5), ("19", 4.375, 5.5),
                      ("10", -5.625, -5.5), ("9", -4.375, -5.5), ("11", -5.625, 5.5), ("12", -4.375, 5.5)):
        pads.append((num, x, y, 1.0, 2.3, "r"))
    return custom_fp("Murata_MGN1_SMD", pads, (-7.5, -7.0, 7.5, 7.0), "Murata MGN1S1208MC, KDC_MGN1_B02 p.17",
                     model="Murata_MGN1_SMD.wrl")


def probe(two_sig):
    """probe landing for passive probes with spring ground, 2.5 and 5.0 mm tip-to-ground spacing.
    two_sig = False: signal (1) at 0, ground (2) at +2.5 and +5.0 mm; True: ground at 0, signal at -2.5 and -5.0 mm."""
    if two_sig:
        pads = [("2", 0, 0, 1.0, 1.0, "c"), ("1", 0, -2.5, 1.0, 1.0, "c"), ("1", 0, -5.0, 1.0, 1.0, "c")]
        cy = (-0.7, -5.7, 0.7, 0.7)
        nm = "Probe_2Sig1Gnd_2.5_5.0"
    else:
        pads = [("1", 0, 0, 1.0, 1.0, "c"), ("2", 0, 2.5, 1.0, 1.0, "c"), ("2", 0, 5.0, 1.0, 1.0, "c")]
        cy = (-0.7, -0.7, 0.7, 5.7)
        nm = "Probe_1Sig2Gnd_2.5_5.0"
    return custom_fp(nm, pads, cy, "probe landing: tip pad 1, spring-ground pad 2 at 2.5 / 5.0 mm", paste=False), nm


def heatsink_fp():
    return custom_fp("HS_LAM4K5012_assembly", [], (-21.0, -10.15, 21.0, 11.25),
                     "Fischer LAM 4 K 50 12 fan heatsink on an aluminium spreader with insulating gap pads",
                     model="HS_LAM4K5012_assembly.wrl")


# project footprint library with the two footprints drawn here (fp-lib-table written by make_kicad_sch.py)
_lib = os.path.join(OUT, "spb_fab.pretty")
os.makedirs(_lib, exist_ok=True)
for _f in (lga13(), mgn1(), probe(False)[0], probe(True)[0], heatsink_fp()):
    _f.SetReference("REF**")
    pcbnew.FootprintSave(_lib, _f)

print("STEP outline", flush=True)
# ------------------------------------------------------------------ outline
def edge(x0, y0, x1, y1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(vec(x0, y0))
    s.SetEnd(vec(x1, y1))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    board.Add(s)


edge(-XO, Y0, XO, Y1)

print("STEP power copper", flush=True)
# ------------------------------------------------------------------ power copper (zones from the Q3D geometry)
NETMAP = {"DCP": "DCP", "DCN": "DCN", "AC": "SW"}
VIA_SHIFT = {round(Y["dcp_via"], 2): 2.5, round(Y["src_via"], 2): 11.5}   # off the 3.6 mm FET stripes
for n, nm, lay, x0, x1, y0, y1 in G["boxes"]:
    if lay in LAYER and n:
        prio = 2 if lay == "L1" else 1
        if nm in ("SRC_L", "SRC_R"):
            y1 = 11.95
        rect_zone(LAYER[lay], NETMAP[n], max(x0, -XE), min(x1, XE), y0, y1, prio)
POWER_VIAS = []
for n, x, y, to in G["vias"]:
    POWER_VIAS.append(via(x, VIA_SHIFT.get(round(y, 2), y), NETMAP[n]))
# DC terminal zone: DC+ left (L1, L3; L2/L4 below the strip), DC- right (all layers, L2 joins the DC- plane)
for lay in ("L1", "L2", "L3", "L4"):
    rect_zone(LAYER[lay], "DCP", -12.0, -1.0, YT, Y["p1"][0] - (0 if lay in ("L1", "L3") else 0.6), 1)
    rect_zone(LAYER[lay], "DCN", 1.0, 12.0, YT, Y["p1"][0] - 0.6 if lay != "L2" else Y["l2"][0], 1)
# Kelvin slots in the L2 DC- plane under the gate stars (corridor), traces added below
YSH, YSL = YQH, YQL                            # star rows (equal branch lengths, gates at y +- 1.23)

print("STEP transistors", flush=True)
# ------------------------------------------------------------------ transistors (real EPC2361 land pattern)
EPC_NETS = lambda g, s, d: {"1": g, "2": s, "4": s, "6": s, "3": d, "5": d, "7": d}
GATE = {}
for side, sgn, rot in (("L", -1, 180.0), ("R", 1, 0.0)):
    xq = sgn * XC
    qh = place(EPC_LIB, "EPC2361", "Q%d" % (1 if side == "L" else 2), "EPC2361", xq, YQH, rot,
               nets=EPC_NETS("GH_" + side, "SW", "DCP"), mpn="EPC2361")
    ql = place(EPC_LIB, "EPC2361", "Q%d" % (3 if side == "L" else 4), "EPC2361", xq, YQL, rot,
               nets=EPC_NETS("GL_" + side, "DCN", "SW"), mpn="EPC2361")
    for tag, fp in (("H", qh), ("L", ql)):
        g = [p for p in fp.Pads() if p.GetNumber() == "1"][0]
        k = [p for p in fp.Pads() if p.GetNumber() == "2"][0]
        GATE[tag + side] = (pcbnew.ToMM(g.GetPosition().x), pcbnew.ToMM(g.GetPosition().y))
        kp = k.GetPosition()
        # Kelvin point: end of the source pad 2 next to the gate pad
        ky = pcbnew.ToMM(kp.y) + (0.85 if GATE[tag + side][1] > pcbnew.ToMM(kp.y) else -0.85)
        GATE["K" + tag + side] = (pcbnew.ToMM(kp.x), ky)


def net_at(x, y):
    """net of the L1 power box containing (x, y)."""
    for n, nm, lay, x0, x1, y0, y1 in G["boxes"]:
        if n and lay in ("L1", "PAD") and x0 <= x <= x1 and y0 <= y <= y1:
            return NETMAP[n]
    return None


def tight_courtyard(fp, body_half, m=0.05):
    """replace the library courtyard of densely packed same-net power capacitors: body length (+ m) along the
    part, pad envelope (+ m) across it (the same-net end pads of neighbouring banks may touch). Built in
    footprint-local coordinates so that every instance equals the library copy."""
    for it in list(fp.GraphicalItems()):
        if it.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            fp.Remove(it)
    hy = max(pcbnew.ToMM(p.GetSize().y) for p in fp.Pads()) / 2 + m
    hx = body_half + m
    for (a, b), (c, d) in (((-hx, -hy), (hx, -hy)), ((hx, -hy), (hx, hy)), ((hx, hy), (-hx, hy)), ((-hx, hy), (-hx, -hy))):
        sh = pcbnew.FP_SHAPE(fp)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetLayer(pcbnew.F_CrtYd)
        sh.SetWidth(MM(0.05))
        sh.SetStart0(vec(a, b))
        sh.SetEnd0(vec(c, d))
        fp.Add(sh)
        sh.SetDrawCoord()


SAVED = set()


def place_power_cap(lib, name, ref, value, x, y, rot, mpn):
    fp = place(lib, name, ref, value, x, y, rot, mpn=mpn)
    tight_courtyard(fp, 1.6 if "1210" in name else 1.0)
    fp.SetFPID(pcbnew.LIB_ID("spb_fab", name + "_TightCrtYd"))
    PARTS[-1]["footprint"] = name + "_TightCrtYd"
    if name not in SAVED:
        SAVED.add(name)
        pcbnew.FootprintSave(os.path.join(OUT, "spb_fab.pretty"), fp)
    for pad in fp.Pads():
        n = net_at(pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y))
        if n:
            pad.SetNet(net(n))
    return fp


cid = 1
for side, sgn in (("L", -1), ("R", 1)):
    for i in range(6):
        place_power_cap(FP + "Capacitor_SMD.pretty", "C_0805_2012Metric", "C%d" % cid, "1uF 100V X7S",
                        sgn * XC + (i - 2.5) * P["cap_p"], (Y["capn"][0] + Y["capp"][1]) / 2, 90,
                        "TDK C2012X7S2A105K125AB")
        cid += 1
for g0 in (Y["p1"][1], Y["n1"][1], Y["p2"][1]):
    gc = g0 + P["gap"] / 2
    for s in (-1, 1):
        for xb in P["bank_x"]:
            place_power_cap(FP + "Capacitor_SMD.pretty", "C_1210_3225Metric", "C%d" % cid, "10uF 100V X7S",
                            s * xb, gc, 90, "Murata GRM32EC72A106KE05L")
            cid += 1

print("STEP gate stars", flush=True)
# ------------------------------------------------------------------ gate stars (L1) and Kelvin returns (L2)
# Star nodes on the symmetry line at the gate rows' centre (y = YSH, YSL): the two cells' gate pads lie at
# y = YS -+ 1.23 (package chirality), so both branches have the same length.
F, L2l, L3l, Bl = pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu
XB = XC - 5.2                                   # branch column, 0.7 mm inside the corridor edge (x = XC - 4.5)
RG_X = 3.0
KROW = {"H": YSH + 0.85, "L": YSL - 0.85}       # Kelvin collector rows on L2
rid = 1


def assign2(fp, n_lo, n_hi, axis):
    """give the pad with the lower x (axis 0) or y (axis 1) coordinate net n_lo, the other n_hi."""
    pads = sorted(fp.Pads(), key=lambda q: q.GetPosition()[axis])
    pads[0].SetNet(net(n_lo))
    pads[1].SetNet(net(n_hi))


def two(lib, name, ref, value, x, y, rot, n_lo, n_hi, mpn, bottom=False):
    fp = place(FP + lib, name, ref, value, x, y, rot, bottom, mpn=mpn)
    assign2(fp, n_lo, n_hi, 1 if rot in (90, 270) else 0)
    return fp


for tag, ys in (("H", YSH), ("L", YSL)):
    for side, sgn in (("L", -1), ("R", 1)):
        gx, gy = GATE[tag + side]
        kx, ky = GATE["K" + tag + side]
        n_star, n_gate = "G%s_STAR" % tag, "G%s_%s" % (tag, side)
        two("Resistor_SMD.pretty", "R_0402_1005Metric", "R%d" % rid, "0R5 1%% (gate %s%s)" % (tag, side),
            sgn * RG_X, ys, 0, n_gate if sgn < 0 else n_star, n_star if sgn < 0 else n_gate,
            "0.5R 0402 1% (Panasonic ERJ-2BQFR50X)")
        rid += 1
        seg(F, [(0, ys), (sgn * (RG_X - 0.48), ys)], 0.3, n_star)
        seg(F, [(sgn * (RG_X + 0.48), ys), (sgn * XB, ys), (sgn * XB, gy), (gx - sgn * 0.55, gy)], 0.3, n_gate)
        kn = "SW" if tag == "H" else "DCN"
        kvx = gx - sgn * 1.05                   # Kelvin via next to the source pad 2 (gate end), corridor side
        seg(F, [(kx, ky), (kvx, ky)], 0.3, kn)
        via(kvx, ky, kn, 0.45, 0.25)
        seg(L2l, [(kvx, ky), (sgn * XB, ky), (sgn * XB, KROW[tag]), (0, KROW[tag])], 0.3, kn)
        # narrow L2 keepout along the Kelvin trace (0.5 mm margin): the DC- return plane stays under the FETs
        pts = [(kvx, ky), (sgn * XB, ky), (sgn * XB, KROW[tag]), (0, KROW[tag])]
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            keepout(LAYER["L2"], min(xa, xb) - 0.5, max(xa, xb) + 0.5, min(ya, yb) - 0.5, max(ya, yb) + 0.5)
DY = 3.5                                        # driver and tab shifted down to make room for the on/off network
keepout(LAYER["L2"], -3.3, 3.3, 3.3, 12.9)      # corridor: no DC- pour around the Kelvin collectors
keepout(LAYER["L2"], -4.6, 4.6, 10.0, 12.9)
keepout(LAYER["L4"], -3.3, 3.3, 4.6, 15.0)      # corridor: no switch-node pour under the gate loops
keepout(LAYER["L4"], -4.6, 4.6, 10.0, 15.0)

# HS loop: star -> via -> L3 trunk; Kelvin collector -> via -> L4 return directly below the trunk
via(0.0, YSH, "GH_STAR")
via(0.0, KROW["H"], "SW", 0.45, 0.25)
GHV2 = (-1.5, 10.0)
seg(L3l, [(0, YSH), (-0.75, YSH + 0.75), (-0.75, 9.25), GHV2], 0.3, "GH_STAR")
via(GHV2[0], GHV2[1], "GH_STAR")
HSK2 = (-3.9, 11.0)
seg(Bl, [(0, KROW["H"]), (-0.75, KROW["H"] + 0.75), (-0.75, 10.6), (-1.15, 11.0), HSK2], 0.3, "SW")
via(HSK2[0], HSK2[1], "SW", 0.45, 0.25)
# gate pull-downs (10 k) at the stars, star node to the Kelvin source of the same switch: hold both paralleled gates
# off when the driver output side is unpowered (12 V off, DC link charged)
two("Resistor_SMD.pretty", "R_0402_1005Metric", "R41", "10k 1% (HS gate pull-down)", 1.0, YSH + 0.43, 90,
    "GH_STAR", "SW", "10k 0402 1%")
seg(F, [(1.0, YSH + 0.91), (0.0, KROW["H"])], 0.25, "SW")
two("Resistor_SMD.pretty", "R_0402_1005Metric", "R42", "10k 1% (LS gate pull-down)", 1.0, YSL - 0.45, 90,
    "DCN", "GL_STAR", "10k 0402 1%")
via(0.0, 7.9, "DCN", 0.45, 0.25)
seg(F, [(1.0, YSL - 0.93), (0.0, 7.9)], 0.25, "DCN")
seg(L2l, [(0.0, 7.9), (0.0, KROW["L"])], 0.3, "DCN")
# LS loop: L1 trunk to the star; Kelvin collector on L2 straight down the symmetry line
LSK2 = (3.9, 11.0)
seg(L2l, [(0, KROW["L"]), (0, 10.6), (0.4, 11.0), LSK2], 0.3, "DCN")
via(LSK2[0], LSK2[1], "DCN", 0.45, 0.25)

print("STEP driver", flush=True)
# ------------------------------------------------------------------ driver (top, corridor below the LS star)
YDR = 15.6 + DY
drv = lga13()
finish(drv, "U1", "2EDF7275K", 0.0, YDR, 0.0, False,
       {"1": "GNDI", "2": "INA", "3": "INB", "4": "GNDI", "5": "DIS", "6": None, "7": "VDDI",
        "8": "VEEB", "9": "OUTB", "10": "VDDB", "11": "VEEA", "12": "OUTA", "13": "VDDA"},
       "Infineon 2EDF7275KXUMA1", "2EDF7275K_PG-TFLGA-13-4")


def padxy(ref, num):
    fp = board.FindFootprintByReference(ref)
    q = [p for p in fp.Pads() if p.GetNumber() == str(num)][0]
    return pcbnew.ToMM(q.GetPosition().x), pcbnew.ToMM(q.GetPosition().y)


with open(os.path.join(OUT, "driver_pads.txt"), "w") as f:
    for k in range(1, 14):
        f.write("%d %.3f %.3f\n" % ((k,) + padxy("U1", k)))
# separate turn-on and turn-off paths per channel:
#   OUT --R_ON-------------+--> trunk -> star -> R_G,i (per transistor) -> gate
#   OUT <-|D|--R_OFF-------+        (diode conducts only when the gate is pulled down)
# per transistor: R_on,eff = 2 R_ON + R_G,i, R_off,eff = 2 (R_ON || (R_OFF + D)) + R_G,i
GATE_NET = {}
for ch, sg, out_pin, node in (("A", -1, 12, "GH_STAR"), ("B", 1, 9, "GL_STAR")):
    two("Resistor_SMD.pretty", "R_0603_1608Metric", "R%d" % rid, "0R75 1%% (R_ON,%s)" % ch, sg * 1.0, 12.2, 90,
        node, "OUT" + ch, "0.75R 0603 1% (Panasonic ERJ-3RQFR75V)")
    rid += 1
    two("Resistor_SMD.pretty", "R_0402_1005Metric", "R%d" % rid, "0R (R_OFF,%s)" % ch, sg * 2.7, 11.7, 90,
        node, "OFF" + ch, "0R 0402 jumper (set R_OFF here)")
    rid += 1
    d = place(FP + "Diode_SMD.pretty", "D_SOD-323F", "D%d" % (1 if ch == "A" else 2), "PMEG3020EJ",
              sg * 2.7, 14.25, 90, False, mpn="Nexperia PMEG3020EJ (30 V, 2 A, SOD323F)")
    if padxy(d.GetReference(), 1)[1] < 14.25:   # cathode (pad 1) toward the driver output
        d.SetOrientationDegrees(270.0)
        PARTS[-1]["rot"] = 270.0
    for q in d.Pads():
        q.SetNet(net("OUT" + ch if q.GetNumber() == "1" else "OFF" + ch))
    ox, oy = padxy("U1", out_pin)
    # node side: R_ON top pad and R_OFF top pad
    seg(F, [(sg * 1.0, 11.375), (sg * 1.0, 11.3), (sg * 2.7, 11.3), (sg * 2.7, 11.22)], 0.3, node)
    # R_OFF -> diode anode
    seg(F, [(sg * 2.7, 12.18), (sg * 2.7, 13.15)], 0.3, "OFF" + ch)
    # driver output: R_ON bottom pad and diode cathode
    seg(F, [(sg * 1.0, 13.025), (sg * 1.0, 15.9), (ox, oy)], 0.3, "OUT" + ch)
    seg(F, [(sg * 2.7, 15.35), (sg * 2.2, 15.9), (sg * 1.0, 15.9)], 0.3, "OUT" + ch)
seg(F, [GHV2, (-1.0, 10.7), (-1.0, 11.375)], 0.3, "GH_STAR")
seg(F, [(1.0, 11.375), (1.0, 10.3), (0, 10.3), (0, YSL)], 0.3, "GL_STAR")
# local decoupling, 1 uF per half rail per channel (>> 20 x Ciss of two EPC2361)
cid2 = 100
for ch, sg, top, bot, sref in (("A", -1, "VDDA", "VEEA", "SW"), ("B", 1, "VEEB", "VDDB", "DCN")):
    for yy, nn in ((13.45 + DY, top), (14.45 + DY, bot)):
        two("Capacitor_SMD.pretty", "C_0402_1005Metric", "C%d" % cid2, "1uF 16V X7R 0402", sg * 3.75, yy, 0,
            sref if sg < 0 else nn, nn if sg < 0 else sref, "Murata GRM155R71C105KA12")
        cid2 += 1
    seg(F, [padxy("U1", 13 if sg < 0 else 8), (sg * 3.27, 13.45 + DY)], 0.3, top)
    seg(F, [padxy("U1", 11 if sg < 0 else 10), (sg * 0.65, 14.45 + DY), (sg * 3.27, 14.45 + DY)], 0.3, bot)
    K2 = HSK2 if sg < 0 else LSK2
    seg(F, [K2, (sg * 4.4, 11.5), (sg * 4.4, 13.45 + DY), (sg * 4.23, 13.45 + DY)], 0.3, sref)
    seg(F, [(sg * 4.4, 13.45 + DY), (sg * 4.4, 14.45 + DY), (sg * 4.23, 14.45 + DY)], 0.3, sref)
    seg(F, [(sg * 4.4, 14.45 + DY), (sg * 4.4, 15.4 + DY), (sg * 4.3, 16.0 + DY)], 0.3, sref)
    via(sg * 4.3, 16.0 + DY, sref)
    seg(F, [(sg * 3.27, 13.45 + DY), (sg * 3.2, 12.75 + DY)], 0.3, top)
    via(sg * 3.2, 12.75 + DY, top)
    seg(F, [(sg * 3.27, 14.45 + DY), (sg * 3.6, 15.3 + DY)], 0.3, bot)
    via(sg * 3.6, 15.3 + DY, bot)
    # L3 supply columns to the gate-supply chain: outer = top-cap net, middle = source reference, inner = bottom
    seg(L3l, [(sg * 3.2, 12.75 + DY), (sg * 5.0, 12.75 + DY), (sg * 5.0, 24.0 + DY)], 0.3, top)
    seg(L3l, [(sg * 4.3, 16.0 + DY), (sg * 4.0, 16.3 + DY), (sg * 4.0, 24.0 + DY)], 0.3, sref)
    seg(L3l, [(sg * 3.6, 15.3 + DY), (sg * 3.0, 15.9 + DY), (sg * 3.0, 24.0 + DY)], 0.3, bot)
    vee_end = (sg * 3.0, 24.0 + DY) if ch == "A" else (sg * 5.0, 24.0 + DY)
    via(vee_end[0], vee_end[1], "VEEA" if ch == "A" else "VEEB")

# input side: RC filters, VDDI (SLDO on: SLDON -> GNDI, 3 k from 12 V, 22 nF), DISABLE
two("Capacitor_SMD.pretty", "C_0402_1005Metric", "C%d" % cid2, "100pF C0G 0402", -2.0, 18.75 + DY, 0, "GNDI", "INA",
    "Murata GRM1555C1H101JA01")
cid2 += 1
two("Capacitor_SMD.pretty", "C_0402_1005Metric", "C%d" % cid2, "100pF C0G 0402", -0.17, 19.85 + DY, 0, "INB", "GNDI",
    "Murata GRM1555C1H101JA01")
cid2 += 1
two("Capacitor_SMD.pretty", "C_0402_1005Metric", "C%d" % cid2, "22nF 25V X7R 0402", 2.2, 18.75 + DY, 0, "VDDI", "GNDI",
    "Murata GRM155R71E223KA61")
cid2 += 1
two("Resistor_SMD.pretty", "R_0402_1005Metric", "R%d" % rid, "47R 1% (INA)", -1.9, 21.3 + DY, 90, "INA", "PWM_H",
    "47R 0402 1%")
rid += 1
two("Resistor_SMD.pretty", "R_0402_1005Metric", "R%d" % rid, "47R 1% (INB)", -0.65, 21.3 + DY, 90, "INB", "PWM_L",
    "47R 0402 1%")
rid += 1
two("Resistor_SMD.pretty", "R_0402_1005Metric", "R%d" % rid, "3k 1% (RVDDI)", 1.9, 20.3 + DY, 90, "VDDI", "+12V",
    "3.0k 0402 1%")
rid += 1
seg(F, [padxy("U1", 2), (-1.3, 18.3 + DY), (-1.52, 18.75 + DY), (-1.52, 19.3 + DY), (-1.9, 19.9 + DY),
        (-1.9, 20.82 + DY)], 0.25, "INA")
seg(F, [padxy("U1", 3), (-0.65, 20.82 + DY)], 0.25, "INB")
seg(F, [padxy("U1", 5), (0.65, 18.4 + DY), (1.0, 18.9 + DY), (1.0, 22.6 + DY)], 0.25, "DIS")
seg(F, [padxy("U1", 7), (1.95, 18.2 + DY), (1.72, 18.75 + DY), (1.9, 19.82 + DY)], 0.25, "VDDI")

print("STEP gate supplies", flush=True)
# ------------------------------------------------------------------ gate supplies (tab, top)
# MGN1S1208MC (+8 V iso) -> TPS7A4901 adjustable LDO (6.29 V) -> TLV431 shunt sets the source node 1.24 V above VEE:
# TPS7A4901 (DGN, HVSSOP-8 PowerPAD): 1 OUT, 2 FB, 3 NC, 4 GND, 5 EN (tied to IN), 6 NR/SS (open), 7 DNC (open), 8 IN,
# 9 exposed pad (to GND); VOUT = 1.185 V (1 + 102k / 23.7k) = 6.29 V; stable with >= 2.2 uF ceramic.
# VDD - S = +5.05 V, VEE - S = -1.24 V.
YMC = 42.4 + DY                                       # module centre row
XMOD = 8.2
SUP = {"A": dict(sg=-1, iso="ISOA_P", vdd="VDDA", vee="VEEA", s="SW", adj="ADJA"),
       "B": dict(sg=1, iso="ISOB_P", vdd="VDDB", vee="VEEB", s="DCN", adj="ADJB")}
for ch, c in SUP.items():
    sg = c["sg"]
    m = mgn1()
    finish(m, "PS%d" % (1 if ch == "A" else 2), "MGN1S1208MC", sg * XMOD, YMC, 90.0, False,
           {"1": "GNDI", "2": "GNDI", "19": "+12V", "20": "+12V", "9": c["vee"], "10": c["vee"],
            "11": c["iso"], "12": c["iso"]}, "Murata MGN1S1208MC-R7", "Murata_MGN1_SMD")
    if padxy("PS%d" % (1 if ch == "A" else 2), 11)[1] > YMC:          # outputs must face the chain (up)
        m.SetOrientationDegrees(270.0)
        PARTS[-1]["rot"] = 270.0
    u = place(FP + "Package_SO.pretty", "HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm", "U%d" % (2 if ch == "A" else 3),
              "TPS7A4901 6.29 V", sg * (11.4 if ch == "A" else 11.0), 25.4 + DY, 180, False,
              {"1": c["vdd"], "2": c["adj"], "3": None, "4": c["vee"], "5": c["iso"], "6": None, "7": None,
               "8": c["iso"], "9": c["vee"]}, "TI TPS7A4901DGNR")
    u.SetFPID(pcbnew.LIB_ID("spb_fab", "HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm"))   # copy with the MSOP model
    if ch == "A":
        pcbnew.FootprintSave(os.path.join(OUT, "spb_fab.pretty"), u)
    if ch == "A":
        pos = dict(cin=(-15.6, 25.6), cout=(-7.0, 25.4), r1=(-14.4, 28.6), r2=(-14.4, 30.4), cs1=(-10.8, 28.8),
                   cs2=(-10.8, 31.0), tl=(-6.8, 29.8), rb=(-3.6, 26.4))
        pos = {k: (v[0], v[1] + DY) for k, v in pos.items()}
    else:
        pos = dict(cin=(6.6, 25.4), cout=(15.2, 25.6), r1=(14.4, 28.6), r2=(14.4, 30.4), cs1=(10.8, 28.8),
                   cs2=(10.8, 31.0), tl=(6.8, 29.8), rb=(3.6, 26.4))
        pos = {k: (v[0], v[1] + DY) for k, v in pos.items()}
    two("Capacitor_SMD.pretty", "C_0805_2012Metric", "C%d" % cid2, "4.7uF 25V X7R 0805", *pos["cin"], 90,
        c["iso"], c["vee"], "Murata GRM21BR71E475KA73")
    cid2 += 1
    two("Capacitor_SMD.pretty", "C_0805_2012Metric", "C%d" % cid2, "10uF 16V X7R 0805", *pos["cout"], 90,
        c["vdd"], c["vee"], "Murata GRM21BR71C106KE51")
    cid2 += 1
    two("Resistor_SMD.pretty", "R_0603_1608Metric", "R%d" % rid, "102k 1%", *pos["r1"], 0,
        c["vdd"] if sg < 0 else c["adj"], c["adj"] if sg < 0 else c["vdd"], "102k 0603 1%")
    rid += 1
    two("Resistor_SMD.pretty", "R_0603_1608Metric", "R%d" % rid, "23.7k 1%", *pos["r2"], 0,
        c["adj"] if sg < 0 else c["vee"], c["vee"] if sg < 0 else c["adj"], "23.7k 0603 1%")
    rid += 1
    two("Capacitor_SMD.pretty", "C_0805_2012Metric", "C%d" % cid2, "4.7uF 16V X7R 0805", *pos["cs1"], 0,
        c["vdd"] if sg < 0 else c["s"], c["s"] if sg < 0 else c["vdd"], "Murata GRM21BR71C475KA73")
    cid2 += 1
    two("Capacitor_SMD.pretty", "C_0805_2012Metric", "C%d" % cid2, "4.7uF 16V X7R 0805", *pos["cs2"], 0,
        c["s"] if sg < 0 else c["vee"], c["vee"] if sg < 0 else c["s"], "Murata GRM21BR71C475KA73")
    cid2 += 1
    place(FP + "Package_TO_SOT_SMD.pretty", "SOT-23", "U%d" % (4 if ch == "A" else 5), "TLV431A (1.24 V)",
          *pos["tl"], 0, False, {"1": c["s"], "2": c["s"], "3": c["vee"]}, "TI TLV431AIDBZR")
    two("Resistor_SMD.pretty", "R_0603_1608Metric", "R%d" % rid, "2.2k 1% (shunt bias)", *pos["rb"], 90,
        c["vdd"], c["s"], "2.2k 0603 1%")
    rid += 1
    two("Capacitor_SMD.pretty", "C_0805_2012Metric", "C%d" % cid2, "4.7uF 25V X7R 0805 (12 V in)", sg * XMOD, 51.3 + DY, 0,
        "+12V" if sg < 0 else "GNDI", "GNDI" if sg < 0 else "+12V", "Murata GRM21BR71E475KA73")
    cid2 += 1
    # domain pours: VEE on L2 under each chain and the module output half
    rect_zone(L2l, c["vee"], min(sg * 2.4, sg * 20.3), max(sg * 2.4, sg * 20.3), 23.6 + DY, 39.2 + DY, 1)

print("STEP connectors", flush=True)
# ------------------------------------------------------------------ connectors, terminals, sensing
TB = FP + "TerminalBlock_Wuerth.pretty"
for ref, nm, x, y, n, lab in (("J1", "Wuerth_REDCUBE-THR_WP-THRBU_74650174_THR", -6.0, YT + 4.6, "DCP", "DC+"),
                              ("J2", "Wuerth_REDCUBE-THR_WP-THRBU_74650174_THR", 6.0, YT + 4.6, "DCN", "DC-"),
                              ("J3", "Wuerth_REDCUBE-THR_WP-THRBU_74650174_THR", -10.5, 17.6, "SW", "AC"),
                              ("J4", "Wuerth_REDCUBE-THR_WP-THRBU_74650174_THR", 10.5, 17.6, "SW", "AC")):
    fp = place(TB, nm, ref, lab, x, y, 0, True, mpn="Wuerth 74650174 (REDCUBE THR, M4)")
    for pad in fp.Pads():
        pad.SetNet(net(n))
# AC terminals sit directly below each cell's switch node: SW copper on all layers there
for sg in (-1, 1):
    xa, xb = (-16.3, -5.4) if sg < 0 else (5.4, 15.3)
    for lay in ("L1", "L2", "L3"):
        rect_zone(LAYER[lay], "SW", xa, xb, 12.4, 23.0, 1)
    rect_zone(LAYER["L4"], "SW", min(sg * 5.4, sg * 16.3) if sg < 0 else 5.4, 15.3 if sg > 0 else -5.4, 4.6, 23.0, 1)
# primary-side pours (GNDI): driver input area L1, centre channel L4, bottom strip L1/L2/L4
rect_zone(Bl, "GNDI", -1.9, 1.9, 16.0 + DY, 23.2 + DY, 1)
rect_zone(Bl, "GNDI", -1.2, 1.2, 23.0 + DY, 46.0 + DY, 1)
STITCH = []
for x, y in ((-4.4, 53.9), (5.5, 55.6), (-11.6, 50.1), (10.4, 55.1), (-17.0, 51.1), (17.0, 51.1), (4.2, 53.7)):
    STITCH.append(via(x, y + DY, "GNDI"))
for lay, y0 in ((Bl, 45.6 + DY), (L2l, 45.6 + DY), (F, 50.0 + DY)):
    rect_zone(lay, "GNDI", -20.3, 20.3, y0, Y1 - 0.5, 1)
# lab header (primary side) 2 x 3: 1 +12V, 2 GND, 3 PWM_H, 4 GND, 5 PWM_L, 6 DISABLE
place(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_2x03_P2.54mm_Vertical", "J5",
      "1:+12V 2:GND 3:PWM_H 4:GND 5:PWM_L 6:DIS", -2.54, Y1 - 2.96, 90, False,
      {"1": "+12V", "2": "GNDI", "3": "PWM_H", "4": "GNDI", "5": "PWM_L", "6": "DIS"}, "2.54 mm header 2x3")
place(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical", "J6",
      "1:NTC 2:DC- (LS domain!)", 3.0, 30.0 + DY, 0, False, {"1": "NTC", "2": "DCN"}, "2.54 mm header 1x2")

# ------------------------------------------------------------------ measurement landings (double-pulse test)
# All landings are probe pads (tip + spring ground at 2.5 / 5.0 mm), no circuitry in the cells. Per side (sg):
#   D: Vds of the low-side FET, tip on the switch-node copper next to the package, ground on its source copper
#   K: v_KS = Kelvin sense vs power-source copper (source-inductance di/dt sensing of each low-side FET)
#   G: Vgs of the low-side FET, gate sense and Kelvin sense routed as a pair on L3
#   H: Vgs of the high-side FET (isolated probe), pair on L3
PROBES = []
TPN = [0]


def landing(two_sig, x, y, rot, sig_net, gnd_net, label):
    fp, nm = probe(two_sig)
    TPN[0] += 1
    ref = "TP%d" % TPN[0]
    finish(fp, ref, label, x, y, rot, False, {"1": sig_net, "2": gnd_net}, "probe landing (no part)", nm)
    PROBES.append((ref, label, x, y))
    return fp


for side, sg in (("L", -1), ("R", 1)):
    q_ls, q_hs = ("Q3", "Q1") if side == "L" else ("Q4", "Q2")
    # source copper of the low-side cell extended to x = 16 (landing area of D and K grounds)
    rect_zone(F, "DCN", min(sg * 14.0, sg * 16.0), max(sg * 14.0, sg * 16.0), 9.5, 11.95, 2)
    landing(True, sg * 13.4, 10.5, 0, "SW", "DCN", "D: Vds %s" % q_ls)
    landing(True, sg * 15.5, 10.5, 0, "DCN", "DCN", "K: vKS %s (tip K)" % q_ls)
    landing(False, sg * 17.3, 6.0, 0, "GL_" + side, "DCN", "G: Vgs %s" % q_ls)
    landing(False, sg * 19.6, 7.2, 180, "GH_" + side, "SW", "H: Vgs %s (iso)" % q_hs)
    # sense pairs on L3 (no current flows in them)
    for tag in ("H", "L"):
        gx, gy = GATE[tag + side]
        kx, ky = GATE["K" + tag + side]
        kvx = gx - sg * 1.05
        gnet = "G%s_%s" % (tag, side)
        knet = "SW" if tag == "H" else "DCN"
        lane_g, lane_k = (5.75, 5.25) if tag == "H" else (8.25, 8.75)
        via(sg * 5.4, gy, gnet, 0.45, 0.25)
        if tag == "H":
            seg(L3l, [(sg * 5.4, gy), (sg * 5.4, lane_g), (sg * 18.6, lane_g), (sg * 18.6, 6.6)], 0.2, gnet)
            via(sg * 18.6, 6.6, gnet, 0.45, 0.25)
            seg(F, [(sg * 18.6, 6.6), (sg * 19.6, 7.2)], 0.25, gnet)
            seg(L3l, [(kvx, ky), (kvx, lane_k), (sg * 18.4, lane_k), (sg * 18.4, 4.0)], 0.2, knet)
            via(sg * 18.4, 4.0, knet, 0.45, 0.25)
            seg(F, [(sg * 19.6, 2.2), (sg * 18.4, 4.0), (sg * 19.6, 4.7)], 0.25, knet)
        else:
            seg(L3l, [(sg * 5.4, gy), (sg * 5.4, lane_g), (sg * 16.2, lane_g), (sg * 16.2, 7.2)], 0.2, gnet)
            via(sg * 16.2, 7.2, gnet, 0.45, 0.25)
            seg(F, [(sg * 16.2, 7.2), (sg * 17.3, 6.0)], 0.25, gnet)
            seg(L3l, [(kvx, ky), (kvx, lane_k), (sg * 18.6, lane_k)], 0.2, knet)
            via(sg * 18.6, lane_k, knet, 0.45, 0.25)
            seg(F, [(sg * 18.6, lane_k), (sg * 17.3, 8.5), (sg * 15.5, 8.0), (sg * 15.5, 5.5)], 0.25, knet)
            seg(F, [(sg * 18.6, lane_k), (sg * 18.2, 10.2), (sg * 17.3, 11.0)], 0.25, knet)
    text("D K G H", sg * 16.6, 12.6, 0.8)

# NTC near the right high-side FET, DC- side via the L2 plane, read out on J6 (LS domain)
two("Resistor_SMD.pretty", "R_0402_1005Metric", "RT1", "NTC 10k B3380", 15.4, 2.4, 90, "NTC", "DCN",
    "Murata NCP15XH103F03RC")
seg(F, [(15.4, 2.88), (15.4, 3.7)], 0.3, "DCN")
via(15.4, 3.7, "DCN")
seg(F, [(15.4, 1.92), (16.9, 1.92)], 0.25, "NTC")
via(16.9, 1.92, "NTC")
seg(L2l, [(16.9, 1.92), (16.9, 22.9 + DY)], 0.25, "NTC")
via(16.9, 22.9 + DY, "NTC")

# ------------------------------------------------------------------ bring-up test landings and LEDs
for sg, ch in ((-1, "A"), (1, "B")):
    c = SUP[ch]
    landing(False, sg * 19.6, 24.5 + DY, 0, c["iso"], c["vee"], "ISO %s" % ch)
    landing(False, sg * 19.6, 31.5 + DY, 0, c["vdd"], c["vee"], "VDD %s" % ch)
    landing(False, sg * 19.6, 38.5 + DY, 0, c["s"], c["vee"], "S %s" % ch)
    # LEDs: isolated module output and regulator output present
    two("LED_SMD.pretty", "LED_0603_1608Metric", "D%d" % (3 if ch == "A" else 5), "green 0603 (ISO %s)" % ch,
        sg * 17.6, 25.0 + DY, 90, "LEDK_ISO" + ch, "LEDA_ISO" + ch, "Wurth 150060GS75000")
    two("Resistor_SMD.pretty", "R_0603_1608Metric", "R%d" % (30 if ch == "A" else 32), "2.7k (LED)", sg * 17.6,
        28.2 + DY, 90, "LEDA_ISO" + ch, c["iso"], "2.7k 0603 1%")
    two("LED_SMD.pretty", "LED_0603_1608Metric", "D%d" % (4 if ch == "A" else 6), "green 0603 (VDD %s)" % ch,
        sg * 17.6, 31.6 + DY, 90, "LEDK_VDD" + ch, "LEDA_VDD" + ch, "Wurth 150060GS75000")
    two("Resistor_SMD.pretty", "R_0603_1608Metric", "R%d" % (31 if ch == "A" else 33), "1.8k (LED)", sg * 17.6,
        34.8 + DY, 90, "LEDA_VDD" + ch, c["vdd"], "1.8k 0603 1%")
# LED cathodes: the two() helper orders the nets by pad position; fix pad roles by number (LED pad 1 = cathode)
for ref, ch, kind in (("D3", "A", "ISO"), ("D4", "A", "VDD"), ("D5", "B", "ISO"), ("D6", "B", "VDD")):
    fp = board.FindFootprintByReference(ref)
    for q in fp.Pads():
        q.SetNet(net(SUP[ch]["vee"] if q.GetNumber() == "1" else "LEDA_%s%s" % (kind, ch)))
# primary: 12 V landing, 12 V LED, PWM pull-downs, fan connector
landing(False, -13.0, 54.5 + DY - 3.5, 0, "+12V", "GNDI", "12V")
two("LED_SMD.pretty", "LED_0603_1608Metric", "D7", "green 0603 (12 V)", -10.0, Y1 - 1.4, 0, "GNDI", "LEDA_12V",
    "Wurth 150060GS75000")
two("Resistor_SMD.pretty", "R_0603_1608Metric", "R34", "4.7k (LED)", -6.6, Y1 - 1.4, 0, "LEDA_12V", "+12V",
    "4.7k 0603 1%")
fp = board.FindFootprintByReference("D7")
for q in fp.Pads():
    q.SetNet(net("GNDI" if q.GetNumber() == "1" else "LEDA_12V"))
two("Resistor_SMD.pretty", "R_0402_1005Metric", "R35", "10k (PWM_H pull-down)", 5.4, Y1 - 4.0, 90, "PWM_H", "GNDI",
    "10k 0402 1%")
two("Resistor_SMD.pretty", "R_0402_1005Metric", "R36", "10k (PWM_L pull-down)", 6.6, Y1 - 4.0, 90, "PWM_L", "GNDI",
    "10k 0402 1%")
place(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical", "J7", "FAN 12V: 1 +12V, 2 GND",
      13.0, Y1 - 5.4, 0, False, {"1": "+12V", "2": "GNDI"}, "2.54 mm header 1x2 (fan)")
# DC link: landing, HV-present LED (0.5 mA) and bleeder (2 x 47 k)
landing(False, 13.8, -15.0, 180, "DCP", "DCN", "DC link")
two("Resistor_SMD.pretty", "R_1206_3216Metric", "R37", "68k 1206 (HV LED)", 16.1, -16.5, 90, "HVA", "DCP",
    "68k 1206 1% 200 V")
two("Resistor_SMD.pretty", "R_1206_3216Metric", "R38", "68k 1206 (HV LED)", 18.6, -16.5, 90, "HVB", "HVA",
    "68k 1206 1% 200 V")
two("LED_SMD.pretty", "LED_0603_1608Metric", "D8", "red 0603 (DC link present)", 18.4, -12.6, 0, "DCN", "HVB",
    "Wurth 150060RS75000")
fp = board.FindFootprintByReference("D8")
for q in fp.Pads():
    q.SetNet(net("DCN" if q.GetNumber() == "1" else "HVB"))
two("Resistor_SMD.pretty", "R_1206_3216Metric", "R39", "100k 1206 (bleeder)", 19.2, -8.5, 90, "DCN", "DCP",
    "100k 1206 1% 200 V")

# ------------------------------------------------------------------ mounting: board corners + heatsink holes
for k, (hx, hy) in enumerate(((-(XO - 2.4), Y1 - 2.4), ((XO - 2.4), Y1 - 2.4), (-(XO - 2.4), Y0 + 2.4),
                              ((XO - 2.4), Y0 + 2.4))):
    place(FP + "MountingHole.pretty", "MountingHole_2.7mm_M2.5", "H%d" % (k + 1), "M2.5 insulated", hx, hy)
for k, (hx, hy) in enumerate(((-19.2, -1.6), (19.2, -1.6), (-19.2, 14.8), (19.2, 14.8))):
    place(FP + "MountingHole.pretty", "MountingHole_2.7mm_M2.5", "H%d" % (k + 5), "M2.5 heatsink", hx, hy)
hs = heatsink_fp()
finish(hs, "HS1", "Fischer LAM 4 K 50 12 + spreader", 0.0, 6.05, 0, False, None,
       "Fischer LAM 4 K 50 12; Al spreader 42x14x3 mm (machined); insulating gap pad 1 mm", "HS_LAM4K5012_assembly")
hs.SetAttributes(hs.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY)

text("SPB leg Rev A", 0, Y1 - 0.8, 0.8)
text("SPB leg building block, 2 x EPC2361 per switch, Rev A, KTH", 0, Y1 + 1.5, 1.0, pcbnew.F_Fab)
text("DC+", -6.0, YT + 0.9, 0.8)
text("DC-", 6.0, YT + 0.9, 0.8)
text("PRIMARY", 0, 44.9 + DY, 0.8)
text("HV", 18.4, -11.0, 0.8)
text("ISO VDD S", -17.6, 22.0 + DY, 0.8)
text("ISO VDD S", 17.6, 22.0 + DY, 0.8)

print("STEP route aux nets", flush=True)
# ------------------------------------------------------------------ auxiliary routing (domain-restricted)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fab_router  # noqa: E402

LAYS = [F, L2l, L3l, Bl]
R = fab_router.Router(board, (-XO, Y0, XO, Y1), LAYS, clearance=0.15, edge=0.7)
YC1 = 39.2 + DY


def dom(sg):
    xa, xb = (-20.4, -2.4) if sg < 0 else (2.4, 20.4)
    xe = (-20.4, -16.3) if sg < 0 else (16.3, 20.4)
    return [(0, xa, xb, 23.2 + DY, YC1), (2, xa, xb, 23.2 + DY, 34.7 + DY), (0, xe[0], xe[1], YC1, 44.8 + DY),
            (2, min(sg * 2.6, sg * 5.3), max(sg * 2.6, sg * 5.3), 12.4 + DY, 24.2 + DY)]


PRI = [(0, -2.6, 2.6, 17.0 + DY, 23.2 + DY), (0, -20.4, 20.4, 45.6 + DY, Y1), (1, -1.2, 1.2, 17.0 + DY, 45.6 + DY),
       (2, -1.2, 1.2, 17.0 + DY, 45.6 + DY), (1, -20.4, 20.4, 45.6 + DY, Y1), (2, -20.4, 20.4, 45.6 + DY, Y1),
       (3, -1.9, 1.9, 16.0 + DY, 23.2 + DY), (3, -1.2, 1.2, 23.0 + DY, 46.0 + DY), (3, -20.4, 20.4, 45.6 + DY, Y1)]
fails = 0
for ch, c in SUP.items():
    sg = c["sg"]
    D = dom(sg)
    if ch == "B":
        D = D + [(0, 16.3, 17.5, 23.0 + DY, 24.0 + DY)]
    for n, w in ((c["adj"], 0.2), (c["vee"], 0.3), (c["vdd"], 0.3), (c["s"], 0.3), (c["iso"], 0.3),
                 ("LEDA_ISO" + ch, 0.25), ("LEDA_VDD" + ch, 0.25)):
        regions = D + ([(1, -20.4 if sg < 0 else 2.4, -2.4 if sg < 0 else 20.4, 23.6 + DY, YC1)] if n == c["vee"] else [])
        fails += R.route_net(n, regions, width=w)
fails += R.route_net("NTC", dom(1) + [(0, 16.3, 17.5, 23.0 + DY, 24.0 + DY)], width=0.25)
for n, w in (("GNDI", 0.3), ("+12V", 0.4), ("PWM_H", 0.25), ("PWM_L", 0.25), ("DIS", 0.25), ("LEDA_12V", 0.25)):
    fails += R.route_net(n, PRI, width=w)
# DC-link indicator and bleeder: own router with 0.6 mm clearance (exposed pads at up to 100 V, IPC-2221 B2)
RHV = fab_router.Router(board, (-XO, Y0, XO, Y1), LAYS, clearance=0.6, edge=0.7)
HVR = [(0, 11.4, 20.4, Y0 + 0.5, -4.6)]
for n in ("HVA", "HVB", "DCN", "DCP"):
    fails += RHV.route_net(n, HVR, width=0.3, vias_ok=False)
print("route failures:", fails, flush=True)

print("STEP prune power vias", flush=True)
# ------------------------------------------------------------------ remove power vias that violate clearance
CLV = 0.16


def _seg_d(px, py, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    ll = vx * vx + vy * vy
    t = 0 if ll == 0 else max(0, min(1, ((px - a[0]) * vx + (py - a[1]) * vy) / ll))
    return math.hypot(px - a[0] - t * vx, py - a[1] - t * vy)


others = []
for fp in board.GetFootprints():
    for q in fp.Pads():
        bb = q.GetBoundingBox()
        others.append(("r", q.GetNetname(), (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                                             pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))))
pv = set(id(v) for v in POWER_VIAS)
for t in board.GetTracks():
    if id(t) in pv:
        continue
    if t.GetClass() == "PCB_VIA":
        others.append(("c", t.GetNetname(), (pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y),
                                             pcbnew.ToMM(t.GetWidth()) / 2)))
    else:
        others.append(("s", t.GetNetname(), (pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y),
                                             pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y),
                                             pcbnew.ToMM(t.GetWidth()) / 2)))
removed = 0
for v in POWER_VIAS:
    x, y, r, n = pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y), pcbnew.ToMM(v.GetWidth()) / 2, v.GetNetname()
    bad = False
    for k, nn, g in others:
        if nn == n:
            continue
        if k == "r":
            d = math.hypot(max(g[0] - x, 0, x - g[2]), max(g[1] - y, 0, y - g[3]))
        elif k == "c":
            d = math.hypot(x - g[0], y - g[1]) - g[2]
        else:
            d = _seg_d(x, y, (g[0], g[1]), (g[2], g[3])) - g[4]
        if d - r < CLV + 0.12:                      # + hole-clearance margin
            bad = True
            break
    if bad:
        board.Remove(v)
        removed += 1
print("power vias removed:", removed, "of", len(POWER_VIAS), flush=True)

print("STEP save, fill, DRC", flush=True)
# ------------------------------------------------------------------ save, fill, DRC
# move the design into positive page coordinates (fabrication outputs, plots): origin -> (OX, OY)
OX, OY = 100.0, 100.0
mv = vec(OX, OY)
for it in list(board.GetDrawings()) + list(board.GetTracks()) + list(board.GetFootprints()) + list(board.Zones()):
    it.Move(mv)
ds.SetAuxOrigin(vec(OX - XO, OY + Y1))
path = os.path.join(OUT, NAME + ".kicad_pcb")
pcbnew.SaveBoard(path, board)
import json  # noqa: E402

pro = os.path.join(OUT, NAME + ".kicad_pro")
json.dump({"board": {"design_settings": {"rule_severities": {
    "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore", "silk_over_copper": "warning",
    "silk_overlap": "warning", "silk_edge_clearance": "warning", "text_height": "warning",
    "text_thickness": "warning"}}},
    "meta": {"filename": NAME + ".kicad_pro", "version": 1}}, open(pro, "w"), indent=1)
json.dump(PARTS, open(os.path.join(OUT, "parts.json"), "w"), indent=1)
board2 = pcbnew.LoadBoard(path)
try:
    sev = board2.GetDesignSettings().m_DRCSeverities
    sev[pcbnew.DRCE_LIB_FOOTPRINT_ISSUES] = pcbnew.RPT_SEVERITY_IGNORE
    sev[pcbnew.DRCE_LIB_FOOTPRINT_MISMATCH] = pcbnew.RPT_SEVERITY_IGNORE
except Exception as e:  # noqa: BLE001
    print("severity override not available:", e)
board2.BuildConnectivity()
print("filling", flush=True)
pcbnew.ZONE_FILLER(board2).Fill(board2.Zones())
print("filled", flush=True)
pcbnew.SaveBoard(path, board2)
rep = os.path.join(OUT, "drc_report.txt")
print("drc", flush=True)
pcbnew.WriteDRCReport(board2, rep, pcbnew.EDA_UNITS_MILLIMETRES, True)
print("saved", path, "footprints", len(board.GetFootprints()), "nets", len(NETS),
      "outline %.1f x %.1f mm" % (2 * XO, Y1 - Y0))

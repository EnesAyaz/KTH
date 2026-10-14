"""
Rev B layout of the SPB leg: 4 x EPC2361 per switch on one board = two Rev A building blocks side by side (block 1 at
x = -BX, block 2 at x = +BX), each with its centre 2EDF7275K driving its two cells through the star networks.
Changes against Rev A (make_kicad_bb_fab.py):
  - PMK UFCS-R001 coaxial shunt (1 mOhm, 120 pH, 50 A continuous) in the low-side source path of every cell; the
    low-side sources of a block (net LSSb) reach DC- only through the shunts; shunts stay fitted for the load test
  - two external isolated gate supplies (HS, LS); each input splits into one branch per driver: WE-CNSW common-mode
    choke -> 5.1 V Zener VDD-S and bias resistor S-VEE (Karakaya, METU 2020, Fig. 4.1); V_GS,off = -(V_ISO - 5.1 V)
  - U.FL connectors on the bottom side under every cell: V_GS of both FETs, V_DS of the low-side FET, each with a
    series-resistor footprint (0 R into 1 MOhm, 953 R into 50 Ohm = 20:1)
  - TMCS1123A1A Hall sensor in series with each cell's AC terminal (I1..I4, summed by the controller)
  - one control connector to the C2000 with WE-CNSW chokes (12 V, 5 V, PWM_H/L, DIS, I1..I4, OCn)
  - bank MLCCs also between the blocks; fan heatsink rotated (tube along x) so that it clears the 27 mm shunts
  - ONE leg, not two blocks on a board (2026-10-13): one DC+ / DC- terminal pair at the centre feeding a laminated
    terminal row (L1/L3 DC+, L2/L4 DC-) over the full width, one continuous bank, the AC of all four cells joined
    and taken out at ONE M6 bolt pad (Cu bar bolted on, LEM HO 250-S on the bar); two drivers, one star per pair

    set BOARD=dpt  (or load);  "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\make_kicad_bb_revb.py

Writes hardware/spb-bb-revb-<BOARD>/spb-bb-revb-<BOARD>.kicad_pcb (+ .kicad_pro, parts.json, fp-lib-table), runs
zone fill and DRC. 3D models: scripts/make_3d_models_revb.py -> hardware/spb-bb-revb-<BOARD>/3d.
Coordinates: mm, x across the board, y down; block-local x (x_r) is relative to the block centre.
"""
import json
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bb_geometry as geo  # noqa: E402
import fab_router  # noqa: E402

# Two final boards (2026-10-14), BOARD = dpt | load:
#   dpt  : double-pulse board, PMK UFCS shunt per cell with the short IN land (blade 1.45 mm from the source), NO
#          heatsink (pulsed test) -> hardware/spb-bb-revb-dpt
#   load : back-to-back load-test board, no shunt, LS source via-in-pad (blind L1-L2), LAM 4 heatsink
#          -> hardware/spb-bb-revb-load
# SHUNT_VARIANT (vip | compact | notch | noshunt | noshunt_rot0) is kept for the shunt-path study boards in
# hardware/variants/spb-bb-revb-<variant>.
BOARD = os.environ.get("BOARD", "dpt")
VARIANT = os.environ.get("SHUNT_VARIANT", "")
if VARIANT:
    NAME = "spb-bb-revb"
    OUT = os.path.join(ROOT, "hardware", "variants", "spb-bb-revb-" + VARIANT)
    NOSHUNT = VARIANT in ("noshunt", "noshunt_rot0")
    SHORT_IN = VARIANT == "notch"
    HEATSINK = True
else:
    assert BOARD in ("dpt", "load"), BOARD
    NAME = "spb-bb-revb-" + BOARD
    OUT = os.path.join(ROOT, "hardware", NAME)
    NOSHUNT = BOARD == "load"
    SHORT_IN = BOARD == "dpt"
    HEATSINK = BOARD == "load"
ROT0 = VARIANT.endswith("rot0")            # symmetry study: left FETs NOT rotated (gate routing of the left cells omitted)
os.makedirs(OUT, exist_ok=True)
FP = KI + "/footprints/"
EPC_LIB = os.path.join(ROOT, "hardware", "epc2361-cell", "epc2361-cell.pretty")
MM = pcbnew.FromMM

# ------------------------------------------------------------------ geometry (block-local, as Rev A)
FAB = dict(xc=9.5, x_edge=16.0, bank_x=(5.75, 8.75, 11.75, 14.75), cap_p=1.6)
# bank strips for TWO rows of 2220 MLCCs (TDK C5750X7S2A226M280KB, pads +-2.55 mm, 1.8 mm tall): row A on the
# P1/N1 boundary (gap centre -11.7), row B on the P2/N2 boundary (gap centre -4.5) just above the bypass row
ROWS_2220 = dict(p1=(-16.0, -12.0), n1=(-11.4, -8.2), p2=(-8.0, -4.8), n2=(-4.2, 0.9),
                 p1_via=-12.65, n1_via=-10.75, p2_via=-5.5, l2=(-11.3, 11.9))
G = geo.build(FAB, ROWS_2220)
P, Y = G["params"], G["rows"]
XE, XC = P["x_edge"], P["xc"]
EDGE, TZ = 1.0, 10.0
YT = -13.4 - TZ                              # DC terminal zone top (fixed: terminals at y = -18.8)
BANK = ("C_2220_5750Metric", "22uF 100V X7S 2220", "TDK C5750X7S2A226M280KB")
BANK_ROWS = {"A": [15.0, 21.0, 27.0, 33.0], "B": [3.0, 9.0, 15.0, 21.0, 27.0, 33.0]}   # |x|, both signs
YQH = sum(Y["qhd"]) / 2 + 1.0
YQL = sum(Y["qld"]) / 2 + 1.0
DY = 3.5
YDR = 15.6 + DY                              # driver centre
BX = 23.75                                   # block centres at x = -+BX
XS_OFF = 12.4                                # shunt centre |x_r| (pads 4.9 .. 19.9)
XO = BX + 19.9 + EDGE + 0.1                  # board half width
Y0, Y1 = YT - EDGE, 55.6
YSH, YSL = YQH, YQL
YS = 15.25                                   # shunt centre (IN pad 12.0..15.0, SHLD 15.5..18.5)
YBUS = 39.3                                  # AC bus (all layers) from here to the bottom
YJ = 49.4                                    # AC output terminals

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(1.6))
ds.m_MinClearance = MM(0.15)
ds.m_TrackMinWidth = MM(0.15)
ds.m_ViasMinSize = MM(0.45)
ds.m_MinThroughDrill = MM(0.25)
ds.m_BlindBuriedViaAllowed = True                  # only the noshunt study variant uses blind vias
ncl = ds.m_NetSettings.m_DefaultNetClass
ncl.SetClearance(MM(0.15))
ncl.SetTrackWidth(MM(0.25))
ncl.SetViaDiameter(MM(0.6))
ncl.SetViaDrill(MM(0.3))
F, L2l, L3l, Bl = pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu
LAYER = {"L1": F, "L2": L2l, "L3": L3l, "L4": Bl}

# ------------------------------------------------------------------ block context: x offset and net suffix
OFFX = [0.0]
BI = [0]
SHARED = {"DCP", "DCN", "SW", "NTC", "HVA", "HVB"}


def bn(name):
    """block net: shared nets keep their name, all others get the block number."""
    return name if (name in SHARED or BI[0] == 0) else "%s%d" % (name, BI[0])


NETS = {}


def net(name):
    if name not in NETS:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        NETS[name] = n
    return NETS[name]


def vec(x, y):
    """board coordinates from block-local x (OFFX added)."""
    return pcbnew.VECTOR2I(MM(x + OFFX[0]), MM(y))


def vloc(x, y):
    """footprint-local coordinates (no offset)."""
    return pcbnew.VECTOR2I(MM(x), MM(y))


def rx(v):
    return pcbnew.ToMM(v) - OFFX[0]


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
        ol.Append(MM(x + OFFX[0]), MM(y))
    board.Add(z)
    return z


def rect_zone(layer, n, x0, x1, y0, y1, prio=0, clearance=0.2):
    return zone(layer, n, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], prio, clearance)


def keepout(layer, x0, x1, y0, y1):
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
        ol.Append(MM(x + OFFX[0]), MM(y))
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
CNT = {}


def ref(prefix):
    CNT[prefix] = CNT.get(prefix, 0) + 1
    return "%s%d" % (prefix, CNT[prefix])


FPNICK = [("R_", "Resistor_SMD"), ("C_", "Capacitor_SMD"), ("D_SOD", "Diode_SMD"), ("SOT-23", "Package_TO_SOT_SMD"),
          ("PinHeader", "Connector_PinHeader_2.54mm"), ("Wuerth", "TerminalBlock_Wuerth"), ("MountingHole", "MountingHole"),
          ("EPC2361", "epc2361-cell"), ("2EDF", "spb_fab"), ("LED_", "LED_SMD"), ("HS_", "spb_fab"),
          ("PMK_UFCS", "spb_fab"), ("TI_DVG", "spb_fab"), ("U.FL", "Connector_Coaxial"), ("L_CommonMode", "Inductor_SMD")]


# parts whose KiCad library model is missing or wrong (scripts/make_3d_models_revb.py -> hardware/spb-bb-revb-<BOARD>/3d)
LOCAL_MODEL = {"C_2220_5750Metric": "C_2220_5750Metric_TDK.wrl",
               "L_CommonMode_Wurth_WE-CNSW-1206": "L_CommonMode_Wurth_WE-CNSW-1206.wrl",
               "AC_BOLT_M6": "AC_BOLT_M6.wrl"}


def set_model(fp, local=None):
    """library parts keep their model (KiCad 7 resolves the library's own ${KICAD6_3DMODEL_DIR}); a part with a
    project model gets it instead and moves to the project library spb_fab (same pads, so no library mismatch)."""
    if not local:
        return
    fp.Models().clear()                          # the SWIG list holds copies: rebuild it
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/3d/" + local
    fp.Models().push_back(m)
    name = fp.GetFPID().GetLibItemName().wx_str()
    fp.SetFPID(pcbnew.LIB_ID("spb_fab", name))
    if name not in SAVED and not name.startswith(("C_2220", "AC_BOLT")):   # those two are saved by their builders
        SAVED.add(name)
        cp = pcbnew.FOOTPRINT(fp)
        cp.SetReference("REF**")
        pcbnew.FootprintSave(_lib, cp)


def finish(fp, rf, value, x, y, rot, bottom, nets, mpn, fpname):
    for pre, nick in FPNICK:
        if fpname.startswith(pre):
            fp.SetFPID(pcbnew.LIB_ID(nick, fpname))
            break
    set_model(fp, LOCAL_MODEL.get(fpname))       # before placement: the library copy is saved at the origin
    fp.SetReference(rf)
    fp.SetValue(value)
    board.Add(fp)
    fp.SetPosition(vec(x, y))
    fp.SetOrientationDegrees(rot)
    if bottom:
        fp.Flip(fp.GetPosition(), False)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    if nets:
        for pad in fp.Pads():
            k = pad.GetNumber()
            if k in nets and nets[k]:
                pad.SetNet(net(nets[k]))
    PARTS.append(dict(ref=rf, value=value, footprint=fpname, mpn=mpn, x=x + OFFX[0], y=y, rot=rot,
                      side="bottom" if bottom else "top", block=BI[0]))
    return fp


def place(lib, name, rf, value, x, y, rot=0.0, bottom=False, nets=None, mpn=""):
    fp = pcbnew.FootprintLoad(lib, name)
    if fp is None:
        raise RuntimeError("footprint not found: %s / %s" % (lib, name))
    return finish(fp, rf, value, x, y, rot, bottom, nets, mpn, name)


def custom_fp(name, pads, courtyard, descr="", model=None, paste=True, fab=None):
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
        p.SetSize(vloc(w, h))
        p.SetPos0(vloc(x, y))
        p.SetPosition(vloc(x, y))
        fp.Add(p)

    def rect(box, lays):
        x0, y0, x1, y1 = box
        for (a, b), (c, d) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            for lay, w in lays:
                sh = pcbnew.FP_SHAPE(fp)
                sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
                sh.SetStart0(vloc(a, b))
                sh.SetEnd0(vloc(c, d))
                sh.SetLayer(lay)
                sh.SetWidth(MM(w))
                sh.SetDrawCoord()
                fp.Add(sh)
    rect(courtyard, ((pcbnew.F_CrtYd, 0.05), (pcbnew.F_Fab, 0.1)) if pads else ((pcbnew.F_Fab, 0.1),))
    if fab:
        rect(fab, ((pcbnew.F_Fab, 0.1),))
    if model:
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = "${KIPRJMOD}/3d/" + model
        fp.Models().push_back(m)
    return fp


def lga13():
    pads = [(str(k + 1), -1.95 + 0.65 * k, 2.05, 0.35, 0.75, "rr") for k in range(7)]
    for num, x in (("13", -1.95), ("12", -1.3), ("11", -0.65), ("10", 0.65), ("9", 1.3), ("8", 1.95)):
        pads.append((num, x, -2.05, 0.35, 0.75, "rr"))
    return custom_fp("2EDF7275K_PG-TFLGA-13-4", pads, (-2.6, -2.5, 2.6, 2.5), "Infineon 2EDF7275K, datasheet Rev 3.0 Fig. 22",
                     model="2EDF7275K_PG-TFLGA-13-4.wrl")


def ufcs():
    """PMK UFCS shunt, recommended footprint (datasheet rev 02A p.3): two 15 x 3 mm pads, 0.5 mm gap; pad 1 = IN,
    pad 2 = SHLD (reference). Courtyard = 15 mm blade x 7.5 mm body; the 22 mm body (above 4.1 mm) on F.Fab.
    Variant "notch": the origin is the blade, IN land shortened to 1.2 mm (solder fillet only, manual p.12), so the
    blade sits 1.45 mm from the source copper; the body overhangs the LS FET at 4.1 mm height (stepped spreader)."""
    if SHORT_IN:
        return custom_fp("PMK_UFCS_R001_short_IN", [("1", 0.0, -0.85, 15.0, 1.2, "r"), ("2", 0.0, 1.75, 15.0, 3.0, "r")],
                         (-7.6, -1.4, 7.6, 3.4), "PMK UFCS-R001, IN land shortened to 1.2 mm (blade at the origin); courtyard ends at the LS FET courtyard (the body overhangs it at 4.1 mm)",
                         model="PMK_UFCS.wrl", fab=(-11.0, -3.75, 11.0, 3.75))
    return custom_fp("PMK_UFCS_R001", [("1", 0.0, -1.75, 15.0, 3.0, "r"), ("2", 0.0, 1.75, 15.0, 3.0, "r")],
                     (-7.6, -3.55, 7.6, 3.55), "PMK UFCS-R001 ultra-fast current shunt, 1 mOhm, 120 pH, SMA output",
                     model="PMK_UFCS.wrl", fab=(-11.0, -3.75, 11.0, 3.75))


def tmcs_dvg():
    """TI TMCS1123 DVG0010A, IPC nominal land pattern (SBOSA24D p.46), top view: 1 IN+ (top left), 2 IN- (bottom
    left), 2.0 x 4.41 mm at x = -4.65, y = -+2.54; pins 3 (bottom right) .. 10 (top right), 2.0 x 0.6 mm, 1.27 mm."""
    pads = [("1", -4.65, -2.54, 2.0, 4.41, "rr"), ("2", -4.65, 2.54, 2.0, 4.41, "rr")]
    for k in range(3, 11):
        pads.append((str(k), 4.65, 4.445 - (k - 3) * 1.27, 2.0, 0.6, "rr"))
    return custom_fp("TI_DVG0010A_TMCS1123", pads, (-5.9, -5.45, 5.9, 5.45),
                     "TI TMCS1123 Hall current sensor, SOIC-10 wide (DVG), IPC nominal land pattern",
                     model="TI_DVG0010A.wrl")


def heatsink_fp():
    """Fischer LAM 4 K 50 12 (40 x 40 mm profile, 50 mm long, 12 V fan; Farnell 4708974, 0.65 K/W), tube along x and
    centred (fan x -35 .. -25, tube -25 .. 25): stays inside the 89.5 mm board, so three legs fit side by side on the
    busbar with 5 mm gaps (a 100 mm LAM 4 + fan = 110 mm would collide with the neighbouring leg)."""
    return custom_fp("HS_LAM4K5012_revb", [], (-35.0, -28.7, 25.0, 8.8 if SHORT_IN else 11.3),
                     "Fischer LAM 4 K 50 12 (50 mm, 12 V fan) across the board on an Al spreader, ends at y = 11.3",
                     model="HS_LAM4K5012_revb.wrl")


_lib = os.path.join(OUT, "spb_fab.pretty")
os.makedirs(_lib, exist_ok=True)
for _f in (lga13(), ufcs(), heatsink_fp()):          # TMCS1123 dropped (LEM HO 250-S on the AC bar)
    _f.SetReference("REF**")
    pcbnew.FootprintSave(_lib, _f)


def padxy(rf, num):
    fp = board.FindFootprintByReference(rf)
    q = [p for p in fp.Pads() if p.GetNumber() == str(num)][0]
    return rx(q.GetPosition().x), pcbnew.ToMM(q.GetPosition().y)


def two(lib, name, rf, value, x, y, rot, n_lo, n_hi, mpn, bottom=False):
    """two-pad part; n_lo goes to the pad with the lower x (rot 0/180) or y (rot 90/270)."""
    fp = place(FP + lib, name, rf, value, x, y, rot, bottom, mpn=mpn)
    axis = 1 if rot in (90, 270) else 0
    pads = sorted(fp.Pads(), key=lambda q: q.GetPosition()[axis])
    pads[0].SetNet(net(n_lo))
    pads[1].SetNet(net(n_hi))
    return fp


def set_pads(fp, nets):
    for q in fp.Pads():
        if q.GetNumber() in nets:
            q.SetNet(net(nets[q.GetNumber()]))


def tight_courtyard(fp, body_half, m=0.05):
    for it in list(fp.GraphicalItems()):
        if it.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            fp.Remove(it)
    hy = max(pcbnew.ToMM(p.GetSize().y) for p in fp.Pads()) / 2 + m
    hx = body_half + m
    for (a, b), (c, d) in (((-hx, -hy), (hx, -hy)), ((hx, -hy), (hx, hy)), ((hx, hy), (-hx, hy)), ((-hx, hy), (-hx, -hy))):
        sh = pcbnew.FP_SHAPE(fp)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetLayer(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
        sh.SetWidth(MM(0.05))
        sh.SetStart0(vloc(a, b))
        sh.SetEnd0(vloc(c, d))
        fp.Add(sh)
        sh.SetDrawCoord()


SAVED = set()


def power_cap(name, value, x, y, n_up, n_lo, mpn, bottom=False):
    """bank/local MLCC across a strip gap (rot 90): pad with the lower y gets n_up."""
    fp = place(FP + "Capacitor_SMD.pretty", name, ref("C"), value, x, y, 90, mpn=mpn)
    tight_courtyard(fp, {"1210": 1.6, "2220": 3.45}.get(name.split("_")[1], 1.0))
    fp.SetFPID(pcbnew.LIB_ID("spb_fab", name + "_TightCrtYd"))
    PARTS[-1]["footprint"] = name + "_TightCrtYd"
    if name not in SAVED:
        SAVED.add(name)
        pcbnew.FootprintSave(_lib, fp)
    if bottom:                                   # flip after the courtyard is drawn: same as the library part
        fp.Flip(fp.GetPosition(), False)
        PARTS[-1]["side"] = "bottom"
    pads = sorted(fp.Pads(), key=lambda q: q.GetPosition().y)
    pads[0].SetNet(net(n_up))
    pads[1].SetNet(net(n_lo))
    return fp


# ------------------------------------------------------------------ outline
def edge(x0, y0, x1, y1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(vloc(x0, y0))
    s.SetEnd(vloc(x1, y1))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    board.Add(s)


edge(-XO, Y0, XO, Y1)
POWER_VIAS = []
TAPS = []
NETMAP = {"DCP": "DCP", "DCN": "DCN", "AC": "SW"}
VIA_SHIFT = {round(Y["dcp_via"], 2): 2.5}


def bank_net(y):
    """polarity of the strip that ends at / starts at a bank row gap."""
    return None


# ==================================================================== one building block
def build_block(bi, xoff):
    OFFX[0], BI[0] = xoff, bi
    print("STEP block", bi, flush=True)
    sw, lss = bn("SW"), bn("LSS")
    kh, kl = bn("KH"), bn("KL")                     # Kelvin networks: meet the source only inside the EPC2361
    # ---- power copper (block-local copy of the Q3D geometry)
    lsrc = {"L": "LSRC%d" % (2 * bi - 1), "R": "LSRC%d" % (2 * bi)}   # low-side source copper of each cell
    if NOSHUNT:
        lsrc = {"L": "DCN", "R": "DCN"}
    for n, nm, lay, x0, x1, y0, y1 in G["boxes"]:
        if lay in LAYER and n:
            prio = 2 if lay == "L1" else 1
            nn = sw if n == "AC" else NETMAP[n]
            if nm in ("SRC_L", "SRC_R"):
                y1 = 11.95
                nn = lsrc[nm[-1]]
            rect_zone(LAYER[lay], nn, max(x0, -XE), min(x1, XE), y0, y1, prio)
    for n, x, y, to in G["vias"]:
        if n == "DCN" and abs(y - Y["src_via"]) < 1e-6 and not NOSHUNT:
            continue                                    # the shunt closes the loop, not a via to L2
        POWER_VIAS.append(via(x, VIA_SHIFT.get(round(y, 2), y), sw if n == "AC" else NETMAP[n]))
    # (DC terminals: one pair for the whole leg at the board centre, see dc_terminals())

    # ---- transistors
    gate = {}
    qn = 4 * (bi - 1)
    for side, sgn, rot in (("L", -1, 0.0 if ROT0 else 180.0), ("R", 1, 0.0)):
        xq = sgn * XC
        epc = lambda g, k, s, d: {"1": g, "2": k, "4": s, "6": s, "3": d, "5": d, "7": d}
        qh = place(EPC_LIB, "EPC2361", "Q%d" % (qn + (1 if side == "L" else 2)), "EPC2361", xq, YQH, rot,
                   nets=epc(bn("GH_" + side), kh, sw, "DCP"), mpn="EPC2361")
        ql = place(EPC_LIB, "EPC2361", "Q%d" % (qn + (3 if side == "L" else 4)), "EPC2361", xq, YQL, rot,
                   nets=epc(bn("GL_" + side), kl, lsrc[side], sw), mpn="EPC2361")
        if NOSHUNT:
            # via-in-pad in the LS source stripes (pads 4, 6) straight into L2 DC-: the via row below the FET
            # cannot be used (it cuts the interleaved drain stripes), so the vias go inside the source stripes
            for q in ql.Pads():
                if q.GetNumber() in ("4", "6"):
                    bb = q.GetBoundingBox()
                    x0_, x1_ = rx(bb.GetLeft()), rx(bb.GetRight())
                    y0_, y1_ = pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())
                    for f_ in (0.2, 0.5, 0.8):
                        if (x1_ - x0_) < (y1_ - y0_):
                            bv = via((x0_ + x1_) / 2, y0_ + f_ * (y1_ - y0_), "DCN", 0.45, 0.25)
                        else:
                            bv = via(x0_ + f_ * (x1_ - x0_), (y0_ + y1_) / 2, "DCN", 0.45, 0.25)
                        bv.SetViaType(pcbnew.VIATYPE_BLIND_BURIED)       # L1 -> L2 only (bottom sense traces)
                        bv.SetLayerPair(F, L2l)
        for tag, fp in (("H", qh), ("L", ql)):
            g = [p for p in fp.Pads() if p.GetNumber() == "1"][0]
            k = [p for p in fp.Pads() if p.GetNumber() == "2"][0]
            gate[tag + side] = (rx(g.GetPosition().x), pcbnew.ToMM(g.GetPosition().y))
            ky = pcbnew.ToMM(k.GetPosition().y) + (0.85 if gate[tag + side][1] > pcbnew.ToMM(k.GetPosition().y) else -0.85)
            gate["K" + tag + side] = (rx(k.GetPosition().x), ky)
    # ---- local and bank MLCCs
    for side, sgn in (("L", -1), ("R", 1)):
        for i in range(6):
            power_cap("C_0805_2012Metric", "1uF 100V X7S", sgn * XC + (i - 2.5) * P["cap_p"],
                      (Y["capn"][0] + Y["capp"][1]) / 2, "DCN", "DCP", "TDK C2012X7S2A105K125AB")
    # bank MLCCs: placed once for the whole leg on a uniform 3 mm grid (see "bank" below)

    # ---- gate stars (L1) and Kelvin collectors (L2), as Rev A
    XB = XC - 5.2
    RG_X = 3.0
    KROW = {"H": YSH + 0.85, "L": YSL - 0.85}
    for tag, ys in (("H", YSH), ("L", YSL)):
        for side, sgn in (("L", -1), ("R", 1)):
            if ROT0 and side == "L":
                continue                        # study variant: left gate/Kelvin routing omitted
            gx, gy = gate[tag + side]
            kx, ky = gate["K" + tag + side]
            n_star, n_gate = bn("G%s_STAR" % tag), bn("G%s_%s" % (tag, side))
            two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "0R5 1%% (R_G %s%s)" % (tag, side),
                sgn * RG_X, ys, 0, n_gate if sgn < 0 else n_star, n_star if sgn < 0 else n_gate,
                "0.5R 0402 1% (Panasonic ERJ-2BQFR50X)")
            seg(F, [(0, ys), (sgn * (RG_X - 0.48), ys)], 0.3, n_star)
            seg(F, [(sgn * (RG_X + 0.48), ys), (sgn * XB, ys), (sgn * XB, gy), (gx - sgn * 0.55, gy)], 0.3, n_gate)
            kn = kh if tag == "H" else kl
            kvx = gx - sgn * 1.05
            seg(F, [(kx, ky), (kvx, ky)], 0.3, kn)
            via(kvx, ky, kn, 0.45, 0.25)
            # Kelvin collector on L4 (bottom), NOT on L2: L2 is the DC- return plane of the commutation loop and the
            # Kelvin pads of the left (180 deg) and right (0 deg) transistors sit at different heights, so L2 slots
            # would cut the return differently under the two cells of a pair (0.13 nH left/right difference).
            if tag == "H":                      # joins the HS Kelvin route on L4 at the corridor centre
                pts = [(kvx, ky), (sgn * XB, ky), (sgn * XB, KROW[tag]), (0, KROW[tag])]
                seg(Bl, pts, 0.3, kn)
            else:                               # LS: back to L2 inside the driver corridor (clear of the HS route)
                pts = [(kvx, ky), (sgn * XB, ky), (sgn * XB, KROW[tag]), (sgn * 1.6, KROW[tag])]
                seg(Bl, pts, 0.3, kn)
                via(sgn * 1.6, KROW[tag], kn, 0.45, 0.25)
                seg(L2l, [(sgn * 1.6, KROW[tag]), (0, KROW[tag])], 0.3, kn)
            # gate via for the U.FL V_GS sense (bottom side)
            via(sgn * 5.4, gy, n_gate, 0.45, 0.25)
            gate["V" + tag + side] = (sgn * 5.4, gy)
            gate["VK" + tag + side] = (kvx, ky)
    keepout(L2l, -3.3, 3.3, 3.3, 12.9)
    keepout(L2l, -4.6, 4.6, 10.0, 12.9)
    keepout(Bl, -3.3, 3.3, 4.6, 15.0)
    keepout(Bl, -4.6, 4.6, 10.0, 15.0)
    via(0.0, YSH, bn("GH_STAR"))
    via(0.0, KROW["H"], kh, 0.45, 0.25)
    GHV2 = (-1.5, 10.0)
    seg(L3l, [(0, YSH), (-0.75, YSH + 0.75), (-0.75, 9.25), GHV2], 0.3, bn("GH_STAR"))
    via(GHV2[0], GHV2[1], bn("GH_STAR"))
    HSK2 = (-3.9, 11.0)
    seg(Bl, [(0, KROW["H"]), (-0.75, KROW["H"] + 0.75), (-0.75, 10.6), (-1.15, 11.0), HSK2], 0.3, kh)
    via(HSK2[0], HSK2[1], kh, 0.45, 0.25)
    two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "10k 1% (HS gate pull-down)", 1.0, YSH + 0.43, 90,
        bn("GH_STAR"), kh, "10k 0402 1%")
    seg(F, [(1.0, YSH + 0.91), (0.0, KROW["H"])], 0.25, kh)
    two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "10k 1% (LS gate pull-down)", 1.0, YSL - 0.45, 90,
        kl, bn("GL_STAR"), "10k 0402 1%")
    via(0.0, 7.9, kl, 0.45, 0.25)
    seg(F, [(1.0, YSL - 0.93), (0.0, 7.9)], 0.25, kl)
    seg(L2l, [(0.0, 7.9), (0.0, KROW["L"])], 0.3, kl)
    LSK2 = (3.9, 11.0)
    seg(L2l, [(0, KROW["L"]), (0, 10.6), (0.4, 11.0), LSK2], 0.3, kl)
    via(LSK2[0], LSK2[1], kl, 0.45, 0.25)

    # ---- driver and its output networks (Rev A)
    finish(lga13(), "U%d" % bi, "2EDF7275K", 0.0, YDR, 0.0, False,
           {"1": bn("GNDI"), "2": bn("INA"), "3": bn("INB"), "4": bn("GNDI"), "5": bn("DIS"), "6": None, "7": bn("VDDI"),
            "8": bn("VEEB"), "9": bn("OUTB"), "10": bn("VDDB"), "11": bn("VEEA"), "12": bn("OUTA"), "13": bn("VDDA")},
           "Infineon 2EDF7275KXUMA1", "2EDF7275K_PG-TFLGA-13-4")
    drv = "U%d" % bi
    for ch, sg, out_pin, node in (("A", -1, 12, bn("GH_STAR")), ("B", 1, 9, bn("GL_STAR"))):
        two("Resistor_SMD.pretty", "R_0603_1608Metric", ref("R"), "0R75 1%% (R_ON,%s)" % ch, sg * 1.0, 12.2, 90,
            node, bn("OUT" + ch), "0.75R 0603 1% (Panasonic ERJ-3RQFR75V)")
        two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "0R (R_OFF,%s)" % ch, sg * 2.7, 11.7, 90,
            node, bn("OFF" + ch), "0R 0402 jumper (set R_OFF here)")
        d = place(FP + "Diode_SMD.pretty", "D_SOD-323F", ref("D"), "PMEG3020EJ", sg * 2.7, 14.25, 90, False,
                  mpn="Nexperia PMEG3020EJ (30 V, 2 A, SOD323F)")
        if padxy(d.GetReference(), 1)[1] < 14.25:
            d.SetOrientationDegrees(270.0)
            PARTS[-1]["rot"] = 270.0
        set_pads(d, {"1": bn("OUT" + ch), "2": bn("OFF" + ch)})
        ox, oy = padxy(drv, out_pin)
        seg(F, [(sg * 1.0, 11.375), (sg * 1.0, 11.3), (sg * 2.7, 11.3), (sg * 2.7, 11.22)], 0.3, node)
        seg(F, [(sg * 2.7, 12.18), (sg * 2.7, 13.15)], 0.3, bn("OFF" + ch))
        seg(F, [(sg * 1.0, 13.025), (sg * 1.0, 15.9), (ox, oy)], 0.3, bn("OUT" + ch))
        seg(F, [(sg * 2.7, 15.35), (sg * 2.2, 15.9), (sg * 1.0, 15.9)], 0.3, bn("OUT" + ch))
    seg(F, [GHV2, (-1.0, 10.7), (-1.0, 11.375)], 0.3, bn("GH_STAR"))
    seg(F, [(1.0, 11.375), (1.0, 10.3), (0, 10.3), (0, YSL)], 0.3, bn("GL_STAR"))
    cols = {}
    for ch, sg, top, bot, sref in (("A", -1, bn("VDDA"), bn("VEEA"), kh), ("B", 1, bn("VEEB"), bn("VDDB"), kl)):
        for yy, nn in ((13.45 + DY, top), (14.45 + DY, bot)):
            two("Capacitor_SMD.pretty", "C_0402_1005Metric", ref("C"), "1uF 16V X7R 0402", sg * 3.75, yy, 0,
                sref if sg < 0 else nn, nn if sg < 0 else sref, "Murata GRM155R71C105KA12")
        seg(F, [padxy(drv, 13 if sg < 0 else 8), (sg * 3.27, 13.45 + DY)], 0.3, top)
        seg(F, [padxy(drv, 11 if sg < 0 else 10), (sg * 0.65, 14.45 + DY), (sg * 3.27, 14.45 + DY)], 0.3, bot)
        K2 = HSK2 if sg < 0 else LSK2
        seg(F, [K2, (sg * 4.4, 11.5), (sg * 4.4, 13.45 + DY), (sg * 4.23, 13.45 + DY)], 0.3, sref)
        seg(F, [(sg * 4.4, 13.45 + DY), (sg * 4.4, 14.45 + DY), (sg * 4.23, 14.45 + DY)], 0.3, sref)
        seg(F, [(sg * 4.4, 14.45 + DY), (sg * 4.4, 15.4 + DY), (sg * 4.3, 16.0 + DY)], 0.3, sref)
        via(sg * 4.3, 16.0 + DY, sref)
        seg(F, [(sg * 3.27, 13.45 + DY), (sg * 3.2, 12.75 + DY)], 0.3, top)
        via(sg * 3.2, 12.75 + DY, top)
        seg(F, [(sg * 3.27, 14.45 + DY), (sg * 3.6, 15.3 + DY)], 0.3, bot)
        via(sg * 3.6, 15.3 + DY, bot)
        # L3 columns down to the supply island (outer = top-cap net, middle = source reference, inner = bottom)
        yc = {5.0: 22.1, 4.0: 27.8, 3.0: 31.6}                    # near / S / far column ends at the island
        seg(L3l, [(sg * 3.2, 12.75 + DY), (sg * 5.0, 12.75 + DY), (sg * 5.0, yc[5.0])], 0.3, top)
        seg(L3l, [(sg * 4.3, 16.0 + DY), (sg * 4.0, 16.3 + DY), (sg * 4.0, yc[4.0])], 0.3, sref)
        seg(L3l, [(sg * 3.6, 15.3 + DY), (sg * 3.0, 15.9 + DY), (sg * 3.0, yc[3.0])], 0.3, bot)
        for xc_, nn in ((5.0, top), (4.0, sref), (3.0, bot)):
            via(sg * xc_, yc[xc_], nn)
        cols[ch] = dict(top=top, bot=bot, s=sref)
    # input side: RC filters, VDDI (SLDO on, 3 k from 12 V, 22 nF), DISABLE
    two("Capacitor_SMD.pretty", "C_0402_1005Metric", ref("C"), "100pF C0G 0402", -2.0, 18.75 + DY, 0, bn("GNDI"),
        bn("INA"), "Murata GRM1555C1H101JA01")
    two("Capacitor_SMD.pretty", "C_0402_1005Metric", ref("C"), "100pF C0G 0402", -0.17, 19.85 + DY, 0, bn("INB"),
        bn("GNDI"), "Murata GRM1555C1H101JA01")
    two("Capacitor_SMD.pretty", "C_0402_1005Metric", ref("C"), "22nF 25V X7R 0402", 2.2, 18.75 + DY, 0, bn("VDDI"),
        bn("GNDI"), "Murata GRM155R71E223KA61")
    two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "47R 1% (INA)", -1.9, 21.3 + DY, 90, bn("INA"), bn("PWM_H"),
        "47R 0402 1%")
    two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "47R 1% (INB)", -0.65, 21.3 + DY, 90, bn("INB"), bn("PWM_L"),
        "47R 0402 1%")
    two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "3k 1% (RVDDI)", 1.9, 20.3 + DY, 90, bn("VDDI"), bn("+12V"),
        "3.0k 0402 1%")
    seg(F, [padxy(drv, 2), (-1.3, 18.3 + DY), (-1.52, 18.75 + DY), (-1.52, 19.3 + DY), (-1.9, 19.9 + DY),
            (-1.9, 20.82 + DY)], 0.25, bn("INA"))
    seg(F, [padxy(drv, 3), (-0.65, 20.82 + DY)], 0.25, bn("INB"))
    seg(F, [padxy(drv, 5), (0.65, 18.4 + DY), (1.0, 18.9 + DY)], 0.25, bn("DIS"))
    seg(F, [padxy(drv, 7), (1.95, 18.2 + DY), (1.72, 18.75 + DY), (1.9, 19.82 + DY)], 0.25, bn("VDDI"))

    # ---- shunts: IN pad continues the LS source strip, SHLD pad drops into the L2 DC- plane
    # variants (SHUNT_VARIANT): vip = DC- return vias inside the SHLD pad; compact = vip + shunt 1 mm closer to the
    # LS source; noshunt = no shunt, source copper is DC- with its vias to L2 (Rev A loop)
    dys = -1.0 if VARIANT == "compact" else 0.0
    ysv = YS + dys
    if SHORT_IN:                           # blade at y = 12.65: IN land 11.2 .. 12.4, SHLD 12.9 .. 15.9
        ysv, dys = 12.65, 12.4 - 15.0
    for side, sgn in (("L", -1), ("R", 1)):
        xs = sgn * XS_OFF
        c = 2 * (bi - 1) + (1 if side == "L" else 2)
        if not NOSHUNT:
            fp = ufcs()
            finish(fp, "RS%d" % c, "UFCS-R001", xs, ysv, 0.0, False, {"1": lsrc[side], "2": "DCN"},
                   "PMK UFCS-R001 (1 mOhm, 50 A cont.)", "PMK_UFCS_R001_short_IN" if SHORT_IN else "PMK_UFCS_R001")
        xa, xb = sorted((sgn * 4.9, sgn * 19.9))
        rect_zone(F, lsrc[side], xa, xb, 11.2, 15.0 + dys, 2)    # IN side, joined to the source strip
        rect_zone(F, "DCN", xa, xb, (ysv + 0.25) if SHORT_IN else 15.5 + dys, 20.2, 2)   # SHLD side
        rows = (19.0, 19.75)
        if not NOSHUNT:                # return vias inside the SHLD pad (shunt study: -0.05 nH)
            rows = (ysv + 0.75, ysv + 1.45, ysv + 2.15, ysv + 2.85) + rows     # via-in-pad (filled, capped)
        for yv in rows:
            k = 0
            while True:
                xv = xa + 0.5 + k * 1.0
                if xv > xb - 0.5:
                    break
                POWER_VIAS.append(via(xv, yv, "DCN"))
                k += 1
        xa2, xb2 = sorted((sgn * 4.9, sgn * 20.3))
        rect_zone(L2l, "DCN", xa2, xb2, 11.9, 20.6, 1)          # L2 DC- return under the shunt
        if not NOSHUNT:
            text("RS%d" % c, xs, 21.2, 0.8, pcbnew.F_Fab)

    # ---- AC columns per cell: L3/L4 from the cell down, L1/L2 below the shunts, into the AC bus (y > 36.3)
    for side, sgn in (("L", -1), ("R", 1)):
        o0, o1 = sorted((sgn * 5.4, sgn * 19.9))
        q0, q1 = sorted((sgn * 13.5, sgn * 19.9))
        for lay in (L3l, Bl):
            rect_zone(lay, sw, o0, o1, 5.2 if lay == L3l else 4.6, 33.4, 1)
            rect_zone(lay, sw, q0, q1, 33.0, YBUS, 1)
        for lay in (F, L2l):
            rect_zone(lay, sw, q0, q1, 20.8, YBUS, 1)
        yv = 21.6
        while yv <= YBUS - 0.6:
            k = 0
            while q0 + 0.6 + k * 1.2 <= q1 - 0.5:
                POWER_VIAS.append(via(q0 + 0.6 + k * 1.2, yv, sw))
                k += 1
            yv += 1.2

    # ---- external-supply islands, hand-routed (left: HS = channel A, ref KH; right: LS = channel B, ref KL)
    # Planar plan on L1: the column next to the island ("near", x = 5) is reached by a horizontal trace from the
    # choke's upper output and a vertical bus at x = 6.6; the far column (x = 3) by a bus at x = 8.05 that turns
    # along the island bottom (y = 29.6). Every source-reference (S) pad drops into the L2 shield, which is S.
    for ch, sg in (("A", -1), ("B", 1)):
        if ch == "A":
            near, far, s, near_in, far_in = bn("VDDA"), bn("VEEA"), kh, bn("VINA_P"), bn("VINA_N")
        else:
            near, far, s, near_in, far_in = bn("VEEB"), bn("VDDB"), kl, bn("VINB_N"), bn("VINB_P")
        vinp, vdd = bn("VIN%s_P" % ch), bn("VDD" + ch)
        X = lambda v: sg * v
        ia, ib = sorted((X(3.5), X(13.0)))
        rect_zone(L2l, s, ia, ib, 20.8, 33.4, 2)                 # shield = source reference of the channel
        # input connector (pin 1 = +): upper pin feeds the near line
        top_is_pin1 = near_in == vinp
        jv = place(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical", ref("J"),
                   "V_ISO,%s in: 1 +, 2 -" % ("HS" if ch == "A" else "LS"), X(13.2), 21.9 if top_is_pin1 else 24.44,
                   0 if top_is_pin1 else 180, False, None, "2.54 mm header 1x2")
        set_pads(jv, {"1": vinp, "2": bn("VIN%s_N" % ch)})
        # common-mode choke: windings 1-2 (upper line) and 4-3 (lower line)
        L = place(FP + "Inductor_SMD.pretty", "L_CommonMode_Wurth_WE-CNSW-1206", ref("L"), "WE-CNSW 744232601",
                  X(9.2), 22.6, 0, False, None, "Wurth 744232601 (600 Ohm @ 100 MHz, 260 mA)")
        if sg > 0:
            set_pads(L, {"2": near_in, "1": near, "3": far_in, "4": far})
        else:
            set_pads(L, {"1": near_in, "2": near, "4": far_in, "3": far})
        seg(F, [(X(13.2), 21.9), (X(10.55), 22.1)], 0.3, near_in)
        seg(F, [(X(13.2), 24.44), (X(10.55), 23.1)], 0.3, far_in)
        seg(F, [(X(7.85), 22.1), (X(5.0), 22.1)], 0.3, near)          # near column via at (5, 22.1)
        seg(F, [(X(6.6), 22.1), (X(6.6), 28.6)], 0.3, near)           # near bus
        seg(F, [(X(7.85), 23.1), (X(7.85), 31.6), (X(3.0), 31.6)], 0.3, far)   # far bus to the column via
        two("Capacitor_SMD.pretty", "C_0805_2012Metric", ref("C"), "4.7uF 25V X7R 0805", X(7.3), 24.7, 0,
            near if sg > 0 else far, far if sg > 0 else near, "Murata GRM21BR71E475KA73")

        def slot(kind, x, y, rot, role, mpn_val):
            name, lib, val, mpn = mpn_val
            fp = place(FP + lib, name, ref(kind), val, X(x), y, rot, False, None, mpn)
            pads = sorted(fp.Pads(), key=lambda q: abs(rx(q.GetPosition().x)) if rot in (0, 180) else
                          pcbnew.ToMM(q.GetPosition().y))
            # rot 0: outer pad = near (slot SN1) or S (slots SF); rot 90: upper pad = near
            if role == "near":
                bus_pad, s_pad = (pads[1], pads[0]) if rot in (0, 180) else (pads[0], pads[1])
                bus_net = near
            else:
                bus_pad, s_pad = pads[0], pads[1]
                bus_net = far
            return fp, bus_pad, s_pad, bus_net

        CAP = ("C_0603_1608Metric", "Capacitor_SMD.pretty", "4.7uF 16V X5R 0603", "Murata GRM188R61C475KAAJ")
        RB = ("R_0603_1608Metric", "Resistor_SMD.pretty", "150R 1% 0603 (bias, <= 82 mW)", "150R 0603 1% 0.1 W")
        DZ = ("D_SOD-323", "Diode_SMD.pretty", "BZX384-C5V1", "Nexperia BZX384-C5V1 (5.1 V, 300 mW)")
        if ch == "A":       # near = VDD: Zener and C(VDD-S) on the near side; R_b and C(S-VEE) on the far side
            plan = [("D", 5.1, 26.8, 0, "near", DZ), ("C", 6.6, 29.45, 90, "near", CAP),
                    ("C", 9.2, 27.0, 0, "far", CAP), ("R", 9.4, 29.6, 0, "far", RB)]
        else:               # near = VEE: R_b and C(S-VEE) near; C(VDD-S) and Zener far
            plan = [("R", 5.1, 26.8, 0, "near", RB), ("C", 6.6, 29.45, 90, "near", CAP),
                    ("C", 9.2, 27.0, 0, "far", CAP), ("D", 9.4, 29.6, 0, "far", DZ)]
        for k, (kind, x, y, rot, role, part) in enumerate(plan):
            fp, bp, sp, bnet = slot(kind, x, y, rot, role, part)
            if kind == "D" and bnet != vdd:
                raise RuntimeError("Zener must sit on the VDD bus")
            if kind == "D" and bp.GetNumber() != "1":          # cathode (pad 1) to VDD
                fp.SetOrientationDegrees((fp.GetOrientationDegrees() + 180) % 360)
                PARTS[-1]["rot"] = fp.GetOrientationDegrees()
                bp, sp = sp, bp
            bp.SetNet(net(bnet))
            sp.SetNet(net(s))
            bx_, by_ = rx(bp.GetPosition().x), pcbnew.ToMM(bp.GetPosition().y)
            sx_, sy_ = rx(sp.GetPosition().x), pcbnew.ToMM(sp.GetPosition().y)
            busx = X(6.6) if role == "near" else X(7.85)
            if rot in (0, 180):
                seg(F, [(bx_, by_), (busx, by_)], 0.3, bnet)
            if k == 0:                                          # S pad -> S column via (also into the shield)
                seg(F, [(sx_, sy_), (X(4.0), 27.8)], 0.3, s)
            elif k == 1:
                via(sx_, sy_ + 0.7, s, 0.45, 0.25)
                seg(F, [(sx_, sy_), (sx_, sy_ + 0.7)], 0.3, s)
            elif k == 2:
                via(sx_, sy_ - 0.85, s, 0.45, 0.25)
                seg(F, [(sx_, sy_), (sx_, sy_ - 0.85)], 0.3, s)
            else:
                via(sx_ + X(0.6), sy_ + 0.75, s, 0.45, 0.25)
                seg(F, [(sx_, sy_), (sx_ + X(0.6), sy_ + 0.75)], 0.3, s)
        text("HS ISO" if ch == "A" else "LS ISO", X(10.6), 20.4, 0.8, pcbnew.F_Fab)

    # ---- primary side of the block: corridor pours, control connector with common-mode chokes
    gi = bn("GNDI")
    rect_zone(Bl, gi, -1.9, 1.9, 16.0 + DY, 23.2 + DY, 1)
    rect_zone(Bl, gi, -4.6, 4.6, 26.7, 38.8, 1)
    rect_zone(Bl, gi, -12.0, 12.0, 33.8, 38.8, 1)
    rect_zone(L2l, gi, -12.0, 12.0, 33.8, 38.8, 1)
    place(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_2x03_P2.54mm_Vertical", ref("J"),
          "CTRL%d: 1 12V 2 GND 3 PWM_H 4 PWM_L 5 DIS 6 GND" % bi, -3.6, 37.6, 90, False,
          {"1": bn("C_12V"), "2": bn("C_GND"), "3": bn("C_PWMH"), "4": bn("C_PWML"), "5": bn("C_DIS"),
           "6": bn("C_GND")}, "2.54 mm header 2x3")
    for xk, (a_in, a_out, b_in, b_out) in ((-10.5, (bn("C_12V"), bn("+12V"), bn("C_GND"), gi)),
                                           (-7.9, (bn("C_PWMH"), bn("PWM_H"), bn("C_PWML"), bn("PWM_L"))),
                                           (4.6, (bn("C_DIS"), bn("DIS"), None, None))):
        L = place(FP + "Inductor_SMD.pretty", "L_CommonMode_Wurth_WE-CNSW-1206", ref("L"), "WE-CNSW 744232601",
                  xk, 36.3, 90, False, None, "Wurth 744232601 (600 Ohm @ 100 MHz, 260 mA)")
        set_pads(L, {"1": a_in, "2": a_out} if b_in is None else {"1": a_in, "2": a_out, "4": b_in, "3": b_out})
    two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "10k (PWM_H pull-down)", 6.3, 34.7, 90, bn("PWM_H"), gi,
        "10k 0402 1%")
    two("Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), "10k (PWM_L pull-down)", 7.4, 34.7, 90, bn("PWM_L"), gi,
        "10k 0402 1%")
    two("Capacitor_SMD.pretty", "C_0805_2012Metric", ref("C"), "4.7uF 25V X7R 0805 (12 V)", 7.4, 37.7, 0, bn("+12V"),
        gi, "Murata GRM21BR71E475KA73")
    if bi == 1:
        d7 = place(FP + "LED_SMD.pretty", "LED_0603_1608Metric", ref("D"), "green 0603 (12 V)", 10.9, 34.6, 90, False,
                   None, "Wurth 150060GS75000")
        set_pads(d7, {"1": gi, "2": bn("LEDA_12V")})
        two("Resistor_SMD.pretty", "R_0603_1608Metric", ref("R"), "4.7k (LED)", 10.9, 37.6, 90, bn("LEDA_12V"),
            bn("+12V"), "4.7k 0603 1%")
    else:
        place(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical", ref("J"),
              "FAN 12V: 1 +12V, 2 GND", 11.4, 34.9, 0, False, {"1": bn("+12V"), "2": gi}, "2.54 mm header 1x2 (fan)")
    text("CTRL%d" % bi, -10.5, 38.9, 0.8, pcbnew.F_Fab)

    # ---- U.FL connectors (bottom side, outer half of each cell), series resistors, explicit L4 traces
    ufl = []
    for side, sgn in (("L", -1), ("R", 1)):
        if ROT0 and side == "L":
            continue
        c = 2 * (bi - 1) + (1 if side == "L" else 2)
        gvh, gvl, kvl, kvh = gate["VH" + side], gate["VL" + side], gate["VKL" + side], gate["VKH" + side]
        rows = (("H", gvh[1], gvh, kh, "0R (V_GS HS)", "0R 0402"),
                ("L", gvl[1], gvl, kl, "0R (V_GS LS)", "0R 0402"),
                ("D", 14.9, None, lsrc[side], "953R 1% (V_DS LS, 20:1 into 50 R)", "953R 0402 1% 100 V"))
        for tag, yy, src, gnd, val, mpn in rows:
            sn = "UFL_%s%d" % (tag, c)
            fp = place(FP + "Connector_Coaxial.pretty", "U.FL_Hirose_U.FL-R-SMT-1_Vertical", ref("J"),
                       "U.FL %s%d" % (tag, c), sgn * (16.2 if tag == "L" else 13.0), yy, 180 if sgn < 0 else 0,
                       True, None,
                       "Hirose U.FL-R-SMT-1(10)")
            set_pads(fp, {"1": sn, "2": gnd})
            for z in list(fp.Zones()):
                fp.Remove(z)                          # library keepout (RF) would block the sense leads and pours
            for it in list(fp.GraphicalItems()):
                if it.GetLayer() in (pcbnew.F_Mask, pcbnew.B_Mask):
                    fp.Remove(it)                     # keep only the pad openings
            if "U.FL" not in SAVED:
                SAVED.add("U.FL")
                cp = pcbnew.FOOTPRINT(fp)
                cp.SetReference("REF**")
                if cp.IsFlipped():
                    cp.Flip(cp.GetPosition(), False)
                cp.SetOrientationDegrees(0)
                pcbnew.FootprintSave(_lib, cp)
            fp.SetFPID(pcbnew.LIB_ID("spb_fab", "U.FL_Hirose_U.FL-R-SMT-1_Vertical"))
            PARTS[-1]["footprint"] = "U.FL_Hirose_U.FL-R-SMT-1_Vertical"
            cx, cy = padxy(fp.GetReference(), "1")
            src_net = sw if tag == "D" else bn(("GH_" if tag == "H" else "GL_") + side)
            ri, ro = sgn * (9.6 - 0.48), sgn * (9.6 + 0.48)
            r = place(FP + "Resistor_SMD.pretty", "R_0402_1005Metric", ref("R"), val, sgn * 9.6, yy, 0, True, None, mpn)
            for q in r.Pads():
                inner = abs(rx(q.GetPosition().x)) < 9.6
                q.SetNet(net(src_net if inner else sn))
            seg(Bl, [(ro, yy), (cx, cy)], 0.25, sn)
            if src is not None:
                seg(Bl, [src, (ri, yy)], 0.25, src_net)
            gpads = [q for q in fp.Pads() if q.GetNumber() == "2"]
            seg(Bl, [(rx(gpads[0].GetPosition().x), pcbnew.ToMM(gpads[0].GetPosition().y)),
                     (rx(gpads[1].GetPosition().x), pcbnew.ToMM(gpads[1].GetPosition().y))], 0.4, gnd)
            if tag in ("H", "L"):                       # Kelvin via -> nearest ground pad, along the Kelvin row
                kv = kvh if tag == "H" else kvl
                gp = min(gpads, key=lambda q: abs(pcbnew.ToMM(q.GetPosition().y) - kv[1]))
                seg(Bl, [kv, (rx(gp.GetPosition().x), kv[1])], 0.25, gnd)
            if tag == "D":                              # LSS via from the shunt IN copper (L1) above
                gp = min(gpads, key=lambda q: pcbnew.ToMM(q.GetPosition().y))
                gx_, gy_ = rx(gp.GetPosition().x), pcbnew.ToMM(gp.GetPosition().y)
                vy_ = min(gy_ - 1.2, 11.8) if SHORT_IN else gy_ - 1.2   # inside the (short) IN land
                via(gx_, vy_, gnd, 0.6, 0.3)
                seg(Bl, [(gx_, vy_), (gx_, gy_)], 0.4, gnd)
            ufl.append((sn, src_net, gnd, c, tag))

    # ---- second bypass row (bottom side, under the top row): 6 more 1 uF 0805 per cell -> 12 per cell
    # (2.1 uF at 75 V; hand-over dip 81 A x sqrt(0.75 nH / 2.1 uF) = 1.5 V). L4 islands DC- (top pad row) and
    # DC+ (bottom pad row) are tied to L2 / L3 by the existing N2 and cell DC+ through-via rows.
    def bottom_free(x, y, hx, hy, m=0.25):
        for fp_ in board.GetFootprints():
            if not fp_.IsFlipped() or fp_.GetValue().startswith("1uF 100V"):
                continue                                 # own row: spaced by the cap pitch
            for q in fp_.Pads():
                bb = q.GetBoundingBox()
                if (rx(bb.GetLeft()) - m < x + hx and rx(bb.GetRight()) + m > x - hx and
                        pcbnew.ToMM(bb.GetTop()) - m < y + hy and pcbnew.ToMM(bb.GetBottom()) + m > y - hy):
                    return False
        for t_ in board.GetTracks():
            if t_.GetClass() == "PCB_TRACK" and t_.GetLayer() == Bl:
                a = (rx(t_.GetStart().x), pcbnew.ToMM(t_.GetStart().y))
                b = (rx(t_.GetEnd().x), pcbnew.ToMM(t_.GetEnd().y))
                for k in range(11):
                    px, py = a[0] + (b[0] - a[0]) * k / 10, a[1] + (b[1] - a[1]) * k / 10
                    if abs(px - x) < hx + m + 0.2 and abs(py - y) < hy + m + 0.2:
                        return False
        return True

    yb = (Y["capn"][0] + Y["capp"][1]) / 2
    xs = lambda sgn, i: sgn * XC + (i - 2.5) * P["cap_p"]                       # noqa: E731
    # mirrored positions only (left index i <-> right index 5 - i): both cells of the pair stay identical
    keep = [i for i in range(6) if bottom_free(xs(-1, i), yb, 0.75, 1.25) and bottom_free(xs(1, 5 - i), yb, 0.75, 1.25)]
    for side, sgn in (("L", -1), ("R", 1)):
        xc_ = sgn * XC
        rect_zone(Bl, "DCN", xc_ - 4.8, xc_ + 4.8, -1.2, 0.95, 1)
        rect_zone(Bl, "DCP", xc_ - 4.8, xc_ + 4.8, 1.45, 3.3, 1)
        for i in keep:
            power_cap("C_0805_2012Metric", "1uF 100V X7S", xs(sgn, i if sgn < 0 else 5 - i), yb, "DCN", "DCP",
                      "TDK C2012X7S2A105K125AB", bottom=True)
    OFFX[0], BI[0] = 0.0, 0
    return dict(gate=gate, ufl=ufl)


def dc_terminals():
    """ONE DC+ / DC- terminal pair for the whole leg at the board centre (x = -6 / +6). The terminal row is a
    laminated stack across both blocks: L1 and L3 DC+, L2 and L4 DC-, so both polarities reach every bank strip
    over the full width (the left and right cells see the same DC path)."""
    xt = BX + 12.0
    rect_zone(F, "DCP", -xt, xt, YT, Y["p1"][0], 1)
    rect_zone(L2l, "DCN", -xt, xt, YT, Y["l2"][0], 1)
    rect_zone(L3l, "DCP", -xt, xt, YT, max(Y["p1"][0], Y["l3"][0]), 1)
    rect_zone(Bl, "DCN", -xt, xt, YT, Y["p1"][0] - 0.6, 1)
    for x, n, lab in ((-6.0, "DCP", "DC+"), (6.0, "DCN", "DC-")):
        fp = place(FP + "TerminalBlock_Wuerth.pretty", "Wuerth_REDCUBE-THR_WP-THRBU_74650174_THR", ref("J"), lab,
                   x, YT + 4.6, 0, True, mpn="Wuerth 74650174 (REDCUBE THR, M4)")
        for pad in fp.Pads():
            pad.SetNet(net(n))
        text(lab, x, YT + 0.9, 0.8)


dc_terminals()
BLK = {1: build_block(1, -BX), 2: build_block(2, BX)}

# ==================================================================== shared copper between the blocks
print("STEP centre", flush=True)
XM = BX - XE                                     # inner strip ends at |x| = 7.75
for nm, net_, y0, y1 in (("P1", "DCP", *Y["p1"]), ("N1", "DCN", *Y["n1"]), ("P2", "DCP", *Y["p2"]),
                         ("N2", "DCN", *Y["n2"])):
    rect_zone(F, net_, -XM - 0.2, XM + 0.2, y0, y1, 2)
rect_zone(L2l, "DCN", -XM - 0.2, XM + 0.2, Y["l2"][0], 20.6, 1)
rect_zone(L3l, "DCP", -XM - 0.2, XM + 0.2, Y["l3"][0], Y["l3"][1], 1)
for yv, n in ((Y["p1_via"], "DCP"), (Y["n1_via"], "DCN"), (Y["p2_via"], "DCP"), (Y["n2_via"], "DCN")):
    x = -XM + 0.6
    while x <= XM - 0.6 + 1e-6:
        POWER_VIAS.append(via(x, yv, n))
        x += 1.2
# bank: 20 x TDK 22 uF 100 V X7S 2220 (3 % ripple at 50 kHz with the three legs of a level sharing the bus):
# row B (12) on the P2/N2 boundary next to the cells, row A (8) on the P1/N1 boundary, clear of the DC terminal pins
for row, g0 in (("A", Y["p1"][1]), ("B", Y["p2"][1])):
    for ax in BANK_ROWS[row]:
        for sx in (-1, 1):
            power_cap(BANK[0], BANK[1], sx * ax, g0 + P["gap"] / 2, "DCP", "DCN", BANK[2])

# ==================================================================== AC bus, output terminals, bar and sensor
print("STEP AC bus", flush=True)
for lay in (F, L2l, L3l, Bl):
    rect_zone(lay, "SW", -XO + 0.8, XO - 0.8, YBUS, Y1 - 0.8, 1)
yv = YBUS + 0.7
while yv <= Y1 - 1.4:
    x = -XO + 1.6
    while x <= XO - 1.6:
        POWER_VIAS.append(via(x, yv, "SW"))
        x += 1.6
    yv += 1.6
def ac_bolt_pad():
    """ONE AC output: M6 bolt pad (6.4 mm plated hole, 14 mm pad on both outer layers, 16 x 0.4 mm vias on two rings
    into all layers). The 12 x 5 mm Cu bar is bolted directly onto it; the LEM HO 250-S sits on the bar."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID("spb_fab", "AC_BOLT_M6"))
    fp.SetDescription("AC output bolt pad, M6, 14 mm pad, via rings")
    pads = [(0.0, 0.0, 14.0, 6.4)]
    for k in range(10):
        a = 2 * math.pi * (k + 0.5) / 10
        pads.append((5.6 * math.cos(a), 5.6 * math.sin(a), 0.8, 0.4))
    for k in range(6):
        a = 2 * math.pi * k / 6
        pads.append((4.4 * math.cos(a), 4.4 * math.sin(a), 0.8, 0.4))
    for x, y, d, dr in pads:
        p = pcbnew.PAD(fp)
        p.SetNumber("1")
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetLayerSet(p.PTHMask())
        p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        p.SetSize(vloc(d, d))
        p.SetDrillSize(vloc(dr, dr))
        p.SetPos0(vloc(x, y))
        p.SetPosition(vloc(x, y))
        fp.Add(p)
    for k in range(36):
        a0, a1 = 2 * math.pi * k / 36, 2 * math.pi * (k + 1) / 36
        for lay, r in ((pcbnew.F_CrtYd, 7.25), (pcbnew.F_Fab, 7.0)):
            sh = pcbnew.FP_SHAPE(fp)
            sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
            sh.SetStart0(vloc(r * math.cos(a0), r * math.sin(a0)))
            sh.SetEnd0(vloc(r * math.cos(a1), r * math.sin(a1)))
            sh.SetLayer(lay)
            sh.SetWidth(MM(0.05 if lay == pcbnew.F_CrtYd else 0.1))
            sh.SetDrawCoord()
            fp.Add(sh)
    finish(fp, ref("J"), "AC", 0.0, YAC, 0.0, False, {"1": "SW"}, "M6 bolt + nut, 12 x 5 mm Cu bar", "AC_BOLT_M6")
    if "AC_BOLT_M6" not in SAVED:
        SAVED.add("AC_BOLT_M6")
        cp = pcbnew.FOOTPRINT(fp)
        cp.SetReference("REF**")
        cp.SetPosition(vloc(0, 0))
        pcbnew.FootprintSave(_lib, cp)
    return fp


YAC = 47.2
ac_bolt_pad()
text("AC OUT: M6 bolt pad, 12 x 5 mm Cu bar bolted on, through the LEM HO 250-S to the load", 0, 39.9, 0.8, pcbnew.F_Fab)


def fab_rect(x0, y0, x1, y1, layer=pcbnew.Cmts_User):
    for (a, b), (c, d) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        sh = pcbnew.PCB_SHAPE(board)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(vloc(a, b))
        sh.SetEnd(vloc(c, d))
        sh.SetLayer(layer)
        sh.SetWidth(MM(0.15))
        board.Add(sh)


fab_rect(-6.0, YAC - 7.0, 6.0, Y1 + 30.0)            # 12 x 5 mm bar from the bolt pad off the board edge
fab_rect(-18.9, Y1 + 8.0, 18.9, Y1 + 23.0)           # LEM HO 250-S (37.8 mm) on the stub
t = pcbnew.PCB_TEXT(board)
t.SetText("LEM HO 250-S on the bar stub; JST PHR-5 lead to the C2000 (1 Uc 2 GND 3 Uout 4 Uref 5 OCD)")
t.SetPosition(vloc(0, Y1 + 25.0))
t.SetLayer(pcbnew.Cmts_User)
board.Add(t)

# NTC near the inner HS FET of block 2, read on J (DC- referenced) in the centre band
two("Resistor_SMD.pretty", "R_0402_1005Metric", "RT1", "NTC 10k B3380", 7.0, 2.8, 90, "NTC", "DCN",
    "Murata NCP15XH103F03RC")
seg(F, [(7.0, 3.28), (7.0, 4.0)], 0.3, "DCN")
via(7.0, 4.0, "DCN")
seg(F, [(7.0, 2.32), (6.0, 2.32)], 0.25, "NTC")
via(6.0, 2.32, "NTC")
place(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical", ref("J"),
      "1:NTC 2:DC- (LS domain!)", 0.0, 24.0, 0, False, {"1": "NTC", "2": "DCN"}, "2.54 mm header 1x2")
seg(L2l, [(6.0, 2.32), (6.0, 21.6), (1.2, 22.8), (0.0, 24.0)], 0.25, "NTC")
seg(L2l, [(0.0, 26.54), (-1.6, 25.4), (-1.6, 20.3)], 0.3, "DCN")

# DC link indicator and bleeder (block 2 terminal zone, as Rev A)
OFFX[0] = BX
two("Resistor_SMD.pretty", "R_1206_3216Metric", ref("R"), "68k 1206 (HV LED)", 16.1, -16.5, 90, "HVA", "DCP",
    "68k 1206 1% 200 V")
two("Resistor_SMD.pretty", "R_1206_3216Metric", ref("R"), "68k 1206 (HV LED)", 18.6, -16.5, 90, "HVB", "HVA",
    "68k 1206 1% 200 V")
d8 = place(FP + "LED_SMD.pretty", "LED_0603_1608Metric", ref("D"), "red 0603 (DC link present)", 18.4, -12.6, 0,
           False, None, "Wurth 150060RS75000")
set_pads(d8, {"1": "DCN", "2": "HVB"})
two("Resistor_SMD.pretty", "R_1206_3216Metric", ref("R"), "100k 1206 (bleeder)", 19.2, -8.5, 90, "DCN", "DCP",
    "100k 1206 1% 200 V")
text("HV", 18.4, -11.0, 0.8)
OFFX[0] = 0.0

# mounting: board corners, spreader holes (outer edges + centre)
for hx, hy in ((-(XO - 2.4), Y1 - 2.4), ((XO - 2.4), Y1 - 2.4), (-(XO - 2.4), Y0 + 2.4), ((XO - 2.4), Y0 + 2.4)):
    place(FP + "MountingHole.pretty", "MountingHole_2.7mm_M2.5", ref("H"), "M2.5 insulated", hx, hy)
if HEATSINK:                                      # load-test board: spreader holes + LAM 4 heatsink
    for hx, hy in ((-(XO - 1.75), 0.2), ((XO - 1.75), 0.2), (0.0, 6.0)):
        place(FP + "MountingHole.pretty", "MountingHole_2.7mm_M2.5", ref("H"), "M2.5 heatsink spreader", hx, hy)
    hs = heatsink_fp()
    finish(hs, "HS1", "Fischer LAM 4 K 50 12 + spreader", 0.0, 0.0, 0, False, None,
           "Fischer LAM 4 K 50 12 (Farnell 4708974); Al spreader 89.5 x 12.8 x 3 mm (machined); insulating gap pads",
           "HS_LAM4K5012_revb")
    hs.SetAttributes(hs.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY)
text("SPB leg Rev B %s: 4 x EPC2361 per switch" % ({"dpt": "DPT (UFCS shunts, no heatsink)", "load": "LOAD TEST (no shunt, heatsink)"}.get(BOARD, "") if not VARIANT else VARIANT), 0, 36.0, 0.8, pcbnew.F_Fab)

# ==================================================================== auxiliary routing
print("STEP route", flush=True)
LAYS = [F, L2l, L3l, Bl]
HARD = ("DCP", "DCN", "SW", "LSRC1", "LSRC2", "LSRC3", "LSRC4", "KH1", "KH2", "KL1", "KL2")
R = fab_router.Router(board, (-XO, Y0, XO, Y1), LAYS, clearance=0.15, edge=0.7, hard_zones=HARD)
fails = 0


def A(bx, x0, x1):
    a, b = sorted((bx + x0, bx + x1))
    return a, b


for bi, bx in ((1, -BX), (2, BX)):
    BI[0] = bi
    # driver channel and sensors: primary nets
    PRI = [(0, bx - 2.6, bx + 2.6, 17.0 + DY, 33.9), (0, bx - 12.2, bx + 12.2, 33.7, 38.9),
           (1, bx - 3.3, bx + 3.3, 26.7, 38.9), (2, bx - 2.6, bx + 2.6, 26.7, 38.9), (3, bx - 4.6, bx + 4.6, 26.7, 38.9),
           (1, bx - 12.2, bx + 12.2, 33.7, 38.9), (2, bx - 12.2, bx + 12.2, 33.7, 38.9),
           (1, bx - 2.6, bx + 2.6, 24.0, 26.7), (2, bx - 2.6, bx + 2.6, 24.0, 26.7),
           (3, bx - 12.2, bx + 12.2, 33.7, 38.9)]
    for n, w in (("GNDI", 0.3), ("+12V", 0.3), ("PWM_H", 0.2), ("PWM_L", 0.2), ("DIS", 0.2), ("LEDA_12V", 0.2),
                 ("C_12V", 0.3), ("C_GND", 0.3), ("C_PWMH", 0.2), ("C_PWML", 0.2), ("C_DIS", 0.2)):
        fails += R.route_net(bn(n), PRI, width=w)
BI[0] = 0
# DC-link indicator: own router with 0.6 mm clearance
RHV = fab_router.Router(board, (-XO, Y0, XO, Y1), LAYS, clearance=0.6, edge=0.7, hard_zones=HARD)
HVR = [(0, BX + 11.4, BX + 20.4, Y0 + 0.5, -4.6)]
for n in ("HVA", "HVB", "DCN", "DCP"):
    fails += RHV.route_net(n, HVR, width=0.3, vias_ok=False)
print("route failures:", fails, flush=True)
# unused second taps (only the L3 column reaches them) would be dangling vias
for v in TAPS:
    vx, vy = pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y)
    used = False
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA" or t.GetLayer() == L3l or t.GetNetname() != v.GetNetname():
            continue
        for e in (t.GetStart(), t.GetEnd()):
            if math.hypot(pcbnew.ToMM(e.x) - vx, pcbnew.ToMM(e.y) - vy) < 0.35:
                used = True
    if not used:
        board.Remove(v)

# ==================================================================== prune power vias that violate clearance
print("STEP prune", flush=True)
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
PTH = []
for fp in board.GetFootprints():
    for q in fp.Pads():
        if q.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) and q.GetDrillSize().x > 0:
            PTH.append((pcbnew.ToMM(q.GetPosition().x), pcbnew.ToMM(q.GetPosition().y),
                        max(pcbnew.ToMM(q.GetDrillSize().x), pcbnew.ToMM(q.GetSize().x)) / 2))
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
BAD = set()
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
        if d - r < CLV + 0.12:
            bad = True
            break
    for hx_, hy_, hr_ in PTH:
        if math.hypot(x - hx_, y - hy_) < hr_ + 0.15 + 0.45:
            bad = True
    if bad:
        BAD.add(id(v))
# symmetric pruning: a power via removed in one cell takes its mirror image (about the block centre) in the other
# cell with it, so both cells of a pair keep identical via sets (a single surviving via changed the loop by ~0.13 nH)
_pos = [(pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y), v.GetNetname(), v) for v in POWER_VIAS]
for x, y, n, v in _pos:
    if id(v) not in BAD:
        continue
    bx_ = -BX if x < 0 else BX
    for x2, y2, n2, v2 in _pos:
        if n2 == n and abs(x2 - (2 * bx_ - x)) < 0.15 and abs(y2 - y) < 0.15:
            BAD.add(id(v2))
for v in POWER_VIAS:
    if id(v) in BAD:
        board.Remove(v)
        removed += 1
print("power vias removed:", removed, "of", len(POWER_VIAS), "(mirror pairs)", flush=True)

# ==================================================================== save, fill, DRC
print("STEP save", flush=True)
OX, OY = 150.0, 100.0
mv = vloc(OX, OY)
for it in list(board.GetDrawings()) + list(board.GetTracks()) + list(board.GetFootprints()) + list(board.Zones()):
    it.Move(mv)
ds.SetAuxOrigin(vloc(OX - XO, OY + Y1))
path = os.path.join(OUT, NAME + ".kicad_pcb")
pcbnew.SaveBoard(path, board)
json.dump({"board": {"design_settings": {"rule_severities": {
    "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore", "silk_over_copper": "warning",
    "silk_overlap": "warning", "silk_edge_clearance": "warning", "text_height": "warning",
    "text_thickness": "warning"}}},
    "meta": {"filename": NAME + ".kicad_pro", "version": 1}}, open(os.path.join(OUT, NAME + ".kicad_pro"), "w"), indent=1)
json.dump(PARTS, open(os.path.join(OUT, "parts.json"), "w"), indent=1)
_epc = "${KIPRJMOD}/.." if not VARIANT else "${KIPRJMOD}/../.."
open(os.path.join(OUT, "fp-lib-table"), "w").write(
    '(fp_lib_table\n'
    '  (lib (name "spb_fab")(type "KiCad")(uri "${KIPRJMOD}/spb_fab.pretty")(options "")(descr "SPB footprints"))\n'
    '  (lib (name "epc2361-cell")(type "KiCad")(uri "%s/epc2361-cell/epc2361-cell.pretty")(options "")'
    '(descr "EPC2361 land pattern"))\n)\n' % _epc)
board2 = pcbnew.LoadBoard(path)
board2.BuildConnectivity()
print("filling", flush=True)
pcbnew.ZONE_FILLER(board2).Fill(board2.Zones())
pcbnew.SaveBoard(path, board2)
pcbnew.WriteDRCReport(board2, os.path.join(OUT, "drc_report.txt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
print("saved", path, "footprints", len(board.GetFootprints()), "nets", len(NETS),
      "outline %.1f x %.1f mm" % (2 * XO, Y1 - Y0), flush=True)

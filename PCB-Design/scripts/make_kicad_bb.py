"""
KiCad 7 placement of the symmetric building block, built from the same geometry as the Q3D model.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\make_kicad_bb.py

Writes hardware/spb-building-block/spb-building-block.kicad_pcb (+ .kicad_pro). This is a PLACEMENT drawing: copper of all four layers is drawn as the
graphic shapes used in Q3D (L1 strips and cell islands, L2 DC-, L3 DC+, L4 AC) with the via rows; footprints are
placed but not netted or routed. Do not fabricate.
"""
import os
import shutil
import sys

KI = "C:/Program Files/KiCad/7.0/share/kicad"
os.environ.setdefault("KICAD7_3DMODEL_DIR", KI + "/3dmodels")
import pcbnew  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "simulation", "bb_q3d"))
import bb_geometry as geo  # noqa: E402

OUT = os.path.join(ROOT, "hardware", "spb-building-block")
MOD = os.path.join(OUT, "models")
os.makedirs(MOD, exist_ok=True)
NAME = "spb-building-block"
P8 = os.path.join(ROOT, "hardware", "epc2361-prototype-p8-placement", "models")
shutil.copy(os.path.join(P8, "EPC2361-envelope.wrl"), MOD)
MM = pcbnew.FromMM
FP = KI + "/footprints/"


def vec(x, y):
    # KiCad y axis points down; the geometry y axis also points "down" the loop, keep it as is
    return pcbnew.VECTOR2I(MM(x), MM(y))


def box_wrl(path, sx, sy, sz, rgb):
    """VRML 2 box (mm -> KiCad 3D units of 0.1 inch: /2.54) sitting on z = 0."""
    hx, hy, hz = sx / 2 / 2.54, sy / 2 / 2.54, sz / 2.54
    pts = [(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0), (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    with open(path, "w") as f:
        f.write("#VRML V2.0 utf8\nShape { appearance Appearance { material Material { diffuseColor %g %g %g } }\n" % rgb)
        f.write(" geometry IndexedFaceSet { coord Coordinate { point [ %s ] }\n" % ", ".join("%g %g %g" % p for p in pts))
        f.write("  coordIndex [ %s ] } }\n" % ", ".join("%d, %d, %d, %d, -1" % q for q in faces))


box_wrl(os.path.join(MOD, "2EDF7275K-envelope.wrl"), 5.0, 5.0, 1.0, (0.1, 0.1, 0.12))   # PG-TFLGA-13-4, 5 x 5 mm

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(1.6))
G = geo.build()
P, Y = G["params"], G["rows"]
XE = P["x_edge"]
# Insulation to the motor housing / cold plate (each submodule floats at up to the full stack voltage):
# EDGE_PB is a copper-free margin added AROUND the Q3D copper (the outline grows, the copper and the extracted
# parasitics stay unchanged). Required value depends on the insulation concept (insulating TIM overhang, coating,
# laminate CTI; IEC 60664-1/-3) and is a design parameter here.
EDGE_PB = 1.5
TZ = 10.0                                       # DC terminal zone above the capacitor bank (busbar interface)
TAB = 13.0                                      # tab below the cells: AC terminal, FFC connector, mounting holes
XO = XE + EDGE_PB                               # outline half width
YT = Y["p1"][0] - TZ                            # top of the DC terminal zone copper
Y0, Y1 = YT - EDGE_PB, Y["t_ac"][1] + TAB

LAYER = {"L1": pcbnew.F_Cu, "L2": pcbnew.In1_Cu, "L3": pcbnew.In2_Cu, "L4": pcbnew.B_Cu}


def rect(layer, x0, x1, y0, y1, fill=True, width=0.0):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(vec(x0, y0))
    s.SetEnd(vec(x1, y1))
    s.SetLayer(layer)
    s.SetFilled(fill)
    s.SetWidth(MM(width))
    board.Add(s)


def text(s, x, y, size=0.8, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(vec(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    board.Add(t)


# outline
rect(pcbnew.Edge_Cuts, -XO, XO, Y0, Y1, fill=False, width=0.1)

# copper of the Q3D geometry (graphic shapes, clipped to the outline)
for net, name, layer, x0, x1, y0, y1 in G["boxes"]:
    if layer in LAYER:
        rect(LAYER[layer], max(x0, -XE), min(x1, XE), max(y0, Y0), min(y1, Y1))

# vias (through, 0.3 mm drill / 0.6 mm pad as in the Q3D model)
for net, x, y, to in G["vias"]:
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetDrill(MM(0.3))                   # via_r = 0.15 mm in the Q3D stack-up
    v.SetWidth(MM(0.6))
    board.Add(v)


def place(lib, name, ref, value, x, y, rot=0.0, model=None, model_scale=None):
    fp = pcbnew.FootprintLoad(lib, name)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(vec(x, y))
    fp.SetOrientationDegrees(rot)
    if model:
        fp.Models().clear()
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = model.replace("\\", "/")
        fp.Models().push_back(m)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)
    return fp


EPC_LIB = os.path.join(ROOT, "hardware", "epc2361-cell", "epc2361-cell.pretty")
EPC_WRL = os.path.join(MOD, "EPC2361-envelope.wrl")
yqh, yql = sum(Y["qhd"]) / 2 + 1.0, sum(Y["qld"]) / 2 + 1.0       # body centres: drain row + 1 mm
for k, (side, s) in enumerate((("L", -1), ("R", 1))):
    rot = 180.0 if s < 0 else 0.0           # gate pads face the centre driver
    place(EPC_LIB, "EPC2361", "Q%d" % (k + 1), "EPC2361 (QH_%s)" % side, s * P["xc"], yqh, rot, EPC_WRL)
    place(EPC_LIB, "EPC2361", "Q%d" % (k + 3), "EPC2361 (QL_%s)" % side, s * P["xc"], yql, rot, EPC_WRL)
    for i in range(6):
        x = s * P["xc"] + (i - 2.5) * P["cap_p"]
        place(FP + "Capacitor_SMD.pretty", "C_0805_2012Metric", "C%d" % (1 + 6 * k + i), "1uF 100V X7S",
              x, (Y["capn"][0] + Y["capp"][1]) / 2, 90)
cid = 13
for g0 in (Y["p1"][1], Y["n1"][1], Y["p2"][1]):
    gc = g0 + P["gap"] / 2
    for s in (-1, 1):
        for xb in P["bank_x"]:
            place(FP + "Capacitor_SMD.pretty", "C_1210_3225Metric", "C%d" % cid, "10uF 100V X7S", s * xb, gc, 90)
            cid += 1

# centre driver: 2EDF7275K (dual-channel isolated, 4 A / 8 A, 4 V UVLO). Channel A drives the high-side gate star,
# channel B the low-side star; each output side is supplied by an isolated 6 V rail split into +5 V / -1 V around the
# Kelvin source (Zener + bleeder), see reports/gate-bump. PAD PATTERN IS A PLACEHOLDER: replace with the Infineon
# PG-TFLGA-13-4 land pattern before routing.
YD = 7.0                                   # driver centre: between the QH and QL gate rows (y = 4.9 / 9.2 mm)
drv = pcbnew.FOOTPRINT(board)
drv.SetReference("U1")
drv.SetValue("2EDF7275K")
lga = [(-2.0 + 1.0 * i, -2.0) for i in range(5)] + [(-2.0 + 1.0 * i, 2.0) for i in range(5)] + [(-2.0, 0), (0, 0), (2.0, 0)]
for k, (px, py) in enumerate(lga):
    pad = pcbnew.PAD(drv)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetLayerSet(pad.SMDMask())
    pad.SetSize(pcbnew.VECTOR2I(MM(0.5), MM(0.5)))
    pad.SetPosition(vec(px, py))
    pad.SetNumber(str(k + 1))
    drv.Add(pad)
m = pcbnew.FP_3DMODEL()
m.m_Filename = os.path.join(MOD, "2EDF7275K-envelope.wrl").replace("\\", "/")
drv.Models().push_back(m)
drv.SetPosition(vec(0, YD))
drv.Reference().SetVisible(False)
drv.Value().SetVisible(False)
board.Add(drv)
CAP, RES = FP + "Capacitor_SMD.pretty", FP + "Resistor_SMD.pretty"
DIO = FP + "Diode_SMD.pretty"
# per gate: Rg_on = 2 ohm with a Schottky diode across it (turn-off 0 ohm); high-side parts above the driver,
# low-side parts below, mirrored about the symmetry line
rid, did = 1, 1
for (side, s) in (("L", -1), ("R", 1)):
    for yg, tag in ((YD - 3.1, "QH"), (YD + 3.1, "QL")):
        place(RES, "R_0402_1005Metric", "R%d" % rid, "2R Rg_on (%s_%s)" % (tag, side), s * 2.2, yg, 0)
        place(DIO, "D_0402_1005Metric", "D%d" % did, "Schottky, Rg_off = 0 (%s_%s)" % (tag, side), s * 0.85, yg, 0)
        rid += 1
        did += 1
# split rails: +5 V (VDD-S) / -1 V (S-GND) decoupling, 5.1 V Zener VDD-S, bleeder S-GND, per channel
cid = 37
for ch, yr in (("A (HS, ref. SW)", YD - 4.6), ("B (LS, ref. DC-)", 12.3)):
    place(CAP, "C_0402_1005Metric", "C%d" % cid, "1uF +5V VDD%s" % ch[0], -2.1, yr, 0)
    place(CAP, "C_0402_1005Metric", "C%d" % (cid + 1), "1uF -1V GND%s" % ch[0], -0.7, yr, 0)
    place(DIO, "D_SOD-523", "D%d" % did, "5.1V Zener VDD%s-S" % ch[0], 0.7, yr, 0)
    place(RES, "R_0402_1005Metric", "R%d" % rid, "bleeder S-GND%s" % ch[0], 2.1, yr, 0)
    cid += 2
    did += 1
    rid += 1
place(CAP, "C_0402_1005Metric", "C%d" % cid, "100nF VDDI (3.3V)", 3.5, 12.3, 0)
place(FP + "Connector_FFC-FPC.pretty", "Molex_200528-0100_1x10-1MP_P1.00mm_Horizontal", "J4",
      "FFC 1:INA 2:INB 3:VDDI 4:GNDI 5:NTC 6:6V_B 7:GNDB(-1V,LS) 8:NC 9:6V_A 10:GNDA(SW-1V)", 8.6, Y["t_ac"][1] + 4.7, 180)
# temperature sensor on the DC- (source) copper next to QL_L, referenced to the low-side domain
place(RES, "R_0402_1005Metric", "RT1", "NTC 10k B3435 (QL_L source)", -10.9, 10.2, 90)
# insulated mounting: M2.5 NPTH in the signal tab, PEEK screws + insulating washers (do not use metal hardware to the
# grounded cold plate unless the keep-out equals the creepage distance)
HOLES = [(-(XO - 2.4), Y1 - 2.4), ((XO - 2.4), Y1 - 2.4), (-(XO - 2.4), Y0 + 2.4), ((XO - 2.4), Y0 + 2.4)]
for k, (hx, hy) in enumerate(HOLES):
    place(FP + "MountingHole.pretty", "MountingHole_2.7mm_M2.5", "H%d" % (k + 1), "M2.5 PEEK, insulated", hx, hy)

# ---------------- power I/O (outside the Q3D power stage; the extracted copper is unchanged) ----------------
# DC terminal zone: DC+ copper (x < 0) joins the L1 DC+ strip P1 and the L3 DC+ plane, DC- copper (x > 0) joins the
# L2 DC- plane through an L2 bridge under P1. Bottom-mounted REDCUBE THR terminals (internal M4 thread) take the
# screws of the axial laminated busbar of the cell. AC: larger REDCUBE in the tab, joined to the L4 AC plane.
ZONES = []
for lay in ("L1", "L2", "L3", "L4"):
    y_dcp = Y["p1"][0] if lay in ("L1", "L3") else Y["p1"][0] - 0.6
    ZONES.append(("DCP", lay, -11.0, -1.0, YT, y_dcp))
    ZONES.append(("DCN", lay, 1.0, 11.0, YT, Y["p1"][0] - 0.6 if lay != "L2" else Y["l2"][0]))
    ZONES.append(("AC", lay, -11.0, -0.8, Y["t_ac"][1] + 0.6 if lay != "L4" else Y["l4"][1], Y1 - EDGE_PB))
for net, lay, x0, x1, y0, y1 in ZONES:
    rect(LAYER[lay], x0, x1, y0, y1)
TB = FP + "TerminalBlock_Wuerth.pretty"
for ref, name, x, y, lab in (("J1", "Wuerth_REDCUBE-THR_WP-THRBU_74650174_THR", -6.0, YT + 4.6, "DC+ (REDCUBE THR M4)"),
                             ("J2", "Wuerth_REDCUBE-THR_WP-THRBU_74650174_THR", 6.0, YT + 4.6, "DC- (REDCUBE THR M4)"),
                             ("J3", "Wuerth_REDCUBE-THR_WP-THRBU_74650094_THR", -5.9, Y1 - 6.3, "AC phase (REDCUBE THR)")):
    fp = place(TB, name, ref, lab, x, y)
    fp.Flip(fp.GetPosition(), False)           # body on the bottom side (busbar / phase-lead side), pins through
for i, (x, y, lab) in enumerate(((-14.0, yql, "VDS_L"), (14.0, yql, "VDS_R"), (-14.0, yqh, "SW_L"), (14.0, yqh, "SW_R"))):
    place(FP + "TestPoint.pretty", "TestPoint_Pad_D1.0mm", "TP%d" % (i + 1), lab, x, y)

# silkscreen
text("insulated mounting (PEEK)", 0, Y1 - 0.6, 0.5)
text("DC+", -6.0, YT + 0.9, 0.7)
text("DC-", 6.0, YT + 0.9, 0.7)
text("AC", -5.9, Y1 - 0.9, 0.7)
text("QH", -12.6, yqh, 0.6)
text("QL", -12.6, yql, 0.6)
text("SPB building block  2x EPC2361 per switch  2EDF7275K +5/-1 V", 0, Y1 - 0.5, 0.6)

# ---------------- clearance report: copper (power nets, all layers) to the outline and to the mounting holes
def rect_dist(px, py, x0, x1, y0, y1):
    dx = max(x0 - px, 0, px - x1)
    dy = max(y0 - py, 0, py - y1)
    return (dx * dx + dy * dy) ** 0.5


cu = [(n, l, max(x0, -XE), min(x1, XE), y0, y1) for n, nm, l, x0, x1, y0, y1 in G["boxes"] if n and l in ("L1", "L2", "L3", "L4", "PAD", "PADB")]
cu += ZONES
d_edge = min(min(x0 + XO, XO - x1, y0 - Y0, Y1 - y1) for _, _, x0, x1, y0, y1 in cu)
d_hole = min(rect_dist(hx, hy, x0, x1, y0, y1) for hx, hy in HOLES for _, _, x0, x1, y0, y1 in cu) - 1.35
print("outline %.1f x %.1f mm; min copper-to-edge %.2f mm; min copper-to-hole-edge %.2f mm" % (2 * XO, Y1 - Y0, d_edge, d_hole))

path = os.path.join(OUT, NAME + ".kicad_pcb")
pcbnew.SaveBoard(path, board)
pro = os.path.join(OUT, NAME + ".kicad_pro")
if not os.path.exists(pro):
    open(pro, "w").write('{"meta": {"filename": "%s.kicad_pro", "version": 1}}\n' % NAME)
print("saved", path, "footprints:", len(board.GetFootprints()), "vias:", len(G["vias"]))

# 3D pictures: scripts/kicad_dump.py (KiCad python) + scripts/render_board.py (KiCad 7 cannot export VRML headless)

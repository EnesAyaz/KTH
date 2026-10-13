"""
Laminated PCB busbar: the common DC bus of one 75 V level, joining the three phase-leg boards (Rev B, spb-bb-revb).

The leg boards stand side by side (pitch 94.5 mm = 89.5 mm board + 5 mm gap). Their DC terminals (Wuerth REDCUBE
74650174, M4 through-thread, 7 x 7 mm, 6.5 mm high) are on the leg-board bottom side in one row at y = -18.8 mm:
DC+ at x = -29.75 / +17.75, DC- at x = -17.75 / +29.75 (leg-local). This strip lies under the three legs, its top face
on the twelve terminal faces, held by M4 x 8 screws from below (1.6 mm PCB + washer, ~5.5 mm thread engagement).

Stack-up (standard 4-layer 1.6 mm FR4, 2 oz on all layers; 3 oz optional), interleaved for low inductance:
    L1 DC+   | prepreg <= 0.2 mm |   L2 DC-   | core |   L3 DC+   | prepreg <= 0.2 mm |   L4 DC-
Each bolt pad is a plated M4 hole with a 10 mm pad on both outer layers (its own polarity) and a via ring; the
opposite-polarity planes clear it. Level-to-level (stack) connection: two M6 lug pads at the centre leg, so each outer
bus segment carries only one leg's DC current. Footprints for damped bulk capacitors (hybrid polymer, fit if ringing
is seen), a level-voltage header, nylon-standoff holes at the leg-board corner holes H3/H4, frame holes with an 8 mm
copper keep-out (the level sits up to 1200 V above the frame).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\make_kicad_busbar.py
      -> hardware/spb-busbar/spb-busbar.kicad_pcb (+ .kicad_pro, parts.json, drc_report.txt)
Coordinates: mm, y down, leg-local y (same as the leg board); x = 0 at the centre of the middle leg.
"""
import json
import math
import os

KI = "C:/Program Files/KiCad/7.0/share/kicad"
os.environ.setdefault("KICAD7_3DMODEL_DIR", KI + "/3dmodels")
os.environ.setdefault("KICAD7_FOOTPRINT_DIR", KI + "/footprints")
import pcbnew  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "spb-busbar"
OUT = os.path.join(ROOT, "hardware", NAME)
os.makedirs(OUT, exist_ok=True)
FP = KI + "/footprints/"
MM = pcbnew.FromMM

# ------------------------------------------------------------------ geometry
LEG_W, GAP = 89.5, 5.0
PITCH = LEG_W + GAP
LEGS = (-PITCH, 0.0, PITCH)                       # leg centres
TERM = ((-29.75, "DCP"), (-17.75, "DCN"), (17.75, "DCP"), (29.75, "DCN"))
YTERM = -18.8                                     # terminal row (leg-local)
LEG_Y0, LEG_Y1 = -24.4, 55.6                      # leg-board outline in y
LEG_HOLES = ((-42.35, -22.0), (42.35, -22.0))     # leg H3/H4 (nylon standoffs, 6.5 mm)
XB = PITCH + LEG_W / 2 + 10.0                     # strip half length (10 mm beyond the outer legs for frame holes)
YB0, YB1 = -49.0, -4.0                            # strip y range: outer edge .. inner edge (clears H5/H6 heads at y 0.2)
YLUG = -37.0
XLUG = 12.0
CU_UM, PP_MM = 70.0, 0.2                          # copper per layer (2 oz), prepreg L1-L2 / L3-L4
PULLBACK = 1.0
FRAME_KEEP = 8.0                                  # copper keep-out radius around frame holes (1200 V to frame)

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(1.6))
ds.m_MinClearance = MM(0.3)
ds.m_CopperEdgeClearance = MM(0.5)
ds.m_TrackMinWidth = MM(0.2)
ds.m_ViasMinSize = MM(0.6)
ds.m_MinThroughDrill = MM(0.3)
ncl = ds.m_NetSettings.m_DefaultNetClass
ncl.SetClearance(MM(0.5))
ncl.SetViaDiameter(MM(0.8))
ncl.SetViaDrill(MM(0.4))
F, L2, L3, B = pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu
PLANES = ((F, "DCP"), (L2, "DCN"), (L3, "DCP"), (B, "DCN"))

NETS = {}


def net(name):
    if name not in NETS:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        NETS[name] = n
    return NETS[name]


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def line(layer, pts, w=0.1):
    for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(a, b))
        s.SetEnd(V(c, d))
        s.SetLayer(layer)
        s.SetWidth(MM(w))
        board.Add(s)


def rect(layer, x0, y0, x1, y1, w=0.1):
    line(layer, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], w)


def text(s, x, y, size=1.5, layer=pcbnew.F_SilkS, mirror=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(V(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    t.SetMirrored(mirror)
    board.Add(t)


def zone(layer, n, pts, prio=0, clearance=0.5):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net(n))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(MM(x), MM(y))
    board.Add(z)


def keepout_circle(x, y, r):
    z = pcbnew.ZONE(board)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(4))
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ol = z.Outline()
    ol.NewOutline()
    for k in range(32):
        a = 2 * math.pi * k / 32
        ol.Append(MM(x + r * math.cos(a)), MM(y + r * math.sin(a)))
    board.Add(z)


PARTS = []
BOXES = []                                        # (x0, y0, x1, y1) keep stitching vias away


def add_part(fp, rf, value, x, y, rot=0.0, nets=None, mpn="", lib="spb_fab", bottom=False):
    fp.SetReference(rf)
    fp.SetValue(value)
    board.Add(fp)
    fp.SetPosition(V(x, y))
    fp.SetOrientationDegrees(rot)
    if bottom:
        fp.Flip(fp.GetPosition(), False)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    for pad in fp.Pads():
        if nets and pad.GetNumber() in nets:
            pad.SetNet(net(nets[pad.GetNumber()]))
    bb = fp.GetBoundingBox(False, False)
    BOXES.append((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()),
                  pcbnew.ToMM(bb.GetBottom())))
    PARTS.append(dict(ref=rf, value=value, footprint=fp.GetFPID().GetLibItemName().wx_str(), mpn=mpn, x=x, y=y,
                      rot=rot, side="bottom" if bottom else "top"))
    return fp


def tht_fp(name, pads, crt, descr):
    """pads: (number, x, y, size_x, size_y, drill, shape 'c' | 'rr')."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID("spb_fab", name))
    fp.SetDescription(descr)
    for num, x, y, w, h, drill, shape in pads:
        p = pcbnew.PAD(fp)
        p.SetNumber(num)
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetLayerSet(p.PTHMask())
        p.SetShape(pcbnew.PAD_SHAPE_CIRCLE if shape == "c" else pcbnew.PAD_SHAPE_ROUNDRECT)
        if shape == "rr":
            p.SetRoundRectRadiusRatio(0.1)
        p.SetSize(V(w, h))
        p.SetDrillSize(V(drill, drill))
        p.SetPos0(V(x, y))
        p.SetPosition(V(x, y))
        fp.Add(p)
    x0, y0, x1, y1 = crt
    for lay, wd in ((pcbnew.F_CrtYd, 0.05), (pcbnew.F_Fab, 0.1)):
        for (a, b), (c, d) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            sh = pcbnew.FP_SHAPE(fp)
            sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
            sh.SetStart0(V(a, b))
            sh.SetEnd0(V(c, d))
            sh.SetLayer(lay)
            sh.SetWidth(MM(wd))
            sh.SetDrawCoord()
            fp.Add(sh)
    return fp


def bolt_m4():
    """M4 bolt pad onto a REDCUBE face: 4.3 mm plated hole, 10 mm pad (covers the 7 x 7 mm face and a 9 mm washer),
    8 x 0.4 mm vias on r = 3.6 mm tie both same-polarity planes to the contact faces."""
    pads = [("1", 0, 0, 10.0, 10.0, 4.3, "c")]
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        pads.append(("1", 3.6 * math.cos(a), 3.6 * math.sin(a), 0.8, 0.8, 0.4, "c"))
    return tht_fp("BUS_M4_REDCUBE", pads, (-5.25, -5.25, 5.25, 5.25), "PCB busbar M4 bolt pad onto a REDCUBE face")


def lug_m6():
    """stack connection: 6.4 mm plated hole in an 18 x 18 mm pad, via field (0.4 mm, 1.5 mm pitch) for the inner layers."""
    pads = [("1", 0, 0, 18.0, 18.0, 6.4, "rr")]
    n = 0
    for i in range(-5, 6):
        for j in range(-5, 6):
            x, y = 1.5 * i, 1.5 * j
            if math.hypot(x, y) >= 4.7:
                pads.append(("1", x, y, 0.8, 0.8, 0.4, "c"))
                n += 1
    return tht_fp("BUS_LUG_M6", pads, (-9.25, -9.25, 9.25, 9.25), "PCB busbar M6 lug pad, %d vias" % n), n


def hole(x, y, d, keep=None):
    fp = pcbnew.FootprintLoad(FP + "MountingHole.pretty", "MountingHole_3.2mm_M3" if d > 3 else "MountingHole_2.7mm_M2.5")
    fp.SetFPID(pcbnew.LIB_ID("MountingHole", fp.GetFPID().GetLibItemName().wx_str()))
    return fp


# ------------------------------------------------------------------ outline, leg outlines (reference)
rect(pcbnew.Edge_Cuts, -XB, YB0, XB, YB1)
for k, xl in enumerate(LEGS):
    rect(pcbnew.Dwgs_User, xl - LEG_W / 2, LEG_Y0, xl + LEG_W / 2, LEG_Y1, 0.15)
    text("LEG %d (phase %s) above" % (k + 1, "abc"[k]), xl, 15.0, 2.0, pcbnew.Dwgs_User)

# ------------------------------------------------------------------ planes
for lay, n in PLANES:
    p = PULLBACK
    zone(lay, n, [(-XB + p, YB0 + p), (XB - p, YB0 + p), (XB - p, YB1 - p), (-XB + p, YB1 - p)])

# ------------------------------------------------------------------ leg terminals
CNT = {"J": 0, "H": 0, "C": 0}


def ref(pre):
    CNT[pre] += 1
    return "%s%d" % (pre, CNT[pre])


for k, xl in enumerate(LEGS):
    for xt, n in TERM:
        x = xl + xt
        add_part(bolt_m4(), ref("J"), "LEG%d %s" % (k + 1, "DC+" if n == "DCP" else "DC-"), x, YTERM,
                 nets={"1": n}, mpn="M4 x 8 screw + washer into REDCUBE 74650174")
        for lay, mir in ((pcbnew.F_SilkS, False), (pcbnew.B_SilkS, True)):
            text("+" if n == "DCP" else "-", x, YTERM + 7.0, 2.5, lay, mir)
    for hx, hy in LEG_HOLES:
        fp = hole(xl + hx, hy, 2.7)
        add_part(fp, ref("H"), "nylon M2.5 standoff 6.5 mm (leg H3/H4)", xl + hx, hy)

# ------------------------------------------------------------------ stack connection, damping, sense header
lugfp, nlugv = lug_m6()
add_part(lugfp, ref("J"), "STACK DC+ (to level above: its DC-)", -XLUG, YLUG, nets={"1": "DCP"},
         mpn="M6 ring lug / Cu braid, both faces clamped")
add_part(lug_m6()[0], ref("J"), "STACK DC- (to level below: its DC+)", XLUG, YLUG, nets={"1": "DCN"},
         mpn="M6 ring lug / Cu braid, both faces clamped")
for lay, mir in ((pcbnew.F_SilkS, False), (pcbnew.B_SilkS, True)):
    text("STACK +", -XLUG, YLUG + 10.8, 1.8, lay, mir)
    text("STACK -", XLUG, YLUG + 10.8, 1.8, lay, mir)
    text("75 V LEVEL BUS - CHECK POLARITY BEFORE BOLTING", 0, -6.5, 1.3, lay, mir)

hdr = pcbnew.FootprintLoad(FP + "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical")
hdr.SetFPID(pcbnew.LIB_ID("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical"))
add_part(hdr, ref("J"), "LEVEL V: 1 DC+, 2 DC- (HV referenced)", 0.0, YLUG - 2.0, nets={"1": "DCP", "2": "DCN"},
         mpn="2.54 mm header 1x2")

DAMP_X = (-46.0, -32.0, 32.0, 46.0)
for x in DAMP_X:
    fp = pcbnew.FootprintLoad(FP + "Capacitor_SMD.pretty", "CP_Elec_10x10.5")
    fp.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", "CP_Elec_10x10.5"))
    add_part(fp, ref("C"), "DNP: 100 V hybrid polymer ~20-30 mOhm ESR (damping, fit if ringing)", x, YLUG, 90.0,
             nets={"1": "DCP", "2": "DCN"}, mpn="select: 100 V hybrid polymer, 10 x 10.5 mm SMD")
    p2 = [p for p in fp.Pads() if p.GetNumber() == "2"][0]
    cx, cy = pcbnew.ToMM(p2.GetPosition().x), pcbnew.ToMM(p2.GetPosition().y)
    # DC- island on L1 under/beyond pad 2, tied to L2/L4 by a via row beyond the pad
    oy = 1 if cy > YLUG else -1
    y_far = cy + oy * 4.0
    zone(F, "DCN", [(cx - 2.6, cy - oy * 2.0), (cx + 2.6, cy - oy * 2.0), (cx + 2.6, y_far + oy * 1.0),
                    (cx - 2.6, y_far + oy * 1.0)], prio=1)
    for vx in (-1.6, 0.0, 1.6):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(V(cx + vx, y_far))
        v.SetWidth(MM(0.8))
        v.SetDrill(MM(0.4))
        v.SetNet(net("DCN"))
        v.SetIsFree(True)
        board.Add(v)
    BOXES.append((cx - 3.0, min(cy, y_far) - 3.0, cx + 3.0, max(cy, y_far) + 3.0))

# ------------------------------------------------------------------ frame holes (chassis potential)
for sx in (-1, 1):
    for y in (-12.0, -41.0):
        x = sx * (XB - 5.0)
        add_part(hole(x, y, 3.2), ref("H"), "M3 insulating standoff to frame (8 mm Cu keep-out)", x, y)
        keepout_circle(x, y, FRAME_KEEP)
        BOXES.append((x - FRAME_KEEP - 1, y - FRAME_KEEP - 1, x + FRAME_KEEP + 1, y + FRAME_KEEP + 1))
for xl in LEGS:
    for hx, hy in LEG_HOLES:
        BOXES.append((xl + hx - 3.0, hy - 3.0, xl + hx + 3.0, hy + 3.0))

# ------------------------------------------------------------------ stitching vias (tie L1-L3 and L2-L4 across the strip)
nst = 0
for i, x in enumerate([-XB + 4.0 + 4.0 * k for k in range(int((2 * XB - 8.0) / 4.0) + 1)]):
    for j, y in enumerate((-45.5, -41.5, -33.5, -29.5, -26.0, -12.0, -8.0)):
        if any(a - 1.0 <= x <= c + 1.0 and b - 1.0 <= y <= d + 1.0 for a, b, c, d in BOXES):
            continue
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(V(x, y))
        v.SetWidth(MM(0.8))
        v.SetDrill(MM(0.4))
        v.SetNet(net("DCP" if (i + j) % 2 == 0 else "DCN"))
        v.SetIsFree(True)
        board.Add(v)
        nst += 1

# ------------------------------------------------------------------ notes on the fab layer
notes = ["4 layers, 1.6 mm FR4, 70 um (2 oz) Cu on ALL layers (3 oz optional), ENIG",
         "L1 DC+ / prepreg <= 0.2 mm / L2 DC- / core / L3 DC+ / prepreg <= 0.2 mm / L4 DC-",
         "top face (L1) faces the leg boards; M4 x 8 screws from the bottom; bolt pads bare (no mask)",
         "frame holes: insulating standoffs, 8 mm Cu keep-out; nylon M2.5 x 6.5 mm at the leg H3/H4 holes"]
for k, s in enumerate(notes):
    text(s, 0.0, YB0 - 4.0 - 2.5 * k, 1.5, pcbnew.Cmts_User)

# ------------------------------------------------------------------ estimates
mu0 = 4e-7 * math.pi
w = (YB1 - YB0 - 2 * PULLBACK) * 1e-3
seg = PITCH * 1e-3
L_seg = mu0 * (PP_MM * 1e-3 / 2) * seg / w                     # two coupled pairs in parallel
R_seg = 1.72e-8 * seg / (w * 2 * CU_UM * 1e-6)                 # per polarity, two layers
I_leg = 300e3 / 16 / 3 / 75.0
P_bus = 4 * I_leg ** 2 * R_seg
EST = dict(L_leg_to_leg_nH=L_seg * 1e9, R_seg_per_polarity_mOhm=R_seg * 1e3, I_leg_dc_A=I_leg,
           P_bus_W=P_bus, width_mm=w * 1e3, length_mm=2 * XB, lug_vias=nlugv, stitch_vias=nst)
print("estimates:", {k: round(v, 3) for k, v in EST.items()}, flush=True)

# ------------------------------------------------------------------ save, fill, DRC
OX, OY = 160.0, 80.0
mv = V(OX, OY)
for it in list(board.GetDrawings()) + list(board.GetTracks()) + list(board.GetFootprints()) + list(board.Zones()):
    it.Move(mv)
ds.SetAuxOrigin(V(OX - XB, OY + YB1))
path = os.path.join(OUT, NAME + ".kicad_pcb")
pcbnew.SaveBoard(path, board)
json.dump({"board": {"design_settings": {"rule_severities": {
    "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore", "silk_over_copper": "warning",
    "silk_overlap": "warning", "silk_edge_clearance": "warning"}}},
    "meta": {"filename": NAME + ".kicad_pro", "version": 1}}, open(os.path.join(OUT, NAME + ".kicad_pro"), "w"), indent=1)
json.dump(PARTS, open(os.path.join(OUT, "parts.json"), "w"), indent=1)
json.dump(EST, open(os.path.join(OUT, "estimates.json"), "w"), indent=1)
open(os.path.join(OUT, "fp-lib-table"), "w").write(
    '(fp_lib_table\n  (lib (name "spb_fab")(type "KiCad")(uri "${KIPRJMOD}/spb_fab.pretty")(options "")(descr "busbar pads"))\n)\n')
lib = os.path.join(OUT, "spb_fab.pretty")
os.makedirs(lib, exist_ok=True)
for fp in board.GetFootprints():
    nm = fp.GetFPID().GetLibItemName().wx_str()
    if nm.startswith("BUS_"):
        pcbnew.FootprintSave(lib, fp)
board2 = pcbnew.LoadBoard(path)
board2.BuildConnectivity()
pcbnew.ZONE_FILLER(board2).Fill(board2.Zones())
pcbnew.SaveBoard(path, board2)
pcbnew.WriteDRCReport(board2, os.path.join(OUT, "drc_report.txt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
print("saved", path, "footprints", len(board.GetFootprints()), "outline %.1f x %.1f mm" % (2 * XB, YB1 - YB0))

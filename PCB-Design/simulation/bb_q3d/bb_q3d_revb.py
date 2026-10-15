# -*- coding: utf-8 -*-
"""
Q3D power model of the ROUTED Rev B leg board (BB_PL_REVB: 4 x EPC2361 per switch, UFCS shunt per cell), built
from results/revb_geometry.json (revb_export.py <- hardware/spb-bb-revb-dpt | -load, REVB_BOARD).

    simulation\\bb_q3d\\run_bb_q3d_revb.cmd     (KTH licence)  -> results/BB_PL_REVB_matrix.txt, _terminals.txt
    post: revb_post.py (commutation loop per cell incl. the shunt; three legs + PCB busbar network)

Same stack-up and setup as BB_PL_FAB (bb_q3d_fab.py), all copper layers 70 um. Nets DCP, DCN, AC, LSRC1..4;
REDCUBE DC/AC terminals are 7 x 7 mm blocks on the bottom (pad side "bottom") with their press-in pins as vias.
Copper polygons are swept sheets with their clearance holes; FET stripes and capacitor pads are boxes from L1 up
to the pad top (terminal faces); vias are through cylinders.
"""
import json
import os
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
OUT = os.path.join(HERE, "results")
REGION = os.environ.get("REVB_REGION", "")   # "" full board | loop (cell band) | lx (cells + AC bus) | bank (DC link)
LOOP = REGION == "loop"                                # fast loop-only model (cell band, bypass, shunts)
VT = os.environ.get("REVB_LOOP_TAG", "")              # board / variant tag (file names)
SFX = ("_" + VT) if VT else ""
KIND = {"loop": "LOOP", "lx": "LX", "bank": "BANK"}.get(REGION, "REVB")
TAG = "BB_PL_" + KIND + SFX
DCONLY = os.environ.get("REVB_SOLVE", "") == "dc"     # full board: DC R/L only (sharing, loss, low-f port matrix)
LOG = open(os.path.join(OUT, "%s_log%s.txt" % (KIND.lower(), SFX)), "w")


def log(m):
    LOG.write(str(m) + "\n")
    LOG.flush()


import traceback
G = json.load(open(os.path.join(OUT, {"loop": "revb_loop_geometry", "lx": "revb_lx_geometry",
                                      "bank": "revb_bank_geometry"}.get(REGION, "revb_geometry")
                                + SFX + ".json")))
ERR = float(os.environ.get("REVB_PERERROR", "2"))     # % convergence for DC and AC (1 % took > 3 h on 4 cores)
# optional thinning of the AC-bus via grid (y > 30 mm, far from the commutation loops) to limit the mesh size
EVERY = int(os.environ.get("REVB_AC_VIA_EVERY", "1"))
_bus = [v for v in G["vias"] if v[0] == "AC" and v[2] > 30.0]
G["vias"] = [v for v in G["vias"] if not (v[0] == "AC" and v[2] > 30.0)] + _bus[::EVERY]
log("geometry loaded: %d polys, %d vias (AC bus vias every %d)" % (len(G["polys"]), len(G["vias"]), EVERY))
STACK = [("h_diel", 0.100), ("h_23", 1.200), ("h_34", 0.100), ("t_L1", 0.070), ("t_L2", 0.070),
         ("t_L3", 0.070), ("t_L4", 0.070), ("t_pad", 0.035)]
Z = dict(STACK)
Z["z_L1"] = Z["t_L2"] + Z["h_diel"]
Z["z_top"] = Z["z_L1"] + Z["t_L1"]
Z["z_L3t"] = -Z["h_23"]
Z["z_L3b"] = -Z["h_23"] - Z["t_L3"]
Z["z_L4t"] = Z["z_L3b"] - Z["h_34"]
Z["z_L4b"] = Z["z_L4t"] - Z["t_L4"]
ZR = {"L1": (Z["z_L1"], Z["z_top"]), "L2": (0.0, Z["t_L2"]), "L3": (Z["z_L3b"], Z["z_L3t"]),
      "L4": (Z["z_L4b"], Z["z_L4t"])}

try:
    oProject = oDesktop.NewProject()
    log("project new")
    oProject.Rename(os.path.join(OUT, "bb_q3d_%s%s.aedt" % (KIND.lower(), SFX)), True)
    log("project renamed")
    oProject.InsertDesign("Q3D Extractor", TAG, "", "")
    oDesign = oProject.SetActiveDesign(TAG)
    ed = oDesign.SetActiveEditor("3D Modeler")
    bnd = oDesign.GetModule("BoundarySetup")
    log("design ready")
except Exception:
    log(traceback.format_exc())
    raise


def mm(v):
    return "%.4fmm" % v


def attrs(name):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", "(255 128 64)", "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global", "UDMId:=", "", "MaterialValue:=", "\"copper\"",
            "SurfaceMaterialValue:=", "\"\"", "SolveInside:=", True, "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False, "IsLightweight:=", False]


N = [0]


def sheet(pts, z, name):
    pp = ["NAME:PolylinePoints"]
    ring = list(pts) + [pts[0]]
    for x, y in ring:
        pp.append(["NAME:PLPoint", "X:=", mm(x), "Y:=", mm(y), "Z:=", mm(z)])
    seg = ["NAME:PolylineSegments"]
    for i in range(len(ring) - 1):
        seg.append(["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", i, "NoOfPoints:=", 2])
    ed.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, pp, seg,
                       ["NAME:PolylineXSection", "XSectionType:=", "None", "XSectionOrient:=", "Auto",
                        "XSectionWidth:=", "0mm", "XSectionTopWidth:=", "0mm", "XSectionHeight:=", "0mm",
                        "XSectionNumSegments:=", "0", "XSectionBendType:=", "Corner"]], attrs(name))
    return name


NETOBJ = {}


def add(net, name):
    NETOBJ.setdefault(net, []).append(name)


def build_polys():
  for k, (net, layer, outl, holes) in enumerate(G["polys"]):
    z0, z1 = ZR[layer]
    name = "P%d_%s_%s" % (k, net, layer)
    log("poly %d start %s %s pts %d holes %d first %r" % (k, net, layer, len(outl), len(holes), outl[:3]))
    sheet(outl, z0, name)
    if holes:
        hn = []
        for j, h in enumerate(holes):
            hn.append(sheet(h, z0, "%s_h%d" % (name, j)))
        ed.Subtract(["NAME:Selections", "Blank Parts:=", name, "Tool Parts:=", ",".join(hn)],
                    ["NAME:SubtractParameters", "KeepOriginals:=", False])
    ed.SweepAlongVector(["NAME:Selections", "Selections:=", name, "NewPartsModelFlag:=", "Model"],
                        ["NAME:VectorSweepParameters", "DraftAngle:=", "0deg", "DraftType:=", "Round",
                         "CheckFaceFaceIntersection:=", False, "SweepVectorX:=", "0mm", "SweepVectorY:=", "0mm",
                         "SweepVectorZ:=", mm(z1 - z0)])
    add(net, name)
    log("poly %d ok (%d pts, %d holes)" % (k, len(outl), len(holes)))


try:
    build_polys()
except Exception:
    log(traceback.format_exc())
    raise
log("polys done")
for k, v_ in enumerate(G["vias"]):
    net, x, y, r = v_[:4]
    za, zb = (ZR[v_[5]][0], ZR[v_[4]][1]) if len(v_) > 5 else (Z["z_L4b"], Z["z_top"])     # blind vias: own span
    name = "V%d_%s" % (k, net)
    ed.CreateCylinder(["NAME:CylinderParameters", "XCenter:=", mm(x), "YCenter:=", mm(y), "ZCenter:=", mm(za),
                       "Radius:=", mm(max(r, 0.15)), "Height:=", mm(zb - za), "WhichAxis:=", "Z",
                       "NumSides:=", "0"], attrs(name))
    add(net, name)
log("vias done")
for net, name, x0, x1, y0, y1, side in G["pads"]:
    if side == "bottom":
        z0, z1 = Z["z_L4b"] - Z["t_pad"], Z["z_L4t"]
    else:
        z0, z1 = Z["z_L1"], Z["z_top"] + Z["t_pad"]
    ed.CreateBox(["NAME:BoxParameters", "XPosition:=", mm(x0), "YPosition:=", mm(y0), "ZPosition:=", mm(z0),
                  "XSize:=", mm(x1 - x0), "YSize:=", mm(y1 - y0), "ZSize:=", mm(z1 - z0)], attrs(name))
    add(net, name)
log("pads done")
BODY = {}


def _diag(obj):
    pts = [[float(v) for v in ed.GetVertexPosition(vid)] for vid in ed.GetVertexIDsFromObject(obj)]
    if not pts:
        return 0.0
    return ((max(p[0] for p in pts) - min(p[0] for p in pts)) ** 2 + (max(p[1] for p in pts) - min(p[1] for p in pts)) ** 2) ** 0.5


for net, objs in NETOBJ.items():
    ed.Unite(["NAME:Selections", "Selections:=", ",".join(objs)], ["NAME:UniteParameters", "KeepOriginals:=", False])
    # separate lumps; floating pieces (cropped copper, lone vias) are deleted, the main conductor is kept
    before = set(ed.GetObjectsInGroup("Solids"))
    ed.SeparateBody(["NAME:Selections", "Selections:=", objs[0], "NewPartsModelFlag:=", "Model"],
                    ["CreateGroupsForNewObjects:=", False])
    lumps = sorted(([objs[0]] + sorted(set(ed.GetObjectsInGroup("Solids")) - before)), key=_diag, reverse=True)
    small = [o for o in lumps[1:] if _diag(o) <= 3.0]
    big = [o for o in lumps if o not in small]
    if small:
        ed.Delete(["NAME:Selections", "Selections:=", ",".join(small)])
    if len(big) > 1:
        log("WARNING net %s has %d large lumps: %r" % (net, len(big), [(o, round(_diag(o), 1)) for o in big]))
        ed.Unite(["NAME:Selections", "Selections:=", ",".join(big)], ["NAME:UniteParameters", "KeepOriginals:=", False])
    log("net %s: %d lumps, %d deleted" % (net, len(lumps), len(small)))
    BODY[net] = big[0]
    bnd.AssignSignalNet(["NAME:" + net, "Objects:=", [big[0]]])
log("united: %r" % BODY)
sinks, sources = {}, {}
for kind, name, net, pts, side in sorted(G["terminals"], key=lambda t: t[0] != "Source"):
    z = Z["z_top"] + Z["t_pad"] if side == "top" else Z["z_L4b"] - Z["t_pad"]
    faces = [ed.GetFaceByPosition(["NAME:FaceParameters", "BodyName:=", BODY[net], "XPosition:=", mm(x),
                                   "YPosition:=", mm(y), "ZPosition:=", mm(z)]) for x, y in pts]
    getattr(bnd, "Assign" + kind)(["NAME:" + name, "Faces:=", faces, "TerminalType:=", "ConstantVoltage",
                                   "Net:=", net])
    if kind == "Sink":
        sinks[net] = name
    else:
        sources.setdefault(net, []).append(name)
log("terminals assigned")
# DC: resistance only everywhere (the DC inductance solve ran > 19 h on the DPT loop model and is not needed:
# loop / lx use the 100 MHz AC matrix, the bank model the 1 MHz AC matrix, the full board only R)
LIGHT = REGION in ("loop", "lx", "bank")               # DC only as a coarse by-product
FREQ = "1MHz" if REGION == "bank" else "100MHz"
SETUP = ["NAME:Setup1", "AdaptiveFreq:=", FREQ, "SaveFields:=", False, "Enabled:=", True,
         ["NAME:Cap", "MaxPass:=", 1, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 30, "PerRefine:=", 30,
          "AutoIncreaseSolutionOrder:=", True, "SolutionOrder:=", "High", "Solver Type:=", "Iterative"],
         ["NAME:DC", "SolveResOnly:=", True,
          ["NAME:Cond", "MaxPass:=", 3 if LIGHT else 10, "MinPass:=", 1, "MinConvPass:=", 1,
           "PerError:=", 5 if LIGHT else ERR, "PerRefine:=", 30],
          "Solution Order:=", "Normal"]]
if not DCONLY:
    SETUP.append(["NAME:AC", "MaxPass:=", 8, "MinPass:=", 2, "MinConvPass:=", 1, "PerError:=", ERR, "PerRefine:=", 30,
                  "Solution Order:=", "High"])
log("setup: %s, DC only %r" % (KIND, DCONLY))
oDesign.GetModule("AnalysisSetup").InsertSetup("Matrix", SETUP)
try:
    log("validate: %r" % oDesign.ValidateDesign())
    oProject.Save()
    oDesign.Analyze("Setup1")
    oDesign.ExportMatrixData(os.path.join(OUT, TAG + "_matrix.txt"), "C, DC RL" if DCONLY else "C, DC RL, AC RL", "", "Setup1:LastAdaptive",
                             "Original", "ohm", "nH", "pF", "mSie", 100000000, "Maxwell,Spice,Couple", 0, False, 15,
                             20, 1)
    f = open(os.path.join(OUT, TAG + "_terminals.txt"), "w")
    for net in sorted(sinks):
        f.write("%s %s %s\n" % (net, sinks[net], " ".join(sources.get(net, []))))
    f.write("# stack: %s\n" % ", ".join("%s=%g" % kv for kv in sorted(Z.items())))
    f.close()
    log(TAG + ": exported")
except Exception as e:
    log("FAILED %r" % e)
    try:
        for m in oDesktop.GetMessages(oProject.GetName(), TAG, 0):
            log("MSG " + str(m))
    except Exception:
        pass
oProject.Save()
LOG.close()

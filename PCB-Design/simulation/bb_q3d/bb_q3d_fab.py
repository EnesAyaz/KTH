# -*- coding: utf-8 -*-
"""
Q3D power-loop model of the ROUTED fabrication board (BB_PL_FAB), built from results/fab_geometry.json
(written by fab_export.py from hardware/spb-bb-fab/spb-bb-fab.kicad_pcb).

    simulation\\bb_q3d\\run_bb_q3d_fab.cmd      (KTH licence)  -> results/BB_PL_FAB_matrix.txt, _terminals.txt

Same stack-up variables, terminal names, setup and export as BB_PL (bb_q3d.py), with all copper layers 70 um
as on the fabrication board, so bb_to_spice.py evaluates the commutation loop with the same definition.
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
LOG = open(os.path.join(OUT, "fab_log.txt"), "w")


def log(m):
    LOG.write(str(m) + "\n")
    LOG.flush()


import traceback
G = json.load(open(os.path.join(OUT, "fab_geometry.json")))
log("geometry loaded: %d polys" % len(G["polys"]))
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
    oProject.Rename(os.path.join(OUT, "bb_q3d_fab.aedt"), True)
    log("project renamed")
    oProject.InsertDesign("Q3D Extractor", "BB_PL_FAB", "", "")
    oDesign = oProject.SetActiveDesign("BB_PL_FAB")
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
for k, (net, x, y, r) in enumerate(G["vias"]):
    name = "V%d_%s" % (k, net)
    ed.CreateCylinder(["NAME:CylinderParameters", "XCenter:=", mm(x), "YCenter:=", mm(y), "ZCenter:=", mm(Z["z_L4b"]),
                       "Radius:=", mm(max(r, 0.15)), "Height:=", mm(Z["z_top"] - Z["z_L4b"]), "WhichAxis:=", "Z",
                       "NumSides:=", "0"], attrs(name))
    add(net, name)
log("vias done")
for net, name, x0, x1, y0, y1 in G["pads"]:
    if name == "T_AC":
        z0, z1 = Z["z_L4b"] - Z["t_pad"], Z["z_L4t"]
    else:
        z0, z1 = Z["z_L1"], Z["z_top"] + Z["t_pad"]
    ed.CreateBox(["NAME:BoxParameters", "XPosition:=", mm(x0), "YPosition:=", mm(y0), "ZPosition:=", mm(z0),
                  "XSize:=", mm(x1 - x0), "YSize:=", mm(y1 - y0), "ZSize:=", mm(z1 - z0)], attrs(name))
    add(net, name)
log("pads done")
BODY = {}
for net, objs in NETOBJ.items():
    ed.Unite(["NAME:Selections", "Selections:=", ",".join(objs)], ["NAME:UniteParameters", "KeepOriginals:=", False])
    BODY[net] = objs[0]
    bnd.AssignSignalNet(["NAME:" + net, "Objects:=", [objs[0]]])
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
oDesign.GetModule("AnalysisSetup").InsertSetup("Matrix", [
    "NAME:Setup1", "AdaptiveFreq:=", "100MHz", "SaveFields:=", False, "Enabled:=", True,
    ["NAME:Cap", "MaxPass:=", 4, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 5, "PerRefine:=", 30,
     "AutoIncreaseSolutionOrder:=", True, "SolutionOrder:=", "High", "Solver Type:=", "Iterative"],
    ["NAME:DC", "SolveResOnly:=", False,
     ["NAME:Cond", "MaxPass:=", 10, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
     ["NAME:Mult", "MaxPass:=", 1, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
     "Solution Order:=", "Normal"],
    ["NAME:AC", "MaxPass:=", 12, "MinPass:=", 2, "MinConvPass:=", 2, "PerError:=", 1, "PerRefine:=", 30,
     "Solution Order:=", "High"]])
try:
    log("validate: %r" % oDesign.ValidateDesign())
    oProject.Save()
    oDesign.Analyze("Setup1")
    oDesign.ExportMatrixData(os.path.join(OUT, "BB_PL_FAB_matrix.txt"), "C, DC RL, AC RL", "", "Setup1:LastAdaptive",
                             "Original", "ohm", "nH", "pF", "mSie", 100000000, "Maxwell,Spice,Couple", 0, False, 15,
                             20, 1)
    f = open(os.path.join(OUT, "BB_PL_FAB_terminals.txt"), "w")
    for net in sorted(sinks):
        f.write("%s %s %s\n" % (net, sinks[net], " ".join(sources.get(net, []))))
    f.write("# stack: %s\n" % ", ".join("%s=%g" % kv for kv in sorted(Z.items())))
    f.close()
    log("BB_PL_FAB: exported")
except Exception as e:
    log("FAILED %r" % e)
    try:
        for m in oDesktop.GetMessages(oProject.GetName(), "BB_PL_FAB", 0):
            log("MSG " + str(m))
    except Exception:
        pass
oProject.Save()
LOG.close()

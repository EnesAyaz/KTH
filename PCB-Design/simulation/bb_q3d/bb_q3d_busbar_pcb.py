# -*- coding: utf-8 -*-
"""
Q3D extraction of the PCB busbar of one 75 V level (BB_BUS_PCB), built from results/busbar_pcb_geometry.json
(busbar_pcb_export.py <- hardware/spb-busbar/spb-busbar.kicad_pcb).

    simulation\\bb_q3d\\run_bb_q3d_revb.cmd   (KTH licence)  -> results/BB_BUS_PCB_matrix.txt; post: revb_post.py

Model: four plane sheets (L1 DCP, L2 DCN, L3 DCP, L4 DCN, CU_UM thick) with antipads around every opposite-polarity
bolt pad, lug and via, and the frame keep-outs; bolt pads = pad discs on L1 and L4 + the 8-via ring; lugs = solid
18 x 18 mm blocks through the board (pad + 92 vias); stitching vias tie L1-L3 and L2-L4.
Terminals: sources on the 7 x 7 mm REDCUBE contact faces on top of L1 (L<leg>_J1/J2/J12/J13, names as on the leg
board), sinks on the lug tops (LUG_P, LUG_N).
"""
import json
import os
import traceback
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
OUT = os.path.join(HERE, "results")
LOG = open(os.path.join(OUT, "busbar_pcb_log.txt"), "w")


def log(m):
    LOG.write(str(m) + "\n")
    LOG.flush()


G = json.load(open(os.path.join(OUT, "busbar_pcb_geometry.json")))
# optional thinning of the stitching vias (mesh size): keep every n-th via (BUS_STITCH_EVERY, default all)
EVERY = int(os.environ.get("BUS_STITCH_EVERY", "1"))
G["vias"] = G["vias"][::EVERY]
CU = float(os.environ.get("BUS_CU_UM", "70")) / 1000.0
PP = 0.2
T = 1.6
CORE = T - 4 * CU - 2 * PP
# z ranges, L1 top = 0 (faces the leg boards), board below
ZR = {"L1": (-CU, 0.0)}
ZR["L2"] = (-2 * CU - PP, -CU - PP)
ZR["L3"] = (ZR["L2"][0] - CORE - CU, ZR["L2"][0] - CORE)
ZR["L4"] = (-T, -T + CU)
TPAD = 0.035
log("stack %r" % ZR)

oProject = oDesktop.NewProject()
oProject.Rename(os.path.join(OUT, "bb_q3d_busbar_pcb.aedt"), True)
oProject.InsertDesign("Q3D Extractor", "BB_BUS_PCB", "", "")
oDesign = oProject.SetActiveDesign("BB_BUS_PCB")
ed = oDesign.SetActiveEditor("3D Modeler")
bnd = oDesign.GetModule("BoundarySetup")


def mm(v):
    return "%.4fmm" % v


def attrs(name):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", "(220 120 60)", "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global", "UDMId:=", "", "MaterialValue:=", "\"copper\"",
            "SurfaceMaterialValue:=", "\"\"", "SolveInside:=", True, "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False, "IsLightweight:=", False]


def box(name, x0, x1, y0, y1, z0, z1):
    ed.CreateBox(["NAME:BoxParameters", "XPosition:=", mm(x0), "YPosition:=", mm(y0), "ZPosition:=", mm(z0),
                  "XSize:=", mm(x1 - x0), "YSize:=", mm(y1 - y0), "ZSize:=", mm(z1 - z0)], attrs(name))
    return name


def cyl(name, x, y, z0, z1, r):
    ed.CreateCylinder(["NAME:CylinderParameters", "XCenter:=", mm(x), "YCenter:=", mm(y), "ZCenter:=", mm(z0),
                       "Radius:=", mm(r), "Height:=", mm(z1 - z0), "WhichAxis:=", "Z", "NumSides:=", "0"],
                      attrs(name))
    return name


def subtract(blank, tools):
    for k in range(0, len(tools), 200):
        ed.Subtract(["NAME:Selections", "Blank Parts:=", blank, "Tool Parts:=", ",".join(tools[k:k + 200])],
                    ["NAME:SubtractParameters", "KeepOriginals:=", False])


def unite(objs):
    ed.Unite(["NAME:Selections", "Selections:=", ",".join(objs)], ["NAME:UniteParameters", "KeepOriginals:=", False])


N = [0]


def nm(p):
    N[0] += 1
    return "%s%d" % (p, N[0])


try:
    x0, y0, x1, y1 = G["outline"]
    pb, clr = G["pullback"], G["clearance"]
    OBJ = {"DCP": [], "DCN": []}
    for lay, net in G["planes"]:
        za, zb = ZR[lay]
        pl = box("PL_" + lay, x0 + pb, x1 - pb, y0 + pb, y1 - pb, za, zb)
        tools = []
        for name, n, x, y, d, hd in G["bolts"]:
            tools.append(cyl(nm("h"), x, y, za - 0.01, zb + 0.01, (d / 2 + clr) if n != net else hd / 2))
        for name, n, x, y, s, hd in G["lugs"]:
            if n != net:
                tools.append(box(nm("h"), x - s / 2 - clr, x + s / 2 + clr, y - s / 2 - clr, y + s / 2 + clr,
                                 za - 0.01, zb + 0.01))
        for n, x, y, r, pr in G["vias"]:
            if n != net:
                tools.append(cyl(nm("h"), x, y, za - 0.01, zb + 0.01, pr + clr))
        # frame keep-outs: the strip ends beyond the keep-out circles carry no current; cut them square so that
        # no copper slivers (separate lumps in Q3D, removed islands in KiCad) remain in the corners
        for side in (-1, 1):
            xs = [x for x, y, r in G["keepouts"] if x * side > 0]
            if xs:
                r = max(k[2] for k in G["keepouts"])
                xi = min(abs(x) for x in xs) - r
                xa, xb = (xi, x1 + 1.0) if side > 0 else (x0 - 1.0, -xi)
                tools.append(box(nm("h"), xa, xb, y0 - 1.0, y1 + 1.0, za - 0.01, zb + 0.01))
        subtract(pl, tools)
        OBJ[net].append(pl)
        log("plane %s %s: %d holes" % (lay, net, len(tools)))
    # bolt pads: discs of the pad polarity on the outer layer where the plane is the other net, via ring, contact face
    for name, n, x, y, d, hd in G["bolts"]:
        for lay in ("L1", "L4"):
            pnet = dict(G["planes"])[lay]
            if pnet != n:
                za, zb = ZR[lay]
                c = cyl(nm("pad"), x, y, za, zb, d / 2)
                subtract(c, [cyl(nm("h"), x, y, za - 0.01, zb + 0.01, hd / 2)])
                OBJ[n].append(c)
        c = box(nm("face"), x - 3.5, x + 3.5, y - 3.5, y + 3.5, 0.0, TPAD)
        subtract(c, [cyl(nm("h"), x, y, -0.01, TPAD + 0.01, hd / 2)])
        OBJ[n].append(c)
    for n, x, y, r in G["pad_vias"]:
        OBJ[n].append(cyl(nm("pv"), x, y, -T, 0.0, max(r, 0.15)))
    for name, n, x, y, s, hd in G["lugs"]:
        c = box(nm("lug"), x - s / 2, x + s / 2, y - s / 2, y + s / 2, -T, TPAD)
        subtract(c, [cyl(nm("h"), x, y, -T - 0.01, TPAD + 0.01, hd / 2)])
        OBJ[n].append(c)
    for n, x, y, r, pr in G["vias"]:
        OBJ[n].append(cyl(nm("v"), x, y, -T, 0.0, max(r, 0.15)))
    log("objects: %r" % {k: len(v) for k, v in OBJ.items()})
    BODY = {}

    def bbox(obj):
        pts = [[float(v) for v in ed.GetVertexPosition(vid)] for vid in ed.GetVertexIDsFromObject(obj)]
        if not pts:
            return None
        return [min(p[i] for p in pts) for i in range(3)] + [max(p[i] for p in pts) for i in range(3)]

    for net, objs in OBJ.items():
        unite(objs)
        before = set(ed.GetObjectsInGroup("Solids"))
        ed.SeparateBody(["NAME:Selections", "Selections:=", objs[0], "NewPartsModelFlag:=", "Model"],
                        ["CreateGroupsForNewObjects:=", False])
        lumps = [objs[0]] + sorted(set(ed.GetObjectsInGroup("Solids")) - before)
        info = []
        for o in lumps:
            b = bbox(o)
            d = ((b[3] - b[0]) ** 2 + (b[4] - b[1]) ** 2) ** 0.5 if b else 0.0
            info.append((d, o, b))
        info.sort(reverse=True)
        big = [o for d, o, b in info if d > 20.0]
        for d, o, b in info:
            log("lump %s %s diag %.2f mm bbox %r" % (net, o, d, b))
        small = [o for d, o, b in info if d <= 20.0]
        if small:
            ed.Delete(["NAME:Selections", "Selections:=", ",".join(small)])
        if len(big) > 1:
            unite(big)
        BODY[net] = big[0]
        bnd.AssignSignalNet(["NAME:" + net, "Objects:=", [big[0]]])
    log("united %r" % BODY)

    def face(body, x, y, z):
        return ed.GetFaceByPosition(["NAME:FaceParameters", "BodyName:=", body, "XPosition:=", mm(x),
                                     "YPosition:=", mm(y), "ZPosition:=", mm(z)])

    for name, n, x, y, d, hd in G["bolts"]:
        bnd.AssignSource(["NAME:" + name, "Faces:=", [face(BODY[n], x + 3.0, y, TPAD)], "TerminalType:=",
                          "ConstantVoltage", "Net:=", n])
    for name, n, x, y, s, hd in G["lugs"]:
        bnd.AssignSink(["NAME:" + name, "Faces:=", [face(BODY[n], x + s / 2 - 1.0, y, TPAD)], "TerminalType:=",
                        "ConstantVoltage", "Net:=", n])
    log("terminals assigned")
    oDesign.GetModule("AnalysisSetup").InsertSetup("Matrix", [
        "NAME:Setup1", "AdaptiveFreq:=", "1MHz", "SaveFields:=", False, "Enabled:=", True,
        ["NAME:Cap", "MaxPass:=", 2, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 10, "PerRefine:=", 30,
         "AutoIncreaseSolutionOrder:=", True, "SolutionOrder:=", "Normal", "Solver Type:=", "Iterative"],
        ["NAME:DC", "SolveResOnly:=", False,
         ["NAME:Cond", "MaxPass:=", 10, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
         ["NAME:Mult", "MaxPass:=", 1, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
         "Solution Order:=", "Normal"],
        ["NAME:AC", "MaxPass:=", 12, "MinPass:=", 2, "MinConvPass:=", 2, "PerError:=", 1, "PerRefine:=", 30,
         "Solution Order:=", "High"]])
    log("validate: %r" % oDesign.ValidateDesign())
    oProject.Save()
    oDesign.Analyze("Setup1")
    oDesign.ExportMatrixData(os.path.join(OUT, "BB_BUS_PCB_matrix.txt"), "C, DC RL, AC RL", "", "Setup1:LastAdaptive",
                             "Original", "ohm", "nH", "pF", "mSie", 1000000, "Maxwell,Spice,Couple", 0, False, 15,
                             20, 1)
    log("BB_BUS_PCB: exported")
except Exception:
    log(traceback.format_exc())
    try:
        for m in oDesktop.GetMessages(oProject.GetName(), "BB_BUS_PCB", 0):
            log("MSG " + str(m))
    except Exception:
        pass
oProject.Save()
LOG.close()

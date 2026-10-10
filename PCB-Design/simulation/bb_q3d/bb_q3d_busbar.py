# -*- coding: utf-8 -*-
"""
Q3D extraction of the laminated DC busbar of one SPB cell (geometry of hardware/cell-assembly, Fusion parameters):
DC+ plate on the DC+ terminals, 0.25 mm film, DC- plate with bosses to the DC- terminals, series tabs at both ends.

    simulation\\bb_q3d\\run_bb_q3d_busbar.cmd   (KTH licence)   -> results/BB_BUS_matrix.txt; post: busbar_post.py
Terminals: DC+ net: sources at the three DC+ terminal faces (J1_A..C), sink at the DC+ series tab;
           DC- net: sources at the three DC- boss faces (J2_A..C), sink at the DC- series tab.
"""
import os
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
OUT = os.path.join(HERE, "results")
LOG = open(os.path.join(OUT, "busbar_log.txt"), "w")

# geometry (mm), same as SPB_Cell_Assembly.py
PITCH, N = 36.0, 3
J1X, J2X, JY = -6.0, 6.0, 18.8
TERM_H, CU, INS = 6.5, 1.5, 0.25
Y0, Y1 = 11.8, 25.8
BX0, BX1 = -24.0, 96.0
CLR, BOSS = 9.0, 7.0
zt = -TERM_H
zp0, zi0 = zt - CU, zt - CU - INS
zn0 = zi0 - CU

oProject = oDesktop.NewProject()
oProject.Rename(os.path.join(OUT, "bb_q3d_busbar.aedt"), True)
oProject.InsertDesign("Q3D Extractor", "BB_BUS", "", "")
oDesign = oProject.SetActiveDesign("BB_BUS")
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


def cyl(name, x, y, z0, z1, d):
    ed.CreateCylinder(["NAME:CylinderParameters", "XCenter:=", mm(x), "YCenter:=", mm(y), "ZCenter:=", mm(z0),
                       "Radius:=", mm(d / 2), "Height:=", mm(z1 - z0), "WhichAxis:=", "Z", "NumSides:=", "0"],
                      attrs(name))
    return name


def subtract(blank, tools):
    ed.Subtract(["NAME:Selections", "Blank Parts:=", blank, "Tool Parts:=", ",".join(tools)],
                ["NAME:SubtractParameters", "KeepOriginals:=", False])


def unite(objs):
    ed.Unite(["NAME:Selections", "Selections:=", ",".join(objs)], ["NAME:UniteParameters", "KeepOriginals:=", False])


xs = [k * PITCH for k in range(N)]
box("DCP", BX0 - 14.0, BX1 - 12.0, Y0, Y1, zp0, zt)
box("DCN", BX0 + 12.0, BX1 + 14.0, Y0, Y1, zn0, zi0)
tools, bosses = [], []
for k, x in enumerate(xs):
    tools.append(cyl("clr%d" % k, x + J2X, JY, zp0 - 0.1, zt + 0.1, CLR))
    bosses.append(cyl("boss%d" % k, x + J2X, JY, zi0, zt, BOSS))
subtract("DCP", tools)
unite(["DCN"] + bosses)
bnd.AssignSignalNet(["NAME:DCP", "Objects:=", ["DCP"]])
bnd.AssignSignalNet(["NAME:DCN", "Objects:=", ["DCN"]])


def face(body, x, y, z):
    return ed.GetFaceByPosition(["NAME:FaceParameters", "BodyName:=", body, "XPosition:=", mm(x),
                                 "YPosition:=", mm(y), "ZPosition:=", mm(z)])


for k, x in enumerate(xs):
    # DC+ terminal contact: top face of the DC+ plate at J1 (a face of the whole plate top; use a small sheet instead)
    pass
# terminals on small contact pads (sheets united as thin copper discs) to localise the current injection
for k, x in enumerate(xs):
    cyl("tp%d" % k, x + J1X, JY, zt, zt + 0.2, 6.0)
    cyl("tn%d" % k, x + J2X, JY, zt, zt + 0.2, 6.0)
unite(["DCP"] + ["tp%d" % k for k in range(N)])
unite(["DCN"] + ["tn%d" % k for k in range(N)])
for k, x in enumerate(xs):
    bnd.AssignSource(["NAME:J1_%s" % "ABC"[k], "Faces:=", [face("DCP", x + J1X, JY, zt + 0.2)],
                      "TerminalType:=", "ConstantVoltage", "Net:=", "DCP"])
    bnd.AssignSource(["NAME:J2_%s" % "ABC"[k], "Faces:=", [face("DCN", x + J2X, JY, zt + 0.2)],
                      "TerminalType:=", "ConstantVoltage", "Net:=", "DCN"])
bnd.AssignSink(["NAME:TAB_P", "Faces:=", [face("DCP", BX0 - 14.0, (Y0 + Y1) / 2, (zp0 + zt) / 2)],
                "TerminalType:=", "ConstantVoltage", "Net:=", "DCP"])
bnd.AssignSink(["NAME:TAB_N", "Faces:=", [face("DCN", BX1 + 14.0, (Y0 + Y1) / 2, (zn0 + zi0) / 2)],
                "TerminalType:=", "ConstantVoltage", "Net:=", "DCN"])
oDesign.GetModule("AnalysisSetup").InsertSetup("Matrix", [
    "NAME:Setup1", "AdaptiveFreq:=", "1MHz", "SaveFields:=", False, "Enabled:=", True,
    ["NAME:Cap", "MaxPass:=", 4, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 5, "PerRefine:=", 30,
     "AutoIncreaseSolutionOrder:=", True, "SolutionOrder:=", "High", "Solver Type:=", "Iterative"],
    ["NAME:DC", "SolveResOnly:=", False,
     ["NAME:Cond", "MaxPass:=", 10, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
     ["NAME:Mult", "MaxPass:=", 1, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
     "Solution Order:=", "Normal"],
    ["NAME:AC", "MaxPass:=", 12, "MinPass:=", 2, "MinConvPass:=", 2, "PerError:=", 1, "PerRefine:=", 30,
     "Solution Order:=", "High"]])
try:
    LOG.write("validate: %r\n" % oDesign.ValidateDesign())
except Exception as e:
    LOG.write("validate exc %r\n" % e)
try:
    for m in oDesktop.GetMessages(oProject.GetName(), "BB_BUS", 0):
        LOG.write("MSG " + str(m) + "\n")
except Exception as e:
    LOG.write("msg exc %r\n" % e)
LOG.flush()
try:
    oDesign.Analyze("Setup1")
    oDesign.ExportMatrixData(os.path.join(OUT, "BB_BUS_matrix.txt"), "C, DC RL, AC RL", "", "Setup1:LastAdaptive",
                             "Original", "ohm", "nH", "pF", "mSie", 1000000, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
    LOG.write("BB_BUS: exported\n")
except Exception as e:
    LOG.write("FAILED %r\n" % e)
    for m in oDesktop.GetMessages(oProject.GetName(), "BB_BUS", 0):
        LOG.write("MSG " + str(m) + "\n")
oProject.Save()
LOG.close()

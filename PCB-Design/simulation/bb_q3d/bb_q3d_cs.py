# -*- coding: utf-8 -*-
"""
Common-source inductance of the building block: one Q3D design with the power loop (BB_PL geometry) AND the
low-side gate star with its Kelvin return, so that the mutual inductance between gate loop and power loop
(= effective common-source inductance L_CS) is extracted.

    simulation\\bb_q3d\\run_bb_q3d_cs.cmd      (KTH licence: campus or VPN)

Designs (project results\\bb_q3d_cs.aedt):
  BB_CS     Kelvin: gate return from a via in each QL source pad, on L2 directly under the gate trace, in a slot of
            the L2 DC- plane, to the driver ground pad (net DCN, because it joins the source pad)
  BB_CS_noK no Kelvin: driver ground pad connected to the L2 DC- plane next to the driver (shared return)
Gate net G: driver output pad -> trunk -> branch on L1 in the gap between QL drain and source pads -> gate pads.
Post-processing: python cs_post.py
"""
import os
import sys
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, HERE)
import bb_geometry as geo  # noqa: E402

OUT = os.path.join(HERE, "results")
LOG = open(os.path.join(OUT, "cs_log.txt"), "w")


def log(msg):
    LOG.write(str(msg) + "\n")
    LOG.flush()


STACK = [("h_diel", 0.100), ("h_23", 1.200), ("h_34", 0.100), ("t_L1", 0.070), ("t_L2", 0.070), ("t_L3", 0.070),
         ("t_L4", 0.070), ("t_pad", 0.035), ("via_r", 0.150), ("r_anti", 0.350)]       # 2 oz stack (BB_PL_2oz)
DERIVED = [("z_L1", "t_L2+h_diel"), ("z_top", "z_L1+t_L1"), ("z_L3t", "-h_23"), ("z_L3b", "-h_23-t_L3"),
           ("z_L4t", "z_L3b-h_34"), ("z_L4b", "z_L4t-t_L4")]
ZRANGE = {"L1": ("z_L1", "z_top"), "PAD": ("z_top", "z_top+t_pad"), "L2": ("0mm", "t_L2"),
          "L3": ("z_L3b", "z_L3t"), "L4": ("z_L4b", "z_L4t"), "PADB": ("z_L4b-t_pad", "z_L4b"),
          "L2X": ("-0.05mm", "t_L2+0.05mm")}
VIA_BOTTOM = {"L2": "0mm", "L3": "z_L3b", "L4": "z_L4b"}

oProject = oDesktop.NewProject()
oProject.Rename(os.path.join(OUT, "bb_q3d_cs.aedt"), True)


def mm(v):
    return "%.4fmm" % v


def attrs(name):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", "(255 128 64)",
            "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "UDMId:=", "",
            "MaterialValue:=", "\"copper\"", "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True, "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False, "IsLightweight:=", False]


class Design(object):
    def __init__(self, name):
        oProject.InsertDesign("Q3D Extractor", name, "", "")
        self.design = oProject.SetActiveDesign(name)
        self.ed = self.design.SetActiveEditor("3D Modeler")
        self.nets, self.sinks, self.sources, self.n, self.z = {}, {}, {}, 0, {}
        props = ["NAME:NewProps"]
        for n, v in STACK:
            props.append(["NAME:" + n, "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", mm(v)])
            self.z[n] = v
        for n, e in DERIVED:
            props.append(["NAME:" + n, "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", e])
            self.z[n] = float(eval(e, {}, dict(self.z)))
        self.design.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
                                    ["NAME:PropServers", "LocalVariables"], props]])

    def box(self, net, name, layer, x0, x1, y0, y1):
        z0, z1 = ZRANGE[layer]
        self.ed.CreateBox(["NAME:BoxParameters", "XPosition:=", mm(x0), "YPosition:=", mm(y0), "ZPosition:=", z0,
                           "XSize:=", mm(x1 - x0), "YSize:=", mm(y1 - y0), "ZSize:=", "(%s)-(%s)" % (z1, z0)],
                          attrs(name))
        if net:
            self.nets.setdefault(net, []).append(name)
        return name

    def cyl(self, net, name, x, y, z0, height, r):
        self.ed.CreateCylinder(["NAME:CylinderParameters", "XCenter:=", mm(x), "YCenter:=", mm(y),
                                "ZCenter:=", z0, "Radius:=", r, "Height:=", height, "WhichAxis:=", "Z",
                                "NumSides:=", "0"], attrs(name))
        if net:
            self.nets.setdefault(net, []).append(name)
        return name

    def via(self, net, x, y, to_layer):
        self.n += 1
        zb = VIA_BOTTOM[to_layer]
        return self.cyl(net, "via%d" % self.n, x, y, zb, "z_top-(%s)" % zb, "via_r")

    def subtract(self, blank, tools):
        if tools:
            self.ed.Subtract(["NAME:Selections", "Blank Parts:=", blank, "Tool Parts:=", ",".join(tools)],
                             ["NAME:SubtractParameters", "KeepOriginals:=", False])

    def holes(self, plane, pts):
        tools = []
        for x, y in pts:
            self.n += 1
            tools.append(self.cyl(None, "anti%d" % self.n, x, y, "z_L4b-1mm", "z_top-z_L4b+2mm", "r_anti"))
        self.subtract(plane, tools)

    def finish_nets(self):
        bnd = self.design.GetModule("BoundarySetup")
        self.body = {}
        for net, objs in self.nets.items():
            if len(objs) > 1:
                self.ed.Unite(["NAME:Selections", "Selections:=", ",".join(objs)],
                              ["NAME:UniteParameters", "KeepOriginals:=", False])
            self.body[net] = objs[0]
            bnd.AssignSignalNet(["NAME:" + net, "Objects:=", [objs[0]]])

    def terminal(self, kind, name, net, pts, side="top"):
        z = self.z["z_top"] + self.z["t_pad"] if side == "top" else self.z["z_L4b"] - self.z["t_pad"]
        faces = [self.ed.GetFaceByPosition(["NAME:FaceParameters", "BodyName:=", self.body[net],
                                            "XPosition:=", mm(x), "YPosition:=", mm(y), "ZPosition:=", mm(z)])
                 for x, y in pts]
        getattr(self.design.GetModule("BoundarySetup"), "Assign" + kind)(
            ["NAME:" + name, "Faces:=", faces, "TerminalType:=", "ConstantVoltage", "Net:=", net])

    def solve_export(self, tag):
        self.design.GetModule("AnalysisSetup").InsertSetup("Matrix", [
            "NAME:Setup1", "AdaptiveFreq:=", "100MHz", "SaveFields:=", False, "Enabled:=", True,
            ["NAME:Cap", "MaxPass:=", 4, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 5,
             "PerRefine:=", 30, "AutoIncreaseSolutionOrder:=", True, "SolutionOrder:=", "High",
             "Solver Type:=", "Iterative"],
            ["NAME:DC", "SolveResOnly:=", False,
             ["NAME:Cond", "MaxPass:=", 10, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
             ["NAME:Mult", "MaxPass:=", 1, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1, "PerRefine:=", 30],
             "Solution Order:=", "Normal"],
            ["NAME:AC", "MaxPass:=", 12, "MinPass:=", 2, "MinConvPass:=", 2, "PerError:=", 1,
             "PerRefine:=", 30, "Solution Order:=", "High"]])
        self.design.Analyze("Setup1")
        self.design.ExportMatrixData(os.path.join(OUT, "%s_matrix.txt" % tag), "C, DC RL, AC RL", "",
                                     "Setup1:LastAdaptive", "Original", "ohm", "nH", "pF", "mSie",
                                     100000000, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
        log("%s: exported" % tag)


XG, YG, YD = 5.3, 9.2, 8.0          # gate pad |x|, gate branch y (gap between QL drain and source pads), driver row


def build(kelvin):
    tag = "BB_CS" if kelvin else "BB_CS_noK"
    d = Design(tag)
    G = geo.build()
    for net, name, layer, x0, x1, y0, y1 in G["boxes"]:
        d.box(net, name, layer, x0, x1, y0, y1)
    for net, x, y, to in G["vias"]:
        d.via(net, x, y, to)
    # gate net on L1 / PAD
    d.box("G", "G_branch", "L1", -XG - 0.2, XG + 0.2, YG - 0.125, YG + 0.125)
    d.box("G", "G_trunk", "L1", -0.125, 0.125, YD - 0.25, YG)
    d.box("G", "DrvOut_l1", "L1", -0.3, 0.3, YD - 0.25, YD + 0.25)
    d.box("G", "DrvOut", "PAD", -0.3, 0.3, YD - 0.25, YD + 0.25)
    for s, side in ((-1, "L"), (1, "R")):
        d.box("G", "GateL1_%s" % side, "L1", s * XG - 0.2, s * XG + 0.2, YG - 0.15, YG + 0.15)
        d.box("G", "Gate_%s" % side, "PAD", s * XG - 0.2, s * XG + 0.2, YG - 0.15, YG + 0.15)
    # driver ground pad (joins DC- through the Kelvin path or directly through the plane)
    d.box("DCN", "DrvGnd_l1", "L1", -0.3, 0.3, YD - 0.95, YD - 0.55)
    d.box("DCN", "DrvGnd", "PAD", -0.3, 0.3, YD - 0.95, YD - 0.55)
    d.via("DCN", 0.0, YD - 0.75, "L2")
    slot = []
    if kelvin:
        ks = [("KS_stub_L", -XG - 0.2, -XG + 0.2, YG - 0.15, 10.15), ("KS_stub_R", XG - 0.2, XG + 0.2, YG - 0.15, 10.15),
              ("KS_branch", -XG - 0.2, XG + 0.2, YG - 0.15, YG + 0.15), ("KS_trunk", -0.45, 0.45, YD - 1.0, YG + 0.15)]
        for name, x0, x1, y0, y1 in ks:
            d.box("DCN", name, "L2", x0, x1, y0, y1)
            d.n += 1
            slot.append(d.box(None, "slot%d" % d.n, "L2X", x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2))
        for s in (-1, 1):
            d.via("DCN", s * XG, 9.95, "L2")           # Kelvin via in the QL source pad
    d.subtract("L2_DCN", slot)
    plane_obj = {"L2": "L2_DCN", "L3": "L3_DCP"}
    for pl in ("L2", "L3"):
        d.holes(plane_obj[pl], [(x, y) for p_, x, y in G["holes"] if p_ == pl])
    d.finish_nets()
    terms = sorted(G["terminals"], key=lambda t: t[0] != "Source")
    terms += [("Source", "Gate_L", "G", [(-XG, YG)], "top"), ("Source", "Gate_R", "G", [(XG, YG)], "top"),
              ("Source", "DrvGnd", "DCN", [(0.15, YD - 0.75)], "top"), ("Sink", "DrvOut", "G", [(0.0, YD - 0.1)], "top")]
    for kind, name, net, pts, side in sorted(terms, key=lambda t: t[0] != "Source"):
        d.terminal(kind, name, net, pts, side)
    d.solve_export(tag)


ONLY = os.environ.get("CS_ONLY", "")
for kel in (True, False):
    if ONLY and ONLY != ("BB_CS" if kel else "BB_CS_noK"):
        continue
    try:
        build(kel)
    except Exception as e:
        log("%s FAILED: %r" % ("kelvin" if kel else "noK", e))
    oProject.Save()
LOG.close()

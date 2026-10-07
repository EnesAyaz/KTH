# -*- coding: utf-8 -*-
"""
Q3D model of the symmetric building block (one phase leg, 2 x EPC2361 per switch, driver in the middle).

    simulation\\bb_q3d\\run_bb_q3d.cmd        (needs the KTH licence: campus network or VPN)

Copper only; components (MLCCs, EPC2361s) are gaps with source/sink terminals on their pads,
as in simulation/q3d. Planar geometry comes from bb_geometry.py; the stack-up is in AEDT design
variables (h_diel, h_23, h_34, t_L1..t_L4, t_pad, via_r, r_anti), editable in the GUI.

Designs:
  BB_PL   power loop: nets DCP / DCN / AC, sinks T_DCP / T_DCN / T_AC (board terminals)
  BB_GL   low-side gate loop: star from the centre driver to QL_L / QL_R (nets G, KS)
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
if not os.path.isdir(OUT):
    os.makedirs(OUT)
LOG = open(os.path.join(OUT, "bb_log.txt"), "w")


def log(msg):
    LOG.write(str(msg) + "\n")
    LOG.flush()


STACK = [  # (name, mm, description)
    ("h_diel", 0.100, "L1-L2 prepreg"), ("h_23", 1.200, "L2-L3 core"), ("h_34", 0.100, "L3-L4 prepreg"),
    ("t_L1", 0.070, "L1 copper"), ("t_L2", 0.035, "L2 copper"), ("t_L3", 0.035, "L3 copper"),
    ("t_L4", 0.070, "L4 copper"), ("t_pad", 0.035, "pad height"), ("via_r", 0.150, "via radius"),
    ("r_anti", 0.350, "plane clearance radius"),
]
DERIVED = [("z_L1", "t_L2+h_diel"), ("z_top", "z_L1+t_L1"),
           ("z_L3t", "-h_23"), ("z_L3b", "-h_23-t_L3"),
           ("z_L4t", "z_L3b-h_34"), ("z_L4b", "z_L4t-t_L4")]
ZRANGE = {"L1": ("z_L1", "z_top"), "PAD": ("z_top", "z_top+t_pad"), "L2": ("0mm", "t_L2"),
          "L3": ("z_L3b", "z_L3t"), "L4": ("z_L4b", "z_L4t"), "PADB": ("z_L4b-t_pad", "z_L4b")}
VIA_BOTTOM = {"L2": "0mm", "L3": "z_L3b", "L4": "z_L4b"}

# optional stack-up override for variants, e.g. BB_STACK="t_L2=0.07,t_L3=0.07" BB_SUFFIX=_2oz
OVR = dict((k, float(v)) for k, v in (kv.split("=") for kv in os.environ.get("BB_STACK", "").split(",") if kv))
STACK = [(n, OVR.get(n, v), d) for n, v, d in STACK]
SUFFIX = os.environ.get("BB_SUFFIX", "")
PROJECT = os.path.join(OUT, "bb_q3d%s.aedt" % SUFFIX)
oProject = oDesktop.NewProject()
oProject.Rename(PROJECT, True)


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
        self.nets, self.sinks, self.sources, self.n = {}, {}, {}, 0
        self.z = {}
        props = ["NAME:NewProps"]
        for n, v, d in STACK:
            props.append(["NAME:" + n, "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", mm(v),
                          "Description:=", d])
            self.z[n] = v
        for n, e in DERIVED:
            props.append(["NAME:" + n, "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", e])
            self.z[n] = float(eval(e, {}, dict(self.z)))
        self.design.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
                                    ["NAME:PropServers", "LocalVariables"], props]])

    def zval(self, expr):
        return float(eval(expr.replace("mm", ""), {}, dict(self.z)))

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

    def holes(self, plane, pts):
        if not pts:
            return
        tools = []
        for x, y in pts:
            self.n += 1
            tools.append(self.cyl(None, "anti%d" % self.n, x, y, "z_L4b-1mm", "z_top-z_L4b+2mm", "r_anti"))
        self.ed.Subtract(["NAME:Selections", "Blank Parts:=", plane, "Tool Parts:=", ",".join(tools)],
                         ["NAME:SubtractParameters", "KeepOriginals:=", False])

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
        if kind == "Sink":
            self.sinks[net] = name
        else:
            self.sources.setdefault(net, []).append(name)

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
        f = open(os.path.join(OUT, "%s_terminals.txt" % tag), "w")
        for net in sorted(self.sinks):
            f.write("%s %s %s\n" % (net, self.sinks[net], " ".join(self.sources.get(net, []))))
        f.write("# stack: %s\n" % ", ".join("%s=%g" % kv for kv in sorted(self.z.items())))
        f.close()
        log("%s: exported" % tag)


def build_power():
    d = Design("BB_PL")
    G = geo.build()
    for net, name, layer, x0, x1, y0, y1 in G["boxes"]:
        d.box(net, name, layer, x0, x1, y0, y1)
    for net, x, y, to in G["vias"]:
        d.via(net, x, y, to)
    plane_obj = {"L2": "L2_DCN", "L3": "L3_DCP"}
    for pl in ("L2", "L3"):
        d.holes(plane_obj[pl], [(x, y) for p_, x, y in G["holes"] if p_ == pl])
    d.finish_nets()
    for kind, name, net, pts, side in sorted(G["terminals"], key=lambda t: t[0] != "Source"):
        d.terminal(kind, name, net, pts, side)
    return d


def build_gate():
    d = Design("BB_GL")
    g = geo.GATE
    yd, yg, xg, wg, sg = g["y_drv"], g["y_gate"], g["x_gate"], g["w_g"], g["s_gk"]
    # G: driver LO pad -> trunk (x = 0) -> branches -> gate pads of QL_L / QL_R
    d.box("G", "G_trunk", "L1", -wg / 2, wg / 2, yd, yg + wg / 2)
    d.box("G", "G_branch", "L1", -xg - 0.25, xg + 0.25, yg - wg / 2, yg + wg / 2)
    d.box("G", "DrvOut", "PAD", -0.6, wg / 2, yd - 0.25, yd + 0.25)
    for s, side in ((-1, "L"), (1, "R")):
        d.box("G", "Gate_%s" % side, "PAD", s * xg - 0.25, s * xg + 0.25, yg - 0.2, yg + 0.2)
    # KS: Kelvin pads at each QL source -> vias -> return on L2 under branch and trunk -> via -> driver GND pad
    for s, side in ((-1, "L"), (1, "R")):
        d.box("KS", "KSpad_%s" % side, "L1", s * xg - 0.25, s * xg + 0.25, yg + sg - 0.2, yg + sg + 0.2)
        d.box("KS", "Kelvin_%s" % side, "PAD", s * xg - 0.25, s * xg + 0.25, yg + sg - 0.2, yg + sg + 0.2)
        d.via("KS", s * xg, yg + sg, "L2")
    d.box("KS", "KS_branch", "L2", -xg - 0.3, xg + 0.3, yg - 0.3, yg + sg + 0.3)
    d.box("KS", "KS_trunk", "L2", -0.3, 0.9, yd - 0.3, yg)
    d.box("KS", "DrvGnd_l1", "L1", 0.35, 0.85, yd - 0.25, yd + 0.25)
    d.box("KS", "DrvGnd", "PAD", 0.35, 0.85, yd - 0.25, yd + 0.25)
    d.via("KS", 0.6, yd, "L2")
    d.finish_nets()
    d.terminal("Source", "Gate_L", "G", [(-xg, yg)])
    d.terminal("Source", "Gate_R", "G", [(xg, yg)])
    d.terminal("Sink", "DrvOut", "G", [(-0.35, yd)])
    d.terminal("Source", "Kelvin_L", "KS", [(-xg - 0.1, yg + sg + 0.1)])
    d.terminal("Source", "Kelvin_R", "KS", [(xg + 0.1, yg + sg + 0.1)])
    d.terminal("Sink", "DrvGnd", "KS", [(0.7, yd + 0.1)])
    return d


ONLY = [s for s in os.environ.get("BB_ONLY", "").split(",") if s]
for tag, build in (("BB_PL", build_power), ("BB_GL", build_gate)):
    if ONLY and tag not in ONLY:
        continue
    try:
        build().solve_export(tag + SUFFIX)
    except Exception as e:
        log("%s FAILED: %r" % (tag, e))
    oProject.Save()
LOG.close()

# -*- coding: utf-8 -*-
"""
Q3D Extractor model of the EPC2361 DPT power-loop cell, three MLCC arrangements.

Run (needs the KTH licence server, i.e. campus network or KTH VPN):
    simulation\\q3d\\run_q3d.cmd

Native AEDT IronPython script (no PyAEDT). Same method as the SiC busbar model
(Busbarfinal.aedt): only copper is modelled; every component (MLCC bank, QH,
QL) is a GAP in the copper with source/sink terminals on its pads. Each copper
region is one net (one sink per net, one or more sources), so Q3D returns the
partial R/L matrix of the copper, which q3d_to_spice.py turns into an LTspice
subcircuit. No shunt and no gate loop in this version.

  PL_A  MLCC bank next to QH (EPC "optimal" vertical loop)     L2 = DC-
  PL_B  MLCC bank between QH and QL                             L2 = AC (switch node)
  PL_C  two banks: A next to QH, B next to QL                   L2 = DC-, L3 = DC+  (h_23 sweep)

Nets / terminals (Src -> Snk), see docs/q3d-geometry-sketches.html:
  A, B:  DCP  CapP -> QH_D      AC  QH_S -> QL_D      DCN  QL_S -> CapN
  C:     DCP  CapAP, CapBP -> QH_D    AC  QH_S -> QL_D    DCN  CapAN, CapBN -> QL_S
All geometry is in design variables (AEDT: Design Properties > Local Variables). Units mm.
"""
import os
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
OUT = os.path.join(HERE, "results")
if not os.path.isdir(OUT):
    os.makedirs(OUT)
LOG = open(os.path.join(OUT, "q3d_log.txt"), "w")


def log(msg):
    LOG.write(str(msg) + "\n")
    LOG.flush()


# ---- shared variables (name, mm, meaning) -------------------------------------
COMMON = [
    ("h_diel",  0.100, "L1-L2 dielectric"),
    ("t_L1",    0.070, "L1 copper"),
    ("t_L2",    0.035, "L2 copper"),
    ("t_pad",   0.035, "pad height; terminal faces on top"),
    ("gap",     0.600, "lateral gap between L1 islands (component pad gap)"),
    ("w_cell",  9.000, "island and plane width"),
    ("fet_w",   5.000, "EPC2361 pad width"),
    ("fet_pad", 1.000, "EPC2361 pad length along the loop"),
    ("cap_p",   1.400, "MLCC pitch"),
    ("cap_w",   1.250, "MLCC pad width"),
    ("via_r",   0.150, "via radius"),
]
VARS_A = COMMON + [
    ("l_vrow", 0.800, "DC- cap landing: via strip"),
    ("l_capn", 0.900, "DC- cap pad strip"),
    ("l_dcp",  3.100, "DC+ island (caps + to QH drain)"),
    ("l_ac",   3.700, "AC island (QH source to QL drain)"),
    ("l_src",  2.000, "QL source island (DC-), via row 0.4 mm before its end"),
]
DER_A = [("z_L1", "t_L2+h_diel"), ("z_top", "z_L1+t_L1"),
         ("y_dcp0", "l_capn+gap"), ("y_dcp1", "y_dcp0+l_dcp"),
         ("y_ac0", "y_dcp1+gap"), ("y_ac1", "y_ac0+l_ac"),
         ("y_s0", "y_ac1+gap"), ("y_s1", "y_s0+l_src")]
VARS_B = COMMON + [
    ("l_ach", 1.800, "AC landing at QH source and at QL drain (via row to L2)"),
    ("l_dcp", 3.100, "DC+ island (QH drain to caps +)"),
    ("l_dcn", 3.100, "DC- island (caps - to QL source)"),
]
DER_B = [("z_L1", "t_L2+h_diel"), ("z_top", "z_L1+t_L1"),
         ("y_p0", "l_ach+gap"), ("y_p1", "y_p0+l_dcp"),
         ("y_n0", "y_p1+gap"), ("y_n1", "y_n0+l_dcn"),
         ("y_q0", "y_n1+gap"), ("y_q1", "y_q0+l_ach")]
VARS_C = VARS_A[:-1] + [
    ("l_src",   2.400, "QL source island (DC-): QL_S pads, via row, caps B - pads"),
    ("l_capbp", 1.700, "caps B + island (DC+), via row to L3"),
    ("h_23",    0.100, "L2-L3 dielectric (DC- plane to DC+ plane)"),
    ("t_L3",    0.035, "L3 copper"),
    ("r_anti",  0.350, "L2 clearance radius around DC+ vias"),
]
DER_C = DER_A[:-1] + [("y_s1", "y_s0+l_src"), ("y_b0", "y_s1+gap"), ("y_b1", "y_b0+l_capbp")]

# Q3D_ONLY=PL_C (environment variable) rebuilds only that design inside the existing project.
ONLY = [d for d in os.environ.get("Q3D_ONLY", "").split(",") if d]
PROJECT = os.path.join(OUT, "dpt_cell_q3d.aedt")
if ONLY and os.path.exists(PROJECT):
    oProject = oDesktop.OpenProject(PROJECT)
    for d in ONLY:
        try:
            oProject.DeleteDesign(d)
        except Exception:
            pass  # design not in the project yet
else:
    oProject = oDesktop.NewProject()
    oProject.Rename(PROJECT, True)


def attrs(name):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", "(255 128 64)",
            "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "UDMId:=", "",
            "MaterialValue:=", "\"copper\"", "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True, "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False, "IsLightweight:=", False]


def mm(v):
    return "%gmm" % v


class Builder(object):
    def __init__(self, design_name, variables, derived):
        oProject.InsertDesign("Q3D Extractor", design_name, "", "")
        self.name = design_name
        self.design = oProject.SetActiveDesign(design_name)
        self.ed = self.design.SetActiveEditor("3D Modeler")
        self.val, self.nets, self.sinks, self.sources, self.n = {}, {}, {}, {}, 0
        props = ["NAME:NewProps"]
        for name, v, desc in variables:
            props.append(["NAME:" + name, "PropType:=", "VariableProp", "UserDef:=", True,
                          "Value:=", mm(v), "Description:=", desc])
            self.val[name] = v
        for name, expr in derived:
            props.append(["NAME:" + name, "PropType:=", "VariableProp", "UserDef:=", True,
                          "Value:=", expr])
            self.val[name] = self.num(expr)
        self.design.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
                                    ["NAME:PropServers", "LocalVariables"], props]])

    def num(self, expr):
        return float(eval(expr.replace("mm", ""), {}, dict(self.val)))

    def _add(self, net, name):
        self.nets.setdefault(net, []).append(name)

    def box(self, net, name, x0, x1, y0, y1, z0, z1):
        self.ed.CreateBox(
            ["NAME:BoxParameters", "XPosition:=", x0, "YPosition:=", y0, "ZPosition:=", z0,
             "XSize:=", "(%s)-(%s)" % (x1, x0), "YSize:=", "(%s)-(%s)" % (y1, y0),
             "ZSize:=", "(%s)-(%s)" % (z1, z0)], attrs(name))
        if net:
            self._add(net, name)
        return name

    def l1(self, net, name, x0, x1, y0, y1):
        return self.box(net, name, x0, x1, y0, y1, "z_L1", "z_top")

    def l2(self, net, name, x0, x1, y0, y1):
        return self.box(net, name, x0, x1, y0, y1, "0mm", "t_L2")

    def l3(self, net, name, x0, x1, y0, y1):
        return self.box(net, name, x0, x1, y0, y1, "-h_23-t_L3", "-h_23")

    def pad(self, net, name, x0, x1, y0, y1):
        return self.box(net, name, x0, x1, y0, y1, "z_top", "z_top+t_pad")

    def cyl(self, net, name, x, y, z0, height, r):
        self.ed.CreateCylinder(
            ["NAME:CylinderParameters", "XCenter:=", x, "YCenter:=", y, "ZCenter:=", z0,
             "Radius:=", r, "Height:=", height, "WhichAxis:=", "Z", "NumSides:=", "0"],
            attrs(name))
        if net:
            self._add(net, name)
        return name

    def via(self, net, x, y, to_l3=False):
        self.n += 1
        if to_l3:
            return self.cyl(net, "via%d" % self.n, x, y, "-h_23-t_L3", "z_top+h_23+t_L3", "via_r")
        return self.cyl(net, "via%d" % self.n, x, y, "0mm", "z_top", "via_r")

    def via_row(self, net, y, to_l3=False, n=9):
        xs = []
        for i in range(n):
            x = "(%d)*w_cell/%d" % (i - (n - 1) // 2, n + 1)
            self.via(net, x, y, to_l3)
            xs.append(x)
        return xs

    def cap_pads(self, net, prefix, y0, y1):
        pts = []
        for i in range(6):
            xc = "(%g)*cap_p" % (i - 2.5)
            self.pad(net, "%s%d" % (prefix, i + 1), xc + "-cap_w/2", xc + "+cap_w/2", y0, y1)
            pts.append((xc, "(%s+%s)/2" % (y0, y1)))
        return pts

    def fet_pad(self, net, name, y0):
        self.pad(net, name, "-fet_w/2", "fet_w/2", y0, y0 + "+fet_pad")
        return [("0mm", y0 + "+fet_pad/2")]

    def clear_holes(self, plane, xs, y):
        tools = []
        for x in xs:
            self.n += 1
            tools.append(self.cyl(None, "anti%d" % self.n, x, y, "-1mm", "z_top+2mm", "r_anti"))
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

    def terminal(self, kind, name, net, points):
        z = mm(self.val["z_top"] + self.val["t_pad"])
        faces = [self.ed.GetFaceByPosition(
            ["NAME:FaceParameters", "BodyName:=", self.body[net], "XPosition:=", mm(self.num(x)),
             "YPosition:=", mm(self.num(y)), "ZPosition:=", z]) for x, y in points]
        getattr(self.design.GetModule("BoundarySetup"), "Assign" + kind)(
            ["NAME:" + name, "Faces:=", faces, "TerminalType:=", "ConstantVoltage", "Net:=", net])
        if kind == "Sink":
            self.sinks[net] = name
        else:
            self.sources.setdefault(net, []).append(name)

    def setup(self):
        self.design.GetModule("AnalysisSetup").InsertSetup("Matrix", [
            "NAME:Setup1", "AdaptiveFreq:=", "100MHz", "SaveFields:=", False, "Enabled:=", True,
            ["NAME:Cap", "MaxPass:=", 10, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1,
             "PerRefine:=", 30, "AutoIncreaseSolutionOrder:=", True, "SolutionOrder:=", "High",
             "Solver Type:=", "Iterative"],
            ["NAME:DC", "SolveResOnly:=", False,
             ["NAME:Cond", "MaxPass:=", 10, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1,
              "PerRefine:=", 30],
             ["NAME:Mult", "MaxPass:=", 1, "MinPass:=", 1, "MinConvPass:=", 1, "PerError:=", 1,
              "PerRefine:=", 30],
             "Solution Order:=", "Normal"],
            ["NAME:AC", "MaxPass:=", 15, "MinPass:=", 2, "MinConvPass:=", 2, "PerError:=", 0.5,
             "PerRefine:=", 30, "Solution Order:=", "High"]])


# ---- scenario A: MLCC bank next to QH, L2 = DC- -----------------------------------
def build_A():
    b = Builder("PL_A", VARS_A, DER_A)
    hw = "w_cell/2"
    b.l1("DCN", "DCN_cap", "-" + hw, hw, "-l_vrow", "l_capn")
    b.via_row("DCN", "-l_vrow/2")
    capn = b.cap_pads("DCN", "CapN", "0.2mm", "0.7mm")
    b.l1("DCP", "DCP", "-" + hw, hw, "y_dcp0", "y_dcp1")
    capp = b.cap_pads("DCP", "CapP", "y_dcp0+0.2mm", "y_dcp0+0.7mm")
    qhd = b.fet_pad("DCP", "QH_D", "y_dcp1-0.2mm-fet_pad")
    b.l1("AC", "AC", "-" + hw, hw, "y_ac0", "y_ac1")
    qhs = b.fet_pad("AC", "QH_S", "y_ac0+0.2mm")
    qld = b.fet_pad("AC", "QL_D", "y_ac1-0.2mm-fet_pad")
    b.l1("DCN", "DCN_src", "-" + hw, hw, "y_s0", "y_s1")
    qls = b.fet_pad("DCN", "QL_S", "y_s0+0.2mm")
    b.via_row("DCN", "y_s1-0.4mm")
    b.l2("DCN", "L2_DCN", "-" + hw, hw, "-l_vrow-0.2mm", "y_s1+0.2mm")
    b.finish_nets()
    b.terminal("Source", "CapP", "DCP", capp)
    b.terminal("Sink", "QH_D", "DCP", qhd)
    b.terminal("Source", "QH_S", "AC", qhs)
    b.terminal("Sink", "QL_D", "AC", qld)
    b.terminal("Source", "QL_S", "DCN", qls)
    b.terminal("Sink", "CapN", "DCN", capn)
    return b


# ---- scenario B: MLCC bank between QH and QL, L2 = AC -------------------------------
def build_B():
    b = Builder("PL_B", VARS_B, DER_B)
    hw = "w_cell/2"
    b.l1("AC", "AC_top", "-" + hw, hw, "0mm", "l_ach")
    b.via_row("AC", "0.3mm")
    qhs = b.fet_pad("AC", "QH_S", "l_ach-0.2mm-fet_pad")
    b.l1("DCP", "DCP", "-" + hw, hw, "y_p0", "y_p1")
    qhd = b.fet_pad("DCP", "QH_D", "y_p0+0.2mm")
    capp = b.cap_pads("DCP", "CapP", "y_p1-0.7mm", "y_p1-0.2mm")
    b.l1("DCN", "DCN", "-" + hw, hw, "y_n0", "y_n1")
    capn = b.cap_pads("DCN", "CapN", "y_n0+0.2mm", "y_n0+0.7mm")
    qls = b.fet_pad("DCN", "QL_S", "y_n1-0.2mm-fet_pad")
    b.l1("AC", "AC_bot", "-" + hw, hw, "y_q0", "y_q1")
    qld = b.fet_pad("AC", "QL_D", "y_q0+0.2mm")
    b.via_row("AC", "y_q1-0.3mm")
    b.l2("AC", "L2_AC", "-" + hw, hw, "-0.2mm", "y_q1+0.2mm")
    b.finish_nets()
    b.terminal("Source", "CapP", "DCP", capp)
    b.terminal("Sink", "QH_D", "DCP", qhd)
    b.terminal("Source", "QH_S", "AC", qhs)
    b.terminal("Sink", "QL_D", "AC", qld)
    b.terminal("Source", "QL_S", "DCN", qls)
    b.terminal("Sink", "CapN", "DCN", capn)
    return b


# ---- scenario C: two banks, L2 = DC-, L3 = DC+ ------------------------------------
def build_C():
    b = Builder("PL_C", VARS_C, DER_C)
    hw = "w_cell/2"
    b.l1("DCN", "DCN_cap", "-" + hw, hw, "-l_vrow", "l_capn")
    b.via_row("DCN", "-l_vrow/2")
    capan = b.cap_pads("DCN", "CapAN", "0.2mm", "0.7mm")
    b.l1("DCP", "DCP", "-" + hw, hw, "y_dcp0", "y_dcp1")
    capap = b.cap_pads("DCP", "CapAP", "y_dcp0+0.2mm", "y_dcp0+0.7mm")
    xs_qh = b.via_row("DCP", "y_dcp0+1.3mm", to_l3=True)           # DC+ to L3 at QH drain
    qhd = b.fet_pad("DCP", "QH_D", "y_dcp1-0.2mm-fet_pad")
    b.l1("AC", "AC", "-" + hw, hw, "y_ac0", "y_ac1")
    qhs = b.fet_pad("AC", "QH_S", "y_ac0+0.2mm")
    qld = b.fet_pad("AC", "QL_D", "y_ac1-0.2mm-fet_pad")
    b.l1("DCN", "DCN_src", "-" + hw, hw, "y_s0", "y_s1")
    qls = b.fet_pad("DCN", "QL_S", "y_s0+0.2mm")
    b.via_row("DCN", "y_s0+1.5mm")                                    # DC- to L2 at QL source
    capbn = b.cap_pads("DCN", "CapBN", "y_s1-0.7mm", "y_s1-0.2mm")
    b.l1("DCP", "DCP_B", "-" + hw, hw, "y_b0", "y_b1")
    capbp = b.cap_pads("DCP", "CapBP", "y_b0+0.2mm", "y_b0+0.7mm")
    xs_b = b.via_row("DCP", "y_b1-0.4mm", to_l3=True)                # caps B + to L3
    b.l2("DCN", "L2_DCN", "-" + hw, hw, "-l_vrow-0.2mm", "y_b1+0.2mm")
    b.clear_holes("L2_DCN", xs_qh, "y_dcp0+1.3mm")
    b.clear_holes("L2_DCN", xs_b, "y_b1-0.4mm")
    b.l3("DCP", "L3_DCP", "-" + hw, hw, "-l_vrow-0.2mm", "y_b1+0.2mm")
    b.finish_nets()
    b.terminal("Source", "CapAP", "DCP", capap)
    b.terminal("Source", "CapBP", "DCP", capbp)
    b.terminal("Sink", "QH_D", "DCP", qhd)
    b.terminal("Source", "QH_S", "AC", qhs)
    b.terminal("Sink", "QL_D", "AC", qld)
    b.terminal("Source", "CapAN", "DCN", capan)
    b.terminal("Source", "CapBN", "DCN", capbn)
    b.terminal("Sink", "QL_S", "DCN", qls)
    return b


def export(b, tag):
    """<tag>_matrix.txt (full Q3D matrix) + <tag>_terminals.txt (net, sink, sources)."""
    b.design.ExportMatrixData(os.path.join(OUT, "%s_matrix.txt" % tag), "C, DC RL, AC RL", "",
                              "Setup1:LastAdaptive", "Original", "ohm", "nH", "pF", "mSie",
                              100000000, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
    f = open(os.path.join(OUT, "%s_terminals.txt" % tag), "w")
    for net in sorted(b.sinks):
        f.write("%s %s %s\n" % (net, b.sinks[net], " ".join(b.sources.get(net, []))))
    f.write("# variables: %s\n" % ", ".join("%s=%g" % kv for kv in sorted(b.val.items())))
    f.close()
    log("%s: exported" % tag)


def set_var(b, var, value):
    b.design.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
                             ["NAME:PropServers", "LocalVariables"],
                             ["NAME:ChangedProps", ["NAME:" + var, "Value:=", value]]]])


# Parametric sweeps run after the nominal solve: {design: (variable, [values])}.
SWEEP = {"PL_C": ("h_23", ["0.5mm", "1.2mm"])}

for tag, build in (("PL_A", build_A), ("PL_B", build_B), ("PL_C", build_C)):
    if ONLY and tag not in ONLY:
        continue
    try:
        b = build()
        b.setup()
        b.design.Analyze("Setup1")
        export(b, tag)
        if tag in SWEEP:
            var, values = SWEEP[tag]
            nominal = b.val[var]
            for value in values:
                set_var(b, var, value)
                b.val[var] = float(value.replace("mm", ""))   # recorded in _terminals.txt
                b.design.Analyze("Setup1")
                export(b, "%s__%s_%s" % (tag, var, value.replace(".", "p")))
            b.val[var] = nominal
            set_var(b, var, mm(nominal))
    except Exception as e:  # keep going so one bad design does not lose the others
        log("%s FAILED: %r" % (tag, e))
    oProject.Save()

LOG.close()

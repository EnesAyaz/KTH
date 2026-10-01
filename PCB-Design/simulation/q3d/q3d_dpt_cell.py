# -*- coding: utf-8 -*-
"""
Q3D Extractor model of the proposed EPC2361 DPT cell: copper only, components as terminals.

Run (needs the KTH licence server, i.e. campus network or VPN):
    simulation\\q3d\\run_q3d.cmd

Native AEDT IronPython script (no PyAEDT). Same method as the SiC busbar model
(Busbarfinal.aedt): only copper is modelled; every component (MLCCs, QH, QL,
shunt array) is a GAP in the copper, with a source/sink terminal on each of its
pads. Each copper region between two components is one net, so Q3D returns
the partial self/mutual inductance matrix of every copper segment, which can
be exported as an equivalent circuit for LTspice together with the device models.

Copper nets of the power loop (current direction of the commutation loop):
    DCP  : Src CapP (6 MLCC + pads)  -> Snk QH_D  (QH drain pad)
    AC   : Src QH_S (QH source pad)  -> Snk QL_D  (QL drain pad)
    SQL  : Src QL_S (QL source pad)  -> Snk SH_in (5 shunt input pads)      [shunt design only]
    DCN  : Src SH_out (shunt output) -> Snk CapN  (6 MLCC - pads), via L2   [no shunt: Src QL_S]
All sources point along the loop, so  L_loop = sum of all ACL(i, j)  (output variable Lloop).
Add the component parts separately: MLCC ESL 0.48 nH / 6, EPC2361 package, shunt ESL and R.

Gate loop:  G : Src DrvOut -> Snk Gate ;  KS : Src Kelvin -> Snk DrvGnd  (L_loop = sum of matrix).

Everything is parametric (design variables, editable in AEDT under
Design Properties, and sweepable). Units mm.
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


# ---- design variables (name, value in mm, meaning) -----------------------------
POWER_VARS = [
    ("h_diel",  0.100, "L1-L2 dielectric: vertical spacing between + (L1) and - (L2) copper"),
    ("t_L1",    0.070, "L1 copper thickness"),
    ("t_L2",    0.035, "L2 copper thickness"),
    ("t_pad",   0.035, "pad/solder height above L1 (terminal faces sit on top)"),
    ("gap",     0.600, "lateral gap between L1 copper islands (DC-/DC+/AC/source)"),
    ("w_cell",  9.000, "width of DC-cap, DC+ and AC islands"),
    ("w_sh",   17.000, "width of the shunt island and DC- shunt landing"),
    ("l_vrow",  0.800, "DC- cap landing: via strip before the cap pads"),
    ("l_capn",  0.900, "DC- cap pad strip"),
    ("l_dcp",   3.100, "DC+ island length (cap + pads to QH drain)"),
    ("l_ac",    3.700, "AC island length (QH source to QL drain)"),
    ("l_s",     2.400, "QL source / shunt-input island length"),
    ("g_sh",    0.800, "copper gap under the shunt body"),
    ("l_dcn",   1.400, "DC- shunt landing length"),
    ("fet_w",   5.000, "EPC2361 pad width (long side, across the loop)"),
    ("fet_pad", 1.000, "EPC2361 drain/source pad length along the loop"),
    ("cap_p",   1.400, "MLCC pitch"),
    ("cap_w",   1.250, "MLCC pad width"),
    ("sh_p",    3.400, "shunt pitch"),
    ("sh_w",    2.800, "shunt pad width"),
    ("via_r",   0.150, "via radius"),
]
# derived edges along the loop (y); evaluated in order
DERIVED = [
    ("z_L1",  "t_L2+h_diel"),
    ("z_top", "z_L1+t_L1"),
    ("y_dcp0", "l_capn+gap"),
    ("y_dcp1", "y_dcp0+l_dcp"),
    ("y_ac0",  "y_dcp1+gap"),
    ("y_ac1",  "y_ac0+l_ac"),
    ("y_s0",   "y_ac1+gap"),
    ("y_s1",   "y_s0+l_s"),
    ("y_dn0",  "y_s1+g_sh"),
    ("y_dn1",  "y_dn0+l_dcn"),
]

GATE_VARS = [
    ("h_diel", 0.100, "L1-L2 dielectric"),
    ("t_L1",   0.070, "L1 copper"),
    ("t_L2",   0.035, "L2 copper"),
    ("t_pad",  0.035, "pad height"),
    ("l_gate", 8.000, "driver-to-gate length"),
    ("w_g",    0.250, "gate trace width (L1)"),
    ("w_ret",  0.600, "Kelvin return width (L2, directly under the gate trace)"),
    ("s_gk",   0.500, "gate pad to Kelvin pad spacing (y)"),
    ("via_r",  0.150, "via radius"),
]
GATE_DERIVED = [("z_L1", "t_L2+h_diel"), ("z_top", "z_L1+t_L1")]

oProject = oDesktop.NewProject()
oProject.Rename(os.path.join(OUT, "dpt_cell_q3d.aedt"), True)


def attrs(name):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", "(255 128 64)",
            "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "UDMId:=", "",
            "MaterialValue:=", "\"copper\"", "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True, "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False, "IsLightweight:=", False]


def mm(v):
    return "%gmm" % v


class Builder(object):
    """Boxes/vias from expressions in design variables; numeric copies for face picking."""

    def __init__(self, design_name, variables, derived):
        oProject.InsertDesign("Q3D Extractor", design_name, "", "")
        self.design = oProject.SetActiveDesign(design_name)
        self.ed = self.design.SetActiveEditor("3D Modeler")
        self.val = {}
        self.nets = {}
        self.n = 0
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
        """Corners as expression strings (x0<x1, y0<y1, z0<z1 numerically)."""
        self.ed.CreateBox(
            ["NAME:BoxParameters", "XPosition:=", x0, "YPosition:=", y0, "ZPosition:=", z0,
             "XSize:=", "(%s)-(%s)" % (x1, x0), "YSize:=", "(%s)-(%s)" % (y1, y0),
             "ZSize:=", "(%s)-(%s)" % (z1, z0)], attrs(name))
        self._add(net, name)

    def l1(self, net, name, x0, x1, y0, y1):
        self.box(net, name, x0, x1, y0, y1, "z_L1", "z_top")

    def l2(self, net, name, x0, x1, y0, y1):
        self.box(net, name, x0, x1, y0, y1, "0mm", "t_L2")

    def pad(self, net, name, x0, x1, y0, y1):
        self.box(net, name, x0, x1, y0, y1, "z_top", "z_top+t_pad")

    def via(self, net, x, y):
        self.n += 1
        name = "via%d" % self.n
        self.ed.CreateCylinder(
            ["NAME:CylinderParameters", "XCenter:=", x, "YCenter:=", y, "ZCenter:=", "0mm",
             "Radius:=", "via_r", "Height:=", "z_top", "WhichAxis:=", "Z", "NumSides:=", "0"],
            attrs(name))
        self._add(net, name)

    def finish_nets(self):
        """Unite each net into one body (vias overlap planes) and assign it."""
        bnd = self.design.GetModule("BoundarySetup")
        self.body = {}
        for net, objs in self.nets.items():
            if len(objs) > 1:
                self.ed.Unite(["NAME:Selections", "Selections:=", ",".join(objs)],
                              ["NAME:UniteParameters", "KeepOriginals:=", False])
            self.body[net] = objs[0]
            bnd.AssignSignalNet(["NAME:" + net, "Objects:=", [objs[0]]])

    def terminal(self, kind, name, net, points):
        """kind 'Source'/'Sink'; points: list of (x, y) expression pairs on pad tops."""
        faces = []
        for x, y in points:
            faces.append(self.ed.GetFaceByPosition(
                ["NAME:FaceParameters", "BodyName:=", self.body[net],
                 "XPosition:=", mm(self.num(x)), "YPosition:=", mm(self.num(y)),
                 "ZPosition:=", mm(self.val["z_top"] + self.val["t_pad"])]))
        bnd = self.design.GetModule("BoundarySetup")
        getattr(bnd, "Assign" + kind)(["NAME:" + name, "Faces:=", faces,
                                       "TerminalType:=", "ConstantVoltage", "Net:=", net])

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

    def loop_variable(self, terms):
        """Lloop = sum of all ACL(i,j) over the loop terminals (net:source)."""
        expr = "+".join("ACL(%s,%s)" % (a, b) for a in terms for b in terms)
        self.design.GetModule("OutputVariable").CreateOutputVariable(
            "Lloop", expr, "Setup1 : LastAdaptive", "Matrix", ["Context:=", "Original"])
        self.terms = terms


def export_results(design, tag, terms):
    """<tag>.csv: Lloop and every ACL/ACR entry at 100 MHz; <tag>_matrix.txt: full matrix."""
    exprs = ["Lloop"] + ["ACL(%s,%s)" % (a, b) for a in terms for b in terms] + \
            ["ACR(%s,%s)" % (a, a) for a in terms]
    rep = design.GetModule("ReportSetup")
    title = "LR_" + tag.split("__")[0]
    if title not in list(rep.GetAllReportNames()):
        # matrix context "Original" + explicit frequency, otherwise the table is empty
        rep.CreateReport(title, "Matrix", "Data Table", "Setup1 : LastAdaptive",
                         ["Context:=", "Original"], ["Freq:=", ["100MHz"]],
                         ["X Component:=", "Freq", "Y Component:=", exprs])
    rep.ExportToFile(title, os.path.join(OUT, "%s.csv" % tag))
    design.ExportMatrixData(os.path.join(OUT, "%s_matrix.txt" % tag), "C, DC RL, AC RL", "",
                            "Setup1:LastAdaptive", "Original", "ohm", "nH", "pF", "mSie",
                            100000000, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
    log("%s: exported %s.csv and %s_matrix.txt" % (tag, tag, tag))


# ---- power loop ------------------------------------------------------------------
def power_loop(name, with_shunt):
    b = Builder(name, POWER_VARS, DERIVED)
    hw, hs = "w_cell/2", "w_sh/2"
    wl2 = hs if with_shunt else hw
    # DC- MLCC landing (L1) + 9 vias to L2
    b.l1("DCN", "DCN_cap", "-" + hw, hw, "-l_vrow", "l_capn")
    for i in range(9):
        b.via("DCN", "(%d)*w_cell/10" % (i - 4), "-l_vrow/2")
    caps_n, caps_p = [], []
    for i in range(6):
        xc = "(%g)*cap_p" % (i - 2.5)
        b.pad("DCN", "CapN%d" % (i + 1), xc + "-cap_w/2", xc + "+cap_w/2", "0.2mm", "0.7mm")
        caps_n.append((xc, "0.45mm"))
    b.l1("DCP", "DCP", "-" + hw, hw, "y_dcp0", "y_dcp1")
    for i in range(6):
        xc = "(%g)*cap_p" % (i - 2.5)
        b.pad("DCP", "CapP%d" % (i + 1), xc + "-cap_w/2", xc + "+cap_w/2",
              "y_dcp0+0.2mm", "y_dcp0+0.7mm")
        caps_p.append((xc, "y_dcp0+0.45mm"))
    # QH spans DCP -> AC, QL spans AC -> source island (packages are gaps)
    b.pad("DCP", "QH_D", "-fet_w/2", "fet_w/2", "y_dcp1-0.2mm-fet_pad", "y_dcp1-0.2mm")
    b.l1("AC", "AC", "-" + hw, hw, "y_ac0", "y_ac1")
    b.pad("AC", "QH_S", "-fet_w/2", "fet_w/2", "y_ac0+0.2mm", "y_ac0+0.2mm+fet_pad")
    b.pad("AC", "QL_D", "-fet_w/2", "fet_w/2", "y_ac1-0.2mm-fet_pad", "y_ac1-0.2mm")
    src_net = "SQL" if with_shunt else "DCN"
    if with_shunt:
        b.l1("SQL", "SQL", "-" + hs, hs, "y_s0", "y_s1")
    else:
        b.l1("DCN", "DCN_src", "-" + hw, hw, "y_s0", "y_s0+2mm")
        for i in range(9):
            b.via("DCN", "(%d)*w_cell/10" % (i - 4), "y_s0+1.6mm")
    b.pad(src_net, "QL_S", "-fet_w/2", "fet_w/2", "y_s0+0.2mm", "y_s0+0.2mm+fet_pad")
    sh_in, sh_out = [], []
    if with_shunt:
        b.l1("DCN", "DCN_sh", "-" + hs, hs, "y_dn0", "y_dn1")
        for i in range(17):
            b.via("DCN", "(%d)*w_sh/18" % (i - 8), "y_dn0+0.9mm")
        for i in range(5):
            xc = "(%d)*sh_p" % (i - 2)
            b.pad("SQL", "SHin%d" % (i + 1), xc + "-sh_w/2", xc + "+sh_w/2",
                  "y_s1-0.5mm", "y_s1-0.1mm")
            b.pad("DCN", "SHout%d" % (i + 1), xc + "-sh_w/2", xc + "+sh_w/2",
                  "y_dn0+0.1mm", "y_dn0+0.5mm")
            sh_in.append((xc, "y_s1-0.3mm"))
            sh_out.append((xc, "y_dn0+0.3mm"))
        b.l2("DCN", "L2_DCN", "-" + wl2, wl2, "-l_vrow-0.2mm", "y_dn1+0.5mm")
    else:
        b.l2("DCN", "L2_DCN", "-" + wl2, wl2, "-l_vrow-0.2mm", "y_s0+2.5mm")
    b.finish_nets()

    fet = lambda y: [("-fet_w/4", y), ("fet_w/4", y)]
    b.terminal("Source", "CapP", "DCP", caps_p)
    b.terminal("Sink", "QH_D", "DCP", [("0mm", "y_dcp1-0.2mm-fet_pad/2")])
    b.terminal("Source", "QH_S", "AC", [("0mm", "y_ac0+0.2mm+fet_pad/2")])
    b.terminal("Sink", "QL_D", "AC", [("0mm", "y_ac1-0.2mm-fet_pad/2")])
    b.terminal("Source", "QL_S", src_net, [("0mm", "y_s0+0.2mm+fet_pad/2")])
    if with_shunt:
        b.terminal("Sink", "SH_in", "SQL", sh_in)
        b.terminal("Source", "SH_out", "DCN", sh_out)
    b.terminal("Sink", "CapN", "DCN", caps_n)
    terms = ["DCP:CapP", "AC:QH_S", "%s:QL_S" % src_net]
    if with_shunt:
        terms.append("DCN:SH_out")
    b.setup()
    b.loop_variable(terms)
    return b


# ---- gate loop -------------------------------------------------------------------
def gate_loop(name, length):
    b = Builder(name, [(n, (length if n == "l_gate" else v), d) for n, v, d in GATE_VARS],
                GATE_DERIVED)
    # G net: driver OUT pad -> gate trace (L1) -> gate pad
    b.l1("G", "G_trace", "-l_gate", "0.3mm", "-w_g/2", "w_g/2")
    b.pad("G", "DrvOut", "-l_gate-0.5mm", "-l_gate+0.3mm", "-0.2mm", "0.2mm")
    b.pad("G", "Gate", "-0.2mm", "0.3mm", "-0.25mm", "0.25mm")
    # KS net: Kelvin pad at the source -> via -> L2 return under the trace -> via -> driver GND
    b.l1("KS", "KS_pad", "-0.2mm", "0.3mm", "s_gk", "s_gk+0.5mm")
    b.pad("KS", "Kelvin", "-0.2mm", "0.3mm", "s_gk", "s_gk+0.5mm")
    b.via("KS", "0.05mm", "s_gk+0.25mm")
    b.l2("KS", "KS_ret", "-l_gate", "0.3mm", "-w_ret/2", "s_gk+0.5mm")
    b.via("KS", "-l_gate+0.3mm", "s_gk+0.25mm")
    b.l1("KS", "DrvGnd_l1", "-l_gate-0.5mm", "-l_gate+0.6mm", "s_gk-0.05mm", "s_gk+0.55mm")
    b.pad("KS", "DrvGnd", "-l_gate-0.5mm", "-l_gate", "s_gk", "s_gk+0.5mm")
    b.finish_nets()
    b.terminal("Source", "DrvOut", "G", [("-l_gate-0.1mm", "0mm")])
    b.terminal("Sink", "Gate", "G", [("0.05mm", "0mm")])
    b.terminal("Source", "Kelvin", "KS", [("0.2mm", "s_gk+0.1mm")])
    b.terminal("Sink", "DrvGnd", "KS", [("-l_gate-0.25mm", "s_gk+0.25mm")])
    b.setup()
    b.loop_variable(["G:DrvOut", "KS:Kelvin"])
    return b


def solve(b, tag):
    b.design.Analyze("Setup1")
    export_results(b.design, tag, b.terms)


# Parametric sweep example: L1-L2 spacing ("distance between + and - copper").
# Each point re-solves the design (~1-2 min). Edit or empty this list as needed.
SWEEP = {"PL_shunt": ("h_diel", ["0.075mm", "0.2mm"])}

JOBS = [("PL_shunt", lambda: power_loop("PL_shunt", True)),
        ("PL_noshunt", lambda: power_loop("PL_noshunt", False)),
        ("GL_near", lambda: gate_loop("GL_near", 8.0)),
        ("GL_far", lambda: gate_loop("GL_far", 25.0))]

for tag, job in JOBS:
    try:
        b = job()
        solve(b, tag)
        if tag in SWEEP:
            var, values = SWEEP[tag]
            nominal = mm(b.val[var])
            for value in values:
                b.design.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
                                         ["NAME:PropServers", "LocalVariables"],
                                         ["NAME:ChangedProps", ["NAME:" + var, "Value:=", value]]]])
                solve(b, "%s__%s_%s" % (tag, var, value.replace(".", "p")))
            b.design.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
                                     ["NAME:PropServers", "LocalVariables"],
                                     ["NAME:ChangedProps", ["NAME:" + var, "Value:=", nominal]]]])
    except Exception as e:  # keep going so one bad design does not lose the others
        log("%s FAILED: %r" % (tag, e))
    oProject.Save()

LOG.close()

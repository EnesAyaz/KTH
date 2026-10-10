# -*- coding: utf-8 -*-
"""
Ansys Icepak (AEDT 2024 R2) steady-state thermal model of the building block, conduction only.

    simulation\\bb_icepak\\run_bb_icepak.cmd      (needs the KTH licence: campus network or VPN)

Geometry from bb_geometry.py (same as Q3D / KiCad); losses from reports/building-block/data (50 kHz, rated point):
  EPC2361 x 4      1.91 W each (conduction + switching + dead time, typical R_DS(on) at 100 C)
  PCB copper       3.29 W (load current) + 1.07 W (switching harmonics): 1.0 W in each cell region, rest uniform
  MLCC ESR         per capacitor group from the network solve; driver 0.08 W
Cooling: 0.5 mm TIM (17.8 W/mK) on the FETs, aluminium pedestals, 3 mm aluminium plate whose top face is held at
60 C (liquid cold plate). Board: anisotropic FR-4/copper equivalent; via arrays under the cells.
Results: results/icepak_results<suffix>.txt (max temperature per object), results/*<suffix>.png.

Options (environment): BB_COOL=top (default) | both  -- "both" adds a 1 mm gap pad (3 W/mK) under the whole board and a
bottom aluminium plate at 60 C;  BB_POST=1 only re-runs the post-processing on an already solved project.
"""
import json
import os
import sys
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "simulation", "bb_q3d"))
import bb_geometry as geo  # noqa: E402

OUT = os.path.join(HERE, "results")
if not os.path.isdir(OUT):
    os.makedirs(OUT)
COOL = os.environ.get("BB_COOL", "top")
SUF = "" if COOL == "top" else "_" + COOL
POST_ONLY = os.environ.get("BB_POST", "") == "1"
LOG = open(os.path.join(OUT, "icepak_log%s.txt" % SUF), "w")


def log(m):
    LOG.write(str(m) + "\n")
    LOG.flush()


def msgs():
    try:
        for m in oDesktop.GetMessages("", "", 2)[-6:]:
            log("   AEDT: " + str(m))
    except Exception:
        pass


DATA = os.path.join(ROOT, "reports", "building-block", "data")
rs = json.load(open(os.path.join(DATA, "results.json")))
hf = json.load(open(os.path.join(DATA, "copper_hf.json")))
r50 = [r for r in rs["loss_vs_f"] if r["f"] == 50e3][0]
P_DEV = (r50["cond"] + r50["sw"] + r50["dead"]) / 4.0
P_CU = r50["cu"] + r50["cu_hf"]
case = [c for c in hf["cases"] if c["mode"] == "SVM" and abs(c["M"] - 1.0) < 1e-6 and c["pf"] == 1.0][0]
P_CAP = case["cap_P"]
log("P_dev %.3f W, P_cu %.3f W, caps %s" % (P_DEV, P_CU, P_CAP))

G = geo.build()
P, Y = G["params"], G["rows"]
XE = P["x_edge"]
Y0, Y1 = Y["p1"][0], Y["t_ac"][1]
T_PCB = 1.6
yqh, yql = sum(Y["qhd"]) / 2 + 1.0, sum(Y["qld"]) / 2 + 1.0

if POST_ONLY:
    oProject = oDesktop.OpenProject(os.path.join(OUT, "bb_icepak%s.aedt" % SUF))
else:
    oProject = oDesktop.NewProject()
    oProject.Rename(os.path.join(OUT, "bb_icepak%s.aedt" % SUF), True)
    oProject.InsertDesign("Icepak", "BB_thermal", "", "")
oDesign = oProject.SetActiveDesign("BB_thermal")
oEditor = oDesign.SetActiveEditor("3D Modeler")
oDef = oProject.GetDefinitionManager()
oBnd = oDesign.GetModule("BoundarySetup")


def material(name, k, rho, cp, kz=None):
    tc = ["NAME:thermal_conductivity", "property_type:=", "AnisoProperty", "unit:=", "",
          "component1:=", str(k), "component2:=", str(k), "component3:=", str(kz)] if kz else None
    args = ["NAME:" + name, "CoordinateSystemType:=", "Cartesian", "BulkOrSurfaceType:=", 1,
            ["NAME:PhysicsTypes", "set:=", ["Thermal"]]]
    args += [tc] if tc else ["thermal_conductivity:=", str(k)]
    args += ["mass_density:=", str(rho), "specific_heat:=", str(cp)]
    try:
        oDef.AddMaterial(args)
        log("material %s ok" % name)
    except Exception as e:
        log("material %s failed: %r" % (name, e))
        msgs()


if not POST_ONLY:
    material("PCB_eff", 55.0, 2100, 1000, kz=0.36)        # 4 x 70 um Cu (~80 % coverage) in 1.6 mm FR-4
    material("PCB_cell", 55.0, 2300, 900, kz=3.5)         # cell regions with 0.3 mm via arrays (~0.8 % Cu)
    material("GaN_die", 108.0, 2330, 700)                 # device body: R_th,jc(top) ~ 0.2 K/W
    material("Bumps", 5.1, 7000, 200)                     # solder-bar layer: R_th,jb ~ 1.5 K/W total
    material("TIM_pad", 17.8, 3000, 900)                  # 0.5 mm gap pad, 1.9 K/W per device footprint
    material("MLCC", 4.0, 5500, 500)


    def box(name, x0, x1, y0, y1, z0, z1, mat, color="(128 128 128)"):
        oEditor.CreateBox(["NAME:BoxParameters", "XPosition:=", "%gmm" % x0, "YPosition:=", "%gmm" % y0,
                           "ZPosition:=", "%gmm" % z0, "XSize:=", "%gmm" % (x1 - x0), "YSize:=", "%gmm" % (y1 - y0),
                           "ZSize:=", "%gmm" % (z1 - z0)],
                          ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", color, "Transparency:=", 0,
                           "PartCoordinateSystem:=", "Global", "UDMId:=", "", "MaterialValue:=", "\"%s\"" % mat,
                           "SurfaceMaterialValue:=", "\"Steel-oxidised-surface\"", "SolveInside:=", True,
                           "IsMaterialEditable:=", True, "UseMaterialAppearance:=", False, "IsLightweight:=", False])
        return name


    def block_power(name, objs, watts):
        try:
            oBnd.AssignBlockBoundary(["NAME:" + name, "Objects:=", objs, "Block Type:=", "Solid",
                                      "Use External Conditions:=", False, "Total Power:=", "%gW" % watts])
            log("block %s %.3f W ok" % (name, watts))
        except Exception as e:
            log("block %s failed: %r" % (name, e))
            msgs()


    # ---------------- board (cell regions with via arrays as separate solids) ----------------
    box("PCB", -XE, XE, Y0, Y1, 0, T_PCB, "PCB_eff", "(0 120 40)")
    cells = []
    for side, s in (("L", -1), ("R", 1)):
        x0, x1 = sorted((s * (P["xc"] - P["w_cell"] / 2), s * (P["xc"] + P["w_cell"] / 2)))
        cells.append(box("Cell_" + side, x0, x1, Y["dcp"][0], Y["src"][1], 0, T_PCB, "PCB_cell", "(0 150 60)"))
    try:
        oEditor.Subtract(["NAME:Selections", "Blank Parts:=", "PCB", "Tool Parts:=", ",".join(cells)],
                         ["NAME:SubtractParameters", "KeepOriginals:=", True])
        log("subtract ok")
    except Exception as e:
        log("subtract failed: %r" % e)

    # ---------------- devices, TIM, heat sink ----------------
    fets, bumps = [], []
    for side, s in (("L", -1), ("R", 1)):
        xc = s * P["xc"]
        for nm, yc in (("QH", yqh), ("QL", yql)):
            bumps.append(box("Bump_%s_%s" % (nm, side), xc - 2.5, xc + 2.5, yc - 1.5, yc + 1.5, T_PCB, T_PCB + 0.1, "Bumps", "(200 200 200)"))
            fets.append(box("%s_%s" % (nm, side), xc - 2.5, xc + 2.5, yc - 1.5, yc + 1.5, T_PCB + 0.1, T_PCB + 0.65, "GaN_die", "(30 30 30)"))
        box("TIM_" + side, xc - 2.75, xc + 2.75, yqh - 1.75, yql + 1.75, T_PCB + 0.65, T_PCB + 1.15, "TIM_pad", "(230 180 60)")
        box("Pedestal_" + side, xc - 2.75, xc + 2.75, yqh - 1.75, yql + 1.75, T_PCB + 1.15, 4.3, "Al-Extruded", "(190 190 200)")
    box("ColdPlate", -XE, XE, Y0, Y1, 4.3, 7.3, "Al-Extruded", "(170 170 185)")
    if COOL == "both":
        material("GapPad_bottom", 3.0, 3000, 900)
        box("BottomPad", -XE, XE, Y0, Y1, -1.0, 0.0, "GapPad_bottom", "(230 180 60)")
        box("BottomPlate", -XE, XE, Y0, Y1, -4.0, -1.0, "Al-Extruded", "(170 170 185)")
    try:
        oEditor.Unite(["NAME:Selections", "Selections:=", "ColdPlate,Pedestal_L,Pedestal_R"], ["NAME:UniteParameters", "KeepOriginals:=", False])
        log("unite heatsink ok")
    except Exception as e:
        log("unite failed: %r" % e)

    # ---------------- capacitors and driver ----------------
    caps = {"local_L": [], "local_R": [], "row1": [], "row2": [], "row3": []}
    for k, (side, s) in enumerate((("L", -1), ("R", 1))):
        for i in range(6):
            x = s * P["xc"] + (i - 2.5) * P["cap_p"]
            caps["local_" + side].append(box("C0805_%s%d" % (side, i), x - 0.625, x + 0.625, Y["capn"][0], Y["capp"][1],
                                             T_PCB, T_PCB + 1.25, "MLCC", "(150 110 80)"))
    for r, g0 in enumerate((Y["p1"][1], Y["n1"][1], Y["p2"][1])):
        gc = g0 + P["gap"] / 2
        for s in (-1, 1):
            for j, xb in enumerate(P["bank_x"]):
                x = s * xb
                caps["row%d" % (r + 1)].append(box("C1210_%d_%s%d" % (r + 1, "LR"[s > 0], j), x - 1.25, x + 1.25, gc - 1.6, gc + 1.6,
                                                   T_PCB, T_PCB + 2.5, "MLCC", "(150 110 80)"))
    drv = box("Driver", -1.0, 1.0, Y["ac"][0] + 0.6, Y["ac"][0] + 2.6, T_PCB, T_PCB + 0.5, "GaN_die", "(20 20 20)")

    # ---------------- region (air, conduction only) ----------------
    try:
        oEditor.CreateRegion(["NAME:RegionParameters",
                              "+XPaddingType:=", "Percentage Offset", "+XPadding:=", "20",
                              "-XPaddingType:=", "Percentage Offset", "-XPadding:=", "20",
                              "+YPaddingType:=", "Percentage Offset", "+YPadding:=", "20",
                              "-YPaddingType:=", "Percentage Offset", "-YPadding:=", "20",
                              "+ZPaddingType:=", "Percentage Offset", "+ZPadding:=", "0",
                              "-ZPaddingType:=", "Percentage Offset", "-ZPadding:=", "50"],
                             ["NAME:Attributes", "Name:=", "Region", "Flags:=", "Wireframe#", "Color:=", "(143 175 143)",
                              "Transparency:=", 0.8, "PartCoordinateSystem:=", "Global", "UDMId:=", "",
                              "MaterialValue:=", "\"air\"", "SurfaceMaterialValue:=", "\"\"", "SolveInside:=", True,
                              "IsMaterialEditable:=", True, "UseMaterialAppearance:=", False, "IsLightweight:=", False])
        log("region ok")
    except Exception as e:
        log("region failed: %r" % e)
        msgs()

    # ---------------- boundaries ----------------
    for f in fets:
        block_power("P_" + f, [f], P_DEV)
    P_CELL = 1.0
    block_power("P_cells", cells, 2 * P_CELL)
    block_power("P_pcb", ["PCB"], P_CU - 2 * P_CELL)
    for g, objs in caps.items():
        block_power("P_" + g, objs, P_CAP[g])
    block_power("P_driver", [drv], r50["gate"])

    top = None
    try:
        top = oEditor.GetFaceByPosition(["NAME:FaceParameters", "BodyName:=", "ColdPlate", "XPosition:=", "0mm",
                                         "YPosition:=", "0mm", "ZPosition:=", "7.3mm"])
        log("cold-plate top face %s" % top)
    except Exception as e:
        log("face lookup failed: %r" % e)
    variants = [
        ("AssignStationaryWallBoundary", ["NAME:ColdPlate60", "Faces:=", [top], "Thickness:=", "0mm", "Solid Material:=", "Al-Extruded",
                                          "External Condition:=", "Temperature", "Temperature:=", "60cel", "Radiate:=", False]),
        ("AssignStationaryWallBoundary", ["NAME:ColdPlate60", "Faces:=", [top], "Thickness:=", "0mm", "Solid Material:=", "Al-Extruded",
                                          "External Condition:=", "Temperature", "Temperature:=", "60cel", "Radiate:=", False,
                                          "RadiateTo:=", "AllObjects", "Surface Material:=", "Steel-oxidised-surface"]),
        ("AssignSourceBoundary", ["NAME:ColdPlate60", "Faces:=", [top], "Thermal Condition:=", "Fixed Temperature",
                                  "Temperature:=", "60cel", "Voltage Current - Enabled:=", False]),
        ("AssignSourceBoundary", ["NAME:ColdPlate60", "Faces:=", [top], "Thermal Condition:=", "Temperature",
                                  "Temperature:=", "60cel", "Voltage Current - Enabled:=", False]),
    ]
    walls = [(top, "ColdPlate60")]
    if COOL == "both":
        bot = oEditor.GetFaceByPosition(["NAME:FaceParameters", "BodyName:=", "BottomPlate", "XPosition:=", "0mm",
                                         "YPosition:=", "0mm", "ZPosition:=", "-4mm"])
        walls.append((bot, "BottomPlate60"))
    for fn, args in variants:
        try:
            for face, nm in walls:
                a = list(args)
                a[0], a[2] = "NAME:" + nm, [face]
                getattr(oBnd, fn)(a)
            log("cold plate(s) via %s ok" % fn)
            break
        except Exception as e:
            log("cold plate %s failed: %r" % (fn, e))
            msgs()

    try:
        oDesign.SetDesignSettings(["NAME:Design Settings Data", "Perform Minimal validation:=", False,
                                   "Default Fluid Material:=", "air", "Default Solid Material:=", "Al-Extruded",
                                   "Default Surface Material:=", "Steel-oxidised-surface", "AmbientTemperature:=", "60cel",
                                   "AmbientPressure:=", "0n_per_meter_sq", "AmbientRadiationTemperature:=", "60cel",
                                   "Gravity Vector CS ID:=", 1, "Gravity Vector Axis:=", "Z", "Positive:=", False],
                                  ["NAME:Model Validation Settings", "EntityCheckLevel:=", "Strict",
                                   "IgnoreUnclassifiedObjects:=", False, "SkipIntersectionChecks:=", False])
        log("design settings ok (ambient 60 C)")
    except Exception as e:
        log("design settings failed: %r" % e)
        msgs()

    # ---------------- setup (temperature only) and solve ----------------
    setup = ["NAME:Setup1", "Enabled:=", True, "Flow Regime:=", "Laminar", "Include Temperature:=", True,
             "Include Flow:=", False, "Include Gravity:=", False, "Solution Initialization - Temperature:=", "AmbientTemp",
             "Convergence Criteria - Energy:=", "1e-07", "Radiation Model:=", "Off",
             "Convergence Criteria - Max Iterations:=", 300, "Sequential Solve of Flow and Energy Equations:=", False]
    try:
        oDesign.GetModule("AnalysisSetup").InsertSetup("IcepakSteadyState", setup)
        log("setup ok")
    except Exception as e:
        log("setup failed: %r" % e)
        msgs()
    oProject.Save()
    try:
        oDesign.Analyze("Setup1")
        log("analyzed")
    except Exception as e:
        log("analyze failed: %r" % e)
    msgs()
    oProject.Save()

# ---------------- results: max temperature per object ----------------
oFR = oDesign.GetModule("FieldsReporter")
fets = ["QH_L", "QL_L", "QH_R", "QL_R"]
cells = ["Cell_L", "Cell_R"]
objs = fets + ["PCB"] + cells + ["ColdPlate", "TIM_L", "TIM_R", "Driver", "C0805_R0", "C1210_3_R0", "C1210_1_R0"]
res = {}
for o in objs:
    try:
        oFR.CalcStack("clear")
        oFR.EnterQty("Temp")
        oFR.EnterVol(o)
        oFR.CalcOp("Maximum")
        oFR.ClcEval("Setup1 : SteadyState", [], "Fields")
        v = oFR.GetTopEntryValue("Setup1 : SteadyState", [])
        oFR.CalcStack("clear")
        res[o] = float(list(v)[0])
        log("Tmax %s = %.2f" % (o, res[o]))
    except Exception as e:
        log("calc %s failed: %r" % (o, e))
with open(os.path.join(OUT, "icepak_results%s.txt" % SUF), "w") as f:
    for k, v in res.items():
        f.write("%s %.2f\n" % (k, v))

# ---------------- images ----------------
plot_objs = [o for o in objs if o not in ("ColdPlate", "TIM_L", "TIM_R")]
for k in ("local_L", "local_R", "row1", "row2", "row3"):
    pass
try:
    allsolids = list(oEditor.GetObjectsInGroup("Solids"))
    plot_objs = [o for o in allsolids if o not in ("ColdPlate", "TIM_L", "TIM_R", "Region", "BottomPlate", "BottomPad")]
except Exception as e:
    log("solids: %r" % e)
faces = []
for o in plot_objs:
    try:
        faces += [int(f) for f in oEditor.GetFaceIDs(o)]
    except Exception as e:
        log("faces %s: %r" % (o, e))
try:
    oFR.CreateFieldPlot(["NAME:Temp_surfaces", "SolutionName:=", "Setup1 : SteadyState", "UserSpecifyName:=", 0,
                         "UserSpecifyFolder:=", 0, "QuantityName:=", "Temperature", "PlotFolder:=", "Temperature",
                         "StreamlinePlot:=", False, "AdjacentSidePlot:=", False, "FullModelPlot:=", False,
                         "IntrinsicVar:=", "", "PlotGeomInfo:=", [1, "Surface", "FacesList", len(faces)] + faces,
                         "FilterBoxes:=", [0], ["NAME:PlotOnSurfaceSettings", "Filled:=", False, "IsoValType:=", "Fringe",
                                                "AddGrid:=", False, "MapTransparency:=", True, "Refinement:=", 0,
                                                "Transparency:=", 0, "SmoothingLevel:=", 0,
                                                ["NAME:Arrow3DSpacingSettings", "ArrowUniform:=", True, "ArrowSpacing:=", 0,
                                                 "MinArrowSpacing:=", 0, "MaxArrowSpacing:=", 0],
                                                "GridColor:=", [255, 255, 255]], "EnableGaussianSmoothing:=", False,
                         "SurfaceOnly:=", True], "Field")
    log("field plot ok")
except Exception as e:
    log("field plot failed: %r" % e)
    msgs()
# temperature on grids (board mid-plane and device layer) for plotting outside AEDT
for tag, z in (("board", 0.8), ("devices", 2.0)):
    fn = os.path.join(OUT, "grid_%s%s.fld" % (tag, SUF))
    done = False
    for variant in range(2):
        try:
            oFR.CalcStack("clear")
            oFR.EnterQty("Temp")
            start, stop, step = ["%gmm" % -XE, "%gmm" % Y0, "%gmm" % z], ["%gmm" % XE, "%gmm" % Y1, "%gmm" % z], ["0.25mm", "0.25mm", "0mm"]
            if variant == 0:
                oFR.ExportOnGrid(fn, start, stop, step, "Setup1 : SteadyState", [], True, "Cartesian", ["0mm", "0mm", "0mm"], False)
            else:
                oFR.ExportOnGrid(fn, start, stop, step, "Setup1 : SteadyState", [])
            log("grid %s ok (variant %d)" % (tag, variant))
            done = True
            break
        except Exception as e:
            log("grid %s variant %d failed: %r" % (tag, variant, e))
    if not done:
        msgs()
for o in ["ColdPlate", "Region", "TIM_L", "TIM_R", "BottomPlate", "BottomPad"]:
    try:
        oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", o],
                                                 ["NAME:ChangedProps", ["NAME:Transparent", "Value:=", 0.9]]]])
    except Exception as e:
        log("transparency %s: %r" % (o, e))
for name, orient in (("icepak_temperature_iso", "Isometric"), ("icepak_temperature_top", "Top")):
    try:
        oEditor.ExportModelImageToFile(os.path.join(OUT, name + SUF + ".png"), 1800, 1300,
                                       ["NAME:SaveImageParams", "ShowAxis:=", "False", "ShowGrid:=", "False",
                                        "ShowRuler:=", "False", "ShowRegion:=", "False", "Selections:=", "",
                                        "FieldPlotSelections:=", "Temp_surfaces", "Orientation:=", orient])
        log("image %s ok" % name)
    except Exception as e:
        log("image %s failed: %r" % (name, e))
oProject.Save()
LOG.close()

# -*- coding: utf-8 -*-
"""
Re-export results from an already-solved results/dpt_cell_q3d.aedt (no re-solve),
e.g. after changing variables and re-solving a design in the AEDT GUI.

    run_q3d.cmd export
"""
import os
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
OUT = os.path.join(HERE, "results")
LOG = open(os.path.join(OUT, "q3d_export_log.txt"), "w")

DESIGNS = {
    "PL_shunt": ["DCP:CapP", "AC:QH_S", "SQL:QL_S", "DCN:SH_out"],
    "PL_noshunt": ["DCP:CapP", "AC:QH_S", "DCN:QL_S"],
    "GL_near": ["G:DrvOut", "KS:Kelvin"],
    "GL_far": ["G:DrvOut", "KS:Kelvin"],
}

oProject = oDesktop.OpenProject(os.path.join(OUT, "dpt_cell_q3d.aedt"))
for name, terms in DESIGNS.items():
    try:
        design = oProject.SetActiveDesign(name)
        exprs = ["Lloop"] + ["ACL(%s,%s)" % (a, b) for a in terms for b in terms]
        rep = design.GetModule("ReportSetup")
        title = "LR_" + name
        if title not in list(rep.GetAllReportNames()):
            rep.CreateReport(title, "Matrix", "Data Table", "Setup1 : LastAdaptive",
                             ["Context:=", "Original"], ["Freq:=", ["100MHz"]],
                             ["X Component:=", "Freq", "Y Component:=", exprs])
        rep.ExportToFile(title, os.path.join(OUT, name + ".csv"))
        design.ExportMatrixData(os.path.join(OUT, name + "_matrix.txt"), "C, DC RL, AC RL", "",
                                "Setup1:LastAdaptive", "Original", "ohm", "nH", "pF", "mSie",
                                100000000, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
        LOG.write("%s: exported\n" % name)
    except Exception as e:
        LOG.write("%s FAILED: %r\n" % (name, e))
oProject.Save()
LOG.close()

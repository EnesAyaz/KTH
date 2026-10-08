# -*- coding: utf-8 -*-
"""
Frequency sweep of the 2 oz building-block power loop (BB_PL in results/bb_q3d_2oz.aedt) for the
switching-frequency copper loss.

    simulation\\bb_q3d\\run_bb_q3d_sweep.cmd     (needs the KTH licence: campus network or VPN)

Opens a copy of the 2 oz project (results/bb_q3d_2oz_sweep.aedt), adds a discrete frequency sweep to Setup1,
solves, and exports the DC and AC R/L matrices at each sweep frequency to results/sweep/BB_PL_2oz_f<Hz>.txt.
Q3D combines its DC and AC (skin-effect) RL solutions to give R(f), L(f) between DC and the adaptive frequency.
"""
import os
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
RES = os.path.join(HERE, "results")
OUT = os.path.join(RES, "sweep")
if not os.path.isdir(OUT):
    os.makedirs(OUT)
LOG = open(os.path.join(OUT, "sweep_log.txt"), "w")


def log(msg):
    LOG.write(str(msg) + "\n")
    LOG.flush()


FREQS = [1e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6, 2e6, 5e6, 1e7, 1e8]


def fstr(f):
    return "%gHz" % f


oProject = oDesktop.OpenProject(os.path.join(RES, "bb_q3d_2oz_sweep.aedt"))
oDesign = oProject.SetActiveDesign("BB_PL")
oModule = oDesign.GetModule("AnalysisSetup")
log("opened, setups: %s" % list(oModule.GetSetups()))

points = ",".join(fstr(f) for f in FREQS)
variants = [
    ["NAME:Sweep1", "IsEnabled:=", True, "RangeType:=", "SinglePoints", "RangeStart:=", fstr(FREQS[0]),
     "RangeEnd:=", fstr(FREQS[0]), "Type:=", "Discrete", "SaveFields:=", False, "SaveRadFields:=", False,
     "AdditionalPoints:=", points],
    ["NAME:Sweep1", "IsEnabled:=", True, "RangeType:=", "LogScale", "RangeStart:=", "1kHz", "RangeEnd:=", "100MHz",
     "RangeCount:=", 1, "RangeSamples:=", 4, "Type:=", "Discrete", "SaveFields:=", False, "SaveRadFields:=", False],
    ["NAME:Sweep1", "IsEnabled:=", True, "RangeType:=", "LogScale", "RangeStart:=", "1kHz", "RangeEnd:=", "100MHz",
     "RangeCount:=", 1, "RangeSamples:=", 4, "Type:=", "Interpolating", "SaveFields:=", False,
     "InterpTolerance:=", 0.5, "InterpMaxSolns:=", 250, "InterpMinSolns:=", 0, "InterpMinSubranges:=", 1],
]
ok = False
for k, v in enumerate(variants):
    try:
        oModule.InsertSweep("Setup1", v)
        log("InsertSweep variant %d accepted" % k)
        ok = True
        break
    except Exception as e:
        log("InsertSweep variant %d failed: %r" % (k, e))
if ok:
    try:
        oDesign.Analyze("Setup1")
        log("analyzed")
    except Exception as e:
        log("Analyze failed: %r" % e)
    try:
        log("solved sweep freqs: %s" % list(oDesign.GetModule("Solutions").GetSolveRangeInfo("Setup1:Sweep1")))
    except Exception as e:
        log("GetSolveRangeInfo: %r" % e)
    for f in FREQS:
        fn = os.path.join(OUT, "BB_PL_2oz_f%d.txt" % int(f))
        try:
            oDesign.ExportMatrixData(fn, "DC RL, AC RL", "", "Setup1:Sweep1", "Original", "ohm", "nH", "pF", "mSie",
                                     f, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
            log("exported %s" % fn)
        except Exception as e:
            log("export %g failed: %r" % (f, e))
oProject.Save()
LOG.close()

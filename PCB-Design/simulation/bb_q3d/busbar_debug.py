import os
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
p = r"C:\Github\KTH\PCB-Design\simulation\bb_q3d\results\bb_q3d_busbar.aedt"
out = open(r"C:\Github\KTH\PCB-Design\simulation\bb_q3d\results\busbar_debug.txt", "w")
proj = oDesktop.OpenProject(p)
d = proj.SetActiveDesign("BB_BUS")
try:
    out.write("validate: %r\n" % d.ValidateDesign())
except Exception as e:
    out.write("validate exc %r\n" % e)
for m in oDesktop.GetMessages(proj.GetName(), "BB_BUS", 0):
    out.write(m + "\n")
bnd = d.GetModule("BoundarySetup")
out.write("excitations: %r\n" % (bnd.GetExcitations(),))
out.close()
oDesktop.CloseProject(proj.GetName())

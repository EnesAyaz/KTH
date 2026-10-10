# -*- coding: utf-8 -*-
"""
Export 3D pictures of the Q3D building-block models (no solve).

    simulation\\bb_q3d\\run_bb_q3d_images.cmd

Opens a copy of results/bb_q3d_2oz.aedt, colours the nets (DC+ red, DC- blue, AC yellow) and writes
results/images/q3d_power_loop_iso.png, q3d_power_loop_xray.png (DC- semi-transparent) and q3d_gate_star.png.
"""
import os
import ScriptEnv

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
RES = os.path.join(HERE, "results")
IMG = os.path.join(RES, "images")
if not os.path.isdir(IMG):
    os.makedirs(IMG)
LOG = open(os.path.join(IMG, "images_log.txt"), "w")


def log(m):
    LOG.write(str(m) + "\n")
    LOG.flush()


PROJ = {"BB_PL": "bb_q3d_2oz_images.aedt", "BB_GL": "bb_q3d_images.aedt"}
COL = {"DCP": (215, 40, 40), "DCN": (40, 90, 215), "AC": (235, 185, 30), "G": (40, 160, 60), "KS": (130, 60, 170)}


def colour(ed, obj, rgb, transp=None):
    for props in (["NAME:Color", "R:=", rgb[0], "G:=", rgb[1], "B:=", rgb[2]],
                  ["NAME:Color", "Value:=", "(%d %d %d)" % rgb]):
        try:
            ed.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", obj],
                                                ["NAME:ChangedProps", props]]])
            break
        except Exception as e:
            log("colour %s %s: %r" % (obj, props[1], e))
    if transp is not None:
        try:
            ed.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", obj],
                                                ["NAME:ChangedProps", ["NAME:Transparent", "Value:=", transp]]]])
        except Exception as e:
            log("transparency %s: %r" % (obj, e))


def image(ed, name, orient="Isometric"):
    for args in (["NAME:SaveImageParams", "ShowAxis:=", "False", "ShowGrid:=", "False", "ShowRuler:=", "False",
                  "ShowRegion:=", "False", "Selections:=", "", "Orientation:=", orient],
                 ["NAME:SaveImageParams", "ShowAxis:=", "False", "ShowGrid:=", "False", "ShowRuler:=", "False",
                  "ShowRegion:=", "False", "Selections:=", ""]):
        try:
            ed.ExportModelImageToFile(os.path.join(IMG, name + ".png"), 1800, 1300, args)
            log("image %s ok" % name)
            return
        except Exception as e:
            log("image %s failed: %r" % (name, e))


def net_of(design, obj):
    try:
        mod = design.GetModule("BoundarySetup")
        for net in mod.GetExcitationsOfType("Net"):
            if obj in list(mod.GetExcitationAssignment(net)):
                return net
    except Exception as e:
        log("net lookup: %r" % e)
    return None


for dname, tag in (("BB_PL", "q3d_power_loop"), ("BB_GL", "q3d_gate_star")):
    try:
        oProject = oDesktop.OpenProject(os.path.join(RES, PROJ[dname]))
        d = oProject.SetActiveDesign(dname)
        ed = d.SetActiveEditor("3D Modeler")
        objs = list(ed.GetObjectsInGroup("Solids"))
        log("%s solids: %s" % (dname, objs))
        nets = {}
        for o in objs:
            n = net_of(d, o)
            if n is None:
                n = {"P1": "DCP", "N1": "DCN", "AC_L": "AC", "G_trunk": "G"}.get(o, "KS" if dname == "BB_GL" else "AC")
            nets[o] = n
            colour(ed, o, COL.get(n, (160, 160, 160)))
        log("nets %s" % nets)
        image(ed, tag + "_iso")
        image(ed, tag + "_top", "Top")
        if dname == "BB_PL":
            for o, n in nets.items():
                if n == "DCN":
                    colour(ed, o, COL["DCN"], 0.75)
            image(ed, tag + "_xray")
        oProject.Close()
    except Exception as e:
        log("%s failed: %r" % (dname, e))
LOG.close()

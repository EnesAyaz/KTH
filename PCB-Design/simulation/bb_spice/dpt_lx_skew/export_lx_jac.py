"""
Geometry export for the L_x extraction of the current DPT board with the load terminal. Runs simulation/bb_q3d/revb_export.py
unchanged except for one in-memory edit: in the LX region the AC bolt pad (J_AC) stays in the model as a source terminal, so the
matrix holds the path from each switch node to the load connection as well as the paths between the switch nodes.
Same environment as run_bb_q3d_final.cmd lx_dpt, tag dpt_swv1. Run with the KiCad python.
"""
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "bb_q3d", "revb_export.py")
P = os.path.abspath(P)
src = open(P, encoding="utf-8").read()
a = '(not CROP or (BANK and f.GetValue() != "AC"))'
b = '(not CROP or (BANK and f.GetValue() != "AC") or (REGION == "lx" and f.GetValue() == "AC"))'
assert src.count(a) == 1
__file__ = P
exec(compile(src.replace(a, b), P, "exec"))

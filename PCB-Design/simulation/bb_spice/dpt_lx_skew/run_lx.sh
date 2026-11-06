#!/bin/bash
# L_x extraction of the current DPT board (SW vias), same setup as run_bb_q3d_final.cmd lx_dpt, plus the J_AC load terminal.
cd /c/Github/KTH/PCB-Design/simulation/bb_q3d
AEDT="/c/Program Files/AnsysEM/v242/Win64/ansysedt.exe"
KPY="/c/Program Files/KiCad/7.0/bin/python.exe"
export REVB_BOARD="$(cygpath -w $PWD/../../hardware/spb-bb-revb-dpt/spb-bb-revb-dpt.kicad_pcb)"
export REVB_LOOP_TAG=dpt_swv1 REVB_REGION=lx REVB_SOLVE= REVB_AC_VIA_EVERY=3
if [ "$1" != "solve" ]; then
  "$KPY" "$(cygpath -w $PWD/../bb_spice/dpt_lx_skew/export_lx_jac.py)" || exit 1
fi
if [ "$1" != "export" ]; then
  echo "[$(date +%H:%M:%S)] start lx dpt_swv1" >> ../bb_spice/dpt_lx_skew/lx_progress.txt
  "$AEDT" -ng -RunScriptAndExit "$(cygpath -w $PWD/bb_q3d_revb.py)"
  echo "[$(date +%H:%M:%S)] aedt exit $?" >> ../bb_spice/dpt_lx_skew/lx_progress.txt
fi

#!/bin/bash
# M1(c): L_x extraction of the committed DPT board with bank, J1/J2 and J_AC as terminals. Same setup as dpt_lx_skew/run_lx.sh, tag dpt_swv1dc.
cd /c/Github/KTH/PCB-Design/simulation/bb_q3d
AEDT="/c/Program Files/AnsysEM/v242/Win64/ansysedt.exe"
KPY="/c/Program Files/KiCad/7.0/bin/python.exe"
export REVB_BOARD="$(cygpath -w $PWD/../../hardware/spb-bb-revb-dpt/spb-bb-revb-dpt.kicad_pcb)"
export REVB_LOOP_TAG=dpt_swv1dc REVB_REGION=lx REVB_SOLVE= REVB_AC_VIA_EVERY=3
if [ "$1" != "solve" ]; then
  "$KPY" "$(cygpath -w $PWD/../bb_spice/dpt_m1_checks/export_lxdc.py)" || exit 1
fi
if [ "$1" != "export" ]; then
  echo "[$(date +%H:%M:%S)] start lx dpt_swv1dc" >> ../bb_spice/dpt_m1_checks/lxdc_progress.txt
  "$AEDT" -ng -RunScriptAndExit "$(cygpath -w $PWD/bb_q3d_revb.py)"
  echo "[$(date +%H:%M:%S)] aedt exit $?" >> ../bb_spice/dpt_m1_checks/lxdc_progress.txt
fi

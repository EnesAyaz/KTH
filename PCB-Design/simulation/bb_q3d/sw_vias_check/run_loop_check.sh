#!/bin/bash
cd /c/Github/KTH/PCB-Design/simulation/bb_q3d
AEDT="/c/Program Files/AnsysEM/v242/Win64/ansysedt.exe"
P=results/final_progress.txt
export REVB_REGION=loop REVB_SOLVE=
for t in "$@"; do
  export REVB_LOOP_TAG=$t
  echo "[$(date +%H:%M:%S)] step loop $t (SW-via check, sim-analyst; same setup as loop_dpt)" >> $P
  "$AEDT" -ng -RunScriptAndExit "$(cygpath -w $PWD/bb_q3d_revb.py)"
  echo "aedt exit $? for $t"
  echo "[$(date +%H:%M:%S)] done loop $t" >> $P
done

#!/bin/bash
S=$(cd "$(dirname "$0")" && pwd)
export SWAC_DIR=$(cygpath -w $S)
cd $S
AEDT="/c/Program Files/AnsysEM/v242/Win64/ansysedt.exe"
export REVB_REGION=swac REVB_SOLVE=
for pl in 0 0.025; do for t in swv0 swv1; do
  export REVB_LOOP_TAG=$t SWAC_PLATE=$pl
  date; echo "run $t plate $pl"
  "$AEDT" -ng -RunScriptAndExit "$(cygpath -w $S/swac_q3d.py)"; echo "exit $?"
done; done
date

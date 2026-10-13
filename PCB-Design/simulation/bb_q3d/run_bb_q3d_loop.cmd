@echo off
rem Fast loop-only Q3D of the Rev B leg (cell band, bypass rows, shunts; no bank, no terminals), KTH licence.
rem   -> results/BB_PL_LOOP_matrix.txt, loop_summary.json (commutation loop per cell)
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
set KPY=C:\Program Files\KiCad\7.0\bin\python.exe
set REVB_REGION=loop
cd /d "%~dp0"
"%KPY%" revb_export.py
if exist results\bb_q3d_loop.aedtresults rmdir /s /q results\bb_q3d_loop.aedtresults
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_revb.py"
type results\loop_log.txt
"%KPY%" loop_post.py
endlocal

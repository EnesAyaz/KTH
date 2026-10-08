@echo off
rem Frequency sweep of the 2 oz building-block power loop for the switching-frequency copper loss.
rem Needs the KTH Ansys licence (campus or KTH VPN). Works on a copy of results\bb_q3d_2oz.aedt.
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
copy /y results\bb_q3d_2oz.aedt results\bb_q3d_2oz_sweep.aedt >nul
if exist results\bb_q3d_2oz_sweep.aedtresults rmdir /s /q results\bb_q3d_2oz_sweep.aedtresults
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_sweep.py"
type results\sweep\sweep_log.txt
endlocal

@echo off
rem Q3D power loop of the routed fabrication board (KTH Ansys licence). Run fab_export.py first.
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
"C:\Program Files\KiCad\7.0\bin\python.exe" fab_export.py
if exist results\bb_q3d_fab.aedtresults rmdir /s /q results\bb_q3d_fab.aedtresults 2>nul
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_fab.py"
type results\fab_log.txt
endlocal

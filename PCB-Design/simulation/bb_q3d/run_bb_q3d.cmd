@echo off
rem Building-block Q3D (power loop + gate star). Needs the KTH Ansys licence (campus or KTH VPN).
rem   run_bb_q3d.cmd            build + solve BB_PL and BB_GL, then write the LTspice subcircuits
rem   run_bb_q3d.cmd only BB_GL rebuild one design (new project)
rem   run_bb_q3d.cmd spice      only rebuild the LTspice subcircuits from results\*_matrix.txt
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
if /i "%1"=="spice" goto spice
if /i "%1"=="only" set BB_ONLY=%2
if exist results rmdir /s /q results\bb_q3d.aedtresults 2>nul
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d.py"
type results\bb_log.txt
:spice
python bb_to_spice.py
endlocal

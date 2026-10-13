@echo off
rem Q3D of the PCB busbar (BB_BUS_PCB) and the Rev B leg (BB_PL_REVB), KTH Ansys licence; then revb_post.py.
rem   run_bb_q3d_revb.cmd [bus | leg | post]     (default: bus, leg and post)
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
set KPY=C:\Program Files\KiCad\7.0\bin\python.exe
cd /d "%~dp0"
if "%1"=="post" goto post
if "%1"=="leg" goto leg
"%KPY%" busbar_pcb_export.py
if exist results\bb_q3d_busbar_pcb.aedtresults rmdir /s /q results\bb_q3d_busbar_pcb.aedtresults
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_busbar_pcb.py"
type results\busbar_pcb_log.txt
if "%1"=="bus" goto post
:leg
"%KPY%" revb_export.py
if exist results\bb_q3d_revb.aedtresults rmdir /s /q results\bb_q3d_revb.aedtresults
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_revb.py"
type results\revb_log.txt
:post
"%KPY%" revb_post.py
endlocal

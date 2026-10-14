@echo off
rem Fast Q3D set of the two final Rev B boards and the PCB busbar (KTH Ansys licence), run one after the other:
rem   loop  : commutation loop per cell (cell band only)                      BB_PL_LOOP_<b>, loop_summary_<b>.json
rem   dc    : full board, DC R/L only (current sharing, copper loss, port)     BB_PL_REVB_<b>
rem   lx    : cells + AC bus, AC at 100 MHz (inductance between driver pairs) BB_PL_LX_<b>
rem   bus   : PCB busbar, stitching vias thinned, 2 %%                         BB_BUS_PCB
rem then final_post.py -> results/final_summary.json, reports/slides/data/final_numbers.json
rem   run_bb_q3d_final.cmd [step ...]   steps: loop_dpt loop_load dc_dpt dc_load bus lx_load lx_dpt post (default all)
setlocal enabledelayedexpansion
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
set KPY=C:\Program Files\KiCad\7.0\bin\python.exe
cd /d "%~dp0"
set STEPS=%*
if "%STEPS%"=="" set STEPS=loop_dpt loop_load dc_dpt dc_load bus lx_load lx_dpt post
for %%s in (%STEPS%) do (
  echo [%time%] step %%s >> results\final_progress.txt
  call :%%s
  echo [!time!] done %%s >> results\final_progress.txt
)
endlocal
goto :eof

:board
set REVB_BOARD=%~dp0..\..\hardware\spb-bb-revb-%1\spb-bb-revb-%1.kicad_pcb
set REVB_LOOP_TAG=%1
goto :eof

:solve
if exist results\bb_q3d_%1_%2.aedtresults rmdir /s /q results\bb_q3d_%1_%2.aedtresults
if exist results\bb_q3d_%1_%2.aedt.lock del results\bb_q3d_%1_%2.aedt.lock
"%KPY%" revb_export.py
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_revb.py"
goto :eof

:loop_dpt
call :board dpt & set REVB_REGION=loop& set REVB_SOLVE=& call :solve loop dpt & "%KPY%" loop_post.py
goto :eof
:loop_load
call :board load & set REVB_REGION=loop& set REVB_SOLVE=& call :solve loop load & "%KPY%" loop_post.py
goto :eof
:dc_dpt
call :board dpt & set REVB_REGION=& set REVB_SOLVE=dc& call :solve revb dpt
goto :eof
:dc_load
call :board load & set REVB_REGION=& set REVB_SOLVE=dc& call :solve revb load
goto :eof
:lx_dpt
call :board dpt & set REVB_REGION=lx& set REVB_SOLVE=& set REVB_AC_VIA_EVERY=3& call :solve lx dpt
goto :eof
:lx_load
call :board load & set REVB_REGION=lx& set REVB_SOLVE=& set REVB_AC_VIA_EVERY=3& call :solve lx load
goto :eof
:bus
"%KPY%" busbar_pcb_export.py
if exist results\bb_q3d_busbar_pcb.aedtresults rmdir /s /q results\bb_q3d_busbar_pcb.aedtresults
set BUS_STITCH_EVERY=2
set BUS_PERERROR=2
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_busbar_pcb.py"
goto :eof
:post
"%KPY%" final_post.py
goto :eof

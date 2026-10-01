@echo off
rem Run the DPT-cell Q3D model headless. Needs the KTH Ansys licence (campus or KTH VPN).
rem   run_q3d.cmd          build + solve all designs, export results (about 7 min)
rem   run_q3d.cmd export   only re-export results from the solved project
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
if /i "%1"=="export" (set SCRIPT=q3d_export.py) else (set SCRIPT=q3d_dpt_cell.py)
if /i not "%1"=="export" if exist results\dpt_cell_q3d.aedt (
  rmdir /s /q results\dpt_cell_q3d.aedtresults 2>nul
  del /q results\dpt_cell_q3d.aedt results\*.csv results\*_matrix.txt results\q3d_export_log.txt 2>nul
)
"%AEDT%" -ng -RunScriptAndExit "%~dp0%SCRIPT%"
type results\q3d_log.txt 2>nul
type results\q3d_export_log.txt 2>nul
python q3d_to_spice.py
endlocal

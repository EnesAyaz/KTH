@echo off
rem Run the DPT power-loop Q3D model headless. Needs the KTH Ansys licence (campus or KTH VPN).
rem   run_q3d.cmd          build + solve PL_A, PL_B, PL_C (+ h_23 sweep), export, LTspice files (~25 min)
rem   run_q3d.cmd spice    only rebuild LTspice files / summary from results\*_matrix.txt
rem   run_q3d.cmd only PL_C   rebuild + solve one design (comma list) in the existing project
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
set LTSPICE=%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe
cd /d "%~dp0"
if /i "%1"=="spice" goto spice
if /i "%1"=="only" (
  set Q3D_ONLY=%2
  "%AEDT%" -ng -RunScriptAndExit "%~dp0q3d_dpt_cell.py"
  type results\q3d_log.txt
  goto spice
)
if exist results (
  rmdir /s /q results\dpt_cell_q3d.aedtresults 2>nul
  del /q results\*.aedt results\*.csv results\*.txt results\*.lib results\*.cir results\*.log results\*.raw 2>nul
)
"%AEDT%" -ng -RunScriptAndExit "%~dp0q3d_dpt_cell.py"
type results\q3d_log.txt
:spice
python q3d_to_spice.py
rem LTspice cross-check of every *_test.cir (writes *_test.log with Lloop_nH)
pushd results
for %%f in (*_test.cir) do "%LTSPICE%" -b "%%f"
for %%f in (*_test.log) do (echo %%f & findstr /i "lloop_nh" "%%f")
popd
endlocal

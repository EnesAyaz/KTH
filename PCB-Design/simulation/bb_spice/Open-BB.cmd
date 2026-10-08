@echo off
rem Open the building-block schematics in LTspice (BB_DPT.asc; others: BB_energy_sweep.asc, BB_rg_slow.asc)
cd /d "%~dp0"
set ASC=%1
if "%ASC%"=="" set ASC=BB_DPT.asc
start "" "%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe" "%~dp0%ASC%"

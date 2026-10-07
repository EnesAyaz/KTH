@echo off
rem Batch-run the double-pulse test and print the .meas results.
rem To look at waveforms, open DPT_PL_A.cir in LTspice instead and press Run.
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe" -b -alt DPT_PL_A.cir
type DPT_PL_A.log

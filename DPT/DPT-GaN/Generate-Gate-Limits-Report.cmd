@echo off
cd /d "%~dp0"
python search_gate_limits.py
if errorlevel 1 goto failure
python check_gate_search.py
if errorlevel 1 goto failure
python build_gate_report.py
if errorlevel 1 goto failure
start "" "dut_gate_search\output\pdf\DUT_Gate_Resistance_Limits.pdf"
exit /b 0
:failure
echo Report generation failed. See the error above.
pause
exit /b 1

@echo off
cd /d "%~dp0"
start "" "%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe" -alt -Run "%~dp0LMG1210_PWM_test.asc"

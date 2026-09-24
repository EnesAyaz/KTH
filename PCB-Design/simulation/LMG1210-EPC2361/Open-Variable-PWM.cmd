@echo off
cd /d "%~dp0"
start "" "%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe" -alt "%~dp0HalfBridge_Variable_PWM.asc"

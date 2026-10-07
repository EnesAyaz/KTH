@echo off
cd /d "%~dp0"
start "" "%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe" -alt "%~dp0Sharing_2xEPC2361.asc"

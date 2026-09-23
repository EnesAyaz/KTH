@echo off
pushd "%~dp0"
python ltspice_gui.py
if errorlevel 1 pause
popd

@echo off
pushd "%~dp0"
python half_bridge_gui.py
if errorlevel 1 pause
popd

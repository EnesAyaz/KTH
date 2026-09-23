@echo off
pushd "%~dp0"
python dpt_gui.py
if errorlevel 1 pause
popd

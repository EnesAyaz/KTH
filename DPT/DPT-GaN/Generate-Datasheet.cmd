@echo off
pushd "%~dp0"
python datasheet_sweep.py
if errorlevel 1 goto failed
python build_datasheet.py
if errorlevel 1 goto failed
start "" "%~dp0dpt_datasheet_75V\output\pdf\EPC2361_DPT_Report.pdf"
popd
exit /b 0
:failed
pause
popd
exit /b 1

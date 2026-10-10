@echo off
rem Common-source inductance: combined power loop + gate star + Kelvin return (BB_CS) and without Kelvin (BB_CS_noK).
rem Needs the KTH Ansys licence (campus or KTH VPN). Post-processing: python cs_post.py
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
if /i "%1"=="only" set CS_ONLY=%2
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_cs.py"
type results\cs_log.txt
python cs_post.py
endlocal

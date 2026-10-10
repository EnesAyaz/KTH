@echo off
rem Icepak steady-state thermal model of the building block. Needs the KTH Ansys licence (campus or KTH VPN).
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
if exist results\bb_icepak.aedtresults rmdir /s /q results\bb_icepak.aedtresults
if exist results\bb_icepak.aedt del results\bb_icepak.aedt
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_icepak.py"
type results\icepak_log.txt
endlocal

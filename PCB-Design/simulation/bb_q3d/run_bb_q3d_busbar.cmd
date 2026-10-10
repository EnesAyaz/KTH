@echo off
rem Laminated DC busbar of one SPB cell (KTH Ansys licence). Post-processing: python busbar_post.py
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_busbar.py"
type results\busbar_log.txt
python busbar_post.py
endlocal

@echo off
rem Export 3D pictures of the Q3D building-block models (works on a copy of results\bb_q3d_2oz.aedt, no solve).
setlocal
set AEDT=C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe
cd /d "%~dp0"
copy /y results\bb_q3d_2oz.aedt results\bb_q3d_2oz_images.aedt >nul
copy /y results\bb_q3d.aedt results\bb_q3d_images.aedt >nul
"%AEDT%" -ng -RunScriptAndExit "%~dp0bb_q3d_images.py"
type results\images\images_log.txt
endlocal

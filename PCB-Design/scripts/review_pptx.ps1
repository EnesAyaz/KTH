# Build the PPTX and export every slide + 3x2 contact sheets to %TEMP%\decknew (visual review).
Set-Location C:\Github\KTH\PCB-Design
$r = powershell -ExecutionPolicy Bypass -File scripts\build_pptx.ps1 2>&1; $r | Select-Object -Last 3
$o="$env:TEMP\decknew"; Remove-Item -Recurse -Force $o -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force $o | Out-Null
$pp=New-Object -ComObject PowerPoint.Application; $p=$pp.Presentations.Open("C:\Github\KTH\PCB-Design\reports\slides\spb_revb_design_flow.pptx",$true,$false,$false)
$i=0; foreach($sl in $p.Slides){ $i++; $sl.Export("$o\s$i.png","PNG",1280,720) }; "exported $i"; $p.Close(); $pp.Quit()
& C:/Github/KTH/LossCalculation-SPB/.venv/Scripts/python.exe -c "
from PIL import Image, ImageDraw
import glob, os
o=os.path.join(os.environ['TEMP'],'decknew'); n=len(glob.glob(os.path.join(o,'s*.png')))
for g in range(0,n,6):
    sheet=Image.new('RGB',(2*960+10,3*540+20),'white')
    for k in range(6):
        i=g+k+1
        if i>n: break
        im=Image.open(os.path.join(o,'s%d.png'%i)).resize((960,540))
        x,y=(k%2)*970,(k//2)*550
        sheet.paste(im,(x,y)); ImageDraw.Draw(sheet).rectangle([x,y,x+959,y+539],outline='gray')
    sheet.save(os.path.join(o,'sheet%02d.png'%(g//6+1)))
print('sheets', (n+5)//6)"

"""Create instrumented revision generators without changing P5."""
from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
scripts=root/'scripts'
src=root/'hardware/epc2361-prototype-p5'
dst=root/'hardware/epc2361-prototype-p6'
dst.mkdir(exist_ok=True)
for folder in src.iterdir():
    if folder.is_dir() and (folder.suffix=='.pretty' or folder.name=='models'):
        shutil.copytree(folder,dst/folder.name,dirs_exist_ok=True)
fp='''(footprint "Current_Link" (version 20221018) (generator pcbnew)
 (layer "F.Cu") (attr smd)
 (fp_text reference "REF**" (at 0 -4.8) (layer "F.SilkS") (effects (font(size .8 .8)(thickness .12))))
 (fp_text value "Cu sense link" (at 0 4.8) (layer "F.Fab") (effects(font(size .8 .8)(thickness .12))))
 (pad "1" smd rect (at 0 -3)(size 2.2 2.2)(layers "F.Cu" "F.Mask"))
 (pad "2" smd rect (at 0 3)(size 2.2 2.2)(layers "F.Cu" "F.Mask"))
 (fp_rect (start -1.2 -4.2)(end 1.2 4.2)(stroke(width .05)(type solid))(fill none)(layer "F.CrtYd"))
)
'''
(dst/'epc2361-prototype.pretty/Current_Link.kicad_mod').write_text(fp)
for stem in ['build_p5_schematic','build_p5_board','route_p5','route_p5_gates','label_p5','check_p5','audit_p5_gate_paths']:
    s=(scripts/(stem+'.py')).read_text(encoding='utf-8-sig')
    s=s.replace('from p5_data import *','from p6_data import *').replace('scripts/route_p5.py','scripts/route_p6.py').replace('/ P5','/ P6').replace('(rev "P5")','(rev "P6")')
    if stem=='build_p5_schematic':
        s=s.replace("text('IIM: external", "put('LK1',375,273)\ntext('IIM: external")
    if stem=='build_p5_board':
        s=s.replace("        for x in [13.725,15.425,17.352]:track(d", "        if cell==1:\n            if y==16:sy=18.5\n            else:d='D_QL1';dy=19.55\n        for x in [13.725,15.425,17.352]:track(d")
        s=s.replace("track(d,13.725,dy,17.352,dy,1)","track(d,13.725,dy,17.352,dy,.5 if d=='D_QL1' else 1)")
        s=s.replace("[(52.8,33.8),(55.2,33.8),(55.2,50),(52.8,50)]","[(53.5,30.5),(56.5,30.5),(56.5,50),(53.5,50)]")
        start=s.index("    track('AC',17.352,19,21,19,1.5)")
        end=s.index('# Supplementary',start)
        s=s[:start]+'''    if cell==1:
        tr('AC',50.352,34.5,53.8,34.5,.8)
        tr('AC',53.8,34.5,55,32,1)
        for dx in [-.6,0,.6]:
            for dy in [-.6,0,.6]:via('AC',55+dx,32+dy)
        tr('D_QL1',50.352,35.55,53.2,35.55,.5)
        tr('D_QL1',53.2,35.55,53.2,38,.8)
        tr('D_QL1',53.2,38,55,38,.8)
    else:
        track('AC',17.352,19,21,19,1.5)
        for dx in [-.6,0,.6]:
            for dy in [-.6,0,.6]:via('AC',*xy(21+dx,19+dy,cell));track('AC',21,19,21+dx,19+dy,.6)
'''+s[end:]
    if stem=='route_p5':s=s.replace("[(54,35),(72,35)]","[(55,32),(72,35)]")
    if stem=='build_p5_board':s += '\nf.write_text(f.read_text().replace(\'(copper_finish "None")\',\'(copper_finish "ENIG")\'))\n'
    if stem=='route_p5_gates':s=s.replace('(52.2,32.9),(44.5,32.9)','(52.2,33.2),(44.5,33.2)')
    if stem=='check_p5':s=s.replace("r.startswith(('TP','H'))","r.startswith(('TP','H','LK'))")
    if stem=='label_p5':
        s=s.replace("label('DC-',39,16,size=.9)","label('DC-',39,16,size=.9)\nlabel('LK1 QL1 CURRENT',55,17,size=.8)")
        s=s.replace('for r,c in parts.items():','for r,c in parts.items():\n    if r==\'LK1\':continue')
    (scripts/(stem.replace('p5','p6')+'.py')).write_text(s)
print('P6 generators prepared')

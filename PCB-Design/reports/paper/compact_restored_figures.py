from pathlib import Path
ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/minimal_original_revision_2026-11-06'
base=P/'icpe/make_compact_digest_figures.py';ns={'__file__':str(base)};exec(base.read_text(encoding='utf-8').split('dimensions={}')[0],ns);ns['A']=A;ns['dimensions']={}
Fig=ns['Fig'];INK=ns['INK'];WINE=ns['WINE']
f=Fig(500,57)
for j,lines in enumerate([('Voltage/current','Choose device / n'),('KiCad','Route prototype'),('Ansys Q3D','Copper R / L / M'),('LTspice','Check VDS and VGS'),('Design decision','Margin / loss tradeoff')]):
 x=2+100*j;f.rect(x,3,94,28,'white',INK)
 for k,t in enumerate(lines):f.text(x+47,14+11*k,t,7.5,'middle')
 if j<4:f.arrow([(x+94,17),(x+100,17)])
f.arrow([(448,31),(448,41),(149,41),(149,31)],WINE);f.text(299,39,'Revise layout or drive settings',7.5,'middle',WINE)
f.arrow([(448,41),(448,55),(49,55),(49,31)],WINE,'3 2');f.text(249,53,'Revisit submodule voltage if margin is insufficient',7.5,'middle',WINE);f.finish('fig06_compact')
f=Fig(500,95);f.text(2,9,'(a) Prototype CAD assembly without heatsink',7.5);f.image(ROOT/'reports/slides/revb_pptx/img/r3d_load_nohs.png',0,12,230,67)
f.text(251,9,'(b) Q3D copper model at device / capacitor ports',7.5);f.image(P/'icpe/revised_blue_2026-11-06/q3d_copper_crop.png',249,12,250,67)
for x,t,c in [(255,'DC+','#d92c27'),(302,'DC−','#2167b7'),(355,'Switch node','#ed9c20'),(438,'Terminals','#d5b85b')]:f.rect(x,85,5,5,c);f.text(x+9,91,t,7.5)
f.finish('fig07_compact')

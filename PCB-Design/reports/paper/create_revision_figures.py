from pathlib import Path
from html import escape
import csv,json,math,base64,sys
ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/revised_blue_2026-11-06';A.mkdir(exist_ok=True)
base=P/'icpe/make_compact_digest_figures.py';src=base.read_text(encoding='utf-8');ns={'__file__':str(base)};exec(src.split('dimensions={}')[0],ns);ns['A']=A;ns['dimensions']={}
Fig=ns['Fig'];INK=ns['INK'];TEAL=ns['TEAL'];WINE=ns['WINE'];OCHRE=ns['OCHRE'];GREY=ns['GREY'];BLUE='#0057B8';LIGHT=ns['LIGHT']
D=json.loads((A/'single_and_sizing.json').read_text());ns['D']=D
styles=[(10,.5,TEAL,None),(10,1,TEAL,'3 2'),(20,.5,WINE,None),(20,1,WINE,'3 2')]
def legend(f,y,width):
 for j,(g,p,c,dash) in enumerate(styles):
  x=21+j*width/4;f.line([(x,y-2),(x+13,y-2)],c,dash);f.text(x+17,y,f'{g} / {p:g} nH',7.5)
# Device survey: quoted test voltages are explicitly shown, not portrayed as normalized operating voltages.
f=Fig(500,154)
def xy(c,r):return 32+211*math.log10(c/15)/math.log10(4000/15),120-105*math.log10(r/.4)/math.log10(900/.4)
for c in [20,100,500,2000]:
 x,y=xy(c,.4);f.line([(x,15),(x,120)],LIGHT,lw=.3);f.text(x,132,str(c),7,'middle')
for r in [1,10,100]:
 x,y=xy(15,r);f.line([(32,y),(243,y)],LIGHT,lw=.3);f.text(28,y+2.5,str(r),7,'end')
f.line([(32,15),(32,120),(243,120)],lw=.5)
for tau in [1,2,5,10]:
 pts=[xy(c,1000*tau/c) for c in [15*(4000/15)**(i/200) for i in range(201)]];pts=[p for p in pts if 15<=p[1]<=120];f.line(pts,GREY,'3 3',.5)
 x,y=xy(22,1000*tau/22);f.text(x,y-2,f'{tau} ps',7,col=GREY)
rows=list(csv.DictReader((P/'icpe/GaN_device_voltage_class_comparison_data.csv').open()))
co={100:TEAL,200:WINE,350:OCHRE,650:INK};offsets=[(6,8),(-7,-4),(6,-5),(-9,-4),(5,1),(-9,-7),(5,-6),(5,-3),(5,-3),(5,-3)]
for j,r in enumerate(rows):
 x,y=xy(float(r['Coss_tr_pF']),float(r['Rds_typ_25C_mOhm']));v=int(r['Voltage_class_V']);f.dot(x,y,co[v],1.8,v==200);dx,dy=offsets[j];f.text(x+dx,y+dy,chr(65+j),7.5,'middle',BLUE)
f.text(138,146,'Charge-equivalent capacitance (pF)',7.5,'middle');f.text(8,69,'On-resistance (mΩ)',7.5,'middle',rotate=-90)
xs=[257,276,372,405,442,477]
for x,h in zip(xs,['ID','Device','Rating','RDS','Vtest','Coss,Q']):f.text(x,13,h,7.5,col=BLUE)
for x,h in zip(xs,['','', '(V)','(mΩ)','(V)','(pF)']):f.text(x,24,h,7,col=BLUE)
f.line([(254,28),(499,28)],INK,lw=.5)
for j,r in enumerate(rows):
 y=39+j*11;vals=[chr(65+j),r['Device'],r['Voltage_class_V'],f"{float(r['Rds_typ_25C_mOhm']):g}",r['Vtest_V'],f"{float(r['Coss_tr_pF']):g}"]
 for x,v in zip(xs,vals):f.text(x,y,v,7.5,col=BLUE)
f.line([(254,141),(499,141)],INK,lw=.5);f.finish('fig02_device_survey_explicit_basis')
# Separate voltage stresses and complete-off-interval energy.
f=Fig(500,130)
panels=[('vdsl_pk',(70,200),[75,100,150,200],'Peak voltage (V)','(a) LS turn-off'),('vdsh_pk',(75,150),[75,100,125,150],'Peak voltage (V)','(b) HS at LS turn-on'),('eon',(0,100),[0,50,100],'Energy (µJ)','(c) LS turn-on'),('eoff',(0,20),[0,10,20],'Energy (µJ)','(d) LS turn-off')]
for j,(key,ylim,yt,ylab,tag) in enumerate(panels):
 x=32+125*j;t=f.axes(x,20,91,69,(0,170),ylim,[0,80,160],yt,'Current (A)',ylab);f.text(x+45,10,tag,7.5,'middle')
 if j<2:f.line([t(0,90),t(170,90)],GREY,'2 2',.6)
 for g,p,c,dash in styles:
  pts=[t(r['iload'],r[key]*(1e6 if j>=2 else 1)) for r in D['single'][f'g{g}_p{p:g}']];f.line(pts,c,dash,lw=.85)
  for x0,y0 in pts:f.dot(x0,y0,c,1.4,g==20)
legend(f,127,500);f.finish('fig03_complete_switching_maps')
# Preliminary loss and cooling calculation, same explicit first-pass model.
f=Fig(500,119)
for j,(label,c) in enumerate([('Conduction',INK),('Switching',TEAL),('Dead time',WINE),('Gate',OCHRE)]):
 x=22+j*119;f.rect(x,1,5,5,c);f.text(x+9,7,label,7.5)
t=f.axes(36,23,192,61,(1.5,8.5),(0,60),list(range(2,9)),[0,20,40,60],'Parallel devices per switch','Phase-leg loss (W)');f.text(36,17,'(a) 10 nH / 0.5 nH',7.5)
for r in D['parallel']['g10_p0.5']:
 v=0
 for k,c in [('cond',INK),('sw',TEAL),('dead',WINE),('gate',OCHRE)]:
  val=r[k];x,y=t(r['n']-.25,v+val);xx,yy=t(r['n']+.25,v);f.rect(x,y,xx-x,yy-y,c);v+=val
 if r['n']==4:f.text(*t(4,v+4),'4 selected',7,'middle',BLUE)
t=f.axes(295,23,192,61,(1.6,8.4),(75,185),list(range(2,9)),[90,120,150,180],'Parallel devices per switch','Low-side peak (V)');f.text(295,17,'(b) Low-side turn-off',7.5);f.line([t(1.6,90),t(8.4,90)],GREY,'2 2',.6)
for g,p,c,dash in styles:
 pts=[t(r['n'],r['vls']) for r in D['parallel'][f'g{g}_p{p:g}']];f.line(pts,c,dash,lw=.85)
 for x,y in pts:f.dot(x,y,c,1.4,g==20)
legend(f,118,500);f.finish('fig04_sizing_remeasured')
# Retain the paired-drive/Kelvin panels and recalculate the sensitivity bars for final intended conditions.
S=json.loads((ROOT/'simulation/bb_spice/icpe_digest_revision_2026-11-06/sharing_final_conditions.json').read_text());shares={r['case']:r for r in S['cases']}
part=src.split('# 5. Three panels in one row,')[1].split('# 6. Same six stages;')[0];part=part[part.index('f=Fig'):]
a="for y,label,v in [(23,'Power loop: ΔL = 0.3 nH',2),(47,'Gate loop: 2 / 8 nH',19),(71,'No Kelvin: ΔLs = 0.2 nH',29)]:"
b="for y,label,v in [(23,'Power loop: ΔL = 0.1 nH',shares[1]['imbalance_pct']),(47,'Gate loop: 10 / 15 nH',shares[2]['imbalance_pct']),(71,'No Kelvin: ΔLs = 0.05 nH',shares[4]['imbalance_pct'])]:"
assert a in part;part=part.replace(a,b).replace("f'{v}%'","f'{v:.0f}%'").replace('v*3','v*5').replace('GREY if v==2 else WINE','GREY if y==23 else WINE').replace("'75 V / 120 A; energy imbalance'","'75 V / 120 A; Rg = 3 Ω'").replace("f.finish('fig05_gate_drive')","f.finish('fig05_sharing_final_conditions')")
ns['shares']=shares;exec(part,ns)
# Shorter flow with readable native lettering.
f=Fig(500,65)
for j,lines in enumerate([('Voltage/current','Choose device / n'),('KiCad','Route prototype'),('Ansys Q3D','Copper R / L / M'),('LTspice','Check VDS and VGS'),('Design decision','Margin / loss tradeoff')]):
 x=2+100*j;f.rect(x,3,94,28,'white',INK)
 for k,t0 in enumerate(lines):f.text(x+47,14+11*k,t0,7.5,'middle')
 if j<4:f.arrow([(x+94,17),(x+100,17)])
f.arrow([(448,31),(448,45),(149,45),(149,31)],WINE);f.text(299,42,'Revise layout or drive settings',7.5,'middle',WINE)
f.arrow([(448,45),(448,59),(49,59),(49,31)],WINE,'3 2');f.text(249,64,'Revisit submodule voltage if margin is insufficient',7.5,'middle',WINE);f.finish('fig06_design_feedback')
# CAD rendering with no heatsink and clear Q3D legend.
f=Fig(500,119);f.text(2,9,'(a) Prototype CAD assembly without heatsink',7.5);f.image(ROOT/'reports/slides/revb_pptx/img/r3d_load_nohs.png',0,12,230,91)
f.text(251,9,'(b) Q3D copper model at device / capacitor ports',7.5)
p=P/'figures/revb/q3d_loop_load.png';cropped=A/'q3d_copper_crop.png'
with ns['Image'].open(p) as im:im.crop((0,390,2400,1360)).save(cropped)
f.image(cropped,249,12,250,91)
for x,t0,c in [(255,'DC+','#d92c27'),(302,'DC−','#2167b7'),(355,'Switch node','#ed9c20'),(438,'Terminals','#d5b85b')]:f.rect(x,109,5,5,c);f.text(x+9,115,t0,7.5)
f.finish('fig07_cad_q3d_readable')
(A/'figure_dimensions.json').write_text(json.dumps(ns['dimensions'],indent=2))
print('STATIC FIGURES DONE',flush=True)

import ast,math,csv
from pathlib import Path
from html import escape
root=Path(r'C:\Github\KTH\PCB-Design');out=root/'reports/paper/icpe'
tree=ast.parse((root/'scripts/device_survey.py').read_text())
dev=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEV' for t in n.targets))
s=['<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="96mm" viewBox="0 0 454 272"><rect width="454" height="272" fill="white"/>']
def line(x,y,X,Y,col='#111111',dash='',w=.65):s.append(f'<path d="M{x} {y} L{X} {Y}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
def text(x,y,t,size=11,anchor='start',col='#111111',extra=''):s.append(f'<text x="{x}" y="{y}" font-family="Times New Roman" font-size="{size}" text-anchor="{anchor}" fill="{col}" {extra}>{t}</text>')
def xy(c,r):return 54+380*math.log10(c/15)/math.log10(4000/15),222-202*math.log10(r/.4)/math.log10(900/.4)
for c in [20,50,100,200,500,1000,2000]:
 x,y=xy(c,.4);line(x,20,x,222,'#E2E0DA',w=.35);line(x,222,x,226);text(x,237,str(c),anchor='middle')
for r in [1,10,100]:
 x,y=xy(15,r);line(54,y,434,y,'#E2E0DA',w=.35);line(50,y,54,y);text(46,y+3,str(r),anchor='end')
line(54,20,54,222);line(54,222,434,222)
for tau in [1,2,5,10]:
 pts=[xy(15* (4000/15)**(i/150),1000*tau/(15*(4000/15)**(i/150))) for i in range(151)]
 pts=[(x,y) for x,y in pts if 20<=y<=222]
 s.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'" fill="none" stroke="#898781" stroke-width="0.65" stroke-dasharray="4 3"/>')
 x,y=xy(21,1000*tau/21);text(x,y-3,f'{tau} ps',col='#52514E',extra=f'transform="rotate(24 {x} {y-3})"')
col={100:'#018789',200:'#A41C59',350:'#C38714',650:'#111111'}
def marker(x,y,v):
 if v==100:s.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{col[v]}" stroke="#111111" stroke-width="0.5"/>')
 elif v==200:s.append(f'<rect x="{x-3}" y="{y-3}" width="6" height="6" fill="{col[v]}" stroke="#111111" stroke-width="0.5"/>')
 elif v==350:s.append(f'<path d="M{x} {y-4} L{x+3.5} {y+3} H{x-3.5} Z" fill="{col[v]}" stroke="#111111" stroke-width="0.5"/>')
 else:s.append(f'<path d="M{x} {y-4} L{x+3.5} {y} L{x} {y+4} L{x-3.5} {y} Z" fill="{col[v]}"/>')
off={'EPC2361':(-7,14,'end'),'EPC2302':(-5,-10,'end'),'EPC2071':(8,1,'start'),'IGC033S10S1':(-9,0,'end'),'EPC2304':(8,-2,'start'),'EPC2215':(-7,13,'end'),'EPC2034C':(-3,-12,'end'),'EPC2050':(8,-2,'start'),'IGT65R025D2':(8,1,'start'),'IGT65R140D2':(8,-3,'start')}
rows=[]
for pn,mk,v,r,q,vt,c,pkg in dev:
 ctr=q/vt*1000;x,y=xy(ctr,r);marker(x,y,v)
 if pn=='EPC2361':text(x+8,y+2,pn,11,'start')
 rows.append([pn,v,r,q,vt,ctr,r*ctr/1000])
for i,v in enumerate([100,200,350,650]):
 marker(343,32+16*i,v);text(352,36+16*i,f'{v} V class')
text(244,258,'Charge-equivalent output capacitance, C<tspan baseline-shift="sub" font-size="8">oss,Q</tspan> (pF)',11,'middle')
text(14,121,'On-state resistance, R<tspan baseline-shift="sub" font-size="8">DS(on)</tspan> (mΩ)',11,'middle',extra='transform="rotate(-90 14 121)"')
s.append('</svg>');(out/'GaN_device_voltage_class_comparison.svg').write_text('\n'.join(s),encoding='utf-8')
with (out/'GaN_device_voltage_class_comparison_data.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Device','Voltage_class_V','Rds_typ_25C_mOhm','Qoss_nC','Vtest_V','Coss_tr_pF','D_FoM_ps']);w.writerows(rows)

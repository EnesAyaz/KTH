from pathlib import Path
from html import escape
p=Path(r'C:\Github\KTH\PCB-Design\reports\paper\icpe')
s=['<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="128mm" viewBox="0 0 454 363"><rect width="454" height="363" fill="white"/>']
ink='#111111';teal='#018789';wine='#A41C59';grey='#898781'
def text(x,y,t,size=10,anchor='start',col=ink):s.append(f'<text x="{x}" y="{y}" font-family="Times New Roman" font-size="{size}" text-anchor="{anchor}" fill="{col}">{t}</text>')
def path(points,col=ink,dash='',w=.9):s.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
def box(x,y,w,h,t='',col=ink,fill='white'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{col}" stroke-width="0.8"/>')
 if t:text(x+w/2,y+h/2+3,t,9,'middle')
text(8,14,'(a)');text(30,14,'Switching-energy imbalance',10)
for y,label,value in [(44,'Power loop: ΔL = 0.3 nH',2),(80,'Gate loop: 2 versus 8 nH',19),(116,'No Kelvin: ΔLsource = 0.2 nH',29)]:
 text(10,y-8,label,9)
 s.append(f'<rect x="10" y="{y}" width="{value*5}" height="12" fill="{teal if value==2 else wine}"/>');text(15+value*5,y+10,f'{value}%',10)
text(10,153,'Two devices; 75 V, 120 A total',9,col=grey)
text(235,14,'(b)');text(257,14,'Two independently driven pairs',10)
for offset,label in [(0,'Pair 1'),(108,'Pair 2')]:
 x=239+offset;text(x+45,36,label,10,'middle')
 for dx,cell in [(0,'1' if offset==0 else '3'),(65,'2' if offset==0 else '4')]:
  box(x+dx,51,25,62,col=grey);text(x+dx+12.5,46,'Cell '+cell,8,'middle');text(x+dx+12.5,70,'HS',9,'middle');text(x+dx+12.5,100,'LS',9,'middle')
 box(x+30,122,30,30,col=ink);text(x+45,134,'Driver',9,'middle');text(x+45,146,'HS / LS',8,'middle')
 # separate outputs branched to corresponding device gates
 path([(x+39,122),(x+39,67),(x+25,67)],wine);path([(x+39,67),(x+65,67)],wine)
 path([(x+51,122),(x+51,97),(x+25,97)],teal);path([(x+51,97),(x+65,97)],teal)
text(340,170,'Each output channel drives two gates',9,'middle')
path([(8,184),(446,184)],'#E2E0DA',w=.5)
text(8,202,'(c)');text(30,202,'One cell pair: routing concept (not to scale)',10)
# placement concept with two mirrored cells and central bottom driver
for x,idx in [(84,'1'),(346,'2')]:
 text(x,222,'Cell '+idx,10,'middle')
 box(x-21,234,42,24,'QH'+idx);box(x-21,276,42,24,'QL'+idx)
 # local decoupling and commutation path, drawn schematic only
 box(x-60 if idx=='1' else x+38,244,22,46,'Cloc',grey)
 cx=x-49 if idx=='1' else x+49
 path([(cx,244),(cx,230),(x,230),(x,234)],grey)
 path([(cx,290),(cx,307),(x,307),(x,300)],grey)
box(193,299,64,36,col=ink);text(225,314,'Dual-channel',9,'middle');text(225,327,'gate driver',9,'middle')
# symmetric dedicated gate/return branches, distinct schematic layers
for side,x in [(-1,105),(1,325)]:
 path([(219,299),(219,246),(x,246)],wine)
 path([(231,299),(231,288),(x,288)],teal)
 path([(209 if side==-1 else 241,299),(209 if side==-1 else 241,255),(x,255)],wine,'3 2')
 path([(201 if side==-1 else 249,320),(174 if side==-1 else 276,320),(174 if side==-1 else 276,297),(x,297)],teal,'3 2')
# legends and explicit abstraction
path([(37,348),(57,348)],wine);text(62,351,'HS',9)
path([(93,348),(113,348)],teal);text(118,351,'LS',9)
path([(157,348),(177,348)],ink);text(182,351,'Gate',9)
path([(237,348),(257,348)],ink,'3 2');text(262,351,'Kelvin return',9)
s.append('</svg>');(p/'paired_gate_drive_cell_layout.svg').write_text('\n'.join(s),encoding='utf-8')

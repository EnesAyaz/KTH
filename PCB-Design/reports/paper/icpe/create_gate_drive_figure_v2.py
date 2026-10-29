from pathlib import Path
from html import escape
p=Path(r'C:\Github\KTH\PCB-Design\reports\paper\icpe')
s=['<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="137mm" viewBox="0 0 454 389"><rect width="454" height="389" fill="white"/>']
ink='#111111';teal='#018789';wine='#A41C59';grey='#898781'
def text(x,y,t,size=10,anchor='start',col=ink):s.append(f'<text x="{x}" y="{y}" font-family="Times New Roman" font-size="{size}" text-anchor="{anchor}" fill="{col}">{t}</text>')
def path(points,col=ink,dash='',w=.9):s.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
def box(x,y,w,h,t='',col=ink,fill='white'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{col}" stroke-width="0.8"/>')
 if t:text(x+w/2,y+h/2+3,t,9,'middle')

def dot(x,y,col=ink):s.append(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{col}"/>')
def fet(x,y,label,flip=False):
 k=1 if flip else -1
 path([(x,y-16),(x,y-8),(x+k*5,y-8)])
 path([(x+k*5,y+8),(x,y+8),(x,y+16)])
 for a,b in [(-10,-5),(-3,3),(5,10)]:path([(x+k*5,y+a),(x+k*5,y+b)])
 path([(x+k*8,y-8),(x+k*8,y+8)]);path([(x+k*15,y),(x+k*8,y)])
 dot(x,y+8);text(x-6 if flip else x+5,y+3,label,9,'end' if flip else 'start')
def resistor(x,y,col):
 path([(x-10,y),(x-5,y)],col);s.append(f'<rect x="{x-5}" y="{y-2}" width="10" height="4" fill="white" stroke="{col}" stroke-width="0.8"/>');path([(x+5,y),(x+10,y)],col)
# sensitivity compact plot
text(8,15,'(a)');text(30,15,'Sensitivity to parasitic mismatch',10)
for y,label,value in [(45,'Power loop: &#916;L = 0.3 nH',2),(85,'Gate loop: 2 versus 8 nH',19),(125,'Without Kelvin: &#916;Ls = 0.2 nH',29)]:
 text(10,y-8,label,9)
 s.append(f'<rect x="10" y="{y}" width="{value*4.1}" height="11" fill="{grey if value==2 else wine}"/>');text(15+value*4.1,y+9,f'{value}%',10)
text(10,162,'Switching-energy imbalance (%)',9)
text(10,178,'Two devices; 75 V, 120 A total',9,col=grey)
# architecture overview actual switch symbols; two identical driver pairs
text(202,15,'(b)');text(224,15,'Four cells, two dual-channel drivers',10)
for i,(y,ids) in enumerate([(60,('1','2')),(140,('3','4'))]):
 # cells left and right have high and low symbols, one driver between
 for x,idx in [(234,ids[0]),(421,ids[1])]:
  fet(x,y-15,'QH'+idx,x==234);fet(x,y+17,'QL'+idx,x==234)
  path([(x,y-31),(x,y-36)],grey);path([(x,y+33),(x,y+37)],grey)
  # Cell identity is carried by the transistor subscripts.
 box(299,y-23,55,55,col=ink,fill='#f5f5f3')
 text(326.5,y-27,'Driver '+str(i+1),9,'middle')
 text(326.5,y-12,'HO',9,'middle',wine);text(326.5,y+23,'LO',9,'middle',teal)
 # each output fans to two gates, routes cross without junction dots
 for yy,col in [(y-15,wine),(y+17,teal)]:
  path([(299,yy),(269,yy)],col);resistor(259,yy,col)
  path([(354,yy),(371,yy)],col);resistor(381,yy,col);path([(391,yy),(406,yy)],col)
text(326,196,'Each output drives two transistors',9,'middle')
# divider
path([(8,211),(446,211)],'#E2E0DA',w=.5)
text(8,229,'(c)');text(30,229,'Kelvin return separates the gate and power loops',10)
# package pad arrangement, not dimension drawing
text(92,250,'EPC2361 pad arrangement',9,'middle')
for x,w,lab,col in [(91,15,'D',grey),(112,15,'S',ink),(133,15,'D',grey),(154,15,'S',ink),(175,23,'D',grey)]:
 box(x,267,w,68,col=col,fill='#f5f5f3');text(x+w/2,304,lab,10,'middle')
box(64,267,21,24,'G',wine);box(64,297,21,38,'K',teal)
text(131,352,'Top view; schematic proportions',8,'middle',grey)
# functional equivalent with source inductance outside Kelvin return
box(239,275,46,48,col=ink,fill='#f5f5f3');text(262,294,'Driver',10,'middle');text(262,309,'output',9,'middle')
# transistor channel
path([(353,255),(353,272),(343,272)]);path([(343,272),(343,310)]);path([(343,310),(353,310),(353,338)])
path([(339,277),(339,305)]);path([(285,287),(339,287)],wine)
text(310,280,'G',9,'middle',wine)
# Kelvin return at die-side source node
path([(285,314),(324,314),(324,310),(353,310)],teal,'3 2');dot(353,310,teal);text(307,331,'K',9,'middle',teal)
# power source inductance coil
s.append('<path d="M353 338 c8 0 8 6 0 6 c8 0 8 6 0 6 c8 0 8 6 0 6" fill="none" stroke="#111111" stroke-width="0.9"/>')
path([(353,356),(353,369)]);text(366,352,'Ls',10);text(360,263,'D',9);text(360,370,'S (power)',9)
text(238,385,'Solid: gate drive    Dashed: Kelvin return',9)
s.append('</svg>');(p/'paired_gate_drive_cell_layout_v2.svg').write_text('\n'.join(s),encoding='utf-8')

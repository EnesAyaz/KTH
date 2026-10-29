from pathlib import Path
from html import escape
p=Path(r'C:\Github\KTH\PCB-Design\reports\paper\icpe')
s=['<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="88mm" viewBox="0 0 454 250"><defs><marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#111111"/></marker></defs><rect width="454" height="250" fill="white"/>']
def line(x1,y1,x2,y2,col='#111111',dash=''):
 s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="0.8" '+(f'stroke-dasharray="{dash}"' if dash else '')+'/>')
def text(x,y,t,size=8,anchor='start',col='#111111'):
 s.append(f'<text x="{x}" y="{y}" font-family="Times New Roman" font-size="{size}" text-anchor="{anchor}" fill="{col}">{t}</text>')
def rect(x,y,w,h,fill='white',col='#111111',dash=''):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{col}" stroke-width="0.8" '+(f'stroke-dasharray="{dash}"' if dash else '')+'/>')
def cap(x,y):
 line(x,y-18,x,y-3);line(x-7,y-3,x+7,y-3);line(x-7,y+1,x+7,y+1);line(x,y+1,x,y+18)
def coil(x,y):
 s.append(f'<path d="M{x} {y} '+''.join('a3 4 0 0 1 6 0 ' for _ in range(3))+'" fill="none" stroke="#111111" stroke-width="0.8"/>')
# (a): actual circuit topology
text(6,12,'(a)');text(170,23,'Common machine',8,'middle')
rect(141,29,67,180,'#f5f8f7', '#898781','3 2')
line(18,39,18,203);line(18,39,47,39);line(18,203,47,203)
# dc supply symbol
rect(13,112,10,19);line(14,119,22,119);line(16,123,20,123);text(2,107,'V<tspan baseline-shift="sub" font-size="6">dc</tspan>')
for y,lab,ci in [(39,'N','N'),(108,'2','2'),(167,'1','1')]:
 cap(47,y+18);line(47,y,69,y);line(47,y+36,69,y+36)
 rect(69,y,42,36,'#f0f5f7');line(69,y+36,111,y);text(77,y+12,'=',10);text(95,y+29,'3~',10)
 text(90,y-5,'Submodule '+lab,8,'middle');text(57,y+20,'C<tspan baseline-shift="sub" font-size="6">'+ci+'</tspan>')
 for dy in [8,18,28]:
  line(111,y+dy,151,y+dy);coil(151,y+dy);line(169,y+dy,190,y+dy)
 line(190,y+8,190,y+28);text(194,y+21,'n<tspan baseline-shift="sub" font-size="6">'+ci+'</tspan>')
line(47,75,47,90);line(47,90,47,101,dash='1 3');line(47,101,47,108);line(47,144,47,167)
text(88,96,'⋮',12,'middle');text(174,96,'⋮',12,'middle')
# current arrow
s.append('<path d="M115 47 H138" fill="none" stroke="#111111" stroke-width="0.8" marker-end="url(#arr)"/>');text(125,42,'i<tspan baseline-shift="sub" font-size="6">ph</tspan>',8,'middle')
text(109,226,'V<tspan baseline-shift="sub" font-size="6">m</tspan> = V<tspan baseline-shift="sub" font-size="6">dc</tspan>/N',9,'middle')
# (b) expanded submodule
text(227,12,'(b)');text(343,25,'One three-phase submodule',8,'middle')
rect(277,49,41,151,'#edf7f7','#018789','4 2')
line(247,56,429,56);line(247,193,429,193);cap(254,124);line(254,56,254,106);line(254,142,254,193)
text(242,125,'C<tspan baseline-shift="sub" font-size="6">m</tspan>',8,'end');text(242,63,'+',9);text(242,191,'−',9)
for x,lab in [(297,'a'),(351,'b'),(405,'c')]:
 for y in [88,160]:
  line(x,y-32,x,y-12);line(x,y+12,x,y+33)
  # Circular insulated-gate transistor symbol matching the supplied reference.
  s.append(f'<circle cx="{x}" cy="{y}" r="15" fill="white" stroke="#111111" stroke-width="0.8"/>')
  # Drain and source, segmented channel, and insulated gate.
  line(x,y-18,x,y-9);line(x,y-9,x-8,y-9)
  line(x,y+9,x,y+18);line(x-8,y+9,x,y+9)
  for aa,bb in [(-12,-6),(-3,3),(6,12)]:line(x-8,y+aa,x-8,y+bb)
  line(x-10.5,y-11,x-10.5,y+11);line(x-21,y,x-10.5,y)
  # Source-connected body terminal and inward arrow.
  line(x,y+9,x,y);line(x,y,x-4,y)
  s.append(f'<path d="M{x-8} {y} L{x-4} {y-2} L{x-4} {y+2} Z" fill="#111111"/>')
  # Reverse-conduction branch as drawn in the user's reference.
  line(x,y-12,x+6,y-12);line(x+6,y-12,x+6,y-3)
  line(x+6,y+3,x+6,y+12);line(x+6,y+12,x,y+12)
  s.append(f'<path d="M{x+2.5} {y+3} L{x+6} {y-3} L{x+9.5} {y+3} Z" fill="#111111" stroke="#111111" stroke-width="0.6"/>')
  line(x+2.5,y-3,x+9.5,y-3)

 line(x,121,x,127);s.append(f'<circle cx="{x}" cy="124" r="1.6" fill="#111111"/>')
 line(x,124,x+22,124);text(x+24,127,lab)
text(297,213,'Studied phase leg',8,'middle', '#018789');text(343,231,'Four parallel GaN transistors per switch position',8,'middle')
text(343,243,'Diode symbol denotes the reverse-conduction path',7.5,'middle')
s.append('</svg>')
(p/'SPB_introduction_topology.svg').write_text('\n'.join(s),encoding='utf-8')



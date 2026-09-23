from pathlib import Path
import shutil
root=Path.cwd(); scripts=root/'scripts'; src=root/'hardware/epc2361-prototype'; dst=root/'hardware/epc2361-prototype-p3'
shutil.copytree(src,dst,dirs_exist_ok=True)
(scripts/'p3_data.py').write_text('''from prototype_data import *
import copy
parts=copy.deepcopy(parts)
OUT=ROOT/'hardware/epc2361-prototype-p3'
NAME='epc2361-prototype-p3'
# Retain local custom footprint library nickname.
left={'QH1','QL1','RGH1','RGL1','JGH1','JGL1'}|{'C'+str(i) for i in range(7,13)}
right={'QH2','QL2','RGH2','RGL2','JGH2','JGL2'}|{'C'+str(i) for i in range(1,7)}
for r,c in parts.items():
    if r in left:c['x']+=14
    elif r in right:c['x']+=10
    elif r not in {'JDC1','JDC2','JAC1','JCTRL1','TP1','TP2','TP3'}:c['x']-=16
for r,x,y in [('JDC1',14,15),('JDC2',30,15),('JAC1',80,35),('JCTRL1',12,30),('TP1',73,28),('TP2',40,25),('TP3',74,43)]:parts[r]['x']=x;parts[r]['y']=y
''')
s=(scripts/'build_prototype_schematic.py').read_text().replace('from prototype_data import *','from p3_data import *').replace('(rev "P2")','(rev "P3")')
(scripts/'build_p3_schematic.py').write_text(s)
s=(scripts/'build_prototype_board.py').read_text().replace('from prototype_data import *','from p3_data import *')
s=s.replace('(49-x,54-y) if cell==1 else (41+x,16+y)','(63-x,54-y) if cell==1 else (51+x,16+y)')
s=s.replace("zone('DC-',p.In1_Cu,[(12,16),(82,16),(82,55),(12,55)])","zone('DC-',p.In1_Cu,[(7,7),(88,7),(88,57),(7,57)])")
s=s.replace("zone('DC+',p.In2_Cu,[(24,8),(82,8),(82,55),(24,55)])","zone('DC+',p.In2_Cu,[(7,7),(88,7),(88,57),(7,57)])")
s=s.replace("zone('AC',p.B_Cu,[(24,32),(31,32),(31,49),(59,49),(59,32),(82,32),(82,56),(24,56)])","zone('AC',p.B_Cu,[(40,32),(45,32),(45,49),(69,49),(69,29),(87,29),(87,56),(40,56)])")
s=s.replace("tr(net,*pos('U1',pin),ex,ey,.15)","tr(net,*pos('U1',pin),ex-16,ey,.15)")
s=s.replace("tr('DC+',63,28,61.25,28.1,.25)","tr('DC+',73,28,71.25,28.1,.25)")
a=s.index('for a,c in [((8,6)');z=s.index('# Dimensioned envelope',a)
s=s[:a]+'''for a,c in [((5,5),(90,5)),((90,5),(90,60)),((90,60),(5,60)),((5,60),(5,5))]:line(a,c)
text('EPC2361 / TWO PER SWITCH / P3',59,8)
text('12 x 1uF 100V / ALL CAPS TOP',59,11)
text('DC+',14,7.8);text('DC-',30,7.8);text('AC',80,27)
text('REVIEW PROTOTYPE',47,58)
# Every component reference; connector pin functions added separately.
for ref,f in fps.items():
    x,y=parts[ref]['x'],parts[ref]['y']
    if ref.startswith('C') and ref[1:].isdigit() and int(ref[1:])<=12:
        text(ref,x, y-3.7 if y<35 else y+3.7,size=.65)
    elif ref.startswith('Q'):text(ref,x,y-.0,p.F_SilkS,.65)
    elif ref in ['JDC1','JDC2','JAC1']:text(ref,x,y+6.7,size=.75)
    elif ref=='U1':text('U1 LMG1210',x,y-3.2,size=.65)
    elif ref=='JCTRL1':text(ref,x, y-2,size=.65)
    else:text(ref,x,y+1.65,size=.6)
for ref in ['JGH1','JGH2','JGL1','JGL2']:
    x,y=pos(ref,1);text('G',x-1.8,y,size=.65)
    x,y=pos(ref,2);text('S',x-1.8,y,size=.65)
for i,label in enumerate(['12V','GND','HI','GND','LI','GND']):
    x,y=pos('JCTRL1',i+1);text(label,x+3,y,size=.7)
for ref in ['TP1','TP2','TP3','TP4','TP5']:
    x,y=pos(ref,1);text(parts[ref]['value'],x,y-1.2,size=.6)
''' +s[z:]
(scripts/'build_p3_board.py').write_text(s)
# Copy routing engine only; endpoints will be rebuilt relative to placed components.
r=(scripts/'route_prototype.py').read_text().replace('from prototype_data import *','from p3_data import *')
a=r.index('# Driver split');z=r.index('# Route driver nets',a)
block='''# Local driver escapes, translated as one island from the checked P2 geometry.
def dp(x,y):return x-16,y
def dt(n,x1,y1,x2,y2,w=.15):tr(n,*dp(x1,y1),*dp(x2,y2),w)
def dv(n,x,y):via(n,*dp(x,y))
tr('DC-',*pos('U1',20),*pos('U1',3),.3);tr('DC-',*pos('U1',20),*pos('U1',7),.2)
for pin in [13,14,9,16]:tr('AC',*pos('U1',21),*pos('U1',pin),.2)
for n,x,y in [('VIN',42.1,34),('VDD',41,35.8),('VDD',43.75,37.6),('LO',44.75,37.6),('HO',46.25,37.6),('HB',48.1,35.5),('BST',44.75,32.3),('DC-',41.8,35),('DC-',41.8,36.8)]:dv(n,x,y)
for n,pin,points in [('VIN',2,[(42.5,34.5),(42.1,34)]),('VDD',4,[(42.5,35.5),(42.1,35.8),(41,35.8)]),('DC-',5,[(42.5,36),(41.8,36.8)])]:
    a=pos('U1',pin)
    for c in points:c=dp(*c);tr(n,*a,*c);a=c
for n,a,c in [('HI',(44.25,32.6),(42.8,32.6)),('HI',(42.8,32.6),(42.8,32.3)),('LI',(43.75,33.1),(42,33.1)),('AC',(47.4,35),(47.4,34.5))]:dt(n,*a,*c)
dv('HI',42.8,32.3);dv('LI',42,33.1);dv('AC',49.2,34.5)
tr('AC',*pos('C18',2),*dp(46.25,32.3));tr('AC',*dp(46.25,32.3),*pos('U1',16))
tr('AC',*pos('C17',2),*dp(45.5,27.225));dt('AC',45.5,27.225,45.5,29.5);tr('AC',*dp(45.5,29.5),*pos('C18',2))
for ref,x,y in [('RGH1',38.81,40.3),('RGL1',38.81,34.3),('RGH2',51.19,31.5),('RGL2',51.19,35.7)]:escape(ref,1,x+(14 if ref.endswith('1') else 10),y)
for ref,pin,x,y in [('C13',1,38.225,22.7),('C13',2,39.775,22.7),('C14',1,42.6,45.45),('C14',2,42.6,43.55),('C15',1,48.4,45.45),('C15',2,48.4,43.55),('C16',1,42.8,40.275),('C16',2,42.8,38.725),('C17',1,48.2,28.775),('C18',1,44.225,30.1),('RB1',1,42.8,28.325),('RB1',2,42.8,26.675),('D1',1,45.6,22.5),('D1',2,49,22.5),('RH1',1,35,21.51),('RH1',2,35,20.49),('RL1',1,40,21.51),('RL1',2,40,20.49)]:escape(ref,pin,x-16,y)
for pin in ['1','3','5']:nodes.setdefault(parts['JCTRL1']['pins'][pin],[]).append(pos('JCTRL1',pin))
nodes['HB'].append(dp(47.8,22));nodes['VDD'].append(dp(51.8,46))
for ref in ['JGH1','JGH2']:nodes['AC'].append(pos(ref,2))
nodes['AC'] += [(42,35),(72,35)]
'''
r=r[:a]+block+r[z:];r=r.replace('step=.1;ox=9;oy=7;W=740;H=510','step=.1;ox=6;oy=6;W=830;H=530')
(scripts/'route_p3.py').write_text(r)
(scripts/'check_p3.py').write_text((scripts/'check_prototype.py').read_text().replace('from prototype_data import *','from p3_data import *'))
print('P3 generators created; P2 preserved')

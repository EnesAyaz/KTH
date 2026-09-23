from pathlib import Path
p=Path('scripts/p3_data.py');s=p.read_text().replace("c['x']-=16","c['x']-=6").replace("('JDC1',14,15),('JDC2',30,15)","('JDC1',14,13),('JDC2',30,13)");p.write_text(s)
p=Path('scripts/build_p3_board.py');s=p.read_text().replace('ex-16,ey','ex-6,ey');s=s.replace("def text(s,x,y,layer=p.F_SilkS,size=.9):","def text(s,x,y,layer=p.F_SilkS,size=.9):\n    size=max(.8,size)")
a=s.index('# Every component reference');z=s.index('# Dimensioned envelope',a)
s=s[:a]+'''# Place all reference and pin labels on unobstructed silk using conservative boxes.
occupied=[]
for f in fps.values():
    for q in f.Pads():
        bb=q.GetBoundingBox();occupied.append((p.ToMM(bb.GetX())-.3,p.ToMM(bb.GetY())-.3,p.ToMM(bb.GetRight())+.3,p.ToMM(bb.GetBottom())+.3))
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):
        a=t.GetPosition();x=p.ToMM(a.x);y=p.ToMM(a.y);occupied.append((x-.55,y-.55,x+.55,y+.55))
def label(s,x,y):
    w=max(1,len(s)*.64);h=1.0
    candidates=[(dx,dy) for dx in range(-12,13) for dy in range(-12,13)]
    candidates.sort(key=lambda d:d[0]**2+d[1]**2)
    for dx,dy in candidates:
        xx=x+dx*.5;yy=y+dy*.5;box=(xx-w/2,yy-h/2,xx+w/2,yy+h/2)
        if box[0]<6 or box[2]>89 or box[1]<20 or box[3]>57:continue
        if any(box[0]<c[2] and box[2]>c[0] and box[1]<c[3] and box[3]>c[1] for c in occupied):continue
        text(s,xx,yy,size=.8);occupied.append(box);return
    raise RuntimeError('No silk label position for '+s)
for ref,f in fps.items():
    x,y=parts[ref]['x'],parts[ref]['y']
    if ref in ['JDC1','JDC2']:text(ref,x,y+7,size=.8)
    elif ref=='JAC1':label(ref,x,y+7)
    elif ref.startswith('C') and ref[1:].isdigit() and int(ref[1:])<=12:label(ref,x,y-4 if y<35 else y+4)
    else:label(ref,x,y+1.8)
for ref in ['JGH1','JGH2','JGL1','JGL2']:
    x,y=pos(ref,1);label('G',x-1.8,y)
    x,y=pos(ref,2);label('S',x-1.8,y)
for i,txt in enumerate(['12V','GND','HI','GND','LI','GND']):
    x,y=pos('JCTRL1',i+1);label(txt,x+3,y)
for ref in ['TP1','TP2','TP3','TP4','TP5']:
    x,y=pos(ref,1);label(parts[ref]['value'],x,y-1.4)
''' + s[z:];p.write_text(s)
p=Path('scripts/route_p3.py');s=p.read_text().replace('return x-16,y','return x-6,y').replace('escape(ref,pin,x-16,y)','escape(ref,pin,x-6,y)');p.write_text(s)

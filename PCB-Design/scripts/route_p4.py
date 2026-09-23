"""Route prototype driver connections and audit native connectivity/clearances.
Grid routing is a connectivity aid, not an impedance or timing optimizer.
"""
from p4_data import *
import os,math,heapq,json
os.environ['KICAD7_FOOTPRINT_DIR']='C:/Program Files/KiCad/7.0/share/kicad/footprints'
import pcbnew as p
import wx
app=wx.App(False)
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')));fps={f.GetReference():f for f in b.GetFootprints()}
nets={n.GetNetname():n for n in b.GetNetInfo().NetsByName().values()}
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def pos(ref,pin):
    q=next(q for q in fps[ref].Pads() if q.GetNumber()==str(pin));a=q.GetPosition();return p.ToMM(a.x),p.ToMM(a.y)
def tr(n,x1,y1,x2,y2,w=.15,layer=p.F_Cu):
    if abs(x1-x2)+abs(y1-y2)<1e-6:return
    t=p.PCB_TRACK(b);t.SetStart(v(x1,y1));t.SetEnd(v(x2,y2));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t)
nodes={}
def via(n,x,y,node=True):
    q=p.PCB_VIA(b);q.SetPosition(v(x,y));q.SetWidth(p.FromMM(.6));q.SetDrill(p.FromMM(.3));q.SetLayerPair(p.F_Cu,p.B_Cu);q.SetNet(nets[n]);b.Add(q)
    if node:nodes.setdefault(n,[]).append((x,y))
def escape(ref,pin,x,y):
    n=parts[ref]['pins'][str(pin)];tr(n,*pos(ref,pin),x,y);via(n,x,y)
# Local driver escapes, translated as one island from the checked P2 geometry.
def dp(x,y):return x-9,y
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
for ref,x,y in [('RGH1',43.19,31.5),('RGL1',43.19,35.7),('RGH2',61.19,31.5),('RGL2',61.19,35.7)]:escape(ref,1,x,y)
for ref,pin,x,y in [('C13',1,38.225,22.7),('C13',2,39.775,22.7),('C14',1,42.6,45.45),('C14',2,42.6,43.55),('C15',1,48.4,45.45),('C15',2,48.4,43.55),('C16',1,42.8,40.275),('C16',2,42.8,38.725),('C17',1,48.2,28.775),('C18',1,44.225,30.1),('RB1',1,42.8,28.325),('RB1',2,42.8,26.675),('D1',1,45.6,22.5),('D1',2,49,22.5),('RH1',1,35,21.51),('RH1',2,35,20.49),('RL1',1,40,21.51),('RL1',2,40,20.49)]:escape(ref,pin,x-9,y)
for pin in ['1','3','5']:nodes.setdefault(parts['JCTRL1']['pins'][pin],[]).append(pos('JCTRL1',pin))
nodes['HB'].append(dp(47.8,22));nodes['VDD'].append((39.8,49))
for ref in ['JGH1','JGH2']:nodes['AC'].append(pos(ref,2))
nodes['AC'] += [(54,35),(72,35)]
# Route driver nets on B.Cu. Existing power and gate copper form obstacles.
step=.1;ox=6;oy=6;W=765;H=490
def grid(x,y):return round((x-ox)/step),round((y-oy)/step)
def world(a):return ox+a[0]*step,oy+a[1]*step
def obstacles(net,layer):
    out=bytearray(W*H)
    def rect(x0,y0,x1,y1):
        a,c=grid(x0,y0);d,e=grid(x1,y1)
        for yy in range(max(0,c),min(H,e+1)):
            for xx in range(max(0,a),min(W,d+1)):out[yy*W+xx]=1
    def diskline(x0,y0,x1,y1,r):
        ax,ay=grid(min(x0,x1)-r,min(y0,y1)-r);bx,by=grid(max(x0,x1)+r,max(y0,y1)+r)
        dx=x1-x0;dy=y1-y0;ll=dx*dx+dy*dy
        for yy in range(max(0,ay),min(H,by+1)):
            y=oy+yy*step
            for xx in range(max(0,ax),min(W,bx+1)):
                x=ox+xx*step;t=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/ll)) if ll else 0
                if (x-x0-t*dx)**2+(y-y0-t*dy)**2<=r*r:out[yy*W+xx]=1
    for f in b.GetFootprints():
        for q in f.Pads():
            if q.GetNetname()==net or not q.IsOnLayer(layer):continue
            box=q.GetBoundingBox();rect(p.ToMM(box.GetX())-.3,p.ToMM(box.GetY())-.3,p.ToMM(box.GetRight())+.3,p.ToMM(box.GetBottom())+.3)
    for t in b.GetTracks():
        if t.GetNetname()==net:continue
        if isinstance(t,p.PCB_VIA):
            a=t.GetPosition();diskline(p.ToMM(a.x),p.ToMM(a.y),p.ToMM(a.x),p.ToMM(a.y),p.ToMM(t.GetWidth())/2+.3)
        elif t.GetLayer()==layer:
            a=t.GetStart();c=t.GetEnd();diskline(p.ToMM(a.x),p.ToMM(a.y),p.ToMM(c.x),p.ToMM(c.y),p.ToMM(t.GetWidth())/2+.3)
    return out
def astar(start,end,blocked):
    s=grid(*start);g=grid(*end)
    for x,y in [s,g]:
        if blocked[y*W+x]:raise RuntimeError(f'Blocked route endpoint {start} -> {end}')
    heap=[(0,0,s)];cost={s:0};prev={};count=0
    while heap:
        _,c,u=heapq.heappop(heap)
        if c!=cost.get(u):continue
        if u==g:
            path=[g]
            while path[-1]!=s:path.append(prev[path[-1]])
            return list(reversed(path))
        count+=1
        if count>300000:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx=u[0]+dx;ny=u[1]+dy
            if not(0<=nx<W and 0<=ny<H) or blocked[ny*W+nx]:continue
            vv=(nx,ny);nc=c+1
            if nc<cost.get(vv,10**10):
                cost[vv]=nc;prev[vv]=u;heapq.heappush(heap,(nc+abs(nx-g[0])+abs(ny-g[1]),nc,vv))
    raise RuntimeError('No route')
failed=[]
for net in ['HO','LO','HB','VDD','BST','BST_A','VIN','HI','LI','AC']:
    layer=p.In2_Cu if net in ['VDD','AC','VIN','HI','LI'] else p.B_Cu
    todo=list(nodes[net]);done=[todo.pop(0)]
    while todo:
        _,i,j=min((math.dist(a,c),i,j) for i,a in enumerate(done) for j,c in enumerate(todo));start=done[i];end=todo.pop(j)
        try:
            path=astar(start,end,obstacles(net,layer));points=[path[0]]
            for k in range(1,len(path)-1):
                if (path[k][0]-path[k-1][0],path[k][1]-path[k-1][1])!=(path[k+1][0]-path[k][0],path[k+1][1]-path[k][1]):points.append(path[k])
            points.append(path[-1]);coords=[start]+[world(a) for a in points]+[end]
            for a,c in zip(coords,coords[1:]):tr(net,*a,*c,.15,layer)
            done.append(end)
        except RuntimeError as e:failed.append((net,start,end,str(e)));done.append(end)
    print(net,'routed',flush=True)
b.BuildConnectivity();p.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b)
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')));f=p.ZONE_FILLER(b);f.Fill(b.Zones());p.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b)
p.WriteDRCReport(b,str(OUT/'drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
(OUT/'routing-status.json').write_text(json.dumps({'failed':failed},indent=2));print('Routing pass complete, failures',failed)

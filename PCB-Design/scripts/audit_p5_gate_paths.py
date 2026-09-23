"""Audit actual gate-track graph, splitting intersections to expose shortcuts."""
from p5_data import *
import sys,json,math,heapq
import pcbnew as p
path=Path(sys.argv[1]) if len(sys.argv)>1 else OUT/(NAME+'-gate-candidate.kicad_pcb')
b=p.LoadBoard(str(path))
def point(a):return(round(p.ToMM(a.x),6),round(p.ToMM(a.y),6))
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return(a[0]-b[0],a[1]-b[1])
def on(q,a,c):return abs(cross(sub(q,a),sub(c,a)))<1e-6 and min(a[0],c[0])-1e-6<=q[0]<=max(a[0],c[0])+1e-6 and min(a[1],c[1])-1e-6<=q[1]<=max(a[1],c[1])+1e-6
def intersections(a,c,d,e):
    r=sub(c,a);s=sub(e,d);den=cross(r,s)
    if abs(den)<1e-10:return {q for q in [a,c,d,e] if on(q,a,c) and on(q,d,e)}
    t=cross(sub(d,a),s)/den;u=cross(sub(d,a),r)/den
    if -1e-6<=t<=1+1e-6 and -1e-6<=u<=1+1e-6:return {(round(a[0]+t*r[0],6),round(a[1]+t*r[1],6))}
    return set()
report={}
for net,start,ends in [('HO',(37.25,37.6),[(43.19,31.5),(61.19,31.5)]),('LO',(35.75,37.6),[(43.19,35.7),(61.19,35.7)])]:
    seg=[(point(t.GetStart()),point(t.GetEnd())) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.B_Cu and t.GetNetname()==net]
    cuts=[set(pair) for pair in seg]
    for i,(a,c) in enumerate(seg):
        for j,(d,e) in enumerate(seg[:i]):
            found=intersections(a,c,d,e);cuts[i]|=found;cuts[j]|=found
    graph={}
    for (a,c),nodes in zip(seg,cuts):
        seq=sorted(nodes,key=lambda q:math.dist(a,q))
        for q,r in zip(seq,seq[1:]):
            length=math.dist(q,r)
            if length>1e-8:graph.setdefault(q,[]).append((r,length));graph.setdefault(r,[]).append((q,length))
    dist={start:0};queue=[(0,start)];previous={}
    while queue:
        v,q=heapq.heappop(queue)
        if v>dist[q]+1e-9:continue
        for r,w in graph.get(q,[]):
            if v+w<dist.get(r,1e9):dist[r]=v+w;previous[r]=q;heapq.heappush(queue,(v+w,r))
    lengths=[dist.get(q) for q in ends];assert all(v is not None for v in lengths),(net,lengths)
    delta=abs(lengths[0]-lengths[1]);report[net]={'actual_shortest_B_Cu_path_mm':lengths,'difference_mm':delta,'within_0.05_mm':delta<=.05}
report['scope']='Centreline graph including segment intersections; excludes pad spreading, F.Cu escapes, vias, and inductance. Equal length is not equal gate-loop impedance.'
(OUT/'gate-path-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert all(report[n]['within_0.05_mm'] for n in ['HO','LO']),'Gate paths not matched'

"""Candidate-only P3 gate/source routing pass, after route_p3.py.
Writes a separate .kicad_pcb and DRC report; never overwrites the source board.
Paired-source corridors are geometric, not electrically isolated Kelvin nets.
Requires both switch cells to have their gate side facing left.
"""
from p6_data import *
import math,heapq,json
import pcbnew as p
import wx
app=wx.App(False)
src=OUT/(NAME+'.kicad_pcb');dest=OUT/(NAME+'-gate-candidate.kicad_pcb')
b=p.LoadBoard(str(src));fps={f.GetReference():f for f in b.GetFootprints()}
nets={n.GetNetname():n for n in b.GetNetInfo().NetsByName().values()}
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def pos(ref,pin):
 q=next(q for q in fps[ref].Pads() if q.GetNumber()==str(pin));a=q.GetPosition();return p.ToMM(a.x),p.ToMM(a.y)
def tr(n,a,c,layer,w=.15):
 if math.dist(a,c)<1e-6:return
 t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*c));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t)
# Fail explicitly rather than apply this topology to the earlier mirrored cell.
assert pos('QH1',1)[0]<48,'Expected updated left-facing QH1 gate'
# Edit only serialized segment records in the separate candidate copy; KiCad 7
# SWIG track-removal ownership can invalidate wrappers during bulk deletion.
import re
codes={name:nets[name].GetNetCode() for name in ['HO','LO','AC']}
lines=[]
for line in src.read_text().splitlines(True):
 remove=False
 if line.lstrip().startswith('(segment '):
  mm=re.search(r'\(net (\d+)\)',line);netcode=int(mm.group(1)) if mm else -1
  remove=('(layer "B.Cu")' in line and netcode in [codes['HO'],codes['LO']]) or ('(layer "In2.Cu")' in line and netcode==codes['AC'])
 if not remove:lines.append(line)
dest.write_text(''.join(lines))
b=p.LoadBoard(str(dest));fps={f.GetReference():f for f in b.GetFootprints()}
nets={n.GetNetname():n for n in b.GetNetInfo().NetsByName().values()}
# Reuse only pure grid/obstacle function definitions from the primary router.
source=(ROOT/'scripts/route_p6.py').read_text();exec(source[source.index('step=.1'):source.index('failed=[]')])
report={'source':str(src),'output':str(dest),'status':'candidate, engineering review required','branches':{},'errors':[],'source_return':'Geometric paired returns; existing same-net plane connections remain. Not net-isolated Kelvin.'}
def route(n,a,c,layer,w=.15,corridor=None):
 blocked=obstacles(n,layer)
 if corridor:
  # Restrict source routing to 3 mm around its corresponding gate path.
  allowed=bytearray(W*H)
  for q in corridor:
   gx,gy=grid(*q)
   for yy in range(max(0,gy-30),min(H,gy+31)):
    for xx in range(max(0,gx-30),min(W,gx+31)):allowed[yy*W+xx]=1
  for index in range(W*H):
   if not allowed[index]:blocked[index]=1
  # Allow a short fanout around return endpoints independently of gate endpoints.
  for e in [a,c]:
   gx,gy=grid(*e)
   for yy in range(max(0,gy-32),min(H,gy+33)):
    for xx in range(max(0,gx-32),min(W,gx+33)):
     if math.dist(world((xx,yy)),e)<3.1:blocked[yy*W+xx]=obstacles_cached[yy*W+xx]
 path=astar(a,c,blocked);points=[path[0]]
 for k in range(1,len(path)-1):
  if (path[k][0]-path[k-1][0],path[k][1]-path[k-1][1])!=(path[k+1][0]-path[k][0],path[k+1][1]-path[k][1]):points.append(path[k])
 points.append(path[-1]);coords=[a]+[world(q) for q in points]+[c]
 for u,z in zip(coords,coords[1:]):tr(n,u,z,layer,w)
 return coords,[world(q) for q in path],sum(math.dist(u,z) for u,z in zip(coords,coords[1:]))
def no_pour(a,c):
 # A copper-only exclusion on L3. Tracks/vias remain permitted; L2 is untouched.
 z=p.ZONE(b);z.SetLayer(p.In2_Cu);z.SetIsRuleArea(True);z.SetDoNotAllowCopperPour(True)
 z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
 x0=min(a[0],c[0])-.5;x1=max(a[0],c[0])+.5;y0=min(a[1],c[1])-.5;y1=max(a[1],c[1])+.5
 poly=z.Outline();poly.NewOutline()
 for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:poly.Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)
# Dedicated geometric pickup vias near each gate feed, connected to source pad 2.
pickups={}
for q,x,y in [('QH1',43.19,32.7),('QH2',61.19,32.7),('QL1',43.19,38.67),('QL2',61.19,38.67)]:
 n='AC' if q.startswith('QH') else 'DC-'
 t=p.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(nets[n]);b.Add(t)
 tr(n,pos(q,2),(x,y),p.F_Cu,.2);pickups[q]=(x,y)
gates={}
for n,start,star,ends in [('HO',(37.25,37.6),(52.2,31),[(43.19,31.5),(61.19,31.5)]),('LO',(35.75,37.6),(52.2,40),[(43.19,35.7),(61.19,35.7)])]:
 try:
  common=[];common_grid=[];cl=0
  trunk=[start,(36,40.8),(52.2,40.8),star] if n=='LO' else [start,star]
  for aa,cc in zip(trunk,trunk[1:]):
   co,pa,le=route(n,aa,cc,p.B_Cu);common+=co;common_grid+=pa;cl+=le
  branches=[]
  for index,end in enumerate(ends):
   waypoints=[star,end]
   if n=='HO' and index==0:waypoints=[star,(52.2,33.2),(44.5,33.2),(44.5,31.5),end]
   coords=[];path=[];length=0
   for aa,cc in zip(waypoints,waypoints[1:]):
    co,pa,le=route(n,aa,cc,p.B_Cu);coords+=co;path+=pa;length+=le
   branches.append((coords,path,length))
  gates[n]=(common,common_grid,branches)
  report['branches'][n]={'shared_trunk_mm':cl,'star_to_gate_resistor_mm':[a[2] for a in branches],'branch_difference_mm':abs(branches[0][2]-branches[1][2])}
 except RuntimeError as e:report['errors'].append(n+': '+str(e))
for gate,n,start,refs in [('HO','AC',(40.2,34.5),['QH1','QH2']),('LO','DC-',(32.8,35),['QL1','QL2'])]:
 if gate not in gates:continue
 common,common_grid,branches=gates[gate];star=common[-1]
 # Source star is projected directly above the gate star, with no through via there.
 try:
  obstacles_cached=obstacles(n,p.In2_Cu)
  coords,_,length=route(n,start,star,p.In2_Cu,.15,common_grid)
  for a,c in zip(coords,coords[1:]):no_pour(a,c)
  source_lengths=[]
  for ref,(gate_coords,path,_) in zip(refs,branches):
   obstacles_cached=obstacles(n,p.In2_Cu)
   coords,_,length=route(n,star,pickups[ref],p.In2_Cu,.15,path)
   for a,c in zip(coords,coords[1:]):no_pour(a,c)
   source_lengths.append(length)
  report['branches'][gate]['source_branch_mm']=source_lengths
 except RuntimeError as e:report['errors'].append(gate+' source: '+str(e))
b.BuildConnectivity();p.SaveBoard(str(dest),b);b=p.LoadBoard(str(dest));f=p.ZONE_FILLER(b);f.Fill(b.Zones());p.SaveBoard(str(dest),b)
p.WriteDRCReport(b,str(OUT/'gate-candidate-drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
(OUT/'gate-candidate-review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))









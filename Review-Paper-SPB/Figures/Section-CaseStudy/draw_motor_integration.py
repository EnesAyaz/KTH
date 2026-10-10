import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pathlib import Path
OUT=Path(__file__).parent
view=np.array([.72,-.65,.48]);view/=np.linalg.norm(view)
right=np.cross([0,0,1],view);right/=np.linalg.norm(right);up=np.cross(view,right)
fig,ax=plt.subplots(figsize=(10,8));ax.set_aspect('equal');ax.axis('off')
def paint(v,c,e='#657783',lw=.35):
 v=np.array(v);ax.add_patch(Polygon(np.column_stack((v@right,v@up)),facecolor=c,edgecolor=e,linewidth=lw))
def disk(r,x,c):
 t=np.linspace(0,2*np.pi,180);paint(np.column_stack((np.full_like(t,x),r*np.cos(t),r*np.sin(t))),c)
def cylinder_side(r,x0,x1,c):
 ts=np.linspace(0,2*np.pi,180)
 parts=[]
 for t,u in zip(ts[:-1],ts[1:]):
  if np.dot([0,np.cos((t+u)/2),np.sin((t+u)/2)],view)>0:
   v=np.array([[x0,r*np.cos(t),r*np.sin(t)],[x1,r*np.cos(t),r*np.sin(t)],[x1,r*np.cos(u),r*np.sin(u)],[x0,r*np.cos(u),r*np.sin(u)]])
   parts.append(v)
 for v in sorted(parts,key=lambda v:np.mean(v@view)):paint(v,c,c,.15)
def box(t,r,w,a,b,d,c):
 ra=np.array([0,np.cos(t),np.sin(t)]);ta=np.array([0,-np.sin(t),np.cos(t)])
 vs=[np.array([x,0,0])+rr*ra+tt*ta for x in [a,b] for rr,tt in [(r,-w/2),(r,w/2),(r+d,w/2),(r+d,-w/2)]]
 return [(np.array([vs[i] for i in ids]),c) for ids in [[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]]
disk(1,-1.4,'#b8c4cc');cylinder_side(1,-1.4,1.4,'#b8c4cc')
parts=[];plates=[];count=0
for k in range(16):
 t=2*np.pi*k/16
 visible=np.dot([0,np.cos(t),np.sin(t)],view)>0
 for j in range(3):
  x=-1.28+j*.86;count+=1
  if visible:
   parts+=box(t,1.06,.355,x,x+.78,.022,'#328568')
   # Eight FETs per four-parallel phase leg, schematically positioned.
   for dx in [.12,.25,.46,.59]:
    for side in [-.095,.095]:
     ra=np.array([0,np.cos(t),np.sin(t)]);ta=np.array([0,-np.sin(t),np.cos(t)])
     block=box(t,1.084,.065,x+dx,x+dx+.075,.035,'#34414a')
     parts += [(vv+side*ta,cc) for vv,cc in block]
   # Local capacitor bank and two driver packages.
   for dx in [.14,.26,.38,.50,.62]:
    block=box(t,1.084,.055,x+dx,x+dx+.07,.044,'#d9caa8')
    parts+=block
   for dx in [.30,.52]:
    block=box(t,1.084,.052,x+dx,x+dx+.06,.025,'#39434b')
    ta=np.array([0,-np.sin(t),np.cos(t)])
    parts += [(vv-.15*ta,cc) for vv,cc in block]
 if visible:
  # One transparent cold plate spans all three axial legs.
  plates+=box(t,1.18,.39,-1.32,1.34,.06,(.62,.75,.83,.13))
  # Laminated cell-local dc busbar along one side.
  ta=np.array([0,-np.sin(t),np.cos(t)])
  for rr,col in [(1.10,'#cf9148'),(1.11,'#e8d183')]:
   parts += [(vv+.205*ta,cc) for vv,cc in box(t,rr,.033,-1.30,1.30,.008,col)]
  # Insulated axial phase-lead corridor, ending at the motor front.
  for j,col in enumerate(['#ce852c','#80559c','#59636c']):
   shift=(-.225-.045*j)*ta
   parts += [(vv+shift,cc) for vv,cc in box(t,1.065,.025,-1.15+j*.86,1.42,.012,col)]
assert count==48
for vv,cc in sorted(parts,key=lambda f:np.mean(f[0]@view)):paint(vv,cc,lw=.22)
for vv,cc in sorted(plates,key=lambda f:np.mean(f[0]@view)):paint(vv,cc,e='#8ba9ba',lw=.4)
cylinder_side(1.015,1.34,1.45,'#8c9fab');disk(1.015,1.45,'#8c9fab');disk(.78,1.458,'#dce3e7')
cylinder_side(.18,1.465,1.93,'#9baab4');disk(.18,1.93,'#aab9c2')
ax.set_xlim(-2.05,2.05);ax.set_ylim(-1.50,1.60)
fig.tight_layout(pad=0)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'motor_cell_integration.{ext}',dpi=220,bbox_inches='tight',pad_inches=.02)

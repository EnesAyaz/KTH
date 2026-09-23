"""Add review overlays on non-copper layers; preserve electrical geometry."""
from p5_data import *
import pcbnew as p
import wx
import json

app = wx.App(False)
path = OUT / (NAME + '.kicad_pcb')
b = p.LoadBoard(str(path))

def vec(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))

def line(a, c, layer, width=.22):
    s = p.PCB_SHAPE()
    s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(vec(*a))
    s.SetEnd(vec(*c))
    s.SetWidth(p.FromMM(width))
    s.SetLayer(layer)
    b.Add(s)

def label(value, x, y, layer):
    t = p.PCB_TEXT(b)
    t.SetText(value)
    t.SetPosition(vec(x, y))
    t.SetTextSize(vec(.8, .8))
    t.SetTextThickness(p.FromMM(.12))
    t.SetLayer(layer)
    b.Add(t)

# The overlay is a separate review board, keeping the main board unchanged.
# Arrows through semiconductor interiors are illustrative, not copper tracks.
power = [(49.05,26.95),(49.05,28.1),(48.425,29.2),
         (48.425,30.5),(49.275,32),(49.275,35),(48.425,36.5),
         (49.275,38),(49.625,41.8)]
for a, c in zip(power, power[1:]):
    line(a, c, p.Dwgs_User, .3)
# Illustrative L2 current return; current spreads in the actual plane.
for a, c in zip([(49.625,41.8),(55.5,41.8),(55.5,23.8),(49.05,23.8)],
                [(55.5,41.8),(55.5,23.8),(49.05,23.8),(49.05,25.05)]):
    line(a, c, p.Dwgs_User, .15)
label('POWER: thick = forward; thin = illustrative L2 return',44,59,p.Dwgs_User)
tracks = []
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA):
        continue
    net, layer = t.GetNetname(), t.GetLayer()
    gate = net in ['HO','LO','GH1','GH2','GL1','GL2']
    source = net in ['AC','DC-'] and layer == p.In2_Cu
    if not (gate or source):
        continue
    a, c = t.GetStart(), t.GetEnd()
    a, c = (p.ToMM(a.x),p.ToMM(a.y)), (p.ToMM(c.x),p.ToMM(c.y))
    line(a,c,p.Cmts_User,.25 if gate else .12)
    tracks.append(dict(net=net,layer=b.GetLayerName(layer),a=a,c=c))
label('GATES: thick = drive; thin = L3 source return',44,61,p.Cmts_User)
label('Same-net plane paths remain; not isolated Kelvin returns',44,63,p.Cmts_User)
label('H1/H2 measure I_OUT; individual-device path unfinished',44,65,p.Dwgs_User)
dest = OUT / (NAME + '-loop-review.kicad_pcb')
p.SaveBoard(str(dest),b)
p.WriteDRCReport(b,str(OUT/'loop-review-drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
(OUT/'loop-geometry.json').write_text(json.dumps(dict(power=power,gate=tracks),indent=2))
print('Saved non-copper loop review:',dest)

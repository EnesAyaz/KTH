import pcbnew, json
b=pcbnew.LoadBoard(r"hardware\spb-bb-fab\spb-bb-fab.kicad_pcb")
out=[]
for fp in sorted(b.GetFootprints(), key=lambda f:(f.GetReference()[0], int(''.join(c for c in f.GetReference() if c.isdigit()) or 0))):
    pads={}
    for p in fp.Pads():
        if p.GetNumber(): pads.setdefault(p.GetNumber(), p.GetNetname())
    out.append((fp.GetReference(), fp.GetValue(), pads))
json.dump(out, open(r"hardware\spb-bb-fab\pad_nets.json","w"), indent=0)
for r,v,p in out:
    if r.startswith("C") and r[1:].isdigit() and int(r[1:])<100: continue
    print(r, "|", v, "|", " ".join("%s:%s"%(k,n) for k,n in sorted(p.items(), key=lambda t: (len(t[0]),t[0]))))
caps=[(r,v,p) for r,v,p in out if r.startswith("C") and r[1:].isdigit() and int(r[1:])<100]
print("power caps", len(caps), set((v, tuple(sorted(set(p.values())))) for r,v,p in caps))

from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=root/'build_digest.py';s=p.read_text(encoding='utf-8')
s=s.replace("h('Cell Count Is Not Pole Count')","h('Cell Voltage and Winding Capacity')")
s=s.replace('That is why 24 appeared previously: it was one intersection of assumptions, not a control requirement.', 'Here 24 cells arises from intersecting the 100 V class with this 72-slot construction; rephasing does not require that count.')
s=s.replace('A verified two-cell, 36-slot', 'A calculated two-cell, 36-slot')
s=s.replace('A 150–200 V versus 100 V shortlist and 2:1 starting ratio merit', 'A comparison of 150 V and 200 V against 100 V, with a 2:1 starting ratio, merits')
p.write_text(s,encoding='utf-8')

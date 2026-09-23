from pathlib import Path
p=Path('scripts/p3_data.py');s=p.read_text();s+='''
# Symmetric six-capacitor fast banks above each pair; lower banks supplementary.
for j in range(6):
    c=copy.deepcopy(parts['C'+str(j+1)]);c['x']-=18;parts['C'+str(19+j)]=c
    c=copy.deepcopy(parts['C'+str(7+j)]);c['x']+=18;parts['C'+str(25+j)]=c
bus_caps=['C'+str(i) for i in list(range(1,13))+list(range(19,31))]
''';p.write_text(s)
p=Path('scripts/build_p3_board.py');s=p.read_text();a=s.index('    if cell==2:');z=s.index("    track('AC'",a)
s=s[:a]+'''    for x in [9.75,11.85,13.95,16.05,18.15,20.25]:
        for n,py,yy in [('DC+',10.95,12.1),('DC-',9.05,7.8)]:
            track(n,x,py,x,yy,.85);via(n,*xy(x,yy,cell))
            if n=='DC-':via(n,*xy(x,yy-.7,cell));track(n,x,yy,x,yy-.7,.6)
    zone('DC+',p.F_Cu,[xy(x,y,cell) for x,y in [(9.1,11.7),(21,11.7),(21,13),(13.3,13),(13.3,13.6),(9.1,13.6)]])
''' +s[z:]
a=s.index('# Common current collectors')
s=s[:a]+'''# Supplementary lower banks connect to the overlapping DC collectors.
for ref in ['C'+str(i) for i in list(range(7,13))+list(range(25,31))]:
    x=parts[ref]['x'];tr('DC+',x,44.95,x,46.1,.85);via('DC+',x,46.1)
    tr('DC-',x,43.05,x,42.5,.85);via('DC-',x,42.5)
for x in [42.1,60.1]:zone('DC+',p.F_Cu,[(x,45.7),(x+11.9,45.7),(x+11.9,47),(x,47)])
''' +s[a:]
s=s.replace('12 x 1uF 100V / ALL CAPS TOP','24 x 1uF 100V / ALL CAPS TOP').replace("ref.startswith('C') and ref[1:].isdigit() and int(ref[1:])<=12","ref in bus_caps")
p.write_text(s)
p=Path('scripts/build_p3_schematic.py');s=p.read_text();s=s.replace("for j in range(12):put('C'+str(j+1),170+(j%6)*39,45+(j//6)*33)","for j,ref in enumerate(bus_caps):put(ref,165+(j%8)*30,38+(j//8)*25)")
s=s.replace('C1-C6 ABOVE RIGHT CELL; C7-C12 BELOW LEFT CELL. ALL COMPONENTS ON TOP FACE.','24 BUS CAPS: SIX ABOVE AND SIX BELOW EACH PAIR. ALL ON TOP FACE.')
p.write_text(s)
p=Path('scripts/check_p3.py');s=p.read_text().replace('all 12 local bus capacitors','all 24 local bus capacitors');p.write_text(s)

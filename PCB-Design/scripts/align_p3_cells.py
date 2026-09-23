from pathlib import Path
p=Path('scripts/p3_data.py');s=p.read_text();s+='''
# Both parallel cells face the driver on the left.
for ref,x,y in [('QH1',48,32),('QL1',48,38),('RGH1',43.7,30.77),('RGL1',43.7,36.77),('JGH1',41.05,30.77),('JGL1',41.05,36.77)]:
    parts[ref]['x']=x;parts[ref]['y']=y;parts[ref]['angle']=0
for i in range(7,13):parts['C'+str(i)]['angle']=90
''';p.write_text(s)
p=Path('scripts/build_p3_board.py');s=p.read_text().replace('(63-x,54-y) if cell==1 else (51+x,16+y)','(33+x,16+y) if cell==1 else (51+x,16+y)')
a=s.index('    for x in [9.75,11.85');z=s.index("    track('AC'",a)
s=s[:a]+'''    if cell==2:
        for x in [9.75,11.85,13.95,16.05,18.15,20.25]:
            for n,py,yy in [('DC+',10.95,12.1),('DC-',9.05,7.8)]:
                track(n,x,py,x,yy,.85);via(n,*xy(x,yy,cell))
                if n=='DC-':via(n,*xy(x,yy-.7,cell));track(n,x,yy,x,yy-.7,.6)
        zone('DC+',p.F_Cu,[xy(x,y,cell) for x,y in [(9.1,11.7),(21,11.7),(21,13),(13.3,13),(13.3,13.6),(9.1,13.6)]])
    else:
        # Lower capacitor row: source side above, positive side below.
        for ref in ['C'+str(i) for i in range(7,13)]:
            x=parts[ref]['x']
            tr('DC+',x,44.95,x,46.1,.85);via('DC+',x,46.1)
            tr('DC-',x,43.05,x,41.8,.85);via('DC-',x,41.8)
        zone('DC+',p.F_Cu,[(42.1,45.7),(57.5,45.7),(57.5,47),(42.1,47)])
        tr('DC+',56.5,46.1,56.5,29.2,2.0)
        tr('DC+',56.5,29.2,46.725,29.2,1.0)
''' +s[z:]
s=s.replace("vx=gx+(.5 if q.endswith('1') else -.5)","vx=gx-.5")
s=s.replace("text('DC-',30,23)","text('DC-',33,25)")
p.write_text(s)
p=Path('scripts/route_p3.py');s=p.read_text();a=s.index("for ref,x,y in [('RGH1'");z=s.index('for ref,pin,x,y',a)
s=s[:a]+"for ref,x,y in [('RGH1',43.19,31.5),('RGL1',43.19,35.7),('RGH2',61.19,31.5),('RGL2',61.19,35.7)]:escape(ref,1,x,y)\n"+s[z:];s=s.replace("[(42,35),(72,35)]","[(54,35),(72,35)]");p.write_text(s)

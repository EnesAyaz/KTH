from pathlib import Path
p=Path('scripts/p3_data.py');s=p.read_text().replace("('TP2',40,25)","('TP2',44,23)");s+="\nparts['TP5']['x']=39;parts['TP5']['y']=49\n";p.write_text(s)
p=Path('scripts/route_p3.py');s=p.read_text().replace("nodes['VDD'].append(dp(51.8,46))","nodes['VDD'].append((39.8,49))");p.write_text(s)
p=Path('scripts/build_p3_board.py');s=p.read_text().replace("text('DC+',14,7.8);text('DC-',30,7.8)","text('DC+',14,6.8);text('DC-',30,6.8)").replace("if ref in ['JDC1','JDC2']:text(ref,x,y+7,size=.8)","if ref in ['JDC1','JDC2']:label(ref,x,y+7)");p.write_text(s)

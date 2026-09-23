from pathlib import Path
for n,a,b in [('p3_data.py',"c['x']-=6","c['x']-=9"),('build_p3_board.py','ex-6,ey','ex-9,ey'),('route_p3.py','return x-6,y','return x-9,y')]:
 p=Path('scripts')/n;s=p.read_text().replace(a,b)
 if n=='route_p3.py':s=s.replace('escape(ref,pin,x-6,y)','escape(ref,pin,x-9,y)')
 p.write_text(s)

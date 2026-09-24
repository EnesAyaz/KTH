from pathlib import Path
import zipfile
from pypdf import PdfReader
import openpyxl
o=Path('reports/EPC9186-inductance');o.mkdir(exist_ok=True)
z=zipfile.ZipFile('C:/Users/enesa/Downloads/EPC9186 Development Board Gerbers.zip')
for n in z.namelist():
 if not n.endswith('/'):
  (o/Path(n).name).write_bytes(z.read(n))
for n in ['EPC9186_Schematic.pdf','EPC9186_qsg.pdf']:
 p=PdfReader('C:/Users/enesa/Downloads/'+n)
 text='\n'.join(f'PAGE {i+1}\n'+x.extract_text() for i,x in enumerate(p.pages))
 (o/(n+'.txt')).write_text(text,encoding='utf-8')
 print(n,len(p.pages))
w=openpyxl.load_workbook('C:/Users/enesa/Downloads/EPC9186BOM (1).xlsx',data_only=True)
rows=[]
for s in w:
 for row in s.iter_rows(values_only=True):
  line=' | '.join(str(v) if v is not None else '' for v in row)
  rows.append(line)
(o/'bom.txt').write_text('\n'.join(rows))
print('\n'.join(rows)[:15000])
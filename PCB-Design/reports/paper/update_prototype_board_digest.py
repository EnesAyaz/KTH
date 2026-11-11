from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import xml.etree.ElementTree as ET
import base64,re,subprocess,hashlib,json
P=Path('reports/paper');SRC=P/'Submission-Files/Digest_LowVoltageGaN_SPB_reframed_6page_2026-11-05.docx';OUT=P/'Submission-Files/Digest_LowVoltageGaN_SPB_PrototypeBoard_2026-11-05.docx'
A=P/'icpe/prototype_board_update_2026-11-05';A.mkdir(exist_ok=True)
F=P/'icpe/low_voltage_gan_digest_2026-11-05';board=Path('reports/slides/revb_pptx/img/r3d_load_nohs.png')
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest()

def rename(t):
 return re.sub(r'load[- ]board',lambda m:'PROTOTYPE BOARD' if m[0].isupper() else 'Prototype Board' if m[0]=='Load Board' else 'Prototype board' if m[0][0].isupper() else 'prototype board',t,flags=re.I)
ET.register_namespace('','http://www.w3.org/2000/svg')
for old,new in [('load_layout_q3d','prototype_layout_q3d'),('load_workflow','prototype_workflow')]:
 root=ET.fromstring((F/(old+'.svg')).read_text(encoding='utf-8'))
 for el in root.iter():
  if el.text:el.text=rename(el.text)
 if old=='load_layout_q3d':
  e=root.find('.//{http://www.w3.org/2000/svg}image');iw,ih=Image.open(board).size;scale=min(165/iw,140/ih);w=iw*scale;h=ih*scale
  e.attrib.update({'x':str((165-w)/2),'y':str(13+(140-h)/2),'width':str(w),'height':str(h),'href':'data:image/png;base64,'+base64.b64encode(board.read_bytes()).decode()})
  for el in root.iter():
   if el.text=='(a) KiCad prototype board assembly':el.text='(a) Prototype PCB without heatsink'
 else:
  for el in root.iter():
   if el.text=='Prototype board layout':el.text='Prototype PCB layout'
 path=A/(new+'.svg');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
 for kind in ['png','pdf']:
  cmd=[r'C:\Program Files\Inkscape\bin\inkscape.com',str(path),'--export-type='+kind,'--export-filename='+str(A/(new+'.'+kind))]
  if kind=='png':cmd+=['--export-dpi=450']
  subprocess.run(cmd,check=True,capture_output=True)
 print(new,flush=True)
doc=Document(SRC);count=0
for q in doc.paragraphs:
 for r in q.runs:
  old=r.text;new=rename(old)
  if new!=old:r.text=new;count+=1
for table in doc.tables:
 for row in table.rows:
  for c in row.cells:
   for q in c.paragraphs:
    for r in q.runs:r.text=rename(r.text)
for q in doc.paragraphs:
 if q.text.startswith('Fig. 7.'):
  # Change wording in the existing run to preserve caption formatting.
  q.runs[0].text='Fig. 7. (a) Prototype PCB without heatsink. (b) Q3D prototype-board power conductors; colours identify the dc rails, switch node and device/capacitor terminals.'
  q.runs[0].text=q.runs[0].text.replace('prototype-board','prototype board')
 for bl in q._p.xpath('.//a:blip'):
  rid=bl.get(qn('r:embed'));part=doc.part.related_parts[rid]
  # Identify the two existing composites by content hash, without relying on relationship numbering.
  for old,new in [('load_layout_q3d','prototype_layout_q3d'),('load_workflow','prototype_workflow')]:
   if hashlib.sha256(part.blob).digest()==hashlib.sha256((F/(old+'.png')).read_bytes()).digest():part._blob=(A/(new+'.png')).read_bytes()
doc.core_properties.subject=rename(doc.core_properties.subject or '')
doc.save(OUT)
s='\n'.join(q.text for q in doc.paragraphs)
assert not re.search(r'load[- ]board|\bDPT\b',s,re.I)
assert len(doc.inline_shapes)==8
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==source_hash
(A/'artifact.md').write_text(f'Update the current six-page digest only. Source {SRC}; SHA256 {source_hash}. Replace all manuscript and figure-label load-board terminology with prototype board. Fig. 7(a) uses existing repository PCB render without heatsink: {board}. Reuse original composite panel sizes, all results, captions, equations, styles and layout. Previous version preserved. Original PCB silkscreen remains as rendered from CAD. Word/Poppler render QA because packaged soffice is unavailable.\n')
print(OUT);print('Renamed text runs:',count)

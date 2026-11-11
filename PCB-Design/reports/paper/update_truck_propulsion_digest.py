from pathlib import Path
import re,json,hashlib
from docx import Document
from docx.shared import RGBColor
P=Path('reports/paper/Submission-Final')
src=P/'ICPE_Digest_revised_blue_2026-11-06.docx'
out=P/'ICPE_Digest_truck_propulsion_blue_2026-11-06.docx'
qa=Path('reports/paper/icpe/truck_propulsion_2026-11-06');qa.mkdir(parents=True,exist_ok=True)
d=Document(src);changes=[]
replacements={
 'Low-Voltage GaN Utilization for High-Voltage Stacked Polyphase Bridge Traction Drives':'Low-Voltage GaN Utilization in High-Voltage Stacked Polyphase Bridge Inverters for Truck Propulsion',
 'a high-voltage traction dc link':'a high-voltage dc link for truck propulsion',
 'at traction current':'at the required phase current',
 'a 300-kW, 1200-V drive':'a 300-kW, 1200-V truck propulsion system',
 'traction inverter.':'truck propulsion.',
 'traction power levels':'truck propulsion power levels',
 'high-voltage traction drives':'high-voltage truck propulsion systems',
 'II. TRACTION REQUIREMENTS AND LOW-VOLTAGE DEVICE SELECTION':'II. TRUCK PROPULSION REQUIREMENTS AND DEVICE SELECTION',
 'A. Traction Drive Requirements':'A. Truck Propulsion Requirements',
 'the traction operating point':'the truck propulsion operating point',
}
for i,p in enumerate(d.paragraphs):
 if re.match(r'^\[\d+\]',p.text):continue
 before=p.text
 for r in p.runs:
  s=r.text
  for a,b in replacements.items():s=s.replace(a,b)
  if s!=r.text:r.text=s;r.font.color.rgb=RGBColor.from_string('0057B8')
 if p.text!=before:changes.append({'paragraph':i,'before':before,'after':p.text})
assert len(changes)==8,len(changes)
assert not any(re.search(r'\btraction\b',p.text,re.I) for p in d.paragraphs if not re.match(r'^\[\d+\]',p.text))
d.core_properties.title=d.paragraphs[0].text
d.save(out)
(qa/'changes.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source':str(src),'output':str(out),'changes':changes},ensure_ascii=False,indent=2),encoding='utf-8')
print(out)

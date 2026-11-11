from pathlib import Path
from copy import deepcopy
import subprocess,hashlib,json
from docx import Document
from docx.shared import RGBColor
ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/source_label_ai_ack_2026-11-06';A.mkdir(parents=True,exist_ok=True)
src=P/'Submission-Final/ICPE_Digest_truck_propulsion_blue_2026-11-06.docx'
out=P/'Submission-Final/ICPE_Digest_truck_propulsion_AI_ack_blue_2026-11-06.docx'
svg=(P/'icpe/revised_blue_2026-11-06/fig05_sharing_final_conditions.svg').read_text(encoding='utf-8')
assert '>S power<' in svg and '>Ls<' in svg
svg=svg.replace('>S power<','>S<').replace('>Ls<','>Lₛ<')
svg=svg.replace('x="453.000" y="110.000" font-size="7" text-anchor="end"','x="431.000" y="112.000" font-size="7" text-anchor="start"')
asset=A/'fig05_source_terminal_corrected';asset.with_suffix('.svg').write_text(svg,encoding='utf-8')
for typ in ['png','pdf']:
 args=[r'C:\Program Files\Inkscape\bin\inkscape.com',str(asset.with_suffix('.svg')),'--export-type='+typ,'--export-filename='+str(asset.with_suffix('.'+typ))]
 if typ=='png':args.append('--export-dpi=450')
 subprocess.run(args,check=True,capture_output=True)
d=Document(src);shape=d.inline_shapes[4];rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
d.part.related_parts[rid]._blob=asset.with_suffix('.png').read_bytes()
for p in d.paragraphs:
 if p.text.startswith('Fig. 5.'):
  r=p.runs[0];r.text=p.text+' S denotes the power-source terminal, K the Kelvin-source return, and Lₛ the power-source inductance.'
  for rr in list(p.runs)[1:]:rr._r.getparent().remove(rr._r)
  r.font.color.rgb=RGBColor.from_string('0057B8')
ref=next(p for p in d.paragraphs if p.text=='REFERENCES')
header=ref.insert_paragraph_before('ACKNOWLEDGMENT',style=ref.style);header._p.getparent().replace(header._p,deepcopy(ref._p))
# The clone shares the reference heading's typography, with its text replaced.
header=ref._p.getprevious()
for el in header.xpath('.//w:t'):el.text='ACKNOWLEDGMENT'
ack=ref.insert_paragraph_before('OpenAI Codex assisted with drafting and language editing throughout this manuscript, preparation of Figs. 1–8 from project data, and scripting for LTspice runs and result processing in Sections III–V. The authors retain responsibility for the technical content and its verification.')
template=next(p for p in d.paragraphs if p.text.startswith('The study links'))
ack._p.insert(0,deepcopy(template._p.pPr))
for r in ack.runs:
 r.font.name='Times New Roman';r.font.size=template.runs[0].font.size;r.font.color.rgb=RGBColor.from_string('0057B8')
d.save(out)
(A/'source_hash.json').write_text(json.dumps({src.name:hashlib.sha256(src.read_bytes()).hexdigest()},indent=2))
print(out)

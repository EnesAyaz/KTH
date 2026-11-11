"""Apply the latest author exclusions and place short red scope notes locally."""
from pathlib import Path
from copy import deepcopy
import re,json,hashlib
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

P=Path(__file__).parent
SRC=P/'Submission-Files/Digest-ParasiticAwareSPB.docx'
OUT=P/'Submission-Files/Digest-ParasiticAwareSPB_revised_2026-11-02.docx'
QA=P/'icpe/latest_digest_qa';QA.mkdir(exist_ok=True)
doc=Document(SRC);pars=list(doc.paragraphs);audit=[]

def isred(r):
 c=r.font.color.rgb
 return c is not None and int(str(c)[:2],16)>160 and int(str(c)[2:4],16)<80 and int(str(c)[4:],16)<80

notes={
 2:'Experimental validation is planned for the full paper; details are omitted due to the digest page limit.',
 22:'Due to the page limit, the voltage-partition discussion is deferred to the full paper.',
 29:'Due to the page limit, the capacitance derivation is deferred to the full paper.',
 36:'Due to the page limit, device-data normalization and screening limits are deferred to the full paper.',
 43:'Due to the page limit, gate-drive and simulation details are deferred to the full paper.',
 45:'Due to the page limit, the full paper will expand the current-range and gate-margin assessment.',
 52:'Due to the page limit, energy integration and the thermal model are deferred to the full paper.',
 62:'Due to the page limit, the detailed parallel-count comparison is deferred to the full paper.',
 65:'Due to the page limit, the full paper will detail the current-sharing perturbations.',
 71:'Due to the page limit, driver loading and gate-voltage margins are deferred to the full paper.',
 75:'Due to the page limit, layout symmetry and Kelvin-return details are deferred to the full paper.',
 78:'Due to the page limit, inter-driver timing and routed-network checks are deferred to the full paper.',
 88:'Due to the page limit, shared inductance and mutual coupling are deferred to the full paper.',
 99:'Due to the page limit, network-model comparisons and drive optimization are deferred to the full paper.',
 105:'Due to the page limit, layout refinement and loss updates are deferred to the full paper.',
 110:'Due to the page limit, the experimental DPT procedure is deferred to the full paper.',
 113:'Due to the page limit, system integration and insulation details are deferred to the full paper.',
 115:'Due to the page limit, final design conclusions will be presented in the full paper.'
}

for i,value in notes.items():
 q=pars[i]
 if i==2:
  # The abstract's short scope note stays in the abstract, with only this run red.
  for r in list(q.runs):
   if isred(r):r._element.getparent().remove(r._element)
  r=q.add_run(' '+value);r.font.color.rgb=RGBColor.from_string('EE0000')
  audit.append({'source_paragraph':i,'replacement':value});continue
 el=OxmlElement('w:p');q._p.addnext(el);new=Paragraph(el,q._parent);new.style=doc.styles['Normal']
 r=new.add_run(value);r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=RGBColor.from_string('EE0000')
 audit.append({'source_paragraph':i,'replacement':value})

for i,q in enumerate(pars):
 if i!=2:
  redtext=''.join(r.text for r in q.runs if isred(r))
  if redtext:audit.append({'source_paragraph':i,'removed':redtext})
  for r in list(q.runs):
   if isred(r):r._element.getparent().remove(r._element)
 # The native capacitance equation is red-marked in its entirety.
 if i==28 or (not re.search(r'\w',q.text) and not q._p.xpath('.//w:drawing | .//m:oMath | .//w:br')):
  q._p.getparent().remove(q._p)

for i,t in enumerate(list(doc.tables)):
 runs=[r for row in t.rows for c in row.cells for p in c.paragraphs for r in p.runs if r.text.strip()]
 if runs and all(isred(r) for r in runs):
  audit.append({'removed_red_table':i});t._tbl.getparent().remove(t._tbl)

for q in doc.paragraphs:
 for r in q.runs:
  old=r.text;new=re.sub(r'\(([345])\)',lambda m:'('+str(int(m[1])-1)+')',old)
  if new!=old:r.text=new

# Short captions preserve every figure/panel; the author will make further prose cuts.
captions={
 8:'Fig. 1. (a) SPB topology and isolated winding sets. (b) Three-phase submodule; each symbol represents four parallel GaN transistors, with the diode indicating reverse conduction.',
 34:'Fig. 2. On-state resistance versus charge-equivalent output capacitance for the surveyed GaN voltage classes.',
 47:'Fig. 3. Single-cell voltage stress and turn-on energy at 75 V. Legend entries specify gate-loop / commutation-loop inductance. Grey line: 90 V target.',
 55:'Fig. 4. (a) Phase-leg losses and (b) peak-current voltage stress versus parallel count at 75 V and 50 kHz. Inductance encoding follows Fig. 3.',
 67:'Fig. 5. (a) Sharing sensitivity, (b) paired gate drive, and (c) device pads and Kelvin return. HS/LS denote high/low side; HO/LO identify driver outputs.',
 84:'Fig. 6. Iterative design flow linking initial sizing, layout, parasitic extraction, switching assessment, and planned DPT correlation.',
 90:'Fig. 7. (a) Operating and (b) DPT boards; (c) commutation-loop composition; (d) individual and pair-driven DPT gate loops.',
 93:'Fig. 8. Q3D conductor models of (a) the operating board, (b) the DPT board, and (c) one cell pair. Colours identify nets.',
 101:'Fig. 9. Waveforms at 75 V and approximately 316 A: (a) worst-cell high-side drain voltage and (b) cell-1 held-off gate voltage. Drive configurations differ in bias and resistance. Grey lines mark 90 V and 0.8 V.'
}
for i,value in captions.items():
 q=pars[i];q.clear();q.add_run(value)

# Embed compact vector-derived artwork at its native physical size: main lettering
# is 7–8 pt, independent of how small the author's previous raster was displayed.
from PIL import Image
FA=P/'icpe/latest_digest_figures'
dimensions=json.loads((FA/'dimensions.json').read_text())
figures={7:'fig01_topology',33:'fig02_devices',46:'fig03_single_cell',54:'fig04_parallel_count',66:'fig05_gate_drive',83:'fig06_workflow',89:'fig07_boards',92:'fig08_q3d',100:'fig09_switching'}
for i,name in figures.items():
 inline=pars[i]._p.xpath('.//wp:inline')[0]
 for crop in inline.xpath('.//a:srcRect'):crop.getparent().remove(crop)
 rid=inline.xpath('.//a:blip')[0].get(qn('r:embed'))
 doc.part.related_parts[rid]._blob=(FA/(name+'.png')).read_bytes()
 cx=int(Pt(dimensions[name]['width_pt']));cy=int(Pt(dimensions[name]['height_pt']))
 e=inline.find(qn('wp:extent'));e.set('cx',str(cx));e.set('cy',str(cy))
 for e in inline.xpath('.//a:xfrm/a:ext'):e.set('cx',str(cx));e.set('cy',str(cy))

# Use the venue's 10 pt minimum and compact spacing; retain the author's figure sizes.
for q in doc.paragraphs:
 q.paragraph_format.line_spacing=1
 q.paragraph_format.space_after=Pt(0)
 if q.style.name.startswith('Heading'):
  q.paragraph_format.space_before=Pt(2);q.paragraph_format.keep_with_next=True
 if q.style.name not in ['Title']:
  for r in q.runs:r.font.size=Pt(10)
 if q._p.xpath('.//w:drawing'):q.paragraph_format.keep_with_next=True
 if q.style.name=='Caption':q.paragraph_format.keep_together=True
for t in doc.tables:
 for j,row in enumerate(t.rows):
  for c in row.cells:
   for q in c.paragraphs:
    q.paragraph_format.space_before=Pt(0);q.paragraph_format.space_after=Pt(0)
    q.paragraph_format.line_spacing=1;q.paragraph_format.first_line_indent=Pt(0)
    q.paragraph_format.keep_with_next=j<len(t.rows)-1
    for r in q.runs:r.font.size=Pt(10)

assert len(doc.inline_shapes)==9
assert len(doc.tables)==1
assert len(doc._element.xpath('.//m:oMath'))==4
assert not any('1.7' in q.text for q in doc.paragraphs)
(QA/'selection_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
(QA/'artifact.md').write_text(f'Latest author-selected digest. Source {SRC}, SHA256 {hashlib.sha256(SRC.read_bytes()).hexdigest()}. Remove red-marked text, both red tables, and the red capacitance equation. Red scope notes placed locally, including multiple positions within a subsection; notes explicitly cite the page limit and full-paper content. Latest steering: keep all figures, shorten captions, enlarge lettering for readability, and leave remaining body prose for the author to trim. All nine figure topics/panels and source numerical data retained in compact vector layouts; main lettering 7–8 pt at native printed size. Preserve all unmarked body wording, headings, operating-point table, citations, and native equations. Body/captions 10 pt; original A4 venue margins retained. Source remains unchanged. Word PDF export and Poppler used for visual QA because bundled LibreOffice is unavailable.',encoding='utf-8')
doc.save(OUT)
print(OUT)
print('Words:',sum(len(q.text.split()) for q in doc.paragraphs))

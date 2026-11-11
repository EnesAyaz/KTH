from pathlib import Path
from copy import deepcopy
import re,json,hashlib
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
P=Path(r'C:\Github\KTH\PCB-Design\reports\paper');SRC=P/'SPB_ICPE_complete_manuscript_with_Q3D_2026-10-29.docx';OUT=P/'SPB_ICPE_digest_original_structure_2026-11-02.docx';QA=P/'icpe/digest_original_structure_qa';QA.mkdir(exist_ok=True)
source=Document(SRC);paras=source.paragraphs;doc=Document(SRC);body=doc._element.body
for e in list(body):
 if e.tag!=qn('w:sectPr'):body.remove(e)
for n in ['Normal','Caption','Heading 1','Heading 2']:
 st=doc.styles[n];st.font.size=Pt(10);st.paragraph_format.space_after=Pt(1.5)
 if n.startswith('Heading'):st.paragraph_format.space_before=Pt(4);st.paragraph_format.keep_with_next=True
normal=doc.styles['Normal'];normal.paragraph_format.line_spacing=1
records=[]
def append(q):body.insert(len(body)-1,q._p);return q

def text(t,style='Normal',red=False):
 q=doc.add_paragraph(t,style)
 q.paragraph_format.space_after=Pt(1.5);q.alignment=3
 if style.startswith('Heading'):q.alignment=1 if style=='Heading 1' else 0
 if red:
  for r in q.runs:r.font.color.rgb=RGBColor.from_string('C00000')
 return q

def sentences(t):
 # Full sentences are selected without rewriting the retained wording.
 return re.split(r'(?<=[.!?])\s+(?=[A-Z])',t)
def src(i,first=None,last=None):
 q=deepcopy(paras[i]._p);body.insert(len(body)-1,q)
 from docx.text.paragraph import Paragraph
 pp=Paragraph(q,doc._body)
 if first is not None or last is not None:
  ss=sentences(paras[i].text);value=' '.join(ss[:first] if first is not None else ss[-last:]);pp.clear();pp.add_run(value)
 pp.paragraph_format.space_after=Pt(1.5)
 records.append({'source_paragraph':i,'selection':'whole' if first is None and last is None else f'first {first}' if first is not None else f'last {last}'})
 return pp

def red(t):return text(t,red=True)
def page():pass
def fig(i,width):
 q=src(i);q.paragraph_format.keep_with_next=True;q.paragraph_format.space_after=Pt(0)
 # Only scale the original image; the design and content remain intact.
 inline=q._p.xpath('.//wp:inline')[0];ext=inline.find(qn('wp:extent'));oldx=int(ext.get('cx'));oldy=int(ext.get('cy'));newx=int(Cm(width));newy=round(oldy*newx/oldx);ext.set('cx',str(newx));ext.set('cy',str(newy))
 for e in inline.xpath('.//a:xfrm/a:ext'):e.set('cx',str(newx));e.set('cy',str(newy))
 cp=src(i+1);cp.paragraph_format.keep_together=True

# Page 1: retain the original introduction and topology.
src(0);src(1)
ss=sentences(paras[2].text);abstract=' '.join(ss[j] for j in [0,2,4,6,8,10]);q=text(abstract);q.paragraph_format.first_line_indent=Pt(0)
for r in q.runs:r.bold=True
src(4);src(5,first=4);src(6,first=1);src(7,first=3);src(9,first=2)
fig(10,14)
page()
# Page 2: retain the original section/subsection ladder and sizing argument.
src(12);src(13)
manual=Document(P/'icpe/WrittenByHand/ICPE_Template.docx');mt=manual.paragraphs[18].text
text(' '.join(sentences(mt)[:4]));text('A peak drain–source voltage target of 90 V is adopted.')
src(15);src(16,first=3)
src(19)
text('Voltage partitioning allows the semiconductor voltage class to be selected together with the submodule count. Following the charge-based screening criterion in [9], the device figure of merit is defined as')
qq=src(23)
for rr in qq.runs:rr.text=rr.text.replace('(3)','(2)')
text('Here, Coss,Q = Qoss/Vtest is the charge-equivalent output capacitance. A higher D-FOM indicates a more favorable combination of conduction resistance and output charge. Among the surveyed devices, EPC2361 has the highest D-FOM and is selected for further investigation [10].')
red('The full paper will provide the device-comparison plot and discuss the respective datasheet test voltages and the limits of this initial screening.')
src(29)
text('A candidate arrangement of sixteen submodules gives a nominal submodule voltage of 75 V, allowing the selected 100 V devices to be considered. The available voltage margin must accommodate submodule-voltage variation and switching overshoot.')
src(33);src(34);src(35,first=3);src(37,first=2)
red('The full paper will provide the single-cell voltage-stress and switching-energy sweeps used to establish this preliminary current scale.')
src(40);src(43,first=1)
text('The thermal assessment assumes 40 °C ambient, 0.65 K/W heatsink-to-ambient for the complete leg, and 7.6 K/W junction-to-heatsink per transistor. Junction temperature and resistance are solved iteratively.')
red('The full paper will provide the parallel-count loss and voltage-stress plots. The electrical and thermal comparison is retained in Table II.')
src(48);src(49)
# Retain the original comparison table, with its number adjusted after omitting the requirements table.
src(50);el=deepcopy(source.tables[1]._tbl);body.insert(len(body)-1,el)
for q in el.xpath('.//w:p'):
 from docx.text.paragraph import Paragraph
 pp=Paragraph(q,doc._body);pp.paragraph_format.space_before=Pt(0);pp.paragraph_format.space_after=Pt(0)
src(52,first=1);text('The four-device arrangement reaches approximately 93 V when the assumed commutation inductance increases to 1 nH.')
page()
# Page 3: original gate-drive section and original three-panel figure.
src(54);src(55)
red('The full paper will detail the current-sharing sensitivity study. The principal gate-impedance and common-source mismatch cases are summarized in Fig. 5(a).')
fig(57,14)
src(59);src(61);src(62,first=1)
red('The full paper will expand the gate-loading comparison and the associated peak sink-current and switching-energy requirements.')
src(63);src(64,first=2)
red('The full paper will detail the individual gate resistors, star-connected gate branches, and dedicated Kelvin returns illustrated in Fig. 5(c).')
src(67);src(68,first=1)
red('The full paper will evaluate inter-driver timing separately from within-pair branch matching and present the corresponding layout iterations.')
page()
# Page 4: original layout/extraction subsections and separate PCB / Q3D figures.
src(70);src(71);src(73,first=2);src(76,first=1)
red('The full paper will provide the complete iterative workflow diagram and extraction setup, including resistance, self-inductance, mutual coupling, and network boundaries.')
src(77);src(78,first=2);src(79,first=2)
fig(80,11)
src(82,first=1)
fig(83,11)
page()
# Page 5: preserve the remaining subsection titles and defer detail explicitly.
src(85);src(86,first=1)
text('With the extracted DPT gate network, increasing turn-on resistance from 2.5 Ω to 3.5 Ω reduces peak drain–source voltage from approximately 105 V to 93 V, while mean turn-on energy per transistor increases from approximately 24 µJ to 31 µJ.')

red('The full paper will provide the drain-voltage and gate-voltage waveforms, complete simulation comparison table, and corresponding switching-energy assessment.')
src(94);src(95,first=2)
src(97);src(98)
red('The full paper will provide the planned experimental DPT correlation of voltage overshoot, gate disturbance, current sharing, and switching energy. Experimental results are not available in this manuscript.')
src(102)
red('The full paper will discuss winding and system integration, submodule balancing, auxiliary-power overhead, common-mode behavior, and the insulation boundary of the selected driver.')
src(105);src(107,last=2)
src(108)
# Reuse the audited 10-entry reference list from the citation-checked digest.
refdoc=Document(P/'SPB_ICPE_digest_expanded_citation_checked_2026-10-29.docx')
for q in refdoc.paragraphs:
 if re.match(r'^\[\d+\]',q.text):
  z=deepcopy(q._p);body.insert(len(body)-1,z)
  from docx.text.paragraph import Paragraph
  pp=Paragraph(z,doc._body);pp.paragraph_format.space_after=Pt(0)
# Correct cross-references after omitting selected figures and the requirements table.
fmap={1:1,5:2,7:3,8:4,9:5};refmap={1:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8,10:9,11:10}
for q in doc.paragraphs:
 is_ref=bool(re.match(r'^\[\d+\]',q.text))
 if is_ref:continue
 for r in q.runs:
  old=r.text
  if not old:continue
  t=old.replace('[2], [3]','[3]')
  t=re.sub(r'\[(\d+)\]',lambda m:'['+str(refmap[int(m.group(1))])+']' if int(m.group(1)) in refmap else m.group(0),t)
  t=re.sub(r'Fig\. (\d+)',lambda m:'Fig. '+str(fmap.get(int(m.group(1)),int(m.group(1)))),t)
  t=t.replace('Table II','Table I').replace('TABLE II','TABLE I')
  if t!=old:r.text=t
# Keep body and captions at the explicit 10 pt venue minimum.
for q in doc.paragraphs:
 if q.style.name=='Caption':
  for r in q.runs:r.font.size=Pt(10)
# Reapply typographic subscripts to new prose only, without changing native equations or drawings.
symbols={'Coss,Q':('C','oss,Q'),'RDS(on)':('R','DS(on)'),'Qoss':('Q','oss'),'Vtest':('V','test'),'Vdc':('V','dc'),'Vm':('V','m'),'Iph,rms':('I','ph,rms'),'fsw':('f','sw')}
pat=re.compile(r'(?<![A-Za-z])('+'|'.join(re.escape(k) for k in sorted(symbols,key=len,reverse=True))+r')(?![A-Za-z])')
for q in doc.paragraphs:
 if q._p.xpath('.//m:oMath | .//w:drawing') or re.match(r'^\[\d+\]',q.text):continue
 for rr in list(q.runs):
  st=rr.text
  if not pat.search(st):continue
  base=deepcopy(rr._r.rPr) if rr._r.rPr is not None else None;pos=0;chunks=[]
  for m in pat.finditer(st):chunks.extend([(st[pos:m.start()],False,False),(symbols[m.group()][0],False,True),(symbols[m.group()][1],True,False)]);pos=m.end()
  chunks.append((st[pos:],False,False))
  for val,isub,ital in chunks:
   if not val:continue
   r=OxmlElement('w:r')
   if base is not None:r.append(deepcopy(base))
   rp=r.find(qn('w:rPr'))
   if rp is None:rp=OxmlElement('w:rPr');r.append(rp)
   if isub:z=OxmlElement('w:vertAlign');z.set(qn('w:val'),'subscript');rp.append(z)
   if ital:rp.append(OxmlElement('w:i'))
   z=OxmlElement('w:t');z.set(qn('xml:space'),'preserve');z.text=val;r.append(z);rr._r.addprevious(r)
  rr._r.getparent().remove(rr._r)
for q in doc.paragraphs:
 q.paragraph_format.line_spacing=1
 q.paragraph_format.space_after=Pt(0)
 if q.style.name.startswith('Heading'):q.paragraph_format.space_before=Pt(2)
# Document the preservation and omission choices for comparison with the full manuscript.
(QA/'selection_map.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(QA/'artifact.md').write_text(f'Original-structure digest. Source: {SRC}; SHA256 {hashlib.sha256(SRC.read_bytes()).hexdigest()}. All original section and subsection headings retained. Selected source paragraphs/sentences and native equations copied; original images scaled, not redesigned. Red notes replace omitted detail. Requirements table and figures 2, 3, 4, 6, 9 deferred. Remaining figures and table renumbered. A4, 3 cm top and 2.5 cm other margins, 10 pt body/captions. Citation balance from audited digest: 2/10 self-citations (20 percent), or 2/8 scholarly works (25 percent). Page QA uses Word and Poppler; LibreOffice unavailable.',encoding='utf-8')
doc.core_properties.subject='Five-page digest preserving full-manuscript structure with red full-paper deferrals';doc.save(OUT)
print(OUT);print('Words',sum(len(q.text.split()) for q in doc.paragraphs),'Images',len(doc.inline_shapes),'Headings',sum(q.style.name.startswith('Heading') for q in doc.paragraphs))



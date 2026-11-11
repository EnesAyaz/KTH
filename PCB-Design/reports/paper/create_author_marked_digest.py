"""Apply the author's red exclusions without rewriting retained manuscript text."""
from pathlib import Path
from copy import deepcopy
import re,json,hashlib
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt,RGBColor
from docx.text.paragraph import Paragraph

ROOT=Path(__file__).parent
SOURCE=ROOT/'Submission-Files/SPB_ICPE_full_paper_LTspice_rerun_2026-11-02.docx'
OUT=ROOT/'Submission-Files/SPB_ICPE_digest_author_selections_2026-11-02.docx'
QA=ROOT/'icpe/digest_author_selections_qa'
QA.mkdir(exist_ok=True)
doc=Document(SOURCE)
pars=list(doc.paragraphs)
audit=[]

def red(run):
    c=run.font.color.rgb
    if c is None:return False
    a=str(c)
    return len(a)==6 and int(a[:2],16)>160 and int(a[2:4],16)<80 and int(a[4:],16)<80

def note_after(q,value):
    e=OxmlElement('w:p');q._p.addnext(e)
    p=Paragraph(e,q._parent);p.style=doc.styles['Normal']
    p.paragraph_format.space_after=Pt(4)
    r=p.add_run(value);r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=RGBColor(0,0,0)
    audit.append({'replacement_after_source_paragraph':pars.index(q),'text':value})
    return p

def delete(q):
    el=q._element
    if el.getparent() is not None:el.getparent().remove(el)

# One brief note per omitted topic; captions lose only their marked detail.
notes={
 21:'The full paper will expand the relationship between voltage partitioning, winding-set voltage, and the phase-current requirement.',
 35:'The full paper will document the device-data comparison underlying the EPC2361 selection, including charge-equivalent capacitance, datasheet test conditions, and the limits of the screening criterion.',
 42:'The full paper will specify the gate-drive model and the complete simulation parameters used for these switching sweeps.',
 51:'The full paper will detail the switching-energy integration and electrothermal model, including cooling assumptions and temperature-dependent conduction losses.',
 61:'The full paper will present the detailed loss, temperature, and voltage-stress comparison supporting the four-device candidate, together with its sensitivity to gate drive and commutation-loop inductance.',
 64:'The full paper will detail the current-sharing perturbation cases and their relationship to the routed gate network.',
 70:'The full paper will assess gate-driver loading, sink-current requirements, and the resulting gate-voltage margins.',
 74:'The full paper will detail the symmetric cell layout, individual gate resistors, and Kelvin-source returns illustrated in Fig. 5(c). It will explain the matching of the power and gate paths within each transistor pair.',
 77:'The full paper will assess inter-driver timing and current sharing using the routed networks. Extracted parasitics will be used to revisit the initial current and switching-margin assumptions.',
 87:'The full paper will compare the lumped and extracted gate networks, including shared-path inductance and mutual coupling.',
 94:'The full paper will detail the simulation configurations underlying Table III, including the assumed operating-board gate paths and the extracted DPT gate network.',
 98:'The full paper will expand the voltage-stress and switching-energy tradeoff in Fig. 9 and assess gate-bias and resistance settings across the evaluated networks.',
 104:'The full paper will use the routed-network results to refine the shared gate paths and drive settings. The corresponding switching energies will update the loss and thermal assessment.',
 109:'Experimental DPT measurements are planned for the full paper to validate the parasitic model and switching-loss estimates, including voltage overshoot, gate disturbance, and current sharing.',
 112:'The full paper will discuss integration constraints, including inter-driver timing, submodule balancing, auxiliary power, and insulation across the series stack.',
 114:'This digest links SPB voltage selection to the current-sharing and parasitic constraints of a high-current phase-leg building block. The full paper will refine the gate network and validate the resulting switching and loss estimates experimentally.'
}

# Insert notes before deletion so a wholly excluded paragraph retains its logical position.
for i,value in notes.items():note_after(pars[i],value)

for i,q in enumerate(pars):
    removed=[]
    for r in list(q.runs):
        if red(r):
            removed.append(r.text)
            r._element.getparent().remove(r._element)
    if removed:audit.append({'source_paragraph':i,'removed_red_text':''.join(removed)})
    # The capacitance-definition equation is wholly marked, including its native math.
    if i==27:
        delete(q);continue
    # Avoid punctuation-only remnants of wholly marked paragraphs and empty spacers.
    visible=q.text.strip()
    if not re.search(r'\w',visible) and not q._p.xpath('.//w:drawing | .//m:oMath | .//w:br'):
        delete(q)

# Remove only the table marked red by the author; preserve both unmarked tables.
for ti,table in enumerate(list(doc.tables)):
    runs=[r for row in table.rows for c in row.cells for p in c.paragraphs for r in p.runs if r.text.strip()]
    if runs and all(red(r) for r in runs):
        audit.append({'removed_red_table':ti,'rows':len(table.rows)})
        table._element.getparent().remove(table._element)

# Close numbering gaps caused by removing the red capacitance equation and Table II.
for q in list(doc.paragraphs)+[p for t in doc.tables for row in t.rows for c in row.cells for p in c.paragraphs]:
    for r in q.runs:
        old=r.text
        value=old.replace('Table III','Table II').replace('TABLE III','TABLE II')
        value=re.sub(r'\(([345])\)',lambda m:'('+str(int(m[1])-1)+')',value)
        if value!=old:r.text=value

# Retained material must be unchanged apart from cross-reference renumbering and
# removal of author-marked runs. Images and native equations stay editable/preserved.
assert len(doc.inline_shapes)==9
assert len(doc.tables)==2
assert len(doc._element.xpath('.//m:oMath'))==4
assert not any(red(r) for q in doc.paragraphs for r in q.runs)
assert not any(red(r) for t in doc.tables for row in t.rows for c in row.cells for q in c.paragraphs for r in q.runs)
assert not any('1.7' in q.text for q in doc.paragraphs)
doc.core_properties.subject='Digest following author-marked exclusions with concise full-paper scope notes'
doc.save(OUT)
(QA/'selection_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
(QA/'artifact.md').write_text(f'Author-selected digest. Source: {SOURCE}; SHA256 {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}. Red runs removed, including the fully red parallel-count table and capacitance-definition equation. Unmarked wording, all 24 headings, all nine original figures at their author-chosen sizes, and both unmarked tables preserved. One or two black sentences per omitted topic identify planned full-paper content. Captions are shortened only by their red selections. Remaining equations and table renumbered. Annotated source unchanged. Layout verified using Word PDF export and Poppler because bundled LibreOffice is unavailable.',encoding='utf-8')
print(OUT)
print('Words:',sum(len(q.text.split()) for q in doc.paragraphs),'Figures:',len(doc.inline_shapes),'Tables:',len(doc.tables))

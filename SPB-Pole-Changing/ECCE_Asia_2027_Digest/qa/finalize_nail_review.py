from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from docx import Document
from docx.shared import Cm
from copy import deepcopy
root=Path.cwd();ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(root/'archive/previous_word_documents/ECCE_Asia_2027_Digest_Numbered_EquationsNail.docx') as z:
 d=E.fromstring(z.read('word/document.xml'))
 for x in d.xpath('//w:del',namespaces=ns):x.getparent().remove(x)
 for x in d.xpath('//w:ins',namespaces=ns):
  par=x.getparent();idx=par.index(x)
  for child in list(x):par.insert(idx,child);idx+=1
  par.remove(x)
 reviewed=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in d.xpath('//w:body/w:p',namespaces=ns)]
doc=Document(root/'archive/previous_word_documents/ECCE_Asia_2027_Digest_Numbered_Equations.docx')
def replace(p,text):
 rpr=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
 for x in list(p._p):
  if E.QName(x).localname!='pPr':p._p.remove(x)
 r=p.add_run(text)
 if rpr is not None:r._r.insert(0,rpr)
replace(doc.paragraphs[0],'Codesign of GaN SPB Cells and Pole-Changing Windings for Propulsion')
abstract=reviewed[1].replace('high-voltage truck propulsion','high-voltage propulsion').replace('device–winding co-design','drive–machine co-design').replace('Discrete GaN voltage ratings, cell-voltage stress, coil allocation, three-phase balance, and pole ratio are treated as coupled constraints.','The method matches discrete GaN voltage ratings to calculated switch stress while enforcing coil allocation, three-phase balance, and pole-ratio constraints.').replace('a balanced winding factor of  in both','balanced winding factors in both').replace('of hybrid excited interior permanent magnet machine','of a hybrid-excited interior permanent-magnet (HE-IPM) machine')
replace(doc.paragraphs[1],abstract)
for p in doc.paragraphs:
 t=p.text
 if t.startswith('Index Terms—'):replace(p,t.replace('Electric truck propulsion','Electric propulsion'))
 if t.startswith('Megawatt-level'):
  replace(p,t.replace('two-level truck propulsion inverter','two-level voltage-source truck propulsion inverter'))
 if t.startswith('Multilevel inverters'):
  match=next(x for x in reviewed if x.startswith('Multilevel inverters'))
  replace(p,match.replace('Three , five , and seven-level','Three-, five-, and seven-level'))
 if t.startswith('Pole changing can exploit'):
  # Retain the reviewed deletion of the cycle-savings aside; qualify the added topology-dependent observation.
  match=next(x for x in reviewed if x.startswith('Pole changing can exploit'))
  match=match.replace('However, such machines are driven by multiple units, only some of which operate over the full duty cycle.','In some multiple-inverter arrangements, only a subset of units operates over the full duty cycle.')
  replace(p,match.strip())
 if t.startswith('Let the device rating be'):
  replace(p,'The device rating Vr is the specified voltage limit; switch stress is the calculated requirement including imbalance and overshoot. With allowed utilization u and multipliers kimb and kov, the stress estimate and voltage-driven cell-count bound are')
table=doc.tables[1]
for row in table.rows:
 for idx in [3,1]:row._tr.remove(row.cells[idx]._tc)
for idx in [3,1]:table._tbl.tblGrid.remove(table._tbl.tblGrid.gridCol_lst[idx])
for row in table.rows:
 for cell in row.cells:cell.width=Cm(6.4)
for p in doc.paragraphs:
 if 'DIRECT COIL-SIDE FOURIER CHECK' in p.text:replace(p,'TABLE II\nWINDING FACTORS FOR THE 36-SLOT CONSTRUCTION')
doc.save(root/'ECCE_Asia_2027_Digest_Final.docx')
print('Created final digest; native equations:',len(doc._element.xpath('//m:oMath')))

from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import hashlib,json

ROOT=Path.cwd();P=ROOT/'reports/paper';S=P/'Submission-Final/ICPE_Template.docx';OUT=P/'Submission-Final/ICPE_Digest_vector_figures_2026-11-07.docx';A=P/'icpe/vector_quality_2026-11-07';A.mkdir(parents=True,exist_ok=True)
paths=['latest_digest_figures/fig01_topology.svg','latest_digest_figures/fig02_devices.svg','revised_blue_2026-11-06/fig03_complete_switching_maps.svg','revised_blue_2026-11-06/fig04_sizing_remeasured.svg','source_label_ai_ack_2026-11-06/fig05_source_terminal_corrected.svg','minimal_original_revision_2026-11-06/fig06_compact.svg','prototype_board_update_2026-11-05/prototype_layout_q3d.svg','revised_blue_2026-11-06/fig08_routed_margin_map.svg']
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
asvg='http://schemas.microsoft.com/office/drawing/2016/SVG/main';relsns='http://schemas.openxmlformats.org/package/2006/relationships';ctns='http://schemas.openxmlformats.org/package/2006/content-types';w14='http://schemas.microsoft.com/office/word/2010/wordml'
with ZipFile(S) as z:files={n:z.read(n) for n in z.namelist()}
sourcehash=hashlib.sha256(S.read_bytes()).hexdigest();d=E.fromstring(files['word/document.xml']);rels=E.fromstring(files['word/_rels/document.xml.rels']);settings=E.fromstring(files['word/settings.xml']);cts=E.fromstring(files['[Content_Types].xml'])
before=E.tostring(d);drawings=d.findall('.//w:drawing',ns);assert len(drawings)==8
if not any(x.get('Extension')=='svg' for x in cts):E.SubElement(cts,'{'+ctns+'}Default',Extension='svg',ContentType='image/svg+xml')
manifest=[]
for i,(drawing,p) in enumerate(zip(drawings,paths),1):
 svgpath=P/'icpe'/p;svg=E.fromstring(svgpath.read_bytes());ext=drawing.find('.//wp:extent',ns);blip=drawing.find('.//a:blip',ns)
 # Retain the user's exact on-page geometry, including any intentional stretching.
 svg.set('width',str(int(ext.get('cx'))/914400)+'in');svg.set('height',str(int(ext.get('cy'))/914400)+'in');svg.set('preserveAspectRatio','none')
 for image in svg.findall('.//{http://www.w3.org/2000/svg}image'):
  if image.get('href') is not None:image.set('{http://www.w3.org/1999/xlink}href',image.get('href'));image.attrib.pop('href',None)
 name=f'word/media/vector_quality_{i}.svg';files[name]=E.tostring(svg,xml_declaration=True,encoding='UTF-8')
 rid=f'rIdVectorQuality{i}';assert not any(x.get('Id')==rid for x in rels)
 E.SubElement(rels,'{'+relsns+'}Relationship',Id=rid,Type=ns['r']+'/image',Target=f'media/vector_quality_{i}.svg')
 el=blip.find('a:extLst',ns)
 if el is None:el=E.SubElement(blip,'{'+ns['a']+'}extLst')
 for prior in list(el):
  if prior.get('uri')=='{96DAC541-7B7A-43D3-8B79-37D633B846F1}':el.remove(prior)
 extSVG=E.SubElement(el,'{'+ns['a']+'}ext',uri='{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
 node=E.SubElement(extSVG,'{'+asvg+'}svgBlip',nsmap={'asvg':asvg});node.set('{'+ns['r']+'}embed',rid)
 manifest.append({'figure':i,'svg_source':str(svgpath),'width_in':int(ext.get('cx'))/914400,'height_in':int(ext.get('cy'))/914400})
# Improve the compatibility fallback for the one previously compressed figure.
files['word/media/image1.png']=(P/'icpe/latest_digest_figures/fig01_topology.png').read_bytes()
for tag in ['doNotAutoCompressPictures']:
 nodes=settings.findall('{'+ns['w']+'}'+tag)
 for n in nodes:settings.remove(n)
 E.SubElement(settings,'{'+ns['w']+'}'+tag)
for node in settings.findall('{'+w14+'}defaultImageDpi'):settings.remove(node)
node=E.SubElement(settings,'{'+w14+'}defaultImageDpi');node.set('{'+w14+'}val','600')
for name,root in [('word/document.xml',d),('word/_rels/document.xml.rels',rels),('word/settings.xml',settings),('[Content_Types].xml',cts)]:files[name]=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for name,data in files.items():z.writestr(name,data)
# Verify that the document edit is limited to the SVG alternatives in drawing nodes.
after=E.fromstring(files['word/document.xml'])
for drawing in after.findall('.//w:drawing',ns):
 blip=drawing.find('.//a:blip',ns);el=blip.find('a:extLst',ns)
 for x in list(el):
  if x.get('uri')=='{96DAC541-7B7A-43D3-8B79-37D633B846F1}':el.remove(x)
 if len(el)==0:blip.remove(el)
assert E.tostring(after)==before,'Unexpected text/layout edit'
assert hashlib.sha256(S.read_bytes()).hexdigest()==sourcehash
(A/'manifest.json').write_text(json.dumps({'source_sha256':sourcehash,'output':str(OUT),'figures':manifest,'verification':'Body XML unchanged except SVG alternatives; original Word file unchanged.'},indent=2))
print(OUT)

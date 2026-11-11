from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'build_digest.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace("R=json.loads((ROOT/'simulation/results/simplified_screen.json').read_text())","R=json.loads((ROOT/'simulation/results_three_phase/three_phase_codesign.json').read_text())")
start=s.index('# PAGE ONE');end=s.index('# Final controls')
s=s[:start]+(root/'paper_body_three_phase.txt').read_text(encoding='utf-8-sig')+'\n'+s[end:]
# Replace old study equations with native Word math for the new study.
start=s.index('def eq(text,num):');end=s.index('\ndef fig(',start)
s=s[:start]+'''def eq(text,num):
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 math=OxmlElement('m:oMath')
 def mr(txt,normal=False):
  r=OxmlElement('m:r')
  if normal:
   pr=OxmlElement('m:rPr');normalel=OxmlElement('m:nor');pr.append(normalel);r.append(pr)
  t=OxmlElement('m:t');t.text=txt;r.append(t);return r
 def sb(base,idx):
  el=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));el.append(e);ss=OxmlElement('m:sub');ss.append(mr(idx));el.append(ss);return el
 if num==1:
  math.append(mr('Q = lcm(3N, 3'));math.append(sb('p','L'));math.append(mr('),   c = Q/(3N)'))
 else:
  math.append(mr('T = (3N/2)p['));math.append(sb('ψ','f'));math.append(mr(' + ('));math.append(sb('L','d'));math.append(mr(' − '));math.append(sb('L','q'));math.append(mr(')'));math.append(sb('I','d'));math.append(mr(']'));math.append(sb('I','q'));math.append(mr(',   P = T'));math.append(sb('ω','m'))
 x._p.append(math);r=x.add_run('    ('+str(num)+')');r.font.name='Times New Roman';r.font.size=Pt(11)
 return x
''' +s[end:]
s=s.replace("'expected_pages':5","'expected_pages':5,'study':'three_wire_cell_count_and_pole_ratio'")
p.write_text(s,encoding='utf-8')

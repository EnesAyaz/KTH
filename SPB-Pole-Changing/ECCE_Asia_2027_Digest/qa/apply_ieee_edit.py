from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=root/'build_digest.py';s=p.read_text(encoding='utf-8')
start=s.index('# PAGE ONE');end=s.index('# Final controls',start)
s=s[:start]+(root/'qa/ieee_manuscript_body.txt').read_text(encoding='utf-8-sig')+'\n'+s[end:]
s=s.replace("D.core_properties.title='Selecting Stacked Three Phase Cells and Pole Ratios for Traction Drives'","D.core_properties.title='Co-Design of GaN Stacked Polyphase Bridges and Pole-Changing Traction Machines'")
# Center table captions and retain the official document paragraph roles.
s=s.replace("if style=='Text':x.paragraph_format.first_line_indent", "if style=='Caption':x.alignment=WD_ALIGN_PARAGRAPH.CENTER\n if style=='Text':x.paragraph_format.first_line_indent")
# IEEE-style tables: no shaded cells or vertical rules. These are documented
# intentional changes requested for a conference manuscript presentation.
s=s.replace("e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)","e.set(qn('w:val'),'nil');b.append(e)")
s=s.replace("sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EEEEEE');pr.append(sh)","pass")
s=s.replace("pr.append(b)\n   if ri==0:","\n   for edge in (['top','bottom'] if ri==0 else ['bottom'] if ri==len(t.rows)-1 else []):\n    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'5' if ri==0 else '4');e.set(qn('w:color'),'000000');b.append(e)\n   pr.append(b)\n   if ri==0:")
start=s.index('def eq(text,num):');end=s.index('\ndef fig(',start)
s=s[:start]+'''def eq(text,num):
 def mr(txt,normal=False):
  r=OxmlElement('m:r')
  if normal:
   pr=OxmlElement('m:rPr');normalel=OxmlElement('m:nor');pr.append(normalel);r.append(pr)
  t=OxmlElement('m:t');t.text=txt;r.append(t);return r
 def sb(base,idx):
  el=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));el.append(e);ss=OxmlElement('m:sub');ss.append(mr(idx));el.append(ss);return el
 def frac(numerator,denominator):
  f=OxmlElement('m:f');nu=OxmlElement('m:num');de=OxmlElement('m:den')
  for obj in numerator:nu.append(obj)
  for obj in denominator:de.append(obj)
  f.append(nu);f.append(de);return f
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 math=OxmlElement('m:oMath')
 if num==1:
  for k,ph in enumerate('abc'):
   if k:math.append(mr(' + '))
   math.append(sb('i',ph+',j'))
  math.append(mr(' = 0'))
 elif num==2:
  math.append(sb('N','V'));math.append(mr(' = ⌈'));math.append(frac([sb('V','dc,max'),sb('k','imb'),sb('k','ov')],[mr('u'),sb('V','r')]));math.append(mr('⌉'))
 elif num==3:
  math.append(mr('a, b ∉ 3ℤ;   Q/(3g) ∈ ℕ;   Q/(3N) ∈ ℕ'))
 elif num==4:
  math.append(sb('k','p,ν'));math.append(mr(' = |sin('));math.append(frac([mr('πνy')],[mr('Q')]));math.append(mr(')|'))
 else:
  math.append(sb('T','e'));math.append(mr(' = '));math.append(frac([mr('3N')],[mr('2')]));math.append(mr('p['));math.append(sb('ψ','f'));math.append(mr(' + ('));math.append(sb('L','d'));math.append(mr(' − '));math.append(sb('L','q'));math.append(mr(')'));math.append(sb('i','d'));math.append(mr(']'));math.append(sb('i','q'))
 x._p.append(math);rr=x.add_run('    ('+str(num)+')');rr.font.name='Times New Roman';rr.font.size=Pt(11)
 return x
''' +s[end:]
s=s.replace("'study':'discrete_device_slot_and_ratio_selection'","'study':'ieee_device_winding_codesign'")
p.write_text(s,encoding='utf-8')

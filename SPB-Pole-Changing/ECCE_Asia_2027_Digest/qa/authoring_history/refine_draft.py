from pathlib import Path
p=Path(__file__).resolve().parent/'build_digest.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("sect=deepcopy(D.sections[-1]._sectPr)","sect=deepcopy(D.sections[-1]._sectPr)\nsect.insert(0,deepcopy(D.sections[0]._sectPr.find(qn('w:footerReference'))))")
s=s.replace("def h(text):\n x=", "sub_counter=0\ndef h(text):\n global sub_counter\n sub_counter=0\n x=")
s=s.replace("def sub(text):\n x=p(text,'Heading 2',11,True)","def sub(text):\n global sub_counter\n label=chr(65+sub_counter); sub_counter+=1\n x=p(label+'. '+text,'Heading 2',11,True)\n np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);x._p.get_or_add_pPr().append(np)")
start=s.index('def eq(text,num):')
end=s.index('\ndef fig(',start)
s=s[:start]+'''def eq(text,num):
 def mr(txt,normal=False):
  r=OxmlElement('m:r')
  if normal:
   pr=OxmlElement('m:rPr');norm=OxmlElement('m:nor');pr.append(norm);r.append(pr)
  t=OxmlElement('m:t');t.text=txt;r.append(t);return r
 def sub(base,idx):
  v=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));v.append(e);ss=OxmlElement('m:sub');ss.append(mr(idx));v.append(ss);return v
 def sup(obj,power):
  v=OxmlElement('m:sSup');e=OxmlElement('m:e');e.append(obj if not isinstance(obj,str) else mr(obj));v.append(e);ss=OxmlElement('m:sup');ss.append(mr(power));v.append(ss);return v
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 math=OxmlElement('m:oMath')
 if num==1:
  math.append(sub('S','r'));math.append(mr(' = '))
  n=OxmlElement('m:nary');pr=OxmlElement('m:naryPr');ch=OxmlElement('m:chr');ch.set(qn('m:val'),'∑');pr.append(ch);loc=OxmlElement('m:limLoc');loc.set(qn('m:val'),'undOvr');pr.append(loc);n.append(pr)
  for tag,txt in [('sub','k = 0'),('sup','m − 1'),('e','exp(j2πrk/m)')]:
   el=OxmlElement('m:'+tag);el.append(mr(txt));n.append(el)
  math.append(n);math.append(mr(' = 0'));math.append(mr('  if m does not divide r',True))
 else:
  math.append(sub('C','min'));math.append(mr(' = '));f=OxmlElement('m:f');nu=OxmlElement('m:num');nu.append(mr('2ΔE'));f.append(nu);de=OxmlElement('m:den');de.append(sup(sub('V','0'),'2'));de.append(mr(' − '));de.append(sup('(0.9V₀)','2'));f.append(de);math.append(f)
 x._p.append(math);r=x.add_run('    ('+str(num)+')');r.font.name='Times New Roman';r.font.size=Pt(11)
 return x
''' + s[end:]
s=s.replace('81.22 V','81.21 V').replace('the requested 4/2- and 6/2-pole candidates','the 4/2- and 6/2-pole candidates').replace('alongside the requested designs','alongside the other candidates')
s=s.replace("table(['Case','m','Poles'", "cap=p('TABLE I  Ideal phase power and buffer sizing','Caption',10);cap.paragraph_format.keep_with_next=True\ntable(['Case','m','Poles'")
s=s.replace("table(['Case','Q','Short y'", "cap=p('TABLE II  Discrete coil pitch comparison','Caption',10);cap.paragraph_format.keep_with_next=True\ntable(['Case','Q','Short y'")
s=s.replace("p('The unit pitch factor", "p('The unit pitch factor")
p.write_text(s,encoding='utf-8')
# Ensure the invalid-energy case is not reported as a physically realized 0 V.
p=Path(__file__).resolve().parent/'simulation/run_simplified_screen.py'
s=p.read_text(encoding='utf-8-sig').replace("'min_V':float(vv.min())","'min_V':float(vv.min()) if v2.min()>0 else None")
p.write_text(s,encoding='utf-8')

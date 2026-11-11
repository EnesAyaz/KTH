"""Native editable OMML equations, numbered and aligned for the digest."""
from docx.oxml import OxmlElement as E
from docx.oxml.ns import qn
from docx.shared import Pt,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_TAB_ALIGNMENT

def run(text,normal=False):
 r=E('m:r')
 if normal:
  pr=E('m:rPr');pr.append(E('m:nor'));r.append(pr)
 pr=E('w:rPr');sz=E('w:sz');sz.set(qn('w:val'),'20');pr.append(sz);r.append(pr)
 t=E('m:t');t.text=text;r.append(t);return r
def put(parent,values):
 if not isinstance(values,(list,tuple)):values=[values]
 for value in values:parent.append(run(value) if isinstance(value,str) else value)
 return parent
def sub(base,index):
 x=E('m:sSub');x.append(put(E('m:e'),base));x.append(put(E('m:sub'),index));return x
def sup(base,power):
 x=E('m:sSup');x.append(put(E('m:e'),base));x.append(put(E('m:sup'),power));return x
def frac(top,bottom):
 x=E('m:f');x.append(put(E('m:num'),top));x.append(put(E('m:den'),bottom));return x
def delim(values,left='(',right=')'):
 x=E('m:d');pr=E('m:dPr')
 for name,val in [('begChr',left),('endChr',right)]:
  e=E('m:'+name);e.set(qn('m:val'),val);pr.append(e)
 x.append(pr);x.append(put(E('m:e'),values));return x
def absolute(values):return delim(values,'|','|')
def summation(values):
 x=E('m:nary');pr=E('m:naryPr')
 for name,val in [('chr','∑'),('limLoc','subSup')]:
  e=E('m:'+name);e.set(qn('m:val'),val);pr.append(e)
 x.append(pr);x.append(put(E('m:sub'),'s = 1'));x.append(put(E('m:sup'),'Q'));x.append(put(E('m:e'),values));return x
def equations(number):
 ph=lambda idx:sub('p',idx)
 P=lambda idx:sub('P',idx)
 V=lambda idx:sub('V',idx)
 theta=lambda idx:sub('θ',idx)
 G=lambda idx:sub('G',idx)
 if number==1:return [[V('c,j'),' = ',frac(V('dc'),'N'),',     ',sub('i','a,j'),' + ',sub('i','b,j'),' + ',sub('i','c,j'),' = 0']]
 if number==2:
  stress=[V('dc,max'),sub('k','imb'),sub('k','ov')]
  return [[V('stress'),' = ',frac(stress,'N'),',     ',sub('N','V'),' = ',delim(frac([V('dc,max'),sub('k','imb'),sub('k','ov')],['u',V('r')]),'⌈','⌉')]]
 if number==3:return [['C = Q ',run('(double layer)',True),';   C = ',frac('Q','2'),' ',run('(single layer)',True),';   c = ',frac('C','3N'),' ∈ ℕ;   3N ≤ C']]
 if number==4:return [[ph('H'),' = ',frac(P('H'),'2'),',   ',ph('L'),' = ',frac(P('L'),'2'),',   g = ',run('gcd',True),delim([ph('H'),', ',ph('L')]),',   a = ',frac(ph('H'),'g'),',   b = ',frac(ph('L'),'g')]]
 if number==5:return [['Δθ = ',frac('2π','3g'),',   a,b ∉ 3ℤ,   d = ',frac('Q','3g'),' ∈ ℕ,   c = ',frac('Q','3N'),' ∈ ℕ']]
 if number==6:return [['s = 1 + q + 3dt + kd,     r(s) = 1 + [(s − 1 + y) ',run('mod',True),' Q]'],['j = 1 + ',delim(frac('gq + t','c'),'⌊','⌋'),';   q = 0,…,d − 1;   t = 0,…,g − 1;   k = 0,1,2']]
 if number==7:return [[sub('τ','H'),' = ',frac('Q',P('H')),',   ρ = ',frac('y',sub('τ','H')),',   ',sub('k','p,ν'),' = ',absolute([run('sin',True),delim(frac('πνy','Q'))]),',   η = ',run('min',True),delim([sub('k','p,H'),', ',sub('k','p,L')])]]
 if number==8:return [[theta('s'),' = ',frac('2π(s − 1)','Q'),',   ',theta('r(s)'),' = ',frac('2π[r(s) − 1]','Q'),',   ',sub('I','s'),' = ',sup('e',['ip',theta('s')])]]
 if number==9:return [[G('ν'),' = ',frac('1','2Q'),summation([sub('I','s'),delim([sup('e',['−iν',theta('s')]),' − ',sup('e',['−iν',theta('r(s)')])],'[',']')])]]
 if number==10:return [[sub('k','w,p'),' = ',absolute(G('p')),',     ',sub('ε','p'),' = ',frac([run('max',True),delim([absolute(G('p′')),', ',absolute(G('−p′'))])],absolute(G('p'))),' ≤ ',sup('10','−8')]]
 if number==11:return [[sub('R','ind'),' = N',sub('R','DS(on)')]]
 if number==12:return [['P = ',sub('T','e'),sub('ω','m')]]
 raise ValueError(number)

def add_equation(document,number):
 p=document.add_paragraph();pf=p.paragraph_format
 pf.alignment=WD_ALIGN_PARAGRAPH.LEFT;pf.first_line_indent=Cm(0);pf.left_indent=Cm(0);pf.right_indent=Cm(0)
 pf.space_before=Pt(1);pf.space_after=Pt(3);pf.line_spacing=1.0;pf.keep_together=True
 pf.tab_stops.add_tab_stop(Cm(7.9),WD_TAB_ALIGNMENT.CENTER);pf.tab_stops.add_tab_stop(Cm(15.8),WD_TAB_ALIGNMENT.RIGHT)
 p.add_run('\t');math=E('m:oMath');rows=equations(number)
 if len(rows)==1:put(math,rows[0])
 else:
  arr=E('m:eqArr')
  for row in rows:arr.append(put(E('m:e'),row))
  math.append(arr)
 p._p.append(math);r=p.add_run('\t('+str(number)+')');r.font.name='Times New Roman';r.font.size=Pt(10)
 return p

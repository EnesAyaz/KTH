from pathlib import Path
import re
root=Path(r'C:/Github/KTH/PCB-Design/simulation')
src=root/'models/ti-lmg1210/original/LMG1210_PSPICE_TRANS/LMG1210_TRANS.lib'
lines=[]
last_statement=None
for line in src.read_text(encoding='cp1252').splitlines():
    if line.startswith('+'):
        assert last_statement is not None
        lines[last_statement]+=' '+line[1:].strip()
    else:
        lines.append(line)
        if line.strip() and not line.lstrip().startswith('*'):last_statement=len(lines)-1
count=0
for i,line in enumerate(lines):
    if re.match(r'^[EG]',line,re.I) and re.search(r'\bVALUE\s*\{',line,re.I):
        start=re.search(r'\bVALUE\s*',line,re.I).end()
        expr=line[start:].strip()
        if expr.startswith('{') and expr.endswith('}'):
            lines[i]=line[:start]+'{'+expr.replace('{','').replace('}','')+'}'
            count+=1
    if not lines[i].startswith('*'):lines[i]=lines[i].replace('*$','')
out=root/'models/ti-lmg1210/LMG1210_LTspice.lib'
out.write_text('* Local syntax adaptation; not a TI-qualified LTspice release\n'+'\n'.join(lines)+'\n',encoding='cp1252')
text=(root/'lmg1210-original-smoke.cir').read_text().replace('models/ti-lmg1210/original/LMG1210_PSPICE_TRANS/LMG1210_TRANS.lib','models/ti-lmg1210/LMG1210_LTspice.lib')
text=text.replace('original TI model','adapted TI model')
(root/'lmg1210-adapted-smoke.cir').write_text(text)
print('Normalized behavioral VALUE expressions:',count)

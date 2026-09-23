"""Finish the saved gate-resistance report after the active grid search exits."""
from pathlib import Path
import json,subprocess,sys,time,csv
BASE=Path(__file__).resolve().parent
ROOT=BASE/'dut_gate_search'
if __name__=='__main__':
 while not (ROOT/'provenance.json').exists():time.sleep(10)
 # Refresh interrupted results from cache and retry failures with the longer timeout.
 for script in ('search_gate_limits.py','check_gate_search.py','build_gate_report.py'):
  print('FINALIZE',script,flush=True)
  subprocess.run([sys.executable,str(BASE/script)],cwd=BASE,check=True)
 cells=json.loads((ROOT/'summary.json').read_text());rows=[]
 for c in sorted(cells,key=lambda c:(c['L_nH'],c['current_A'])):
  r=c['selected'];peak=max(c[k]['peak_V'] for k in ('selected','fine','finest')) if r else None
  rows.append(dict(layout_nH=c['L_nH'],nominal_current_A=c['current_A'],Ron_ohm=r['Ron'] if r else '',Roff_ohm=r['Roff'] if r else '',worst_checked_DUT_peak_V=peak if r else '',margin_to_100V=100-peak if r else '',status='three-step pass' if r else 'no verified pair',unresolved_runs=c['unresolved_runs']))
 with (ROOT/'selected_settings.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 from pypdf import PdfReader
 pdf=ROOT/'output/pdf/DUT_Gate_Resistance_Limits.pdf'
 assert len(PdfReader(pdf).pages)==3
 render=ROOT/'tmp/pdfs';render.mkdir(parents=True,exist_ok=True)
 subprocess.run(['pdftoppm','-scale-to','1400','-png',str(pdf),str(render/'final')],check=True)
 (ROOT/'READY-FOR-VISUAL-REVIEW.txt').write_text(str(pdf))
 print('READY FOR VISUAL REVIEW',pdf,flush=True)

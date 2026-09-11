"""Run the canonical design study and compile its LaTeX report."""
import argparse,os,shutil,subprocess
from pathlib import Path
from run_sweep import ROOT,run

def main(config):
 s=run(config);out=ROOT/'reports/generated';out.mkdir(parents=True,exist_ok=True)
 text=(ROOT/'reports/templates/half_bridge_report.tex').read_text(encoding='utf-8-sig')
 rows='\n'.join(f"{r['modulation']} & {r['parallel_count']} & {r['frequency_hz']/1000:.0f} & {r['efficiency_pct']:.3f} & {r['junction_c']:.1f}"+r' \\' for r in s['highest_frequency_per_configuration'])
 text=text.replace('@ROWS@',rows).replace('@RESULTS@','Selected by highest switching frequency in each configuration, subject to the assumed efficiency, mean thermal, current, voltage and minimum-pulse screens. No parallel-bank hardware qualification is implied.')
 (out/'loss_report.tex').write_text(text,encoding='utf-8')
 fallback=Path(os.environ.get('LOCALAPPDATA',''))/'Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
 exe=os.environ.get('PDFLATEX') or shutil.which('pdflatex') or str(fallback)
 for _ in range(2):subprocess.run([exe,'-interaction=nonstopmode','-halt-on-error','loss_report.tex'],cwd=out,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 print('Built '+str(out/'loss_report.pdf'))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=ROOT/'data/inputs/design.json');main(p.parse_args().config)

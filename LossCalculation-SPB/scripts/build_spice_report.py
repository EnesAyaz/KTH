"""Build the standalone SPICE report; --refresh regenerates DC runs and figures."""
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from characterize_spice import ROOT, main as characterize


def main(refresh=False):
    summary_path=ROOT/'results/spice_characterization/summary.json'
    if refresh or not summary_path.exists(): characterize()
    summary=json.loads(summary_path.read_text())
    template=(ROOT/'reports/templates/spice_characterization.tex').read_text()
    table='\n'.join(f"{r['temperature_c']:g} & {r['rds_on_mohm']:.4f}"+r' \\' for r in summary['rds_at_50a'])
    figures='\n'.join(r'\clearpage\subsection{'+f['label'].replace('(uJ)','(microjoule)')+r'}'+ '\n'+r'\includegraphics[width=\linewidth]{../../results/spice_characterization/'+f['file']+'.pdf}' for f in summary['figures'])
    c=summary['dpt_config']
    setup='\n'.join(label+' & '+str(c[key])+r' \\' for key,label in [
        ('bus_voltages_v','Bus voltages (V)'),('target_currents_a','Target currents (A)'),
        ('external_gate_resistances_ohm','External gate resistances (ohm)'),
        ('power_loop_inductances_nh','Bus-side loop inductances (nH)'),
        ('temperature_c','DPT temperature (C)'),('driver_resistance_ohm','Driver resistance (ohm)'),
        ('driver_edge_ns','Driver edge (ns)'),('common_source_inductance_nh','Additional common-source L (nH)'),
        ('gate_loop_inductance_nh','Gate-loop L (nH)'),('energy_window_ns','Energy window (ns)')])
    for marker,value in {'@RDS@':table,'@FIGURES@':figures,'@SETUP@':setup,
                         '@CASES@':str(summary['switching_cases']),'@FAILURES@':str(summary['failed_cases'])}.items():
        template=template.replace(marker,value)
    out=ROOT/'reports/generated'; out.mkdir(parents=True,exist_ok=True)
    (out/'spice_characterization.tex').write_text(template,encoding='utf-8')
    fallback=Path(os.environ.get('LOCALAPPDATA',''))/'Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
    latex=os.environ.get('PDFLATEX') or shutil.which('pdflatex') or str(fallback)
    for _ in range(2):
        subprocess.run([latex,'-interaction=nonstopmode','-halt-on-error','spice_characterization.tex'],cwd=out,check=True)
    print(f"Report: {out/'spice_characterization.pdf'}")


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true')
    main(parser.parse_args().refresh)

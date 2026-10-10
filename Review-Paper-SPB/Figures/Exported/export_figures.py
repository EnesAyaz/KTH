"""Rebuild all embeddable figures from the repository root.
Usage: python Figures/Exported/export_figures.py [--aux PATH_TO_MAIN_AUX]
Requires pdflatex, numpy, pymupdf, matplotlib. The saved source snippets
retain the original drawing inputs. Refresh after changing figure citations.
"""
from pathlib import Path
import argparse,concurrent.futures,json,os,subprocess,tempfile
import numpy as np
import pymupdf
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('--aux',type=Path);args=parser.parse_args()
aux=args.aux or ROOT/'main.aux'
if aux.exists():
 OUT.joinpath('crossrefs.tex').write_text('\n'.join(x for x in aux.read_text().splitlines() if x.startswith(r'\bibcite') or x.startswith(r'\newlabel'))+'\n')
items=json.loads((OUT/'manifest.json').read_text())
BUILD=Path(tempfile.mkdtemp(prefix='spb-figure-export-'))
PREAMBLE=r'''
\documentclass[border=0pt]{standalone}
\usepackage{times,amsmath,amsfonts,amssymb,array,textcomp,graphicx,booktabs,cite}
\usepackage[table]{xcolor}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{circuitikz}
\input{Figures/Style/pes_figure_style}
\renewcommand{\footnotesize}{\fontsize{8}{9.5}\selectfont}
\renewcommand{\scriptsize}{\fontsize{7}{8}\selectfont}
\setlength{\textwidth}{504pt}
\makeatletter\input{Figures/Exported/crossrefs}\makeatother
'''
def export(item):
 name=item['name'];width='504pt' if item['wide'] else '246pt'
 tex=PREAMBLE+r'\setlength{\columnwidth}{'+width+'}\n'+r'\begin{document}'+'\n'+r'\begin{minipage}{'+width+'}\n'+r'\centering\pesfigfont'+'\n'+r'\input{Figures/Exported/'+name+'_source}\n'+r'\end{minipage}\end{document}'+'\n'
 source=BUILD/(name+'.tex');source.write_text(tex)
 result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(BUILD),str(source)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (BUILD/(name+'-console.txt')).write_bytes(result.stdout)
 if result.returncode:raise RuntimeError(name+': '+result.stdout.decode(errors='replace')[-1800:])
 doc=pymupdf.open(BUILD/(name+'.pdf'));page=doc[0]
 # Find visible ink on a rendered page, then crop the original vector PDF.
 pix=page.get_pixmap(matrix=pymupdf.Matrix(3,3),alpha=False)
 data=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3]
 ys,xs=np.where(np.min(data,axis=2)<247)
 rect=pymupdf.Rect(max(0,xs.min()/3-.8),max(0,ys.min()/3-.8),min(page.rect.width,(xs.max()+1)/3+.8),min(page.rect.height,(ys.max()+1)/3+.8))
 page.set_cropbox(rect)
 target=OUT/(name+'.pdf')
 if target.exists():target.unlink()
 doc.save(target,garbage=4,deflate=True);doc.close()
 cropped=pymupdf.open(target);p=cropped[0]
 p.get_pixmap(matrix=pymupdf.Matrix(300/72,300/72),alpha=False).save(OUT/(name+'.png'))
 (OUT/(name+'.svg')).write_text(p.get_svg_image(text_as_path=True),encoding='utf-8')
 cropped.close();return name
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for future in concurrent.futures.as_completed([pool.submit(export,x) for x in items]):print('Exported',future.result(),flush=True)
print('All 16 figures exported. Build logs:',BUILD)

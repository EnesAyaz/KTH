from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sys,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from lxml import etree as E

ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/vector_alignment_2026-11-07';A.mkdir(parents=True,exist_ok=True)
SRC=P/'Submission-Final/ICPE_Digest_vector_figures_2026-11-07.docx';OUT=P/'Submission-Final/ICPE_Digest_vector_figures_aligned_2026-11-07.docx'
R=ROOT/'simulation/bb_spice/icpe_digest_revision_2026-11-06/controlled_current';D=json.loads((R/'results_complete_windows.json').read_text())
sys.path.insert(0,str(ROOT/'scripts'));from icpe_gate_results import read_raw
with ZipFile(SRC) as z:files={n:z.read(n) for n in z.namelist()}
sourcehash=hashlib.sha256(SRC.read_bytes()).hexdigest();root=E.fromstring(files['word/document.xml']);ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
extent=root.findall('.//w:drawing',ns)[7].find('.//wp:extent',ns);width=int(extent.get('cx'))/12700;height=int(extent.get('cy'))/12700
matplotlib.rcParams.update({'font.family':'Times New Roman','font.size':7,'svg.fonttype':'none','pdf.fonttype':42,'axes.linewidth':.5,'axes.labelsize':7,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.unicode_minus':True,'savefig.pad_inches':0})
fig=plt.figure(figsize=(width/72,height/72),facecolor='white')
left=[27,145,263];plotw=width-263-7;bottom=30;top=height-18
axs=[fig.add_axes([x/width,bottom/height,plotw/width,(top-bottom)/height]) for x in left]
for ax in axs:
 ax.spines[['top','right']].set_visible(False);ax.tick_params(direction='out',length=2,width=.5,pad=1)
 ax.grid(axis='y',color='#E2E0DA',linewidth=.3);ax.set_axisbelow(True)
 ax.xaxis.labelpad=1;ax.yaxis.labelpad=1
axs[0].set(xlim=(0,45),ylim=(-4,110),xticks=[0,20,40],yticks=[0,50,100],xlabel='Time from turn-on (ns)',ylabel='Drain voltage (V)')
axs[1].set(xlim=(0,45),ylim=(-3,2),xticks=[0,20,40],yticks=[-2,0,1],xlabel='Time from turn-on (ns)',ylabel='Gate voltage (V)')
axs[2].set(xlim=(0,330),ylim=(85,94),xticks=[0,160,320],yticks=[86,90,94],xlabel='Total current (A)',ylabel='Peak voltage (V)')
titles=['(a) Rated current','(b) Rated current','(c) Current sweep']
for ax,title in zip(axs,titles):fig.text(ax.get_position().x0+ax.get_position().width/2,(height-5.5)/height,title,ha='center',va='baseline',fontsize=7)
INK='#111111';OCHRE='#C38714';WINE='#A41C59';TEAL='#018789';GREY='#898781'
series={};handles=[]
for lab,r,bias,col,ls in [('A',2,0,INK,'-'),('B',3,0,OCHRE,'--'),('C',3,-1,WINE,'-')]:
 key=f'proto_g20_r{r}_off{bias}_i322.061_v75_t27_dt0.2';z=read_raw(R/(key+'.raw'))[0];v=D[key]
 k=max(v['branches'],key=lambda b:b['vhs_on'])['k'];kg=max(v['branches'],key=lambda b:b['gate_bump'])['k'];t=(z['time']-1.7e-6)*1e9
 mask=(t>=-.2)&(t<=45.2);vv=z[f'v(dh{k})']-z[f'v(qh_s_{k})'];gg=z[f'v(gh{kg})']-z[f'v(qh_s_{kg})']
 axs[0].plot(t[mask],vv[mask],color=col,lw=.8,ls=ls,clip_on=True);axs[1].plot(t[mask],gg[mask],color=col,lw=.8,ls=ls,clip_on=True)
 handles.append(Line2D([],[],color=col,lw=.8,ls=ls,label=lab))
 series[lab]={'source':key,'drain_branch':k,'gate_branch':kg,'drain_min_V':float(vv[mask].min()),'drain_max_V':float(vv[mask].max())}
for g,col,ls,mark,lab in [(10,TEAL,'-','o','D: 10 nH'),(20,WINE,'--','s','C: 20 nH')]:
 pts=sorted((v['setup']['controlled_current_A'],v['vds_peak']) for v in D.values() if v['setup']['gate_loop_nH']==g and v['setup']['Rgon_ohm']==3 and v['setup']['Voff_V']==-1 and v['setup']['Tj_C']==27 and v['setup']['Vbus_V']==75 and abs(v['setup']['controlled_current_A']-315.946)>.1)
 assert len(pts)==6
 axs[2].plot(*np.array(pts).T,color=col,lw=.8,ls=ls,marker=mark,ms=2.7,mew=.5,label=lab,clip_on=True)
 series[lab]=pts
for ax,level in [(axs[0],90),(axs[1],.8),(axs[2],90)]:ax.axhline(level,color=GREY,lw=.6,ls=(0,(3,2)),zorder=1)
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.35,.005),ncol=3,frameon=False,borderpad=0,borderaxespad=0,columnspacing=1.1,handlelength=1.6,handletextpad=.4)
axs[2].legend(loc='lower center',bbox_to_anchor=(.85,.005),bbox_transform=fig.transFigure,ncol=2,frameon=False,borderpad=0,borderaxespad=0,columnspacing=.7,handlelength=1.4,handletextpad=.4)
fig.canvas.draw();renderer=fig.canvas.get_renderer()
# Labels must fit inside the figure, and the three plot frames share exact top/bottom bounds.
for ax in axs:
 for text in [ax.xaxis.label,ax.yaxis.label,*ax.get_xticklabels(),*ax.get_yticklabels()]:
  bb=text.get_window_extent(renderer);assert bb.x0>=-.5 and bb.y0>=-.5 and bb.x1<=fig.bbox.width+.5 and bb.y1<=fig.bbox.height+.5,(text.get_text(),bb,fig.bbox)
assert len({round(ax.get_position().y0,8) for ax in axs})==1
assert len({round(ax.get_position().y1,8) for ax in axs})==1
asset=A/'fig08_aligned'
for typ in ['svg','pdf','png']:fig.savefig(asset.with_suffix('.'+typ),dpi=600,facecolor='white')
plt.close(fig)
files['word/media/vector_quality_8.svg']=asset.with_suffix('.svg').read_bytes();files['word/media/image8.png']=asset.with_suffix('.png').read_bytes()
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for name,data in files.items():z.writestr(name,data)
with ZipFile(SRC) as z:
 assert z.read('word/document.xml')==files['word/document.xml']
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==sourcehash
(A/'verification.json').write_text(json.dumps({'source_sha256':sourcehash,'width_pt':width,'height_pt':height,'axes_bounds':[list(ax.get_position().bounds) for ax in axs],'data':series,'text_and_layout_xml_unchanged':True},indent=2))
print(OUT)

"""EPC2361 low-side double pulse test generator and Tkinter editor."""
from pathlib import Path
import datetime
import json
import math
import os
import queue
import re
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from dpt_visuals import FIELDS, SetupDiagram, conduction_loss as _conduction_loss

BASE = Path(__file__).resolve().parent
GROUPS = {
 'Operating point': [
  ('Vin','Bus voltage (V)','48'), ('Itest','Target current for estimated first pulse (A)','16'),
  ('Lload','Load inductance (H)','20u'), ('Rload','Load inductor resistance (ohm)','20m'),
  ('Tj','Fixed device temperature (deg C)','100'), ('AutoT1','Estimate first pulse: 1=yes, 0=manual','1'),
  ('Tcharge','Manual first-pulse plateau (s)','6.667u'),
  ('Fsw','Switching frequency for loss estimate (Hz)','500k'),
  ('Vlimit','Vds design ceiling for both devices (V)','100')],
 'Pulse timing': [
  ('Tdelay','Initial delay (s)','1u'), ('Toff','Off interval between pulses (s)','1u'),
  ('Tsecond','Second-pulse plateau (s)','1u'), ('Tr','Command rise time (s)','2n'),
  ('Tf','Command fall time (s)','2n'), ('Ttail','Observation after final turn-off (s)','2u'),
  ('Maxstep','Maximum simulation step (s)','1n'),
  ('Wpre','Energy window before command edge (s)','20n'),
  ('Wpost','Energy window after command edge (s)','100n')],
 'DC link & layout': [
  ('Cin','DC-link input capacitance (F)','100u'), ('ESR','DC-link capacitor ESR (ohm)','5m'),
  ('ESL','DC-link capacitor ESL (H)','1n'), ('Lloop','External layout loop inductance (H)','5n'),
  ('Rloop','Layout loop resistance (ohm)','5m'),
  ('Rcharge','Supply charging / isolation resistance (ohm)','10'),
  ('CSI','Common-source inductance per device (H)','100p')],
 'Gate drive': [
  ('Von','Low-side on voltage (V)','5'), ('Voff','Off voltage, both devices (V)','0'),
  ('Rg_on','External turn-on gate resistance (ohm)','1.8'),
  ('Rg_off','External turn-off gate resistance (ohm)','0.5'),
  ('RGD_PU','Driver pull-up resistance (ohm)','0.7'),
  ('RGD_PD','Driver pull-down resistance (ohm)','0.4'),
  ('Rg_HS','Upper device off-state gate resistance (ohm)','0.9')]
}
GROUPS['Conduction loss'] = FIELDS
DEFAULTS = {k:v for rows in GROUPS.values() for k,_,v in rows}

def number(text):
    s = str(text).strip().replace('µ','u').replace('μ','u')
    m = re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)(meg|[tgkmunpf]?)(?:[a-z]*)',s,re.I)
    if not m:
        raise ValueError(f'Invalid numeric value: {text}. Examples: 48, 20u, 5n, 100pH.')
    value = float(m[1])*{'':1,'t':1e12,'g':1e9,'meg':1e6,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12,'f':1e-15}[m[2].lower()]
    if not math.isfinite(value): raise ValueError('Values must be finite.')
    return value

def validate(values):
    p = {k:number(values[k]) for k in DEFAULTS}
    nonnegative = {'Rload','ESR','ESL','Lloop','Rloop','CSI','Rg_on','Rg_off','RGD_PU','RGD_PD','Tdelay','Icond','DutyLS','DutyHS'}
    special = {'Tj','Voff','AutoT1'}
    for k,v in p.items():
        if k in special: continue
        if (k in nonnegative and v<0) or (k not in nonnegative and v<=0):
            raise ValueError(f'{k} must be {"nonnegative" if k in nonnegative else "positive"}.')
    conduction_loss(values)
    if p['AutoT1'] not in (0,1): raise ValueError('AutoT1 must be 0 or 1.')
    if not p['Vin'] < p['Vlimit'] <= 120: raise ValueError('Choose a Vds ceiling above the DC supply and at most 120 V. Prefer 100 V with margin.')
    if p['Tj']<=-273.15: raise ValueError('Temperature must exceed absolute zero.')
    if p['Von']<=p['Voff']: raise ValueError('On voltage must exceed off voltage.')
    if p['Rg_on']+p['RGD_PU']<=0 or p['Rg_off']+p['RGD_PD']<=0:
        raise ValueError('Total on/off gate resistances must be positive.')
    p['T1'] = p['Itest']*p['Lload']/p['Vin'] if p['AutoT1'] else p['Tcharge']
    p['A'] = p['Tdelay'] + p['Tr'] + p['T1']
    p['B'] = p['A'] + p['Tf'] + p['Toff']
    p['C'] = p['B'] + p['Tr'] + p['Tsecond']
    p['Stop'] = p['C'] + p['Tf'] + p['Ttail']
    if p['Wpre']>=min(p['T1'],p['Toff'],p['Tsecond']):
        raise ValueError('Energy pre-window must be shorter than each pulse and off interval.')
    if p['Wpost']>=min(p['Toff'],p['Tsecond'],p['Ttail']):
        raise ValueError('Energy post-window must be shorter than the off interval, second pulse and tail.')
    if p['Wpost']<=max(p['Tr'],p['Tf']): raise ValueError('Energy post-window must exceed command edge time.')
    if p['Maxstep']>min(p['Tr'],p['Tf'])/2:
        raise ValueError('Maximum step must be at most half the shorter command edge.')
    if p['Stop']/p['Maxstep']>5e6: raise ValueError('More than 5 million steps requested; adjust timing or maximum step.')
    return p

def circuit(values):
    p=validate(values)
    fmt=lambda v: format(v,'.12g')
    params = ['.param '+' '.join(f'{k}={fmt(p[k])}' for k,_,_ in rows) for title,rows in GROUPS.items() if title!='Conduction loss']
    params += ['.param T1=if(AutoT1,Itest*Lload/Vin,Tcharge)',
               '.param A=Tdelay+Tr+T1 B=A+Tf+Toff C=B+Tr+Tsecond Stop=C+Tf+Ttail']
    pwl='PWL(0 0 {Tdelay} 0 {Tdelay+Tr} 5 {A} 5 {A+Tf} 0 {B} 0 {B+Tr} 5 {C} 5 {C+Tf} 0 {Stop} 0)'
    # kind, instance, nodes, value, additional instance attributes
    parts=[
      ('voltage','Vdc',['supply','0'],'{Vin}',''),
      ('res','Rcharge',['supply','bus'],'{Rcharge}',''),
      ('res','Rcap',['bus','cap_esl'],'{ESR}',''),
      ('ind','Lcap',['cap_esl','cap'],'{max(ESL,1e-15)}','Rser=0'),
      ('cap','Cin',['cap','0'],'{Cin}',''),
      ('ind','Llayout',['bus','rail'],'{max(Lloop,1e-15)}','Rser={Rloop}'),
      ('ind','Lload',['rail','sw'],'{Lload}','Rser={Rload}'),
      ('EPCGaN','XHS',['gh','rail','sh'],'EPC2361',''),
      ('ind','Lsh',['sh','sw'],'{max(CSI,1e-15)}','Rser=0'),
      ('voltage','Vsense',['sw','drain'],'0',''),
      ('EPCGaN','XDUT',['gl','drain','sl'],'EPC2361',''),
      ('ind','Lsl',['sl','0'],'{max(CSI,1e-15)}','Rser=0'),
      ('voltage','Vhs',['offhs','sw'],'{Voff}',''),
      ('res','Rhs',['offhs','gh'],'{Rg_HS}',''),
      ('voltage','Vcmd',['cmd','0'],pwl,''),
      ('voltage','Von',['on','0'],'{Von}',''),
      ('voltage','Voff',['off','0'],'{Voff}',''),
      ('sw','Sup',['on','pu','cmd','0'],'DRV_ON',''),
      ('res','Rup',['pu','gl'],'{Rg_on+RGD_PU}',''),
      ('sw','Sdown',['off','pd','cmd','0'],'DRV_OFF',''),
      ('res','Rdown',['pd','gl'],'{Rg_off+RGD_PD}',''),
    ]
    directives=params+[
      '.model DRV_ON SW(Ron=1m Roff=1G Vt=2.5 Vh=0)',
      '.model DRV_OFF SW(Ron=1G Roff=1m Vt=2.5 Vh=0)',
      '.include ".\\EPCGaNLibrary.lib"', '.temp {Tj}',
      '.tran 0 {Stop} 0 {Maxstep}', '.options plotwinsize=0',
      '.save V(cmd) V(gl,sl) V(gh,sh) V(drain,sl) V(bus) V(rail) V(sw) I(Lload) I(Vsense) I(Cin)',
      '.meas tran I_first_off FIND I(Lload) AT={A}',
      '.meas tran I_second_on FIND I(Lload) AT={B}',
      '.meas tran Vds_peak MAX V(drain,sl)',
      '.meas tran Vds_HS_peak MAX V(rail,sh)',
      '.meas tran Vds_HS_min MIN V(rail,sh)',
      '.meas tran Vgs_HS_peak MAX V(gh,sh)',
      '.meas tran Vgs_HS_min MIN V(gh,sh)',
      '.meas tran Vbus_min MIN V(bus)',
      '.meas tran Eoff1_window INTEG V(drain,sl)*I(Vsense) FROM={A-Wpre} TO={A+Wpost}',
      '.meas tran Eon2_window INTEG V(drain,sl)*I(Vsense) FROM={B-Wpre} TO={B+Wpost}',
      '.meas tran Eoff2_window INTEG V(drain,sl)*I(Vsense) FROM={C-Wpre} TO={C+Wpost}',
      '.meas tran Eoff1_uJ PARAM Eoff1_window*1e6',
      '.meas tran Eon2_uJ PARAM Eon2_window*1e6',
      '.meas tran Eoff2_uJ PARAM Eoff2_window*1e6',
      '.meas tran Psw_DUT_W PARAM (Eon2_window+Eoff1_window)*Fsw',
      '.meas tran Psw_second_pair_W PARAM (Eon2_window+Eoff2_window)*Fsw',
    ]
    return parts,directives,p

def netlist(values):
    parts,directives,_=circuit(values)
    return '\n'.join(['* EPC2361 low-side DPT; upper GaN held off']+
      [' '.join([name]+nodes+[value]+([extra] if extra else [])) for kind,name,nodes,value,extra in parts]+directives+['.end',''])

def schematic(values):
    parts,directives,_=circuit(values)
    # Each element has explicit labeled terminals; identical labels connect across sections.
    positions=[(96,96),(96,320),(352,96),(352,320),(352,544),
               (640,96),(928,96),(1200,192),(1264,320),(1552,96),
               (1472,416),(1536,544),(928,320),(928,544),
               (96,896),(352,896),(352,1120),(672,896),(928,896),(672,1120),(928,1120)]
    lines=['Version 4','SHEET 1 2700 1600',
      'TEXT 48 0 Left 3 ;EPC2361 DOUBLE PULSE TEST - LOW-SIDE DUT',
      'TEXT 48 40 Left 2 ;DC link / capacitor     |     External layout     |     Load and half bridge',
      'TEXT 48 736 Left 2 ;Named terminals connect electrically. Llayout is additional PCB/bus loop inductance.',
      'TEXT 48 776 Left 2 ;Upper GaN held OFF; reverse conduction carries load current between pulses.',
      'TEXT 48 832 Left 3 ;GATE DRIVER - two pulses, separate pull-up / pull-down resistances',
      'TEXT 48 1328 Left 2 ;Probe V(drain,sl), V(gl,sl), I(Vsense), I(Lload), V(bus). Energy integrals use adjustable time windows.']
    for (kind,name,nodes,value,extra),(x,y) in zip(parts,positions):
        lines.append(f'SYMBOL {kind} {x} {y} R0')
        if name=='Vcmd':
            lines += ['WINDOW 3 24 108 Left 0']
        lines += [f'SYMATTR InstName {name}',f'SYMATTR Value {value}']
        if extra: lines.append(f'SYMATTR SpiceLine {extra}')
        if kind=='EPCGaN': lines.append('SYMATTR ModelFile .\\EPCGaNLibrary.lib')
        pins={'res':[(16,16),(16,96)],'ind':[(16,16),(16,96)],
              'cap':[(16,0),(16,64)],'voltage':[(0,16),(0,96)],
              'sw':[(0,16),(0,96),(-48,80),(-48,32)],
              'EPCGaN':[(0,0),(80,-96),(80,32)]}[kind]
        for node,(dx,dy) in zip(nodes,pins): lines.append(f'FLAG {x+dx} {y+dy} {node}')
    for i,d in enumerate(directives): lines.append(f'TEXT 1792 {32+i*40} Left 2 !{d}')
    return '\n'.join(lines)+'\n'

def export(values,path):
    validate(values)
    path=Path(path)
    if path.suffix.lower()!='.asc': raise ValueError('Choose an .asc file.')
    if path.resolve()==(BASE/'Example-EPC.asc').resolve(): raise ValueError('Choose a DPT filename; the original buck example is protected.')
    library=BASE/'EPCGaNLibrary.lib'
    symbol=BASE/'EPCGaN.asy'
    for source in (library,symbol):
        target=path.parent/source.name
        if not source.is_file(): raise ValueError(f'Missing {source.name}')
        if source.resolve()!=target.resolve() and target.exists() and target.read_bytes()!=source.read_bytes():
            raise ValueError(f'Different {source.name} already exists in destination. Choose a new folder.')
    path.parent.mkdir(parents=True,exist_ok=True)
    for source in (library,symbol):
        target=path.parent/source.name
        if source.resolve()!=target.resolve() and not target.exists(): shutil.copy2(source,target)
    path.write_text(schematic(values),encoding='utf-8')
    path.with_suffix('.cir').write_text(netlist(values),encoding='utf-8')
    path.with_suffix('.json').write_text(json.dumps(values,indent=2),encoding='utf-8')
    return path

def find_ltspice():
    for path in [Path(os.environ.get('LOCALAPPDATA',''))/'Programs/ADI/LTspice/LTspice.exe',
                 Path('C:/Program Files/ADI/LTspice/LTspice.exe'),Path('C:/Program Files/LTC/LTspiceXVII/XVIIx64.exe')]:
        if path.is_file(): return str(path)
    return ''

def normalize_settings(data):
    if not isinstance(data,dict) or set(data)-set(DEFAULTS) or set(DEFAULTS)-set(data)-{'Fsw','Vlimit','Icond','DutyLS','DutyHS','RdsLS','RdsHS'}:
        raise ValueError('Select a settings file from this DPT editor.')
    merged=dict(DEFAULTS,**data)
    if 'Icond' not in data:merged['Icond']=data['Itest']
    return merged

def conduction_loss(values):
    return _conduction_loss(values,number)

def parse_measurements(content):
    return {k.lower():float(v) for k,v in re.findall(r'^(\w+):[^\r\n]*?=([-+\d.eE]+)',content,re.M)}

def result_summary(content,values):
    m=parse_measurements(content)
    frequency=number(values['Fsw'])
    rows=[]
    for key,label,unit,scale in [
        ('i_first_off','Load current at first turn-off','A',1),
        ('i_second_on','Load current at second turn-on','A',1),
        ('vds_peak','Low-side DUT maximum Vds','V',1),
        ('vds_hs_peak','High-side maximum Vds','V',1),
        ('vds_hs_min','High-side minimum Vds','V',1),
        ('vgs_hs_peak','High-side maximum Vgs','V',1),
        ('vgs_hs_min','High-side minimum Vgs','V',1),
        ('eoff1_window','DUT Eoff1 - first turn-off','uJ',1e6),
        ('eon2_window','DUT Eon2 - second turn-on','uJ',1e6),
        ('eoff2_window','DUT Eoff2 - second turn-off','uJ',1e6)]:
        rows.append((label,format(m[key]*scale,'.6g') if key in m else 'Unavailable',unit))
    rows.append(('Switching frequency',format(frequency/1000,'.6g'),'kHz'))
    negative=False
    for off,label in [('eoff1_window','Estimated DUT Psw: Eon2 + Eoff1'),('eoff2_window','Alternate DUT Psw: Eon2 + Eoff2')]:
        if off not in m or 'eon2_window' not in m:value='Unavailable'
        elif m[off]<0 or m['eon2_window']<0:value='Review energy';negative=True
        else:value=format((m[off]+m['eon2_window'])*frequency,'.6g')
        rows.append((label,value,'W'))
    low,high,total=conduction_loss(values)
    rows.extend([('Estimated low-side ON conduction',format(low,'.6g'),'W'),
                 ('Estimated high-side ON conduction',format(high,'.6g'),'W'),
                 ('Estimated half-bridge ON conduction',format(total,'.6g'),'W')])
    limit=number(values.get('Vlimit','100'))
    peak=max(m.get('vds_peak',float('nan')),m.get('vds_hs_peak',float('nan')))
    margin=limit-peak
    voltage_note=f'Vds ceiling {limit:g} V: worst peak {peak:.3f} V; margin {margin:.3f} V. '+('Exceeded.' if margin<0 else 'Within ceiling for this simulation only.')+'\n'
    notes=voltage_note+'Psw = (Eon + Eoff) x Fsw. Primary pair: Eon2 + Eoff1, at similar load current. Eoff2 is at a higher current. Frequency scales the loss estimate; it does not repeat the DPT pulses.\nSigned integration-window energies include capacitive/ringing energy. These are DUT-only estimates, excluding conduction, gate-drive and high-side losses.'
    notes+='\nConduction is a separate periodic half-bridge estimate: I_rms,on^2 x ON fraction x Rds(on). Upper FET stays OFF in the DPT. Rds inputs must reflect operating temperature; dead-time reverse conduction is excluded.'
    notes+='\nEnergy depends on integration bounds and timestep; check convergence before using the estimate.'
    if m.get('vds_hs_peak',0)>120 or m.get('vds_peak',0)>120:
        notes+='\nSimulated Vds exceeds EPC2361 120 V repetitive-transient rating (rating applies only at <=1% duty). The model does not establish survival.'
    if negative:notes+='\nA negative event energy prevents a meaningful dissipative-loss estimate; inspect the waveforms and integration bounds.'
    return rows,notes

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('EPC GaN | Double pulse test')
        self.geometry('1000x800'); self.minsize(900,740)
        self.events=queue.Queue(); self.running=False
        frame=ttk.Frame(self,padding=18); frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='Double pulse test',font=('Segoe UI',22,'bold')).pack(anchor='w')
        ttk.Label(frame,text='EPC2361 low-side DUT  /  upper device held off  /  finite DC-link capacitor').pack(anchor='w',pady=(3,12))
        tabs=ttk.Notebook(frame); tabs.pack(fill='both',expand=True)
        self.vars={}
        for title,rows in GROUPS.items():
            page=ttk.Frame(tabs,padding=16); tabs.add(page,text=title); page.columnconfigure(1,weight=1)
            for i,(key,label,default) in enumerate(rows):
                ttk.Label(page,text=label).grid(row=i,column=0,sticky='w',pady=8)
                v=tk.StringVar(value=default); self.vars[key]=v
                ttk.Entry(page,textvariable=v,width=24).grid(row=i,column=1,sticky='ew',padx=(24,0))
                v.trace_add('write',self.preview)
            if title=='Conduction loss':
                ttk.Label(page,text='Periodic half-bridge estimate, separate from the two-pulse simulation.\nUse RMS current within the ON intervals; ON fraction is applied once.\nDefault 2 mOhm values are illustrative: enter Rds(on) at the actual temperature and gate voltage.\nExcludes dead-time reverse conduction, switching, gate drive and passive losses.',wraplength=820).grid(row=len(rows),column=0,columnspan=2,sticky='w',pady=12)
                self.conduction_text=tk.StringVar()
                ttk.Label(page,textvariable=self.conduction_text,font=('Segoe UI',12,'bold')).grid(row=len(rows)+1,column=0,columnspan=2,sticky='w',pady=8)
        diagram_page=ttk.Frame(tabs)
        tabs.add(diagram_page,text='Setup schematic')
        self.diagram=SetupDiagram(diagram_page,self.values)
        self.diagram.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(frame,height=94,bg='#f0f4f8',highlightthickness=0)
        self.canvas.pack(fill='x',pady=(12,4))
        self.summary=tk.StringVar(); ttk.Label(frame,textvariable=self.summary,wraplength=950).pack(anchor='w')
        ttk.Label(frame,text='Input capacitance = DC-link Cin. Device capacitances remain in the EPC model.\nSPICE units: u=micro, n=nano, p=pico, m=milli, Meg=mega. Results show signed window energies in uJ and estimated DUT switching loss in W.',wraplength=950).pack(anchor='w',pady=8)
        self.exe=tk.StringVar(value=find_ltspice())
        ex=ttk.Frame(frame); ex.pack(fill='x')
        ttk.Label(ex,text='LTspice:').pack(side='left'); ttk.Entry(ex,textvariable=self.exe).pack(side='left',fill='x',expand=True,padx=8)
        ttk.Button(ex,text='Browse...',command=self.browse).pack(side='right')
        actions=ttk.Frame(frame); actions.pack(fill='x',pady=12)
        for label,fn in [('Load settings',self.load),('Defaults',self.reset),('75 V / 50 A preset',self.load_75_50),('Save setup',self.save),('Save + open',lambda:self.save(True)),('Run DPT',self.run)]:
            ttk.Button(actions,text=label,command=fn).pack(side='left',padx=(0,8))
        self.status=tk.StringVar(value='Ready. First-pulse current is an estimate; use measured current from the simulation.')
        ttk.Label(frame,textvariable=self.status,wraplength=950).pack(anchor='w')
        self.preview(); self.poll_id=self.after(200,self.poll)

    def destroy(self):
        if hasattr(self,'poll_id'):
            self.after_cancel(self.poll_id)
        super().destroy()

    def values(self): return {k:v.get().strip() for k,v in self.vars.items()}
    def preview(self,*_):
        if not hasattr(self,'canvas'): return
        self.canvas.delete('all')
        try:
            p=validate(self.values())
            low,high,total=conduction_loss(self.values())
            self.conduction_text.set(f'Low-side: {low:.3f} W   |   High-side: {high:.3f} W   |   Total ON conduction: {total:.3f} W')
            self.diagram.redraw()
            self.summary.set(f'First pulse: {p["T1"]*1e6:.3f} us | Gap: {p["Toff"]*1e6:.3f} us | Second pulse: {p["Tsecond"]*1e6:.3f} us | Total: {p["Stop"]*1e6:.3f} us\nIdeal first turn-off current: {p["Vin"]*p["T1"]/p["Lload"]:.2f} A. Finite capacitance, resistance and freewheeling change actual current.')
            ts=[0,p['Tdelay'],p['Tdelay']+p['Tr'],p['A'],p['A']+p['Tf'],p['B'],p['B']+p['Tr'],p['C'],p['C']+p['Tf'],p['Stop']]
            ys=[70,70,30,30,70,70,30,30,70,70]
            coords=[z for t,y in zip(ts,ys) for z in (30+850*t/p['Stop'],y)]
            self.canvas.create_line(*coords,fill='#166caa',width=3)
            self.canvas.create_text(30,12,text='Gate command: charge pulse → freewheel → measurement pulse',anchor='w',fill='#263e53')
        except (ValueError,KeyError) as exc:
            self.summary.set(str(exc))
            self.conduction_text.set('Enter valid conduction-loss assumptions.')
            self.diagram.redraw()
    def reset(self):
        for k,v in DEFAULTS.items(): self.vars[k].set(v)
    def load_75_50(self):
        try:
            data=normalize_settings(json.loads((BASE/'DPT-75V-50A-candidate.json').read_text(encoding='utf-8-sig')))
            validate(data)
            for k,v in data.items():self.vars[k].set(str(v))
            self.status.set('Simulation candidate loaded: requires 1 nH layout and 0.2 nH capacitor ESL. Not hardware qualification.')
        except (OSError,ValueError) as exc:messagebox.showerror('Preset',str(exc))
    def browse(self):
        p=filedialog.askopenfilename(filetypes=[('LTspice executable','*.exe')])
        if p:self.exe.set(p)
    def load(self):
        path=filedialog.askopenfilename(initialdir=BASE,filetypes=[('DPT settings','*.json')])
        if not path:return
        try:
            data=json.loads(Path(path).read_text(encoding='utf-8-sig'))
            data=normalize_settings(data)
            validate(data)
            for k,v in data.items():self.vars[k].set(str(v))
        except (OSError,ValueError,TypeError) as exc:messagebox.showerror('Settings',str(exc))
    def save(self,open_after=False):
        try:
            values=self.values(); validate(values)
            path=filedialog.asksaveasfilename(initialdir=BASE,initialfile='DPT-EPC-edited.asc',defaultextension='.asc',filetypes=[('LTspice schematic','*.asc')])
            if not path:return
            companions=[Path(path).with_suffix(s) for s in ('.cir','.json') if Path(path).with_suffix(s).exists()]
            if companions and not messagebox.askyesno('Replace saved setup','Replace associated .cir and .json files for this setup?'):return
            export(values,path); self.status.set(f'Saved schematic, netlist and settings: {path}')
            if open_after:
                exe=self.exe.get()
                if not Path(exe).is_file():raise ValueError('Select LTspice.exe to open the saved schematic.')
                subprocess.Popen([exe,path],cwd=Path(path).parent)
        except (OSError,ValueError) as exc:messagebox.showerror('Save',str(exc))
    def run(self):
        if self.running:return
        try:
            values=self.values(); validate(values)
            exe=self.exe.get()
            if not Path(exe).is_file():raise ValueError('Select LTspice.exe first.')
            dest=BASE/'dpt_runs'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')/'DPT-EPC.asc'
            export(values,dest)
            self.running=True; self.status.set('Running DPT... The interface remains available.')
            def worker():
                try:
                    result=subprocess.run([exe,'-b',str(dest.with_suffix('.cir'))],cwd=dest.parent,capture_output=True,timeout=180)
                    log=dest.with_suffix('.log')
                    raw=log.read_bytes() if log.exists() else b''
                    content=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else ('utf-16-le' if b'\0' in raw[:100] else 'utf-8'),errors='replace')
                    if result.returncode or not dest.with_suffix('.raw').exists() or 'i_second_on:' not in content.lower():
                        raise ValueError('Simulation did not produce complete measurements.\n'+content+'\n'+result.stderr.decode(errors='replace'))
                    self.events.put((True,dest,content))
                except Exception as exc:self.events.put((False,dest,str(exc)))
            threading.Thread(target=worker,daemon=True).start()
        except (OSError,ValueError) as exc:messagebox.showerror('Run DPT',str(exc))
    def poll(self):
        try:
            ok,dest,content=self.events.get_nowait(); self.running=False
            self.status.set(('Completed: ' if ok else 'Simulation failed: ')+str(dest.parent))
            win=tk.Toplevel(self);win.title('DPT results' if ok else 'DPT simulation log');win.geometry('900x600')
            if ok:
                saved=json.loads(dest.with_suffix('.json').read_text())
                tabs=ttk.Notebook(win);tabs.pack(fill='both',expand=True,padx=12,pady=12)
                summary=ttk.Frame(tabs,padding=12);tabs.add(summary,text='Measurements')
                table_frame=ttk.Frame(summary);table_frame.pack(fill='both',expand=True)
                tree=ttk.Treeview(table_frame,columns=('value','unit'),show='tree headings',height=13)
                tree.heading('#0',text='Measurement');tree.heading('value',text='Value');tree.heading('unit',text='Unit')
                tree.column('#0',width=430);tree.column('value',width=140,anchor='e');tree.column('unit',width=90)
                scroll=ttk.Scrollbar(table_frame,orient='vertical',command=tree.yview)
                tree.configure(yscrollcommand=scroll.set)
                scroll.pack(side='right',fill='y');tree.pack(side='left',fill='both',expand=True)
                rows,notes=result_summary(content,saved)
                for label,value,unit in rows:tree.insert('', 'end',text=label,values=(value,unit))
                ttk.Label(summary,text=notes,wraplength=820).pack(anchor='w',pady=10)
                logpage=ttk.Frame(tabs);tabs.add(logpage,text='Raw LTspice log')
                ttk.Button(win,text='Open waveforms in LTspice',command=lambda:subprocess.Popen([self.exe.get(),str(dest.with_suffix('.raw'))],cwd=dest.parent)).pack(pady=10)
            else:logpage=win
            box=tk.Text(logpage,wrap='word',padx=12,pady=12);box.pack(fill='both',expand=True)
            box.insert('1.0',content);box.configure(state='disabled')
        except queue.Empty:pass
        self.poll_id=self.after(200,self.poll)

if __name__=='__main__':App().mainloop()

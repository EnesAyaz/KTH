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
import dpt_parasitics as parasitics
import half_bridge

BASE = Path(__file__).resolve().parent
GROUPS = {
 'Operating point': [
  ('Vin','Bus voltage (V)','75'), ('Itest','Target current for estimated first pulse (A)','45'),
  ('Lload','Load inductance (H)','20u'), ('Rload','Load inductor resistance (ohm)','20m'),
  ('Tj','Fixed device temperature (deg C)','100'), ('AutoT1','Estimate first pulse: 1=yes, 0=manual','1'),
  ('Tcharge','Manual first-pulse plateau (s)','6.667u'),
  ('Fsw','Switching frequency for loss estimate (Hz)','500k'),
  ('Vlimit','Vds design ceiling for both devices (V)','100')],
 'Pulse timing': [
  ('Tdelay','Initial delay (s)','1u'), ('Toff','Off interval between pulses (s)','1u'),
  ('Tsecond','Second-pulse plateau (s)','1u'), ('Tr','Command rise time (s)','2n'),
  ('Tf','Command fall time (s)','2n'), ('Ttail','Observation after final turn-off (s)','2u'),
  ('Maxstep','Maximum simulation step (s)','100p'),
  ('Wpre','Energy window before command edge (s)','20n'),
  ('Wpost','Energy window after command edge (s)','100n')],
 'DC link & layout': [
  ('Cin','DC-link input capacitance (F)','470u'), ('ESR','DC-link capacitor ESR (ohm)','5m'),
  ('ESL','DC-link capacitor ESL (H)','200p'), ('Lloop','External layout loop inductance (H)','5n'),
  ('Rloop','Layout loop resistance (ohm)','5m'),
  ('Rcharge','Supply charging / isolation resistance (ohm)','10'),
  ('CSI','Common-source inductance per device (H)','100p')],
 'Gate drive': [
  ('Von','Low-side on voltage (V)','5'), ('Voff','Off voltage, both devices (V)','-1'),
  ('Rg_on','External turn-on gate resistance (ohm)','1'),
  ('Rg_off','External turn-off gate resistance (ohm)','0'),
  ('RGD_PU','Driver pull-up resistance (ohm)','0.7'),
  ('RGD_PD','Driver pull-down resistance (ohm)','0.4'),
  ('Rg_HS','HS off-state resistance: external + driver (ohm)','0.4')]
}
GROUPS['DC link & layout'] = [row for row in GROUPS['DC link & layout'] if row[0] not in {'Lloop','Rloop','CSI'}] + parasitics.DECOUPLING
GROUPS.update(parasitics.GROUPS)
GROUPS['Half-bridge PWM'] = half_bridge.GROUP
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
    values=normalize_settings(values)
    p = {k:number(values[k]) for k in DEFAULTS}
    nonnegative = {'Rload','ESR','ESL','Lloop','Rloop','CSI','Rg_on','Rg_off','RGD_PU','RGD_PD','Tdelay','Icond','DutyLS','DutyHS'}
    nonnegative |= set(parasitics.NEW_DEFAULTS)-{'Refined'}
    special = {'Tj','Voff','AutoT1','Refined','Mode','Iinitial'}
    for k,v in p.items():
        if k in special: continue
        if (k in nonnegative and v<0) or (k not in nonnegative and v<=0):
            raise ValueError(f'{k} must be {"nonnegative" if k in nonnegative else "positive"}.')
    if p['Refined'] not in (0,1):raise ValueError('Refined must be 0 (legacy) or 1 (refined).')
    if any(not 0<=p[k]<=1 for k in parasitics.FRACTIONS):raise ValueError('Power-path fractions must be between 0 and 1.')
    if p['LplusFrac']+p['LreturnFrac']>1 or p['RplusFrac']+p['RreturnFrac']>1:raise ValueError('Positive-feed and return fractions must sum to at most 1; the remainder is the switch-node path.')
    if p['AutoT1'] not in (0,1): raise ValueError('AutoT1 must be 0 or 1.')
    if not p['Vin'] < p['Vlimit'] <= 120: raise ValueError('Choose a Vds ceiling above the DC supply and at most 120 V. Prefer 100 V with margin.')
    if p['Tj']<=-273.15: raise ValueError('Temperature must exceed absolute zero.')
    if p['Von']<=p['Voff']: raise ValueError('On voltage must exceed off voltage.')
    if p['Rg_on']+p['RGD_PU']<=0 or p['Rg_off']+p['RGD_PD']<=0:
        raise ValueError('Total on/off gate resistances must be positive.')
    if p['Mode']:
        return half_bridge.timing(p)
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
    if p['Refined']:
        parts=parasitics.refine_parts(parts)
        if p['Cdecap']>0:parts+=parasitics.decoupling_parts()
    if p['Mode']:return half_bridge.build(parts,p)
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
      '.meas tran Vgs_LS_peak MAX V(gl,sl)',
      '.meas tran Vgs_LS_min MIN V(gl,sl)',
      '.meas tran Rail_peak MAX V(rail)',
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
    if p['Refined']:
        directives += ['.save V(pgnd) V(hs_ref) V(lret) V(hret) I(Llayout) I(Lmid) I(Lreturn) I(LgateLS) I(LgateHS)',
                       '.meas tran Local_bus_peak MAX V(rail,pgnd)', '.meas tran Local_bus_min MIN V(rail,pgnd)', '.meas tran Return_peak MAX V(pgnd)', '.meas tran Return_min MIN V(pgnd)']
    return parts,directives,p

def netlist(values):
    parts,directives,_=circuit(values)
    return '\n'.join(['* EPC2361 synchronous RL half-bridge' if validate(values)['Mode'] else '* EPC2361 low-side DPT; upper GaN held off']+
      [' '.join([name]+nodes+[value]+([extra] if extra else [])) for kind,name,nodes,value,extra in parts]+directives+['.end',''])

def schematic(values):
    parts,directives,_=circuit(values)
    # Each element has explicit labeled terminals; identical labels connect across sections.
    positions=[(96+(i%7)*320,112+(i//7)*320) for i in range(len(parts))]
    height=max(2100,480+((len(parts)+6)//7)*320,len(directives)*40+100)
    lines=['Version 4',f'SHEET 1 4400 {height}',
      'TEXT 48 0 Left 3 ;EPC2361 - named terminals connect electrically',
      'TEXT 48 40 Left 2 ;'+('REFINED: distributed power paths and private gate loops.' if validate(values)['Refined'] else 'LEGACY: original lumped power path.'),
      'TEXT 48 72 Left 2 ;Re-export from the GUI after changing model mode or enabling local decoupling.']
    for (kind,name,nodes,value,extra),(x,y) in zip(parts,positions):
        lines.append(f'SYMBOL {kind} {x} {y} R0')
        if name=='Vcmd':
            lines += ['WINDOW 3 24 108 Left 0']
        symbol_name=name[1:] if kind=='EPCGaN' and name.startswith('X') else name
        lines += [f'SYMATTR InstName {symbol_name}',f'SYMATTR Value {value}']
        if extra: lines.append(f'SYMATTR SpiceLine {extra}')
        if kind=='EPCGaN': lines.append('SYMATTR ModelFile .\\EPCGaNLibrary.lib')
        pins={'res':[(16,16),(16,96)],'ind':[(16,16),(16,96)],
              'cap':[(16,0),(16,64)],'voltage':[(0,16),(0,96)],
              'sw':[(0,16),(0,96),(-48,80),(-48,32)],
              'EPCGaN':[(0,0),(80,-96),(80,32)]}[kind]
        for node,(dx,dy) in zip(nodes,pins): lines.append(f'FLAG {x+dx} {y+dy} {node}')
    for i,d in enumerate(directives): lines.append(f'TEXT 2440 {32+i*40} Left 2 !{d}')
    return '\n'.join(lines)+'\n'

def export(values,path):
    values=normalize_settings(values)
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
    if isinstance(data,dict):data={k:v for k,v in data.items() if k not in {'Icond','DutyLS','DutyHS','RdsLS','RdsHS'}}
    if not isinstance(data,dict) or set(data)-set(DEFAULTS) or set(DEFAULTS)-set(data)-set(parasitics.NEW_DEFAULTS)-set(half_bridge.DEFAULTS)-{'Fsw','Vlimit','Icond','DutyLS','DutyHS','RdsLS','RdsHS'}:
        raise ValueError('Select a settings file from this DPT editor.')
    merged=dict(DEFAULTS,**data)
    if 'Refined' not in data:
        merged.update({k:v for k,v in parasitics.LEGACY_DEFAULTS.items() if k not in data})
    return merged

def conduction_loss(values):
    return _conduction_loss(values,number)

def parse_measurements(content):
    return {k.lower():float(v) for k,v in re.findall(r'^(\w+):[^\r\n]*?=([-+\d.eE]+)',content,re.M)}

def result_summary(content,values,raw_path=None):
    m=parse_measurements(content)
    if number(values.get('Mode','0')):
        p=validate(values);rows,notes=half_bridge.summary(m,p)
        if raw_path is not None:
            try:rows.extend(half_bridge.rates(raw_path,p))
            except (OSError,ValueError,KeyError,ImportError) as exc:rows.append(('PWM rates','Unavailable: '+str(exc),''))
        if raw_path is not None:
            try:
                from half_bridge_losses import analyze
                loss_rows,loss_notes,loss_data=analyze(raw_path,p);rows.extend(loss_rows);notes+='\n'+loss_notes
                Path(raw_path).with_suffix('.losses.json').write_text(json.dumps(loss_data,indent=2),encoding='utf-8')
            except (OSError,ValueError,KeyError,ImportError) as exc:rows.append(('Half-bridge losses','Unavailable; rerun with new GUI: '+str(exc),''))
        notes+=' Rates use the penultimate PWM cycle, signed 10-90% transitions within Wpost after each command edge. ZVS or pre-existing reverse conduction may produce no complete transition; this is not zero slew rate.'
        return rows,notes
    frequency=number(values['Fsw'])
    rows=[]
    for key,label,unit,scale in [
        ('i_first_off','Load current at first turn-off','A',1),
        ('i_second_on','Load current at second turn-on','A',1),
        ('vds_peak','Low-side DUT maximum Vds','V',1),
        ('vds_hs_peak','High-side maximum Vds','V',1),
        ('vds_hs_min','High-side minimum Vds','V',1),
        ('vgs_ls_peak','Low-side maximum Vgs','V',1),
        ('vgs_ls_min','Low-side minimum Vgs','V',1),
        ('rail_peak','Local rail maximum voltage','V',1),
        ('return_peak','Bridge return maximum voltage','V',1),
        ('return_min','Bridge return minimum voltage','V',1),
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
    if raw_path is not None:
        try:
            from dpt_rates import measure
            rows.extend(measure(raw_path,validate(values)))
        except (OSError,ValueError,KeyError,ImportError) as exc:
            rows.append(('DUT switching rates','Unavailable: '+str(exc),'') )
    else:
        rows.append(('DUT switching rates','Unavailable: waveform file required',''))
    limit=number(values.get('Vlimit','100'))
    peak=max(m.get('vds_peak',float('nan')),m.get('vds_hs_peak',float('nan')))
    margin=limit-peak
    voltage_note=f'Vds ceiling {limit:g} V: worst peak {peak:.3f} V; margin {margin:.3f} V. '+('Exceeded.' if margin<0 else 'Within ceiling for this simulation only.')+'\n'
    notes=voltage_note+'Psw = (Eon + Eoff) x Fsw. Primary pair: Eon2 + Eoff1, at similar load current. Eoff2 is at a higher current. Frequency scales the loss estimate; it does not repeat the DPT pulses.\nSigned integration-window energies include capacitive/ringing energy. These are DUT-only estimates, excluding conduction, gate-drive and high-side losses.'
    notes+='\nRates: signed 10-90% averages, voltage referenced to Vin and current to load current at each edge. Uses the first completed directed transition after the command, within Wpost; ringing is not a peak derivative. Missing crossings show Unavailable.'
    notes+='\nEnergy depends on integration bounds and timestep; check convergence before using the estimate.'
    if m.get('vds_hs_peak',0)>120 or m.get('vds_peak',0)>120:
        notes+='\nSimulated Vds exceeds EPC2361 120 V repetitive-transient rating (rating applies only at <=1% duty). The model does not establish survival.'
    if any(m.get(k,0)>6 for k in ('vgs_ls_peak','vgs_hs_peak')) or any(m.get(k,0)<-4 for k in ('vgs_ls_min','vgs_hs_min')):
        notes+='\nA measured Vgs exceeds the EPC2361 +6/-4 V absolute gate limits.'
    notes+='\nParasitic model: '+('refined, using entered PCB assumptions.' if number(values.get('Refined','0')) else 'legacy lumped layout.')
    if negative:notes+='\nA negative event energy prevents a meaningful dissipative-loss estimate; inspect the waveforms and integration bounds.'
    return rows,notes

class App(tk.Tk):
    def __init__(self,mode=0):
        super().__init__()
        self.fixed_mode=int(mode)
        self.title('EPC GaN | Half-bridge RL' if self.fixed_mode else 'EPC GaN | Double pulse test')
        self.geometry('1100x900'); self.minsize(950,780)
        self.events=queue.Queue(); self.running=False
        frame=ttk.Frame(self,padding=18); frame.pack(fill='both',expand=True)
        ttk.Label(frame,text=('Synchronous half-bridge RL' if self.fixed_mode else 'Double pulse test'),font=('Segoe UI',22,'bold')).pack(anchor='w')
        ttk.Label(frame,text=('EPC2361 | complementary PWM | RL load | film and ceramic DC link' if self.fixed_mode else 'EPC2361 | low-side DUT | upper device held off')).pack(anchor='w',pady=(3,12))
        tabs=ttk.Notebook(frame); tabs.pack(fill='both',expand=True);self.main_tabs=tabs
        self.vars={k:tk.StringVar(value=v) for k,v in DEFAULTS.items()}
        self.vars['Mode'].set(str(self.fixed_mode))
        for title,rows in GROUPS.items():
            if not self.fixed_mode and title=='Half-bridge PWM':continue
            rows=[r for r in rows if r[0]!='Mode' and not (self.fixed_mode and r[0] in {'Itest','AutoT1','Tcharge','Toff','Tsecond','Ttail','Rg_HS'})]
            if not rows:continue
            holder=ttk.Frame(tabs);tabs.add(holder,text=title)
            scroll=ttk.Scrollbar(holder,orient='vertical');scroll.pack(side='right',fill='y')
            area=tk.Canvas(holder,highlightthickness=0,height=320,yscrollcommand=scroll.set);area.pack(side='left',fill='both',expand=True);scroll.configure(command=area.yview)
            page=ttk.Frame(area,padding=16);window=area.create_window((0,0),window=page,anchor='nw')
            page.bind('<Configure>',lambda e,a=area:a.configure(scrollregion=a.bbox('all')))
            area.bind('<Configure>',lambda e,a=area,w=window:a.itemconfigure(w,width=e.width))
            page.columnconfigure(1,weight=1)
            for i,(key,label,default) in enumerate(rows):
                if self.fixed_mode and key=='Fsw':label='PWM switching frequency (Hz)'
                if self.fixed_mode and key=='Von':label='On voltage, both devices (V)'
                ttk.Label(page,text=label).grid(row=i,column=0,sticky='w',pady=8)
                v=tk.StringVar(value=default); self.vars[key]=v
                ttk.Entry(page,textvariable=v,width=24).grid(row=i,column=1,sticky='ew',padx=(24,0))
                v.trace_add('write',self.preview)
            if title in parasitics.NOTES:
                ttk.Label(page,text=parasitics.NOTES[title],wraplength=860).grid(row=len(rows),column=0,columnspan=2,sticky='w',pady=10)
            if title=='Half-bridge PWM':
                ttk.Button(page,text='Load 75 V RL + film/ceramic preset',command=self.load_pwm).grid(row=len(rows),column=0,columnspan=2,sticky='w',pady=8)
                ttk.Label(page,text='Mode 1 uses Fsw as actual PWM frequency. RL connects switch node to bridge return. Rg on/off applies to both devices. Ceramic bank uses Cdecap/ESRdecap/ESLdecap on DC link tab. Values are effective bank assumptions; see HALF-BRIDGE-RL.md.',wraplength=820).grid(row=len(rows)+1,column=0,columnspan=2,sticky='w')
            if title=='Power parasitics':
                ttk.Button(page,text='Apply illustrative parasitic starting values',command=self.apply_parasitics).grid(row=len(rows)+1,column=0,columnspan=2,sticky='w',pady=6)
                ttk.Button(page,text='Split layout 50/50 (keep other settings)',command=self.apply_symmetric_layout).grid(row=len(rows)+2,column=0,columnspan=2,sticky='w',pady=6)
        diagram_page=ttk.Frame(tabs)
        tabs.add(diagram_page,text='Setup schematic')
        self.diagram=SetupDiagram(diagram_page,self.values)
        self.diagram.pack(fill='both',expand=True)
        self.results_page=ttk.Frame(tabs);tabs.add(self.results_page,text='Results')
        ttk.Label(self.results_page,text='Click Run simulation. Measurements will appear here automatically.',padding=20).pack(anchor='w')
        self.canvas=tk.Canvas(frame,height=94,bg='#f0f4f8',highlightthickness=0)
        self.canvas.pack(fill='x',pady=(12,4))
        self.summary=tk.StringVar(); ttk.Label(frame,textvariable=self.summary,wraplength=950).pack(anchor='w')
        ttk.Label(frame,text='Input capacitance = DC-link Cin. Device capacitances remain in the EPC model.\nSPICE units: u=micro, n=nano, p=pico, m=milli, Meg=mega. Results show signed window energies in uJ and estimated DUT switching loss in W.',wraplength=950).pack(anchor='w',pady=8)
        self.exe=tk.StringVar(value=find_ltspice())
        ex=ttk.Frame(frame); ex.pack(fill='x')
        ttk.Label(ex,text='LTspice:').pack(side='left'); ttk.Entry(ex,textvariable=self.exe).pack(side='left',fill='x',expand=True,padx=8)
        ttk.Button(ex,text='Browse...',command=self.browse).pack(side='right')
        actions=ttk.Frame(frame); actions.pack(fill='x',pady=12)
        for label,fn in [('Load settings',self.load),('Defaults',self.reset),(('75 V RL preset' if self.fixed_mode else '75 V / 45 A fast preset'),(self.load_pwm if self.fixed_mode else self.load_75_50)),('Save setup',self.save),('Save + open',lambda:self.save(True)),('Run simulation',self.run)]:
            ttk.Button(actions,text=label,command=fn).pack(side='left',padx=(0,8))
        self.status=tk.StringVar(value='Ready. First-pulse current is an estimate; use measured current from the simulation.')
        ttk.Label(frame,textvariable=self.status,wraplength=950).pack(anchor='w')
        if self.fixed_mode:self.load_pwm()
        self.preview(); self.poll_id=self.after(200,self.poll)

    def destroy(self):
        if hasattr(self,'poll_id'):
            self.after_cancel(self.poll_id)
        super().destroy()

    def values(self):
        values={k:v.get().strip() for k,v in self.vars.items()};values['Mode']=str(self.fixed_mode);return values
    def preview(self,*_):
        if not hasattr(self,'canvas'): return
        self.canvas.delete('all')
        try:
            p=validate(self.values())
            if p['Mode']:
                self.diagram.redraw()
                self.summary.set(f'PWM: {p["Fsw"]/1e3:g} kHz | Duty {p["Duty"]:g} | Dead time {p["Deadtime"]*1e9:g} ns | Duration {p["Stop"]*1e6:g} us | Ideal mean current approx. {p["Vin"]*p["Duty"]/(p["Rout"]+p["Rload"]):.2f} A')
                for high,color,y in [(True,'#cc6a16',10),(False,'#166caa',48)]:
                    points=half_bridge.commands(p,high)
                    pts=[(t,v) for t,v in points if t<=p['Tdelay']+2/p['Fsw']]
                    self.canvas.create_line(*[z for t,v in pts for z in (30+820*t/(p['Tdelay']+2/p['Fsw']),y+25-v*4)],fill=color,width=2)
                return
            self.diagram.redraw()
            self.summary.set(f'First pulse: {p["T1"]*1e6:.3f} us | Gap: {p["Toff"]*1e6:.3f} us | Second pulse: {p["Tsecond"]*1e6:.3f} us | Total: {p["Stop"]*1e6:.3f} us\nIdeal first turn-off current: {p["Vin"]*p["T1"]/p["Lload"]:.2f} A. Finite capacitance, resistance and freewheeling change actual current.')
            ts=[0,p['Tdelay'],p['Tdelay']+p['Tr'],p['A'],p['A']+p['Tf'],p['B'],p['B']+p['Tr'],p['C'],p['C']+p['Tf'],p['Stop']]
            ys=[70,70,30,30,70,70,30,30,70,70]
            coords=[z for t,y in zip(ts,ys) for z in (30+850*t/p['Stop'],y)]
            self.canvas.create_line(*coords,fill='#166caa',width=3)
            self.canvas.create_text(30,12,text='Gate command: charge pulse → freewheel → measurement pulse',anchor='w',fill='#263e53')
        except (ValueError,KeyError) as exc:
            self.summary.set(str(exc))
            self.diagram.redraw()
    def apply_symmetric_layout(self):
        self.vars['Refined'].set('1')
        for key in parasitics.FRACTIONS:self.vars[key].set('0.5')
        self.status.set('Layout L/R split 50% upper feed / 50% lower return; total L/R and gate settings preserved. DPT voltage stress can still differ.')

    def apply_parasitics(self):
        for k,v in parasitics.NEW_DEFAULTS.items():self.vars[k].set(v)
        self.status.set('Refined PCB model enabled with illustrative starting values. Existing operating point, total Lloop/Rloop and CSI retained; local decoupling disabled until specified.')

    def reset(self):
        if self.fixed_mode:self.load_pwm();return
        for k,v in DEFAULTS.items(): self.vars[k].set(v)
    def load_pwm(self):
        try:
            data=normalize_settings(json.loads((BASE/'HalfBridge-75V-RL.json').read_text(encoding='utf-8')))
            validate(data)
            for k,v in data.items():self.vars[k].set(str(v))
            self.status.set('Synchronous RL preset loaded: film and ceramic banks enabled; 45 A initial current is a warm-start assumption.')
        except (OSError,ValueError) as exc:messagebox.showerror('Preset',str(exc))

    def load_75_50(self):
        try:
            data=normalize_settings(json.loads((BASE/'DPT-75V-45A-fast-negative.json').read_text(encoding='utf-8-sig')))
            validate(data)
            for k,v in data.items():self.vars[k].set(str(v))
            self.status.set('75 V / 45 A fast preset: +5/-1 V, external Rg 1/0 ohm. EPC reference uses 0 V off at 48 V/30 A; see FAST-PRESET-NOTES.md.')
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
            if int(number(data['Mode']))!=self.fixed_mode:raise ValueError('Open this setup in the other GUI (DPT or Half-bridge).')
            validate(data)
            for k,v in data.items():self.vars[k].set(str(v))
            self.status.set('Refined settings loaded.' if number(data['Refined']) else 'Legacy settings loaded unchanged. Use Power parasitics > Apply illustrative parasitic starting values to refine them.')
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
            self.running=True; self.status.set('Running simulation... The interface remains available.')
            def worker():
                try:
                    result=subprocess.run([exe,'-b',str(dest.with_suffix('.cir'))],cwd=dest.parent,capture_output=True,timeout=180)
                    log=dest.with_suffix('.log')
                    raw=log.read_bytes() if log.exists() else b''
                    content=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else ('utf-16-le' if b'\0' in raw[:100] else 'utf-8'),errors='replace')
                    if result.returncode or not dest.with_suffix('.raw').exists() or ('iload_avg:' if number(values.get('Mode','0')) else 'i_second_on:') not in content.lower():
                        raise ValueError('Simulation did not produce complete measurements.\n'+content+'\n'+result.stderr.decode(errors='replace'))
                    rows,notes=result_summary(content,values,dest.with_suffix('.raw'))
                    self.events.put((True,dest,content,rows,notes))
                except Exception as exc:self.events.put((False,dest,str(exc),[],''))
            threading.Thread(target=worker,daemon=True).start()
        except (OSError,ValueError) as exc:messagebox.showerror('Run DPT',str(exc))
    def show_results(self,ok,dest,content,rows,notes):
        self.running=False
        self.status.set(('Completed: ' if ok else 'Simulation or analysis failed: ')+str(dest.parent))
        for widget in self.results_page.winfo_children():widget.destroy()
        tabs=ttk.Notebook(self.results_page);tabs.pack(fill='both',expand=True,padx=8,pady=8)
        if ok:
            summary=ttk.Frame(tabs);tabs.add(summary,text='Measurements')
            tree=ttk.Treeview(summary,columns=('value','unit'),show='tree headings',height=13)
            tree.heading('#0',text='Measurement');tree.heading('value',text='Value');tree.heading('unit',text='Unit')
            tree.column('#0',width=540);tree.column('value',width=140,anchor='e');tree.column('unit',width=75)
            scroll=ttk.Scrollbar(summary,orient='vertical',command=tree.yview);tree.configure(yscrollcommand=scroll.set)
            scroll.pack(side='right',fill='y');tree.pack(side='left',fill='both',expand=True)
            for label,value,unit in rows:tree.insert('', 'end',text=label,values=(value,unit))
            method=ttk.Frame(tabs);tabs.add(method,text='Measurement definitions')
            explanation=tk.Text(method,wrap='word',padx=12,pady=12);explanation.pack(fill='both',expand=True);explanation.insert('1.0',notes);explanation.configure(state='disabled')
            ttk.Button(self.results_page,text='Open waveforms in LTspice',command=lambda:subprocess.Popen([self.exe.get(),str(dest.with_suffix('.raw'))],cwd=dest.parent)).pack(pady=4)
        logpage=ttk.Frame(tabs);tabs.add(logpage,text='Simulation log')
        box=tk.Text(logpage,wrap='word',padx=12,pady=12);box.pack(fill='both',expand=True);box.insert('1.0',content);box.configure(state='disabled')
        self.main_tabs.select(self.results_page)

    def poll(self):
        try:
            self.show_results(*self.events.get_nowait())
        except queue.Empty:pass
        except Exception as exc:
            self.running=False;self.status.set('Could not display results: '+str(exc))
        finally:
            self.poll_id=self.after(200,self.poll)

if __name__=='__main__':App().mainloop()

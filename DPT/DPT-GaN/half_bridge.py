"""Synchronous buck-style half bridge with RL load and explicit capacitor banks."""
import math
GROUP=[('LossVth','Effective dead-time Vgs threshold (V)','1.5'),('Mode','Mode: 0=DPT, 1=synchronous RL half-bridge','0'),('Duty','High-side duty ratio (0..1)','0.5'),('Deadtime','Both-off interval between gate ramps (s)','10n'),('Cycles','Number of PWM cycles','20'),('Rout','External series load resistance (ohm)','0.8'),('Iinitial','Initial load current: 0=cold start (A)','45'),('Cfilm','Film bank capacitance (F)','22u'),('ESRfilm','Film bank ESR (ohm)','5m'),('ESLfilm','Film bank + connection ESL (H)','3n')]
DEFAULTS={k:v for k,_,v in GROUP}

def timing(p):
    if p['Mode'] not in (0,1):raise ValueError('Mode must be 0 or 1.')
    if not 0<p['Duty']<1:raise ValueError('PWM duty must be between 0 and 1.')
    if p['Cycles']!=int(p['Cycles']) or not 2<=p['Cycles']<=2000:raise ValueError('Choose 2..2000 PWM cycles.')
    period=1/p['Fsw']
    if min(p['Duty'],1-p['Duty'])*period<=p['Deadtime']+p['Tr']+p['Tf']:raise ValueError('PWM interval too short for dead time and gate ramps.')
    if not p['Refined']:raise ValueError('PWM requires refined parasitics.')
    p['Stop']=p['Tdelay']+p['Cycles']*period
    if p['Maxstep']>min(p['Tr'],p['Tf'])/2 or p['Stop']/p['Maxstep']>5e6:raise ValueError('Adjust PWM duration or maximum step (at most half the command edge, at most 5 million steps).')
    return p

def commands(p,high):
    points=[(0,0)]
    for n in range(int(p['Cycles'])):
        start=p['Tdelay']+n/p['Fsw'];mid=start+p['Duty']/p['Fsw'];end=start+1/p['Fsw']
        a,b=(start+p['Deadtime'],mid-p['Tf']) if high else (mid+p['Deadtime'],end-p['Tf'])
        points += [(a,0),(a+p['Tr'],5),(b,5),(b+p['Tf'],0)]
    return points

def build(parts,p):
    out=[]
    for kind,name,nodes,value,extra in parts:
        if name in {'Vhs','Rhs'}:continue
        if name=='Lload':nodes=['sw','load_r'];extra='Rser={Rload}'
        if name=='Vcmd':value='PWL('+' '.join(f'{t:.12g} {v}' for t,v in commands(p,False))+')'
        out.append((kind,name,nodes,value,extra))
    out += [('res','Rout',['load_r','pgnd'],'{Rout}',''),
      ('voltage','VcmdHS',['cmdhs','0'],'PWL('+' '.join(f'{t:.12g} {v}' for t,v in commands(p,True))+')',''),
      ('voltage','VhsOn',['h_on','hret'],'{Von}',''),('voltage','VhsOff',['h_off','hret'],'{Voff}',''),
      ('sw','Shup',['h_on','h_pu','cmdhs','0'],'DRV_ON',''),('sw','Shdown',['h_off','h_pd','cmdhs','0'],'DRV_OFF',''),
      ('res','Rhup',['h_pu','hdrive'],'{Rg_on+RGD_PU}',''),('res','Rhdown',['h_pd','hdrive'],'{Rg_off+RGD_PD}',''),
      ('res','Rfilm',['bus','film_l'],'{ESRfilm}',''),('ind','Lfilm',['film_l','film_c'],'{max(ESLfilm,1e-15)}','Rser=0'),('cap','Cfilm',['film_c','0'],'{Cfilm}','')]
    directives=['.param '+ ' '.join(f'{k}={v:.12g}' for k,v in p.items()),'.include ".\\EPCGaNLibrary.lib"','.temp {Tj}',
      '.model DRV_ON SW(Ron=1m Roff=1G Vt=2.5 Vh=0)','.model DRV_OFF SW(Ron=1G Roff=1m Vt=2.5 Vh=0)',
      '.ic I(Lload)={Iinitial}', '.tran 0 {Stop} 0 {Maxstep}', '.options plotwinsize=0',
      '.save V(cmd) V(cmdhs) V(gl,sl) V(gh,sh) V(drain,sl) V(rail,sh) V(bus) V(rail) V(pgnd) I(Lload) I(Vsense) I(Lsh) I(Cin) I(Cfilm)',
      '.meas tran Vds_peak MAX V(drain,sl)', '.meas tran Vds_HS_peak MAX V(rail,sh)',
      '.meas tran Vgs_LS_peak MAX V(gl,sl)', '.meas tran Vgs_LS_min MIN V(gl,sl)',
      '.meas tran Vgs_HS_peak MAX V(gh,sh)', '.meas tran Vgs_HS_min MIN V(gh,sh)',
      '.meas tran Local_bus_peak MAX V(rail,pgnd)', '.meas tran Local_bus_min MIN V(rail,pgnd)']
    for name,expr,op in [('Iload_avg','I(Lload)','AVG'),('Iload_min','I(Lload)','MIN'),('Iload_max','I(Lload)','MAX'),('Ibulk_rms','I(Cin)','RMS'),('Ifilm_rms','I(Cfilm)','RMS'),('Bus_ripple','V(rail,pgnd)','PP')]:
        directives.append(f'.meas tran {name} {op} {expr} FROM={{Stop-2/Fsw}} TO={{Stop}}')
    if p['Cdecap']>0:directives+=['.save I(Cdecap)','.meas tran Iceramic_rms RMS I(Cdecap) FROM={Stop-2/Fsw} TO={Stop}']
    for device in ('HS','DUT'):
        directives.append('.save '+' '.join([f'V({device}:drain)',f'V({device}:source)',f'V({device}:gate)',f'I({device}:bswitch)',f'I({device}:rd)',f'I({device}:rs)']))
    return out,directives,p

def summary(m,p):
    specs=[('vds_peak','Low-side maximum Vds','V'),('vds_hs_peak','High-side maximum Vds','V'),('vgs_ls_peak','Low-side maximum Vgs','V'),('vgs_ls_min','Low-side minimum Vgs','V'),('vgs_hs_peak','High-side maximum Vgs','V'),('vgs_hs_min','High-side minimum Vgs','V'),('local_bus_peak','Local DC-link peak','V'),('local_bus_min','Local DC-link minimum','V'),('bus_ripple','Local DC-link ripple, final 2 cycles','Vpp'),('iload_avg','Mean RL current, final 2 cycles','A'),('iload_min','Minimum RL current, final 2 cycles','A'),('iload_max','Maximum RL current, final 2 cycles','A'),('ibulk_rms','Bulk capacitor RMS current, final 2 cycles','A'),('ifilm_rms','Film capacitor RMS current, final 2 cycles','A'),('iceramic_rms','Ceramic bank RMS current, final 2 cycles','A')]
    rows=[(label,format(m[key],'.6g') if key in m else 'Unavailable',unit) for key,label,unit in specs]
    notes='Synchronous RL half-bridge. Rg on/off and driver resistances apply to both devices; Rg_HS is DPT-only. Full-run voltage extrema; capacitor RMS/ripple and load statistics cover the last two cycles. Initial current is an explicit warm-start assumption, not proof of steady state. DPT energy measurements are not applied to PWM.'
    if max(m.get('vds_peak',0),m.get('vds_hs_peak',0))>p['Vlimit']:notes+=' Vds design ceiling exceeded.'
    if max(m.get('vgs_ls_peak',0),m.get('vgs_hs_peak',0))>6 or min(m.get('vgs_ls_min',0),m.get('vgs_hs_min',0))< -4:notes+=' Vgs absolute limit exceeded.'
    return rows,notes

def draw(canvas,v):
    canvas.delete('all');scale=min(max(canvas.winfo_width(),100)/1050,max(canvas.winfo_height(),100)/560)
    def txt(x,y,s):canvas.create_text(x*scale,y*scale,text=s,font=('Segoe UI',max(7,int(10*scale))))
    def line(*a):canvas.create_line(*[x*scale for x in a],width=2)
    def box(x,y,s):canvas.create_rectangle((x-65)*scale,(y-24)*scale,(x+65)*scale,(y+24)*scale,fill='white');txt(x,y,s)
    txt(520,22,'Synchronous half-bridge: complementary source-referenced drives, series RL load')
    line(70,100,950,100);line(70,450,950,450)
    for x,s in [(80,v['Vin']+' V source\n+ Rcharge'),(250,'Bulk Cin\nESR + ESL'),(420,'Film Cfilm\nESR + ESL')]:line(x,100,x,180);box(x,205,s);line(x,230,x,450)
    box(555,100,'Lplus / Rplus');box(555,450,'Lreturn / Rreturn')
    line(650,100,650,180);box(650,205,'Ceramic Cdecap\nESR + ESL');line(650,230,650,450)
    line(800,100,800,155);box(800,180,'Upper GaN');line(800,205,800,265);txt(890,235,'CSI + Lmid')
    line(800,265,800,315);box(800,340,'Lower GaN');line(800,365,800,450);txt(880,404,'CSI')
    line(800,265,950,265,950,300);box(950,325,'Lload + Rload');line(950,350,950,375);box(950,400,'Rout');line(950,425,950,450)
    txt(420,510,'Both gate paths: driver resistance + external Rg + forward/return L and R.\nShared-source CSI remains separate. Bulk/film are upstream; ceramics are at the bridge.\nExported .asc includes every component and node. Drawing is simplified.')

def rates(path,p):
    import numpy as np
    from datasheet_sweep import raw_read
    from dpt_rates import transition
    w={k.lower():v for k,v in raw_read(path).items()};t=w['time'];rows=[]
    def voltage(a,b):return w[f'v({a})']-w[f'v({b})']
    for name,high,v,i in [('Upper',True,voltage('rail','sh'),w['i(lsh)']),('Lower',False,voltage('drain','sl'),w['i(vsense)'])]:
        period=1/p['Fsw'];start=p['Stop']-2*period
        on=start+(p['Deadtime'] if high else p['Duty']*period+p['Deadtime'])
        off=start+(p['Duty']*period if high else period)-p['Tf']
        for label,edge,is_on in [('on',on,True),('off',off,False)]:
            ref=float(np.interp(edge,t,w['i(lload)']))*(1 if high else -1)
            for q,y,reference,unit in [('dv/dt',v,p['Vin'],'V/ns'),('di/dt',i,ref,'A/ns')]:
                rising=(q=='di/dt')==is_on
                a,b=(.1*reference,.9*reference) if rising else (.9*reference,.1*reference)
                result=transition(t,y,a,b,edge,edge+min(p['Wpost'],.4*period))
                rows.append((f'{name} {label} {q} (10-90%)',format(result[0],'.6g') if result else 'No complete transition',unit))
    return rows

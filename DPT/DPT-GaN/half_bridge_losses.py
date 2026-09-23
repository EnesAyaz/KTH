"""Exclusive waveform loss partition using EPC2361 internal dissipative elements."""
import numpy as np
from datasheet_sweep import raw_read
from half_bridge import commands

def analyze(path,p):
    w={k.lower():v for k,v in raw_read(path).items()};t=w['time'];period=1/p['Fsw'];cycles=min(3,int(p['Cycles'])-1)
    start=p['Tdelay']+(p['Cycles']-cycles-1+.25)*period;stop=start+cycles*period
    if t[-1]<stop:raise ValueError('Incomplete waveform for loss averaging interval.')
    # Include interpolated interval boundaries and use midpoint classification of each trapezoid.
    inside=t[(t>start)&(t<stop)];tt=np.r_[start,inside,stop];dt=np.diff(tt);tm=(tt[:-1]+tt[1:])/2
    def sample(key):return np.interp(tt,t,w[key.lower()])
    def mid(x):return (x[:-1]+x[1:])/2
    threshold=p.get('LossVth',1.5)
    gates={dev:mid(sample(f'V({dev}:gate)')-sample(f'V({dev}:source)')) for dev in ('HS','DUT')}
    dead=(gates['HS']<threshold)&(gates['DUT']<threshold)
    output={};rows=[]
    for name,dev,high,drain,source in [('Upper','HS',True,'rail','sh'),('Lower','DUT',False,'drain','sl')]:
        vd=sample(f'V({dev}:drain)');vs=sample(f'V({dev}:source)');ich=sample(f'I({dev}:bswitch)')
        power=(vd-vs)*ich+(sample(f'V({drain})')-vd)*sample(f'I({dev}:rd)')+(sample(f'V({source})')-vs)*sample(f'I({dev}:rs)')
        if not np.all(np.isfinite(power)):raise ValueError('Nonfinite intrinsic dissipation.')
        energy=mid(power)*dt
        on=np.zeros(len(tm),bool);off=on.copy()
        for n in range(int(p['Cycles'])):
            base=p['Tdelay']+n*period
            a=base+(p['Deadtime'] if high else p['Duty']*period+p['Deadtime'])
            b=base+(p['Duty']*period if high else period)-p['Tf']
            on|=(tm>=a-p['Wpre'])&(tm<a+p['Wpost'])
            off|=(tm>=b-p['Wpre'])&(tm<b+p['Wpost'])
        if np.any(on&off):raise ValueError('Loss windows overlap: reduce Wpre/Wpost.')
        reverse=dead&(mid(vd-vs)<0)&(mid(ich)<0)
        masks={'deadtime':reverse,'on':on&~reverse,'off':off&~reverse}
        used=reverse|on|off
        masks['conduction']=(gates[dev]>=threshold)&~used
        masks['other']=~(used|masks['conduction'])
        powers={k:float(np.sum(energy[mask])/(stop-start)) for k,mask in masks.items()}
        total=float(np.sum(energy)/(stop-start));assert abs(sum(powers.values())-total)<1e-8*max(1,abs(total))
        output[name]={'Eon_uJ':powers['on']/p['Fsw']*1e6,'Eoff_uJ':powers['off']/p['Fsw']*1e6,**{k+'_W':v for k,v in powers.items()},'total_W':total}
        for key,label,unit in [('Eon_uJ','Eon, switching window','uJ'),('Eoff_uJ','Eoff, switching window','uJ'),('on_W','Pon = Eon x Fsw','W'),('off_W','Poff = Eoff x Fsw','W'),('conduction_W','On-state conduction, outside switching windows','W'),('deadtime_W','Reverse conduction during effective dead time','W'),('other_W','Other / off-state dissipation','W'),('total_W','Total channel + drain/source resistance loss','W')]:
            rows.append((name+' '+label,format(output[name][key],'.6g'),unit))
    output['interval']={'start_s':start,'stop_s':stop,'cycles':cycles,'threshold_V':threshold}
    notes=f'Losses averaged over {cycles} complete interior PWM cycles. Integrates intrinsic channel + internal drain/source resistor dissipation, excluding ideal capacitor storage, gate/driver and PCB losses. Exclusive allocation: reverse conduction while BOTH internal Vgs < {threshold:g} V; then switching windows; then gate-on conduction; then other. Eon/Eoff include dissipation within Wpre/Wpost, including any on-state baseline there. Attribution is window/threshold dependent; totals are not. No extra Eoss term is added. Not a full thermal or steady-state qualification.'
    return rows,notes,output

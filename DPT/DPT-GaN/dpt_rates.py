"""Windowed, signed DUT 10-90% transition rates from LTspice terminal waveforms."""
import numpy as np
from datasheet_sweep import raw_read

def transition(t,y,a,b,start,stop):
    direction=1 if b>a else -1
    def cross(level):
        mask=(t[:-1]>=start)&(t[1:]<=stop)
        mask &= ((y[:-1]<level)&(y[1:]>=level)) if direction>0 else ((y[:-1]>level)&(y[1:]<=level))
        k=np.flatnonzero(mask)
        return t[k]+(level-y[k])*(t[k+1]-t[k])/(y[k+1]-y[k])
    starts,ends=cross(a),cross(b)
    for end in ends:
        before=starts[starts<end]
        if len(before):
            first=float(before[-1]);return (b-a)/(end-first)*1e-9,(end-first)*1e9
    return None

def measure(path,p):
    w={k.lower():v for k,v in raw_read(path).items()};t=w['time']
    v=w['v(drain,sl)'] if 'v(drain,sl)' in w else w['v(drain)']-w['v(sl)'];i=w['i(vsense)'];load=w['i(lload)']
    rows=[]
    for label,key,on in [('Turn-on 2','B',True),('Turn-off 1','A',False),('Turn-off 2','C',False)]:
        edge=p[key];iref=float(np.interp(edge,t,load));stop=edge+p['Wpost']
        for quantity,y,ref,unit in [('dv/dt',v,p['Vin'],'V/ns'),('di/dt',i,iref,'A/ns')]:
            rising=(quantity=='di/dt')==on
            a,b=(.1*ref,.9*ref) if rising else (.9*ref,.1*ref)
            result=transition(t,y,a,b,edge,stop) if ref>0 else None
            rows.append((f'DUT {label} {quantity} (10-90%)',format(result[0],'.6g') if result else 'Unavailable',unit))
    return rows

import spb_core as c, numpy as np, json
import sys
c.CAP_MODE["mode"]=sys.argv[1]
J=c.J; sp=np.array(J['speed_rpm'])
def an(mach,key,n):
    T=J['machines'][mach][key]['torque_Nm']; return float(np.interp(n,sp,T))
for p,key in ((4,'2p8'),(2,'2p4')):
    par=c.im_params(p)
    for n in (300,1000,2100,3000,4250,4500,6000):
        T,d=c.im_envelope(par,n)
        print(key,n,'sim',round(T,1),'an',round(an('IM',key,n),1), 'psi',round(d['psi'],4),'Bt',round(d['Bt'],2),'V',round(d['V'],1),'I',round(d['I'],1))

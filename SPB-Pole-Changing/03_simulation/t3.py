import spb_core as c, numpy as np
c.CAP_MODE["mode"]="an_caps"
mp=c.J['machine_parameters']['IM']
for p,key in ((4,'2p8'),(2,'2p4')):
    par=c.im_params(p); a=mp[key]
    print(key,'mine Lsig_s',par['Lsig_s'],'an',a['L_sigma_s_H'],'Lsig_r',par['Lsig_r'],a['L_sigma_r_H'],'Rr',par['Rr'],a['R_r_ohm'])
    for n in (1000,4500,6000):
        T0,_=c.im_envelope(par,n)
        q=dict(par); q['Lsig_s']=a['L_sigma_s_H']; q['Lsig_r']=a['L_sigma_r_H']; q['Rr']=a['R_r_ohm']
        T1,_=c.im_envelope(q,n)
        print('  ',n,'mine',round(T0,1),'with analyst leakage/Rr',round(T1,1))

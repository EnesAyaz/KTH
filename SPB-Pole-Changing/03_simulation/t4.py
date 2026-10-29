import spb_core as c, numpy as np, sync_model as s
J=c.J; sp=np.array(J['speed_rpm'])
def an(mach,key,n):
    return float(np.interp(n,sp,J['machines'][mach][key]['torque_Nm']))
pm=s.Sync('PMSM','2p8')
for n in (500,1000,2100,4250,4500,6000):
    T,d=pm.envelope(n); print('PMSM',n,round(T,1),'an',round(an('PMSM','2p8',n),1),round(d['I'],1),round(d['V'],1))
for mode,key in (('2p8','2p8'),('2p4','2p4')):
    w=s.Sync('WRSM',mode,tag='_gs4')
    for n in (500,1000,2100,4250,4500,6000):
        T,d=w.envelope(n); 
        print('WRSM',mode,n,round(T,1),'an freeId',round(an('WRSM_freeId',key,n),1),'Id0',round(an('WRSM_Id0',key,n),1),'If',round(d['If'],2),'id',round(d['id']),'iq',round(d['iq']))

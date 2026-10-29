import time; t=time.time()
import spb_core as c, numpy as np
print('SIG',c.SIG)
for p in (4,2):
    print(p,'Lm_fund',c.L_m_fund(p),'tot',c.L_mode_total(p),'Ldiff',c.L_diff(p),'Lslot',c.L_slot_mode(p),'Lend',c.L_END)
    im,ps,bt,by=c.mag_curve(p)
    print(' lin MEC L',ps[1]/im[1], 'at i=300A rms psi',np.interp(300,im,ps), 'Bt',np.interp(300,im,bt),'By',np.interp(300,im,by))
    par=c.im_params(p); print({k:(round(v,8) if isinstance(v,float) else v) for k,v in par.items()})
print(time.time()-t)

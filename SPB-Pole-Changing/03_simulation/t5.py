import spb_core as c, numpy as np
print('GEFF',c.GEFF,'AT',c.AT,'TIP',c.AT_TIP,'caps',c.B_TOOTH_CAP,c.B_YOKE_CAP,'mass',c.M_TEETH,c.M_YOKE,'RS',c.RS)
print('lambdas',c.slot_lambdas())
c.CAP_MODE['mode']='an_caps'
for p in (4,2):
    par=c.im_params(p)
    print(p,{k:(round(float(v),8)) for k,v in par.items()}, 'psi_max',c.psi_max(p),'Lm_lin',c.L_m_fund(p))
    for n in (1000,2100,4500):
        print('  ',n,round(c.im_envelope(par,n)[0],1))

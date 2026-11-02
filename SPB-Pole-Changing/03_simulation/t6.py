import math, numpy as np, spb_core as c, wrsm_model as w
G=c.GEOM["rotor_wrsm"]; kcs=c.GEOM["airgap"]["carter_stator"]
LB=c.VMAX/(c.IMAX*4*1200*c.RPM)
B0=G["B0_noload_T"]
for gm in (1.0,2.0,3.0,4.0,5.0,6.0):
    geff=gm*1e-3*kcs
    gs=geff/c.GEFF
    w.GS['v']=gs
    F=B0*geff/c.MU0
    rint=geff/G["interpolar_path_length_m"]
    kw_={'r_int':rint}
    def sp(mode,idv,iqv,If):
        return w.solve_point(mode,idv,iqv,If,rotor_kw=kw_)
    out={}
    for mode in ('2p8','2p4'):
        pd0,pq0,r0=sp(mode,0,0,1.0)
        pd1,_,_=sp(mode,-20,0,1.0); _,pq2,_=sp(mode,0,20,1.0)
        out[mode]=(pd0/c.SQ2,(pd0-pd1)/-20*1,pq2/20, r0['By'].max())
    Rro=c.R-gm*1e-3
    rm=Rro-0.0275
    wsl=2*math.pi*rm/8-G['pole_body_width_m']
    Acu=0.5*wsl*G['field_slot_depth_m']/2
    J=F/Acu/1e6
    P=8*G['rho_cu_120C_ohm_m']*G['mean_turn_length_m']*F**2/Acu
    print(gm,'geff',round(geff*1e3,2),'F',round(F),'Acu mm2',round(Acu*1e6),'J',round(J,1),'Pf kW',round(P/1e3,2),
     '| 2p8 psi',round(out['2p8'][0],4),'Ld pu',round(out['2p8'][1]/LB,2),'Lq pu',round(out['2p8'][2]/LB,2),'| 2p4 psi',round(out['2p4'][0],4),'Ld',round(out['2p4'][1]/LB,2),'Lq',round(out['2p4'][2]/LB,2),'By',round(out['2p4'][3],2))

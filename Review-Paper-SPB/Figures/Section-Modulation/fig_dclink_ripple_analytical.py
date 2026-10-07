"""Ideal natural-SPWM periodic steady state; analytical interval integrals.
No time marching, fitted smoothing, dead time or parasitic ringing.
Frequency coefficients are complex two-sided Fourier coefficients.
Run this file to export Fig. 9, its data, and convergence diagnostics.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT = Path(__file__).resolve().parent
N, M, F1, FSW = 3, .85, 1., 100.
PHI = np.deg2rad(20.)
IM = 1 / (.75*M*np.cos(PHI))
L, C, R = .0085, .01, 2.5
H, NS = 8000, 65536

def carrier(t, shift):
    return 1 - 4*np.abs(np.mod(FSW*t-shift, 1)-.5)

def coefficients(shift, harmonics=H):
    h = np.arange(harmonics+1)
    coeff = np.zeros(harmonics+1, complex)
    # Each half-carrier segment has at most one crossing: carrier slope
    # exceeds the maximum sinusoidal-reference slope for these parameters.
    knots = (np.arange(-2, int(2*FSW)+3)/2+shift)/FSW
    knots = np.unique(np.r_[0., knots[(knots>0)&(knots<1)], 1.])
    for theta in [0., -2*np.pi/3, 2*np.pi/3]:
        def gap(t):
            return M*np.cos(2*np.pi*t-theta-PHI)-carrier(t,shift)
        edges = [0., 1.]
        for a,b in zip(knots[:-1],knots[1:]):
            if gap(a)*gap(b)<0:
                lo,hi=a,b
                for _ in range(48):
                    mid=(lo+hi)/2
                    if gap(lo)*gap(mid)<=0: hi=mid
                    else: lo=mid
                edges.append((lo+hi)/2)
        edges=np.sort(edges)
        for a,b in zip(edges[:-1],edges[1:]):
            if gap((a+b)/2)<=0: continue
            # Integral_a^b exp(-j*2*pi*r*t) dt, including r=0.
            def integral(r):
                return (b-a)*np.sinc(r*(b-a))*np.exp(-1j*np.pi*r*(a+b))
            coeff += IM/2*(np.exp(-1j*theta)*integral(h-1)
                            +np.exp(1j*theta)*integral(h+1))
    return coeff

def reconstruct(c, count=NS):
    spectrum=np.zeros(count,complex)
    spectrum[:len(c)]=c
    spectrum[-(len(c)-1):]=np.conj(c[1:][::-1])
    return np.fft.ifft(spectrum).real*count

def main():
    cells=np.array([coefficients(k/N) for k in range(N)])
    w=2*np.pi*F1*np.arange(H+1)
    den=N-w*w*L*C+1j*w*C*R
    # Shared dc current follows Eq. (battery_current_tf).
    spectra=np.array([N*cells[0]/den, cells.sum(axis=0)/den])
    waves=np.array([reconstruct(c) for c in spectra])
    low=np.array([reconstruct(c[:H//2+1]) for c in spectra])
    t=np.arange(NS)/NS/F1
    rms=np.sqrt(2*np.sum(np.abs(spectra[:,1:])**2,axis=1))
    err=np.max(np.abs(waves-low),axis=1)
    assert np.max(np.abs(spectra[:,0]-1))<1e-9
    print("Truncation change:",err)
    assert np.max(err)<2e-5
    assert np.allclose(waves.std(axis=1),rms,rtol=1e-10)
    np.savetxt(OUT/'dclink_ripple_data.csv',np.c_[t,waves.T],delimiter=',',
               header='t_seconds,without_interleaving,with_interleaving',comments='')
    metrics=dict(method='Analytical switching-interval Fourier integrals; periodic frequency-domain response',
        N=N,M=M,f1_Hz=F1,fsw_Hz=FSW,power_factor_angle_deg=20,
        L_normalized=L,C_normalized=C,R_normalized=R,harmonics=H,
        dc_mean=waves.mean(axis=1).tolist(),ripple_rms=rms.tolist(),
        ripple_peak_to_peak=np.ptp(waves,axis=1).tolist(),
        max_change_4000_to_8000_harmonics=err.tolist())
    (OUT/'dclink_ripple_analytical_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman'],
        'mathtext.fontset':'stix','font.size':8.5,'axes.linewidth':.5,
        'xtick.direction':'in','ytick.direction':'in','pdf.fonttype':42})
    fig,ax=plt.subplots(figsize=(8.8/2.54,4.6/2.54))
    for y,col,sty,label in zip(waves,['#da4d2a','#3070be'],['-','--'],
                              ['Without interleaving','With interleaving']):
        ax.plot(t*FSW,y,color=col,ls=sty,lw=.65,label=label)
    ax.grid(color='.88',lw=.35)
    ax.set_ylabel(r'$i_{\mathrm{dc}}$ (p.u.)',labelpad=4)
    ax.set_xlim(0,100);ax.set_xlabel(r'$t/T_{\mathrm{sw}}$')
    fig.legend(*ax.get_legend_handles_labels(),loc='upper center',
               bbox_to_anchor=(.58,1.02),frameon=False,fontsize=8.5)
    fig.subplots_adjust(left=.21,right=.94,bottom=.24,top=.73)
    fig.savefig(OUT/'fig_dclink_ripple.pdf')
    fig.savefig(OUT/'fig_dclink_ripple.png',dpi=220)
    plt.close(fig)
    print(json.dumps(metrics,indent=2))
if __name__=='__main__': main()

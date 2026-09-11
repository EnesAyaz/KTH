"""Spatial FFT of a uniformly sampled full mechanical revolution.
CSV columns: angle_deg,value. Do not duplicate the 360-degree endpoint.
Orders 1 and 2 correspond to two and four poles, respectively.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def spectrum(angle, value):
    if len(angle)<4 or not np.all(np.isfinite(angle)) or not np.all(np.isfinite(value)):
        raise ValueError("Need at least four finite samples")
    step=np.diff(angle)
    if step[0]<=0 or not np.allclose(step,step[0],rtol=1e-5,atol=1e-8) or not np.isclose(step[0]*len(angle),360,rtol=1e-5):
        raise ValueError("Angles must increase uniformly over one revolution, endpoint excluded")
    amp=2*np.abs(np.fft.rfft(value))/len(value)
    amp[0]/=2
    if len(value)%2==0: amp[-1]/=2
    return np.arange(len(amp)),amp

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv",type=Path)
    args=parser.parse_args()
    data=pd.read_csv(args.csv)
    orders,amplitudes=spectrum(data.angle_deg.to_numpy(),data.value.to_numpy())
    root=Path(__file__).resolve().parents[1]
    name=args.csv.stem
    pd.DataFrame({"spatial_order":orders,"peak_amplitude":amplitudes}).to_csv(root/"results/tables"/f"{name}_harmonics.csv",index=False)
    fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")
    ax.stem(orders[:31],amplitudes[:31])
    ax.set(xlabel="Spatial order (cycles/mechanical revolution)",ylabel="Peak amplitude (input units)")
    fig.savefig(root/"results/figures"/f"{name}_harmonics.pdf")
    fig.savefig(root/"results/figures"/f"{name}_harmonics.png",dpi=200)
    plt.close(fig)
if __name__=="__main__": main()

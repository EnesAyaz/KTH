import numpy as np
exec(open('gen_fig_dclink_ripple.py').read().split("fig, ax = plt.subplots")[0])

dt_local = t[1] - t[0]

def spectrum(x):
    X = np.fft.rfft(x - x.mean())
    freqs = np.fft.rfftfreq(len(x), d=dt_local)
    mag = np.abs(X) / len(x)
    return freqs, mag

f_w, m_w = spectrum(idc_without)
f_i, m_i = spectrum(idc_with)

print("Low-frequency family (6*f1 multiples), without vs with:")
for h in [6, 12, 18, 24, 30, 36]:
    idx = np.argmin(np.abs(f_w - h))
    print(f"  f={h:5.1f} Hz   without={m_w[idx]:.5f}   with={m_i[idx]:.5f}   ratio={m_w[idx]/max(m_i[idx],1e-9):.2f}")

print("\nSwitching-frequency family, without vs with:")
for h in [97, 100, 103, 194, 200, 206]:
    idx = np.argmin(np.abs(f_w - h))
    print(f"  f={h:5.1f} Hz   without={m_w[idx]:.5f}   with={m_i[idx]:.5f}   ratio={m_w[idx]/max(m_i[idx],1e-9):.2f}")

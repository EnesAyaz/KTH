import numpy as np
exec(open('gen_fig_dclink_ripple.py').read().split("fig, ax = plt.subplots")[0])

# Check periodicity: compare last period vs second-to-last period
n = n_per_period
last = idc_without_full[-n:]
prev = idc_without_full[-2*n:-n]
diff = np.abs(last - prev)
print(f"periodicity check (without): max|last-prev|={diff.max():.5f}, "
      f"vs pp={last.max()-last.min():.5f}  -> {'SETTLED' if diff.max() < 0.05*(last.max()-last.min()) else 'NOT SETTLED (still transient)'}")

# envelope amplitude in first vs second half of the kept period
half = n // 2
env1 = last[:half].max() - last[:half].min()
env2 = last[half:].max() - last[half:].min()
print(f"envelope pp first-half={env1:.4f}  second-half={env2:.4f}  ratio={env1/env2:.2f}")

# FFT of the settled 'without' signal
dt_local = t[1] - t[0]
fs = 1.0 / dt_local
spec = np.fft.rfft(last - last.mean())
freqs = np.fft.rfftfreq(len(last), d=dt_local)
mag = np.abs(spec) / len(last)
top_idx = np.argsort(mag)[::-1][:15]
print("Top frequency components (Hz, magnitude):")
for i in sorted(top_idx):
    if mag[i] > 0.0005:
        print(f"  f={freqs[i]:7.2f} Hz   mag={mag[i]:.5f}")

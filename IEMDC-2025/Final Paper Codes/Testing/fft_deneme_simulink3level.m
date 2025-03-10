vpp=out.Vpp.signals.values;
f1=500;
time=out.Vpp.time;
sample_time=time(2)-time(1);
Fs=1/sample_time;
Y = fft(vpp);
L=length(time);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));
%%
% figure();
% plot(time,vpp,"LineWidth",2) 

%%
figure();
plot(f/1e3,2*P1./625.*f1./f',"LineWidth",2) 
% title("Single-Sided Amplitude Spectrum of Phase Curremt")
% xlabel("Harmonic Number")
% ylabel("Magnitude of Phase Current (A)")
xlim([0 200])
ylim([0 0.02])

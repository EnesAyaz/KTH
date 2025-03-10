vp=out.Vpa.signals.values;
f1=ffund;
time=out.Vpa.time;
sample_time=time(2)-time(1);
Fs=1/sample_time;
Y = fft(vp);
L=length(time);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));
%%
% figure();
% plot(time,vpp,"LineWidth",2) 

%%
% Convert to string and set title
title_str = sprintf('Modulation Index: %.2f\nFundamental Frequency: %.1f Hz\nSwitching Frequency: %.1f kHz', ...
                    ma, ffund, fsw / 1000);
figure();
plot(f/1e3,P1',"LineWidth",2) 
title(title_str);
xlabel("Frequency (kHz)")
ylabel("Amplitude of Phase Voltage (V)")
xlim([0 80])
% ylim([0 0.02])

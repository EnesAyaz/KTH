

time=theta/2/pi/f1;
sample_time=time(2)-time(1);
Fs=1/sample_time;

plot(theta,i_a)
hold on
plot(theta,ipA)
hold on

%%
Y = fft(i_a);
L=length(time);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs/L*(0:(L/2));
%%
figure()
plot(f,P1,"LineWidth",3) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")
xlim([0 20000])
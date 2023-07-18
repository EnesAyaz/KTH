SA= out.ScopeData1.signals(1).values;
time=out.ScopeData1.time;

Fs= 1/(time(2)-time(1));

L=length(SA);
Y = fft(SA);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:(L/2))/L;
stem(f,P1) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")

xlim([0 50e3])
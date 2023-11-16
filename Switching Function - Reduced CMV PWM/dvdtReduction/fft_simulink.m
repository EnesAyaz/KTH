data= out.ScopeData7.signals(1).values  ;
time= out.ScopeData7.time ;
%%
L=length(data)
Fs =1/(time(2)-time(1));            % Sampling frequency

Y = fft(data);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs/L*(0:(L/2));
stem(f,P1,"LineWidth",3) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")
xlim([0 2*fsw])
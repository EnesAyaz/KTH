time = out.ScopeData8 (:,1);
data = out.ScopeData8 (:,2);

%%

Fs = 1/(time(2)-time(1));    % Sampling frequency                   

 Y = fft(data);

recordLength2=length(Y)

P2 = abs(Y/recordLength2);
P1 = P2(1:recordLength2/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs/recordLength2*(0:(recordLength2/2));


stem(f,P1,"LineWidth",1) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")

 xlim([0 200e3])
fm=10e3;
fc=100e3;

time_final=10/fm;

time_space=0:1e-7:time_final;

carrier=[];
K=1.44;
f=[];
theta_c=pi;
theta_m=0;
for t=time_space
theta=mod(2*pi*fc*t+K*cos(2*pi*fm*t+theta_m)+theta_c, 2*pi);

carrier=[carrier, (theta-pi)/pi];

end
%%

plot(carrier)
%%

Ref=0; 
    duty=[];
for i=1:length(carrier)
    if Ref>carrier(i)
duty=[duty 1];
    else 
duty=[duty 0];
    end
end
%%

plot(duty)
%%


Fs = 1/(time_space(2)-time_space(1));    % Sampling frequency                   

 y = fft(duty);

recordLength2=length(y)

P2 = abs(y/recordLength2);
P1 = P2(1:recordLength2/2+1);
P1(2:end-1) = 2*P1(2:end-1);

P_phase= angle(y/recordLength2);
P1_phase=P_phase(1:recordLength2/2+1);

f = Fs/recordLength2*(0:(recordLength2/2));

tol = 0.05;
f1_phase=f;
indices= find(abs(P1) < tol);
P1_phase(indices) = [];
f1_phase(indices) = [];

figure(1)
stem(f,P1,"LineWidth",1) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")

 xlim([0 400e3])

 figure(2)
stem(f1_phase,P1_phase*180/pi,"LineWidth",1) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")

 xlim([0 400e3])

 %%

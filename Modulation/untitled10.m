len=1200;
phi= linspace(0,2*pi,len);
ma=1;

a= ma*sin(phi);
b= ma*sin(phi-2*pi/3);
c= ma*sin(phi+2*pi/3);

x1=ma*ones([1,len/6])
x2=-ma*ones([1,len/6])
x3=ma*zeros([1,len/6])

xa= [x3 x2 x3 x3 x1 x3];

xa= [x2 x2 x2 x1 x1 x1]/3;
xb= [x1 x3 x3 x2 x3 x3];
xc= [x3 x3 x1 x3 x3 x2];
%%
%%

ffund=1e3;
time=linspace(0,1/ffund,len);
L=len
Fs = ffund*len;            % Sampling frequency

Y = fft(a+xa);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs/L*(0:(L/2));
stem(f,P1,"LineWidth",3) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")
xlim([0 10e3])

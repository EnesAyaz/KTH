len=1200;
phi= linspace(0,2*pi,len)
ma=1;
x1=linspace(0,ma,len/6)
x2=linspace(ma,0,len/6)
x=[x1, x2]
x3=zeros([1,len/6])
% xc= [x x3 -x x3]
% xa=[-x2 x3 x x3 -x1]
% xb=[x3 -x x3 x ]

xc= [x1 x3 x3 x2 x3 x3]
xb= [x3 x2 x3 x3 x1 x3]
xa= [x3 x3 x1 x3 x3 x2]

x1=cos(phi1);
x2=cos(phi2);

xc= [x3 x3 x1 x2 x1 x2 ];
xb= [x1 x2 x1 x2 x3 x3];
xa= [x1 x2 x3 x3 x1 x2 ],



% x=[x x x]-0.5
% a= ma*sin(phi) +linspace(0,ma,100)
a= ma*cos(phi)+xa/2;
b= ma*cos(phi-2*pi/3) +xb/2;
c= ma*cos(phi+2*pi/3)+xc/2;
%%
%%

ffund=1e3;
time=linspace(0,1/ffund,len);
L=len
Fs = ffund*len;            % Sampling frequency

Y = fft(xa);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs/L*(0:(L/2));
stem(f,P1,"LineWidth",3) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")
xlim([0 10e3])





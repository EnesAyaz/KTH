len=1200;
phi= linspace(0,2*pi,len);
ma=1;

x1=ones([1,len/24])/3;
x2=-ones([1,len/24])/3;
x3=zeros([1,len/24])/3;
x4= 3*x1/2;
x5=3*x2/2;

x3a=-zeros([1,len/24]);
x3b=-zeros([1,len/24]);
x4= 3*x1/2;
x5=3*x2/2;

% 
% xa=[x2 x5 x3a x1 x1 x4 x5 x2 x2 x3b x4 x1 x1 x4 x3b x2 x2 x5 x4 x1 x1 x3a x5 x2 ];
% xb=[x2 x5 x4 x1 x1 x3a x5 x2 x2 x5 x3a x1 x1 x4 x5 x2 x2 x3b x4 x1 x1 x4 x3b x2 ];
% xc=[x2 x3b x4 x1 x1 x4 x3b x2 x2 x5 x1 x1 x1 x3a x5 x2 x2 x2 x3a x1 x1 x4 x2 x2 ];

xa=[x2 x5 x3a x3a x4 x4 x5 x2 x3b x3b x4 x1 x1 x4 x3b x3b x2 x5 x4 x1 x3a x3a x5 x2 ];
xb=[x2 x5 x4 x4 x3a x3a x5 x2 x5 x5 x3a x3a x1 x4 x5 x5 x2 x3b x4 x1 x4 x4 x3b x2 ];
xc=[x2 x3b x4 x4 x4 x4 x3b x2 x5 x5 x1 x1 x1 x3a x5 x5 x2 x2 x3a x1 x4 x4 x2 x2 ];


a= ma*cos(phi) ;
b= ma*cos(phi-2*pi/3);
c= ma*cos(phi+2*pi/3);

figure()
plot(b+xb)
hold on
%%
% figure()
% plot(a)
% hold on
plot(a+xa)
hold on
% plot(b+xb)
% hold on
% plot(c+xc)
% hold on
% % plot(b)
% % hold on
% % plot(c)
% % hold on; 
% % plot(x)
% plot(a+b+c+3*x)
%%
ffund=1e3;
time=linspace(0,1/ffund,len);
L=len;
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





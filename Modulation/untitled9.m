len=1200;
phi= linspace(0,2*pi,len);
ma=1;

a= ma*sin(phi);
b= ma*sin(phi-2*pi/3);
c= ma*sin(phi+2*pi/3);

x1=ma*ones([1,len/6])
x2=-ma*ones([1,len/6])
x3=ma*zeros([1,len/6])

xa= 2*[x2 x2 x2 x1 x1 x1]/3;
xb= [x1 x3 x3 x2 x3 x3];
xc= [x3 x3 x1 x3 x3 x2];
% 
%%
% plot(a)
% hold on,
% plot(xa)
% hold on;
plot(a+xa)
%%
% plot(b)
% hold on,
% plot(xb)
% hold on;
plot(b+xb)
%%
plot(c)
hold on,
plot(xc)
hold on;
plot(c+xc)
%%

signal= a+b+c+xa+xb+xc


plot(signal/2+3/2)

len=1200;
phi= linspace(0,2*pi,len)
ma=1;
x1=linspace(0,ma,len/6);
x2=linspace(ma,0,len/6);
x=[x1 x2];
x3=zeros([1,len/6]);

xc= [x x3 -x x3];
xa=[-x2 x3 x x3 -x1];
xb=[x3 -x x3 x ];

xa=1/3;
xb=1/3;
xc=1/3;

a= ma*cos(phi) +xa
b= ma*cos(phi-2*pi/3) +xb
c= ma*cos(phi+2*pi/3)+xc;
%%
plot(phi,a,"r")
hold on
plot(phi,b,"b")
hold on
plot(phi,c,"g")
hold on
%%

Da=(1+a)/2;
Db=(1+b)/2;
Dc=(1+c)/2;
plot(phi,a,"r")
hold on
plot(phi,Da+Db+Dc,"b")
hold on
% plot(phi,Da+Db+Dc,"b")
% hold on
% plot(phi,Da+Db+Dc,"g")




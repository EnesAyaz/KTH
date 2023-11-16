len=1200;
phi= linspace(0,2*pi,len)
ma=1.64;
x1=linspace(0,ma,len/6)
x2=linspace(ma,0,len/6)
x=[x1 x2]
x3=zeros([1,len/6])

xc= [x1 x2 x3 -x1 -x2 x3]
xa=[-x2 x3 x1 x2 x3 -x1]
xb=[x3 -x1 -x2 x3 x1 x2 ]

% xc= [x1 x3 x3 x2 x3 x3]
% xb= [x3 x2 x3 x3 x1 x3]
% xa= [x3 x3 x1 x3 x3 x2]
% x=[x x x]-0.5
% a= ma*sin(phi) +linspace(0,ma,100)

% phi1=linspace(2*pi/3,pi,len/6)
% phi2=linspace(pi,2*pi/3,len/6)
% 
% x1=cos(phi1);
% x2=cos(phi2);

% xc= [x3 x3 x1 x2 x1 x2 ];
% xb= [x1 x2 x1 x2 x3 x3];
% xa= [x1 x2 x3 x3 x1 x2 ],
% 
% xa=0;
% xb=0;
% xc=0;
a= ma*cos(phi) +xa/2
b= ma*cos(phi-2*pi/3) +xb/2
c= ma*cos(phi+2*pi/3)+xc/2;
%%
plot(phi,(a+b),"r")
hold on
plot(phi,(a+c),"b")
hold on
plot(phi,(c+b),"g")
hold on
plot(phi,a)
hold on
plot(phi,c)


%%
% phi=[phi phi]
% a=[a a]
% b=[b b]
% c=[c c]

%%
figure()
plot(b)
% hold on;
% % plot(xb)
% plot(c)
% hold on;
% plot(a)
% hold on;


%%
figure()
% plot(1/2+c/2)
% hold on
plot(1/2+a/2+1/2+b/2)
hold on
plot(1/2+b/2+c/2+1/2)
hold on
plot(1/2+c/2+1/2+a/2)
hold on

%%
figure()
plot(c)
hold on;
plot(xc)

%%
figure()
% plot(a)
% hold on;
% plot(b)
% hold on;
% plot(c)
hold on
plot(xa/2)
hold on
plot(xb/2)
hold on
plot(xc/2)



%%
figure()
plot(c)
hold on;
plot(xc)

%%
figure()
plot(phi,1/2+a/2+b/2)
hold on
plot(phi,1/2+a/2+c/2)
hold on
plot(phi,1/2+b/2+c/2)
% hold on
% plot(phi,1/2+c/2)
% hold on
% plot(phi,3/2+a/2+b/2+c/2)
% hold on
% plot(phi,1/2+a/2+b/2-c/2)
% hold on
% plot(phi,1/2+a/2-b/2+c/2)
% hold on
% plot(phi,1/2-a/2+b/2+c/2)
% hold on
% plot(phi,x/3)
% hold on
%%

da=1





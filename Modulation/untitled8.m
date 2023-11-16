len=1200;
phi= linspace(0,pi/3,len)
ma=1;

a= ma*cos(phi) 
b= ma*cos(phi-2*pi/3) 
c= ma*cos(phi+2*pi/3)

%%

plot(a+(1-a-b+c)/2)
hold on
plot(b+(1-a-b+c)/2)
hold on
plot(c)
hold on
% plot(1/4-a-b+c)
% hold on

refa=a+(1-a-b+c)/2;

refb=b+(1-a-b+c)/2;

refc= c;



DA=refa/2+1/2;
DB=refb/2+1/2
DC=refc/2+1/2


%%



plot(DB/2+DC)
hold on;

% plot(DA-DB+DC)

% plot(DC)
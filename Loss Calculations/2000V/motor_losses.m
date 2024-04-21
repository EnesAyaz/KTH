ffund=1e3;
f1=1e3:ffund:1e5;
% f1=log10(f1);
Z1= linspace(7,800,length(f1));
R1= linspace(2,700,length(f1));

% Z1= logspace(0.8451,2.9031,length(f1));
% R1= logspace(0.3010, 2.8451,length(f1));

f2=1e5:ffund:1e6;
% f2=log10(f2);

Z2=linspace(800,30,length(f2));
R2= linspace(700,5,length(f2));

% Z2=logspace(2.9031,1.4771,length(f2));
% R2= logspace(2.8451,0.6990,length(f2));

f=[f1,f2(2:end)];
Z=[Z1,Z2(2:end)];
R=[R1,R2(2:end)];

plot(f,R)
hold on 
% plot(f,Z)

%%
M=0.1;
fsw=30e3;
p=fsw/ffund;
nharm=16*p;
theta0=0;
thetac=0;
Va= spect2lanalyt(p,M,nharm,'tria' ,theta0,thetac);
theta0=2*pi/3;
Vb= spect2lanalyt(p,M,nharm,'tria' ,theta0,thetac);
theta0=4*pi/3;
Vc= spect2lanalyt(p,M,nharm,'tria' ,theta0,thetac);
Vll=Va-Vb;
Vll2=Vc-Va;
Vll=Vll*1250;
Vll2=Vll2*1250;


Vll=Vll(2:end);
Vll2=Vll2(2:end);

fll=f(1:length(Vll));
Zll=Z(1:length(Vll));
Rll=R(1:length(Vll));
Lll=sqrt(Zll.^2-Rll.^2);
Zll2=1i*Lll+Rll;

ILL= Vll./Zll2;
ILL2=Vll2./Zll2;

P1=abs(ILL).^2.*Rll/2;
P2=abs(ILL2).^2.*Rll/2;
P=P1*3/2;

Ph=P(2:end);
fh=fll(2:end);


Pt=sum(Ph)


figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot(fh/1e3,Ph);

% Create ylabel
ylabel({'Harmonic Loss (W)'});

% Create xlabel
xlabel({'Frequency (kHz)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'XGrid','on','YGrid','on');







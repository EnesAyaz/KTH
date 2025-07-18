addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

% Compute modulation pattern in time domain
ma=1.15;   % Modulation index
f1 = 700; % Fundamental frequency
fc = 14e3; % Carrier frequency
pn = fc/f1; % Pulse number
npoints = 10000; % Number of timepoints
carrytype='tria'; % carrier type 
smp= 'ns';  % reference sampling mode 
cmode='tri6'; % reference common-mode injection 
 % cmode='none'; % reference common-mode injection 
theta0=0; % reference phase offset
thetac=0; % carrier phase offset
start_angle= 0; % reference angle to start with
end_angle=2*pi; %reference angle to end with 
ma_dc=0; % DC reference 
[vp_a,wt,carr,ref] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
theta0=2*pi/3; % reference phase offset
[vp_b,wt,carr,ref] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
  theta0=-2*pi/3; % reference phase offset
[vp_c,wt,carr,ref] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
        %
% Compute phase current in time domain (sinusoidal for simplicity)
Ud = 1070; % p2p DC voltage
P = 360e3;    % Only 200 kW because the chosen semiconductor device is too small
cosphi =1;  % Cos(phi) at inverter terminal
uppk = 1*Ud/2; % Peak phase voltage reference;
ippk = P*2/3/uppk/cosphi;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip_a = ippk*cos(wt-phi);   % sampled phase current over one cycle
ip_b = ippk*cos(wt-phi +2*pi/3);   % sampled phase current over one cycle
ip_c = ippk*cos(wt-phi -2*pi/3);   % sampled phase current over one cycle

%%
figure(1)
plot(wt,vp_a*Ud/2, wt,ip_a)
hold on;
% plot(wt,vp_b*1070, wt,ip_b)
% hold on;
% plot(wt,vp_c*1070, wt,ip_c)
%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create multiple line objects using matrix input to plot
plot1 = plot(wt*180/pi,vp_a*Ud/2,'LineWidth',1);
plot2 = plot(wt*180/pi,ip_a,'LineWidth',1);
set(plot1,'DisplayName','V_{LN}','Color',[1 0 0]);
set(plot2,'DisplayName','I_L','Color',[0 0 1]);
% Create ylabel
ylabel({'Voltage, Current (V, A)'});
% Create xlabel
xlabel({'Angular Frequency (^o)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.719345239452306 0.711507940126791 0.1464285697788 0.148809519693965]);
xlim([0 360])

%% Leg current

% Leg current a
Ipk = ip_a;
Upk = vp_a;   

ip = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(Ipk.*sw);                     % current through switch
Idi = abs(Ipk.*di);                     % current through diode

Isw_a=Isw;

% Leg current b
Ipk = ip_b;
Upk = vp_b;   

ip = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(Ipk.*sw);                     % current through switch
Idi = abs(Ipk.*di);                     % current through diode

Isw_b=Isw;

% Leg current c
Ipk = ip_c;
Upk = vp_c;   

ip = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(Ipk.*sw);                     % current through switch
Idi = abs(Ipk.*di);                     % current through diode

Isw_c=Isw;

%% Leg current plot 
figure(2)
plot(wt,Isw_a)
hold on;
plot(wt,Isw_b)
hold on;
plot(wt,Isw_c)
hold on;
%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create multiple line objects using matrix input to plot
plot1 = plot(wt*180/pi,Isw_a,'LineWidth',2,'Parent',axes1);
plot2 = plot(wt*180/pi,Isw_b,'LineWidth',2,'Parent',axes1);
plot3 = plot(wt*180/pi,Isw_c,'LineWidth',2,'Parent',axes1);
set(plot1,'DisplayName','Leg A','Color',[0 0 1]);
set(plot2,'DisplayName','Leg B','Color',[1 0 0]);
set(plot3,'DisplayName','Leg C',...
    'Color',[0.717647058823529 0.274509803921569 1]);

% Create ylabel
ylabel({'Current (A)'});
% Create xlabel
xlabel({'Angular Frequency (^o)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend(axes1,'show');
xlim([0 360])


%% Capacitor Current
Ic=Isw_a+Isw_b+Isw_c;
Ic=Ic-mean(Ic);
%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create multiple line objects using matrix input to plot
plot1 = plot(wt*180/pi,Ic,'LineWidth',2,'Parent',axes1);
set(plot1,'DisplayName','Cap Current','Color',[0 0 1]);
% Create ylabel
ylabel({'Current (A)'});
% Create xlabel
xlabel({'Angular Frequency (^o)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend(axes1,'show');
xlim([0 360])

%%
nharm=pn*5;

harmonic=fourser(Ic,nharm);
% f=1:1:(nharm-1);
% harmonic=harmonic(1:end);
f=1:1:nharm;

%% Capacitor Current harmonic plot
harmonic_mag=abs(harmonic);
figure(3)
stem(f,harmonic_mag)
%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create stem
stem(f,harmonic_mag,'Marker','^','LineWidth',1);
% Create ylabel
ylabel({'Peak Magnitude (A)'});
% Create xlabel
xlabel({'Harmonic number'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times','FontSize',15);

%%
t=wt/2/pi/f1;
CdV= cumtrapz(Ic,t);
deltaT=t(2)-t(1);
I_c_mm= zeros(size(Ic));
for i=2:length(Ic)
I_c_mm(i)=I_c_mm(i-1) + (Ic(i)*deltaT);
end
figure(4)
plot(t,I_c_mm)
%%
deltaV= 14;
C= (max(I_c_mm)-min(I_c_mm))/deltaV;
C*1e6
V= zeros(size(Ic));
for i=2:length(Ic)
V(i)=V(i-1) + (1/(C))* (Ic(i)*deltaT);
end
figure(5)
plot(t,V)
max(V)-min(V)

%%
% t=wt/2/pi/f1;
% CdV= cumtrapz(Ic,t);
% plot(t,Ic)
% 
% %
% C=565e-6;
% deltaT=t(2)-t(1);
% V= zeros(size(Ic));
% for i=2:length(Ic)
% 
% V(i)=V(i-1) + (1/(C))* (Ic(i)*deltaT);
% 
% end
% plot(t,V)
% deltaV= max(V)-min(V);
% 
% 100*deltaV/1250;
% 
% %
% t=wt/2/pi/f1;
% CdV= cumtrapz(Ic,t);
% plot(t,Ic)
% deltaT=t(2)-t(1);
% I_c_mm= zeros(size(Ic));
% for i=2:length(Ic)
% I_c_mm(i)=I_c_mm(i-1) + (Ic(i)*deltaT);
% end
% plot(t,I_c_mm)
% deltaV= 12.5000;
% C= (max(I_c_mm)-min(I_c_mm))/deltaV;
% C*1e6







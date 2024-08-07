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
cosphi =0.9;  % Cos(phi) at inverter terminal
uppk = 1.15*Ud/2; % Peak phase voltage reference;
ippk = P*2/3/uppk/cosphi;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip_a = ippk*cos(wt-phi);   % sampled phase current over one cycle
ip_b = ippk*cos(wt-phi +2*pi/3);   % sampled phase current over one cycle
ip_c = ippk*cos(wt-phi -2*pi/3);   % sampled phase current over one cycle
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
%% Capacitor Current
Ic=Isw_a+Isw_b+Isw_c;
Ic=Ic-mean(Ic);
%% Fourier
nharm=pn*200;

harmonic=fourser(Ic,nharm);
% f=1:1:(nharm-1);
% harmonic=harmonic(1:end);
f=1:1:nharm;

%% Capacitor Current harmonic plot
harmonic_mag=abs(harmonic);
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

filename="Case4.mat";
carrier_frequency= fc;
fundamental_frequency=f1;
modulation=ma;
DCVoltage=Ud;
power= P;
power_factor= cosphi;
current_harmonics= harmonic;
harmonic_frequency=f*f1;

save(filename, "harmonic_frequency","current_harmonics","power_factor","power","DCVoltage","modulation","fundamental_frequency","carrier_frequency");
%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create stem
stem(harmonic_frequency,abs(current_harmonics),'Marker','^','LineWidth',1);
% Create ylabel
ylabel({'Peak Magnitude (A)'});
% Create xlabel
xlabel({'Harmonic number'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times','FontSize',15);


addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

% Compute modulation pattern in time domain
ma=1.15;   % Modulation index
f1 = 500; % Fundamental frequency
fc = 20e3; % Carrier frequency
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
Ud = 1250; % p2p DC voltage
P = 300e3;    % Only 200 kW because the chosen semiconductor device is too small
cosphi =0.9;  % Cos(phi) at inverter terminal
uppk = 1*Ud/2; % Peak phase voltage reference;
ippk = P*2/3/uppk/cosphi;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip_a = ippk*cos(wt-phi);   % sampled phase current over one cycle
ip_b = ippk*cos(wt-phi +2*pi/3);   % sampled phase current over one cycle
ip_c = ippk*cos(wt-phi -2*pi/3);   % sampled phase current over one cycle

%%
% plot(wt,vp_a*100, wt,ip_a)
% %%
% plot(wt,vp_b*100, wt,ip_b)
% %%
% plot(wt,vp_c*100, wt,ip_c)

Ipk = ip_a;
Upk = vp_a;   

ip = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(Ipk.*sw);                     % current through switch
Idi = abs(Ipk.*di);                     % current through diode

Isw_a=Isw;

Ipk = ip_b;
Upk = vp_b;   

ip = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(Ipk.*sw);                     % current through switch
Idi = abs(Ipk.*di);                     % current through diode

Isw_b=Isw;


Ipk = ip_c;
Upk = vp_c;   

ip = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(Ipk.*sw);                     % current through switch
Idi = abs(Ipk.*di);                     % current through diode

Isw_c=Isw;

% 
% plot(wt,Isw_a)
% hold on;
% plot(wt,Isw_b)
% hold on;
% plot(wt,Isw_c)
% hold on;

%%
Ic=Isw_a+Isw_b+Isw_c;
Ic=Ic-mean(Ic);

nharm=pn*5;

harmonic=fourser(Ic,nharm);
harmonic=harmonic(2:end);

stem(harmonic)
%%
t=wt/2/pi/f1;
CdV= cumtrapz(Ic,t);
plot(t,Ic)
C=565e-6;
deltaT=t(2)-t(1);
V= zeros(size(Ic));
for i=2:length(Ic)

V(i)=V(i-1) + (1/(C))* (Ic(i)*deltaT);

end
plot(t,V)
deltaV= max(V)-min(V);

100*deltaV/1250;

%%


t=wt/2/pi/f1;
CdV= cumtrapz(Ic,t);
plot(t,Ic)
deltaT=t(2)-t(1);
I_c_mm= zeros(size(Ic));
for i=2:length(Ic)

I_c_mm(i)=I_c_mm(i-1) + (Ic(i)*deltaT);

end


plot(t,I_c_mm)

deltaV= 12.5000;

C= (max(I_c_mm)-min(I_c_mm))/deltaV;
C*1e6







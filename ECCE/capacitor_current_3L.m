addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

% Compute modulation pattern in time domain
% Compute modulation pattern in time domain
ma=1;   % Modulation index
f1 = 500; % Fundamental frequency
fc = 25e3; % Carrier frequency
p = fc/f1; % Pulse number
nlev=3;
theta0=0;
npts = 10000; % Number of timepoints
type='sc1'; % carrier type 
opt='3rd1'; % reference common-mode injection
thetac=0; % carrier phase offset
%scale=0;
%offset=0;
%carrmod=0;
[vp_a,wt,ref,carr] = mlspwm(ma, p ,nlev, theta0, npts,type,opt);  % Numerical waveforms during one cycle
theta0=2*pi/3; % reference phase offset
[vp_b,wt,ref,carr] = mlspwm(ma, p ,nlev, theta0, npts,type,opt);  % Numerical waveforms during one cycle
theta0=-2*pi/3; % reference phase offset
[vp_c,wt,ref,carr] = mlspwm(ma, p ,nlev, theta0, npts,type,opt);  % Numerical waveforms during one cycle
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

sw1 =  (Ipk>=0&Upk>0) | (Ipk<0&Upk<0);   % =1 when current passes through switch
di1 = (Ipk>=0&Upk<0) | (Ipk<0&Upk>0);    % =1 when current passes through diode
di2 = di1;
di5 =  (Upk==0);
sw2 =  (sw1 | di5);

Isw1 = abs(Ipk.*sw1);
Isw2 = abs(Ipk.*sw2);
Idi1 = abs(Ipk.*di1);    
Idi2 = Idi1;
Idi5 = abs(Ipk.*di5);

Isw_a=Isw1;

Ipk = ip_b;
Upk = vp_b;   

sw1 =  (Ipk>=0&Upk>0) | (Ipk<0&Upk<0);   % =1 when current passes through switch
di1 = (Ipk>=0&Upk<0) | (Ipk<0&Upk>0);    % =1 when current passes through diode
di2 = di1;
di5 =  (Upk==0);
sw2 =  (sw1 | di5);

Isw1 = abs(Ipk.*sw1);
Isw2 = abs(Ipk.*sw2);
Idi1 = abs(Ipk.*di1);    
Idi2 = Idi1;
Idi5 = abs(Ipk.*di5);

Isw_b=Isw1;


Ipk = ip_c;
Upk = vp_c;   

sw1 =  (Ipk>=0&Upk>0) | (Ipk<0&Upk<0);   % =1 when current passes through switch
di1 = (Ipk>=0&Upk<0) | (Ipk<0&Upk>0);    % =1 when current passes through diode
di2 = di1;
di5 =  (Upk==0);
sw2 =  (sw1 | di5);

Isw1 = abs(Ipk.*sw1);
Isw2 = abs(Ipk.*sw2);
Idi1 = abs(Ipk.*di1);    
Idi2 = Idi1;
Idi5 = abs(Ipk.*di5);

Isw_c=Isw1;

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
plot(Ic)
%%
nharm=pn*10

harmonic=fourser(Ic,nharm)
harmonic=harmonic(2:end)

stem(harmonic)
%%
% t=wt/2/pi/f1;
% CdV= cumtrapz(Ic,t)
% plot(t,Ic)
% C=175e-6;
% deltaT=t(2)-t(1),
% V= zeros(size(Ic));
% for i=2:length(Ic)
% 
% V(i)=V(i-1) + (1/(C))* (Ic(i)*deltaT);
% 
% end
% plot(t,V)
% deltaV= max(V)-min(V);
% 
% 100*deltaV/1250/2

%%


t=wt/2/pi/f1;
CdV= cumtrapz(Ic,t)
plot(t,Ic)
deltaT=t(2)-t(1),
I_c_mm= zeros(size(Ic));
for i=2:length(Ic)

I_c_mm(i)=I_c_mm(i-1) + (Ic(i)*deltaT);

end

plot(t,I_c_mm)
deltaV= 12.5000;

C= (max(I_c_mm)-min(I_c_mm))/deltaV;
C*1e6






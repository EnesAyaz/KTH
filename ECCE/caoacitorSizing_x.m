addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

C_y=[];
% Compute modulation pattern in time domain
for ma=0.1:0.05:1.15   % Modulation index
C_x=[];
for cosphi =0.6:0.1:1
f1 = 500; % Fundamental frequency
fc = 11e3; % Carrier frequency
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
% cosphi =0.9;  % Cos(phi) at inverter terminal
uppk = 1.15*Ud/2; % Peak phase voltage reference;
ippk = P*2/3/uppk/cosphi;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip_a = ippk*cos(wt-phi);   % sampled phase current over one cycle
ip_b = ippk*cos(wt-phi +2*pi/3);   % sampled phase current over one cycle
ip_c = ippk*cos(wt-phi -2*pi/3);   % sampled phase current over one cycle

%
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
Ic=Isw_a+Isw_b+Isw_c;
Ic=Ic-mean(Ic);

t=wt/2/pi/f1;
CdV= cumtrapz(Ic,t);
deltaT=t(2)-t(1);
I_c_mm= zeros(size(Ic));
for i=2:length(Ic)
I_c_mm(i)=I_c_mm(i-1) + (Ic(i)*deltaT);
deltaV= 12.5000;
C= (max(I_c_mm)-min(I_c_mm))/deltaV;
end
C_x= [C_x, C*1e6];
end
C_y= [ C_y ; C_x];
end

%%

ma=0.1:0.05:1.15;   % Modulation index
cosphi =0.6:0.1:1;

[X,Y] = meshgrid(cosphi,ma);
mesh(X,Y,C_y)
colormap(jet)
colorbar()
xlabel("Power factor");
ylabel("Modulation Index")
zlabel("Capacitance ( \mu F)")


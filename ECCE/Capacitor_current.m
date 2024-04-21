addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')
clear;
topology='2L' ;  % use '2L' for two level topology and '3L' for three level topology
switch topology
case '2L' 
        % Compute modulation pattern in time domain
        ma=0.1;   % Modulation index
        f1 = 500; % Fundamental frequency
        fc = 20e3; % Carrier frequency
        pn = fc/f1; % Pulse number
        npoints = 10000; % Number of timepoints
        carrytype='tria'; % carrier type 
        smp= 'ns';  % reference sampling mode 
        % cmode='tri6'; % reference common-mode injection 
         cmode='none'; % reference common-mode injection 
        theta0=0; % reference phase offset
        thetac=0; % carrier phase offset
        start_angle= 0; % reference angle to start with
        end_angle=2*pi; %reference angle to end with 
        ma_dc=0; % DC reference 
        [vp_a,wt,carr,ref] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
        theta0=2*pi/3; % reference phase offset
        [vp_b,wt,carr,ref] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
          theta0=2*pi/3; % reference phase offset
        [vp_b,wt,carr,ref] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
        % Numerical waveforms during one cycle
case '3L'
        % Compute modulation pattern in time domain
        ma=1;   % Modulation index
        f1 = 500; % Fundamental frequency
        fc = 20e3; % Carrier frequency
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
end 

% Compute phase current in time domain (sinusoidal for simplicity)
Ud = 1250; % p2p DC voltage
P = 300e3;    % Only 200 kW because the chosen semiconductor device is too small
cosphi =0.9;  % Cos(phi) at inverter terminal
uppk = ma*Ud/2; % Peak phase voltage reference;
ippk = P*2/3/uppk/cosphi;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip = ippk*cos(wt-phi);   % sampled phase current over one cycle

Ipk = ip;
Upk = vp_a;   

switch topology
case '2L'        

ip = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(Ipk.*sw);                     % current through switch
Idi = abs(Ipk.*di);                     % current through diode

case '3L'

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
end 

%%  Capacitor current







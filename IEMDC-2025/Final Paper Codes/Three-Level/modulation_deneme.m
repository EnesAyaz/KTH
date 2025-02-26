ma=1;   % Modulation index
% f1 = fe; % Fundamental frequency
% fc = 34*fe; %Selected carrier frequency 
% pn = fc/f1; % Pulse number
pn=21;
npoints = 8*(1/20)*1e7; % Number of timepoints
carrytype='pcs'; % carrier type 
smp= 'ns';  % reference sampling mode 
cmode='none'; % reference common-mode injection 
% % cmode='tri6'; % reference common-mode injection 
thetac=0; % carrier phase offset
start_angle= 0; % reference angle to start with
end_angle=16*2*pi; %reference angle to end with 
ma_dc=0; % DC reference

theta0=0; % reference phase offset
[vp_a,wt_a,ref_a, carr_a] = mlspwm(ma, pn, 3, theta0,npoints, carrytype, cmode);
fundamental_count=24;
wt_a1=wt_a;
vp_a1=vp_a;
ref_a1=ref_a;
carr_a1=carr_a;
for i=1:1:fundamental_count
vp_a=[vp_a, vp_a1];
wt_a=[wt_a, wt_a1+2*pi*(i)];
ref_a=[ref_a, ref_a1];
carr_a=[carr_a, carr_a1];
end


theta0=4*pi/3; % reference phase offset
[vp_b,wt_b,ref_b,carr_b] = mlspwm(ma, pn, 3, theta0,npoints, carrytype, cmode);
wt_b1=wt_b;
vp_b1=vp_b;
ref_b1=ref_b;
carr_b1=carr_b;
for i=1:1:fundamental_count
vp_b=[vp_b, vp_b1];
wt_b=[wt_b, wt_b1+2*pi*(i)];
ref_b=[ref_b, ref_b1];
carr_b=[carr_b, carr_b1];
end



theta0=2*pi/3; % reference phase offset
[vp_c,wt_c,ref_c,carr_c] = mlspwm(ma, pn, 3, theta0, npoints,carrytype, cmode);
wt_c1=wt_c;
vp_c1=vp_c;
ref_c1=ref_c;
carr_c1=carr_c;
for i=1:1:fundamental_count
vp_c=[vp_c, vp_c1];
wt_c=[wt_c, wt_c1+2*pi*(i)];
ref_c=[ref_c, ref_c1];
carr_c=[carr_c, carr_c1];
end


% Numerical waveforms during one cycle
vp= vp_a- (vp_a+vp_b+vp_c)/3;
wt= wt_b;
carr= carr_a;
ref= ref_a;

figure('Name','Reference Voltages of the Modulation' )
plot(wt_a,'r')
hold on 
% plot(wt/2/pi/20, ref_b,'b')
hold on; 
% plot(wt/2/pi/20, ref_c,'g')
hold on; 


figure('Name','Reference Voltages of the Modulation' )
plot(wt_a/2/pi/20, ref_a,'r')
hold on 
% plot(wt/2/pi/20, ref_b,'b')
hold on; 
% plot(wt/2/pi/20, ref_c,'g')
hold on; 

figure('Name','Reference Voltages of the Modulation' )
plot(wt_a/2/pi/20, vp_a,'r')
hold on 
% plot(wt/2/pi/20, vp_b,'b')
hold on; 
% plot(wt/2/pi/20, vp_c,'g')
hold on; 

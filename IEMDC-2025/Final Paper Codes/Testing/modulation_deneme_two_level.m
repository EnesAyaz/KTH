ma=0.05;   % Modulation index
fe=500;
f1 = fe; % Fundamental frequency
fc = 10e3; %Selected carrier frequency 
pn = fc/f1; % Pulse number
npoints = 20*(1/f1)*1e7; % Number of timepoints
carrytype='tria'; % carrier type 
smp= 'ns';  % reference sampling mode 
cmode='none'; % reference common-mode injection 
% % cmode='tri6'; % reference common-mode injection 
thetac=0; % carrier phase offset
start_angle= 0; % reference angle to start with
end_angle=48*2*pi; %reference angle to end with 
ma_dc=0; % DC reference

theta0=0; % reference phase offset
[vp_a,wt_a,carr_a,ref_a] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
 theta0=4*pi/3; % reference phase offset
[vp_b,wt_b,carr_b,ref_b] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
theta0=2*pi/3; % reference phase offset
[vp_c,wt_c,carr_c,ref_c] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
% Numerical waveforms during one cycle
vp= vp_a- (vp_a+vp_b+vp_c)/3;
wt= wt_a;
carr= carr_a;
ref= ref_a;

%%
figure('Name','Reference Voltages of the Modulation' )
% plot(wt/2/pi, ref_a,'r')
hold on 
% plot(wt/2/pi, carr_a(1,:),'b')
hold on; 
% plot(wt/2/pi, carr_a(2,:),'g')
% hold on; 
plot(wt/2/pi, vp_a,'k')
hold on; 
%%

figure('Name','Reference Voltages of the Modulation' )
plot(wt_a/2/pi/20, ref_a,'r')
hold on 
% plot(wt/2/pi/20, ref_b,'b')
hold on; 
% plot(wt/2/pi/20, ref_c,'g')
hold on; 

figure('Name','Reference Voltages of the Modulation' )
plot(wt_a/2/pi/20, vp_a-vp_b,'r')
hold on 
% plot(wt/2/pi/20, vp_b,'b')
hold on; 
% plot(wt/2/pi/20, vp_c,'g')
hold on; 
%%
vpp=vp_a-vp_b;
% vpp=vp_a;
f1=fe;
time=wt_a/2/pi/f1;
sample_time=time(2)-time(1);
Fs=1/sample_time;
Y = fft(vpp);
L=length(time);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));
%%
figure();
plot(f/fe,P1.*fe./f,"LineWidth",2) 
% title("Single-Sided Amplitude Spectrum of Phase Curremt")
xlabel("Harmonic Number")
% ylabel("Magnitude of Phase Current (A)")
xlim([0 200])
ylim([0 0.005])

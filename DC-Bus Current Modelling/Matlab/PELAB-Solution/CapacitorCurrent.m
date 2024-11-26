addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')
% Compute modulation pattern in time domain
ma=1;   % Modulation index
f1 = 200; % Fundamental frequency
fc = 24*1e3; % Carrier frequency
pn = fc/f1; % Pulse number
npoints = pn*100; % Number of timepoints
carrytype='tria'; % carrier type 
smp= 'ns';  % reference sampling mode 
cmode='tri6'; % reference common-mode injection 
%cmode='none'; % reference common-mode injection 
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
%%
% ip_a = ippk*cos(wt-phi)+0.1*(ippk*cos(5*wt-phi))+0.05*(ippk*cos(7*wt-phi));   % sampled phase current over one cycle
% ip_b = ippk*cos(wt-phi +2*pi/3)+0.1*(ippk*cos(5*wt-phi-2*pi/3))+0.05*(ippk*cos(7*wt-phi+2*pi/3));  % sampled phase current over one cycle
% ip_c = ippk*cos(wt-phi -2*pi/3)+0.1*(ippk*cos(5*wt-phi+2*pi/3))+0.05*(ippk*cos(7*wt-phi-2*pi/3)); % sampled phase current over one cycle

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

%%
% Isw_a-mean(Isw_a);
% Isw_b-mean(Isw_b);
% Isw_c-mean(Isw_c);
%% Fourier
nharm=pn*10*10;

N = length(Isw_a);
nharm = min(nharm, floor(N/2));

harmonic_IswA=fourser2(Isw_a,nharm);
harmonic_IswB=fourser2(Isw_b,nharm);
harmonic_IswC=fourser2(Isw_c,nharm);

harmonic_IswA=harmonic_IswA(2:end);
harmonic_IswB=harmonic_IswB(2:end);
harmonic_IswC=harmonic_IswC(2:end);


harmonic_SA=fourser2(vp_a,nharm);
harmonic_SB=fourser2(vp_b,nharm);
harmonic_SC=fourser2(vp_c,nharm);

harmonic_SA=harmonic_SA(2:end);
harmonic_SB=harmonic_SB(2:end);
harmonic_SC=harmonic_SC(2:end);


harmonic_ip_a=fourser2(ip_a,nharm);
harmonic_ip_b=fourser2(ip_b,nharm);
harmonic_ip_c=fourser2(ip_c,nharm);

harmonic_ip_a=harmonic_ip_a(2:end);
harmonic_ip_b=harmonic_ip_b(2:end);
harmonic_ip_c=harmonic_ip_c(2:end);

% f=1:1:(nharm-1);
% harmonic=harmonic(1:end);

f=1:1:(nharm-1);
%%
hold on
harmonic_mag_IswA=abs(harmonic_IswA);
harmonic_mag_SA=abs(harmonic_SA);
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create stem
stem(f,harmonic_mag_IswA,'Marker','^','LineWidth',1);
stem(f,harmonic_mag_SA,'Marker','^','LineWidth',1);
stem(f,harmonic_ip_a,'Marker','^','LineWidth',1);
% Create ylabel
ylabel({'Peak Magnitude (A)'});
% Create xlabel
xlabel({'Harmonic number'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times','FontSize',15);
xlim([0 100])
%%
figure();
subplot(3,1,1);
stem(f,harmonic_ip_a,'Marker','^','LineWidth',1);
xlim([0 pn*2])

subplot(3,1,2);
stem(f,harmonic_mag_SA,'Marker','^','LineWidth',1);
xlim([0 pn*2])

subplot(3,1,3);
stem(f,harmonic_mag_IswA,'Marker','^','LineWidth',1);
xlim([0 pn*2])
%%
harmonic_mag=abs(harmonic_IswA+harmonic_IswB+harmonic_IswC);
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
xlim([0 100])

%% Phase A
filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhAResponse.txt";
filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhAResponseIncludingBattery.txt";

dataLines = [2, Inf];
[freq, IC1real, IC1imag, IC2real, IC2imag, IC3real, IC3imag, IC4real, IC4imag] = capacitorStepResponse(filename, dataLines);

values= [IC1real,IC1imag, IC2real,IC2imag,IC3real,IC3imag,IC4real,IC4imag];

% New frequency array for interpolation
new_freq = f*f1; 

% Preallocate the new interpolated values
interpolated_values = zeros(length(new_freq),8);

% Interpolation loop
for i = 1:8
    % Interpolate the values for each array using 'linear' method
    interpolated_values(:,i) = interp1(freq, values(:, i), new_freq, 'linear');
end

% Display the interpolated values
cap1_phA= interpolated_values(:,1)+1i*interpolated_values(:,2);
cap2_phA= interpolated_values(:,3)+1i*interpolated_values(:,4);
cap3_phA= interpolated_values(:,5)+1i*interpolated_values(:,6);
cap4_phA= interpolated_values(:,7)+1i*interpolated_values(:,8);


cap1_phA=cap1_phA';
cap2_phA=cap2_phA';
cap3_phA=cap3_phA';
cap4_phA=cap4_phA';

%%

figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

loglog1=loglog(f*f1, abs(cap1_phA));
hold on
loglog2=loglog(f*f1, abs(cap2_phA));
hold on
loglog3=loglog(f*f1, abs(cap3_phA));
hold on
loglog4=loglog(f*f1, abs(cap4_phA));
hold on
set(loglog1,'DisplayName','Cap-1');
set(loglog2,'DisplayName','Cap-2');
set(loglog3,'DisplayName','Cap-3');
set(loglog1,'DisplayName','Cap-4');

% Create ylabel
ylabel({'Magnitude Response'});

% Create xlabel
xlabel({'Frequency (Hz)'});

% Uncomment the following line to preserve the X-limits of the axes
% xlim(axes1,[0 120000]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XMinorTick','on',...
    'XScale','log','YMinorTick','on','YScale','log');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.708630954429862 0.651984132235012 0.169642854801246 0.213095232134774]);

% ylim([0 0.5])
xlim([0 120e3])
%%
%% Phase B

filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhBResponse.txt";
filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhBResponseIncludingBattery.txt";
dataLines = [2, Inf];
[freq, IC1real, IC1imag, IC2real, IC2imag, IC3real, IC3imag, IC4real, IC4imag] = capacitorStepResponse(filename, dataLines);

values= [IC1real,IC1imag, IC2real,IC2imag,IC3real,IC3imag,IC4real,IC4imag];

% New frequency array for interpolation
new_freq = f*f1; 

% Preallocate the new interpolated values
interpolated_values = zeros(length(new_freq),8);

% Interpolation loop
for i = 1:8
    % Interpolate the values for each array using 'linear' method
    interpolated_values(:,i) = interp1(freq, values(:, i), new_freq, 'linear');
end

% Display the interpolated values
cap1_phB= interpolated_values(:,1)+1i*interpolated_values(:,2);
cap2_phB= interpolated_values(:,3)+1i*interpolated_values(:,4);
cap3_phB= interpolated_values(:,5)+1i*interpolated_values(:,6);
cap4_phB= interpolated_values(:,7)+1i*interpolated_values(:,8);

cap1_phB=cap1_phB';
cap2_phB=cap2_phB';
cap3_phB=cap3_phB';
cap4_phB=cap4_phB';


plot(new_freq, abs(cap1_phB));
hold on
plot(new_freq, abs(cap2_phB));
hold on
plot(new_freq, abs(cap3_phB));
hold on
plot(new_freq, abs(cap4_phB));
hold on
%% Phase C
filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhBResponse.txt";
filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhCResponseIncludingBattery.txt";
dataLines = [2, Inf];
[freq, IC1real, IC1imag, IC2real, IC2imag, IC3real, IC3imag, IC4real, IC4imag] = capacitorStepResponse(filename, dataLines);

values= [IC1real,IC1imag, IC2real,IC2imag,IC3real,IC3imag,IC4real,IC4imag];

% New frequency array for interpolation
new_freq = f*f1; 

% Preallocate the new interpolated values
interpolated_values = zeros(length(new_freq),8);

% Interpolation loop
for i = 1:8
    % Interpolate the values for each array using 'linear' method
    interpolated_values(:,i) = interp1(freq, values(:, i), new_freq, 'linear');
end

% Display the interpolated values
cap1_phC= interpolated_values(:,1)+1i*interpolated_values(:,2);
cap2_phC= interpolated_values(:,3)+1i*interpolated_values(:,4);
cap3_phC= interpolated_values(:,5)+1i*interpolated_values(:,6);
cap4_phC= interpolated_values(:,7)+1i*interpolated_values(:,8);


cap1_phC=cap1_phC';
cap2_phC=cap2_phC';
cap3_phC=cap3_phC';
cap4_phC=cap4_phC';


plot(new_freq, abs(cap1_phC));
hold on
plot(new_freq, abs(cap2_phC));
hold on
plot(new_freq, abs(cap3_phC));
hold on
plot(new_freq, abs(cap4_phC));
hold on

clear values IC1real IC1imag IC2real IC2imag IC3real IC3imag IC4real IC4imag new_freq interpolated_values
%%
w=f*f1*2*pi;

%% capacitor response A 
cap1= cap1_phA.*harmonic_IswA+ cap1_phB.*harmonic_IswB+ cap1_phC.*harmonic_IswC;
cap2= cap2_phA.*harmonic_IswA+ cap2_phB.*harmonic_IswB+ cap2_phC.*harmonic_IswC;
cap3= cap3_phA.*harmonic_IswA+ cap3_phB.*harmonic_IswB+ cap3_phC.*harmonic_IswC;
cap4= cap4_phA.*harmonic_IswA+ cap4_phB.*harmonic_IswB+ cap4_phC.*harmonic_IswC;

S=harmonic_IswA+harmonic_IswB+harmonic_IswC;
%%

FreqLimit=180e3;
figure;
hold all;
subplot(2,1,1);
stem(w/(2*pi),abs(harmonic_IswA),'b-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  ' Capaacitor A'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])

subplot(2,1,2);
stem(w/(2*pi),abs(S),'b-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  ' Capaacitor A'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])


%%
FreqLimit=80e3;
figure;
hold all;
subplot(2,2,1);
stem(w/(2*pi),abs(cap1),'b-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  ' Capaacitor 1'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])



subplot(2,2,2);
stem(w/(2*pi),abs(cap2),'r-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of' 'Capaacitor 2'} ...
    ,'FontSize',14,'FontWeight','Bold');

grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])

subplot(2,2,3);
stem(w/(2*pi),abs(cap3),'k-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  'Capacitor 3'} ...
    ,'FontSize',14,'FontWeight','Bold');


grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])
      
subplot(2,2,4);
stem(w/(2*pi),abs(cap4),'k-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  'Capacitor 4'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])

%%

FreqLimit=fc*5;
figure;
hold all;
plot(w/(2*pi)/1e3,abs(cap1),'b-','Linewidth',1);
plot(w/(2*pi)/1e3,abs(cap2),'r-','Linewidth',1);
plot(w/(2*pi)/1e3,abs(cap3),'g-','Linewidth',1);
plot(w/(2*pi)/1e3,abs(cap4),'k-','Linewidth',1);
set(gca,'FontSize',10);
legend('Cap1','Cap2','Cap3','Cap4' )
xlim([0 FreqLimit/1e3])


cap1(isnan(cap1)) = 0;
cap2(isnan(cap2)) = 0;
cap3(isnan(cap3)) = 0;
cap4(isnan(cap4)) = 0;

sqrt(sum(abs(cap1.^2)))
sqrt(sum(abs(cap2.^2)))
sqrt(sum(abs(cap3.^2)))
sqrt(sum(abs(cap4.^2)))



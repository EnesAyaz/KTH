for n=[1,1.5,2,2.5,3] 
given_parameters=2;
% Given parameters- 2
id = -224.33; %  d-axis current value in A
iq = 325.97; %  q-axis current value in A
vd = -138.8; %  d-axis voltage value in V
vq = 94.9; %  q-axis voltage value in V
Vdc= 625; % DC link voltage in V
Ld= 62.1e-6; % d-axis inductance value in H
Lq=101e-6; % q-axis inductance value in H
Torque= 600; % Torque of the motor in N.m
RPM = 3000; % Rotational speed in RPM

%% Electrical Frequency
% Given values
p = 6; % Number of pole pairs
% Calculate electrical frequency
fe = (RPM * p) / 60;
%% Swithcing frequency and SPWM mode selection 

f1 = fe; % Fundamental frequency
fc = n*34*fe; %Selected carrier frequency 
pn = fc/f1; % Pulse number
cmode='none'; % reference common-mode injection 
cmode='tri6'; % reference common-mode injection 

%% Calculations 
debug_mode=1; % make 1 if you want to see the graphs
Length=1000;
theta= linspace(0,2*pi,Length); % Electrical angle in radians (change as per the rotor position or time-varying angle)

%% Time domain currents
% Given d-axis and q-axis currents (id, iq)
% Inverse Park Transformation: dq to alpha-beta
ialpha = id * cos(theta) - iq * sin(theta);
ibeta = id * sin(theta) + iq * cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
i_a = ialpha;
i_b = -0.5 * ialpha + (sqrt(3) / 2) * ibeta;
i_c = -0.5 * ialpha - (sqrt(3) / 2) * ibeta;

if debug_mode==1
figure('Name','Time Domain Currents')
plot(theta,i_a)
hold on; 
plot(theta,i_b)
hold on; 
plot(theta,i_c)
end
%% Time domain voltages 
% Given d-axis and q-axis voltages (vd, vq)
% Inverse Park Transformation: dq to alpha-beta
valpha = vd * cos(theta) - vq * sin(theta);
vbeta = vd * sin(theta) + vq * cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
v_a = valpha;
v_b = -0.5 * valpha + (sqrt(3) / 2) * vbeta;
v_c = -0.5 * valpha - (sqrt(3) / 2) * vbeta;

if debug_mode==1
figure('Name','Time Domain Voltages')
plot(theta,v_a)
hold on; 
plot(theta,v_b)
hold on; 
plot(theta,v_c)
end

%% i_a, v_a
if debug_mode==1
figure('Name','Time Domain Phase-A Current and Voltage')
plot(theta,i_a)
hold on; 
plot(theta,v_a)
end
%% Modulation index calculation
ma_calculated=2*max(v_a)/Vdc; % modulation index
peak_phase_current= max(i_a); % peak phase current

%% Power Factor Calculation
% Calculate apparent power (S) in dq frame
S = vd * id + vq * iq; % Real power in dq
V_magnitude = sqrt(vd^2 + vq^2); % Magnitude of voltage vector
I_magnitude = sqrt(id^2 + iq^2); % Magnitude of current vector
% Calculate power factor
power_factor = S / (V_magnitude * I_magnitude);

%% Display results
if debug_mode==1
clc
fprintf('modulation index: %.4f\n', ma_calculated);
fprintf('Power factor: %.4f\n', power_factor);
fprintf('Electrical Frequency: %.2f Hz\n', fe);
fprintf('DC-link Voltage: %.2f V\n', Vdc);fprintf('Peak phase current: %.2f A\n', peak_phase_current);
end 
%% Load angle calculation 
% Given Ld-Lq
vd_machine= vd+id*Ld*fe*2*pi;
vq_machine=vq-Lq*iq*fe*2*pi; 

% Inverse Park Transformation: dq to alpha-beta
valpha_machine = vd_machine * cos(theta) - vq_machine * sin(theta);
vbeta_machine = vd_machine * sin(theta) + vq_machine * cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
v_a_machine = valpha_machine;
v_b_machine = -0.5 * valpha_machine + (sqrt(3) / 2) * vbeta_machine;
v_c_machine = -0.5 * valpha_machine - (sqrt(3) / 2) * vbeta_machine;

theta_backEMF = atan2(vq_machine, vd_machine);
theta_voltage = atan2(vq, vd);
theta_current = atan2(iq, id);
theta_difference= theta_voltage-theta_backEMF;


if debug_mode==1
figure('Name','Time Domain Voltages of EM')
plot(theta,v_a_machine)
hold on; 
plot(theta,v_b_machine)
hold on; 
plot(theta,v_c_machine)

figure('Name','Time Domain Voltages of EM and Phase')
plot(theta,v_a_machine,'r')
hold on; 
plot(theta,v_a,'b')
hold on; 
end 
%% Load calculation 
resistance= 1.045*max(v_a)*power_factor/max(i_a);
%%

ma=ma_calculated;   % Modulation index
% f1 = fe; % Fundamental frequency
% fc = 34*fe; %Selected carrier frequency 
% pn = fc/f1; % Pulse number
npoints = 8*(1/f1)*1e7; % Number of timepoints
carrytype='tria'; % carrier type 
smp= 'ns';  % reference sampling mode 
% cmode='none'; % reference common-mode injection 
% % cmode='tri6'; % reference common-mode injection 
thetac=0; % carrier phase offset
start_angle= 0; % reference angle to start with
end_angle=16*pi; %reference angle to end with 
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

if debug_mode==1
figure('Name','Reference Voltages of the Modulation' )
plot(wt, ref_a,'r')
hold on 
plot(wt, ref_b,'b')
hold on; 
plot(wt, ref_b,'g')
hold on; 
end

%% Compute phase current in time domain (sinusoidal for simplicity)
Ud = 625; % p2p DC voltage
cosphi =power_factor;  % Cos(phi) at inverter terminal
ippk = peak_phase_current;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip_a_t = ippk*cos(wt-phi);   % sampled phase current over one cycle
ip_b_t = ippk*cos(wt-phi-2*pi/3);   % sampled phase current over one cycle
ip_c_t = ippk*cos(wt-phi-4*pi/3);   % sampled phase current over one cycle

if debug_mode==1
figure('Name','Ideal Current Waveform of phases' )
plot(wt, ip_a_t,'r')
hold on 
plot(wt, ip_b_t,'b')
hold on; 
plot(wt, ip_c_t,'g')
hold on; 
end
%%
theta= wt; 
v_phase_a=vp_a*Ud/2;
v_phase_b=vp_b*Ud/2;
v_phase_c=vp_c*Ud/2;
ipA=ip_a_t;
ipB=ip_b_t;
ipC=ip_c_t;

rs=resistance;
t_end=theta(end)/f1/2/pi;

if debug_mode==1
figure('Name',' Phase Voltage, Phase current and Back-emf' )
plot(theta,v_phase_a)
hold on
plot(theta,ipA)
hold on
end


%% Time domain inductance Calculation
L_a = Ld * sin(theta-theta_difference).^2 + Lq *cos(theta-theta_difference).^2;
L_b = Ld * sin(theta-theta_difference-2*pi/3).^2 + Lq *cos(theta-theta_difference-2*pi/3).^2;
L_c = Ld * sin(theta-theta_difference+2*pi/3).^2 + Lq *cos(theta-theta_difference+2*pi/3).^2;

if debug_mode==1

figure('Name','Time Domain Indutances')
plot(theta,L_a, 'r')
hold on
plot(theta,L_b,'b')
hold on 
plot(theta,L_c,'g')

end

%%

i_a= zeros(size(v_phase_a));
i_b= zeros(size(v_phase_b));
i_c= zeros(size(v_phase_c));

time=wt/2/pi/f1; % angle-to-time
sample_time=time(2)-time(1); % sample_time

for t=2:length(time)

dL_dt = (L_a(t) - L_a(t-1)) / sample_time;
i_a(t) = i_a(t-1) + sample_time * ((v_phase_a(t) - rs*i_a(t-1) - dL_dt * i_a(t-1)) / L_a(t));


dL_dt = (L_b(t) - L_b(t-1)) / sample_time;
i_b(t) = i_b(t-1) + sample_time * ((v_phase_b(t) - rs*i_b(t-1) - dL_dt * i_b(t-1)) / L_b(t));

dL_dt = (L_c(t) - L_c(t-1)) / sample_time;
i_c(t) = i_c(t-1) + sample_time * ((v_phase_c(t) - rs*i_c(t-1) - dL_dt * i_c(t-1)) / L_c(t));

end

if debug_mode==1

figure('Name','Ideal and Solved Currents including Common mode- PhA')
plot(theta,i_a,'-.r')
hold on
plot(theta,ipA,'r')
hold on

figure('Name','Ideal and Solved Currents including Common mode- PhB')
plot(theta,i_b,'-.b')
hold on
plot(theta,ipB,'b')
hold on
figure('Name','Ideal and Solved Currents including Common mode- PhC')
plot(theta,i_c,'-.g')
hold on
plot(theta,ipC,'g')
hold on
end
%%
i_a_differential= i_a- (i_a+i_b+i_c)/3;
i_b_differential= i_b- (i_a+i_b+i_c)/3;
i_c_differential= i_c- (i_a+i_b+i_c)/3;

if debug_mode==1
figure; 
plot(theta,i_a_differential,'r')
hold on
plot(theta,ipA,'b')
hold on
end

if debug_mode==1
figure('Name','Solved Currents Differential')
plot(theta,i_a_differential,'r')
hold on
plot(theta,i_b_differential,'b')
hold on
plot(theta,i_c_differential,'g')
end

%%
Fs=1/sample_time;
Y = fft(i_a_differential);
L=length(time);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));
%%
if debug_mode==1
figure('Name','Solved Currents FFT for phase-A')
plot(f,P1,"LineWidth",3) 
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (Hz)")
ylabel("|P1(f)|")
xlim([0 20000])
end
%% 
required_length=round(1/fe/sample_time);

start=required_length*4;

time2= time(start:start+required_length);
time2=time2-time2(1);
i_a_differential2= i_a_differential(start:start+required_length);
i_b_differential2= i_b_differential(start:start+required_length);
i_c_differential2= i_c_differential(start:start+required_length);


frequency=1/(time2(end)-time2(1));
theta2=linspace(0,2*pi,length(i_a_differential2));

theta2=theta2-(pi+theta_difference)+0.195; % findind dq update

% Initialize arrays to store results
id2 = zeros(size(time2));
iq2 = zeros(size(time2));

% Compute i_d and i_q over the fundamental period
for k = 1:length(time2)
    thetax=theta2(k); % Electrical angle at each time step
    % Clarke Transformation (3-phase to 2-phase stationary coordinates)
    i_alpha2 = i_a_differential2(k);
    i_beta2 = (1 / sqrt(3)) * (i_a_differential2(k) + 2 * i_b_differential2(k));
    % Park Transformation (Stationary to Rotating Coordinates)
    id2(k) = i_alpha2 * cos(thetax) + i_beta2 * sin(thetax);
    iq2(k) = -i_alpha2 * sin(thetax) + i_beta2 * cos(thetax);
end

id_mean=mean(id2);
iq_mean = mean(iq2);
is= sqrt(id_mean^2+iq_mean^2)
%%
if debug_mode==1
figure('Name','dq')
plot(time2,id2) 
hold on
plot(time2,iq2) 
end

%%

% Create a struct to store all data
data.time = time2;
data.i_d_time = id2;
data.i_q_time= iq2;
data.id = id;
data.iq = iq;
data.id_mean = id_mean;
data.iq_mean = iq_mean;
data.vd = vd;
data.vq = vq;
data.Ld = Ld;
data.Lq = Lq;
data.Torque= Torque;
data.Speed= RPM;
data.fundamentalfrequency=fe;
data.fsw=fc;
data.mode=cmode;

% Save the struct to a .mat file

% Define the folder where you want to save the file
saveFolder = 'C:\Github\KTH\IEMDC-2025\Waveforms'; % Replace with the actual folder pat
folder2 =  num2str(given_parameters);  % Converts the number to a string with single quotes '123'
saveFolder=fullfile(saveFolder,folder2);

% Check if the folder exists, create it if it doesn't
if ~isfolder(saveFolder)
    mkdir(saveFolder);
end

% Determine the filename with an incrementing number
baseFilename = 'current_waveform';

fileNumber = 1;

% Check for existing files with similar names and increment
while exist(fullfile(saveFolder, sprintf('%s%d.mat', baseFilename, fileNumber)), 'file')
    fileNumber = fileNumber + 1;
end

% Define the final filename with the folder path
finalFilename = fullfile(saveFolder, sprintf('%s%d.mat', baseFilename, fileNumber));

% Save the struct to the determined filename
save(finalFilename, 'data');

fprintf('Data saved to %s\n', finalFilename);

end

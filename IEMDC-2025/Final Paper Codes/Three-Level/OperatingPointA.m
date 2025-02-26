for  n=[1 1.5 2 2.5 3]
% n= 1 1.49 2 2.5 2.99
given_parameters='A';
% Given parameters- 2
Torque= 1250; % Torque of the motor in N.m
RPM = 200; % Rotational speed in RPM
vd = -22.4; %  d-axis voltage value in V
vq = 8.4; %  q-axis voltage value in V
id = -565.4; %  d-axis current value in A
iq = 570.5; %  q-axis current value in A
Ld= 109e-6; % d-axis inductance value in H
Lq=109e-6; % q-axis inductance value in H
Vdc= 625; % DC link voltage in V
is_desired=sqrt(id^2+iq^2)
%% Electrical Frequency
% Given values
p = 6; % Number of pole pairs
% Calculate electrical frequency
fe = (RPM * p) / 60;
%%
% cmode='none'; % reference common-mode injection 
cmode='tri6'; % reference common-mode injection 

debug_mode=3; % make 1 if you want to see the graphs
% Load calculation 
if cmode=='none' 
if n==1
coeff=1.0025;
elseif n==1.5
coeff=0.9997;
elseif n==2
coeff=0.9997;
elseif n==2.5
coeff=1.001;
elseif n==3
coeff=0.9985;
end
end

if cmode=='tri6' % reference common-mode injection 
if n==1
coeff=1.0015;
elseif n==1.5
coeff=1.0013;
elseif n==2
coeff=1.002;
elseif n==2.5
coeff=1.0132;
elseif n==3
coeff=1.0015;
end
end

%% Swithcing frequency and SPWM mode selection 

f1 = fe; % Fundamental frequency
fc = n*500*fe; %Selected carrier frequency 
pn = fc/f1; % Pulse number


%% Modulation index calculation
ma_calculated=2*sqrt(vd^2+vq^2)/Vdc; % modulation index
%%
%% Calculations 
% debug_mode=2; % make 1 if you want to see the graphs
Length=10000000;
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
plot(theta/2/pi/fe,i_a)
hold on; 
plot(theta/2/pi/fe,v_a)
% xlim([0 0.027])
end
%% Modulation index calculation
ma_calculated=2*max(v_a)/Vdc; % modulation index
% if ma_calculated>1
%     ma_calculated=1;
% end
peak_phase_current= max(i_a); % peak phase current
%% Power Factor Calculation
% Calculate apparent power (S) in dq frame
S = vd * id + vq * iq; % Real power in dq
V_magnitude = sqrt(vd^2 + vq^2); % Magnitude of voltage vector
I_magnitude = sqrt(id^2 + iq^2); % Magnitude of current vector
% Calculate power factor
power_factor = S / (V_magnitude * I_magnitude);
%%
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

%%
ma=ma_calculated;   % Modulation index
% f1 = fe; % Fundamental frequency
% fc = 34*fe; %Selected carrier frequency 
% pn = fc/f1; % Pulse number
npoints = 20*(1/f1)*1e7; % Number of timepoints
carrytype='tria'; % carrier type 
smp= 'ns';  % reference sampling mode 
% cmode='none'; % reference common-mode injection 
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

if debug_mode==1
figure('Name','Reference Voltages of the Modulation' )
plot(wt/2/pi/fe, ref_a,'r')
hold on 
plot(wt/2/pi/fe, ref_b,'b')
hold on; 
plot(wt/2/pi/fe, ref_c,'g')
hold on; 
xlim([0 0.027])
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
plot(wt/2/pi/fe, ip_a_t,'r')
hold on 
plot(wt/2/pi/fe, ip_b_t,'b')
hold on; 
plot(wt/2/pi/fe, ip_c_t,'g')
hold on; 
% xlim([0 0.027])
end
%%
theta= wt; 
v_phase_a=vp_a*Ud/2;
v_phase_b=vp_b*Ud/2;
v_phase_c=vp_c*Ud/2;
ipA=ip_a_t;
ipB=ip_b_t;
ipC=ip_c_t;



%% Time domain inductance Calculation
L_a = Ld;
L_b = Ld;
L_c = Ld;

%%

i_a= zeros(size(v_phase_a));
i_b= zeros(size(v_phase_b));
i_c= zeros(size(v_phase_c));


% v_phase_a1=v_phase_a-ma_calculated*cos(wt)*Ud/2;
% v_phase_b1=v_phase_b-ma_calculated*cos(wt-2*pi/3)*Ud/2;
% v_phase_c1=v_phase_c-ma_calculated*cos(wt-4*pi/3)*Ud/2;



v_phase_a1=v_phase_a;
v_phase_b1=v_phase_b;
v_phase_c1=v_phase_c;

v_phase_a1=v_phase_a1-mean(v_phase_a1);
v_phase_b1=v_phase_b1-mean(v_phase_b1);
v_phase_c1=v_phase_c1-mean(v_phase_c1);



% v_phase_a1=v_phase_a;
% v_phase_b1=v_phase_b;
% v_phase_c1=v_phase_c;


time=wt/2/pi/f1; % angle-to-time
sample_time=time(2)-time(1); % sample_time

starting= round(1/(sample_time*fe)/3);

% v_phase_a1=v_phase_a1;

for t=2:length(time)

i_a(t) = i_a(t-1) + sample_time * ((v_phase_a1(t))/ L_a);
i_b(t) = i_b(t-1) + sample_time * ((v_phase_b1(t))/ L_a);
i_c(t) = i_c(t-1) + sample_time * ((v_phase_c1(t))/ L_a);

end


i_a=i_a-sqrt(2)*rms(i_a)*sin(fe*2*pi*time);
i_b=i_b-mean(i_b);
i_b=i_b-sqrt(2)*rms(i_b)*sin(fe*2*pi*time-2*pi/3);
i_c=i_c-mean(i_c);
i_c=i_c-sqrt(2)*rms(i_c)*sin(fe*2*pi*time+2*pi/3);

% i_b= [i_a(2*starting:end), i_a(1:2*starting-1)];
% i_c= [i_a(1*starting:end), i_a(1:1*starting-1)];
% 
% i_a=i_a+ipA;
% i_b=i_b+ipB;
% i_c=i_c+ipC;

%%
if debug_mode==2
figure('Name','Ideal and Solved Currents including Common mode- PhA')
plot(theta/2/pi/fe,i_a,'r')
hold on
plot(theta/2/pi/fe,i_b,'b')
hold on
plot(theta/2/pi/fe,i_c,'c')
hold on
% plot(theta/2/pi/fe,i_a_fundamental,'b',LineWidth=2)
% xlim([0 0.027])
hold on
end
%%

if debug_mode==2
figure('Name','Ideal and Solved Currents including Common mode- PhA')
plot(theta/2/pi/fe,i_a,'r')
hold on
plot(theta/2/pi/fe,i_b,'b',LineWidth=2)
hold on
plot(theta/2/pi/fe,i_c,'g',LineWidth=2)
% xlim([0 0.027])
hold on
% plot(theta/2/pi/fe,ipA,'b',LineWidth=2)
end

%%
if debug_mode==1
figure('Name','Ideal and Solved Currents including Common mode- PhB')
plot(theta,i_b,'-.b')
hold on
plot(theta,ipB,'b')
hold on
end
%%
if debug_mode==1
figure('Name','Ideal and Solved Currents including Common mode- PhC')
plot(theta,i_c,'-.g')
hold on
% plot(theta,ipC,'g')
hold on
end
%%


i_a_differential= i_a- (i_a+i_b+i_c)/3;
i_b_differential= i_b- (i_a+i_b+i_c)/3;
i_c_differential= i_c- (i_a+i_b+i_c)/3;



if debug_mode==2
figure; 
plot(theta,i_a_differential,'r')
hold on
% plot(theta,ipA,'b')
hold on
end
%%
if debug_mode==2
figure('Name','Solved Currents Differential')
plot(theta/2/pi/fe,i_a_differential,'r')
hold on
plot(theta/2/pi/fe,i_b_differential,'b')
hold on
plot(theta/2/pi/fe,i_c_differential,'g')
% xlim([0 0.027])
end

i_a_differential=i_a_differential+ipA*coeff;
i_b_differential=i_b_differential+ipB*coeff;
i_c_differential=i_c_differential+ipC*coeff;

%%
Fs=1/sample_time;
Y = fft(i_a_differential);
L=length(time);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));
%%
if debug_mode==3
figure1= figure('Name','Solved Currents FFT for phase-A');
axes1 = axes('Parent',figure1);

plot(f,P1,"LineWidth",2) 
% title("Single-Sided Amplitude Spectrum of Phase Curremt")
xlabel("f (Hz)")
ylabel("Magnitude of Phase Current (A)")
xlim([1000 80000])
set(axes1,'FontName','Times New Roman','FontSize',15);

end
%% 
required_length=round(1/fe/sample_time);

start=required_length*40;

time2= time(start:start+required_length);
time2=time2-time2(1);
i_a_differential2= i_a_differential(start:start+required_length);
i_b_differential2= i_b_differential(start:start+required_length);
i_c_differential2= i_c_differential(start:start+required_length);


frequency=1/(time2(end)-time2(1));
theta2=linspace(0,2*pi,length(i_a_differential2));

if cmode=='none' % reference common-mode injection 
if n==1
theta2=theta2-(pi+theta_difference)+0.0255; % findind dq update
elseif n==1.5
theta2=theta2-(pi+theta_difference)+0.0187; % findind dq update
elseif n==2
theta2=theta2-(pi+theta_difference)+0.0179; % findind dq update
elseif n==2.5
theta2=theta2-(pi+theta_difference)+0.0195; % findind dq update
elseif n==3
theta2=theta2-(pi+theta_difference)+0.0235; % findind dq update
end
end

if cmode=='tri6' % reference common-mode injection 
if n==1
theta2=theta2-(pi+theta_difference)+0.0241; % findind dq update
elseif n==1.5
theta2=theta2-(pi+theta_difference)+0.0241; % findind dq update
elseif n==2
theta2=theta2-(pi+theta_difference)+0.0231; % findind dq update
elseif n==2.5
theta2=theta2-(pi+theta_difference)+0.045; % findind dq update
elseif n==3
theta2=theta2-(pi+theta_difference)+0.0231; % findind dq update
end
end

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

id_mean=mean(id2)
iq_mean = mean(iq2)
is= sqrt(id_mean^2+iq_mean^2)
%%
if debug_mode==3
    
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
saveFolder = 'C:\Github\KTH\IEMDC-2025\Final Paper Codes\Two-Level\Waweforms'; % Replace with the actual folder pat
% folder2 =  num2str(given_parameters);  % Converts the number to a string with single quotes '123'
saveFolder=fullfile(saveFolder,given_parameters);

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

Length=1000;
theta= linspace(0,2*pi,Length); % Electrical angle in radians (change as per the rotor position or time-varying angle)

%% Time domain currents
% Given d-axis and q-axis currents (id, iq)
id = -224.33; % Example d-axis current value
iq = 325.97; % Example q-axis current value
% Inverse Park Transformation: dq to alpha-beta
ialpha = id * cos(theta) - iq * sin(theta);
ibeta = id * sin(theta) + iq * cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
i_a = ialpha;
i_b = -0.5 * ialpha + (sqrt(3) / 2) * ibeta;
i_c = -0.5 * ialpha - (sqrt(3) / 2) * ibeta;

figure('Name','Time Domain Currents')
plot(theta,i_a)
hold on; 
plot(theta,i_b)
hold on; 
plot(theta,i_c)

%% Time Domain voltages 
% Given d-axis and q-axis voltages (vd, vq)
vd = -138.8; %  d-axis voltage value
vq = 94.9; %  q-axis voltage value
% Inverse Park Transformation: dq to alpha-beta
valpha = vd * cos(theta) - vq * sin(theta);
vbeta = vd * sin(theta) + vq * cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
v_a = valpha;
v_b = -0.5 * valpha + (sqrt(3) / 2) * vbeta;
v_c = -0.5 * valpha - (sqrt(3) / 2) * vbeta;

figure('Name','Time Domain Voltages')
plot(theta,v_a)
hold on; 
plot(theta,v_b)
hold on; 
plot(theta,v_c)

%%
figure('Name','Phase-A Current and Voltage')
plot(theta,i_a)
hold on; 
plot(theta,v_a)
%% Modulation index
Vdc= 625; % DC link voltage
ma=2*max(v_a)/Vdc; % modulation index
peak_phase_current= max(i_a); % peak phase current

%% Power Factor Calculation
% Calculate apparent power (S) in dq frame
S = vd * id + vq * iq; % Real power in dq
V_magnitude = sqrt(vd^2 + vq^2); % Magnitude of voltage vector
I_magnitude = sqrt(id^2 + iq^2); % Magnitude of current vector

% Calculate power factor
power_factor = S / (V_magnitude * I_magnitude);

%% Electrical Frequency
% Given values
RPM = 3000; % Rotational speed in RPM
p = 6; % Number of pole pairs

% Calculate electrical frequency
fe = (RPM * p) / 60;

%% Display results
clc
fprintf('modulation index: %.4f\n', ma);
fprintf('Power factor: %.4f\n', power_factor);
fprintf('Electrical Frequency: %.2f Hz\n', fe);
fprintf('DC-link Voltage: %.2f V\n', Vdc);
fprintf('Peak phase current: %.2f A\n', peak_phase_current);


%%
Ld= 61.1e-6;
Lq=209e-6;

vd_machine= vd+id*Ld*fe*2*pi;
vq_machine=vq-Lq*iq*fe*2*pi; 

% Inverse Park Transformation: dq to alpha-beta
valpha_machine = vd_machine * cos(theta) - vq_machine * sin(theta);
vbeta_machine = vd_machine * sin(theta) + vq_machine * cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
v_a_machine = valpha_machine;
v_b_machine = -0.5 * valpha_machine + (sqrt(3) / 2) * vbeta_machine;
v_c_machine = -0.5 * valpha_machine - (sqrt(3) / 2) * vbeta_machine;


figure('Name','Time Domain Voltages of EM')
plot(theta,v_a_machine)
hold on; 
plot(theta,v_b_machine)
hold on; 
plot(theta,v_c_machine)

%%


figure('Name','Time Domain Voltages')
plot(theta,v_a_machine,'r')
hold on; 
plot(theta,v_a,'b')
hold on; 

%% phases

theta_backEMF = atan2(vq_machine, vd_machine);
% theta_backEMF = rad2deg(theta_backEMF)
v_max_back_emf= max(v_a_machine);

theta_voltage = atan2(vq, vd);
% theta_voltage = rad2deg(theta_voltage)


theta_current = atan2(iq, id);
% theta_current = rad2deg(theta_current)


theta_difference= theta_voltage-theta_backEMF;


%%
resistance= max(v_a_machine)*power_factor/max(i_a);




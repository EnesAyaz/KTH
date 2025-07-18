% Example parameters
fs = 1e7;       % 10 MHz sampling
fsw = 10e3;        % 10 kHz switching

theta_fund=10;
theta_fund = theta_fund * pi / 180;
Ipp = 100;
pf = 0.9;
load_angle = acos(pf);
ma = 0.8;


n_points = 360; % Number of points for theta_b and theta_c
theta_b_values = linspace(0,360, n_points);
theta_c_values = linspace(0, 360, n_points);


% Initialize RMS current matrix
I_rms_matrix = zeros(n_points, n_points);

theta_fund_x=[];
optimum_theta_b_tot= [];
optimum_theta_c_tot= [];
optimum_theta_b_first= [];
optimum_theta_c_first= [];
optimum_theta_b_second= [];
optimum_theta_c_second= [];

optimum_theta_RMS=[];
optimum_theta_RMS_first=[];
optimum_theta_RMS_second=[];

for i = 1:1:n_points  
for j = 1:1:n_points  

shiftB = theta_b_values(i)*pi/180;     % in radians
shiftC = theta_b_values(j)*pi/180;      % in radians

% Generate carriers
[t, carrierA,carrierB,carrierC] = generate_triangular_carriers(fs, fsw, shiftB, shiftC);

% Fundamental currents (sinusoidal)
Ia = Ipp * cos(theta_fund - load_angle);
Ib = Ipp * cos(theta_fund - 2*pi/3 - load_angle);
Ic = Ipp * cos(theta_fund + 2*pi/3 - load_angle);

Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));

Ibx=Ib./(abs(Ia)+abs(Ib)+abs(Ic));

Icx=Ic./(abs(Ia)+abs(Ib)+abs(Ic));

Ia=Iax;
Ib=Ibx;
Ic=Icx;

% Modulation index and duty cycles

Va_ref = ma * cos(theta_fund);
Vb_ref = ma * cos(theta_fund - 2*pi/3);
Vc_ref = ma * cos(theta_fund + 2*pi/3);

Ica = Ia * (Va_ref > carrierA);
Icb = Ib * (Vb_ref > carrierB);
Icc = Ic * (Vc_ref > carrierC);
Ic_total=Ica+Icb+Icc-mean(Ica+Icb+Icc);


Ic_RMS=rms(Ic_total);

I_rms_matrix(i, j) = Ic_RMS;

end
end

[min_value, linear_index] = min(I_rms_matrix(:));

% Convert linear index to row and column subscripts
[row_index, col_index] = ind2sub(size(I_rms_matrix), linear_index);

theta_fund_x=[theta_fund_x theta_fund];
optimum_theta_b_tot= [optimum_theta_b_tot theta_b_values(col_index)];
optimum_theta_c_tot= [optimum_theta_c_tot theta_c_values(row_index)];
optimum_theta_RMS=[optimum_theta_RMS, min_value];

RMS_00= I_rms_matrix(1,1);

%%
shiftB=optimum_theta_b_tot*pi/180;
shiftC=optimum_theta_c_tot*pi/180;

[t, carrierA,carrierB,carrierC] = generate_triangular_carriers(fs, fsw, shiftB, shiftC);

% Fundamental currents (sinusoidal)
Ia = Ipp * cos(theta_fund - load_angle);
Ib = Ipp * cos(theta_fund - 2*pi/3 - load_angle);
Ic = Ipp * cos(theta_fund + 2*pi/3 - load_angle);

Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));

Ibx=Ib./(abs(Ia)+abs(Ib)+abs(Ic));

Icx=Ic./(abs(Ia)+abs(Ib)+abs(Ic));

Ia=Iax;
Ib=Ibx;
Ic=Icx;

% Modulation index and duty cycles

Va_ref = ma * cos(theta_fund);
Vb_ref = ma * cos(theta_fund - 2*pi/3);
Vc_ref = ma * cos(theta_fund + 2*pi/3);

Ica = Ia * (Va_ref > carrierA);
Icb = Ib * (Vb_ref > carrierB);
Icc = Ic * (Vc_ref > carrierC);
Ic_total=Ica+Icb+Icc-mean(Ica+Icb+Icc);


da = (Va_ref > carrierA);
db= (Vb_ref > carrierB);
db = (Vc_ref > carrierC);


%%
figure;
plot(t, carrierA, 'b', 'LineWidth', 1.5); hold on;
plot(t, carrierB, 'r', 'LineWidth', 1.5);
plot(t, carrierC, 'g', 'LineWidth', 1.5);
yline( Va_ref, 'b--', 'LineWidth', 1.5); hold on;
yline(Vb_ref, 'r--', 'LineWidth', 1.5); hold on;
yline(Vc_ref, 'g--', 'LineWidth', 1.5); hold on;
hold off;
legend('u_{carrA} (0°)', sprintf('u_{carrB} (%.0f°)', rad2deg(shiftB)), ...
       sprintf('u_{carrC} (%.0f°)', rad2deg(shiftC)), 'u_A','u_B','u_C');
xlabel('Time (s)'); ylabel('Normalized Voltage');
title('Phase-Shifted Triangular Carriers and Voltage References');
grid on;
xlim([0 1/fsw]);  % Show one complete period
%%

figure;
plot(t, Ica, 'b', 'LineWidth', 1.5); hold on;
plot(t, Icb, 'r', 'LineWidth', 1.5);
plot(t, Icc, 'g', 'LineWidth', 1.5);
hold off;
legend('I_{legA}','I_{legB}','I_{legC}');
xlabel('Time (s)'); ylabel(' Normalized Current');
title('Leg Currents');
grid on;
xlim([0 1/fsw]);  % Show one complete period

%%
figure;
plot(t, Ic_total,'k', 'LineWidth', 1.5);
legend('Ic');
xlabel('Time (s)'); ylabel('Normalized Current');
title('Capacitor Current');
grid on;
xlim([0 1/fsw]);  % Show one complete period

rms(Ic_total)

%%


%%
shiftB=0;
shiftC=0;

[t, carrierA,carrierB,carrierC] = generate_triangular_carriers(fs, fsw, shiftB, shiftC);

% Fundamental currents (sinusoidal)
Ia = Ipp * cos(theta_fund - load_angle);
Ib = Ipp * cos(theta_fund - 2*pi/3 - load_angle);
Ic = Ipp * cos(theta_fund + 2*pi/3 - load_angle);

Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));

Ibx=Ib./(abs(Ia)+abs(Ib)+abs(Ic));

Icx=Ic./(abs(Ia)+abs(Ib)+abs(Ic));

Ia=Iax;
Ib=Ibx;
Ic=Icx;

% Modulation index and duty cycles

Va_ref = ma * cos(theta_fund);
Vb_ref = ma * cos(theta_fund - 2*pi/3);
Vc_ref = ma * cos(theta_fund + 2*pi/3);

Ica = Ia * (Va_ref > carrierA);
Icb = Ib * (Vb_ref > carrierB);
Icc = Ic * (Vc_ref > carrierC);
Ic_total=Ica+Icb+Icc-mean(Ica+Icb+Icc);

da = (Va_ref > carrierA);
db= (Vb_ref > carrierB);
db = (Vc_ref > carrierC);


%%
figure;
plot(t, carrierA, 'k', 'LineWidth', 1.5); hold on;
% plot(t, carrierB, 'r', 'LineWidth', 1.5);
% plot(t, carrierC, 'g', 'LineWidth', 1.5);
yline( Va_ref, 'b--', 'LineWidth', 1.5); hold on;
yline(Vb_ref, 'r--', 'LineWidth', 1.5); hold on;
yline(Vc_ref, 'g--', 'LineWidth', 1.5); hold on;
hold off;
legend('u_{carr}', 'u_A','u_B','u_C');
xlabel('Time (s)'); ylabel('Normalized Voltage');
title('Single Triangular Carrier and Voltage References');
grid on;
xlim([0 1/fsw]);  % Show one complete period
%%

figure;
plot(t, Ica, 'b', 'LineWidth', 1.5); hold on;
plot(t, Icb, 'r', 'LineWidth', 1.5);
plot(t, Icc, 'g', 'LineWidth', 1.5);
hold off;
legend('I_{legA}','I_{legB}','I_{legC}');
xlabel('Time (s)'); ylabel(' Normalized Current');
title('Leg Currents');
grid on;
xlim([0 1/fsw]);  % Show one complete period

%%
figure;
plot(t, Ic_total,'k', 'LineWidth', 1.5);
legend('Ic');
xlabel('Time (s)'); ylabel('Normalized Current');
title('Capacitor Current');
grid on;
xlim([0 1/fsw]);  % Show one complete period

rms(Ic_total)



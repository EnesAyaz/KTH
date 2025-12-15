%% Load data
filename = 'C:\Users\enesa\KTH\Shahriar Sarmast Ghahfarokhi - Calorimetric results\8Dec\test011.xlsx';

% Import with datetime time column
opts = detectImportOptions(filename);
opts = setvartype(opts, 1, 'datetime');   % make sure first column is datetime
opts = setvaropts(opts, 1, 'InputFormat', 'yyyy-MM-dd HH:mm:ss');

T = readtable(filename, opts);

% Time vector in seconds from start
time_dt = T{:,1};                      % datetime
t = seconds(time_dt - time_dt(1));     % t(1) = 0 s
dt = mean(diff(t));                    % sample time [s]
fs = 1/dt;                             % sampling frequency [Hz]

% ---- NUMERIC DATA ----
% Only take columns 2..10 as numeric array
A = T{:, 2:10};     % this avoids the datetime issue

P_loss_el   = A(:,1);   % loss calculation (electrical)
T_in_raw    = A(:,2);   % inlet temperature [°C]
T_out_raw   = A(:,3);   % outlet temperature [°C]
flow_raw    = A(:,4);   % flow rate [e.g. L/min]
I_rms       = A(:,5);   % RMS current
V_dc        = A(:,6);   % DC link voltage
dT_raw      = A(:,7);   % temperature difference (if already in file)
P_loss_tot  = A(:,8);   % total loss (if present)
f_sw        = A(:,9);   % switching frequency

% ---- FILTER DESIGN ----
fc = 0.02;                 % example cutoff [Hz] – tune this!
Wn = fc/(fs/2);
[b,a] = butter(2, Wn, 'low');

% Filter signals
T_in  = filtfilt(b,a,T_in_raw);
T_out = filtfilt(b,a,T_out_raw);
flow  = filtfilt(b,a,flow_raw);
dT    = T_out - T_in;
dT_raw= T_out_raw-T_in_raw;
% ---- CALORIMETRIC LOSS ----
% Assume flow in L/min, water coolant
rho = 1000;        % kg/m^3
cp  = 4180;        % J/(kg*K)

% L/min -> m^3/s -> kg/s
m_dot_raw= flow_raw * 1e-3 / 60 * rho;   % [kg/s]
m_dot = flow * 1e-3 / 60 * rho;   % [kg/s]

% Calorimetric power
P_cal = m_dot .* cp .* dT;        % [W]
P_cal_raw= m_dot_raw.*cp.*dT_raw; % [W]

%% ---- COLORS (similar style to col800 / col1200) ----
col_raw = [0.36 0.54 0.75];   % filtered (lighter)
col_filt  = [0.18 0.32 0.52];   % raw (darker)

% ---- FIGURE ----
figure('Color','w','Position',[160 90 1200 720],'Renderer','painters');

fsz = 22;    % global axis font size
lw_raw = 2;
lw_flt = 2;

t=t;

Xlimit = 400;   % time limit in seconds
Xlimbe= 0;
subplot(2,1,1);

% Temperature difference (left y-axis)
yyaxis left;
plot(t, T_out_raw - T_in_raw, 'LineWidth',lw_raw, 'Color',col_raw); hold on;
ylabel('\Delta T = T_{out}-T_{in} [°C]');
set(gca,'YColor',col_raw);  % color of left axis ticks
set(gca,'YColor',[0 0 0]);  % keep flow axis black (optional)
% ylim([0 5])

% Flow (right y-axis)
yyaxis right;
plot(t, flow_raw , 'LineWidth',lw_raw, 'Color',col_filt); hold on;
ylabel('Flow [L/min]');
 set(gca,'YColor',col_filt);  % keep flow axis black (optional)
 set(gca,'YColor',[0 0 0]);  % keep flow axis black (optional)
% ylim([0 4])

grid on; box on;
% title('\Delta T and Flow Rate');
set(gca,'FontName','Times New Roman','FontSize',fsz,'TickDir','out');
xlim([Xlimbe Xlimit]);

% Optional legend
yyaxis left;
legend({'\DeltaT','Flow Rate'}, ...
       'Location','best','Box','on');

subplot(2,1,2);
plot(t, P_cal_raw, 'LineWidth',lw_raw, 'Color',col_raw); hold on;
% plot(t, P_cal, '--',    'LineWidth',lw_flt, 'Color',col_filt);
grid on; box on;
ylabel('Power [W]');
xlabel('Time [s]');
% title('Calorimetric Power');
set(gca,'YColor',[0 0 0]);  % keep flow axis black (optional)
set(gca,'FontName','Times New Roman','FontSize',fsz,'TickDir','out');
legend({'Calorimetric Loss Calculation','filtered'}, 'Location','best', 'Box','on');
xlim([Xlimbe Xlimit]);
% ylim([0 1200])


%%
% figure 
% plot(t, P_cal_raw, 'r', t, P_cal, 'b'); grid on; ylabel('Power'); xlabel('Time [s]');
% legend('raw','filtered');

%% ---- STEADY-STATE ESTIMATION ----

N = numel(t);
% Use last 10% of samples as steady-state window
idx_ss = round(0.9*N) : N;

P_cal_ss_mean     = mean(P_cal(idx_ss));
P_cal_ss_std      = std(P_cal(idx_ss));

P_cal_raw_ss_mean = mean(P_cal_raw(idx_ss));
P_cal_raw_ss_std  = std(P_cal_raw(idx_ss));

fprintf('Steady-state (filtered):   %.2f W ± %.2f W (1σ)\n', ...
        P_cal_ss_mean, P_cal_ss_std);
fprintf('Steady-state (raw):        %.2f W ± %.2f W (1σ)\n', ...
        P_cal_raw_ss_mean, P_cal_raw_ss_std);
%%
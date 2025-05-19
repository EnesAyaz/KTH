clc;
clear;


% load('ma0.75Adaptive.mat')
%load('ma0.85Adaptive.mat')
load('ma0.2Adaptive.mat')
load('ma0.4Adaptive.mat')
load('ma0.6Adaptive.mat')
load('ma0.8Adaptive.mat')
load('ma1Adaptive.mat')


time_pro=VABC.time ;
VA= VABC.signals(1).values;
VB= VABC.signals(2).values;
VC= VABC.signals(3).values;

VCM_pro=VCM.signals.values;

% load('ma0.75Interleaved.mat')
% load('ma0.85Interleaved.mat')
load('ma0.2Interleaved.mat')
load('ma0.4Interleaved.mat')
load('ma0.6Interleaved.mat')
load('ma0.8Interleaved.mat')
load('ma1Interleaved.mat')



time_conv=VABC.time ;
VA= VABC.signals(1).values;
VB= VABC.signals(2).values;
VC= VABC.signals(3).values;

VCM_conv=VCM.signals.values;



figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

bias_conv=0;
bias_pro=1.16;

plot1=plot(time_pro, VCM_pro + bias_pro); hold on;
plot2=plot(time_conv, VCM_conv + bias_conv);


set(plot1,'Color',[0.5 0 0.5]);
set(plot2,'Color',[0 0.5 0.5]);


% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0.02 0.04]);
ylim(axes1,[-0.6 1.8])
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'GridAlpha',0.25,'GridColor',...
    [0 0 0],'MinorGridAlpha',0.5,...
    'MinorGridColor',[0 0 0],...
    'XGrid','on','XMinorGrid','on','YGrid','on','YMinorGrid','on','YTick',...
    -0.5:0.167:2,'ZMinorGrid','on');

% yticks = [-0.5 -0.16 0.16 0.5  ];
% yticklabels = {'-0.5','-0.16', '0.16', '0.5'};

% X ve Y ekseni etiketlerini sıfırla
set(axes1, 'XTickLabel', {}, 'YTickLabel', {});
%%
rms(VCM_conv)
rms(VCM_pro)


%%

L= length(VCM_pro);
VCM_pro= VCM_pro(L/2: end);
VCM_conv= VCM_conv(L/2: end);
time_pro=time_pro(L/2: end);
time_conv=time_conv(L/2: end);
              
% Define a new uniform time grid (Fs = desired sampling rate)
Fs_new = 5e6; % Example: 100 kHz (adjust based on your signal)
t_uniform = min(time_pro):1/Fs_new:max(time_pro);

% Resample signals using interpolation
VCM_pro_uniform = interp1(time_pro, VCM_pro, t_uniform, 'linear', 'extrap');
VCM_conv_uniform = interp1(time_conv, VCM_conv, t_uniform, 'linear', 'extrap');

% Now compute FFT on uniformly sampled data
N = length(t_uniform);
f = (0:N-1)*(Fs_new/N); % Frequency axis (Hz)

% Compute FFT (no normalization)
VCM_pro_fft = abs(fft(VCM_pro_uniform));
VCM_conv_fft = abs(fft(VCM_conv_uniform));

% Single-sided spectrum
VCM_pro_fft = VCM_pro_fft(1:N/2+1)/N;
VCM_pro_fft(2:end-1) = 2*VCM_pro_fft(2:end-1);

VCM_conv_fft = VCM_conv_fft(1:N/2+1)/N;
VCM_conv_fft(2:end-1) = 2*VCM_conv_fft(2:end-1);

f = f(1:N/2+1);

% % Plot
% figure;
% hold on;
% plot(f/50, VCM_pro_fft, 'Color', [0.75 0 0.75], 'DisplayName', 'Adaptive');
% plot(f/50, VCM_conv_fft, 'Color', [0 0.75 0.75], 'DisplayName', 'Interleaved');
% xlabel('Frequency (Hz)');
% ylabel('Magnitude');
% title('FFT of CMV (Resampled Uniformly)');
% xlim([50 500]); % Adjust based on your needs
% ylim([0 0.5])
% legend;
% grid on;

%%

figure2 = figure;

% Create axes
axes2 = axes('Parent',figure2);
hold(axes2,'on');

plot(f/50, VCM_pro_fft, 'Color', [0.5 0 0.5], 'DisplayName', 'The Proposed Method', 'LineWidth', 1);
hold on;
plot(f/50, VCM_conv_fft, 'Color', [0 0.5 0.5], 'DisplayName', 'The Conventional Interleaved SPWM', 'LineWidth', 1);
xlim([50 550]);  % Focus on first few switching harmonics
grid on;

% Add custom x-ticks for switching frequency and harmonics
fsw = 100;  % Your switching frequency (adjust if different)
xticks = [fsw, 2*fsw, 3*fsw, 4*fsw, 5*fsw];
xticklabels = {'f_{sw}', '2f_{sw}', '3f_{sw}', '4f_{sw}', '5f_{sw}'};

set(axes2, ...
    'FontName', 'Times New Roman', ...
    'FontSize', 15);

% Set custom x-ticks for switching harmonics
fsw = 100;  % Your switching frequency
xticks = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000];
xticklabels = {'f_{sw}', '2f_{sw}', '3f_{sw}', '4f_{sw}', '5f_{sw}', ...
              '6f_{sw}', '7f_{sw}', '8f_{sw}', '9f_{sw}', '10f_{sw}'};
set(axes2, 'XTick', xticks, 'XTickLabel', xticklabels);

% Add legend
legend(axes2, 'show', 'Location', 'northeast', 'FontName', 'Times New Roman', 'FontSize', 15);
ylim([0 0.25])
% xlim[50 600]


% Axis labels
% xlabel('Frequency (Hz)', 'FontName', 'Times New Roman', 'FontSize', 15);
% ylabel('Magnitude', 'FontName', 'Times New Roman', 'FontSize', 15);
% title('CMV Frequency Spectrum', 'FontName', 'Times New Roman', 'FontSize', 15);

% hold(axes1, 'off');
% % Highlight the switching harmonics with vertical lines
% for k = 1:length(xticks)
%     xline(xticks(k), '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.5);
% end

% legend('Proposed Adaptive', 'Conventional Interleaved', 'Location', 'northeast');

% Calculate and display harmonic components at switching frequencies
% fprintf('\nHarmonic Components at Switching Frequencies:\n');
% fprintf('%-10s %-20s %-20s\n', 'Freq (Hz)', 'Adaptive (dB)', 'Interleaved (dB)');
% 
% for k = 1:5
%     freq = k*fsw;
%     [~, idx] = min(abs(f - freq));
%     adaptive_val = 20*log10(VCM_pro_fft(idx));
%     conv_val = 20*log10(VCM_conv_fft(idx));
% 
%     fprintf('%-10d %-20.2f %-20.2f\n', freq, adaptive_val, conv_val);
% end


%%
harmonic_range = (f > 50) & (f <= Fs_new/2);
% Get harmonic frequencies and orders
harmonic_freqs = f(harmonic_range);
harmonic_orders = harmonic_freqs / 50;

WTHD0_pro = sqrt(sum((VCM_pro_fft(harmonic_range)./harmonic_orders).^2))
WTHD0_conv = sqrt(sum((VCM_conv_fft(harmonic_range)./harmonic_orders).^2)) 

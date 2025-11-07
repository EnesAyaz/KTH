%% ===================== Loss vs Switching Frequency (Total / Inverter / Harmonic) =====================

load('C:\Github\KTH\Loss Calculations\2000V\motorlosses\savePM.mat')
load('C:\Github\KTH\Loss Calculations\2000V\motorlosses\savefsw1.mat')
load('C:\Github\KTH\Loss Calculations\2000V\savefsw_tot.mat')
load('C:\Github\KTH\Loss Calculations\2000V\savePfsw.mat')

P_tot = P_fsw + P_M;

% --- Dull blue color palette ---
cH  = [80 110 160]/255;    % Harmonic loss – medium blue
cI  = [120 150 190]/255;   % Inverter loss – light blue
cT  = [40 60 90]/255;      % Total loss – dark blue-gray

% --- Figure setup ---
f1 = figure('Color','w','Position',[220 180 780 520],'Renderer','painters');
ax1 = axes('Parent',f1); 
hold(ax1,'on'); box(ax1,'on'); grid(ax1,'on');

% --- Plot losses ---
p1 = plot(fsw1/1e3, P_M, '-<',  'Color', cH, 'MarkerFaceColor', cH, ...
          'LineWidth', 2.2, 'MarkerSize', 7, 'DisplayName','Motor Harmonic');
p2 = plot(fsw_tot/1e3, P_fsw, '-v',  'Color', cI, 'MarkerFaceColor', cI, ...
          'LineWidth', 2.2, 'MarkerSize', 7, 'DisplayName','Inverter');
p3 = plot(fsw_tot/1e3, P_tot, '-*',  'Color', cT, ...
          'LineWidth', 2.4, 'MarkerSize', 8, 'DisplayName','Total');

% --- Axes formatting ---
xlim([min(fsw_tot)/1e3 max(fsw_tot)/1e3]);
ylim([0 max(P_tot)*1.1]);
set(ax1, 'FontName','Times New Roman', 'FontSize',20, ...
          'LineWidth',1.2, ...
          'GridAlpha',0.25, 'MinorGridAlpha',0.15, ...
          'XGrid','on','YGrid','on', ...
          'XMinorTick','on','YMinorTick','on');

xlabel('Switching Frequency (kHz)', 'FontName','Times New Roman', 'FontSize',20);
ylabel('Losses (W)', 'FontName','Times New Roman', 'FontSize',20);

% --- Legend ---
leg = legend([p3 p2 p1], 'Location','northwest'); % Total first for clarity
leg.Box = 'off';
leg.FontName = 'Times New Roman';
leg.FontSize = 18;
leg.TextColor = [30 40 60]/255;

% % --- Export as vector ---
% exportgraphics(f1, 'Loss_vs_SwitchingFrequency_Blue.pdf', ...
%                'ContentType','vector', ...
%                'BackgroundColor','white');
%%


%% ===================== Inverter Loss vs Switching Frequency =====================
load('C:\Github\KTH\Loss Calculations\2000V\savefsw_tot.mat')
load('C:\Github\KTH\Loss Calculations\2000V\savePfsw.mat')

fsw_tot = 1e3*[7 10 15 19];     % known fsw points (Hz)
P_fsw   = [1700 2300 3200 3900];    % known losses (W)

% New frequency vector from 5 kHz to 30 kHz:
fsw_vec = 1e3 * (5:1:30);    

% Interpolate + extrapolate (linear)
P_interp = interp1(fsw_tot, P_fsw, fsw_vec, 'linear', 'extrap');


fsw_tot=fsw_vec;
P_fsw=P_interp;


% --- Dull blue tone (same family as previous plots) ---
cInv = [70 100 150]/255;

% --- Figure setup ---
f2 = figure('Color','w','Position',[220 180 780 520],'Renderer','painters');
ax2 = axes('Parent',f2); 
hold(ax2,'on'); box(ax2,'on'); grid(ax2,'on');

% --- Plot inverter losses ---
plot(fsw_tot/1e3, P_fsw, '-o', ...
     'Color', cInv, ...
     'MarkerFaceColor', cInv, ...
     'LineWidth', 2.2, ...
     'MarkerSize', 7);

% --- Axes formatting ---
xlim([min(fsw_tot)/1e3 max(fsw_tot)/1e3]);
ylim([0 max(P_fsw)*1.1]);
set(ax2, 'FontName','Times New Roman', 'FontSize',20, ...
          'LineWidth',1.2, ...
          'GridAlpha',0.25, 'MinorGridAlpha',0.15, ...
          'XGrid','on','YGrid','on', ...
          'XMinorTick','on','YMinorTick','on');

xlabel('Switching Frequency (kHz)', 'FontName','Times New Roman', 'FontSize',20);
ylabel('Inverter Loss (W)', 'FontName','Times New Roman', 'FontSize',20);

% --- Optional annotation: optimum switching range (e.g., 14–16 kHz) ---
xOpt = [14 16];
% patch([xOpt(1) xOpt(2) xOpt(2) xOpt(1)], ...
%       [0 0 max(P_fsw)*1.1 max(P_fsw)*1.1], ...
%       [200 220 255]/255, 'FaceAlpha',0.15, 'EdgeColor','none');
% text(mean(xOpt), max(P_fsw)*0.9, 'Optimum range', ...
%      'FontName','Times New Roman', 'FontSize',16, ...
%      'Color',[40 60 90]/255, 'HorizontalAlignment','center');

% --- Export as vector PDF ---
exportgraphics(f2, 'InverterLoss_vs_Fsw_Blue.pdf', ...
               'ContentType','vector', ...
               'BackgroundColor','white');


%% Time window to crop
t_start = 1/ffund;   % [s]
t_end   = 3/ffund;   % [s]
t_switch = 2/ffund;   % [s]

%% Extract time vector
t = out.ScopeData10.time(:);

%% Extract signals based on your order
i_cap     = out.ScopeData10.signals(1).values(:)  ;   % Capacitor current
i_cap_rms = out.ScopeData10.signals(2).values(:)  ;   % Capacitor RMS current
v_cap     = out.ScopeData10.signals(3).values(:)  ;   % Capacitor voltage
i_bat     = out.ScopeData10.signals(4).values(:)  ;   % Battery current

%% Crop window
idx = (t >= t_start) & (t <= t_end);

t_crop = t(idx)-t_start;
t_switch=t_switch-t_start;
t_end= t_end -t_start;
t_start=0;

i_cap_crop = i_cap(idx);
i_rms_crop = i_cap_rms(idx);
v_cap_crop = v_cap(idx);
i_bat_crop = i_bat(idx);

%% IEEE style settings
set(groot,'defaultAxesFontName','Times New Roman')
set(groot,'defaultTextFontName','Times New Roman')

fs = 14;       % font size
lw = 1.5;     % line width

% Professional color palette
c1 = [0 0.4470 0.7410];   % blue
c2 = [0.8500 0.3250 0.0980]; % orangec
c3 = [0.4660 0.6740 0.1880]; % green
c4 = [0.4940 0.1840 0.5560]; % purple

% Colors matching the reference figure
c2   = [0 0.25 0.75];
c1  = [0 0.6 0.2];
c3   = [0 0.65 0.65];
c4 = [0.55 0.1 0.55];

%% Create figure sized for IEEE column
figure('Color','w','Units','centimeters','Position',[10 10 20 20])

tiledlayout(4,1,'TileSpacing','compact','Padding','compact')

%% Capacitor current
ax1 = nexttile;
plot(t_crop,i_cap_crop,'Color',c1,'LineWidth',lw)
grid on
ylabel('i_{cap} [A]')
title('Capacitor Current')
xlim([t_start t_end])
ylim([min(i_cap_crop) 1.1*max(i_cap_crop)])
xline(t_switch,'k--','LineWidth',1)

%% Capacitor RMS current
ax2 = nexttile;
plot(t_crop,i_rms_crop,'Color',c2,'LineWidth',lw)
grid on
ylabel('i_{cap,RMS} [A]')
title('Capacitor RMS Current')
xlim([t_start t_end])
ylim([min(i_rms_crop) max(i_rms_crop)])
xline(t_switch,'k--','LineWidth',1)

%% Capacitor voltage
ax3 = nexttile;
plot(t_crop,v_cap_crop,'Color',c3,'LineWidth',lw)
grid on
ylabel('v_{cap} [V]')
title('Capacitor Voltage')
xlim([t_start t_end])
ylim([min(v_cap_crop) max(v_cap_crop)])
xline(t_switch,'k--','LineWidth',1)

%% Battery current
ax4 = nexttile;
plot(t_crop,i_bat_crop,'Color',c4,'LineWidth',lw)
grid on
ylabel('i_{bat} [A]')
xlabel('Time [s]')
title('Battery Current')
xlim([t_start t_end])
ylim([min(i_bat_crop) max(i_bat_crop)])
xline(t_switch,'k--','LineWidth',1)

set([ax1 ax2 ax3 ax4],'FontSize',fs)

linkaxes([ax1 ax2 ax3 ax4],'x')



%% Add method labels to the last subplot
axes(ax4)

yl = ylim;
y_text = yl(1) + 0.05*(yl(2)-yl(1));   % slightly above bottom

% Left side label
text((t_start+t_switch)/2 , y_text , ...
    'Conventional Method', ...
    'HorizontalAlignment','center', ...
    'VerticalAlignment','bottom', ...
    'FontSize',fs-1, ...
    'BackgroundColor','white', ...
    'EdgeColor','black');

% Right side label
text((t_switch+t_end)/2 , y_text , ...
    'Proposed Method', ...
    'HorizontalAlignment','center', ...
    'VerticalAlignment','bottom', ...
    'FontSize',fs-1, ...
    'BackgroundColor','white', ...
    'EdgeColor','black');
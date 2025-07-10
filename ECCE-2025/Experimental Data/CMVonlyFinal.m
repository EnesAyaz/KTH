start_point=13;

time_data=Time(start_point:end);

phA_voltage=Va(start_point:end);

phB_voltage=Vb(start_point:end)*1.0196;

phC_voltage=Vc(start_point:end);
%%

plot(time_data*1e3, phA_voltage);
hold on
plot(time_data*1e3, phB_voltage);
hold on
plot(time_data*1e3, phC_voltage);
hold on
%%
plot(time_data*1e3, (phA_voltage+phB_voltage+phC_voltage)/3);
hold on
%%
close all;
%%


fs = 1 / (time_data(2) - time_data(1));  % Sampling frequency
fc = 1000e3;  % Cut-off frequency, adjust as needed

[b, a] = butter(2, fc / (fs/2), 'low');
phA_smooth = filtfilt(b, a, phA_voltage);
phB_smooth = filtfilt(b, a, phB_voltage);
phC_smooth = filtfilt(b, a, phC_voltage);
% common_mode= filtfilt(b, a, phA_voltage+phB_voltage+phC_voltage);
common_mode=(phA_smooth+phB_smooth+phC_smooth)/3;
common_mode=(phA_voltage+phB_voltage+phC_voltage)/3;
common_mode= filtfilt(b, a, (phA_voltage+phB_voltage+phC_voltage)/3);

% Bias değerleri
bias_A = 3;
bias_B = 1.5;
bias_C = 0;
bias_CM = 0;  % Ortak mod voltajı için

% Grafik
figure1 = figure( 'Position', [0 0 1500 300]);



% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');


plot4=plot(time_data*1e3, common_mode);

set(plot4,'Color',[0 0 0],'LineWidth',0.5);

% Create ylabel
ylabel({'Voltage'},'FontName','Times New Roman');

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 20]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[0.6 1.5]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',20,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'MinorGridAlpha',0.5,'MinorGridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'XGrid','on',...
    'XMinorGrid','on','XTick',[0 5 10 15 20],'YGrid','on','YMinorGrid','on',...
    'YTick',[0.68 1.38],'YTickLabel',{'-V_{DC}/6','+V_{DC}/6'},'ZMinorGrid',...
    'on');


%%

% Grafik
figure1 = figure( 'Position', [0 0 1500 300]);
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');


plot4=plot(time_data*1e3, common_mode);

set(plot4,'Color',[0 0 0],'LineWidth',0.5);

x_start=12;
x_end=x_start+0.5;
% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[x_start x_end]);
ylim(axes1,[0.6 1.5]);



% Create ylabel
ylabel({'Voltage'},'FontName','Times New Roman');

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman');

% Uncomment the following line to preserve the X-limits of the axes
% xlim(axes1,[0 20]);
% Uncomment the following line to preserve the Y-limits of the axes

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',20,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'MinorGridAlpha',0.5,'MinorGridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'XGrid','on',...
    'XMinorGrid','on','XTick',12:0.1:12.5,'YGrid','on','YMinorGrid','on',...
    'YTick',[0.68 1.38],'YTickLabel',{'-V_{DC}/6','+V_{DC}/6'},'ZMinorGrid',...
    'on');



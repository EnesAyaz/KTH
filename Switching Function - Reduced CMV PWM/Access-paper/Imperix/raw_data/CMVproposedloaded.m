opts = delimitedTextImportOptions("NumVariables", 5);

% Specify range and delimiter
opts.DataLines = [13, Inf];
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["HorizontalUnits", "us", "VarName3", "VarName4", "VarName5"];
opts.VariableTypes = ["double", "double", "double", "double","double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
opts.ConsecutiveDelimitersRule = "join";

% Import the data

SDS00001 = readtable("C:\Github\KTH\Switching Function - Reduced CMV PWM\Access-paper\Imperix\raw_data\SDS00006.csv", opts);

%% Convert to output type
data_VABC = table2array(SDS00001);

%% Clear temporary variables
clear opts

time=data_VABC(:,1);
Va=2*data_VABC(:,2);
Vb=2*data_VABC(:,3);
Vc=2*data_VABC(:,4);
IphA=50*data_VABC(:,5);

% plot(time,Va*50)
% hold on
% plot(time,Vb*50)
% plot(time,Vc*50)
% sum=(Va+Vb+Vc)*50;
% plot(time,sum)

%%

start_point=1;

time_data=time(start_point:end);

phA_voltage=Va(start_point:end);

phB_voltage=Vb(start_point:end);

phC_voltage=Vc(start_point:end);


fs = 1 / (time_data(2) - time_data(1));  % Sampling frequency
fc = 10e4;  % Cut-off frequency, adjust as needed

[b, a] = butter(2, fc / (fs/2), 'low');
phA_smooth = filtfilt(b, a, phA_voltage);
phB_smooth = filtfilt(b, a, phB_voltage);
phC_smooth = filtfilt(b, a, phC_voltage);
fc = 10e4;
[b, a] = butter(2, fc / (fs/2), 'low');
IphA_smooth= filtfilt(b, a, IphA);
%common_mode= filtfilt(b, a, phA_voltage+phB_voltage+phC_voltage);
fc = 25e4;  % Cut-off frequency, adjust as needed
fc = 10e4;  % Cut-off frequency, adjust as needed
[b, a] = butter(2, fc / (fs/2), 'low');
common_mode= filtfilt(b, a, phA_voltage+phB_voltage+phC_voltage);
% common_mode=phA_voltage+phB_voltage+phC_voltage;

% Bias değerleri
bias_A = 3-0.075;
bias_B = 0-0.0067;
bias_C = -3-0.0096;
bias_CM = -5.5;  % Ortak mod voltajı için
bias_current = -3.2;  % Ortak mod voltajı için

% Grafik
figure1 = figure;
set(gcf,'position',[0,0,1000,400])
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot1=plot(time_data*1000, phA_smooth + bias_A); hold on;
plot2=plot(time_data*1000, phB_smooth + bias_B);
plot3=plot(time_data*1000, phC_smooth + bias_C);
plot4=plot(time_data*1000, common_mode/3 + bias_CM);
plot5=plot(time_data*1000, IphA_smooth + bias_current);

set(plot1,'DisplayName','Va','Color',[0 0 1]);
set(plot2,'DisplayName','Vb','Color',[0 1 0]);
set(plot3,'DisplayName','Vc','Color',[1 0 0]);
set(plot4,'DisplayName','V_{CM}','Color',[0 0 0]);
set(plot5,'DisplayName','I_{phA}','Color',[1 0 1]);

% Create ylabel
ylabel({'Voltage (V), Current(A)'},'FontName','Times New Roman');

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 20]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[-8.5 5.5]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',18,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'MinorGridAlpha',1,'MinorGridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'YTick',...
    [-7.7 -6.2 -4.74 -4.06 -3 -1 0.072 2.04 3 5],'YTickLabel',...
    {'-1','1','33','66','-50','50','-50','50','-50','50'},'ZMinorGrid','on');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.797333334495624 0.579583339889844 0.0869999989271164 0.243749993145466],...
    'EdgeColor','none');


% Create ylabel
ylabel({'Voltage (V)'},'FontName','Times New Roman','FontSize',20);

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman','FontSize',20);
%%

figure1 = figure;
set(gcf,'position',[0,0,1000,400])
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot4=plot(time_data*1000, common_mode/3);

set(plot4,'DisplayName','V_{CM}','Color',[0 0 0]);


% Create ylabel
ylabel({'Common-Mode Voltage (V)'},'FontName','Times New Roman');

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 50]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[0.2 1.8]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',18,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'MinorGridAlpha',1,'MinorGridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'YTick',...
    [ 0.72 1.42],'YTickLabel',...
    {'-16.67','16.67'},'ZMinorGrid','on');
% Create legend
% legend1 = legend(axes1,'show');
% set(legend1,...
    % 'Position',[0.797333334495624 0.579583339889844 0.0869999989271164 0.243749993145466],...
    % 'EdgeColor','none');


% Create ylabel
ylabel({'Voltage (V)'},'FontName','Times New Roman','FontSize',20);

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman','FontSize',20);



opts = delimitedTextImportOptions("NumVariables", 5);

% Specify range and delimiter
opts.DataLines = [13+421000, Inf];
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["HorizontalUnits", "us", "VarName3", "VarName4", "VarName5"];
opts.VariableTypes = ["double", "double", "double", "double","double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
opts.ConsecutiveDelimitersRule = "join";

% Import the data

SDS00001 = readtable("C:\Github\KTH\Switching Function - Reduced CMV PWM\Access-paper\Imperix\raw_data\2025.04.23\SDS00002.csv", opts);

%% Convert to output type
data_VABC = table2array(SDS00001);

%% Clear temporary variables
clear opts

time=data_VABC(:,1);
time=time-time(1);
Va=data_VABC(:,2);
Vb=data_VABC(:,3);
Vc=data_VABC(:,4);
IphA=data_VABC(:,5);

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
fc = 10e5;  % Cut-off frequency, adjust as needed

[b, a] = butter(2, fc / (fs/2), 'low');
phA_smooth = filtfilt(b, a, phA_voltage);
phB_smooth = filtfilt(b, a, phB_voltage);
phC_smooth = filtfilt(b, a, phC_voltage);
%common_mode= filtfilt(b, a, phA_voltage+phB_voltage+phC_voltage);
fc = 25e4;  % Cut-off frequency, adjust as needed
fc = 100e4;  % Cut-off frequency, adjust as needed
fc = 100e5;  % Cut-off frequency, adjust as needed
[b, a] = butter(2, fc / (fs/2), 'low');
common_mode= filtfilt(b, a, phA_voltage+phB_voltage+phC_voltage);
% common_mode=phA_voltage+phB_voltage+phC_voltage;

% Bias değerleri
bias_A = 3-0.075;
bias_B = 0-0.0067;
bias_C = -3-0.0096;
bias_CM = -5.9;  % Ortak mod voltajı için

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


set(plot1,'DisplayName','Va','Color',[0 0 1]);
set(plot2,'DisplayName','Vb','Color',[0 1 0]);
set(plot3,'DisplayName','Vc','Color',[1 0 0]);
set(plot4,'DisplayName','V_{CM}','Color',[0 0 0]);

% Create ylabel
ylabel({'Voltage (V)'},'FontName','Times New Roman');

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 20]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[-6.25 5.5]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',18,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'MinorGridAlpha',1,'MinorGridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'YTick',...
    [-5.66 -4.98 -4.3 -3.62 -3 -1 0.072 2.04 3 5],'YTickLabel',...
    {'-50','-16','16','50','-50','50','-50','50','-50','50'},'ZMinorGrid','on');
set(axes1,'FontName','Times New Roman','FontSize',18,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'MinorGridAlpha',1,'MinorGridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'YTick',...
    [-5.86 -3.82 -3 -1 0.072 2.04 3 5],'YTickLabel',...
    {'-50','50','-50','50','-50','50','-50','50'},'ZMinorGrid','on');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.797333334495624 0.579583339889844 0.0869999989271164 0.243749993145466],...
    'EdgeColor','none');

% Create ylabel
ylabel({'Voltage (V)'},'FontName','Times New Roman','FontSize',20);

% Create xlabel
xlabel({'Time (ms)'},'FontName','Times New Roman','FontSize',20);



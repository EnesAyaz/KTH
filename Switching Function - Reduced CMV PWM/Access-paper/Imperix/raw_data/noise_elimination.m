time=data_VABC(:,1);
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
[b, a] = butter(2, fc / (fs/2), 'low');
common_mode= filtfilt(b, a, phA_voltage+phB_voltage+phC_voltage);
% common_mode=phA_voltage+phB_voltage+phC_voltage;

% Bias değerleri
bias_A = 3-0.075;
bias_B = 0-0.0067;
bias_C = -3-0.0096;
bias_CM = -5.5;  % Ortak mod voltajı için

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


set(plot1,'Color',[1 0 0]);
set(plot2,'Color',[1 0 1]);
set(plot3,'Color',[0 0 1]);
set(plot4,'Color',[0 0 0],'LineWidth',0.5);

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 20]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'GridAlpha',0.5,'GridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'MinorGridAlpha',1,...
    'MinorGridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'XGrid','off','XMinorGrid','off','YGrid','off','YMinorGrid','off','YTick',...
    [-4.75 -4.15 -3 -1 0 2 3 5],'ZMinorGrid','on');

ylim([-6 5.5])
% X ve Y ekseni etiketlerini sıfırla
%set(axes1, 'XTickLabel', {}, 'YTickLabel', {});
set(axes1,'YTickLabel', {'-33', '-66','-50', '50','-50', '50','-50', '50'});
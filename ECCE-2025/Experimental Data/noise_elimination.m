start_point=13;

time_data=Time(start_point:end);

phA_voltage=Va(start_point:end);

phB_voltage=Vb(start_point:end);

phC_voltage=Vc(start_point:end);


fs = 1 / (time_data(2) - time_data(1));  % Sampling frequency
fc = 10e6;  % Cut-off frequency, adjust as needed

[b, a] = butter(2, fc / (fs/2), 'low');
phA_smooth = filtfilt(b, a, phA_voltage);
phB_smooth = filtfilt(b, a, phB_voltage);
phC_smooth = filtfilt(b, a, phC_voltage);
common_mode= filtfilt(b, a, phA_voltage+phB_voltage+phC_voltage);
% common_mode=phA_voltage+phB_voltage+phC_voltage;

% Bias değerleri
bias_A = 3;
bias_B = 1.5;
bias_C = 0;
bias_CM = -1.5;  % Ortak mod voltajı için

% Grafik
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');


plot1=plot(time_data, phA_smooth + bias_A); hold on;
plot2=plot(time_data, phB_smooth + bias_B);
plot3=plot(time_data, phC_smooth + bias_C);
plot4=plot(time_data, common_mode/3 + bias_CM);


set(plot1,'Color',[1 0 0]);
set(plot2,'Color',[1 0 1]);
set(plot3,'Color',[0 0 1]);
set(plot4,'Color',[0 0 0],'LineWidth',0.5);


% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 0.02]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'GridAlpha',0.5,'GridColor',...
    [0.301960784313725 0.745098039215686 0.933333333333333],'MinorGridAlpha',1,...
    'MinorGridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'XGrid','on','XMinorGrid','on','YGrid','on','YMinorGrid','on','YTick',...
    [-2 -1 0 1 2 3 4 5 6],'ZMinorGrid','on');

% X ve Y ekseni etiketlerini sıfırla
set(axes1, 'XTickLabel', {}, 'YTickLabel', {});

%%





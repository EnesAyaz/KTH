load('ma0.85SingleCarrier.mat');
load('ma0.85Adaptive.mat')
load('ma0.85Interleaved.mat')

time=VABC.time ;
VA= VABC.signals(1).values;
VB= VABC.signals(2).values;
VC= VABC.signals(3).values;

VCM=VCM.signals.values;

figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

bias_A=3;
bias_B=1.5;
bias_C=0;
bias_CM=-1;

plot1=plot(time, VA + bias_A); hold on;
plot2=plot(time, VB + bias_B);
plot3=plot(time, VC + bias_C);
plot4=plot(time, VCM + bias_CM);


set(plot1,'Color',[0 0 1]);
set(plot2,'Color',[1 0 1]);
set(plot3,'Color',[0 1 0]);
set(plot4,'Color',[0 0 0],'LineWidth',0.5);


% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0.02 0.04]);
ylim(axes1,[-2  5])
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'GridAlpha',0,'GridColor',...
    [0 0 0],'MinorGridAlpha',0.5,...
    'MinorGridColor',[0 0 0],...
    'XGrid','on','XMinorGrid','on','YGrid','on','YMinorGrid','on','YTick',...
    -10:0.5:10,'ZMinorGrid','on');

% X ve Y ekseni etiketlerini sıfırla
set(axes1, 'XTickLabel', {}, 'YTickLabel', {});

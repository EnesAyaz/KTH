%% Operating point-1 

fsw1= [10200 15300 20400 25500 30600 ];

Loss1= [818 1001 1185 1368 1552];

fsw2= [10000 15000 20000 25000 30000 ];

Loss2= [412 531 647 763 879];



figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(fsw1/1e3,Loss1);
plot2= plot(fsw2/1e3,Loss2);
xlim([5 35])
ylim([0 1750])
set(plot1,'DisplayName','Operating Point 1','MarkerSize',15,...
    'Marker','pentagram',...
    'LineWidth',0.1,...
    'Color',[0 0 1]);
set(plot2,'DisplayName','Operating Point 2','MarkerSize',10,...
    'Marker','diamond',...
    'LineWidth',0.2,...
    'Color',[1 0 0]);

% Create ylabel
ylabel({'Inverter Loss (W)'});

% Create xlabel
xlabel({'Switching Frequency (kHz)'});

box(axes1,'on');
grid(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.25,...
    'GridColor',[1 0 1],'MinorGridColor',[1 0 1],'MinorGridLineWidth',0.25,...
    'XMinorGrid','on','YMinorGrid','on','YTick',...
    [0 250 500 750 1000 1250 1500 1750],'ZMinorGrid','on');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.55863095682469 0.178174606154837 0.319642850330898 0.110714282734054]);




load('C:\Github\KTH\Loss Calculations\2000V\motorlosses\savePM.mat')
load('C:\Github\KTH\Loss Calculations\2000V\motorlosses\savefsw1.mat')
load('C:\Github\KTH\Loss Calculations\2000V\savefsw_tot.mat')
load('C:\Github\KTH\Loss Calculations\2000V\savePfsw.mat')

%%
P_tot= P_fsw+P_M;

% plot(fsw1/1e3, P_M)
% hold on
% plot(fsw_tot/1e3, P_fsw)
% hold on;
% plot(fsw_tot/1e3,P_tot)


figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create multiple line objects using matrix input to plot
plot1 = plot(fsw1/1e3, P_M,'LineWidth',2,'Parent',axes1);
plot2 = plot(fsw_tot/1e3, P_fsw,'LineWidth',2,'Parent',axes1);
plot3 = plot(fsw_tot/1e3,P_tot,'LineWidth',2,'Parent',axes1);

set(plot1,'DisplayName','Harmonic','Marker','<','Color',[0 0 1]);
set(plot2,'DisplayName','Inverter','Marker','v','Color',[1 0 0]);
set(plot3,'DisplayName','Total','Marker','*','Color',[0 0 0]);

% The following line demonstrates an alternative way to create a data tip.
% datatip(plot1(3),14,1940.38562273101);
% Create datatip
% datatip(plot1(3),'DataIndex',10,'Location','northeast');

% Create ylabel
ylabel({'Losses (W)'});

% Create xlabel
xlabel({'Switching Frequency (kHz)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.599702383906003 0.296031750502094 0.21964285331113 0.161904757434414]);

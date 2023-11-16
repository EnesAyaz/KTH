
fs=1/(time(2)-time(1));
flp=100e6;
[Vgs_lp, lp]= lowpass(Vgs,flp,fs);
[Vds_lp, lp]= lowpass(Vds,flp,fs);
[Id_lp, lp]= lowpass(Id,flp,fs);

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
colororder([0 0.447 0.741]);
% Activate the left side of the axes
yyaxis(axes1,'left');
% Create multiple line objects using matrix input to plot
plot1 = plot(time*1e6,10*Vgs_lp,'LineStyle','-','LineWidth',1);
plot2 =  plot(time*1e6,Vds_lp,'LineStyle','-','LineWidth',1);

set(plot1,'DisplayName','10 xV_{GS}','Color',[1 0 0]);
set(plot2,'DisplayName','V_{DS}','Color',[0 0 1]);

% Create ylabel
ylabel({'Voltage (V)'});

% Set the remaining axes properties
set(axes1,'YColor',[0 0 1]);
% Activate the right side of the axes
yyaxis(axes1,'right');
% Create plot
plot(time*1e6,Id_lp,'DisplayName','I_{D}','LineWidth',1,'Color',[0 0 0]);

% Create ylabel
ylabel({'Current (A)'});

% Set the remaining axes properties
set(axes1,'YColor',[0 0 0]);
% Create xlabel
xlabel({'Time (\mus)'});

title(tit)


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.658630955121701 0.44603175135359 0.205357139451163 0.219047612874281]);

clearvars -except Vgs Vds Id time





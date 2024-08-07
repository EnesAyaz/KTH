load('Ids_Vds_25.mat')
IdsVds25=IdsVds;
clear IdsVds

load('Ids_Vds_125.mat')
IdsVds125=IdsVds;
clear IdsVds

load('Ids_Vds_175.mat')
IdsVds175=IdsVds;
clear IdsVds

%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(IdsVds25.I, IdsVds25.V,'DisplayName','Tj=25 C^o','Marker','x','LineWidth',0.1,...
    'Color',[1 0 0]);
% Create plot
plot(IdsVds125.I, IdsVds125.V,'DisplayName','Tj=125 C^o','Marker','x','LineWidth',0.1,...
    'Color',[0 0 1]);
%
plot(IdsVds175.I, IdsVds175.V,'DisplayName','Tj=175 C^o','Marker','x','LineWidth',0.1,...
    'Color',[1 0 1]);
% Create ylabel
ylabel({'Drain-Source Voltage (V)'});
% Create xlabel
xlabel({'Drain Current(A)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);

%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(IdsVds25.I, 1000*IdsVds25.V./IdsVds25.I,'DisplayName','Tj=25 C^o','Marker','x','LineWidth',0.1,...
    'Color',[1 0 0]);
% Create plot
plot(IdsVds125.I, 1000*IdsVds125.V./IdsVds125.I,'DisplayName','Tj=125 C^o','Marker','x','LineWidth',0.1,...
    'Color',[0 0 1]);
%
plot(IdsVds175.I, 1000*IdsVds175.V./IdsVds175.I,'DisplayName','Tj=175 C^o','Marker','x','LineWidth',0.1,...
    'Color',[1 0 1]);
% Create ylabel
ylabel({'On-state resistance (m\Omega)'});
% Create xlabel
xlabel({'Drain-Source Current (V)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);


%%
plot(IdsVds25.I, IdsVds25.V)
hold on
plot(IdsVds125.I, IdsVds125.V)
hold on
plot(IdsVds175.I, IdsVds175.V)


%%
plot(IdsVds25.I, IdsVds25.V./IdsVds25.I)
hold on
plot(IdsVds125.I, IdsVds125.V./IdsVds125.I)
hold on
plot(IdsVds175.I, IdsVds175.V./IdsVds175.I)
ylim([0 30e-3])
%%
rds_25=mean(IdsVds25.V./IdsVds25.I);
rds_125=mean(IdsVds125.V./IdsVds125.I);
rds_175=mean(IdsVds175.V./IdsVds175.I);


% rds_25*(1+(125-25)*K)=rds_125

K= ((rds_125/rds_25)-1)/(125-25);
K1= ((rds_175/rds_125)-1)/(175-125);

rds_25*(1+(125-25)*K);
rds_125;
% 
% 
% 
rds_125*(1+(175-125)*K1);
rds_175;


T=[25:5:175];
rds= zeros(1,length(T));
%%
i=1;
for T1=T
if T1<=125 
     rds(i) =rds_25*(1+(T1-25)*K);
elseif T1<=175
    rds(i) =rds_125*(1+(T1-125)*K1);
end
i=i+1;
end
%%



rds=[rds_25, rds_125, rds_175];
T1= [25 125 175];



rds_T=[25:5:175];
figure
rds_inter = interp1(T1,rds,rds_T);
plot(T1,rds,'o',rds_T,rds_inter,':x');
% xlim([0 2*pi]);
title('(Default) Linear Interpolation');

%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(rds_T,1000*rds_inter,"Marker",'x','LineWidth',0.1,...
    'Color',[1 0 0]);
% Create ylabel
ylabel({'On-state resistance (m\Omega)'});
% Create xlabel
xlabel({'Tj (C^o)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
% Create legend
% legend1 = legend(axes1,'show');
% set(legend1,...
    % 'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);

%%

clear ans i IdsVds25 IdsVds125 IdsVds175 K K1 rds rds_125 rds_25 rds_175 T T1

close all





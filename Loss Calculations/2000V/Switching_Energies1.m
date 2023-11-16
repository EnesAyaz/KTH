load('Eon_150.mat')
Eon_150=Eon;
clear Eon

%%

load('Eoff_150.mat')
Eoff_150=Eoff;
clear Eoff


%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(Eon_150.I, Eon_150.E,'DisplayName','Switch-on','Marker','x','LineWidth',1,...
    'Color',[1 0 0]);
% Create plot
plot(Eoff_150.I, Eoff_150.E,'DisplayName','Switch.off','Marker','x','LineWidth',1,...
    'Color',[0 0 1]);
% Create ylabel
ylabel({'Switching Energies (mJ)'});
% Create xlabel
xlabel({'Current (A)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);
%%
Eon_150_Id = linspace(0,max(Eon_150.I),1000); 
figure
Eon_150_inter = interp1(Eon_150 .I,Eon_150 .E,Eon_150_Id);
Eon_150_inter(isnan(Eon_150_inter))=min(Eon_150_inter);
plot(Eon_150.I,Eon_150.E,'o',Eon_150_Id,Eon_150_inter,':x');
% xlim([0 2*pi]);
title('(Default) Linear Interpolation');
%%
Eoff_150_Id = linspace(0,max(Eoff_150.I),1000); 
figure
Eoff_150_inter = interp1(Eoff_150.I,Eoff_150.E,Eoff_150_Id);
Eoff_150_inter(isnan(Eoff_150_inter))=min(Eoff_150_inter);
plot(Eoff_150.I,Eoff_150.E,'o',Eoff_150_Id,Eoff_150_inter,':x');
% xlim([0 2*pi]);
title('(Default) Linear Interpolation');

%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(Eon_150_Id , Eon_150_inter,'DisplayName','Switch-on','Marker','x','LineWidth',0.1,...
    'Color',[1 0 0]);
% Create plot
plot(Eoff_150_Id , Eoff_150_inter,'DisplayName','Switch.off','Marker','x','LineWidth',0.1,...
    'Color',[0 0 1]);
% Create ylabel
ylabel({'Switching Energies (mJ)'});
% Create xlabel
xlabel({'Current (A)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);

%%
clear ans Eoff_150 Eon_150

close all

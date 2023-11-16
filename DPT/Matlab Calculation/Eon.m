
fs=1/(time(2)-time(1));
flp=100e6;
[Vgs_lp, lp]= lowpass(Vgs,flp,fs);
 ws=200;
Vgs_lp= medfilt1(Vgs_lp,ws);

[Vds_lp, lp]= lowpass(Vds,flp,fs);
[Id_lp, lp]= lowpass(Id,flp,fs);
% 
Vgs_lp=circshift(Vgs_lp,98);
Vds_lp=circshift(Vds_lp,254);

Vds_lp=Vds_lp+24;
Id_lp=Id_lp+3.2;
P=Vds_lp.*Id_lp;

figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(time*1e6,P,'Color',[0 0 1]);

% Create ylabel
ylabel({'Power (W)'});

% Create xlabel
xlabel({'time (\mus)'});

% Uncomment the following line to preserve the X-limits of the aes
% xlim(axes1,[15 16]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% xlim([15 16])

clearvars -except Vgs Vds Id time





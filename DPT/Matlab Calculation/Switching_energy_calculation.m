% Vgs;
% Vds;
% Id;
% time;
V=Id

fs=1/(time(2)-time(1))
flp=100e6;
[V_lp, lp]= lowpass(V,flp,fs);
ws=1;
V_mf= medfilt1(V_lp,ws);

figure1 = figure('Renderer', 'painters', 'Position', [0 0 400 600]);

% Create subplot
subplot1 = subplot(2,1,1,'Parent',figure1);
hold(subplot1,'on');
% Create plot
plot(time*1e6,V,'Parent',subplot1,'Color',[0 0 1]);
% Create title
title({'Raw Data'});
ylabel({'Voltage (V)'});
ylabel({'Current (A)'});


box(subplot1,'on');
hold(subplot1,'off');
% Set the remaining axes properties
set(subplot1,'FontName','Times New Roman','FontSize',15);
% Create subplot
subplot2 = subplot(2,1,2,'Parent',figure1);
hold(subplot2,'on');

% Create plot
plot(time*1e6,V_lp,'Parent',subplot2,'Color',[0 0 1]);

% Create ylabel
ylabel({'Voltage (V)'});
ylabel({'Current (A)'});

% Create title

a=string(flp/1e6);
titlp= strcat(a,'{ }', 'Mhz Low-pass');


title({titlp});

box(subplot2,'on');
hold(subplot2,'off');
% Set the remaining axes properties
set(subplot2,'FontName','Times New Roman','FontSize',15);
% % Create subplot
% subplot3 = subplot(3,1,3,'Parent',figure1);
% hold(subplot3,'on');

% % Create plot
% plot(time*1e6,V_mf,'Parent',subplot3,'Color',[0 0 1]);
% 
% % Create ylabel
% ylabel({''});
% 
% % Create xlabel
% xlabel({'Time (\mus)'});
% 
% % Create title
% 
% a=string(ws);
% titmf= strcat('Median Filter Window size=',a);
% 
% title(titmf);
% 
% box(subplot3,'on');
% hold(subplot3,'off');
% % Set the remaining axes properties
% set(subplot3,'FontName','Times New Roman','FontSize',15);


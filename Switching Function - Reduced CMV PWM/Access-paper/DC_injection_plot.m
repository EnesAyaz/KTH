time_array= out.ReferenceCarrier.time;
VcarrierA=out.ReferenceCarrier.signals(1).values;
VcarrierB=out.ReferenceCarrier.signals(2).values;
VcarrierC=out.ReferenceCarrier.signals(3).values;

VrefA=out.ReferenceCarrier.signals(4).values;
VrefB=out.ReferenceCarrier.signals(5).values;
VrefC=out.ReferenceCarrier.signals(6).values;

Tfinal=1/ffund;

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,VrefA,'Linewidth',3,'Color','b')
hold on;
plot(time_array,VrefB,'Linewidth',3,'Color','m')
hold on;
plot(time_array,VrefC,'Linewidth',3,'Color','g')

ylim([-1 1])

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 -ma 0 ma 1],'YTickLabel',{'-1','-ma','0','ma','1'},'FontName','TimesNewRoman','FontSize',20);


legend1 = legend(axes1,'show',{'$u_A$','$u_B$','$u_C$','$u_{carr}$'},'FontName','TimesNewRoman','FontSize',16);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('Normalized Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
%%

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

hold on;
cf=plot(time_array,VcarrierA,'Linewidth',1.5,'Color','b')
cf.Color= [cf.Color 1]
cf=plot(time_array,VcarrierB,'Linewidth',1,'Color','m')
cf.Color= [cf.Color 1]
cf=plot(time_array,VcarrierC,'Linewidth',1,'Color','g')
cf.Color= [cf.Color 1]
ylim([-1 1])


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 -ma 0 ma 1],'YTickLabel',{'-1','-ma','0','ma','1'},'FontName','TimesNewRoman','FontSize',20);


legend1 = legend(axes1,'show',{'$u_{carr_A}$','$u_{carr_B}$','$u_{carr_C}$','$u_{carr}$'},'FontName','TimesNewRoman','FontSize',16);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('Normalized Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
%%
time_array=out.CMV.time;
CMV=out.CMV.signals.values;

Tfinal=1/ffund;

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array, CMV,'Linewidth',3,'Color','k')
hold on;

% Tfinalx=0.056
% Tfinalx=0.01;
% xlimH= Tfinalx+1/fsw;
% xlim([Tfinalx xlimH])

ylim([-1 1])


box(axes1,'on');
hold(axes1,'off');

set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 -0.66 -0.33 0 0.33 0.66 1],'YTickLabel',{'-V_{DC}','-2V_{DC}/3','-V_{DC}/3','0', 'V_{DC}/3','2V_{DC}/3','V_{DC}'},'FontName','TimesNewRoman','FontSize',20);

xlabel('Time ', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel(' Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
%%

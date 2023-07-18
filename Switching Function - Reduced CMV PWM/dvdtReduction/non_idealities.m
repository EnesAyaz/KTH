clear ;
clc;
tic;
close all
%% Time array
fsw = 10000; % Hz
Tstep = (1/fsw)/80; % s
Ts = Tstep; % s
Tfinal =5/fsw ; % s
time_array = 0:Tstep:Tfinal-Tstep;
NumberofSteps = numel(time_array);
%%
%Generate switching signals
The_c=0;
The_f=-pi/2;
phaseA=The_f+0;
phaseB=The_f-2*pi/3;
phaseC=The_f+2*pi/3;
VrefA = 1/2-1/3;
VrefB = -1/4-1/3;
VrefC = -1/4-1/3;
VrefA=VrefA*ones(size(time_array));
VrefB=VrefB*ones(size(time_array));
VrefC=VrefC*ones(size(time_array));

Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end

carrierPhA=0;
carrierPhB=225;
carrierPhC=76;
carA= round(carrierPhA/(fsw*Ts)/360);
if carA==0
    carA=1;
end
carB= round(carrierPhB/(fsw*Ts)/360);
if carB==0
    carB=1;
end
carC= round(carrierPhC/(fsw*Ts)/360);
if carC==0
    carC=1;
end

VcarrierA = [ Vtriang(carA:end), zeros(1,carA-1)];
VcarrierB = [ Vtriang(carB:end), zeros(1,carB-1)];
VcarrierC = [ Vtriang(carC:end), zeros(1,carC-1)];


SA = double(VrefA >= VcarrierA);
SB = double(VrefB >=VcarrierB);
SC = double(VrefC >= VcarrierC);

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA+1.5,'Linewidth',1,'Color','r')
hold on;
plot(time_array,SB,'Linewidth',1,'Color','b')
hold on;
plot(time_array,SC-1.5,'Linewidth',1,'Color','m')
hold on; 
plot(time_array,SC-1.5,'Linewidth',1,'Color','m')

ylim([-2 3])
xlim([0 1/fsw])
% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);


legend1 = legend(axes1,'show',{'$S_A$','$S_B$','$S_C$'},'FontName','TimesNewRoman','FontSize',16);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('PWM Signals','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)


%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA,'Linewidth',3,'Color','r')
hold on;
plot(time_array,SB,'Linewidth',3,'Color','b')
hold on;
plot(time_array,SC,'Linewidth',3,'Color','m')

% hold on;
% cf=plot(time_array,VcarrierA,'Linewidth',1,'Color','r')
% cf.Color= [cf.Color 1]
% cf=plot(time_array,VcarrierB,'Linewidth',1,'Color','b')
% cf.Color= [cf.Color 1]
% cf=plot(time_array,VcarrierC,'Linewidth',1,'Color','m')
% cf.Color= [cf.Color 1]


% box(axes1,'on');
% hold(axes1,'off');
% % Set the remaining axes properties
% set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
% set(axes1,'YTick',[-1 -ma 0 ma 1],'YTickLabel',{'-1','-ma','0','ma','1'},'FontName','TimesNewRoman','FontSize',20);


% legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$','Carrier'},'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');

% xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
%     'FontSize',20)
% ylabel('Normalized References','interpreter','latex','FontName','Times New Roman',...
%     'FontSize',20)

% figure();
% plot(time_array,SA+1.5,'Linewidth',1,'Color','r')
% hold on;
% plot(time_array,SB,'Linewidth',1,'Color','b')
% hold on;
% plot(time_array,SC-1.5,'Linewidth',1,'Color','m')
%%

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA+1.5,'Linewidth',1,'Color','r')
hold on;
plot(time_array,SB,'Linewidth',1,'Color','b')
hold on;
plot(time_array,SC-1.5,'Linewidth',1,'Color','m')

ylim([-2 3])
xlim([0 1/fsw])
% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);


legend1 = legend(axes1,'show',{'$S_A$','$S_B$','$S_C$'},'FontName','TimesNewRoman','FontSize',16);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('PWM Signals','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)

%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,VrefA,'Linewidth',3,'Color','r')
hold on;
plot(time_array,VrefB,'Linewidth',3,'Color','b')
hold on;
plot(time_array,VrefC,'Linewidth',3,'Color','m')

hold on;
plot(time_array,VcarrierA,'Linewidth',2,'Color','k')

Tfinalx=0.005
Tfinalx=0.01;
xlimH= Tfinalx+1/fsw;
xlim([Tfinalx xlimH])
ylim([-1 1])

% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 0 1]);


legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$','Carrier'},'FontName','TimesNewRoman','FontSize',20);
set(legend1,...
    'Position',[0.704191336922702 0.57341270550849 0.196428568288684 0.251190469094685],...
    'EdgeColor','none',...
    'Color','none','interpreter','Latex');

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA+1.5,'Linewidth',3,'Color','r')
hold on;
plot(time_array,SB,'Linewidth',3,'Color','b')
hold on;
plot(time_array,SC-1.5,'Linewidth',3,'Color','m')

xlimH= Tfinalx+1/fsw;
xlim([Tfinalx xlimH])
ylim([-2 3])

% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);



legend1 = legend(axes1,'show',{'$S_A$','$S_B$','$S_C$'},'FontName','TimesNewRoman','FontSize',20);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','none','interpreter','Latex');

%%

Tfinalx=0.005
Tfinalx=0.01;
xlimH= Tfinalx+1/fsw;


figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array, (SA+SB +SC)/3,'Linewidth',3,'Color','k')
hold on;


xlimH= Tfinalx+1/fsw;
xlim([Tfinalx xlimH])
ylim([-2 3])

% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
% set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
% set(axes1,'YTick',[-1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);

set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[0 0.33 0.66 1],'FontName','TimesNewRoman','FontSize',20);
ylim([0 1])

% legend1 = legend(axes1,'show',{'$S_A$','$S_B$','$S_C$'},'FontName','TimesNewRoman','FontSize',20);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','none','interpreter','Latex');


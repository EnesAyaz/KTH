clear ;
clc;
tic;
%% Time array
ma = 0.6;
fout = 50; % Hz
fsw = 50*22; % Hz
Tstep = (1/fsw)/800; % s
Ts = Tstep; % s
Tfinal =1/fout ; % s
time_array = 0:Tstep:Tfinal-Tstep;
NumberofSteps = numel(time_array);
%Generate switching signals
The_c=0;
The_f=-pi/2;
phaseA=The_f+0;
phaseB=The_f-2*pi/3;
phaseC=The_f+2*pi/3;
VrefA = ma*cos(2*pi*fout*time_array+phaseA);
VrefB = ma*cos(2*pi*fout*time_array+phaseB);
VrefC = ma*cos(2*pi*fout*time_array+phaseC);
pf=0.8;

mc=ma; 
IA = mc*cos(2*pi*fout*time_array+phaseA- acos(pf));
IB = mc*cos(2*pi*fout*time_array+phaseB- acos(pf));
IC = mc*cos(2*pi*fout*time_array+phaseC- acos(pf));

Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end

carrierPhA=0;
carrierPhB=0;
carrierPhC=0;

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


SA = double(VrefA > VcarrierA);
SB = double(VrefB > VcarrierB);
SC = double(VrefC > VcarrierC);

%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,VrefA,'Linewidth',3,'Color',[0.5 0 0])
hold on;
plot(time_array,VrefB,'Linewidth',3,'Color',[0 0.5 0])
hold on;
plot(time_array,VrefC,'Linewidth',3,'Color',[0 0 0.5])

hold on;
cf=plot(time_array,VcarrierA,'Linewidth',1,'Color',[0.2 0.2 0.2],'LineStyle','-')
cf.Color= [cf.Color 1]


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 -ma 0 ma 1],'YTickLabel',{'-1','-m_a','0','m_a','1'},'FontName','TimesNewRoman','FontSize',20);


% legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$','Carrier'},'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
% ylabel('Normalized References','interpreter','latex','FontName','Times New Roman',...
%     'FontSize',20)
%%

figure1 = figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% --- Plot voltage references ---
plot(time_array, VrefA, 'LineWidth', 3, 'Color', [0.5 0 0])
plot(time_array, VrefB, 'LineWidth', 3, 'Color', [0 0.5 0])
plot(time_array, VrefC, 'LineWidth', 3, 'Color', [0 0 0.5])

% --- Left y-axis for voltage ---
yyaxis left
set(gca,'YColor','k')
set(gca,'YTick',[-1 -ma 0 ma 1], ...
        'YTickLabel',{'-V_{DC}','-m_aV_{DC}','0','m_aV_{DC}','V_{DC}'}, ...
        'FontName','TimesNewRoman','FontSize',20);
ylim([-1 1])
ylabel('Phase Voltages', 'interpreter','latex','FontSize',20)

% --- Right y-axis for normalized current ---
yyaxis right
set(gca,'YColor','k')
plot(time_array, IA, '--', 'LineWidth', 2, 'Color', [0.5 0 0])
plot(time_array, IB, '--', 'LineWidth', 2, 'Color', [0 0.5 0])
plot(time_array, IC, '--', 'LineWidth', 2, 'Color', [0 0 0.5])
ylabel('Phase Currents', ...
        'interpreter','latex','FontSize',20, ...
        'FontName','TimesNewRoman','Rotation',-90, ...
        'VerticalAlignment','bottom');

set(gca,'YTick',[-1 0 1], ...
        'YTickLabel',{'-I_{max}','0','I_{max}'}, ...
        'FontName','TimesNewRoman','FontSize',20);
ylim([-1 1])


% --- Common X-axis setup ---
set(gca,'XTick',[0 Tfinal/2 Tfinal], ...
        'XTickLabel',{'0','180','360'}, ...
        'FontName','TimesNewRoman','FontSize',20);
xlabel('Fundamental Phase ($^o$)', ...
        'interpreter','latex','FontName','Times New Roman','FontSize',20)

% --- Legend ---
% legend1 = legend({'$Ref\_A$', '$Ref\_B$', '$Ref\_C$', ...
%                   '$i\_A$', '$i\_B$', '$i\_C$'}, ...
%                 'FontName','TimesNewRoman','FontSize',16);
% set(legend1, ...
%     'Location','Best', ...
%     'EdgeColor','none', ...
%     'Color','white', ...
%     'interpreter','Latex');

box on

%%

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA+1.5,'Linewidth',2,'Color',[0.5 0 0])
hold on;
plot(time_array,SB,'Linewidth',2,'Color',[0 0.5  0])
hold on;
plot(time_array,SC-1.5,'Linewidth',2,'Color',[0 0 0.5])

ylim([-2 3])

% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);


% legend1 = legend(axes1,'show',{'$S_A$','$S_B$','$S_C$'},'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('PWM Signals','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)

%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,VrefA,'Linewidth',3,'Color',[0.5 0 0])
hold on;
plot(time_array,VrefB,'Linewidth',3,'Color',[0 0.5 0])
hold on;
plot(time_array,VrefC,'Linewidth',3,'Color',[0 0 0.5],'LineStyle','--')

hold on;
plot(time_array,VcarrierA,'Linewidth',2,'Color',[0.2 0.2 0.2])

Tfinalx=0.006
% Tfinalx=0.01;
xlimH= Tfinalx+1/fsw;
xlim([Tfinalx xlimH])
ylim([-1 1])

% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 0 1]);


% legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$','Carrier'},'FontName','TimesNewRoman','FontSize',20);
% set(legend1,...
%     'Position',[0.704191336922702 0.57341270550849 0.196428568288684 0.251190469094685],...
%     'EdgeColor','none',...
%     'Color','none','interpreter','Latex');
%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% 
% plot(time_array,SA.*IA+1.5,'Linewidth',3,'Color',[0.5 0 0])
% hold on;
% plot(time_array,SB.*IB,'Linewidth',3,'Color',[0 0.5 0])
% hold on;
% plot(time_array,SC.*IC-1.5,'Linewidth',3,'Color',[0 0 0.5])


plot(time_array,SB.*IB+SA.*IA+SC.*IC-mean(SB.*IB+SA.*IA+SC.*IC),'Linewidth',3,'Color',[0 0 0.5])

% Tfinalx=0.005
% xlimH= Tfinalx+1/fsw;
% xlim([Tfinalx xlimH])
% ylim([-2 3])

% xticklabels({'Ts','','Ts'})

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);



% legend1 = legend(axes1,'show',{'$S_A$','$S_B$','$S_C$'},'FontName','TimesNewRoman','FontSize',20);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','none','interpreter','Latex');


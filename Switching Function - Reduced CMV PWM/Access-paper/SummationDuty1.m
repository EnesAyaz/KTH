clear ;
clc;
tic;
close all
%% Time array
ma = 0.8;
fout = 10; % Hz
% fsw = 800; % Hz
fsw = 10000; % Hz
Tstep = (1/fsw)/80; % s
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
VrefA = ma*cos(2*pi*fout*time_array+phaseA)-1/3;
VrefB = ma*cos(2*pi*fout*time_array+phaseB)-1/3;
VrefC = ma*cos(2*pi*fout*time_array+phaseC)-1/3+1/20;
Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end

carrierPhA=0;
carrierPhB=203;
carrierPhC=52;
% carrierPhA=0;
% carrierPhB=0;
% carrierPhC=0;
% carrierPhA=0;
% carrierPhB=180-25;
% carrierPhC=180-104.9518;
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
%%
%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,VrefA,'Linewidth',3,'Color','b')
hold on;
plot(time_array,VrefB,'Linewidth',3,'Color','m')
hold on;
plot(time_array,VrefC,'Linewidth',3,'Color','g')

hold on;
plot(time_array,VcarrierA,'-.','Linewidth',1.5,'Color','b')
hold on;
plot(time_array,VcarrierB,'-.','Linewidth',1.5,'Color','m')
hold on;
plot(time_array,VcarrierC,'-.','Linewidth',1.5,'Color','g')

Tfinalx=0.056
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


legend1 = legend(axes1,'show',{'$u_A$','$u_B$','$u_C$','$u_{carr_A}$','$u_{carr_B}$','$u_{carr_C}$'},'FontName','TimesNewRoman','FontSize',20);
set(legend1,...
    'Position',[0.704191336922702 0.57341270550849 0.196428568288684 0.251190469094685],...
    'EdgeColor','none',...
    'Color','none','interpreter','Latex');

xlabel('Time ', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('Normalized Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA+3,'Linewidth',3,'Color','b')
hold on;
plot(time_array,SB,'Linewidth',3,'Color','m')
hold on;
plot(time_array,SC-3,'Linewidth',3,'Color','g')

Tfinalx=0.056
xlimH= Tfinalx+1/fsw;
xlim([Tfinalx xlimH])
ylim([-4 5])

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
% set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-3 -2 0 1 3 4],'YTickLabel',{'-V_{DC}/2','V_{DC}/2','-V_{DC}/2','V_{DC}/2','-V_{DC}/2','V_{DC}/2'},'FontName','TimesNewRoman','FontSize',15);
set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);

legend1 = legend(axes1,'show',{'$V_A$','$V_B$','$V_C$'},'FontName','TimesNewRoman','FontSize',20);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','none','interpreter','Latex');

xlabel('Time ', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel(' Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)

%%

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array, (SA+SB +SC)/3-1/2,'Linewidth',3,'Color','k')
hold on;

Tfinalx=0.056
xlimH= Tfinalx+1/fsw;
xlim([Tfinalx xlimH])


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
% set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
% set(axes1,'YTick',[-1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);

% set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'XTick',[Tfinalx xlimH],'XTickLabel',{'0','Ts'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-0.5 -0.16 0 0.16 0.5],'YTickLabel',{'-V_{DC}/2','-V_{DC}/6','0', 'V_{DC}/6','V_{DC}/2'},'FontName','TimesNewRoman','FontSize',20);
 ylim([-0.5 0.5])

xlabel('Time ', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel(' Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
%%
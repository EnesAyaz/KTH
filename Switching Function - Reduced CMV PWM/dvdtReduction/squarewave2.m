clear ;
clc;
tic;
close all
%% Time array
ma = 0.65;
fout = 3*50; % Hz
% fsw =100; % Hz
fsw = 10000; % Hz
Tstep =1e-6;
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

% CM=0;
CM= [ (1/3)* ones([1, length(time_array)/6]), ...
             -(1/3)* ones([1, length(time_array)/6]),  ...
             (1/3)* ones([1, length(time_array)/6]), ...
             -(1/3)* ones([1, length(time_array)/6]),  ...
             (1/3)* ones([1, length(time_array)/6]), ...
             -(1/3)* ones([1, length(time_array)/6]) ];


VrefA=VrefA+CM; 
VrefB=VrefB+CM; 
VrefC=VrefC+CM; 

Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end

% carrierPhA=0;
% carrierPhB=197;
% carrierPhC=76;
carrierPhA=0;
carrierPhB=0;
carrierPhC=0;

carrierPhA=0;
carrierPhB=210
carrierPhC=146

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
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA+1.5,'Linewidth',3,'Color','r')
hold on;
plot(time_array,SB,'Linewidth',3,'Color','b')
hold on;
plot(time_array,SC-1.5,'Linewidth',3,'Color','m')


Tfinalx=0.005 +1/fsw/2;
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


figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array, (SA+SB +SC)/3,'Linewidth',3,'Color','k')
hold on;

Tfinalx=0.005 +1/fsw/2;
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


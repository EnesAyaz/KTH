clear ;
clc;
tic;
close all
% Time array
ffund=50;
fsw = 10000; % Hz
Tstep = (1/fsw)/200; % s
Ts = Tstep; % s
Tfinal =1/ffund ; % s
time_array = 0:Tstep:Tfinal-Tstep;
NumberofSteps = numel(time_array);
%
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

ma=0.9;
VrefA=ma*sin(2*pi*ffund*time_array+ phaseA);
VrefB=ma*sin(2*pi*ffund*time_array+ phaseB);
VrefC=ma*sin(2*pi*ffund*time_array+ phaseC);



Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end

carrierPhA=0;
carrierPhB=220;
carrierPhC=144.5;

% carrierPhA=0;
% carrierPhB=225;
% carrierPhC=147;

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
SB = double(VrefB >VcarrierB);
SC = double(VrefC > VcarrierC);

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,SA+1.5,'Linewidth',0.5,'Color','r')
hold on;
plot(time_array,VrefA/2+2,'Linestyle','--','Linewidth',2,'Color','k')
hold on;
plot(time_array,SB,'Linewidth',1,'Color','b')
hold on;
plot(time_array,VrefB/2+0.5,'Linestyle','--','Linewidth',2,'Color','k')
hold on;
plot(time_array,SC-1.5,'Linewidth',1,'Color','m')
hold on; 
plot(time_array,VrefC/2-1,'Linestyle','--','Linewidth',2,'Color','k')
hold on;
plot(time_array,(SA+SB+SC)/3-3,'Linewidth',1,'Color','k')

ylim([-3.5 3])
% xlim([0 1/fsw])
% xticklabels({'Ts','','Ts'})
%
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
% set(axes1,'XTick',[0 Tfinal/10 Tfinal/5],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
% set(axes1,'YTick',[-5 -4.5 -4 -1.5 -0.5 0 1 1.5 2.5],'YTickLabel',{'-1','0','1','L','H','L','H','L','H'},'FontName','TimesNewRoman','FontSize',20);
% 
% 
% legend1 = legend(axes1,'show',{'$S_A$','$S_B$','$S_C$','CMV' },'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');

% xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
%     'FontSize',20)
% ylabel('PWM Signals','interpreter','latex','FontName','Times New Roman',...
%     'FontSize',20)


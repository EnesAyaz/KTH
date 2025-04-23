clear ;
clc;
tic;
close all
% Time array
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

box(axes1,'on');
hold(axes1,'off');

set(axes1,'XTick',[Tfinalx (Tfinalx+xlimH)/2 xlimH],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-0.5 -0.16 0 0.16 0.5],'YTickLabel',{'-V_{DC}/2','-V_{DC}/6','0', 'V_{DC}/6','V_{DC}/2'},'FontName','TimesNewRoman','FontSize',20);
 ylim([-0.5 0.5])


xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel(' Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
%%

clear ;
clc;
tic;
close all
%Time array
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
VrefA = ma*cos(2*pi*fout*time_array+phaseA)+1/3;
VrefB = ma*cos(2*pi*fout*time_array+phaseB)+1/3-1/20;
VrefC = ma*cos(2*pi*fout*time_array+phaseC)+1/3;
Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end

carrierPhA=0;
carrierPhB=316;
carrierPhC=165;
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

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array, (SA+SB +SC)/3-1/2,'Linewidth',3,'Color','k')
hold on;

Tfinalx=0.044
xlimH= Tfinalx+1/fsw;
xlim([Tfinalx xlimH])


box(axes1,'on');
hold(axes1,'off');

set(axes1,'XTick',[Tfinalx (Tfinalx+xlimH)/2 xlimH],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-0.5 -0.16 0 0.16 0.5],'YTickLabel',{'-V_{DC}/2','-V_{DC}/6','0', 'V_{DC}/6','V_{DC}/2'},'FontName','TimesNewRoman','FontSize',20);
 ylim([-0.5 0.5])


xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel(' Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
%%

time_array=linspace(-2*pi,4*pi,10000);

CMV=sign(sin(3*time_array))/6;


figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array, CMV,'Linewidth',3,'Color','k')
hold on;
xlim([0 2*pi])


box(axes1,'on');
hold(axes1,'off');

set(axes1,'XTick',[0 pi 2*pi],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-0.5 -0.16 0 0.16 0.5],'YTickLabel',{'-V_{DC}/2','-V_{DC}/6','0', 'V_{DC}/6','V_{DC}/2'},'FontName','TimesNewRoman','FontSize',20);
 ylim([-0.5 0.5])


xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel(' Voltage','interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
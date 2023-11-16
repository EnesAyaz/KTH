clear ;
clc;
tic;
close all

%% Time array
ma = 0.6;
fout = 50; % Hz
fsw = 1000; % Hz
% fsw = 10000; % Hz
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
phaseA2=phaseA+pi/3;
phaseB2=phaseB+pi/3;
phaseC2=phaseC+pi/3;

VrefA = ma*cos(2*pi*fout*time_array+phaseA);
VrefB = ma*cos(2*pi*fout*time_array+phaseB);
VrefC = ma*cos(2*pi*fout*time_array+phaseC);

VrefA2 = ma*cos(2*pi*fout*time_array+phaseA2);
VrefB2 = ma*cos(2*pi*fout*time_array+phaseB2);
VrefC2 = ma*cos(2*pi*fout*time_array+phaseC2);

Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end


carrierPhA=0;
carrierPhB=0;
carrierPhC=0;
carrierPhA2=180;
carrierPhB2=180;
carrierPhC2=180;

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

carA2= round(carrierPhA2/(fsw*Ts)/360)+1;
if carA2==0
    carA2=1;
end

carB2= round(carrierPhB2/(fsw*Ts)/360)+1;
if carB2==0
    carB2=1;
end

carC2= round(carrierPhC2/(fsw*Ts)/360)+1;
if carC2==0
    carC2=1;
end



VcarrierA = [ Vtriang(carA:end), zeros(1,carA-1)];
VcarrierB = [ Vtriang(carB:end), zeros(1,carB-1)];
VcarrierC = [ Vtriang(carC:end), zeros(1,carC-1)];

VcarrierA2 = [ Vtriang(carA2:end), zeros(1,carA2-1)];
VcarrierB2 = [ Vtriang(carB2:end), zeros(1,carB2-1)];
VcarrierC2 = [ Vtriang(carC2:end), zeros(1,carC2-1)];


SA = double(VrefA >= VcarrierA);
SB = double(VrefB >=VcarrierB);
SC = double(VrefC >= VcarrierC);


SA2 = double(VrefA2 >= VcarrierA2);
SB2 = double(VrefB2 >=VcarrierB2);
SC2 = double(VrefC2 >= VcarrierC2);

%%

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% plot(time_array,VcarrierA,'Linewidth',3,'Color','r')

% plot(time_array,VrefA,'Linewidth',3,'Color','r')
% plot(time_array,VrefB,'Linewidth',3,'Color','g')
% plot(time_array,VrefC,'Linewidth',3,'Color','b')
% plot(time_array,VrefA2,'Linewidth',3,'Color','c')
% plot(time_array,VrefB2,'Linewidth',3,'Color','m')
% plot(time_array,VrefC2,'Linewidth',3,'Color',[0.9290 0.6940 0.1250])


% plot(time_array,SA,'Linewidth',3,'Color','r')
% plot(time_array,SB,'Linewidth',3,'Color','g')
% plot(time_array,SC,'Linewidth',3,'Color','b')
% plot(time_array,SA2,'Linewidth',3,'Color','c')
% plot(time_array,SB2,'Linewidth',3,'Color','m')
% plot(time_array,SC2,'Linewidth',3,'Color',[0.9290 0.6940 0.1250])
hold on;

box(axes1,'on');
hold(axes1,'off');

set(axes1,'XTick',[],'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[],'FontName','TimesNewRoman','FontSize',20);




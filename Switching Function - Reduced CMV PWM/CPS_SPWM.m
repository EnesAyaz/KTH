% clear ; clc; tic;
%%
A=[];
for ma = 0:0.1:1
fout = 1000; % Hz
fsw = 40e3; % Hz
Tstep = (1/fsw)/200; % s
Ts = Tstep; % s
Tfinal =2/fout ; % s
time_array = 0:Tstep:Tfinal-Tstep;
NumberofSteps = numel(time_array);
%Generate switching signals
The_c=0;
The_f=-pi/6;
phaseA=The_f+0;
phaseB=The_f-2*pi/3;
phaseC=The_f+2*pi/3;
VrefA = ma*cos(2*pi*fout*time_array+phaseA);
VrefB = ma*cos(2*pi*fout*time_array+phaseB);
VrefC = ma*cos(2*pi*fout*time_array+phaseC);
Vtriang = zeros(1, NumberofSteps);
for k = 1:Tfinal*fsw
   Triang_temp = triang(1/(Ts*fsw));
   Vtriang((length(Triang_temp)*(k-1)+1:k/(Tstep*fsw))) = (Triang_temp*2)-1;
end

carrierPhA=0;
carrierPhB=240;
carrierPhC=120;

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

Vcmv= (SA+SB+SC)/3;

figure();
plot(time_array, Vcmv,'color',[0.5 0 0.5],'LineWidth',2);
ylim([-0.2 1.2])


A =[A  rms(Vcmv)] ;

end

 
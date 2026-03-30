%% Time array
ma = 0.6;
fout = 1; % Hz
mf=48;
fsw = fout*mf; % Hz
Tstep = (1/fsw); % s
Ts = Tstep; % s
Tfinal =1/fout ; % s
time_array = 0:Tstep:Tfinal-Tstep;
NumberofSteps = numel(time_array);


%Generate switching signals
The_c=0;
The_f=0;
phaseA=The_f+0;
phaseB=The_f-2*pi/3;
phaseC=The_f+2*pi/3;
VrefA = ma*cos(2*pi*fout*time_array+phaseA);
VrefB = ma*cos(2*pi*fout*time_array+phaseB);
VrefC = ma*cos(2*pi*fout*time_array+phaseC);

mc=1;
pf=0.9;

IphA = mc*cos(2*pi*fout*time_array+phaseA-acos(pf));
IphB = mc*cos(2*pi*fout*time_array+phaseB-acos(pf));
IphC = mc*cos(2*pi*fout*time_array+phaseC-acos(pf));


da=(1+VrefA)/2; 
db=(1+VrefB)/2; 
dc=(1+VrefC)/2; 

carrierPhA=zeros(1,NumberofSteps);
carrierPhB=zeros(1,NumberofSteps);
carrierPhC=zeros(1,NumberofSteps);
%%
for i=1:NumberofSteps

[theta_b_opt, theta_c_opt, min_rms] = optimize_interleaving_rms(IphB(i), IphC(i), db(i), dc(i));

carrierPhB(i)=theta_b_opt;
carrierPhC(i)=theta_c_opt;

end

%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

for  variable_carrier=0:1

fsw = mf;
Ts = 1/fsw;
N = 1000;
t = linspace(0, Ts, N);

carrierA= [];
carrierB=[];
carrierC=[];

for i=1:NumberofSteps

if variable_carrier==1
% Reference triangular carrier for phase A
carrier = sawtooth(2*pi*fsw*t, 0.5);  % symmetric triangle [-1,1]

shift_b = mod(carrierPhB(i) / 360, 1) * Ts;
shift_c = mod(carrierPhC(i) / 360, 1) * Ts;

% Create phase-shifted carriers
carrier_b = sawtooth(2*pi*fsw*(t - shift_b), 0.5);
carrier_c = sawtooth(2*pi*fsw*(t - shift_c), 0.5);

carrierA=[carrierA, carrier(1:N)];

carrierB=[carrierB, carrier_b(1:N)];

carrierC=[carrierC, carrier_c(1:N)];

else 

carrier = sawtooth(2*pi*fsw*t, 0.5);  % symmetric triangle [-1,1]

carrierA=[carrierA, carrier(1:N)];

carrierB=[carrierB, carrier(1:N)];

carrierC=[carrierC, carrier(1:N)];

end 

end

time_array=linspace(0, mf*Ts, mf*N);
%%
VrefA = ma*cos(2*pi*fout*time_array+phaseA);
VrefB = ma*cos(2*pi*fout*time_array+phaseB);
VrefC = ma*cos(2*pi*fout*time_array+phaseC);


IphA = mc*cos(2*pi*fout*time_array+phaseA-acos(pf));
IphB = mc*cos(2*pi*fout*time_array+phaseB-acos(pf));
IphC = mc*cos(2*pi*fout*time_array+phaseC-acos(pf));

SA = double(VrefA > carrierA);
SB = double(VrefB > carrierB);
SC = double(VrefC > carrierC);

%%
Icap=IphA.*SA+IphB.*SB+IphC.*SC-mean(IphA.*SA+IphB.*SB+IphC.*SC);


num_windows = fsw;
window_size = length(Icap) / num_windows;

% Preallocate result
rms_values = zeros(1, num_windows);

% Calculate RMS for each 20-sample window
for i = 1:num_windows
    idx_start = (i-1)*window_size + 1;
    idx_end = i*window_size;
    window_data = Icap(idx_start:idx_end);
    rms_values(i) = sqrt(mean(window_data.^2));
end

%% Display result

theta=linspace(0,360,fsw);

C=[0.5 0 0.5 ;0 0.5 0.5];
index=variable_carrier+1;
stairs(theta,rms_values,'Linewidth',2,'Color',C(index,:))
hold on
end

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 180 360],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[0 0.1 0.2 0.3 0.4 0.5],'YTickLabel',{'0','0.1','0.2','0.3','0.4','0.5'}, ...
    'FontName','TimesNewRoman','FontSize',20, ...
    'TickLabelInterpreter','latex');
ylim([0 0.5])
xlim([0 360])

legend1 = legend(axes1,'show',{'The Conventional PWM','The Proposed PWM'},'FontName','TimesNewRoman','FontSize',16);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel(sprintf('Capacitor Current (RMS)\nat Switching Frequency'), ...
       'Interpreter','latex', ...
       'FontName','Times New Roman', 'FontSize', 20)


%%
if 1
theta=linspace(0,360,fsw);

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% plot(theta,carrierPhA,'Linewidth',3,'Color',[0.5 0 0])
hold on;
stairs(theta,carrierPhB,'Linewidth',2,'Color',[0 0.5 0])
hold on;
stairs(theta,carrierPhC,'Linewidth',2,'Color',[0 0 0.5])
% hold on 
% plot(time_array,IphA.*SA+IphB.*SB+IphC.*SC-mean(IphA.*SA+IphB.*SB+IphC.*SC) ,'Linewidth',3,'Color',[0 0 0])
hold on;


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 180 360],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[0 90 180 270 360],'YTickLabel',{'0','90','180','270','360'}, ...
    'FontName','TimesNewRoman','FontSize',20, ...
    'TickLabelInterpreter','latex');
ylim([0 360])
xlim([0 360])

legend1 = legend(axes1,'show',{'$\theta_b^{opt}$','$\theta_c^{opt}$'},'FontName','TimesNewRoman','FontSize',20);
set(legend1,...
    'Location','Best',...
    'EdgeColor','none',...
    'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('Phase-Shift ($^o$)', ...
       'Interpreter','latex', ...
       'FontName','Times New Roman', 'FontSize', 20)
end 
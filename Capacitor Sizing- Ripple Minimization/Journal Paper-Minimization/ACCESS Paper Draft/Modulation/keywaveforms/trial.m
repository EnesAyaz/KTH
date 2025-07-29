%% Time array
ma = 0.6;
fout = 1; % Hz
mf=12;
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

mc=ma;
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

variable_carrier=1;

%%
for i=1:NumberofSteps

[theta_b_opt, theta_c_opt, min_rms] = optimize_interleaving_rms(IphB(i), IphC(i), db(i), dc(i));

carrierPhB(i)=theta_b_opt;
carrierPhC(i)=theta_c_opt;

end

%%
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
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,VrefA,'Linewidth',3,'Color',[0.5 0 0])
hold on;
plot(time_array,VrefB,'Linewidth',3,'Color',[0 0.5 0])
hold on;
plot(time_array,VrefC,'Linewidth',3,'Color',[0 0 0.5])

hold on;
if variable_carrier==1
cf=plot(time_array,carrierA,'Linewidth',1,'Color',[0.8 0 0],'LineStyle','-')
% cf.Color= [cf.Color 1]

cf=plot(time_array,carrierB,'Linewidth',1,'Color',[0 0.8 0],'LineStyle','-')
% cf.Color= [cf.Color 1]

cf=plot(time_array,carrierC,'Linewidth',1,'Color',[0 0 0.8],'LineStyle','-')
% cf.Color= [cf.Color 1]
else 
cf=plot(time_array,carrierA,'Linewidth',1,'Color',[0 0 0],'LineStyle','-')
end
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 -ma 0 ma 1],'YTickLabel',{'-1','-m_a','0','m_a','1'},'FontName','TimesNewRoman','FontSize',20);


% legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$','$Car_A$','$Car_B$','$Car_C$'},'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
% ylabel('Normalized References','interpreter','latex','FontName','Times New Roman',...
%     'FontSize',20)
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
% figure1=figure();
% axes1 = axes('Parent',figure1);
% hold(axes1,'on');
% 
% plot(time_array,IphA,'Linewidth',3,'Color',[0.5 0 0])
% hold on;
% plot(time_array,IphB,'Linewidth',3,'Color',[0 0.5 0])
% hold on;
% plot(time_array,IphC,'Linewidth',3,'Color',[0 0 0.5])
% 
% box(axes1,'on');
% hold(axes1,'off');
% % Set the remaining axes properties
% set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
% set(axes1,'YTick',[-1 -mc 0 mc 1],'YTickLabel',{'-1','-Iph','0','Iph','1'},'FontName','TimesNewRoman','FontSize',20);
% ylim([-1 1])
% 
% legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$'},'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');
% 
% xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
%     'FontSize',20)
% % ylabel('Normalized References','interpreter','latex','FontName','Times New Roman',...
% %     'FontSize',20)
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
    'YTickLabel',{'-1','-$m_a$','0','$m_a$','1'}, ...
    'FontName','TimesNewRoman','FontSize',20, ...
    'TickLabelInterpreter','latex');
ylim([-1 1])

ylabel('Normalized Phase Voltages', 'interpreter','latex','FontSize',20)

% --- Right y-axis for normalized current ---
yyaxis right
set(gca,'YColor','k')
plot(time_array, IphA, '--', 'LineWidth', 2, 'Color', [0.5 0 0])
plot(time_array, IphB, '--', 'LineWidth', 2, 'Color', [0 0.5 0])
plot(time_array, IphC, '--', 'LineWidth', 2, 'Color', [0 0 0.5])
ylabel('Normalized Phase Currents', ...
        'interpreter','latex','FontSize',20, ...
        'FontName','TimesNewRoman','Rotation',-90, ...
        'VerticalAlignment','bottom');

set(gca,'YTick',[-1 -mc 0 mc 1], ...
    'YTickLabel',{'-1','-$\hat{I}_{\mathrm{ph}}$','0','$\hat{I}_{\mathrm{ph}}$','1'}, ...
    'FontName','TimesNewRoman','FontSize',20, ...
    'TickLabelInterpreter','latex');
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

% box on
%%

figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_array,IphA.*SA,'Linewidth',3,'Color',[0.5 0 0])
hold on;
plot(time_array,IphB.*SB,'Linewidth',3,'Color',[0 0.5 0])
hold on;
plot(time_array,IphC.*SC,'Linewidth',3,'Color',[0 0 0.5])
hold on 
% plot(time_array,IphA.*SA+IphB.*SB+IphC.*SC-mean(IphA.*SA+IphB.*SB+IphC.*SC) ,'Linewidth',3,'Color',[0 0 0])
hold on;


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 -mc 0 mc 1],'YTickLabel',{'-1','-$\hat{I}_{\mathrm{ph}}$','0','$\hat{I}_{\mathrm{ph}}$','1'}, ...
    'FontName','TimesNewRoman','FontSize',20, ...
    'TickLabelInterpreter','latex');
ylim([-1 1])


% legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$'},'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('Leg Currents', ...
       'Interpreter','latex', ...
       'FontName','Times New Roman', 'FontSize', 20)

%%


figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% plot(time_array,IphA.*SA,'Linewidth',3,'Color',[0.5 0 0])
% hold on;
% plot(time_array,IphB.*SB,'Linewidth',3,'Color',[0 0.5 0])
% hold on;
% plot(time_array,IphC.*SC,'Linewidth',3,'Color',[0 0 0.5])
hold on 
plot(time_array,IphA.*SA+IphB.*SB+IphC.*SC-mean(IphA.*SA+IphB.*SB+IphC.*SC) ,'Linewidth',3,'Color',[0 0 0])
hold on;


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'XTick',[0 Tfinal/2 Tfinal],'XTickLabel',{'0','180','360'},'FontName','TimesNewRoman','FontSize',20);
set(axes1,'YTick',[-1 -mc 0 mc 1],'YTickLabel',{'-1','-$\hat{I}_{\mathrm{ph}}$','0','$\hat{I}_{\mathrm{ph}}$','1'}, ...
    'FontName','TimesNewRoman','FontSize',20, ...
    'TickLabelInterpreter','latex');
ylim([-1 1])

% legend1 = legend(axes1,'show',{'$Ref_A$','$Ref_B$','$Ref_C$'},'FontName','TimesNewRoman','FontSize',16);
% set(legend1,...
%     'Location','Best',...
%     'EdgeColor','none',...
%     'Color','white','interpreter','Latex');

xlabel('Fundamental Phase ($^o$)', 'interpreter','latex','FontName','Times New Roman',...
    'FontSize',20)
ylabel('Capacitor Current', ...
       'Interpreter','latex', ...
       'FontName','Times New Roman', 'FontSize', 20)


rms(IphA.*SA+IphB.*SB+IphC.*SC-mean(IphA.*SA+IphB.*SB+IphC.*SC))
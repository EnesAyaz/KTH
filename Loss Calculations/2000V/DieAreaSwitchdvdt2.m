Tj=100;
Ptot_y=[];
number_of_parallel_dies_x=1:0.5:16;
fc_x=5e3:0.5e3:30e3;

% number_of_parallel_dies_x=8:10;
% fc_x=5e3:1e3:30e3;

% di_dt_on= 5e9; % A/s
% dv_dt_on= 10e9; % V/s
% di_dt_off= 20e9; % A/s
% dv_dt_off= 15e9; % V/s


% di_dt_on= 20e9; % A/s
% dv_dt_on= 30e9; % V/s
% di_dt_off= 60e9; % A/s
% dv_dt_off= 30e9; % V/s

di_dt_on= 30e9; % A/s
dv_dt_on= 30e9; % V/s
di_dt_off= 30e9; % A/s
dv_dt_off= 30e9; % V/s


% di_dt_on= 10e9; % A/s
% dv_dt_on= 10e9; % V/s
% di_dt_off= 10e9; % A/s
% dv_dt_off= 10e9; % V/s


for number_of_parallel_dies= number_of_parallel_dies_x
Ptot_x=[];
for fc = fc_x % Carrier frequency
rds=17.2e-3*(1+(Tj-25)/75);
rds=rds*1/number_of_parallel_dies;
E_zcs= 0.15e-3;
% E_zcs= 0;
E_zcs=E_zcs*number_of_parallel_dies/1;

ma=1.15;   % Modulation index
f1 = 500; % Fundamental frequency
pn = fc/f1; % Pulse number
npoints = 10000; % Number of timepoints
carrytype='tria'; % carrier type 
smp= 'ns';  % reference sampling mode 
cmode='tri6'; % reference common-mode injection 
theta0=0; % reference phase offset
thetac=0; % carrier phase offset
start_angle= 0; % reference angle to start with
end_angle=2*pi; %reference angle to end with 
ma_dc=0; % DC reference 
[vp,wt,carr,ref] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
        % Numerical waveforms during one cycle

Ud = 1250; % p2p DC voltage
P = 300e3;    % Only 200 kW
cosphi =0.9;  % Cos(phi) at inverter terminal
uppk = ma*Ud/2; % Peak phase voltage reference;
ippk = P*2/3/uppk/cosphi;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip = ippk*cos(wt-phi);   % sampled phase current over one cycle
Vp=(ma*Ud/2)*cos(wt) ;   % sampled phase voltage over one cycle

sw = (ip>=0&vp>0) | (ip<0&vp<=0);   % =1 when current passes through switch
di = ~sw;                               % =1 when current passes through diode
Isw = abs(ip.*sw);                     % current through switch
Idi = abs(ip.*di);                     % current through diode

comm = sw - [sw(end) sw(1:end-1)];   % Nonzero at commutations (NOTE includes natural as well as forced commutations)

s2d=find(comm < -eps);          % Find the instants (samples) when current commutates from switch to diode
d2s=find(comm > eps);           % Find the instants (samples) when current commutates from diode to switch
is2d = abs(ip(s2d));            % Current at commutations switch to diode
id2s = abs(ip(d2s));            % Current at commutations diode to switch

% Conduction
Ploss_con_time_leg=(ip.^2)*rds;
Ploss_con_3Leg = mean(Ploss_con_time_leg)*3;

% Switch onn
Eon=[];
for i= 1:length(id2s)

IL=id2s(i);
Udc=Ud;
Eon_1= ((Udc*IL.^2/(2*di_dt_on))+(Udc^2.*IL/(2*dv_dt_on)));

Eon_x=Eon_1+E_zcs;

Eon=[Eon Eon_x];

end

P_loss_switching_on= 3*(sum(Eon))*f1;

% Switch off
Eoff=[];

for i= 1:length(is2d)

IL=is2d(i);
Udc=Ud;
Eoff_x= ((Udc*IL.^2/(2*di_dt_off))+(Udc^2.*IL/(2*dv_dt_off)));

Eoff=[Eoff Eoff_x];
end

P_loss_switching_off= 3*(sum(Eoff))*f1;
%
P_loss_switching= P_loss_switching_on+P_loss_switching_off;
Pcon=Ploss_con_3Leg;
%
Ptot= P_loss_switching+ Pcon;

[ P_loss_switching Pcon Ptot]/1e3

eff=300e3/(300e3+Ptot);

Ptot_x=[Ptot_x Ptot];

end

Ptot_y=[Ptot_y ; Ptot_x];

end

[X,Y] = meshgrid(fc_x/1e3,number_of_parallel_dies_x);

%%
figure1 = figure();
colormap("jet")

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

hLines = 500; 
[~,h] = contour(X,Y,Ptot_y,hLines,'Fill','on',"EdgeAlpha",1,"FaceAlpha",1,'DisplayName','Loss (W)');

targetLoss = 1500;
contour(X, Y, Ptot_y, [targetLoss, targetLoss], 'LineColor', [1 1 1], 'LineWidth', 2,'DisplayName','Loss Limit at 1500 W');
colorbar()

% Create xline
% xline(10,'DisplayName','10 kHz','Parent',axes1,'LineStyle','--',...
%     'Color',[1 1 1],...
%     'LineWidth',2);

% Create xline
% xline(10,'DisplayName','10 kHz','Parent',axes1,'LineStyle','-.',...
%     'Color',[1 1 1],...
%     'LineWidth',2);

% Create ylabel
ylabel('Number of Parallel Easy SiC','FontName','Times');

% Create xlabel
xlabel('Switching Frequency (kHz)','FontName','Times');

axis(axes1,'tight');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times','FontSize',20);
% Create colorbar
colorbar(axes1);

% title_x= strcat(  'dv/dt ',  '= ', string(dv_dt_on/1e9),  'V/nS ');
% title(title_x,'FontSize',15);

% Create legend
legend1 = legend(axes1,'show');
set(legend1,'TextColor',[1 1 1],...
    'Position',[0.40059524410892 0.574603179002566 0.39642856232822 0.23214285061473],...
    'FontSize',15,...
    'FontName','Times New Roman',...
    'EdgeColor','none',...
    'Color','none');


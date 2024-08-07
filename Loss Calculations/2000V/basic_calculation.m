clear; 
run("Rds_on.m")
run("Switching_Energies1.m")
close all
clear  figure1 legend1 axes1

%%
  fc = 10e3; % Carrier frequency
  die_number=14;
  scaling=10;
%% Scaling with dv/dt and di/dt

% scaling=4;
a=Eon_150_inter(1);
b= Eoff_150_inter(1);

Eon_150_inter=Eon_150_inter-a;
Eoff_150_inter=Eoff_150_inter-b;

Eon_150_inter=Eon_150_inter/scaling;
Eoff_150_inter=Eoff_150_inter/scaling;


Eon_150_inter=Eon_150_inter+a;
Eoff_150_inter=Eoff_150_inter+b;



%% Scaling die area
% die_number=4;

rds_inter=rds_inter*10;
Eon_150_inter= Eon_150_inter-(Eon_150_inter(1))+Eon_150_inter(1)/10;
Eoff_150_inter= Eoff_150_inter-(Eoff_150_inter(1))+Eoff_150_inter(1)/10;

rds_inter=rds_inter/die_number;

Eon_150_inter=Eon_150_inter+ Eon_150_inter(1)*die_number;
Eoff_150_inter=Eoff_150_inter+ Eoff_150_inter(1)*die_number;
%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(Eon_150_Id , Eon_150_inter,'DisplayName','Switch-on','Marker','x','LineWidth',0.1,...
    'Color',[1 0 0]);
% Create plot
plot(Eoff_150_Id , Eoff_150_inter,'DisplayName','Switch.off','Marker','x','LineWidth',0.1,...
    'Color',[0 0 1]);
% Create ylabel
ylabel({'Switching Energies (mJ)'});
% Create xlabel
xlabel({'Current (A)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);



%%
        ma=1.15;   % Modulation index
        f1 = 100; % Fundamental frequency
        % fc = 30e3; % Carrier frequency
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

%% Conduction
Tjx= [];
Ploss_con_Tj=[];

for Tj=75:5:175
% Define your arrays
% Tj= 125; % The value you want to find the nearest point for
% Find the index of the nearest point in array1
[~, index] = min(abs(rds_T - Tj));
rds_Tj= rds_inter(index);
Ploss_con_time_leg=(ip.^2)*rds_Tj;
Ploss_con = mean(Ploss_con_time_leg)*3;
Ploss_con_Tj=[Ploss_con_Tj Ploss_con];
Tjx=[Tjx Tj];
end
 % plot(Tjx,Ploss_con_Tj)
%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(Tjx,Ploss_con_Tj,"Marker",'x','LineWidth',0.1,...
    'Color',[1 0 0]);
% Create ylabel
ylabel({'Conduction Loss (W)'});
% Create xlabel
xlabel({'Tj (C^o)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
% Create legend
% legend1 = legend(axes1,'show');
% set(legend1,...
    % 'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);



%%
%%
Eon=[];
for i= 1:length(id2s)
[~, index] = min(abs( id2s(i)- Eon_150_Id));
Eon=[Eon Eon_150_inter(index)];
end
%%
Eoff=[];
for i= 1:length(is2d)
[~, index] = min(abs( is2d(i)- Eoff_150_Id));
Eoff=[Eoff Eoff_150_inter(index)];
end

% plot(Eon)
% hold off
% plot(Eoff)
%%
fon=linspace(0,1000\f1,length(Eon));
foff=linspace(0,1000\f1,length(Eoff));
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
stem(fon,Eon,'DisplayName','Eon',"Marker",'x','LineWidth',0.1,...
    'Color',[1 0 0]);
yline(3*sum(Eon)*f1/1000,'DisplayName','P_{sw-on}','LineWidth',0.1,'Color',[0 0 1]);
% Create ylabel
ylabel({'Energy (Joule), Switching  Loss (W)'});
% Create xlabel
xlabel({'Time (ms)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);
% 
% xlim([0 2*pi])

%%
fon=linspace(0,1000\f1,length(Eon));
foff=linspace(0,1000\f1,length(Eoff));
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
stem(fon,Eoff,'DisplayName','Eoff',"Marker",'x','LineWidth',0.1,...
    'Color',[1 0 0]);
yline(3*sum(Eoff)*f1/1000,'DisplayName','P_{sw-off}','LineWidth',0.1,'Color',[0 0 1]);
% Create ylabel
ylabel({'Energy (Joule), Switching  Loss (W)'});
% Create xlabel
xlabel({'Time (ms)'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',14);
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.236309526683319 0.729166666666667 0.238690473316681 0.101010101010102]);


% close all
%%
P_loss_switching= 3*(sum(Eon)+sum(Eoff))*f1/1000;

Pcon=Ploss_con_Tj(16); % Tj 100
Ptot= P_loss_switching+ Pcon;

eff=300e3/(300e3+Ptot);

[P_loss_switching Pcon Ptot]



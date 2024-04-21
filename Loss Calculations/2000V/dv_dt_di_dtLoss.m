clear; 
run("Rds_on.m");
% run("Switching_Energies1.m")
close all
%%
        ma=1.15;   % Modulation index
        f1 = 100; % Fundamental frequency
        fc = 10e3; % Carrier frequency
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
Eoss=10e-3;
Eon=[];
%on
di_dt= 5e9; % A/s
dv_dt= 10e9; % V/s

for i= 1:length(id2s)

Vdc=1250;


dt= id2s(i)/di_dt;

I_max=id2s(i);
V_max= Vdc;
V_min= Vdc-dv_dt*dt;

a=(V_max*I_max);
b=(V_max-V_min)*I_max;

Eon_1= (a/2)*(dt)-(b/3)*(dt);

V_max=V_min;
I_max=id2s(i);

dt=V_max/dv_dt;

a=V_max*I_max;
b= V_max*I_max;

Eon_2= a*dt- (b/2)*dt;

Eon_x=Eon_1+Eon_2+Eoss;

Eon=[Eon Eon_x*1e3];
end
%%
Eoff=[];
di_dt= 20e9; % A/s
dv_dt= 15e9; % V/s

for i= 1:length(is2d)


Vdc=1250;

V_max=Vdc;
I_max=is2d(i);

dt=V_max/dv_dt;

a=V_max*I_max;

Eoff_1= (a/2)*dt;


V_max=Vdc;
I_max=is2d(i);

dt=I_max/di_dt;

a=V_max*I_max;

Eoff_2= (a/2)*dt;

Eoff_x=Eoff_1+Eoff_2;



Eoff=[Eoff Eoff_x*1e3];
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
Pcon=Ploss_con_Tj(6);
%%
Ptot= P_loss_switching+ Pcon;

[ P_loss_switching Pcon Ptot]

eff=300e3/(300e3+Ptot);



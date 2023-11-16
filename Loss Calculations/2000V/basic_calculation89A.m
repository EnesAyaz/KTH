clear; 
run("Rds_on_75.m")
run("Switching_Energies.m")
close all

%%
        ma=1;   % Modulation index
        f1 = 1e3; % Fundamental frequency
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

Ud = 1200; % p2p DC voltage
module=20;
P = 300e3/module;    % Only 200 kW
cosphi =1;  % Cos(phi) at inverter terminal
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

for Tj=25:5:175
   
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
 plot(Tjx,module*Ploss_con_Tj/1e3)

%%
%%
Eon=[];
for i= 1:length(id2s)
[~, index] = min(abs( id2s(i)- Eon_175_Id));
Eon=[Eon Eon_175_inter(index)];
end
%%
Eoff=[];
for i= 1:length(is2d)
[~, index] = min(abs( is2d(i)- Eoff_175_Id));
Eoff=[Eoff Eoff_175_inter(index)];
end


Er=[];
for i= 1:length(is2d)
[~, index] = min(abs( is2d(i)- Er_175_Id));
Er=[Er Er_175_inter(index)];
end


% plot(Eon)
% hold off
% plot(Eoff)

P_loss_switching= module*3*(sum(Eon)+sum(Eoff)+sum(Er))*f1/1e6






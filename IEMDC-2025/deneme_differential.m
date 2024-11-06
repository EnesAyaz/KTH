% clear;
% Compute modulation pattern in time domain
topology='2L' ;
switch topology
case '2L' 
        ma=0.5381;   % Modulation index
        f1 = 300; % Fundamental frequency
        fc = 10200; % Carrier frequency
        pn = fc/f1; % Pulse number
        npoints = (1/f1)*1e7; % Number of timepoints
        carrytype='tria'; % carrier type 
        smp= 'ns';  % reference sampling mode 
        cmode='none'; % reference common-mode injection 
        % cmode='tri6'; % reference common-mode injection 
        thetac=0; % carrier phase offset
        start_angle= 0; % reference angle to start with
        end_angle=16*pi; %reference angle to end with 
        ma_dc=0; % DC reference

        theta0=0; % reference phase offset
        [vp_a,wt_a,carr_a,ref_a] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
         theta0=2*pi/3; % reference phase offset
        [vp_b,wt_b,carr_b,ref_b] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
        theta0=4*pi/3; % reference phase offset
        [vp_c,wt_c,carr_c,ref_c] = mod_2lcarr(ma, pn,  npoints ,carrytype,smp,cmode,theta0,thetac,start_angle,end_angle,ma_dc); 
        % Numerical waveforms during one cycle
        vp= vp_a- (vp_a+vp_b+vp_c)/3;
        wt= wt_a;
        carr= carr_a;
        ref= ref_a;

case '3L' 
        ma=1;   % Modulation index
        f1 = 50; % Fundamental frequency
        fc = 1e3; % Carrier frequency
        p = fc/f1; % Pulse number
        nlev=3;
        theta0=0;
        npts = 10000; % Number of timepoints
        type='sc1'; % carrier type 
        opt='3rd1'; % reference common-mode injection
        thetac=0; % carrier phase offset
        %scale=0;
        %offset=0;
        %carrmod=0;
        [vp,wt,ref,carr] = mlspwm(ma, p ,nlev, theta0, npts,type,opt);  % Numerical waveforms during one cycle
end 

% Compute phase current in time domain (sinusoidal for simplicity)
Ud = 625; % p2p DC voltage
% P = 300e3;    % Only 200 kW because the chosen semiconductor device is too small
% cosphi =0.9;  % Cos(phi) at inverter terminal
% uppk = ma*Ud/2; % Peak phase voltage reference;
cosphi =0.9329;  % Cos(phi) at inverter terminal
ippk = 395.7;  % Peak phase current
phi= acos(cosphi);       % Load angle
ip = ippk*cos(wt-phi);   % sampled phase current over one cycle

%% plot waveforms
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1,...
    'Position',[0.131785714285714 0.11 0.775 0.815]);
hold(axes1,'on');
% Create multiple line objects using matrix input to plot
plot1 = plot(wt,vp*Ud/2,'LineWidth',2);
plot2 = plot(wt,ip,'LineWidth',2);
set(plot1,'DisplayName','Voltage','Color',[0 0 1]);
set(plot2,'DisplayName','Current','Color',[1 0 0]);
% Create xlabel
xlabel({''});
ylabel(' Voltage (V), Current (A)')
% Uncomment the following line to preserve the X-limits of the axes
% xlim(axes1,[0 6.28318530717959]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XTick',...
    [0 pi/3 2*pi/3 pi 4*pi/3 5*pi/3 2*pi],'XTickLabel',...
    {'0','\pi /3','2\pi /3','\pi','4\pi /3 ',' 5\pi/3 ',' 2\pi '},'xlim', [0 2*pi]);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.434379533689465 0.726286774195283 0.171717168305458 0.104966137129351]);
%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1,...
    'Position',[0.131785714285714 0.11 0.775 0.815]);
hold(axes1,'on');
% Create multiple line objects using matrix input to plot
plot1 = plot(wt,ref,'LineWidth',2);
plot2 = plot(wt,carr,'LineWidth',2);
set(plot1,'DisplayName','Reference','Color',[0 0 1]);
set(plot2,'DisplayName','Carrier Signal','Color',[1 0 0]);
% Create xlabel
xlabel({''});
% Uncomment the following line to preserve the X-limits of the axes
% xlim(axes1,[0 6.28318530717959]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XTick',...
    [0 pi/3 2*pi/3 pi 4*pi/3 5*pi/3 2*pi],'XTickLabel',...
    {'0','\pi /3','2\pi /3','\pi','4\pi /3 ',' 5\pi/3 ',' 2\pi '},'YTick',...
    [-1 -0.75 -0.5 -0.25 0 0.25 0.5 0.75 1],'xlim', [0 2*pi]);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.434379533689465 0.726286774195283 0.171717168305458 0.104966137129351]);




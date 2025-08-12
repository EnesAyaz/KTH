Icap_prop_XY=[];
Icap_conv_XY=[];

ma_values = 0:0.1:1;
pf_values = 0:0.1:1;

%% Time array
for ma = ma_values

Icap_prop_X=[];
Icap_conv_X=[];

for pf=pf_values
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
if variable_carrier==0
Icap_con=rms(IphA.*SA+IphB.*SB+IphC.*SC-mean(IphA.*SA+IphB.*SB+IphC.*SC));
else 
Icap_prop=rms(IphA.*SA+IphB.*SB+IphC.*SC-mean(IphA.*SA+IphB.*SB+IphC.*SC));  
end

end
Icap_prop_X=[Icap_prop_X Icap_prop];
Icap_conv_X=[Icap_conv_X Icap_con];

end

Icap_prop_XY=[Icap_prop_XY; Icap_prop_X];
Icap_conv_XY=[Icap_conv_XY; Icap_conv_X];

end
%%

% Create modulation index and power factor grids


[MaGrid, PfGrid] = meshgrid(ma_values, pf_values);

% Transpose to match meshgrid orientation
Icap_conv_plot = Icap_conv_XY';  % size: [length(pf_values), length(ma_values)]
Icap_prop_plot = Icap_prop_XY';

% Determine common color limits
zmin = min([Icap_conv_plot(:); Icap_prop_plot(:)]);
zmax = max([Icap_conv_plot(:); Icap_prop_plot(:)]);

%%
% Plot
figure;

contourf(MaGrid, PfGrid, Icap_conv_plot, 20, 'LineColor', 'none');
caxis([zmin zmax]);
colormap('jet');
% Increase tick label font sizes
set(gca, 'FontSize', 15);  % Axis tick font size
title('Capacitor Curent (RMS p.u.)', 'Interpreter', 'latex','FontSize',20);
xlabel('Modulation Index ($m_a$)', 'Interpreter', 'latex','FontSize',20);
ylabel('Power Factor ($p.f.$)', 'Interpreter', 'latex','FontSize',20);
% Add and format colorbar
c = colorbar;
c.Label.String = '';       % Optional: set colorbar label
c.FontSize = 18;           % Colorbar tick font size

%%
figure;
contourf(MaGrid, PfGrid, Icap_prop_plot, 20, 'LineColor', 'none');

caxis([zmin zmax]);
colormap('parula');
colormap('jet');
% Increase tick label font sizes
set(gca, 'FontSize', 15);  % Axis tick font size
title('Capacitor Curent (RMS p.u.)', 'Interpreter', 'latex','FontSize',20);
xlabel('Modulation Index ($m_a$)', 'Interpreter', 'latex','FontSize',20);
ylabel('Power Factor ($p.f.$)', 'Interpreter', 'latex','FontSize',20);
% Add and format colorbar
c = colorbar;
c.Label.String = '';       % Optional: set colorbar label
c.FontSize = 18;           % Colorbar tick font size

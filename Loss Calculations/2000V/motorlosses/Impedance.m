 load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\Harmonics_analysis\Harmonics_analysis\EMimpedanceData.mat');
f=EM_impedance_stator_only.f;
Z_mag=EM_impedance_stator_only.Z/2; %% phase impedance
Z_angle=EM_impedance_stator_only.theta*pi/180;
%%
f=EM_impedance_stator_rotor_housing.f;
Z_mag=EM_impedance_stator_rotor_housing.Z/2; %% phase impedance
Z_angle=EM_impedance_stator_rotor_housing.theta*pi/180;

%%
f=f(1:end-2);
Z_mag=Z_mag(1:end-2);
Z_angle=Z_angle(1:end-2);
Z= Z_mag.*exp(-1i.*Z_angle);
%%
figure(1)
loglog(f,abs(Z))
hold on;
loglog(f,real(Z))
hold on;
 loglog(f,abs(imag(Z)))
hold on
% plot(f/1e3,sqrt(imag(Z).^2+real(Z).^2))
xlim([10e2 10e6])

%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create multiple line objects using matrix input to loglog
loglog1 = loglog(f,abs(Z),'LineWidth',2,'Parent',axes1);
loglog2 = loglog(f,real(Z),'LineWidth',2,'Parent',axes1);
loglog3 = loglog(f,abs(imag(Z)),'LineWidth',2,'Parent',axes1);

set(loglog1,'DisplayName','Z','Color',[0 0 1]);
set(loglog2,'DisplayName','R','Color',[0 0 0]);
set(loglog3,'DisplayName','|X|','LineStyle','--','Color',[1 0 0]);

% Create ylabel
ylabel({'Ohm'});
% Create xlabel
xlabel({'Frequency (Hz)'});

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[1000 10000000]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XMinorTick','on',...
    'XScale','log','YMinorTick','on','YScale','log');
% Create legend
legend(axes1,'show');

% Create textarrow
annotation(figure1,'textarrow',[0.591071428571429 0.598214285714285],...
    [0.238095238095238 0.785714285714287],'String',{'Resonance'},'FontSize',15,...
    'FontName','Times New Roman');

% Create textbox
annotation(figure1,'textbox',...
    [0.620642857142856 0.31904761904762 0.211500000000001 0.0738095238095239],...
    'String',{'Capacitive'},...
    'FontSize',15,...
    'FontName','Times New Roman',...
    'FitBoxToText','off',...
    'EdgeColor','none');

% Create textbox
annotation(figure1,'textbox',...
    [0.417071428571428 0.342857142857143 0.122214285714286 0.0452380952380958],...
    'String',{'Inductive'},...
    'FontSize',15,...
    'FontName','Times New Roman',...
    'FitBoxToText','off',...
    'EdgeColor','none');

%%
R=real(Z);

loss_factor= R./Z_mag./Z_mag;

%%
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create semilogx
semilogx(f,loss_factor,'LineWidth',2,'Color',[0 0 1]);
% Create ylabel
ylabel({'Loss Factor (W/V^2)'},'FontSize',15);
% Create xlabel
xlabel({'Frequency (Hz)'},'FontSize',15);
% Uncomment the following line to preserve the X-limits of the axes
 xlim(axes1,[1000 1000000]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'MinorGridAlpha',0.5,'XGrid','on','XMinorTick','on','XScale','log','YGrid',...
    'on','YMinorGrid','on','ZMinorGrid','on');


%%
% figure(2)
% loglog(f,loss_factor)
% xlim([1e3 1e6])

%%

% Sample frequency and data arrays (assuming sorted frequencies)
frequencies = f;
data = loss_factor;

% Example frequency input
freq_input = 20e3;

% Perform linear interpolation
interp_data = interp1(frequencies, data, freq_input, 'linear');

interp_data*1e3
%%
M=1;
fsw=10e3;
ffund=500;
p=fsw/ffund;
nharm=16*p;
theta0=0;
thetac=0;
Va= spect2lanalyt(p,M,nharm,'tria' ,theta0,thetac);
theta0=2*pi/3;
Vb= spect2lanalyt(p,M,nharm,'tria' ,theta0,thetac);
theta0=4*pi/3;
Vc= spect2lanalyt(p,M,nharm,'tria' ,theta0,thetac);
Vll=Va-Vb;
Vll2=Vc-Va;
Va_n= (Vll-Vll2)/3;
Vll=Vll*650;
Va_n= Va_n*650;

Va=abs(Va(2:end));
Va_n=abs(Va_n(2:end));
Vll=abs(Vll(2:end));

fll=1:1:length(Vll);
fll= fll*ffund;

Ph=[];
%
for i=1:length(fll)

loss_factor = interp1(frequencies, data, fll(i), 'linear');

Ph= [ Ph ((Va_n(i)^2)/2)*loss_factor];

end
Ph=Ph*3;
% Ph=Ph;

%
stem(fll,Ph)

sum(Ph)-max(Ph)


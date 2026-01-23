 % load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\Harmonics_analysis\Harmonics_analysis\EMimpedanceData.mat');
load('C:\Users\enesa\OneDrive - KTH\Hemizero\Harmonics_analysis\Harmonics_analysis\EMimpedanceData.mat')

 %%
f=EM_impedance_stator_only.f;
Z_mag=EM_impedance_stator_only.Z/4; %% phase impedance
Z_angle=EM_impedance_stator_only.theta*pi/180;
%%
% f=EM_impedance_stator_rotor_housing.f;
% Z_mag=EM_impedance_stator_rotor_housing.Z/2; %% phase impedance
% Z_angle=EM_impedance_stator_rotor_housing.theta*pi/180;
%%
%%
f=f(1:end-2);
Z_mag=Z_mag(1:end-2);
Z_angle=Z_angle(1:end-2);
Z= Z_mag.*exp(-1i.*Z_angle);
%%
R=real(Z);
loss_factor= R./Z_mag./Z_mag;

frequencies = f;
data = loss_factor;
%%
P_M=[];
M1=[];

for M=0:0.1:1

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

P_M =[ P_M (sum(Ph)-max(Ph))];
M1= [ M1 M];

end
%%
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot(M1,P_M,'Marker','o','LineWidth',2,'Color',[0 0 1]);

% Create ylabel
ylabel({'Harmonic Loss (W)'},'FontSize',15);

% Create xlabel
xlabel({'Modulation Index'},'FontSize',15);

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'MinorGridAlpha',0.5,'XGrid','on','XMinorGrid','on','YGrid','on',...
    'YMinorGrid','on');

%%
P_M=[];
fsw1=[];

for fsw=5e3:1e3:30e3
M=1;
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

P_M =[ P_M sum(Ph)-max(Ph)];
fsw1= [ fsw1 fsw];

end

%  save('savefsw1.mat','fsw1');
% save('savePM.mat','P_M');
%%

%% ===================== Harmonic Loss vs Switching Frequency =====================
f1 = figure('Color','w','Position',[220 180 780 520],'Renderer','painters');
ax1 = axes('Parent',f1);
hold(ax1,'on'); box(ax1,'on'); grid(ax1,'on');

% Define dull blue tone
c1 = [60 85 140]/255;

% Plot Harmonic Loss vs Switching Frequency
plot(fsw1/1e3, P_M/2, '-o', ...
     'LineWidth', 2.2, ...
     'MarkerSize', 7, ...
     'MarkerFaceColor', c1, ...
     'Color', c1);

% Axis labels and limits
xlabel('Switching Frequency (kHz)', ...
       'FontName','Times New Roman', 'FontSize', 20);
ylabel('Harmonic Loss (W)', ...
       'FontName','Times New Roman', 'FontSize', 20);

xlim([min(fsw1)/1e3 max(fsw1)/1e3]);
ylim([0 max(P_M/2)*1.1]);

% Axes formatting
set(ax1, 'FontName','Times New Roman', 'FontSize', 20, ...
          'LineWidth',1.2, ...
          'GridAlpha',0.25, 'MinorGridAlpha',0.15, ...
          'XGrid','on','YGrid','on', ...
          'XMinorTick','on','YMinorTick','on');

% Optional annotation of minimum loss point
% [~, idx_min] = min(P_M);
% text(fsw1(idx_min)/1e3, P_M(idx_min)*1.05, ...
%      sprintf('Min @ %.1f kHz', fsw1(idx_min)/1e3), ...
%      'FontName','Times New Roman', 'FontSize', 16, ...
%      'Color', c1, 'HorizontalAlignment','center');

% % Export as vector PDF
% exportgraphics(f1, 'HarmonicLoss_vs_Fsw.pdf', ...
%                'ContentType','vector', ...
%                'BackgroundColor','white');

%%

f=[10 15 20 25];
loss= [1927 1749 1769 1856];
lossH= [960 618 468 385];
lossIn=[967 1131 1301 1471];

% lossH= [252 230 214 202 ];
loss=lossH+lossIn;

figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot(f,loss,'Marker','o','LineWidth',2,'Color',[0 0 0]);
hold on
plot(f,lossH,'Marker','o','LineWidth',2,'Color',[0 0 1]);
hold on
plot(f,lossIn,'Marker','o','LineWidth',2,'Color',[1 0 0]);
hold on

% Create ylabel
ylabel({'Harmonic Loss (W)'},'FontSize',15);

% Create xlabel
xlabel({'Switching Frequency (kHz)'},'FontSize',15);

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'MinorGridAlpha',0.5,'XGrid','on','XMinorGrid','on','YGrid','on',...
    'YMinorGrid','on');

ylim([0 2000])
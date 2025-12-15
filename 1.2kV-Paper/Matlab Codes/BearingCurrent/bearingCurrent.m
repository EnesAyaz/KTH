%% One switching period SPWM: six-step CMV and bearing voltage (800 V vs 1200 V)
clear; clc; close all;

% -------------------- Parameters --------------------
ma      = 0.8;             % modulation index
theta   = 0;               % electrical angle
fsw     = 10e3;            % switching frequency [Hz]
Ts      = 1/fsw;           % switching period [s]
Fs      = 5e6;             % sample rate [Hz]
t       = (0:1/Fs:Ts).';   % single switching period

% -------------------- Duty cycles (centered SPWM) --------------------
mA = ma*sin(theta);
mB = ma*sin(theta - 2*pi/3);
mC = ma*sin(theta + 2*pi/3);

dA = 0.5*(1 + mA);
dB = 0.5*(1 + mB);
dC = 0.5*(1 + mC);

Tc = Ts/2;
tA1 = Tc - dA*Ts/2; tA2 = Tc + dA*Ts/2;
tB1 = Tc - dB*Ts/2; tB2 = Tc + dB*Ts/2;
tC1 = Tc - dC*Ts/2; tC2 = Tc + dC*Ts/2;

Sa = double(t>=tA1 & t<tA2);
Sb = double(t>=tB1 & t<tB2);
Sc = double(t>=tC1 & t<tC2);

% -------------------- Capacitances & BVR --------------------
Csr      = 1.2e-9;      % stator–rotor [F]
Cwr_800  = 400e-12;     % winding–rotor [F]
Cwr_1200 = 300e-12;     % reinforced insulation
Cb_each  = 150e-12;     % per bearing [F]
Cb_tot   = 10*Cb_each;

BVR_800  = Cwr_800  /(Cwr_800  + Csr + Cb_tot);
BVR_1200 = Cwr_1200 /(Cwr_1200 + Csr + Cb_tot);

% -------------------- Voltages --------------------
Vdc_800  = 800;  Vdc_1200 = 1200;

vA800 = (Sa-0.5)*Vdc_800;  vB800 = (Sb-0.5)*Vdc_800;  vC800 = (Sc-0.5)*Vdc_800;
vCM800 = (vA800 + vB800 + vC800)/3;

vA1200 = (Sa-0.5)*Vdc_1200; vB1200 = (Sb-0.5)*Vdc_1200; vC1200 = (Sc-0.5)*Vdc_1200;
vCM1200 = (vA1200 + vB1200 + vC1200)/3;

vBear800  = BVR_800  * vCM800;
vBear1200 = BVR_1200 * vCM1200;

% -------------------- Plot styling --------------------
set(groot, 'DefaultAxesFontName','Times New Roman', ...
           'DefaultAxesFontSize',20, ...
           'DefaultTextFontName','Times New Roman', ...
           'DefaultLineLineWidth',1.8);

% Muted color palette
c1 = [0.36 0.54 0.75];   % muted blue (base)
c3 = [0.60 0.75 0.90];   % lighter blue
c2 = [0.25 0.35 0.55];   % darker blue

% -------------------- Figure --------------------
%% -------------------- Improved Figure Layout --------------------
figure('Color','w','Position',[200 120 800 800]); % more compact figure

% Common font settings
font_axes = 25;
font_label = 25;
font_title = 20;

t_norm = t / Ts;   % normalized time 0–1 per switching period

tiledlayout(3,1,'Padding','compact','TileSpacing','compact');

% ----- (1) PWM States -----
nexttile;
plot(t_norm,(Sa),':','Color',c3,'DisplayName','S_a','LineWidth',3); hold on;
plot(t_norm,(Sb),'--','Color',c2,'DisplayName','S_b','LineWidth',3);
plot(t_norm,(Sc),'-','Color',c1,'DisplayName','S_c','LineWidth',3);
xlim([0 1]); ylim([-0.1 1.1]);
ylabel('$S_a,S_b,S_c$','Interpreter','latex','FontSize',font_label);
%xlabel('Normalized switching period ($T_s$)','Interpreter','latex','FontSize',font_label);
xticks([0 0.5 1]); xticklabels({'0','0.5T_s','1T_s'});
title('Centered SPWM (Switching Period ($T_s$))','Interpreter','latex','FontSize',font_title);
grid on; box on;
set(gca,'FontName','Times New Roman','FontSize',font_axes);
legend('Location','southoutside','Orientation','horizontal','Box','off');

% ----- (2) CMV -----
nexttile;
plot(t_norm,vCM800,'-','Color',c3,'DisplayName','800 V','LineWidth',3); hold on;
plot(t_norm,vCM1200,':','Color',c2,'DisplayName','1200 V','LineWidth',3);
xlim([0 1]); ylim([-700 700]);
ylabel('$v_{\mathrm{CM}}$ (V)','Interpreter','latex','FontSize',font_label);
%xlabel('Normalized switching period ($T_s$)','Interpreter','latex','FontSize',font_label);
title('Common-mode Voltage', 'Interpreter','latex','FontSize',font_title);
xticks([0 0.5 1]); xticklabels({'0','0.5T_s','1T_s'});
grid on; box on;
set(gca,'FontName','Times New Roman','FontSize',font_axes);
legend('Location','southoutside','Orientation','horizontal','Box','off');

% ----- (3) Bearing Voltage -----
nexttile;
plot(t_norm,vBear800,'-','Color',c3,'DisplayName',sprintf('800 V (BVR=%.3f)',BVR_800),'LineWidth',3); hold on;
plot(t_norm,vBear1200,':','Color',c2,'DisplayName',sprintf('1200 V (BVR=%.3f)',BVR_1200),'LineWidth',3);
xlim([0 1]); ylim([-100 100]);
%xlabel('Normalized switching period (T_s)','Interpreter','latex','FontSize',font_label);
title('$V_{\mathrm{bearing}} = \mathrm{BVR} \cdot v_{\mathrm{CM}}$','Interpreter','latex','FontSize',font_title);
ylabel('$V_{\mathrm{bearing}}$ (V)','Interpreter','latex','FontSize',font_label);
xticks([0 0.5 1]); xticklabels({'0','0.5T_s','1T_s'});
grid on; box on;
set(gca,'FontName','Times New Roman','FontSize',font_axes);
legend('Location','southoutside','Orientation','horizontal','Box','off');


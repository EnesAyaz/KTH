load('C:\Users\enesa\OneDrive - KTH\Hemizero\Harmonics_analysis\Harmonics_analysis\EMimpedanceData.mat')
%% ===================== Journal plotting style ============================
set(groot,'defaultFigureColor','w',...
    'defaultAxesFontName','Times New Roman',...
    'defaultAxesFontSize',11,...
    'defaultAxesLineWidth',0.8,...
    'defaultAxesGridAlpha',0.15,...
    'defaultAxesMinorGridAlpha',0.10,...
    'defaultLineLineWidth',1.6);

% Dull blue palette
c1 = [ 70  90 120]/255;   % primary blue
c2 = [ 40  60  90]/255;   % darker blue (lines/axes)
c3 = [140 160 190]/255;   % light blue (secondary)
c4 = [180 190 205]/255;   % very light (fills)
cred = [170  70  70]/255; % muted red for |X|

% Common export helper
export = @(h,fn) exportgraphics(h, fn, 'ContentType','vector', ...
    'BackgroundColor','white');

%% ===================== Build complex impedance Z(f) ======================
% Choose the measured set you want (uncomment ONE of the two):
% S = EM_impedance_stator_only;          % stator-only
S = EM_impedance_stator_rotor_housing;   % stator + rotor + housing

f       = S.f(:);
Z_mag   = S.Z(:)/2;                      % convert to per-phase as you did
Z_angle = S.theta(:)*pi/180;
% Trim trailing two points like your script (if needed)
n = numel(f)-2;  f = f(1:n);  Z_mag = Z_mag(1:n);  Z_angle = Z_angle(1:n);

Z = Z_mag .* exp(-1j*Z_angle);
R = real(Z);
X = imag(Z);

%% ===================== Fig 1: |Z| , R , |X| (log–log) ====================
%% ===================== Impedance plot (|Z|, R, |X|) =====================
%% ===================== Impedance plot (|Z|, R, |X|) =====================

% Define consistent dull-blue shades
c1 = [60 85 140]/255;    % darkest (Impedance)
c2 = [90 120 170]/255;   % mid (Resistance)
c3 = [130 160 200]/255;  % lightest (Reactance)

% Create figure
f1 = figure('Color','w','Position',[220 180 780 520],'Renderer','painters');
ax1 = axes('Parent',f1); 
hold(ax1,'on'); box(ax1,'on'); grid(ax1,'on');

% Plot curves (all blue family)
loglog(f, abs(Z), 'Color', c1, 'LineWidth', 2.2, 'DisplayName','Impedance');
loglog(f, R,':',       'Color', c2, 'LineWidth', 2.2, 'DisplayName','Resistance');
loglog(f, abs(X), '--', 'Color', c3, 'LineWidth', 2.2, 'DisplayName','Reactance');

% Axis settings
xlim([1e3 1e7]); ylim([1e-1 1e3]);
set(ax1, 'XScale','log','YScale','log', ...
         'XMinorTick','on','YMinorTick','on', ...
         'FontName','Times New Roman','FontSize',20, ...
         'LineWidth',1.2, ...
         'GridColor',[0.7 0.7 0.7], ...
         'GridAlpha',0.25, 'MinorGridAlpha',0.15);

xlabel('Frequency (Hz)','FontName','Times New Roman','FontSize',20);
ylabel('\Omega','FontName','Times New Roman','FontSize',20);

% Legend
leg = legend('show','Location','northeast');
leg.Box = 'off';
leg.FontSize = 20;
leg.FontName = 'Times New Roman';
leg.TextColor = [40 60 90]/255;

% Optional: Annotations (blue tones)
% text(1.5e5, 2.5e2, 'Resonance','FontSize',20,'FontName','Times New Roman','Color',c1);
% text(2.5e4,  2.5e1,'Inductive','FontSize',20,'FontName','Times New Roman','Color',c2);
% text(5e5,    3e1, 'Capacitive','FontSize',20,'FontName','Times New Roman','Color',c3);

% Export as vector (high-quality PDF)
% exportgraphics(f1, 'Impedance_Z_R_X_BlueShades.pdf', ...
%                'ContentType','vector', ...
%                'BackgroundColor','white');


%% ===================== Fig 2: Equivalent inductance vs f = -X/(2πf) =====
L = -X ./ (2*pi.*f);
f2 = figure('Units','inches','Position',[0 0 3.35 2.4]);
ax2 = axes('Parent',f2); hold(ax2,'on'); box(ax2,'on'); grid(ax2,'on');
plot(f, L, 'Color', c1);
xlim([5e2 1e5]);
xlabel('Frequency (Hz)'); ylabel('Inductance (H)');
set(ax2,'XScale','linear','YScale','linear','XMinorTick','on','YMinorTick','on');
% export(f2,'Inductance_vs_Frequency.pdf');

%% ===================== Fig 3: Loss factor Φ(f) = R/|Z|^2 (semilogx) =====
%% ===================== Loss Factor Plot =====================
phi = R ./ (abs(Z).^2);     % W/V^2

% Dull blue tone
c1 = [60 85 140]/255;

% Create figure
f3 = figure('Color','w','Position',[220 180 780 520],'Renderer','painters');
ax3 = axes('Parent',f3);
hold(ax3,'on'); box(ax3,'on'); grid(ax3,'on');

% Plot
semilogx(f, phi, 'Color', c1, 'LineWidth', 2.2);

% Axis limits and labels
xlim([1e3 1e6]);
xlabel('Frequency (Hz)', 'FontName', 'Times New Roman', 'FontSize', 20);
ylabel('Loss Factor, \Phi (W/V^2)', 'FontName', 'Times New Roman', 'FontSize', 20);

% Axes formatting
set(ax3, 'XScale', 'log', ...
          'XMinorTick', 'on', 'YMinorTick', 'on', ...
          'FontName', 'Times New Roman', 'FontSize', 20, ...
          'LineWidth', 1.2, ...
          'GridAlpha', 0.25, 'MinorGridAlpha', 0.15);

% Optional y-range (comment out if not needed)
% ylim([1e-7 1e-3]);

% Export as vector (journal quality)
exportgraphics(f3, 'LossFactor_phi.pdf', ...
               'ContentType', 'vector', ...
               'BackgroundColor', 'white');


%% ===================== Fig 4: Harmonic loss sum using your PWM spectrum ==
% --- build phase-to-neutral harmonic spectrum using your function ---------
ffund  = 500;          % Hz
fsw    = 10e3;         % Hz
p      = fsw/ffund;
nharm  = 16*p;
M      = 1; theta0=0; thetac=0;

Va   = spect2lanalyt(p,M,nharm,'tria',theta0,thetac);
Vb   = spect2lanalyt(p,M,nharm,'tria',2*pi/3,thetac);
Vc   = spect2lanalyt(p,M,nharm,'tria',4*pi/3,thetac);

Vll   = Va - Vb;                % line-line
Vll2  = Vc - Va;
Va_n  = (Vll - Vll2)/3;         % phase-to-neutral harmonic voltage (per your code)

% Scale to 650 Vdc (rms of harmonic components scale with Vdc)
Vdc_scale = 650;
Va_n = abs(Va_n(2:end))*Vdc_scale;   % drop DC/1st bin as you did
f_h  = (1:numel(Va_n))*ffund;        % harmonic frequencies

% Interpolate phi(f) at harmonic bins (pchip smoother than linear)
phi_interp = interp1(f, phi, f_h, 'pchip', 'extrap');

% Per-phase additional loss contribution at each harmonic
Ph = (Va_n.^2)/2 .* phi_interp;      % W (per phase)
Ph_total = 3*Ph;                     % 3-phase
total_harmonic_loss = sum(Ph_total) - max(Ph_total);  %#ok<NOPTS>

% ---- stem-like plot with journal styling ---------------------------------
f4 = figure('Units','inches','Position',[0 0 3.35 2.4]);
ax4 = axes('Parent',f4); hold(ax4,'on'); box(ax4,'on'); grid(ax4,'on');
% Use stem look without markers (cleaner for print)
for k = 1:numel(f_h)
    plot([f_h(k) f_h(k)],[0 Ph_total(k)],'Color',c2,'LineWidth',1.1);
end
plot(f_h, Ph_total, '.', 'Color', c1, 'MarkerSize', 6); % subtle tops
xlim([ffund 20e3]);  % adjust as needed
xlabel('Frequency (Hz)'); ylabel('Harmonic Loss (W)');
set(ax4,'XScale','log','XMinorTick','on','YMinorTick','on');
% export(f4,'HarmonicLosses_Stem.pdf');

% Display the total (excluding dominant fundamental-like peak if present)
disp(['Total harmonic loss (excluding max bin): ', ...
      num2str(total_harmonic_loss,'%.2f'), ' W']);



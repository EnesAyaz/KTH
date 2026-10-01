% fig_intro_ronsp_trend.m
%
% Ideal unipolar specific on-state resistance R_on,sp (left axis) and
% the resulting high-frequency figure of merit
% FOM = 1/sqrt(R_on,sp * C_oss,sp) (right axis) versus blocking voltage,
% for Si, 4H-SiC, and GaN. Reproduces Fig. 2 of the SPB review paper
% (previously drawn inline in TikZ/pgfplots in
% Sections/Section_I_Intro.tex).
%
% -------------------------------------------------------------------
% R_on,sp(V) = RonCoeff * V^RonExp   [mOhm*cm^2], V in volts
%   Power-law fits to the ideal 1-D unipolar drift-region limit. The
%   coefficients below reproduce the curves already cited in the paper
%   next to this figure (Millan et al., "A Survey of Wide Bandgap
%   Power Semiconductor Devices," IEEE Trans. Power Electron., 2014;
%   Udrea, Deboy & Fujihira, "Superjunction Power Devices, History,
%   Development, and Future Prospects," IEEE Trans. Electron Devices,
%   2017). Si follows the well-known empirical ~V^2.5 trend; 4H-SiC and
%   GaN sit close to the ideal constant-critical-field exponent of 2.
%
% C_oss,sp(V) = eps0*epsR*Ecrit / (2*V)   [F/cm^2]
%   Specific (per-unit-area) capacitance of the fully depleted drift
%   region at the rated blocking voltage, from the classical abrupt
%   one-sided-junction unipolar-limit derivation (Baliga, "Fundamentals
%   of Power Semiconductor Devices," Springer, 2008, Ch. 3): for a
%   triangular field profile, V = Ecrit*W/2 and the breakdown depletion
%   width W = eps*Ecrit/(q*Nd) combine to give W(V) = 2*V/Ecrit, so the
%   specific capacitance C = eps/W = eps0*epsR*Ecrit/(2*V) falls off as
%   1/V. epsR and Ecrit are the standard tabulated material constants
%   (e.g. Millan et al. 2014, Table I; Baliga 2008) -- this is the
%   literature-grounded counterpart to R_on,sp requested for this
%   figure, in exactly the same spirit as the existing R_on,sp curves.
%
% FOM(V) = 1/sqrt(R_on,sp(V) * C_oss,sp(V))
%   Baliga's high-frequency figure of merit (Baliga, "Power
%   semiconductor device figure of merit for high-frequency
%   applications," IEEE Electron Device Lett., 1989).
%
% Every material constant is exposed in the PARAMETERS block below --
% edit epsR, Ecrit, or the R_on,sp coefficients/exponents directly to
% try different literature values or fits; everything downstream
% (both curves, the crossover-based plot domains, and the export)
% recomputes automatically.

clear; close all; clc;

%% ===================== PARAMETERS (edit freely) ========================
eps0 = 8.8541878128e-14;   % vacuum permittivity, F/cm

% name      : legend label
% color     : RGB plot color
% RonCoeff, RonExp : Ron,sp[mOhm*cm^2] = RonCoeff * V[Volt]^RonExp
% epsR      : relative permittivity (dielectric constant)
% Ecrit_Vcm : critical electric field for avalanche breakdown, V/cm
% Vmin,Vmax : plotted voltage domain for this material's curves, V
%             (Vmin is simply where each curve is drawn from for
%             visual clarity at low voltage; it is not derived from a
%             physical crossover, and can be set to Vmin=Vplot(1) for
%             all materials if you want the curves drawn over the full
%             range instead)

% Colors match Fig. 1's blue/red palette (Figures/Section-Intro/
% fig_intro_hv_motivation.m) plus a matching green for the third
% material, so the paper's figures read as one consistent color system.
mat(1).name  = 'Si';
mat(1).color = [0.10 0.20 0.55];   % same blue as Fig. 1
mat(1).RonCoeff = 5e-6;   mat(1).RonExp = 2.5;
mat(1).epsR = 11.7;       mat(1).Ecrit_Vcm = 0.3e6;    % Baliga 2008; Millan 2014
mat(1).Vmin = 10;         mat(1).Vmax = 1000;

mat(2).name  = '4H-SiC';
mat(2).color = [0.65 0.06 0.06];   % same red as Fig. 1
mat(2).RonCoeff = 2e-7;   mat(2).RonExp = 2.0;
mat(2).epsR = 9.7;        mat(2).Ecrit_Vcm = 2.2e6;    % Millan 2014, Table I
mat(2).Vmin = 22.4;       mat(2).Vmax = 1000;

mat(3).name  = 'GaN';
mat(3).color = [0.00 0.45 0.15];   % matching green
mat(3).RonCoeff = 5e-8;   mat(3).RonExp = 2.0;
mat(3).epsR = 9.0;        mat(3).Ecrit_Vcm = 3.3e6;    % Millan 2014, Table I
mat(3).Vmin = 44.7;       mat(3).Vmax = 1000;

Vaxis = [10 1000];         % left/right axis voltage range, V

% Unit reduction check: Ron,sp is an area-specific resistance (Ohm*cm^2)
% and Coss,sp an area-specific capacitance (F/cm^2), so their product
% Ron,sp*Coss,sp = Ohm*F -- the cm^2 area units cancel completely,
% leaving a pure RC time constant in seconds. FOM = 1/sqrt(RC) therefore
% reduces exactly to 1/sqrt(s) = sqrt(Hz); no area units survive, so
% there IS a real reduced unit here rather than needing "a.u.".
%   normalizeFOM=false (default): plot the physically computed FOM in
%   sqrt(Hz), rescaled by FOMunitScale for readability (values come out
%   to ~1e5-1e7 sqrt(Hz), i.e. an O(1-10) range in sqrt(MHz)).
%   normalizeFOM=true: divide by a reference value instead, back to the
%   old dimensionless "(a.u.)" convention, if you prefer that look.
normalizeFOM = false;
FOMunitScale = 1e6;        % 1e6 -> sqrt(MHz); 1e3 -> sqrt(kHz); 1 -> sqrt(Hz)
FOMunitLabel = '\sqrt{\mathrm{MHz}}';
FOMrefMaterial = 1;        % index into mat(): which material's FOM(V=FOMrefV) is used as the reference (normalizeFOM=true only)
FOMrefV = 100;              % reference voltage, V (normalizeFOM=true only)

%% ===================== Working-size scale factor =======================
% Same idea as fig_intro_hv_motivation.m: the figure is designed at a
% print size with 8-9 pt text (how it looks once \includegraphics
% scales it to the paper's column width). figScale blows the whole
% design up uniformly for comfortable on-screen editing; the exported
% PDF looks identical after LaTeX scales it back down. Just raise
% figScale for a bigger canvas.
figScale = 4;
figWcm = 8*figScale; figHcm = 3.6*figScale;   % low-profile: wide and short, not square
fontAxis  = 8*figScale;
fontAxisLatex = 8*figScale;    % same nominal size as the plain-text
                                % x-label; kept as a separate variable
                                % in case the latex/plain rendering ever
                                % needs to be nudged apart again
fontTick  = 7*figScale;
fontLeg   = 5.5*figScale;      % smaller legend text
lwCurve   = 1.3*figScale;

%% ===================== Compute curves ===================================
nMat = numel(mat);
for m = 1:nMat
    V = logspace(log10(mat(m).Vmin), log10(mat(m).Vmax), 200);
    RonSp_mOhmcm2 = mat(m).RonCoeff .* V.^mat(m).RonExp;
    RonSp_Ohmcm2  = RonSp_mOhmcm2 * 1e-3;
    CossSp_Fcm2   = eps0 .* mat(m).epsR .* mat(m).Ecrit_Vcm ./ (2*V);
    FOM = 1 ./ sqrt(RonSp_Ohmcm2 .* CossSp_Fcm2);

    mat(m).V = V;
    mat(m).RonSp_mOhmcm2 = RonSp_mOhmcm2;
    mat(m).CossSp_Fcm2 = CossSp_Fcm2;
    mat(m).FOM = FOM;
end

if normalizeFOM
    mRef = mat(FOMrefMaterial);
    FOMref = (1/sqrt( (mRef.RonCoeff*FOMrefV^mRef.RonExp*1e-3) * ...
        (eps0*mRef.epsR*mRef.Ecrit_Vcm/(2*FOMrefV)) ));
    for m = 1:nMat
        mat(m).FOMplot = mat(m).FOM / FOMref;
    end
    fomLabel = 'FOM (a.u.)';
else
    for m = 1:nMat
        mat(m).FOMplot = mat(m).FOM / sqrt(FOMunitScale);
    end
    fomLabel = ['FOM ($' FOMunitLabel '$)'];
end
allFOM = [mat.FOMplot];
fomYlim = [10^floor(log10(min(allFOM))) 10^ceil(log10(max(allFOM)))];

%% ===================== Figure ============================================
fig = figure('Color','w','Units','centimeters','Position',[2 2 figWcm figHcm]);
set(fig,'PaperPositionMode','auto');   % reliable, uncropped GUI print/export
ax = axes(fig); hold(ax,'on'); box(ax,'on');
set(ax,'XScale','log','FontSize',fontTick,'FontName','Times New Roman');
xlim(ax,Vaxis);
grid(ax,'on'); ax.GridColor = [0.85 0.85 0.85]; ax.GridAlpha = 0.5;

axColor = 'k';   % black, matching the x-axis, for both y-axes/labels

hLeft = gobjects(1,nMat);
yyaxis(ax,'left');
set(ax,'YScale','log','YColor',axColor);
for m = 1:nMat
    hLeft(m) = plot(ax, mat(m).V, mat(m).RonSp_mOhmcm2, '-', ...
        'Color', mat(m).color, 'LineWidth', lwCurve);
end
ylabel(ax,'$R_{\mathrm{on,sp}}$ (m$\Omega\cdot$cm$^2$)','Interpreter','latex', ...
    'FontSize',fontAxisLatex,'FontName','Times New Roman','Color',axColor);
ylim(ax,[1e-4 1e4]);
% Force a readable set of tick labels -- with a low-profile (short)
% figure MATLAB's automatic log-axis ticking can collapse to a single
% label, so space them explicitly every 2 decades instead.
set(ax,'YTick',10.^(-4:2:4));

hRight = gobjects(1,nMat);
yyaxis(ax,'right');
set(ax,'YScale','log','YColor',axColor);
for m = 1:nMat
    hRight(m) = plot(ax, mat(m).V, mat(m).FOMplot, '--', ...
        'Color', mat(m).color, 'LineWidth', lwCurve);
end
ylabel(ax,fomLabel,'Interpreter','latex','FontSize',fontAxisLatex, ...
    'FontName','Times New Roman','Color',axColor);
ylim(ax,fomYlim);
set(ax,'YTick',10.^(log10(fomYlim(1)):log10(fomYlim(2))));

xlabel(ax,'Blocking voltage (V)','FontSize',fontAxis,'FontName','Times New Roman');

% Two small legends, one per curve family, each placed where that
% family leaves the most empty room -- Ron,sp curves are lowest at low
% V (top-left is clear), FOM curves are lowest at high V (top-right is
% clear) -- so nothing overlaps, and the figure stays low-profile since
% no external legend column is needed. MATLAB only supports one legend
% per axes, so the second legend lives on a transparent overlay axes
% (dummy lines, same colors/styles, just for the legend entries).
leftLabels  = arrayfun(@(m) [m.name ' $R_{\mathrm{on,sp}}$'], mat, 'UniformOutput', false);
rightLabels = arrayfun(@(m) [m.name ' FOM'], mat, 'UniformOutput', false);

% Wider icon lines than MATLAB's default (30 pt) so a dashed entry
% actually shows multiple dash segments instead of reading as solid.
itemTok = [16*figScale 18];

yyaxis(ax,'left');
lgLeft = legend(ax, hLeft, leftLabels, 'Interpreter','latex', ...
    'FontSize',fontLeg, 'FontName','Times New Roman', ...
    'Location','northwest', 'Box','on', 'Color','white', ...
    'EdgeColor',[0.5 0.5 0.5]);
lgLeft.ItemTokenSize = itemTok;
drawnow;   % make sure ax.Position is final before copying it below

ax2 = axes('Position',ax.Position,'Color','none','XLim',[0 1],'YLim',[0 1], ...
    'XTick',[],'YTick',[],'Box','off','HitTest','off');
hold(ax2,'on');
hDummy = gobjects(1,nMat);
for m = 1:nMat
    % Thinner than the actual data lines purely for the legend icon --
    % a thick dashed line at this scale reads as solid.
    hDummy(m) = plot(ax2, NaN, NaN, '--', 'Color', mat(m).color, 'LineWidth', lwCurve*0.6);
end
lgRight = legend(ax2, hDummy, rightLabels, 'Interpreter','latex', ...
    'FontSize',fontLeg, 'FontName','Times New Roman', ...
    'Location','northeast', 'Box','on', 'Color','white', ...
    'EdgeColor',[0.5 0.5 0.5]);
lgRight.ItemTokenSize = itemTok;

%% ===================== Export ============================================
outFile = fullfile(fileparts(mfilename('fullpath')), ...
    'fig_intro_ronsp_trend.pdf');
exportgraphics(fig, outFile, 'ContentType', 'vector', ...
    'BackgroundColor','white');
fprintf('Saved %s\n', outFile);

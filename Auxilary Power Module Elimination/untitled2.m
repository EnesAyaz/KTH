clear; clc; close all;

% ----------------------------
% 1) Define grids (inputs)
% ----------------------------
ma_v   = linspace(0,1,81);        % modulation index m_a
phif_v = linspace(0,180,91);      % fundamental phase shift [deg]
phic_v = linspace(0,360,361);     % carrier phase shift phi_CPS [deg] (dense)

% For slice()/interp3(): use meshgrid in X,Y,Z order
% X = phif, Y = phic, Z = ma
[PHIF, PHIC, MA] = meshgrid(phif_v, phic_v, ma_v);

% ----------------------------
% 2) Bessel-based components
% ----------------------------
arg = MA * (pi/2);        % m_a*pi/2
J0  = besselj(0, arg);
J2  = besselj(2, arg);

% Your dependencies (as you wrote)
Vsl = (2/pi) .* J2 .* sqrt(1 - cosd(PHIC - 2*PHIF));  % sideband low
Vsw = (2/pi) .* J0 .* sqrt(1 - cosd(PHIC));           % switching
Vsh = (2/pi) .* J2 .* sqrt(1 - cosd(PHIC + 2*PHIF));  % sideband high

% Total metric
Vsum = sqrt(Vsl.^2 + Vsw.^2 + Vsh.^2);

% ----------------------------
% 3) Choose what to analyze/plot
% ----------------------------
toPlot = "Vsum";   % "Vsw", "Vsl", "Vsh", "Vsum"

switch toPlot
    case "Vsw", V = abs(Vsw);
    case "Vsl", V = abs(Vsl);
    case "Vsh", V = abs(Vsh);
    case "Vsum", V = Vsum;   % already nonnegative
    otherwise, error("Unknown toPlot.");
end

% Dimension order after meshgrid: V(phic, phif, ma)

% ----------------------------
% 4) Max & Min reachable magnitude at each (m_a, phi_f) by sweeping phi_cps
% ----------------------------
[Vmax_over_phic, idxMax] = max(V, [], 1);     % max over phic (dim 1)
[Vmin_over_phic, idxMin] = min(V, [], 1);     % min over phic (dim 1)

Vmax_over_phic = squeeze(Vmax_over_phic);     % -> size: Nphif x Nma
Vmin_over_phic = squeeze(Vmin_over_phic);     % -> size: Nphif x Nma

phiCPS_max = phic_v(squeeze(idxMax));         % argmax, size: Nphif x Nma
phiCPS_min = phic_v(squeeze(idxMin));         % argmin, size: Nphif x Nma

% ----------------------------
% 5) 3D slice plot of original V (optional)
% ----------------------------
phif_slices = [];                       % constant phi_f planes (vertical if set)
phic_slices = [];                       % constant phi_cps planes (vertical if set)
ma_slices   = [0 0.25 0.5 0.75 1];      % constant m_a planes (horizontal)

figure('Name','3D slices of V over (phi_f, phi_cps, m_a)');
slice(PHIF, PHIC, MA, V, phif_slices, phic_slices, ma_slices);
shading interp;
colormap(turbo);
cb = colorbar; cb.Label.String = "|Component amplitude| (p.u.)";
xlabel('\phi_f (deg)'); ylabel('\phi_{cps} (deg)'); zlabel('m_a');
title("Slices of " + toPlot + " (not optimized over \phi_{cps})");
grid on; box on; view(45,25);

% ----------------------------
% 6) 2D map: MAX over phi_cps
% ----------------------------
figure('Name','Vmax over phi_cps (heatmap + contours)');
imagesc(ma_v, phif_v, Vmax_over_phic); axis xy;
colormap(turbo); colorbar;
xlabel('m_a'); ylabel('\phi_f (deg)');
title("V_{max}(m_a,\phi_f) = max_{\phi_{cps}} " + toPlot);
hold on; contour(ma_v, phif_v, Vmax_over_phic, 8, 'k', 'LineWidth', 1); hold off;

% ----------------------------
% 7) 2D map: MIN over phi_cps
% ----------------------------
figure('Name','Vmin over phi_cps (heatmap + contours)');
imagesc(ma_v, phif_v, Vmin_over_phic); axis xy;
colormap(turbo); colorbar;
xlabel('m_a'); ylabel('\phi_f (deg)');
title("V_{min}(m_a,\phi_f) = min_{\phi_{cps}} " + toPlot);
hold on; contour(ma_v, phif_v, Vmin_over_phic, 8, 'k', 'LineWidth', 1); hold off;

% ----------------------------
% 8) Argmax / Argmin maps (phi_cps* that achieves max/min)
% ----------------------------
figure('Name','phi_cps* that maximizes V');
imagesc(ma_v, phif_v, phiCPS_max); axis xy;
colormap(turbo); colorbar; caxis([0 360]);
xlabel('m_a'); ylabel('\phi_f (deg)');
title("\phi_{cps}^{*max}(m_a,\phi_f) for " + toPlot);

figure('Name','phi_cps* that minimizes V');
imagesc(ma_v, phif_v, phiCPS_min); axis xy;
colormap(turbo); colorbar; caxis([0 360]);
xlabel('m_a'); ylabel('\phi_f (deg)');
title("\phi_{cps}^{*min}(m_a,\phi_f) for " + toPlot);

% ----------------------------
% 9) Surface plots (optional)
% ----------------------------
[MA2, PHIF2] = meshgrid(ma_v, phif_v);

figure('Name','Surface: Vmax over phi_cps');
surf(PHIF2, MA2, Vmax_over_phic, Vmax_over_phic);
shading interp; colormap(turbo); colorbar;
xlabel('\phi_f (deg)'); ylabel('m_a'); zlabel('V_{max}');
title("Surface of V_{max} over \phi_{cps} (" + toPlot + ")");
grid on; box on; view(45,25);

figure('Name','Surface: Vmin over phi_cps');
surf(PHIF2, MA2, Vmin_over_phic, Vmin_over_phic);
shading interp; colormap(turbo); colorbar;
xlabel('\phi_f (deg)'); ylabel('m_a'); zlabel('V_{min}');
title("Surface of V_{min} over \phi_{cps} (" + toPlot + ")");
grid on; box on; view(45,25);
%%

figure('Name','Envelope: Vmin and Vmax over \phi_{cps}');
hold on;

% Upper envelope (Vmax)
s1 = surf(PHIF2, MA2, Vmax_over_phic, Vmax_over_phic);
s1.EdgeColor = 'none';
s1.FaceAlpha = 1.0;

% Lower envelope (Vmin)
s2 = surf(PHIF2, MA2, Vmin_over_phic, Vmin_over_phic);
s2.EdgeColor = 'none';
s2.FaceAlpha = 1;   % transparency so both are visible

shading interp;

% Hand-tuned pastel colormap (blue → green → yellow → orange → red)
cmap = [
    0.30 0.45 0.85   % soft blue
    0.35 0.65 0.85
    0.40 0.78 0.70   % green
    0.75 0.88 0.55   % yellow-green
    0.95 0.85 0.55   % yellow
    0.95 0.70 0.45   % orange
    0.85 0.45 0.45   % soft red
];

% Smooth interpolation
cmap = interp1(linspace(0,1,size(cmap,1)), cmap, linspace(0,1,256));

colormap(cmap);
colorbar;
cb = colorbar;
cb.Label.String = 'Amplitude (p.u.)';

xlabel('\phi_f (deg)');
ylabel('m_a');
zlabel('Component amplitude');
title("Envelope of " + toPlot + " over \phi_{cps}");

grid on; box on;
view(45,25);

% legend([s1 s2], {'V_{max}','V_{min}'}, 'Location','best');
hold off;
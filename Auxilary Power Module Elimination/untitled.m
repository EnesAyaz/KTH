clear; clc;

% ----------------------------
% 1) Define grids (inputs)
% ----------------------------
ma_v   = linspace(0,1,81);        % modulation index m_a
phif_v = linspace(0,180,91);      % fundamental phase shift [deg]
phic_v = linspace(0,360,91);      % carrier phase shift (phi_CPS) [deg]

% For slice(), use meshgrid in X,Y,Z order
% X=phif, Y=phic, Z=ma
[PHIF, PHIC, MA] = meshgrid(phif_v, phic_v, ma_v);

% ----------------------------
% 2) Define how phi_CPS enters
% ----------------------------
% In your equations, phi_CPS is an input.
% If your effective CPS depends also on fundamental phase shift, you can define:
%   PHIC_eff = PHIC + k*PHIF   (example)
% For now: use PHIC directly.


% ----------------------------
% 3) Bessel-based components (like your screenshot)
% ----------------------------
arg = MA * (pi/2);        % m_a*pi/2
J0  = besselj(0, arg);
J2  = besselj(2, arg);

Vsl = (2/pi) .* J2 .* sqrt(1 - cosd(PHIC + -2*PHIF));  % sideband low
Vsw = (2/pi) .* J0 .* sqrt(1 - cosd(PHIC));        % switching
Vsh = (2/pi) .* J2 .* sqrt(1 - cosd(PHIC +2*PHIF));  % sideband high

% Optional: total metric (choose what you want to visualize)
Vsum =sqrt(Vsl.^2+Vsw.^2+Vsh.^2);


% ----------------------------
% 4) Choose what to plot
% ----------------------------
toPlot = "Vsum";   % "Vsw", "Vsl", "Vsh", "Vsum", "Vmax"

switch toPlot
    case "Vsw", V = abs(Vsw);
    case "Vsl", V = abs(Vsl);
    case "Vsh", V = abs(Vsh);
    case "Vsum", V = Vsum;
    otherwise, error("Unknown toPlot.");
end

% ----------------------------
% 5) Vertical slice plot
% ----------------------------
% Vertical planes can be:
% - constant PHIF  (fundamental phase shift)
% - constant PHIC  (carrier phase shift)

phif_slices = [];    % constant fundamental phase shift planes
phic_slices = [];             % e.g., [0 60 120 180]
ma_slices   = [0 0.25 0.5 0.75 1];             % keep empty => vertical only

figure;
slice(PHIF, PHIC, MA, V, phif_slices, phic_slices, ma_slices);
shading interp;

colormap(turbo);       % palette like your figure
cb = colorbar;
cb.Label.String = "|Component amplitude| (p.u.)";

xlabel('\phi_f (deg)');
ylabel('\phi_{cps} (deg)');
zlabel('m_a');
title("Vertical slices of " + toPlot);
grid on; box on;
view(45,25);

% Optional: overlay contour lines on slices
% hold on;
% contourslice(PHIF,PHIC,MA,V,phif_slices,phic_slices,ma_slices,[0.05 0.1 0.2 0.3],'k');
% hold off;
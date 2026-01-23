clc; clear; close all;

%% Machine parameters
Ns    = 6;              % Number of slots
pp    = 1;              % Pole pairs
theta = linspace(0,2*pi,1000);

%% Slot positions
slot_angle = (0:Ns-1)*2*pi/Ns;

% Phase sequence: 1 2 3 1 2 3
phase_seq = [1 2 3 -1 -2 -3];

%% Time instants
wt = linspace(0, 2*pi, 6);

figure('Color','w');

for k = 1:length(wt)
    t = wt(k);

    % Balanced phase currents
    ia = cos(t);
    ib = cos(t - 2*pi/3);
    ic = cos(t - 4*pi/3);

    F = zeros(size(theta));

    % MMF synthesis
    for s = 1:Ns
        ang = slot_angle(s);

        switch phase_seq(s)
            case 1, I = ia;
            case 2, I = ib;
            case 3, I = ic;
        end

        F = F + I*cos(pp*(theta - ang));
    end

    F = F / max(abs(F));

    subplot(3,2,k)
    plot(theta*180/pi, F, 'k','LineWidth',1.6)
    hold on
    grid on

    %% Slot markers and phase labels
    for s = 1:Ns
        x = slot_angle(s)*180/pi;
        plot([x x], [-1.2 1.2], ':','Color',[0.6 0.6 0.6])
        text(x, -1.35, num2str(phase_seq(s)), ...
             'HorizontalAlignment','center', ...
             'FontSize',11,'FontWeight','bold')
    end

    xlabel('Mechanical angle (deg)')
    ylabel('Normalized MMF')
    title(['\omega t = ', num2str(t,'%.2f'), ' rad'])
    ylim([-1.5 1.2])
end

sgtitle('Rotating Air-Gap MMF with Slot Phase Labels (1–2–3–1–2–3)')

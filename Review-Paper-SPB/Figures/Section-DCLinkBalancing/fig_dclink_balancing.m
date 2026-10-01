%% Figure 12: nonlinear SPB dc-link voltage balancing
% Run this script directly; no additional toolboxes are required (R2016b+).
% Reproduces the fixed-step RK4 simulation in gen_fig_dclink_balancing.py.
% Model: Nikouie et al., IEEE TPEL, 2017, doi:10.1109/TPEL.2016.2553129.
% DeltaP_k = Kp*(V_k-mean(V)) assumes ideal power-command tracking.
% It is motivated by controller alternative I, not a reproduction of its
% complete current-control implementation. These are simulated results.
% Exports editable FIG, vector PDF and PNG alongside this script.
% The manuscript's existing PDF in the parent Figures folder is not replaced.

p.N = 3;
p.Lb = 8e-6;       % Shared source-to-stack inductance (H)
p.Rb = 0.35;       % Shared source-to-stack resistance (ohm)
p.C = 100e-6;      % Capacitance per cell (F)
p.Vbase = 100;     % Normalization voltage (V), not loaded equilibrium voltage
p.Eb = 300;        % DC-source voltage (V)
p.Pcell = 1000;    % Nominal power per cell (W)
p.Kp = 30;        % Differential power gain (W/V)
p.Vinitial = [108; 95; 102];
p.Iinitial = 10;   % Shared initial source current (A)
p.tEnd = 3e-3;
p.nPoints = 6000;
p.Vstop = 1;       % Stop near constant-power model singularity (V)

[t, Vopen, Iopen] = simulateSPB(p, false);
[~, Vclosed, Iclosed] = simulateSPB(p, true);
eOpen = (Vopen - mean(Vopen, 2))/p.Vbase;
eClosed = (Vclosed - mean(Vclosed, 2))/p.Vbase;

fig = figure('Visible','off','Color','w','Units','inches','Position',[1 1 3.5 2.35], ...
    'Name','Figure 12 - SPB voltage balancing','NumberTitle','off', ...
    'Renderer','painters');
colors = [31 78 153; 178 58 51; 35 118 74]/255;
styles = {'-','--','-.'};
ax = gobjects(1,2);
lineHandles = gobjects(1,p.N);
positions = {[0.18 0.30 0.38 0.50], [0.61 0.30 0.38 0.50]};
for panel = 1:2
    ax(panel) = axes(fig,'Position',positions{panel});
    hold(ax(panel),'on');
    if panel == 1
        values = eOpen;
    else
        values = eClosed;
    end
    for k = 1:p.N
        h = plot(ax(panel),t*1e3,values(:,k),'Color',colors(k,:), ...
            'LineStyle',styles{k},'LineWidth',1.05, ...
            'DisplayName',sprintf('Cell %d',k));
        if panel == 1, lineHandles(k) = h; end
    end
    yline(ax(panel),0,'Color',[0.5 0.5 0.5],'LineWidth',0.5, ...
        'HandleVisibility','off');
    set(ax(panel),'FontName','Times New Roman','FontSize',8, ...
        'LineWidth',0.7,'TickDir','in','Box','off', ...
        'XLim',[0 3],'XTick',0:3,'YLim',[-1.05 0.7], ...
        'YTick',[-1 -0.5 0 0.5],'GridAlpha',0.18);
    grid(ax(panel),'on');
    xlabel(ax(panel),'$t$ (ms)','Interpreter','latex','FontSize',8);
end
linkaxes(ax,'xy');
ax(2).YTickLabel = [];
ylabel(ax(1),'$\widetilde{V}_k/V_{\mathrm{base}}$ (p.u.)', ...
    'Interpreter','latex','FontSize',8);
title(ax(1),'(a) Without balancing','FontWeight','normal','FontSize',7.2);
title(ax(2),{'(b) With proportional','power balancing'}, ...
    'FontWeight','normal','FontSize',7.2);
lgd = legend(ax(1),lineHandles,'Orientation','horizontal','Box','off', ...
    'FontName','Times New Roman','FontSize',7,'AutoUpdate','off');
lgd.Units = 'normalized';
lgd.Position = [0.25 0.045 0.70 0.07];
% Legends can adjust their parent axes; restore the intended geometry.
ax(1).Position = positions{1};
ax(2).Position = positions{2};
drawnow;

outputDir = fileparts(mfilename('fullpath'));
outputBase = fullfile(outputDir,'fig_dclink_balancing');
set(fig,'PaperUnits','inches','PaperPosition',[0 0 3.5 2.35], ...
    'PaperSize',[3.5 2.35],'PaperPositionMode','manual');
savefig(fig,[outputBase '.fig']);
print(fig,[outputBase '.pdf'],'-dpdf','-painters');
print(fig,[outputBase '_preview.png'],'-dpng','-r300');

finalSpread = max(Vclosed(end,:))-min(Vclosed(end,:));
assert(finalSpread < 0.1,'Closed-loop imbalance did not settle as expected.');
assert(abs(sum(p.Kp*(Vclosed(end,:)-mean(Vclosed(end,:))))) < 1e-8, ...
    'Differential power correction must sum to zero.');
if usejava('desktop'), set(fig,'Visible','on'); end
fprintf('Final cell voltages: %.8f, %.8f, %.8f V\n',Vclosed(end,:));
fprintf('Final voltage spread: %.8f V\n',finalSpread);
fprintf('Saved figure files in: %s\n',outputDir);

function [t,V,I] = simulateSPB(p, balancingOn)
% Match the Python model, step size, initial state and stop condition.
    t = linspace(0,p.tEnd,p.nPoints).';
    dt = t(2)-t(1);
    states = nan(p.nPoints,p.N+1);
    states(1,:) = [p.Iinitial; p.Vinitial].';
    for n = 1:p.nPoints-1
        x = states(n,:).';
        k1 = spbRHS(x,p,balancingOn);
        k2 = spbRHS(x+dt*k1/2,p,balancingOn);
        k3 = spbRHS(x+dt*k2/2,p,balancingOn);
        k4 = spbRHS(x+dt*k3,p,balancingOn);
        xNext = x+dt*(k1+2*k2+2*k3+k4)/6;
        states(n+1,:) = xNext.';
        if any(xNext(2:end)<=p.Vstop) || any(xNext(2:end)>5*p.Vbase)
            break;
        end
    end
    I = states(:,1);
    V = states(:,2:end);
end

function dx = spbRHS(x,p,balancingOn)
    I = x(1);
    V = x(2:end);
    deltaP = zeros(p.N,1);
    if balancingOn
        deltaP = p.Kp*(V-mean(V));
    end
    dI = (p.Eb-p.Rb*I-sum(V))/p.Lb;
    dV = (I-(p.Pcell+deltaP)./V)/p.C;
    dx = [dI; dV];
end
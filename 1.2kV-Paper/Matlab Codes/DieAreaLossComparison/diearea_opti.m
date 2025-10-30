r = 0.5/2*(3/2);

NumberofDie = 0.1:0.01:4;   % avoid division by zero
rds = r ./ NumberofDie;
Psw = (NumberofDie)/4*(3/2);
Pover = ones(size(NumberofDie))/4;

X1 = NumberofDie;

% === Figure setup ===
figure('Color','w','Position',[160 90 940 480]);
axes1 = axes('FontName','Times New Roman','FontSize',16,'LineWidth',1.2);
hold(axes1,'on'); grid on; box on;

% === Muted (dull) color palette ===
c1 = [0.36 0.54 0.75];   % muted blue
c3 = [0.75 0.35 0.35];   % muted red
c2 = [0.45 0.65 0.45];   % muted green
c4 = [0.1 0.1 0.1];      % black (total)

% === Plot curves ===
p1 = plot(X1, rds, '--',  'Color', c1, 'LineWidth', 2.3, 'DisplayName', 'Conduction losses');
% p2 = plot(X1, Psw, '-.',  'Color', c2, 'LineWidth', 2.3, 'DisplayName', 'Zero-current switching losses');
p3 = plot(X1, Pover+Psw, '--', 'Color', c3, 'LineWidth', 2.3, 'DisplayName', 'Overlapping losses');
p4 = plot(X1, Psw + rds + Pover, '-', 'Color', c4, 'LineWidth', 2.6, 'DisplayName', 'Total losses');

% === Labels ===
xlabel({'$A_{\mathrm{die}} / A_{\mathrm{die,opt}}$ (p.u.)'}, ...
    'Interpreter','latex','FontSize',25);
ylabel({'$P_{\mathrm{semi}} / P_{\mathrm{semi,opt}}$ (p.u.)'}, ...
    'Interpreter','latex','FontSize',25);

set(p1,'DisplayName','Conduction Losses');
% set(p2,'DisplayName','Switching loss (zero-current)');
set(p3,'DisplayName','Switching Losses');
set(p4,'DisplayName','Total Losses');



% === Axes setup ===
xlim([0 4]);
ylim([0 3]);
xticks(0:1:4);
yticks(0:0.5:3);
set(gca,'GridAlpha',0.25,'MinorGridAlpha',0.1,'TickDir','out');

% === Legend in boxed style ===
legend('show','Location','northwest','FontSize',20, ...
    'Box','on','EdgeColor',[0.7 0.7 0.7],'Color','w');

% === Annotation ===
annotation('arrow',[0.43 0.33],[0.52 0.42],'LineWidth',1.2,'Color',[0.3 0.3 0.3]);
annotation('textbox',[0.29 0.52 0.30 0.06], ...
    'String',{'Optimized point'}, ...
    'FontSize',20, 'FontName','Times New Roman', ...
    'FitBoxToText','off', 'EdgeColor','none', 'Color',[0.2 0.2 0.2]);

% === Export ===
set(gcf,'PaperPositionMode','auto');

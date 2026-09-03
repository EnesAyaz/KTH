%% ===================== Die-area (normalized) vs Loss (normalized) =====================
r = 0.5/2*(3/2);

NumberofDie = 0.1:0.01:4;                  % avoid division by zero
rds   = r ./ NumberofDie;                  % conduction ~ 1/Adie
Psw   = (NumberofDie)/4*(3/2);             % exemplar scaling ~ Adie
Pover = ones(size(NumberofDie))/4;         % constant overlap term (pu)

X1 = NumberofDie;                          % = Adie / Adie,opt (pu)

% ---- Dull blue palette (consistent with other figs) ----
cCond  = [60  85 140]/255;  % conduction – dark blue
cSw    = [90 120 170]/255;  % switching – mid blue
cTotal = [40  60  90]/255;  % total – darkest blue/gray
cOpt   = [200 220 255]/255; % very light blue (optimum fill)

% ---- Figure/Axes ----
f = figure('Color','w','Position',[160 90 940 480],'Renderer','painters');
ax = axes('Parent',f,'FontName','Times New Roman','FontSize',20,'LineWidth',1.2);
hold(ax,'on'); grid(ax,'on'); box(ax,'on');
set(ax,'GridAlpha',0.25,'MinorGridAlpha',0.12,'TickDir','out');

% ---- Optional shaded optimum region around x=1 ----
xOpt = [0.95 1.05];
patch([xOpt(1) xOpt(2) xOpt(2) xOpt(1)], [0 0 3 3], cOpt, ...
      'FaceAlpha',0.25, 'EdgeColor','none');

% ---- Curves ----
p1 = plot(X1, rds,        '--', 'Color', cCond,  'LineWidth', 2.6, 'DisplayName','Conduction losses');
p3 = plot(X1, Pover+Psw,  ':', 'Color', cSw,    'LineWidth', 2.6, 'DisplayName','Switching losses');
p4 = plot(X1, Psw+rds+Pover, '-', 'Color', cTotal,'LineWidth', 2.8, 'DisplayName','Total losses');

% ---- Vertical line at optimum (x=1) ----
plot([1 1],[0 3],'k:','LineWidth',1.2,'Color',[0.35 0.45 0.6]);

% ---- Labels ----
xlabel('$A_{\mathrm{die}}/A_{\mathrm{die,opt}}$ (p.u.)','Interpreter','latex','FontSize',22);
ylabel('$P_{\mathrm{semi}}/P_{\mathrm{semi,opt}}$ (p.u.)','Interpreter','latex','FontSize',22);

% ---- Axes limits/ticks ----
xlim([0 4]); ylim([0 3]);
xticks(0:1:4); yticks(0:0.5:3);

% ---- Legend ----
leg = legend([p4 p1 p3],'Location','northeast'); % total first
leg.Box = 'off'; leg.FontName = 'Times New Roman'; leg.FontSize = 20;

% ---- Annotation (concise) ----
text(1.00, 2.7, 'Optimized point', 'FontName','Times New Roman', ...
     'FontSize',18, 'HorizontalAlignment','center', 'Color',[0.25 0.35 0.55]);

% ---- Export vector PDF ----
% exportgraphics(f,'DieArea_vs_Loss_BlueStyle.pdf','ContentType','vector','BackgroundColor','white');

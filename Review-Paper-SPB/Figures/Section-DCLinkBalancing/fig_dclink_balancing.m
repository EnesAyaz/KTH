%% Fig. 12: analytical illustration of differential power balancing
% Run directly; no toolboxes. Small-signal motoring model:
% C*V0*dVtilde/dt = I0*Vtilde - DeltaP, with I0>0.
% tau0=C*V0/I0, s=t/tau0, kappa=Kp/I0.
% Before s=sb: DeltaP=0. After sb: DeltaP=Kp*Vtilde.
% The illustrative gain and small initial deviations are not hardware data.
outputDir=fileparts(mfilename('fullpath'));
s=linspace(0,3.5,1401).';sb=1;kappa=3;e0=[.012,-.015,.003];
factor=exp(min(s,sb)+(1-kappa)*max(s-sb,0));
e=factor*e0;
assert(max(abs(sum(e,2)))<1e-12,'Deviation sum must remain zero.');
[~,ib]=min(abs(s-sb));
assert(max(abs(e(end,:)))<.01*max(abs(e(ib,:))));
fig=figure('Visible','off','Color','w','Units','centimeters', ...
    'Position',[2 2 8.8 5.1],'Renderer','painters');
ax=axes(fig,'Position',[.17 .32 .80 .64]);hold(ax,'on');
patch(ax,[sb 3.5 3.5 sb],[-.048 -.048 .07 .07], ...
    [ .95 .975 .96],'EdgeColor','none','HandleVisibility','off');
yline(ax,0,'Color',[.6 .6 .6],'LineWidth',.5,'HandleVisibility','off');
xline(ax,sb,':','Color',[.4 .4 .4],'LineWidth',.7,'HandleVisibility','off');
colors=[48 112 190;218 77 42;55 137 89]/255;styles={'-','--','-.'};
for k=1:3
    plot(ax,s,e(:,k),'Color',colors(k,:),'LineStyle',styles{k}, ...
        'LineWidth',1.1,'DisplayName',sprintf('Cell %d',k));
end
set(ax,'FontName','Times New Roman','FontSize',8.5,'LineWidth',.5, ...
    'Box','off','TickDir','in','XLim',[0 3.5],'YLim',[-.048 .07], ...
    'YTick',0,'XTick',[0 sb],'XTickLabel',{'0','$t_b/\tau_0$'}, ...
    'TickLabelInterpreter','latex');
text(ax,.5,.048,{'Equal cell','power'},'HorizontalAlignment','center', ...
    'VerticalAlignment','bottom','FontName','Times New Roman','FontSize',8.5);
text(ax,2.25,.048,{'Power balancing','enabled'},'HorizontalAlignment','center', ...
    'VerticalAlignment','bottom','FontName','Times New Roman','FontSize',8.5);
ylabel(ax,'$\widetilde V_k/V_0$','Interpreter','latex','FontSize',8.5);
xlabel(ax,'Normalized time $t/\tau_0$','Interpreter','latex','FontSize',8.5);
lgd=legend(ax,'Orientation','horizontal','Box','off','FontSize',8.5);
lgd.Units='normalized';lgd.Position=[.22 .01 .73 .08];
ax.Position=[.17 .32 .80 .64];
set(fig,'PaperUnits','centimeters','PaperPosition',[0 0 8.8 5.1], ...
    'PaperSize',[8.8 5.1]);
outputBase=fullfile(outputDir,'fig_dclink_balancing');
savefig(fig,[outputBase '.fig']);print(fig,[outputBase '.pdf'],'-dpdf','-painters');
print(fig,[outputBase '_preview.png'],'-dpng','-r220');
if usejava('desktop'),set(fig,'Visible','on');end

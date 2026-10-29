% Azurza Anderson et al., OJPEL 1 (2020), 322-338.
% DOI: 10.1109/OJPEL.2020.3018220. Tables I-II; Eqs. (2), (5), (9).
% Columns: kR [mOhm mm^2 / V^alphaR], alphaR,
% kC [pF/mm^2 / V^alphaC], alphaC, UB minimum, UB maximum.
clear; close all;
p=[4.8e-4 2.5 2.4e5 -1.6 100 250;7.2e-3 1.6 1.6e4 -1 900 10000;.26 1.1 2.7e3 -.7 100 650];
names={'Si','SiC','GaN'};colors=[.188 .439 .745;.855 .302 .165;.216 .537 .349];
fig=figure('Color','w','Units','centimeters','Position',[2 2 8.8 5.2]);ax=axes(fig);hold(ax,'on');
for k=1:3
 v=logspace(log10(p(k,5)),log10(p(k,6)),200);
 ron=p(k,1)*v.^p(k,2);cq=p(k,3)*v.^p(k,4);
 d=1./sqrt(ron*1e-3.*cq*1e-12)/1e3;
 yyaxis left;h(k)=plot(v,ron/100,'Color',colors(k,:),'LineWidth',1.2);hold on;
 yyaxis right;plot(v,d,'--','Color',colors(k,:),'LineWidth',1.2);hold on;
end
set(ax,'XScale','log','FontName','Times New Roman','FontSize',8.5);xlim([100 10000]);
yyaxis left;set(ax,'YScale','log');ylim([.1 1000]);ylabel('R_{on,sp} (m\Omega cm^2)');
yyaxis right;set(ax,'YScale','log');ylim([150 600]);yticks([150 200 300 400 600]);ylabel('D-FOM (\surdMHz)');
xlabel('Blocking voltage U_B (V)');grid on;
legend(h,names,'Location','southeast','Orientation','horizontal','Box','off');
title('Solid: resistance; dashed: D-FOM','FontWeight','normal','FontSize',8);
out=fullfile(fileparts(mfilename('fullpath')),'fig_intro_ronsp_trend');
exportgraphics(fig,[out '.pdf'],'ContentType','vector');

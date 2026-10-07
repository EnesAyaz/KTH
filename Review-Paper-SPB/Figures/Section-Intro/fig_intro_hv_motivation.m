% fig_intro_hv_motivation.m
%
% Conceptual radar/spider chart: qualitative system-level tradeoffs
% between a low-voltage and a high-voltage traction architecture.
% Reproduces Fig. 1 of the SPB review paper (previously drawn inline
% in TikZ in Sections/Section_I_Intro.tex).
%
% Values are illustrative/qualitative, not measured or simulated data.
%
% Run this script to regenerate fig_intro_hv_motivation.pdf in this
% same folder; the PDF is what main.tex embeds via \includegraphics.

clear; close all; clc;

% ---------------------------------------------------------------------
% Data (fraction of full axis radius, one value per axis, 0..1)
% ---------------------------------------------------------------------
categories = { ...
    sprintf('Motor Power\nDensity'), ...
    sprintf('Faster\nCharging'), ...
    sprintf('BMS\nSimplicity'), ...
    sprintf('Lower\nSwitching\nLosses'), ...
    sprintf('Lower\nConduction\nLosses'), ...
    sprintf('Lighter\nCables'), ...
    sprintf('Lower\nEMI'), ...
    sprintf('Lower\nInsulation\nStress'), ...
    sprintf('Lower\nSemiconductor\nVoltage'), ...
    sprintf('Lower\nCapacitor\nVolume')};

highV = [0.90 0.85 0.35 0.45 0.60 0.95 0.45 0.25 0.20 0.80];  % High Voltage System
lowV  = [0.45 0.40 0.85 0.80 0.35 0.30 0.75 0.80 0.65 0.35];  % Low Voltage System

nAx = numel(categories);
R = 1;                                  % outer axis radius
ringFrac = [0.2 0.4 0.6 0.8 1.0];       % grid ring radii (fraction of R)
labelR = 1.32*R;                        % label placement radius

% Axis i (1-indexed) sits at angle 90 - (i-1)*36 degrees, matching the
% original TikZ layout (i=0..9 there).
ang = deg2rad(90 - (0:nAx-1)*36);


%% Publication-size plot: original conceptual scores, restyled only.
addpath(fullfile(fileparts(mfilename('fullpath')),'..','Style'));
st=pes_style();
fig=figure('Visible','off','Color','w','Units','centimeters', ...
 'Position',[2 2 8.8 7.0],'Renderer','painters');
ax=axes(fig,'Position',[0.02 0.02 0.96 0.96]);hold(ax,'on');axis(ax,'equal');axis(ax,'off');
for r=ringFrac
 plot(ax,r*cos([ang ang(1)]),r*sin([ang ang(1)]),'Color',[.75 .75 .75],'LineWidth',.4);
end
for k=1:nAx
 plot(ax,[0 cos(ang(k))],[0 sin(ang(k))],'Color',[.65 .65 .65],'LineWidth',.45);
end
fill(ax,highV.*cos(ang),highV.*sin(ang),st.blue,'FaceAlpha',.17,'EdgeColor','none');
fill(ax,lowV.*cos(ang),lowV.*sin(ang),st.red,'FaceAlpha',.13,'EdgeColor','none');
h1=plot(ax,highV([1:end 1]).*cos([ang ang(1)]),highV([1:end 1]).*sin([ang ang(1)]), ...
 '-o','Color',st.blue,'MarkerFaceColor',st.blue,'MarkerSize',3,'LineWidth',1.1);
h2=plot(ax,lowV([1:end 1]).*cos([ang ang(1)]),lowV([1:end 1]).*sin([ang ang(1)]), ...
 '--s','Color',st.red,'MarkerFaceColor','w','MarkerSize',3,'LineWidth',1.0);
for k=1:nAx
 x=1.45*cos(ang(k));y=1.45*sin(ang(k));
 ha='center';
 va='middle';
 text(ax,x,y,categories{k},'FontName',st.font,'FontSize',8.5, ...
 'HorizontalAlignment',ha,'VerticalAlignment',va);
end
xlim(ax,[-2.15 2.15]);ylim(ax,[-1.95 1.95]);
lg=legend(ax,[h1 h2],{'HV','LV'},'Orientation','horizontal','Box','off', ...
 'FontName',st.font,'FontSize',8.5,'Position',[.34 .91 .33 .05]);
out=fullfile(fileparts(mfilename('fullpath')),'fig_intro_hv_motivation');
set(fig,'PaperUnits','centimeters','PaperPosition',[0 0 8.8 7],'PaperSize',[8.8 7]);
savefig(fig,[out '.fig']);print(fig,[out '.pdf'],'-dpdf','-painters');
if usejava('desktop'),set(fig,'Visible','on');end

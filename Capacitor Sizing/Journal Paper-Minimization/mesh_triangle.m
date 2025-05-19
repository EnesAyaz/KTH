mf=20;
wt_x=linspace(0,2*pi,mf);
pf=0.9;
theta=acos(pf);
% ma=0.6;
% theta_x=linspace(0,pi/2,15);
ma_x=linspace(1/10,1,11);

Trinagle_all=[];
for wt=wt_x
Trinagle_x=[];
for ma=ma_x

Isw_A= abs(cos(wt-theta).*sin(pi*(ma*cos(wt)+1)/2));
Isw_B= abs(cos(wt-2*pi/3-theta).*sin(pi*(ma*cos(wt-2*pi/3)+1)/2));
Isw_C= abs(cos(wt+2*pi/3-theta).*sin(pi*(ma*cos(wt+2*pi/3)+1)/2));

if abs(Isw_A+Isw_B)>Isw_C && abs(Isw_A-Isw_B)<Isw_C 
Trinagle_x=[Trinagle_x, 1];
else
Trinagle_x=[Trinagle_x, 0];
end
end
Trinagle_all=[Trinagle_all; Trinagle_x];
end

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create mesh
[X,Y]=meshgrid(ma_x, mf*wt_x/2/pi);

mesh1 = surf(Y,X,Trinagle_all,'Parent',axes1,'Parent',axes1,'FaceLighting','none',...
    'EdgeLighting','flat',...
    'EdgeColor',[0 0 1]);
colormap summer

xlim([0, mf])
ylim([0, 1])

view(axes1,[0 90]);
grid(axes1,'on');
hold(axes1,'off');

% Create ylabel
ylabel({'Modulation index'},'FontName','Times New Roman');

% Create xlabel
xlab=strcat('a fundamental period (at m_f=',num2str(mf),')')
xlabel({'Switching intervals along with',xlab},...
    'FontName','Times New Roman');

% Create title
tit=strcat('Power Factor = ',' ',num2str(pf))
title({tit},'FontSize',15);

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 mf]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[1/10 1]);
grid(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XTick',0:1:mf,'YTick',ma_x);




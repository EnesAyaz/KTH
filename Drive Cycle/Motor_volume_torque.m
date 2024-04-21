
n_syn_rpm=1000:2000:11000;

P=300e3; % motor output power
pf=0.9;

S=P/pf/1e3; % motor kVA

kw1=0.956;
A=60;
B=1.05;

C=(pi^2/2)*kw1*A*B;  % kW s/m3

n_syn= n_syn_rpm/60; % 1/Hz

Volume= S./C./n_syn;

Volume_liter= Volume*1000;

k= [1.43 1.54 1.66 1.78 1.88 2]
% k=2
power_density= S./(Volume_liter.*k.^2);
%%
% plot(n_syn_rpm,power_density)
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(n_syn_rpm,power_density,'LineStyle','-','LineWidth',1,'Color',[1 0 0]);
hold on
% Create ylabel
ylabel('Power Density (kVA/L) ','FontName','Times New Roman');
% Create xlabel
xlabel('Speed (RPM)','FontName','Times New Roman');
% Create title
% % title('Drive Cycle from Scania');
box(axes1,'on');
hold(axes1,'off');
% ylim([-400 400])
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0,...
    'GridColor',[0.0745098039215686 0.623529411764706 1],'GridLineWidth',1,...
    'MinorGridAlpha',0,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineStyle','--','XGrid',...
    'on','XMinorGrid','on','YGrid','on','YMinorGrid','on','ZMinorGrid','on');

annotation(figure1,'textbox',...
    [0.149214285714285 0.735714285714289 0.463285714285715 0.133333333333333],...
    'String',{strcat('Winding factor =', '  ', string(kw1)),strcat('Magnetic loading =', '  ', string(B), '  ', ' T'), strcat('Current loading =', '  ', string(A), '  ', ' kA/m')},...
    'FontSize',15,...
    'FontName','Times New Roman',...
    'FitBoxToText','off',...
    'EdgeColor','none');



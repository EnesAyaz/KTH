%% Single Stage 

d=[];
for U1=1:-0.1:0.3

Tin=2500*1e3; %N.mm

Kf=6.20; %  N/mm2 for helical gear
Phi1=1.5; % aspect ratio


d1=(( 2*Tin*(U1+1)*1e3)/(Kf*U1^2*Phi1))^(1/3)

d1/1e3
d1/1e3/Phi1

d=[d d1/1e3]

end


%%
U1=1:-0.1:0.3
plot(1./U1,d)

% plot(n_syn_rpm,power_density)
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(1./U1,d.^2/Phi1,'LineStyle','-','LineWidth',1,'Color',[1 0 0]);
hold on
% Create ylabel
% ylabel('Diameter (m) ','FontName','Times New Roman');
ylabel('Volume (m^2) ','FontName','Times New Roman');
% Create xlabel
xlabel('Gear ratio','FontName','Times New Roman');
% Create title
% title('Drive Cycle from Scania');
box(axes1,'on');
hold(axes1,'off');
% ylim([-400 400])
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0,...
    'GridColor',[0.0745098039215686 0.623529411764706 1],'GridLineWidth',1,...
    'MinorGridAlpha',0,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineStyle','--','XGrid',...
    'on','XMinorGrid','on','YGrid','on','YMinorGrid','on','ZMinorGrid','on');
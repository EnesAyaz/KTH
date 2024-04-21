load(['C:\Users\enesa\OneDrive - KTH\Hemizero\DriveCycle\OneDrive_2023-11-29\Scania -' ...
    ' Long Haulage Truck Specs\Long_Haulage_Highway_and_Suburban_40_ton.mat'])
%%
rad_wheels=0.52 ;                                  %Radius of wheels in m

w_wheel= (Actual_speed/3.6)/rad_wheels;

T_wheel= Wheel_power./w_wheel;

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
hold on
scatter(30*w_wheel/pi, T_wheel/1e3,'Marker','*','MarkerFaceColor',[1 0 0],'MarkerEdgeColor',[1 0 0]);
hold on
% Create ylabel
ylabel('Torque(kN.m)','FontName','Times New Roman');
% Create xlabel
xlabel('N(RPM)','FontName','Times New Roman');
% Create title
title('Vehicle Operating Points (Wheel)');
box(axes1,'on');
hold(axes1,'off');

set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'GridColor',[0 0 0],'GridLineWidth',1,'GridLineStyle','--',...
    'MinorGridAlpha',0,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineStyle','--','XGrid',...
    'on','XMinorGrid','on','YGrid','on','YMinorGrid','on','ZMinorGrid','on');
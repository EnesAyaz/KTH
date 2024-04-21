%% Given constants
rad_wheels=0.52 ;                                  %Radius of wheels in m
vehicle_frontal_area= 10.5;                  %Vehicle front area in m^2
aero_drag_coef=0.7;                              %Aerodynamic drag coefficinent 
rolling_coef= 0.01;                                  % Rolling coefficient
vehicle_mass=40e3;                               %total mass with load in kg
mass_inc=1.05;                                        %mass increase due to rotation of wheel  
friction_coeff = 0.8;                                %Coefficient of friction 

density_air=1.225;                                 %kg/m^3
g=9.81;                                                     %gravity in m/s^2

alfa=0;
alfa=alfa*pi/180;

%% Drive cycle 
load(['C:\Users\enesa\OneDrive - KTH\Hemizero\DriveCycle\OneDrive_2023-11-29\Scania -' ...
    ' Long Haulage Truck Specs\Long_Haulage_Highway_and_Suburban_40_ton.mat'])
%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(Time,Actual_speed/3.6,'LineWidth',1,'Color',[1 0 0]);
% Create ylabel
ylabel('Speed(m/s) ','FontName','Times New Roman');
% Create xlabel
xlabel('Time(sec)','FontName','Times New Roman');
% Create title
title('Drive Cycle from Scania');
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',1,...
    'GridColor',[0.0745098039215686 0.623529411764706 1],'GridLineWidth',1,...
    'MinorGridAlpha',0,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineStyle','--','XGrid',...
    'on','XMinorGrid','on','YGrid','on','YMinorGrid','on','ZMinorGrid','on');


time_drive_cycle=Time;  % in s
speed_drive_cyle= Actual_speed/3.6; % in m/s


  %%  Drive Cycle Implementation
    v_ref=speed_drive_cyle; %reference speed is determined by the drive cycle speed at the given time
    v_car=zeros(length(speed_drive_cyle),1); % car speed is initally 0 for all time steps and will be determined
    pow_spent=zeros(length(speed_drive_cyle),1); % stores the power output (positive if m/c acts as a motor negative if regenerative braking)
    time_step= time_drive_cycle(2,1)-time_drive_cycle(1,1); % time step for accelaration

    %Car enters  drive cycle iterations
    for t=2:1:length(speed_drive_cyle) %loops around the time

        if((v_ref(t,1)-v_ref(t-1,1))>=0) %standstill or acceleration 

        acc=(v_ref(t,1)-v_ref(t-1,1))/time_step;  %desired acceleration

        Frr=  rolling_coef*vehicle_mass*g*cos(alfa) ;
        Fad= (1/2) *aero_drag_coef*density_air*vehicle_frontal_area*v_ref(t-1,1)^2;
        Fg=  vehicle_mass*g*sin(alfa);
        Fa= acc*(vehicle_mass*mass_inc);

        F_trac= Frr+Fad+Fg+Fa;
        T_trac= F_trac*rad_wheels;

        pow_spent(t,1)=v_ref(t-1,1)*F_trac;

        end

         if((v_ref(t,1)-v_ref(t-1,1))<0)  %deacceleration 

        acc=(v_ref(t,1)-v_ref(t-1,1))/time_step;  %desired acceleration

        Frr=  rolling_coef*vehicle_mass*g*cos(alfa) ;
        Fad= (1/2) *aero_drag_coef*density_air*vehicle_frontal_area*v_ref(t-1,1)^2;
        Fg=  vehicle_mass*g*sin(alfa);
        Fa= acc*(vehicle_mass*mass_inc);

        F_trac= Frr+Fad+Fg+Fa;
        T_trac= F_trac*rad_wheels;

        pow_spent(t,1)=v_ref(t-1,1)*F_trac;

        end

        end
%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
plot(time_drive_cycle(1:end), pow_spent/1e3,'LineStyle','-','LineWidth',1,'Color',[1 0 0]);
hold on
% Create ylabel
ylabel('Power (kW) ','FontName','Times New Roman');
% Create xlabel
xlabel('Time(sec)','FontName','Times New Roman');
% Create title
title('Drive Cycle from Scania');
box(axes1,'on');
hold(axes1,'off');
% ylim([-400 400])
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0,...
    'GridColor',[0.0745098039215686 0.623529411764706 1],'GridLineWidth',1,...
    'MinorGridAlpha',0,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineStyle','--','XGrid',...
    'on','XMinorGrid','on','YGrid','on','YMinorGrid','on','ZMinorGrid','on');

%%
%%

T_operating=zeros(length(speed_drive_cyle),1);

for(ii=1:1:length(speed_drive_cyle))
    
T_operating(ii,1)=pow_spent(ii,1)/((v_ref(ii,1)/rad_wheels));    
    
end

%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
hold on
scatter((30*v_ref/rad_wheels/pi), T_operating/1e3,'Marker','*','MarkerFaceColor',[1 0 0],'MarkerEdgeColor',[1 0 0]);
hold on
% Create ylabel
ylabel('Torque(kNm)','FontName','Times New Roman');
% Create xlabel
xlabel('Speed (RPM)','FontName','Times New Roman');
% Create title
% title('Vehicle Operating Points (Wheel)');
ylim([0 ])
box(axes1,'on');
hold(axes1,'off');
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'GridColor',[0 0 0],'GridLineWidth',1,'GridLineStyle','--',...
    'MinorGridAlpha',0,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineStyle','--','XGrid',...
    'on','XMinorGrid','on','YGrid','on','YMinorGrid','on','ZMinorGrid','on');

%%

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create plot
hold on
scatter(v_ref*3.6,pow_spent/1e3,'Marker','*','MarkerFaceColor',[1 0 0],'MarkerEdgeColor',[1 0 0]);
hold on
% Create ylabel
ylabel('Power(kW)','FontName','Times New Roman');
% Create xlabel
xlabel('V(km/h)','FontName','Times New Roman');
% Create title
title('Vehicle Operating Points (Wheel)');
box(axes1,'on');
hold(axes1,'off');

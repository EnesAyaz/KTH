Iph_rms=250;

P_on_y=[];
Psw_zcs_y=[];
Psw_dvdt_y= [];

Fsw_a=10e3:5e2:40e3;

A_die_a=30:10:1000;

for fsw=Fsw_a

k_r=7.2*10e-3;
alpha_r= 1.6;

P_on_x=[];
Psw_zcs_x=[];
Psw_dvdt_x= [];


for A_die=A_die_a

U_b=1.7; % kV 

r_on=k_r * U_b^(alpha_r)./A_die;
P_on= Iph_rms^2*r_on;

Udc=1250; 
Ub=U_b*1e3;
k_c=1.6e4;
alpha_c=-1;

C_oss= k_c*(Ub^alpha_c)*A_die*1e-12;

Esw=C_oss*Udc^2;

Psw_zcs= Esw*fsw;



dv_dt=15e3/1e-6; % V/s
di_dt=20e3/1e-6; % V/s

theta=0:1e-3:2*pi;
Iph=Iph_rms*sqrt(2)*sin(theta);
Iph=abs(Iph);
Psw_over= ((Udc*Iph.^2/di_dt)+(Udc^2.*Iph/dv_dt));
Psw_dvdt= fsw*trapz(theta,Psw_over)/2/pi;


P_on_x=[P_on_x P_on];
Psw_zcs_x=[Psw_zcs_x Psw_zcs];
Psw_dvdt_x= [Psw_dvdt_x Psw_dvdt];

end 

P_on_y=[P_on_y ; P_on_x];
Psw_zcs_y=[Psw_zcs_y ; Psw_zcs_x];
Psw_dvdt_y= [Psw_dvdt_y; Psw_dvdt_x];

end

P_tot= P_on_y+Psw_zcs_y+Psw_dvdt_y;


[X,Y] = meshgrid(A_die_a,Fsw_a/1e3);

figure1 = figure('GraphicsSmoothing','off');
colormap(hsv);

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create contour
hLines = 500; 
 % [~,h] = contour(X,Y,3*P_on_y,hLines,'Fill','on');
  % [~,h] = contour(X,Y,3*Psw_zcs_y,hLines,'Fill','on');
    % [~,h] = contour(X,Y,3*Psw_dvdt_y,hLines,'Fill','on');
   [~,h] = contour(X,Y,3*P_tot,hLines,'Fill','on');

% Create ylabel
ylabel('Frequency (kHz)','FontSize',15);

% Create xlabel
xlabel('Die area (mm^2)','FontSize',15);

% Create title
 % title(' Total Loss (W)','FontSize',20,'FontWeight','bold','Interpreter','none');


box(axes1,'on');
axis(axes1,'tight');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'BoxStyle','full','FontName','Times New Roman','FontSize',15,...
    'Layer','top');
% Create colorbar
colorbar(axes1,'FontSize',15,'FontName','Times New Roman');
caxis([1000 6000]);

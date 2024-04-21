theta= linspace(0,2*pi,1000);
I_peak= 356;
theta_pf= acos(0.9);
IL= I_peak*sin(theta-theta_pf);
IL2= I_peak*sin(theta);
% plot(theta,IL,theta,IL2)
m_a=1;

P_on_y=[];

Fsw_a=10e3:5e2:40e3;
A_die_a=30:10:1000;

for fsw=Fsw_a

P_on_x=[];

for A_die=A_die_a


k_r=7.2*10e-3;
alpha_r= 1.6;
U_b=1.7; % kV 
r_on=k_r * U_b^(alpha_r)./A_die;

P_c= 0;
sample_theta=1e-2;

for theta=theta_pf:sample_theta:theta_pf+pi

    IL= I_peak*sin(theta-theta_pf);
    D_upper= (1+m_a*sin(theta))/2;
    D_lower= (1-m_a*sin(theta))/2;
    P_c= P_c+ (r_on*IL^2*D_upper*sample_theta)+  (r_on*IL^2*D_lower*sample_theta);

end

P_on_x=[P_on_x P_c/2/pi];

end 

P_on_y=[P_on_y ; P_on_x];
end


P_tot= 3*P_on_y;


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
   [~,h] = contour(X,Y,P_tot,hLines,'Fill','on');

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
caxis([0 2000]);





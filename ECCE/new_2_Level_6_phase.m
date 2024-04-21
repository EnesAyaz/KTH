
I_peak= 356/2;
theta_pf= acos(0.9);
m_a=1;


P_on_y=[];
P_zcs_y=[];
P_over_y=[];

ffund=500;

Fsw_a=10e3:1e2:30e3;
A_die_a=30:5:1000;

for fsw=Fsw_a

P_on_x=[];
P_zcs_x=[];
P_over_x=[];

for A_die=A_die_a


k_r=7.2*10e-3;
alpha_r= 1.6;
U_b=1.7; % kV 
r_on=k_r * U_b^(alpha_r)./A_die;

P_c= 0;
sample_theta=1e-2;


for theta=theta_pf:sample_theta:(theta_pf+pi)
    IL= I_peak*sin(theta-theta_pf);
    D_upper= (1+m_a*sin(theta))/2;
    D_lower= (1-m_a*sin(theta))/2;
    P_c= P_c+ (r_on*IL^2*D_upper*sample_theta)+  (r_on*IL^2*D_lower*sample_theta);
end


Udc=1250; 
Ub=U_b*1e3;
k_c=1.6e4;
alpha_c=-1;
C_oss= k_c*(Ub^alpha_c)*A_die*1e-12;
Esw=C_oss*Udc^2;

E_zcs= 0;
sample_theta=1e-2;

sample_theta=ffund*2*pi/(fsw);

for theta=theta_pf:sample_theta:(theta_pf+pi)
    
    E_zcs= E_zcs+ Esw;

end

dv_dt=10e3/1e-6; % V/s
di_dt=10e3/1e-6; % V/s
E_over=0;
for theta=theta_pf:sample_theta:(theta_pf+pi)
   IL= abs(I_peak*sin(theta-theta_pf));
   E_over2= ((Udc*IL.^2/di_dt)+(Udc^2.*IL/dv_dt));
   E_over =E_over + E_over2;

end


P_on_x=[P_on_x 2*P_c/2/pi];
P_zcs_x=[P_zcs_x  ffund*2*E_zcs];
P_over_x=[P_over_x  ffund*2*E_over];

end 

P_on_y=[P_on_y ; P_on_x];
P_zcs_y=[P_zcs_y ; P_zcs_x];
P_over_y=[P_over_y ; P_over_x];

end



Pout=300e3;


P_tot= 6*(1.5*P_on_y+P_zcs_y+P_over_y);
% P_tot= 3*(P_over_y);
% P_tot= 3*(P_zcs_y);

[X,Y] = meshgrid(A_die_a,Fsw_a/1e3);

figure1 = figure('GraphicsSmoothing','off');
colormap("colorcube");
% colormap("sky");

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create contour
hLines = 500; 
 % [~,h] = contour(X,Y,3*P_on_y,hLines,'Fill','on');
  % [~,h] = contour(X,Y,3*Psw_zcs_y,hLines,'Fill','on');
    % [~,h] = contour(X,Y,3*Psw_dvdt_y,hLines,'Fill','on');
   [~,h] = contour(X,Y,100*Pout./(Pout+P_tot),hLines,'Fill','on');
      % [~,h] = contour(X,Y,P_tot,hLines,'Fill','on');



% for targetEfficiency = 99.4:0.01:99.8
% Specify the desired efficiency value
% Plot a specific contour line for the desired efficiency value
% contour(X, Y, 100 * Pout ./ (Pout + P_tot), [targetEfficiency, targetEfficiency], 'LineColor', 'k', 'LineWidth', 1);
% end

% Create ylabel
ylabel(' Switching Frequency (kHz)','FontSize',15);

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
% caxis([97.5 99.75]);
 caxis([98.2 99.8]);

% Create textbox
annotation(figure1,'textbox',...
    [0.751785714285713 0.945238095238097 0.262500000000001 0.0619047619047691],...
    'String',{'Efficiency (%)'},...
    'FontSize',15,...
    'FontName','Times New Roman',...
    'FitBoxToText','off',...
    'EdgeColor','none');


% % Create textarrow
% annotation(figure1,'textarrow',[0.398214285714285 0.364285714285714],...
%     [0.315666666666668 0.197619047619049],'String',{'99.4 %'},'FontSize',15,...
%     'FontName','Times New Roman');


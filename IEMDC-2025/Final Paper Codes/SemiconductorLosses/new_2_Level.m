I_peak= 356;
theta_pf= acos(0.9);
m_a=1;



I_peak=600;
theta_pf= 0.9;
m_a=1;
ffund=100;



P_on_y=[];
P_zcs_y=[];
P_over_y=[];



Fsw_a=10e3:5e3:30e3;
A_die_a=20:50:320;

for fsw=Fsw_a

P_on_x=[];
P_zcs_x=[];
P_over_x=[];

for A_die=A_die_a

% k_r=7.2*10e-3;
% alpha_r= 1.6;
% U_b=1.7; % kV 
% r_on=k_r * U_b^(alpha_r)./A_die;

k_r=7.2*1e-3;
alpha_r= 1.6;
U_b=0.9; % kV 
r_on=k_r * (U_b*1000)^(alpha_r)/A_die/1000; %% I changed this formulation because it is not correct 


P_c= 0;
sample_theta=1e-2;

for theta=theta_pf:sample_theta:(theta_pf+pi)
    IL= I_peak*sin(theta-theta_pf);
    D_upper= (1+m_a*sin(theta))/2;
    D_lower= (1-m_a*sin(theta))/2;
    P_c= P_c+ (r_on*IL^2*D_upper*sample_theta)+  (r_on*IL^2*D_lower*sample_theta);
end


Udc=625; 
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

P_totx= 3*(1.5*P_on_x+P_zcs_x+P_over_x);

P_tot= 3*(1.5*P_on_y+P_zcs_y+P_over_y);




[X,Y] = meshgrid(A_die_a,Fsw_a/1e3);
figure1 = figure('GraphicsSmoothing','off');
axes1 = axes('Parent',figure1);
hold(axes1,'on');
contour(X,Y,P_tot)
% Create ylabel
ylabel('Switching Frequency (kHz)','FontSize',15);
% Create xlabel
xlabel('Die area (mm^2)','FontSize',15);





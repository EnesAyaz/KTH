close all
I_peak= sqrt(rms(id2)^2+rms(iq2)^2);
theta_pf= acos(power_factor);
m_a=ma;


ffund=fe;
% Fsw_a=34*fe*[1 1.5 2 2.5 3];

A_die_a=50:50:1000;

A_die_a=300;

fsw=20*fe*n;
fsw=34*fe*n;

P_on_x=[];
P_zcs_x=[];
P_over_x=[];

for A_die=A_die_a

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

dv_dt=15e3/1e-6; % V/s
di_dt=15e3/1e-6; % V/s

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

P_tot= 3*(1.5*P_on_x+P_zcs_x+P_over_x);

minimum = min(min(P_tot));
[x,y]=find(P_tot==minimum)



figure()
plot(A_die_a,3*P_on_x*1.5)
hold on
plot(A_die_a,3*(P_zcs_x+P_over_x))
hold on
plot(A_die_a,P_tot)
hold on


[3*P_on_x(y)*1.5 3*(P_zcs_x(y)+P_over_x(y)) P_tot(y) A_die_a(y) fsw/1e3]



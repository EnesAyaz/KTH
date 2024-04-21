I_peak= 356;
theta_pf= acos(0.9);

m_a=1;

P_on_y=[];

A_die=100;

k_r=7.2*10e-3;
alpha_r= 1.6;
U_b=1.7; % kV 
r_on=k_r * U_b^(alpha_r)/A_die

P_c= 0;

sample_theta=1e-2;
for theta=theta_pf:sample_theta:(theta_pf+pi)

    IL= I_peak*sin(theta-theta_pf);
    D_upper= (1+m_a*sin(theta))/2;
    D_lower= (1-m_a*sin(theta))/2;
    P_c= P_c+ (r_on*IL^2*D_upper*sample_theta)+  (r_on*IL^2*D_lower*sample_theta);

end

2*P_c/(2*pi)
r_on*I_peak*I_peak/2




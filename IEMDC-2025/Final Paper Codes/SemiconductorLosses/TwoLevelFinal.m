operating_point='F'

if operating_point=='A'
vd = -22.4; %  d-axis voltage value in V
vq = 8.4; %  q-axis voltage value in V
id = -565.4; %  d-axis current value in A
iq = 570.5; %  q-axis current value in A
Ld= 109e-6; % d-axis inductance value in H
Lq=109e-6; % q-axis inductance value in H
Vdc= 625; % DC link voltage in V
electrical_frequency=20; % Hz
end

if operating_point=='B'
vd = -308.8; %  d-axis voltage value in V
vq = 101.2; %  q-axis voltage value in V
id = -688.5; %  d-axis current value in A
iq = 457.4; %  q-axis current value in A
Ld= 116e-6; % d-axis inductance value in H
Lq=156e-6; % q-axis inductance value in H
Vdc= 625; % DC link voltage in V
electrical_frequency=300; % Hz
end


if operating_point=='C'
vd = -254; %  d-axis voltage value in V
vq = 202.7; %  q-axis voltage value in V
id = -253.6; %  d-axis current value in A
iq = 318.8; %  q-axis current value in A
Ld= 125e-6; % d-axis inductance value in H
Lq=209e-6; % q-axis inductance value in H
Vdc= 625; % DC link voltage in V
electrical_frequency=300; % Hz
end



if operating_point=='D'
vd = -184.4; %  d-axis voltage value in V
vq = 248.5; %  q-axis voltage value in V
id = -92.3; %  d-axis current value in A
iq = 192.7; %  q-axis current value in A
Ld= 135e-6; % d-axis inductance value in H
Lq=330e-6; % q-axis inductance value in H
Vdc= 625; % DC link voltage in V
electrical_frequency=300; % Hz
end



if operating_point=='E'
vd = -301.9; %  d-axis voltage value in V
vq = 120.1; %  q-axis voltage value in V
id = -774.2; %  d-axis current value in A
iq = 200.4; %  q-axis current value in A
Ld= 133e-6; % d-axis inductance value in H
Lq=394e-6; % q-axis inductance value in H
Vdc= 625; % DC link voltage in V
electrical_frequency=500; % Hz
end



if operating_point=='F'
vd = -211.9; %  d-axis voltage value in V
vq = 246.3; %  q-axis voltage value in V
id = -468.9; %  d-axis current value in A
iq = 118.6; %  q-axis current value in A
Ld= 145e-6; % d-axis inductance value in H
Lq=  503e-6; % q-axis inductance value in H
Vdc= 625; % DC link voltage in V
electrical_frequency=500; % Hz
end


S = vd * id + vq * iq; % Real power in dq
V_peak = sqrt(vd^2 + vq^2); % Magnitude of voltage vector
I_peak = sqrt(id^2 + iq^2); % Magnitude of current vector

theta_pf = S / (V_peak * I_peak);
m_a=V_peak/Vdc;
ffund=electrical_frequency;
I_peak
%%
Fsw_a=5e3:5e3:30e3;
A_die=500;

P_on_x=[];
P_zcs_x=[];
P_over_x=[];

for fsw=Fsw_a

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

dv_dt=20e3/1e-6; % V/s
di_dt=20e3/1e-6; % V/s

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

P_totx= 3*(P_on_x+P_zcs_x+P_over_x);


figure()

plot(Fsw_a/1e3,P_totx)

P_totx
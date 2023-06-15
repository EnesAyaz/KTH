%% Calculation Rds on based on chip area and number of Size
Vdc=1250;
Vdss=2000;

at= 258.5e-17; % ohm m^2 V^(-2.5)

bt=565.1e-9; % ohm m^2

rds_on_spes=at*Vdss^(2.5)+bt ;

A_ac_die=  50e-6;
n_die=5;

Rds_on= (1/n_die)*rds_on_spes/A_ac_die;

% Assuming the junction temperature is constant 
% n_die= 10;
% rds_on=rdson_Tj;
% A_ac_die=5e-6;
% Rds_on=0.0053;
% 
%% Fundamental frequency and creating time array
f_L=1e3;
time=linspace(0,1/f_L,1e5);
gamma=2*pi*f_L*time;
delta_gamma =gamma(5)-gamma(4);

%%  The load current and power factor
I_Lp=320;
psi=0;
i_L= I_Lp*sin(gamma-psi);

%% Modulation and duty ratios
M= 0.8; 
alpha= M*sin(gamma);
D_T1= (1+alpha)/2;
D_T2=(1-alpha)/2;

%%
Vdss_x= 1000;
Usw_x= 600; %V
I_L_x=50;  % A
Theta_j_x =25 ; % degree
A_ac_die_x= 100e-6;
 
E_turnon_x= 360e-6; %  Joule
E_turnoff_x= 116e-6; %  joulle

E_sw_ref=E_turnon_x+E_turnoff_x;

Usw=Vdc; 

f1 = (Usw/Usw_x)^ (1.5);  % upscaling with switching voltage

pI1= 225.7e-7;
pI2= 118.1e-4;
pI3= 357e-3;
% I_L=I_Lp;
% f2= pI1* I_L^2 * pI2* I_L+pI3

pv1= 197.6e-5;
pv2=909.4e-3;

Theta_j= 398.15 ;

f3= pv1*Theta_j + pv2;

f4= (Vdss/Vdss_x)^2;

%% Switching losses

gamma_3= psi;
gamma_4 =psi+pi;
P_TVSW1=[];

for i=1:length(gamma)

    if gamma(i)> gamma_3 && gamma(i) < gamma_4
   
    P_TVSW1=[P_TVSW1  E_sw_ref*f1* (pI1*(i_L(i)*A_ac_die_x/(A_ac_die*n_die))^2 * pI2*(i_L(i)*A_ac_die_x/(A_ac_die*n_die))+pI3)*f3*f4*delta_gamma];
    else 
     P_TVSW1=[P_TVSW1 0];
  
    end 

end

fs=20e3;

Pt_one_leg_fs= fs*n_die*A_ac_die/A_ac_die_x*sum(P_TVSW1)/(2*pi);
Pt_one_leg_fs

Pt_one_leg_fs*6




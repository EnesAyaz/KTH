%% Calculation Rds on based on chip area and number of Size
Vdc=1250;
Vdss=2000;

at= 258.5e-17; % ohm m^2 V^(-2.5)
bt=565.1e-9; % ohm m^2

rds_on_spes=at*Vdss^(2.5)+bt ;

A_ac_die=  50e-6;
n_die=5;

Rds_on= (1/n_die)*rds_on_spes/A_ac_die;
%% Fundamental frequency and creating time array
f_L=1e3;
time=linspace(0,1/f_L,1e5);
gamma=2*pi*f_L*time;
delta_gamma =gamma(5)-gamma(4);

%%  The load current and power factor
I_Lp=320;
psi=0;
i_L= I_Lp*sin(gamma-psi);

%% Determining conduction angles
gamma_1=psi;
gamma_2=psi+pi;

%% Modulation and duty ratios
M= 0.8; 
alpha= M*sin(gamma);
D_T1= (1+alpha)/2;
D_T2=(1-alpha)/2;

%% Conduction Loss arrays and calculating conduction currents
P_TVC1=[];
P_TVC2=[];
for i=1:length(gamma)

    if gamma(i)> gamma_1 && gamma(i) < gamma_2
    P_TVC1=[P_TVC1  i_L(i)^2*D_T1(i)*delta_gamma];
    P_TVC2=[P_TVC2  i_L(i)^2*D_T2(i)*delta_gamma];
    else 
     P_TVC1=[P_TVC1 0];
     P_TVC2=[P_TVC2 0];
    end 

end

Pt1=sum(P_TVC1)/2/pi*Rds_on; % for T1
Pt2=sum(P_TVC2)/2/pi*Rds_on;  % for T2

Pt1
Pt2

%%

Pt_one_leg_cond=(Pt1+Pt2)*2; % total loss for one leg

Pt1
Pt2

Pt_one_leg_cond*3






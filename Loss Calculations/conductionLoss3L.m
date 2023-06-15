%% Calculation Rds on based on chip area and number of Size
Vdc=1250;
Vdss=2400;

at= 258.5e-17; % ohm m^2 V^(-2.5)
bt=565.1e-9; % ohm m^2

rds_on_spes=at*(Vdss/2)^(2.5)+bt ;

A_ac_die=  50e-6;
n_die=5;

Rds_on= (1/n_die)*rds_on_spes/A_ac_die;

ad= 649.6e-17; % ohm m^2 V^(-2.5)
bd=202.2e-9; % ohm m^2
uo= 0.8127;  %V

rd_spec= ad*(Vdss/2)^(2.5)+bd ;

Rd_d= (1/n_die)*rd_spec/A_ac_die;

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
gamma_2= pi;
gamma_3=psi+pi;

%% Modulation and duty ratios
M= 0.8; 
alpha= M*sin(gamma);
D_T1= alpha;
D_T2_1=1+alpha-alpha;
D_T2_2=1-alpha;
D_T3= alpha;
D_T4=- alpha;
D_D5_1= 1-alpha;
D_D5_2= 1+alpha;

%% Conduction Loss arrays and calculating conduction currents
P_TVC1=[];
P_TVC2=[];
P_TVC3=[];
P_TVC4=[];
P_D5=[];
P_D6=[];

for i=1:length(gamma)

    if gamma(i)> gamma_1 && gamma(i) < gamma_2
    P_TVC1=[P_TVC1  Rds_on*i_L(i)^2*D_T1(i)*delta_gamma];
    P_TVC2=[P_TVC2  Rds_on*i_L(i)^2*D_T2_1(i)*delta_gamma];
    P_TVC3=[P_TVC3  0];
    P_TVC4=[P_TVC4  0];
    P_D5=[P_D5  (uo*i_L(i)+Rd_d*i_L(i)^2)*D_D5_1(i)*delta_gamma];

    elseif gamma(i)> gamma_2 && gamma(i) < gamma_3
    P_TVC1=[P_TVC1  0];
    P_TVC2=[P_TVC2  Rds_on*i_L(i)^2*D_T2_2(i)*delta_gamma];
    P_TVC3=[P_TVC3  Rds_on*i_L(i)^2*D_T3(i)*delta_gamma];
    P_TVC4=[P_TVC4  Rds_on*i_L(i)^2*D_T4(i)*delta_gamma];
    P_D5=[P_D5  (uo*i_L(i)+Rd_d*i_L(i)^2)*D_D5_2(i)*delta_gamma];

    else 
     P_TVC1=[P_TVC1 0];
     P_TVC2=[P_TVC2 0];
     P_TVC3=[P_TVC3 0];
     P_TVC4=[P_TVC4 0];
     P_D5=[P_D5 0];
 
    end 

end

Pt1=sum(P_TVC1)/2/pi; % for T1
Pt2=sum(P_TVC2)/2/pi;  % for T2
Pt3=sum(P_TVC3)/2/pi; % for T1
Pt4=sum(P_TVC4)/2/pi;  % for T2
Pd5=sum(P_D5)/2/pi; % for T1

Pt1
Pt2
Pt3
Pt4
Pd5

%%

Pt_one_leg_cond=(Pt1+Pt2+Pt4+Pd5)*2; % total loss for one leg


Pt_one_leg_cond*3






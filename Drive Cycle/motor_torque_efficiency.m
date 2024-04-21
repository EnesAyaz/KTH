P=300e3;
n_base_rpm=6000; %RPM
scale=1;
n_base_rpm=n_base_rpm*scale;
w_base= (pi/30)*n_base_rpm;
T_max= P/w_base;           % N.m

T=linspace(0,T_max,500);
n_rpm=1000:100:n_base_rpm*3;
n_rpm=n_rpm';
n_lim=n_base_rpm;

Losses=[];
Pout=[];
for i=1:length(n_rpm)


    Losses_1=[];
    Pout_1=[];

    for j=1:length(T)
    
    A=0.04*scale*scale;
    B=5*scale;
    C=1e-5/scale/scale;

    if  n_rpm(i)< n_lim
    Losses_1=[Losses_1, A*T(j)^2 + B*T(j) + C*n_rpm(i)^2 ];
    Pout_1=[Pout_1 n_rpm(i)*T(j)*(pi/30)]  ;
   
    else

   if T(j)>P/((pi/30)*n_rpm(i))    
    Losses_1=[Losses_1, 0];
    Pout_1=[Pout_1 1]  ;
   else 
    Losses_1=[Losses_1, A*T(j)^2 + B*T(j) + C*n_rpm(i)^2];
    Pout_1=[Pout_1 n_rpm(i)*T(j)*(pi/30)]  ;
    end

    end

    end
    Losses=[Losses; Losses_1];
    Pout=[Pout; Pout_1];

end

%%


%%


[X,Y] = meshgrid(T,n_rpm);

eff=Pout./(Pout+Losses);

contourf(Y,X,Losses)
colorbar

% Create ylabel
ylabel({'Torque (N.m)'});
% Create xlabel
xlabel({'Speed (RPM)'});

title('Losses (W)')


% clim([0.9 1])
% set(gca,'ColorScale','log')



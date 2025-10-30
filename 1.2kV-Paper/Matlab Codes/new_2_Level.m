I_peak= 356;
I_peak= 356*1.5;
theta_pf= acos(1);
m_a=1;


P_on_y=[];
P_zcs_y=[];
P_over_y=[];

ffund=500;

Fsw_a=5e3:1e2:30e3;
A_die_a=30:5:1000;

for fsw=Fsw_a

P_on_x=[];
P_zcs_x=[];
P_over_x=[];

for A_die=A_die_a

k_r=7.2*10e-3;
alpha_r= 1.6;
% U_b=1.7; % kV 
U_b=1.2; % kV 
r_on=k_r * U_b^(alpha_r)./A_die;

P_c= 0;
sample_theta=1e-2;

for theta=theta_pf:sample_theta:(theta_pf+pi)
    IL= I_peak*sin(theta-theta_pf);
    D_upper= (1+m_a*sin(theta))/2;
    D_lower= (1-m_a*sin(theta))/2;
    P_c= P_c+ (r_on*IL^2*D_upper*sample_theta)+  (r_on*IL^2*D_lower*sample_theta);
end


% Udc=1200; 
Udc=800; 
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


P_tot= 3*(2*P_on_y+P_zcs_y+P_over_y);
% P_tot= 3*(P_over_y);
% P_tot= 3*(P_zcs_y);

[X,Y] = meshgrid(A_die_a,Fsw_a/1e3);

% === Efficiency field ===
eta = 100 * Pout ./ (Pout + P_tot);   % (%)  size = [numel(Fsw_a) x numel(A_die_a)]

% === Figure / axes ===
figure('Color','w','Position',[220 180 780 520],'Renderer','painters'); % vector-friendly
axes1 = axes('FontName','Times New Roman','FontSize',15,'LineWidth',1.1);
hold(axes1,'on'); box on; grid off; set(axes1,'Layer','top');

% === Filled contour (no edge lines) ===
nLevels = 10;
contourf(X, Y, eta, nLevels, 'LineStyle','none');

% === Single-hue muted blue colormap (very light -> deep blue) ===
nC = 256;
stops = [ ...
    1.00 1.00 1.00  % near-white
    0.92 0.95 0.98  % very light blue
    0.75 0.84 0.93  % light muted blue
    0.56 0.70 0.86  % mid muted blue
    0.36 0.54 0.75  % deep muted blue
    0.18 0.32 0.52  % darkest
];
xi = linspace(0,1,size(stops,1));
cmap = interp1(xi, stops, linspace(0,1,nC));
colormap(cmap);

% === Optional: thin isolines at key efficiencies (and a legend box) ===
% isoVals = [99.2 99.4 99.6 99.7 99.75 99.8];
% [~, hIso] = contour(X, Y, eta, isoVals, 'LineColor',[0 0 0], 'LineWidth',0.75);
% Build a tiny legend for the isolines (white box)
% leg = legend(hIso, string(isoVals) + " %", 'Location','northwest');
% set(leg,'Box','on','EdgeColor',[0.7 0.7 0.7],'Color','w','FontSize',12);

% === Axes + labels ===
xlabel('Die area (mm^2)','FontSize',20);
ylabel('Switching frequency (kHz)','FontSize',20);
xlim([min(A_die_a) max(A_die_a)]);
ylim([min(Fsw_a)/1e3 max(Fsw_a)/1e3]);
set(gca,'TickDir','out');

% === Colorbar with proper label ===
c = colorbar('FontSize',14,'FontName','Times New Roman');
ylabel(c,'Efficiency (%)','FontSize',20);
caxis([98.2 99.8]);     % keep your range

% === Tight layout ===
axis tight

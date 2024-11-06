theta= wt; 
v_phase_A=vp*Ud/2;
ipA=ip;
back_emf_A= v_max_back_emf* cos(wt-theta_difference);
rs=resistance;

plot(theta,v_phase_A)
hold on
plot(theta,ipA)
hold on
plot(theta,back_emf_A)

t_end=theta(end)/f1/2/pi;

%%
% Inverse Park Transformation: dq to alpha-beta
% Lalpha = Ld * cos(theta) - Lq * sin(theta);
% Lbeta = Ld * sin(theta) + Lq * cos(theta);
% % Inverse Clarke Transformation: alpha-beta to abc
% L_a = Lalpha;

L_a = Ld * sin(theta-theta_difference).^2 + Lq *cos(theta-theta_difference).^2;

% L_a = Ld * ones(size(theta-theta_difference));


figure('Name','Time Domain Currents')
plot(theta,L_a)
hold on
plot(theta,back_emf_A*1e-6)
hold on
%%

i_a= zeros(size(v_phase_A));

time=wt/2/pi/f1;
sample_time=time(2)-time(1);

for t=2:length(time)

dL_dt = (L_a(t) - L_a(t-1)) / sample_time;
i_a(t) = i_a(t-1) + sample_time * ((v_phase_A(t) - rs*i_a(t-1) - dL_dt * i_a(t-1)) / L_a(t));
% i_a(t) = i_a(t-1) + sample_time * ((v_phase_A(t) - back_emf_A(t-1) - dL_dt * i_a(t-1)) / L_a(t));

end
%%
plot(theta,i_a)
hold on
plot(theta,ipA)
hold on
%%




time;
i_a_differential;
i_b_differential;
i_c_differential;

required_length=round(1/fe/sample_time);


start=required_length*4;

time2= time(start:start+required_length);
time2=time2-time2(1);
i_a_differential2= i_a_differential(start:start+required_length);
i_b_differential2= i_b_differential(start:start+required_length);
i_c_differential2= i_c_differential(start:start+required_length);


frequency=1/(time2(end)-time2(1));
theta2=linspace(0,2*pi,length(i_a_differential2));

theta2=theta2-(pi+theta_difference)+0.35;


% Initialize arrays to store results
id2 = zeros(size(time2));
iq2 = zeros(size(time2));

% Compute i_d and i_q over the fundamental period
for k = 1:length(time2)

    thetax=theta2(k); % Electrical angle at each time step

  
    % Clarke Transformation (3-phase to 2-phase stationary coordinates)
    i_alpha2 = i_a_differential2(k);
    i_beta2 = (1 / sqrt(3)) * (i_a_differential2(k) + 2 * i_b_differential2(k));

    % Park Transformation (Stationary to Rotating Coordinates)
    id2(k) = i_alpha2 * cos(thetax) + i_beta2 * sin(thetax);
    iq2(k) = -i_alpha2 * sin(thetax) + i_beta2 * cos(thetax);
end

%%
% figure()
% plot(time2,i_a_differential2)
% hold on
% plot(time2,i_b_differential2)
% hold on
% plot(time2,i_c_differential2)
% hold on

%%
figure()
plot(time2,id2,'r')
hold on
plot(time2,iq2,'b')
hold on
plot(time2,sqrt((iq2.^2)+(id2.^2)),'k')

mean(iq2)
mean(id2)
mean(sqrt((iq2.^2)+(id2.^2)))
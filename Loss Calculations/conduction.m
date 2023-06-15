f_L=1e3;
time=linspace(0,1/f_L,1e4); % should be even
gama= 2*pi*f_L.*time;

M=1;
reference_signal= M*sin(gama);



theta=pi/4;
I_L_peak=1;
I_L= I_L_peak*sin(gama-theta);

figure()
plot(gama,reference_signal);
hold on;
plot(gama,I_L);

xlim([0 2*pi])

%% Two level converter (T1 T2)

% CONDUCTION ANGLES γ1 , γ2 and The Currents

I_T1= [zeros(1,max(find(theta>=gama))), I_L(1,max(find(theta>=gama)):max(find(theta>=gama))+length(gama)/2) , zeros(1,-max(find(theta>=gama))+length(gama)/2)  ];

I_T1=I_T1(2:end);

I_T2=I_T1-I_L;

figure();
plot(gama,I_T1,'Color', 'r')
hold on;

figure();
plot(gama,I_T2,'Color', 'b')
hold on;











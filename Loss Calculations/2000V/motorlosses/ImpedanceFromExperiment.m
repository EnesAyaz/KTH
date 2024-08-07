load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\OneDrive_1_3-28-2024\measuredData.mat');
%%
time=Data.Time;
U_RS=Data.U_R1_S1;
U_TR=Data.U_T1_R1;
U_ST=Data.U_S1_T1;
%%
U_R= (U_RS-U_TR)/3;
U_S= (U_ST-U_RS)/3;
U_T= (U_TR-U_ST)/3;
%%
I_R=Data.I_R1;
I_S=Data.I_S1;
I_T=Data.I_T1;

% n=1;
% t_sample= time(2)-time(1);
% T_fundamental=1/300;
% time_end=round(T_fundamental*n/t_sample);
% 
% U_R=U_R(1:time_end);
% I_R=I_R(1:time_end);
% U_S=U_S(1:time_end);
% I_S=I_S(1:time_end);
% U_T=U_T(1:time_end);
% I_T=I_T(1:time_end);
% time=linspace(0,T_fundamental*n,length(I_R));



%%
[U_R_mag, U_R_angle,f] = fft_mag_angle(U_R,time);
[U_S_mag, U_S_angle,f] = fft_mag_angle(U_S,time);
[U_T_mag, U_T_angle,f] = fft_mag_angle(U_T,time);

U_R_h= U_R_mag.* exp(-1i*U_R_angle);
U_S_h= U_S_mag.* exp(-1i*U_S_angle);
U_T_h= U_T_mag.* exp(-1i*U_T_angle);

[I_R_mag, I_R_angle,f] = fft_mag_angle(I_R,time);
[I_S_mag, I_S_angle,f] = fft_mag_angle(I_S,time);
[I_T_mag, I_T_angle,f] = fft_mag_angle(I_T,time);

I_R_h= I_R_mag.* exp(-1i*I_R_angle);
I_S_h= I_S_mag.* exp(-1i*I_S_angle);
I_T_h= I_T_mag.* exp(-1i*I_T_angle);


P_R_h=3*((U_R_mag.*I_R_mag)/2).*cos(U_R_angle-I_R_angle);
%%
stem(f,P_R_h)
% xlim([8e3 12e3])


%%
a=exp(1i*2*pi/3);

S= [1 1 1 ; 1 a^2 a ; 1 a a^2];

U= [U_R_h' ; U_S_h' ; U_T_h'];

I= [I_R_h' ; I_S_h' ; I_T_h'];

U_pn= inv(S)*U;
I_pn= inv(S)*I;

%%
 % plot(f,abs(I_p(2,:)))
% 
% plot(f,abs(U_pn(3,:)))
% hold on
% % plot(f,abs(U_pn(2,:)))
% hold on 
% % plot(f,abs(U_R_h),'--')
%%


U_p= U_pn(3,:);
U_n= U_pn(2,:);


Up_min_plus= ones(size(U_p));
Un_min_plus= ones(size(U_n));

for i=1:1:(length(f)-2)

if U_p(i)>U_n(i+2)
Up_min_plus(i)=1;
Un_min_plus(i)=-1;
else
Up_min_plus(i)=-1;
Un_min_plus(i)=1;
end
end


% threshold=max(abs(U_p))/100;
% U_p(abs(U_p)<threshold)=0; % determines the low-amplitude threshold
% P_R_h(abs(U_p)<threshold)=0; % determines the low-amplitude threshold
% 
% threshold=max(abs(U_n))/100;
% U_n(abs(U_n)<threshold)=0; % determines the low-amplitude threshold
% P_R_h(abs(U_n)<threshold)=0; % determines the low-amplitude threshold

%%
% U_p(abs(U_p)<abs(U_n))=0; % determines the low-amplitude threshold
% U_n(abs(U_p)>abs(U_n))=0; % determines the low-amplitude threshold

%%
stem(f/1e3,abs(U_p))
hold on
stem(f/1e3,abs(U_n))
hold on 
% stem(f,P_R_h)
hold on 
% xlim([8e3 12e3])
xlim([0 40])
%%



figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple stem objects using matrix input to stem
stem1 = stem(f/1e3,abs(U_p),'Marker','none','LineWidth',2);
stem2=stem(f/1e3,abs(U_n),'Marker','none','LineWidth',2);
set(stem1,'DisplayName','Negative Sequence','Color',[0 0 1]);
set(stem2,'DisplayName','Positive Sequence','Color',[1 0 0]);

% Create ylabel
ylabel({'Voltage (V)'});

% Create xlabel
xlabel({'Frequency (kHz)'});

% Create title
title({'Voltage Spectrum'});

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 40]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.402380959352566 0.618650796631028 0.339285706888352 0.110714282734053]);
%%
Ks=zeros(size(U_p));
Kr=zeros(size(U_p));

for i=1:1:(length(f)-2)

A11= (abs(U_p(i))^2)/2;
A12= Up_min_plus(i)*(abs(U_p(i))^2)/2;

A21= (abs(U_n(i))^2)/2;
A22= Un_min_plus(i)*(abs(U_n(i))^2)/2;

A= [A11 A12; A21 A22];

X= [P_R_h(i); P_R_h(i+2)];

B= inv(A)*X;

Ks(i)= B(1);
Kp(i)= B(2);

end


%%
plot(f,Ks)
xlim([8e3 11e3])



% % 
% % U_p= U_pn(3,:);
% % U_n= U_pn(2,:);
% % 
% % Up= [U_p,0,0];
% % Un= [0,0, U_n];
% % f_pn= [(f(1)-f(2)), f, (f(end)+f(1)-f(2)) ];
% % 
% % %%
% % plot(f_pn,abs(Up))
% % hold on
% % plot(f_pn,abs(Un))
% % hold on
% % 
% 





pp_4= [1 -1 1 -1 1 -1 1 -1];

pp_2= [1  1 -1 -1 1 1 -1 -1];

pp_trans= [1  0 0 -1 1 0 0 -1];
k=0.5;
pp_trans= [1  k -1*k -1 1 k -1*k -1];



pp_4= repelem(pp_4, 100);
pp_2= repelem(pp_2, 100);
pp_trans= repelem(pp_trans, 100);

%%
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple stair objects using matrix input to stairs
stairs1 = stairs(pp_4,'LineWidth',2);
stairs2 = stairs(pp_2-3,'LineWidth',2);
stairs3= stairs(pp_trans-6,'LineWidth',2);

set(stairs1,'Color',[0 0 1]);
set(stairs2,'Color',[1 0 0]);
set(stairs3,'Color',[0 0 0]);

% The following line demonstrates an alternative way to create a data tip.
% datatip(stairs1(1),7,1);
% Create datatip

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XTick',zeros(1,0),...
    'YTick',[-7 -6 -5 -4 -2 -1 1],'YTickLabel',{'{S}','{0}','{N}','{S}','{N}','{S}','{N}'});
%%


L = length(pp_4);

fft_pp4 = fft(pp_4);
P2 = abs(fft_pp4/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
fft_pp4=P1;


fft_pp2 = fft(pp_2);
P2 = abs(fft_pp2/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
fft_pp2=P1;

fft_pptrans = fft(pp_trans);
P2 = abs(fft_pptrans/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
fft_pptrans=P1;



% Frequency axis
f = (0:(L)/2);  % normalized frequency


% Plot FFT magnitude
figure;
subplot(3,1,1);
plot(f, fft_pp4);
title('FFT of pp\_4 sequence');
xlabel('Normalized Frequency');
ylabel('|X(f)|');
xlim([0 40])

subplot(3,1,2);
plot(f, fft_pp2);
title('FFT of pp\_2 sequence');
xlabel('Normalized Frequency');
ylabel('|X(f)|');
xlim([0 40])

subplot(3,1,3);
plot(f, fft_pptrans);
title('FFT of pp\_trans sequence');
xlabel('Normalized Frequency');
ylabel('|X(f)|');
xlim([0 40])
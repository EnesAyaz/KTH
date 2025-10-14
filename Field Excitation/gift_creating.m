%% Parameters
samples_per_symbol = 100;
k_values = linspace(-1,1,20);   % sweep from -1 to 1 (40 frames)
filename = 'pptrans_sweep_MMF.gif';

% Base patterns
pp_4_base = [1 -1 1 -1 1 -1 1 -1];
pp_2_base = [1  1 -1 -1 1 1 -1 -1];

for idx = 1:length(k_values)
    k = k_values(idx);

    % Define transition pattern for this k
    pp_trans_base = [1 k -k -1 1 k -k -1];

    % Expand (100 samples per symbol)
    pp_4 = repelem(pp_4_base, samples_per_symbol);
    pp_2 = repelem(pp_2_base, samples_per_symbol);
    pp_trans = repelem(pp_trans_base, samples_per_symbol);

 
figure1 = figure(1);

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


    % --- Capture frame ---
    frame = getframe(gcf);
    im = frame2im(frame);
    [A,map] = rgb2ind(im,256);

    if idx == 1
        imwrite(A,map,filename,"gif","LoopCount",Inf,"DelayTime",0.2);
    else
        imwrite(A,map,filename,"gif","WriteMode","append","DelayTime",0.2);
    end
end


filename = 'pptrans_sweep_FFT.gif';

for idx = 1:length(k_values)
    k = k_values(idx);

    % Define transition pattern for this k
    pp_trans_base = [1 k -k -1 1 k -k -1];

    % Expand (100 samples per symbol)
    pp_4 = repelem(pp_4_base, samples_per_symbol);
    pp_2 = repelem(pp_2_base, samples_per_symbol);
    pp_trans = repelem(pp_trans_base, samples_per_symbol);

    % --- FFTs ---
    L = length(pp_4);
    % pp4
    P2 = abs(fft(pp_4)/L); P1 = P2(1:L/2+1); P1(2:end-1) = 2*P1(2:end-1);
    fft_pp4 = P1;
    % pp2
    P2 = abs(fft(pp_2)/L); P1 = P2(1:L/2+1); P1(2:end-1) = 2*P1(2:end-1);
    fft_pp2 = P1;
    % pptrans
    P2 = abs(fft(pp_trans)/L); P1 = P2(1:L/2+1); P1(2:end-1) = 2*P1(2:end-1);
    fft_pptrans = P1;

    f = 0:(L/2);

    % --- Plot ---
    figure(1); clf;
    subplot(3,1,1);
    plot(f, fft_pp4,'b','LineWidth',1.5);
    title('FFT of pp\_4'); xlabel('Frequency'); ylabel('|X(f)|'); xlim([0 40]); ylim([0 1.3])

    subplot(3,1,2);
    plot(f, fft_pp2,'r','LineWidth',1.5);
    title('FFT of pp\_2'); xlabel('Frequency'); ylabel('|X(f)|'); xlim([0 40]);  ylim([0 1.3])

    subplot(3,1,3);
    plot(f, fft_pptrans,'k','LineWidth',1.5);
    title(sprintf('FFT of pp\\_trans (k = %.2f)',k));
    xlabel('Frequency'); ylabel('|X(f)|'); xlim([0 40]);  ylim([0 1.3])

    % --- Capture frame ---
    frame = getframe(gcf);
    im = frame2im(frame);
    [A,map] = rgb2ind(im,256);

    if idx == 1
        imwrite(A,map,filename,"gif","LoopCount",Inf,"DelayTime",0.2);
    else
        imwrite(A,map,filename,"gif","WriteMode","append","DelayTime",0.2);
    end
end


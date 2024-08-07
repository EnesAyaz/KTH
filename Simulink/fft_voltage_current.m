IphA= out.IphA (:,2);
time= out.IphA (:,1);
VAB=out.VAB (:,2);
Irotating=out.Irotating(:,2);
%%
L=length(IphA);
Fs = 1/(time(2)-time(1));    % Sampling frequency                   

 Y = fft(VAB);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create bar
bar(f/1000,P1,'FaceColor',[0 0 1],'EdgeColor','none','BarWidth',4);
% Create ylabel
ylabel({'Voltage (V)'});

% Create xlabel
xlabel({'Frequency (kHz)'});

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 40]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',1,...
    'MinorGridAlpha',1,'XGrid','on','XMinorGrid','on','YGrid','on','YMinorGrid',...
    'on');
%%
 Y = fft(IphA);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create bar
bar(f/1000,P1,'FaceColor',[1 0 0],'EdgeColor','none','BarWidth',4);
% Create ylabel
ylabel({'Current (A)'});

% Create xlabel
xlabel({'Frequency (kHz)'});

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 40]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',1,...
    'MinorGridAlpha',1,'XGrid','on','XMinorGrid','on','YGrid','on','YMinorGrid',...
    'on');
%%

 Y = fft(Irotating);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create bar
bar(f/1000,P1,'FaceColor',[1 0 1],'EdgeColor','none','BarWidth',4);
% Create ylabel
ylabel({'Current (A)'});

% Create xlabel
xlabel({'Frequency (kHz)'});

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 40]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',1,...
    'MinorGridAlpha',1,'XGrid','on','XMinorGrid','on','YGrid','on','YMinorGrid',...
    'on');
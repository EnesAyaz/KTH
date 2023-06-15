fs=10e3:1e3:40e3;

Pco_2l= ones(size(fs))*537;
Pco_3l= ones(size(fs))*890;

Psw_2l= ones(size(fs))*625/20e3.*fs;
Psw_3l= ones(size(fs))*188/20e3.*fs;

% %%
Pco_2l= ones(size(fs))*631;
Pco_3l= ones(size(fs))*1004;

Psw_2l= ones(size(fs))*865/20e3.*fs;
Psw_3l= ones(size(fs))*374/20e3.*fs;


% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(fs/1e3,Pco_2l,'MarkerSize',5,'LineWidth',3);
plot2 = plot(fs/1e3,Pco_3l,'MarkerSize',5,'LineWidth',3);
plot3 =plot(fs/1e3,Psw_2l,'MarkerSize',5,'LineWidth',3);
plot4 =plot(fs/1e3,Psw_3l,'MarkerSize',5,'LineWidth',3);


set(plot1,'Marker','none','Color',[1 0 0],'DisplayName','2L-c' );
set(plot3,'Marker','diamond','Color',[1 0 0],'DisplayName','2L-sw' );

set(plot2,'Marker','none','Color',[0 0 1],'DisplayName','3L-c' );
set(plot4,'Marker','square','Color',[0 0 1],'DisplayName','3L-sw' );

% title( strcat('fsw=  ',string(fs/1000),' kHz'));

% Create ylabel
ylabel({'Power Loss (W)'});

% Create xlabel
xlabel({'Switching Frequency (kHz)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',20,'GridAlpha',1,...
    'GridColor',[0.466666666666667 0.674509803921569 0.188235294117647],...
    'GridLineWidth',1,'XGrid','on','YGrid','on');

legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.373809525246421 0.77817460700633 0.139285712848817 0.139285710453987]);

%%


% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(fs/1e3,Pco_2l+Psw_2l,'MarkerSize',5,'LineWidth',3);
plot2 = plot(fs/1e3,Pco_3l+Psw_3l,'MarkerSize',5,'LineWidth',3);


set(plot1,'Marker','none','Color',[1 0 0],'DisplayName','2L');

set(plot2,'Marker','none','Color',[0 0 1],'DisplayName','3L');

% title( strcat('fsw=  ',string(fs/1000),' kHz'));

% Create ylabel
ylabel({'Power Loss (W)'});

% Create xlabel
xlabel({'Switching Frequency (kHz)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',20,'GridAlpha',1,...
    'GridColor',[0.466666666666667 0.674509803921569 0.188235294117647],...
    'GridLineWidth',1,'XGrid','on','YGrid','on');

legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.373809525246421 0.77817460700633 0.139285712848817 0.139285710453987]);
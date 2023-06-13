
% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(x*A_ac_die*1000,Pco,'MarkerSize',15,'LineWidth',3);
plot2 = plot(x*A_ac_die*1000,Psw,'MarkerSize',15,'LineWidth',3);

set(plot1,'Marker','diamond','Color',[1 0 0]);
set(plot2,'Marker','square','Color',[0 0 1]);


title( strcat('fsw=  ',string(fs/1000),' kHz'));

% Create ylabel
ylabel({'Power Loss (W)'});

% Create xlabel
xlabel({'Area of the Die (mm2)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',20,'GridAlpha',1,...
    'GridColor',[0.466666666666667 0.674509803921569 0.188235294117647],...
    'GridLineWidth',1,'XGrid','on','YGrid','on');

frequency=[6 7 8 9 10 11 12 13 14 15 17 18 20];

Cap=[697 630 561 501 473 430 405 384 368 342  335 313 307 ];

figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot(frequency,Cap,'LineWidth',2,'Color',[0 0 1]);

% Create ylabel
ylabel({'Capacitance (\muF)'});

% Create xlabel
xlabel({'Switching Frequency (khZ)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);

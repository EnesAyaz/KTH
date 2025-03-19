% Parameters
number_of_dies = 8;
total_current = 1;
health_dies = 8:-1:1;
current_per_die = total_current ./ health_dies;
failed = number_of_dies - health_dies;
total_current2 = total_current * ones(size(current_per_die));

% Calculations
r = 1;
P = current_per_die .* current_per_die * r .* health_dies;
Rthermal = 1 ./ ((1/8) * health_dies);
Rheatsink=8;
DeltaT = P .*( Rheatsink+ Rthermal);

DeltaT=DeltaT/DeltaT(1);

% Plotting
figure;
yyaxis left;
plot(failed, DeltaT, 'r', 'LineWidth', 2); % Red line for DeltaT
ylabel('Normalized \DeltaT_{max}', 'Color', 'r'); % Red label for left y-axis
ylim([0 DeltaT(8)]); % Adjust ylim for left axis

yyaxis right;
plot(failed, current_per_die, 'b', 'LineWidth', 2); % Blue line for current per die
hold on;
plot(failed, total_current2, 'b--', 'LineWidth', 2); % Dashed blue line for total current
ylabel('Normalized Current per Die', 'Color', 'b'); % Blue label for right y-axis
ylim([0 1.2]); % Adjust ylim for right axis
yticks(0:0.2:1); % Set x-axis ticks to integers
% Labels and grid
xlabel('Number of Failed Dies');
grid on;
set(gca, 'GridAlpha', 0.3); % Set grid transparency

% Change axis colors
ax = gca; % Get current axes
ax.YAxis(1).Color = 'r'; % Left y-axis (temperature) in red
ax.YAxis(2).Color = 'b'; % Right y-axis (current) in blue
ax.XAxis.Color = 'k'; % X-axis in black

% Set x-axis limits and ticks
xlim([0 7]); % Set x-axis limits
xticks(0:1:7); % Set x-axis ticks to integers

% Set font to Times New Roman and font size to 15
set(gca, 'FontName', 'Times New Roman', 'FontSize', 15);
% set([xlabel(''), ylabel('')], 'FontName', 'Times New Roman', 'FontSize', 15);
legend('\DeltaT_{max}', 'Current per Die', 'Total Current', 'Location', 'best', 'FontName', 'Times New Roman', 'FontSize', 15);

% Adjust title font (if you add a title later)
% title('Impact of Failed Dies on Current and Temperature', 'FontName', 'Times New Roman', 'FontSize', 15);

% Ensure the right y-label is visible
ax = gca;
ax.Position(3) = ax.Position(3) * 0.9; % Reduce the width of the plot to make space for the right y-label



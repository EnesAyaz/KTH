theta = linspace(0, 2*pi, 100);

delta = 60;  % degrees
delta_rad = delta * pi / 180;

m1 = 1.15;
m2 = 0.80;
V1 = m1 * sin(theta);
V2 = m2 * sin(theta - delta_rad);

common_mode = (-m1/6) * sin(3*theta);

% Set default font sizes
set(groot, 'defaultAxesFontSize', 12);
set(groot, 'defaultTextFontSize', 12);

% First figure - with common mode removed
figure;
plot(theta, V1 - common_mode, 'b', 'LineWidth', 1.5);
hold on;
plot(theta, V2 - common_mode, 'r', 'LineWidth', 1.5);
xlabel('Theta (radians)', 'FontSize', 14);
ylabel('Voltage (V)', 'FontSize', 14);
title(sprintf('m_1 = %.2f, m_2 = %.2f, \\delta = %d°', m1, m2, delta), 'FontSize', 12);
legend('V_1 - Common Mode', 'V_2 - Common Mode', 'FontSize', 12, 'Location', 'best');
grid on;

% Second figure - original signals and common mode
figure;
plot(theta, V1, 'b', 'LineWidth', 1.5);
hold on;
plot(theta, V2, 'r', 'LineWidth', 1.5);
hold on;
plot(theta, -common_mode, 'g--', 'LineWidth', 1.5);
xlabel('Theta (radians)', 'FontSize', 14);
ylabel('Voltage (V)', 'FontSize', 14);
title(sprintf('m_1 = %.2f, m_2 = %.2f, \\delta = %d°', m1, m2, delta), 'FontSize', 12);
legend('V_1', 'V_2', '-Common Mode', 'FontSize', 12, 'Location', 'best');
grid on;
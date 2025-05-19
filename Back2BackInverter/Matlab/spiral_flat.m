% --- Input Parameters (Modify These) ---
L_target = 500;      % Inductance (uH)
w = 0.1;            % Wire diameter (inches)
s = 0.05;           % Spacing between turns (inches)
Di_min = 0.1;       % Min inner diameter (inches)
Di_max = 2.0;       % Max inner diameter (inches)

% --- Optimization ---
% Define the function to minimize (cable length)
f = @(Di) compute_cable_length(Di, L_target, w, s);

% Find optimal Di using fminbnd
[Di_opt, min_length] = fminbnd(f, Di_min, Di_max);

% Compute N and other parameters at optimal Di
[A_opt, N_opt] = solve_N(Di_opt, L_target, w, s);
Do_opt = Di_opt + 2 * N_opt * (w + s); % Outer diameter

% --- Display Results ---
fprintf('Optimal inner diameter (Di): %.4f inches\n', Di_opt);
fprintf('Optimal number of turns (N): %.2f\n', N_opt);
fprintf('Outer diameter (Do): %.4f inches\n', Do_opt);
fprintf('Minimum cable length: %.2f inches (≈%.2f m)\n', min_length, min_length * 0.0254);

% --- Helper Functions (Defined at the end) ---
function length = compute_cable_length(Di, L_target, w, s)
    [A, N] = solve_N(Di, L_target, w, s);
    if isreal(N) && N > 0
        length = pi * N * (Di + (N - 1) * (w + s)); % Total wire length
    else
        length = Inf; % Invalid solution
    end
end

function [A, N] = solve_N(Di, L_target, w, s)
    % Solve cubic equation: A^3 - 30*L*A + 11*L*Di = 0
    coeffs = [1, 0, -30 * L_target, 11 * L_target * Di];
    A_roots = roots(coeffs);
    
    % Select the real, positive root
    A = A_roots(imag(A_roots) == 0 & A_roots > 0);
    if isempty(A)
        A = Inf;
        N = Inf;
    else
        A = A(1);
        N = (2 * A - Di) / (w + s); % Compute N
    end
end
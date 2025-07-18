% Parameters
theta_vals = deg2rad(0:1:359);        % electrical angle [rad]
phi_vals   = deg2rad(-75:1:75);      % power factor angle [rad]
ma_vals    = 0:0.01:1.0;             % modulation index

% Preallocate input arrays
N = length(theta_vals) * length(phi_vals) * length(ma_vals);
input_data = zeros(N, 5);  % columns: [ib, ic, db, dc, ma]

index = 1;
for ma = ma_vals
    for phi = phi_vals
        for theta = theta_vals

            % Phase shifts
            theta_b = theta - 2*pi/3;
            theta_c = theta - 4*pi/3;

            % Duty cycles (SPWM)
            db = 0.5 + (ma/2)*sin(theta_b);
            dc = 0.5 + (ma/2)*sin(theta_c);

            % Phase currents
            ia= sin(theta);
            ib = sin(theta_b - phi);
            ic = sin(theta_c - phi);

            ib=ib/(abs(ia)+abs(ib)+abs(ic));
            ic=ic/(abs(ia)+abs(ib)+abs(ic));

            % Store inputs
            input_data(index, :) = [ib, ic, db, dc, ma];
            index = index + 1;
        end
    end
end


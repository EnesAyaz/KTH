numD = 2;  % or higher resolution
numI = 2;

DB_vals   = linspace(0, 1, numD);
DC_vals   = linspace(0, 1, numD);
iphB_vals = linspace(-0.5, 0.5, numI);
iphC_vals = linspace(-0.5, 0.5, numI);

theta_b_LUT = NaN(numD, numD, numI, numI);
theta_c_LUT = NaN(numD, numD, numI, numI);

for i = 1:numD
    for j = 1:numD
        DB = DB_vals(i);
        DC = DC_vals(j);
        
        if DB + DC >= 1.5  % Constraint
            continue;
        end

        for k = 1:numI
            for l = 1:numI
                iphB = iphB_vals(k);
                iphC = iphC_vals(l);
                
                try
                    [theta_b, theta_c, ~] = optimize_interleaving_rms(iphB, iphC, DB, DC);
                    theta_b_LUT(i,j,k,l) = theta_b;
                    theta_c_LUT(i,j,k,l) = theta_c;
                catch
                    % leave as NaN
                end
            end
        end
    end
end

save('interleaving_lut.mat', 'theta_b_LUT', 'theta_c_LUT', ...
     'DB_vals', 'DC_vals', 'iphB_vals', 'iphC_vals');

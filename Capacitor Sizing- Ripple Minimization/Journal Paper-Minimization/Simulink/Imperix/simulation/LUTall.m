numSamples = 20;
D_vals   = linspace(0, 1, numSamples);     % DB and DC in [0, 1)

numSamples_current=50; 
Iph_vals = linspace(-0.5, 0.5, numSamples_current);   % IphB and IphC in [-0.5, 0.5]


% Initialize LUTs
theta_b_LUT = NaN(numSamples, numSamples, numSamples_current, numSamples_current);
theta_c_LUT = NaN(numSamples, numSamples, numSamples_current, numSamples_current);
min_rms_LUT = NaN(numSamples, numSamples, numSamples_current, numSamples_current);

for i = 1:numSamples
for j = 1:numSamples
        DB = D_vals(i);
        DC = D_vals(j);
for k = 1:numSamples_current
for l = 1:numSamples_current
            iphB = Iph_vals(k);
            iphC = Iph_vals(l);
            if 0 <(1.5-DB-DC) && (1.5-DB-DC)<1
            [theta_b_opt, theta_c_opt, min_rms] = optimize_interleaving_rms(iphB, iphC, DB, DC);
            % Store values
            theta_b_LUT(i,j,k,l) = theta_b_opt;
            theta_c_LUT(i,j,k,l) = theta_c_opt;
            else 
                continue;
            end
end
end
end
end
% Save results
save('interleaving_results.mat','D_vals', 'D_vals', 'Iph_vals', 'Iph_vals','theta_b_LUT', 'theta_c_LUT')

save('theta_b_LUT.mat','theta_b_LUT')
save('theta_c_LUT.mat','theta_c_LUT')

save('DB.mat','D_vals')
save('DC.mat','D_vals')

save('Ib.mat','Iph_vals')
save('Ic.mat','Iph_vals')



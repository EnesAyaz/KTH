% Adjustable resolution
numSamples = 12;

ma=0.6;
theta=linspace(0,2*pi,numSamples);
Da_x=(1+ma*sin(theta))/2;
Db_x=(1+ma*sin(theta-2*pi/3))/2;
Dc_x=(1+ma*sin(theta+2*pi/3))/2;

% Sampling ranges
% D_vals   = linspace(0, 1, numSamples);     % DB and DC in [0, 1)

numSamples_current=50; 
% Iph_vals = linspace(-0.5, 0.5, numSamples);   % IphB and IphC in [-0.5, 0.5]

theta=linspace(0,2*pi,numSamples_current);
Ia=10*sin(theta);
Ib=10*sin(theta-2*pi/3);
Ic=10*sin(theta+2*pi/3);

Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));

Ibx=Ib./(abs(Ia)+abs(Ib)+abs(Ic));

Icx=Ic./(abs(Ia)+abs(Ib)+abs(Ic));

% Initialize LUTs
theta_b_LUT = NaN(numSamples, numSamples, numSamples_current, numSamples_current);
theta_c_LUT = NaN(numSamples, numSamples, numSamples_current, numSamples_current);
min_rms_LUT = NaN(numSamples, numSamples, numSamples_current, numSamples_current);

for i = 1:numSamples
    DB = Db_x(i);
    DC = Dc_x(i);
for k = 1:numSamples_current
            iphB = Ibx(k);
            iphC = Icx(k);
            [theta_b_opt, theta_c_opt, min_rms] = optimize_interleaving_rms(iphB, iphC, DB, DC);
            % Store values
            theta_b_LUT(i,i,k,k) = theta_b_opt;
            theta_c_LUT(i,i,k,k) = theta_c_opt;
end
end
% Save results
save('interleaving_results.mat','Db_x', 'Dc_x', 'Ibx', 'Icx','theta_b_LUT', 'theta_c_LUT')

%%


% ma=0.6;
% theta=40*pi/180;
% DB_query=(1+ma*sin(theta-2*pi/3))/2;
% DC_query=(1+ma*sin(theta+2*pi/3))/2;
% 
% theta=40*pi/180;
% Ia=10*sin(theta);
% Ib=10*sin(theta-2*pi/3);
% Ic=10*sin(theta+2*pi/3);
% 
% Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));
% 
% iphB_query=Ib./(abs(Ia)+abs(Ib)+abs(Ic));
% 
% iphC_query=Ic./(abs(Ia)+abs(Ib)+abs(Ic));
% 
% 
% D_tol  = 0.5 * min(abs(diff(Db_x)));
% iph_tol = 0.1;  % assumes Ibx and Icx same resolution
% 
% 
% % Find valid i indices (DB and DC match)
% valid_i = find( abs(Db_x - DB_query) < D_tol & ...
%                 abs(Dc_x - DC_query) < D_tol );
% 
% % Find valid k indices (iphB and iphC match)
% valid_k = find( abs(Ibx - iphB_query) < iph_tol & ...
%                 abs(Icx - iphC_query) < iph_tol );
% 
% % Lookup
% for i = valid_i
%     for k = valid_k
%         theta_b_val = theta_b_LUT(i, i, k, k)
%         if ~isnan(theta_b_val)
%             fprintf('Match: i=%d, k=%d → θ_b = %.4f rad\n', i, k, theta_b_val);
%         end
%     end
% end



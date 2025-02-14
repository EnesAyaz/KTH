pHA=0.36;
pHB=0.24;
pHC=-0.6;


DA= (1+pHA)/2;
DB= (1+pHB)/2;
DC= (1+pHC)/2;

% DA=0.5;
% DB=0.5;
% DC=0.5;

% Ensure inputs are single
DA = single(DA);
DB = single(DB);
DC = single(DC);

SA_fs_mag = abs((single(2)/single(pi)) * sin(single(pi) * DA));
SB_fs_mag = abs((single(2)/single(pi)) * sin(single(pi) * DB));
SC_fs_mag = abs((single(2)/single(pi)) * sin(single(pi) * DC));
    
    a =SA_fs_mag;
    b = SB_fs_mag;
    c = SC_fs_mag;
    
    % Check if the sides form a valid triangle
    if a + b <= c || a + c <= b || b + c <= a
        error('The sides do not form a valid triangle.');
    end
    
    % Calculate the angles using the Law of Cosines
    angle_A = acosd((b^2 + c^2 - a^2) / (2 * b * c));
    angle_B = acosd((a^2 + c^2 - b^2) / (2 * a * c));
    angle_C = acosd((a^2 + b^2 - c^2) / (2 * a * b));
    
    % Display the results
    fprintf('Angles of the triangle are:\n');
    fprintf('A = %.2f°, B = %.2f°, C = %.2f°\n', angle_A, angle_B, angle_C);

    phiB=180-angle_C
    phiC=360-(180-angle_B)
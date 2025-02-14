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

PhiA = single(0); % Explicitly set to single

if abs(SA_fs_mag - SB_fs_mag) <= SC_fs_mag && SC_fs_mag <= (SA_fs_mag + SB_fs_mag)

    a = SA_fs_mag;
    b = SB_fs_mag;
    c = SC_fs_mag;

    angle_A = acosd((b^2 + c^2 - a^2) / (2 * b * c));
    angle_B = acosd((a^2 + c^2 - b^2) / (2 * a * c));
    angle_C = acosd((a^2 + b^2 - c^2) / (2 * a * b));

    PhiB=180-angle_C;
    PhiC=360-(180-angle_B);

elseif SA_fs_mag >= SB_fs_mag && SA_fs_mag >= SC_fs_mag 
    PhiB = single(180);
    PhiC = single(180);
elseif SB_fs_mag >= SA_fs_mag && SB_fs_mag >= SC_fs_mag 
    PhiB = single(180);
    PhiC = single(180);
elseif SC_fs_mag >= SA_fs_mag && SC_fs_mag >= SB_fs_mag 
    PhiB = single(0);
    PhiC = single(180);
else 
    PhiB = single(0);
    PhiC = single(0);
end

PhiB
PhiC


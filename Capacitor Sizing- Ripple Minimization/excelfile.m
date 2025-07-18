load('C:\Github\KTH\Capacitor Sizing\CurrentHarmonics\Case3.mat')
%%
filename = 'Case3.xlsx';
current_harmonics_mag=abs(current_harmonics);
current_harmonics_angle=angle(current_harmonics);

T = table(harmonic_frequency', current_harmonics_mag',current_harmonics_angle');

T.Properties.VariableNames = ["Frequency", "Current Harmonics Magnitude", ...
    "Current Harmonics Angle" ];

C = {'Carrier Frequency', 'DC Voltage', 'Fundamental Frequency', 'Modulation', 'Power', 'Power Factor' ; ...
    carrier_frequency, DCVoltage, fundamental_frequency, modulation, power, power_factor};

writetable(T,filename,'Sheet','data');
writecell(C,filename,'Sheet','Info');


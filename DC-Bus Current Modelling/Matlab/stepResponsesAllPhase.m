%% Phase A
filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhAResponse.txt";
dataLines = [2, Inf];
[freq, IC1real, IC1imag, IC2real, IC2imag, IC3real, IC3imag, IC4real, IC4imag] = capacitorStepResponse(filename, dataLines);

values= [IC1real,IC1imag, IC2real,IC2imag,IC3real,IC3imag,IC4real,IC4imag];

% New frequency array for interpolation
new_freq = frequency_C_new; 

% Preallocate the new interpolated values
interpolated_values = zeros(length(new_freq),8);

% Interpolation loop
for i = 1:8
    % Interpolate the values for each array using 'linear' method
    interpolated_values(:,i) = interp1(freq, values(:, i), new_freq, 'linear');
end

% Display the interpolated values
cap1_phA= interpolated_values(:,1)+1i*interpolated_values(:,2);
cap2_phA= interpolated_values(:,3)+1i*interpolated_values(:,4);
cap3_phA= interpolated_values(:,5)+1i*interpolated_values(:,6);
cap4_phA= interpolated_values(:,7)+1i*interpolated_values(:,8);


cap1_phA=cap1_phA';
cap2_phA=cap2_phA';
cap3_phA=cap3_phA';
cap4_phA=cap4_phA';


% plot(new_freq, abs(cap1_phA));
% hold on
% plot(new_freq, abs(cap2_phA));
% hold on
% plot(new_freq, abs(cap3_phA));
% hold on
% plot(new_freq, abs(cap4_phA));
% hold on

%% Phase B

filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhBResponse.txt";
dataLines = [2, Inf];
[freq, IC1real, IC1imag, IC2real, IC2imag, IC3real, IC3imag, IC4real, IC4imag] = capacitorStepResponse(filename, dataLines);

values= [IC1real,IC1imag, IC2real,IC2imag,IC3real,IC3imag,IC4real,IC4imag];

% New frequency array for interpolation
new_freq = frequency_C_new; 

% Preallocate the new interpolated values
interpolated_values = zeros(length(new_freq),8);

% Interpolation loop
for i = 1:8
    % Interpolate the values for each array using 'linear' method
    interpolated_values(:,i) = interp1(freq, values(:, i), new_freq, 'linear');
end

% Display the interpolated values
cap1_phB= interpolated_values(:,1)+1i*interpolated_values(:,2);
cap2_phB= interpolated_values(:,3)+1i*interpolated_values(:,4);
cap3_phB= interpolated_values(:,5)+1i*interpolated_values(:,6);
cap4_phB= interpolated_values(:,7)+1i*interpolated_values(:,8);

cap1_phB=cap1_phB';
cap2_phB=cap2_phB';
cap3_phB=cap3_phB';
cap4_phB=cap4_phB';



% plot(new_freq, abs(cap1_phB));
% hold on
% plot(new_freq, abs(cap2_phB));
% hold on
% plot(new_freq, abs(cap3_phB));
% hold on
% plot(new_freq, abs(cap4_phB));
% hold on

%% Phase C
filename="C:\Github\KTH\DC-Bus Current Modelling\Matlab\PhBResponse.txt";
dataLines = [2, Inf];
[freq, IC1real, IC1imag, IC2real, IC2imag, IC3real, IC3imag, IC4real, IC4imag] = capacitorStepResponse(filename, dataLines);

values= [IC1real,IC1imag, IC2real,IC2imag,IC3real,IC3imag,IC4real,IC4imag];

% New frequency array for interpolation
new_freq = frequency_C_new; 

% Preallocate the new interpolated values
interpolated_values = zeros(length(new_freq),8);

% Interpolation loop
for i = 1:8
    % Interpolate the values for each array using 'linear' method
    interpolated_values(:,i) = interp1(freq, values(:, i), new_freq, 'linear');
end

% Display the interpolated values
cap1_phC= interpolated_values(:,1)+1i*interpolated_values(:,2);
cap2_phC= interpolated_values(:,3)+1i*interpolated_values(:,4);
cap3_phC= interpolated_values(:,5)+1i*interpolated_values(:,6);
cap4_phC= interpolated_values(:,7)+1i*interpolated_values(:,8);


cap1_phC=cap1_phC';
cap2_phC=cap2_phC';
cap3_phC=cap3_phC';
cap4_phC=cap4_phC';


% plot(new_freq, abs(cap1_phC));
% hold on
% plot(new_freq, abs(cap2_phC));
% hold on
% plot(new_freq, abs(cap3_phC));
% hold on
% plot(new_freq, abs(cap4_phC));
% hold on

clear values IC1real IC1imag IC2real IC2imag IC3real IC3imag IC4real IC4imag new_freq interpolated_values
 

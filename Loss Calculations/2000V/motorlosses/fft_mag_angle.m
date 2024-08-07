function [U_mag, U_angle,f] = fft_mag_angle(U,time)

L = length(U);  % Length of signal

U_mag=fft(U);
U_mag=abs(U_mag/L);
U_mag=U_mag(1:L/2+1);
U_mag(2:end-1)=2*U_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

U_angle=fft(U);
U_angle=angle(U_angle);
U_angle=U_angle(1:L/2+1);

end